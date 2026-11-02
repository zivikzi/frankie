"""The logged tuning search for K-F and TW7 (KILL_TEST section 7, kill-test/TUNING_PLAN.md, KT-126 to KT-131).

    python kill-test/tune.py run LOG.jsonl [--workers N]
        Runs the agreed plan in order, appending every event to LOG (one JSON
        object per line), and stops where the plan says to stop:

        1. the floor on the search half (B1n-bot-r and B1n-mind, KT-101's radii);
        2. K-F at the start values on the search half (step 2);
        3. passes through KT-19 to KT-26, one number at a time, at most 3
           (steps 3 to 5);
        4. KT-27 by KT-47's rule at the pick, then the pick measured again with
           it (step 6);
        5. the pick and OS10 on the kept-back half, judged as on a kill-run set
           (step 7);
        6. TW7's gain and time constant, with as many passes as K-F used, and
           its own check (step 8).

        It stops, logs why and exits with 2 when the plan sends the search to
        Aitzaz: D at check 1 of 0.15 or more in any setting tried, 3 passes
        with no setting reaching every target, or a failed check. It never
        changes a value in the mind's code: registering the picks (step 9)
        is a separate commit Aitzaz approves.

        LOG is append-only. Run again with the same LOG and the search picks
        up where it stopped: every event it would make is compared with the
        one already logged, and a setting already measured is not measured
        again (every run is deterministic, I05).

    python kill-test/tune.py summary LOG.jsonl
        One line per setting tried, and the search's state.

The search half is the 15 odd tuning families and the kept-back half the 15
even ones, 10 runs each (TUNING_PLAN.md, step 1). Every run is the frozen
harness's run (harness/run.py) on the tuning set's own plans. While the
search runs, the minds are hosted in the tool's own worker processes, which
gives the same records as their own sandboxed process (KT-93, tested in
tests/test_kf_spiking.py); both checks run them in their own process, as
the kill run does (KT-129).
"""

import argparse
import dataclasses
import json
import pathlib
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from harness import agents, bench, judge, scoring  # noqa: E402
from harness import constants as C  # noqa: E402
from harness.readings_cache import ReadingCache  # noqa: E402
from harness.run import run_one  # noqa: E402
from mind import constants as K  # noqa: E402
from world import keys  # noqa: E402
from world.run_plan import generate_run  # noqa: E402

SEARCH = tuple(range(1, 31, 2))          # the 15 odd tuning families (TUNING_PLAN.md, step 1)
KEPT_BACK = tuple(range(2, 31, 2))       # the 15 even ones
RUNS = bench.RUNS_PER_FAMILY             # 10 runs per family (section 5)
MAX_PASSES = 3                           # (TUNING_PLAN.md, step 5)
TUNING = "tuning"
CHECK_SET_NAME = "tuning-kept-back"      # names the kept-back check's bootstrap resamples (KT-131)

# The closed list, in its order, with the values tried (TUNING_PLAN.md's table). Start values are mind.constants'.
KF_GRID = (
    ("KT-19", "leak", (0.025, 0.05, 0.1, 0.2, 0.4)),
    ("KT-20", "threshold", (0.625, 1.25, 2.5, 5, 10)),
    ("KT-21", "refractory_ms", (0, 1, 2, 4, 8)),
    ("KT-22", "inhibition", (0.078, 0.156, 0.3125, 0.625, 1.25)),
    ("KT-23", "detector_width_nw", (3.5, 4, 5, 6.5, 8)),
    ("KT-24", "commit_margin", (0.5, 1, 2, 4, 8)),
    ("KT-25", "objection_threshold", (0.125, 0.25, 0.5, 1, 2)),
    ("KT-26", "new_kind_threshold", (0.125, 0.25, 0.5, 1, 2)),
)
# The agreed start values (TUNING_PLAN.md's table). mind.constants held them while the search ran (c0b0814) and
# now holds the values set on the tuning set (kill-test/TUNED.md).
KF_START = {"leak": 0.1, "threshold": 2.5, "refractory_ms": 2, "inhibition": 0.3125, "detector_width_nw": 4,
            "commit_margin": 2, "objection_threshold": 0.5, "new_kind_threshold": 0.5}
GAIN_START = 1                           # TW7's start values (KT-28, KT-29, TUNING_PLAN.md)
TAU_START = 10
TW7_GRID = (
    ("KT-28", "gain", (0.25, 0.5, 1, 2, 4)),
    ("KT-29", "tau_ms", (2.5, 5, 10, 20, 40)),
)

# What tuning aims at (TUNING_PLAN.md): the power check's planned values (KT-15)
T_SETTLE = Fraction(97, 100)
T_COPY = Fraction(90, 100)
T_D_LEARN = Fraction(35, 100)
T_D_OVER_FLOOR = Fraction(20, 100)
T_FMN = Fraction(25, 100)
T_LOOK = Fraction(70, 100)
T_Q = Fraction(35, 100)
T_SOUR_DROP = Fraction(5, 100)
T_NOTICED = Fraction(70, 100)
LEAK_STOP = Fraction(15, 100)            # D at check 1 of 0.15 or more stops the search (TUNING_PLAN.md)

# Each shortfall is measured in that measure's spread between families: MK10's registered spreads (KT-128)
SPREAD_KEY = {"settle_rate": "settle", "copy_accept": "copy_accept", "d_learn_strict": "d_learn",
              "fmn_strict": "fmn", "lr_h1": "lr_h1", "lr_far": "lr_far", "dq_sour_strict": "q_sour",
              "sour_drop_strict": "sour_drop", "noticed": "noticed"}


# ------------------------------------------------------------------ plain JSON

def plain(x):
    if isinstance(x, Fraction):
        return {"exact": str(x), "value": float(x)}
    if isinstance(x, dict):
        return {str(k): plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [plain(v) for v in x]
    return x


def unplain(x):
    if isinstance(x, dict) and set(x) == {"exact", "value"}:
        return Fraction(x["exact"])
    if isinstance(x, dict):
        return {k: unplain(v) for k, v in x.items()}
    if isinstance(x, list):
        return [unplain(v) for v in x]
    return x


# ------------------------------------------------------------------ one mind on one half

@dataclasses.dataclass(frozen=True)
class Trial:
    mind: str                      # "K-F", "OS10" or "TW7"
    setting: tuple                 # K-F's closed list, as (name, value) pairs in KF_GRID's order
    rate: tuple = ()               # TW7's (gain, tau_ms) pairs
    spike_nano: int = 0            # KT-27; 0 until it is set (KT-126)
    half: str = "search"
    hosting: str = "in-process"

    def key(self) -> str:
        return json.dumps([self.mind, list(map(list, self.setting)), list(map(list, self.rate)), self.spike_nano,
                           self.half, self.hosting])


def spec_for(trial):
    specs = {s.label: s for s in agents.tower_minds(trial.spike_nano)}
    tuned = dict(trial.setting)
    if trial.mind == "TW7":
        base = specs["TW7"]
        params = {"twin": "TW7", "tuned": tuned, "rate": dict(trial.rate)}
        entry = "twins.entry:make"
    else:
        base = specs[trial.mind]
        params = {"tuned": tuned, "spike_nano": trial.spike_nano}
        if trial.mind == "OS10":
            params["OS10"] = True
        entry = "mind.entry:make"
    if trial.hosting == "in-process":
        return dataclasses.replace(base, host="in-process", entry=entry, params=params)
    return dataclasses.replace(base, params=params)


def stability(rec) -> dict:
    """Section 11's stability on near-ties, from the decision logs (KT-127). Reported only."""
    out = {"decisions": 0, "unsettled": 0, "hold_broke": 0, "leads_unknown": 0, "oscillating": 0,
           "near_tie_steps": 0, "steps": 0, "holds_broken": 0}
    for d in rec.decisions.values():
        lg = d["mind"]["log"]
        out["decisions"] += 1
        out["steps"] += lg["last_step"]
        out["near_tie_steps"] += lg["near_ties"]
        out["holds_broken"] += len(lg["holds_broken"])
        if d["mind"]["verdict"] == "unsettled":
            out["unsettled"] += 1
            out["hold_broke" if lg["unsettled_why"].startswith("a hold") else "leads_unknown"] += 1
        runs, last = [], None
        for g in lg["leaders"]:                  # a tie means no group leads (KT-56), so it breaks a lead
            if g is not None and g != last:
                runs.append(g)
            last = g
        if len(runs) > len(set(runs)):           # a group led, lost the lead and led again
            out["oscillating"] += 1
    return out


def _one(job):
    trial, family, run = job
    plan = generate_run(TUNING, keys.tuning_set_key(), family, run)
    spec = spec_for(trial)
    package = None if trial.hosting == "in-process" else ROOT / "src" / ("twins" if trial.mind == "TW7" else "mind")
    rec = run_one(plan, spec, ReadingCache(plan.noise_key), package_dir=package)
    used = [d["mind"]["thinking"]["count"] for d in rec.decisions.values()]
    checks = [d["mind"]["log"]["checks"] for d in rec.decisions.values()]
    return family, run, bench.core_placement(plan.family), scoring.measures(rec), stability(rec), used, checks


def run_trial(trial, families, workers):
    jobs = [(trial, f, r) for f in families for r in range(1, RUNS + 1)]
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            done = list(pool.map(_one, jobs, chunksize=1))
    else:
        done = [_one(j) for j in jobs]
    runs, core_of, stab, used, checks = {}, {}, {}, [], []
    for f, r, core, m, s, u, c in done:
        runs[(f, r)] = m
        core_of[f] = core
        for k, v in s.items():
            stab[k] = stab.get(k, 0) + v
        used += u
        checks += c
    return runs, core_of, stab, used, checks


def kt47_nano(median_spikes, median_checks) -> int:
    """KT-47's per-spike cost: 0.001 x median checks / median spikes, in whole nano-units, halves up (KT-92)."""
    exact = Fraction(K.CHECK_NANO) * Fraction(median_checks) / Fraction(median_spikes)
    return int(exact + Fraction(1, 2))


def costliest(trial, used, med_spikes, med_checks) -> dict:
    """The decision that thinks most, and what it would cost at this setting's own KT-47 rate (KT-126).

    A cost can change a choice only when one decision's thinking nears 10 units
    (skip's test, KT-48), so this shows whether paying 0 per spike during the
    search could have changed anything.
    """
    top = max(used)
    nano = K.CHECK_NANO if trial.mind == "TW7" else (trial.spike_nano or kt47_nano(med_spikes, med_checks))
    return {"most_in_one_decision": top, "unit_nano": nano,
            "milli": (2 * top * nano + K.NANO_PER_MILLI) // (2 * K.NANO_PER_MILLI)}


def median(xs) -> Fraction:
    xs = sorted(xs)
    n = len(xs)
    return Fraction(xs[n // 2]) if n % 2 else Fraction(xs[n // 2 - 1] + xs[n // 2], 2)


# ------------------------------------------------------------------ the targets (TUNING_PLAN.md, KT-128)

def floor_of(families, workers):
    specs = [agents.b1n_bot_r(agents.RADIUS_B1N_BOT_R), agents.b1n_mind(agents.RADIUS_B1N_MIND)]
    measures, core_of, _ = bench.run_set(TUNING, keys.tuning_set_key(), families, specs, runs=RUNS, workers=workers)
    minds = {"B1n-bot-r": measures[specs[0].label], "B1n-mind": measures[specs[1].label]}
    name, value = judge.floor(minds)
    return {"floor_mind": name, "floor": value,
            "means": {n: judge.set_mean(m, "d_learn_beh") for n, m in minds.items()}}, minds, core_of


def targets(runs, core_of, floor_value, spreads):
    """Every target on one half, met or missed, with each shortfall in spreads between families (KT-128)."""
    d_target = max(T_D_LEARN, floor_value + T_D_OVER_FLOOR)
    whole = (("settle_rate", ">=", T_SETTLE), ("copy_accept", ">=", T_COPY), ("d_learn_strict", ">=", d_target),
             ("fmn_strict", ">=", T_FMN), ("lr_h1", ">=", T_LOOK), ("lr_far", ">=", T_LOOK),
             ("dq_sour_strict", ">=", T_Q), ("sour_drop_strict", "<=", T_SOUR_DROP), ("noticed", ">=", T_NOTICED))
    rows = []
    for field, sense, aim in whole:
        rows.append(_row(field, "all runs", judge.count_runs(runs), judge.set_mean(runs, field), sense, aim, spreads))
    groups = [(name, fams, None) for name, fams in judge.core_groups(core_of).items()]
    groups += [("h1: new candidate", None, lambda m: bool(m["h1_new"])),
               ("h1: old candidate", None, lambda m: not m["h1_new"])]
    for name, fams, keep in groups:                       # rules 4, 4b and 4c in every subgroup of 100+ runs
        n = judge.count_runs(runs, fams, keep)
        if n < judge.SUBGROUP_MIN_RUNS:
            continue
        for field, aim in (("d_learn_strict", T_D_LEARN), ("fmn_strict", T_FMN), ("lr_h1", T_LOOK),
                           ("lr_far", T_LOOK)):
            rows.append(_row(field, name, n, judge.set_mean(runs, field, fams, keep), ">=", aim, spreads))
    misses = sum(1 for r in rows if not r["met"])
    shortfall = sum((r["shortfall"] for r in rows), Fraction(0))
    return {"rows": rows, "misses": misses, "shortfall": shortfall, "every_target": misses == 0,
            "d_check1": judge.set_mean(runs, "d_strict_1")}


def _row(field, group, n, value, sense, aim, spreads):
    met = value >= aim if sense == ">=" else value <= aim
    gap = Fraction(0) if met else (aim - value if sense == ">=" else value - aim)
    return {"measure": field, "group": group, "runs": n, "value": value, "sense": sense, "target": aim,
            "met": met, "shortfall": gap / Fraction(spreads[SPREAD_KEY[field]])}


def better(a, b) -> bool:
    """a misses fewer targets than b, or as many by less (TUNING_PLAN.md, step 3)."""
    return (a["misses"], a["shortfall"]) < (b["misses"], b["shortfall"])


# ------------------------------------------------------------------ the log

class Log:
    """Append-only. On a second run each event is compared with the one already logged (KT-130)."""

    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.old = []
        for k, line in enumerate(self.path.read_text().splitlines() if self.path.exists() else []):
            try:
                self.old.append(json.loads(line))
            except json.JSONDecodeError:
                raise SystemExit(f"line {k + 1} of {self.path} is not a whole event (a run stopped while "
                                 "writing it?): remove it by hand, note why in the commit, and run again")
        self.n = 0
        self.measured = {e["trial"]: e for e in self.old if e["type"] == "setting" and "measures" in e}

    def add(self, event):
        event = dict(plain(event), n=self.n)
        if self.n < len(self.old):
            logged = {k: v for k, v in self.old[self.n].items() if k not in ("seconds", "commit", "at")}
            ours = {k: v for k, v in event.items() if k not in ("seconds", "commit", "at")}
            if logged != ours:
                raise SystemExit(f"event {self.n} differs from the logged one: the search is not replaying\n"
                                 f"logged: {json.dumps(logged)[:400]}\nnow: {json.dumps(ours)[:400]}")
        else:
            event["at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            with self.path.open("a") as f:
                f.write(json.dumps(event, sort_keys=True) + "\n")
            print(_line(event), flush=True)
        self.n += 1
        return event


def _line(e):
    if e["type"] != "setting":
        return f"[{e['n']}] {e['type']}: " + json.dumps({k: v for k, v in e.items() if k not in ("n", "type", "at")})[:300]
    head = (f"[{e['n']}] {e.get('mind', '')} {e.get('half', '')} {e.get('step', '')} {e.get('row', '')} "
            f"{e.get('name', '')}={e.get('value', '')}")
    if "targets" not in e:
        return head
    t = e["targets"]
    return (f"{head}: misses {t['misses']}, shortfall {t['shortfall']['value']:.3f}, D1 {t['d_check1']['value']:.3f}"
            f"{' (same as ' + str(e['same_as']) + ')' if 'same_as' in e else ''}")


def code_state():
    """The code a log belongs to: git's ids for src/ and this tool at HEAD (KT-130)."""
    ids = {}
    for path in ("src", "kill-test/tune.py", "uv.lock", "kill-test/results/tuning-bench.json"):
        ids[path] = subprocess.run(["git", "rev-parse", f"HEAD:{path}"], cwd=ROOT, capture_output=True,
                                   text=True).stdout.strip()
    return ids


def commit_state():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain", "src", "kill-test/tune.py", "uv.lock", "pyproject.toml",
                            "kill-test/results/tuning-bench.json"],
                           cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return head, dirty


# ------------------------------------------------------------------ the search

class Search:
    def __init__(self, log, workers, spreads, commit):
        self.log, self.workers, self.spreads, self.commit = log, workers, spreads, commit
        self.floors = {}
        self.seen = {}           # trial key -> the event that measured it

    def floor(self, half):
        if half not in self.floors:
            families = SEARCH if half == "search" else KEPT_BACK
            t0 = time.time()
            f, minds, core_of = floor_of(families, self.workers)
            self.log.add({"type": "floor", "half": half, "families": list(families), **f,
                          "seconds": round(time.time() - t0, 1), "commit": self.commit})
            self.floors[half] = (f, minds, core_of)
        return self.floors[half]

    def measure(self, trial, what, keep_runs=False):
        """Measure one setting on its half, or reuse the earlier measurement of the same setting (KT-130)."""
        key = trial.key()
        if key in self.seen and not keep_runs:
            e = self.seen[key]
            out = self.log.add(dict(what, type="setting", trial=key, same_as=e["n"], targets=e["targets"]))
            return unplain(out["targets"]), None
        f, _, _ = self.floor(trial.half)
        families = SEARCH if trial.half == "search" else KEPT_BACK
        logged = self.log.measured.get(key)
        t0 = time.time()
        if logged is not None and not keep_runs:
            runs = None
            measures, tg = unplain(logged["measures"]), unplain(logged["targets"])
            stab, kt47, costly, core_of = logged["stability"], unplain(logged["kt47"]), logged["costliest"], None
        else:
            runs, core_of, stab, used, checks = run_trial(trial, families, self.workers)
            tg = targets(runs, core_of, f["floor"], self.spreads)
            measures = {fld: judge.set_mean(runs, fld) for fld in
                        ("settle_rate", "copy_accept", "d_learn_strict", "fmn_strict", "lr_h1", "lr_far",
                         "dq_sour_strict", "sour_drop_strict", "noticed", "d_strict_1", "d_learn_beh",
                         "dq_s8_strict", "dq_sweet_strict")}
            kt47 = {"median_spikes": median(used), "median_checks": median(checks)}
            costly = costliest(trial, used, kt47["median_spikes"], kt47["median_checks"])
        event = dict(what, type="setting", trial=key, mind=trial.mind, half=trial.half, hosting=trial.hosting,
                     setting=dict(trial.setting), rate=dict(trial.rate), spike_nano=trial.spike_nano,
                     families=list(families), runs_per_family=RUNS, measures=measures, targets=tg,
                     stability=stab, kt47=kt47, costliest=costly, floor=f["floor"],
                     seconds=round(time.time() - t0, 1), commit=self.commit)
        out = self.log.add(event)
        self.seen[key] = out
        return tg, runs

    def repeats(self, logged) -> bool:
        """On a resume, the last setting the log measured is run again and must give the same numbers (KT-130)."""
        families = tuple(logged["families"])
        setting = tuple((name, logged["setting"][name]) for _, name, _ in KF_GRID)       # the log sorts keys
        rate = tuple((name, logged["rate"][name]) for _, name, _ in TW7_GRID if name in logged["rate"])
        trial = Trial(logged["mind"], setting, rate=rate, spike_nano=logged["spike_nano"], half=logged["half"],
                      hosting=logged["hosting"])
        if trial.key() != logged["trial"]:
            print("the log's last measured setting does not rebuild to its own trial key")
            return False
        runs, core_of, stab, used, checks = run_trial(trial, families, self.workers)
        tg = targets(runs, core_of, Fraction(logged["floor"]["exact"]), self.spreads)
        same = plain(tg) == logged["targets"] and stab == logged["stability"]
        print(f"resume: setting {logged['n']} measured again: {'the same' if same else 'DIFFERENT'}", flush=True)
        return same

    def leak_stop(self, tg) -> bool:
        if tg["d_check1"] >= LEAK_STOP:
            self.log.add({"type": "stop", "why": "D at check 1 is 0.15 or more: a possible leak, to trace with "
                          "Aitzaz (TUNING_PLAN.md)", "d_check1": tg["d_check1"]})
            return True
        return False

    def coordinate(self, mind, grid, start, passes, fixed=(), rate_mode=False, spike_nano=0, label="start"):
        """Steps 2 to 5: passes through the grid one number at a time.

        Returns (values, passes used, how): how is "pick" when a setting reached
        every target (values is it), "leak" after a leak stop, or "passes" when
        none did (values is the setting the passes ended on).
        """
        current = dict(start)

        def trial(values):
            if rate_mode:
                return Trial(mind, tuple(fixed), rate=tuple(values.items()))
            return Trial(mind, tuple(values.items()), spike_nano=spike_nano)

        tg, _ = self.measure(trial(current), {"step": label})
        if self.leak_stop(tg):
            return current, passes.start - 1, "leak"
        best_tg = tg
        if tg["every_target"]:
            self.log.add({"type": "pick", "mind": mind, "values": current, "passes": passes.start - 1})
            return current, passes.start - 1, "pick"
        for p in passes:
            for row, name, values in grid:
                here = {current[name]: best_tg}
                for v in values:
                    if v == current[name]:
                        continue
                    cand = dict(current, **{name: v})
                    tg, _ = self.measure(trial(cand), {"step": "pass", "pass": p, "row": row, "name": name,
                                                       "value": v})
                    if self.leak_stop(tg):
                        return cand, p, "leak"
                    if tg["every_target"]:
                        self.log.add({"type": "pick", "mind": mind, "values": cand, "passes": p})
                        return cand, p, "pick"
                    here[v] = tg
                keep = current[name]
                for v in values:                            # the table's order; a tie keeps the current value
                    if v != keep and better(here[v], here[keep]):
                        keep = v
                self.log.add({"type": "keep", "mind": mind, "pass": p, "row": row, "name": name, "value": keep,
                              "was": current[name], "misses": here[keep]["misses"],
                              "shortfall": here[keep]["shortfall"]})
                current[name], best_tg = keep, here[keep]
        self.log.add({"type": "no pick", "mind": mind, "passes": passes.stop - 1, "values": current,
                      "why": f"no setting reached every target by pass {passes.stop - 1} (TUNING_PLAN.md, step 5)"})
        return current, passes.stop - 1, "passes"

    def check(self, mind, setting, rate, spike_nano, os10_runs=None):
        """Step 7: the pick on the kept-back half, judged as on a kill-run set (KT-131)."""
        f, minds, core_of = self.floor("kept-back")
        t = Trial(mind, tuple(setting.items()), rate=tuple(rate.items()), spike_nano=spike_nano,
                  half="kept-back", hosting="subprocess")
        _, runs = self.measure(t, {"step": "check"}, keep_runs=True)
        if os10_runs is None:
            o = Trial("OS10", tuple(setting.items()), spike_nano=spike_nano, half="kept-back", hosting="subprocess")
            _, os10_runs = self.measure(o, {"step": "check"}, keep_runs=True)
        verdict = judge.judge(CHECK_SET_NAME, runs, minds[f["floor_mind"]], f["floor"], os10_runs, core_of)
        self.log.add({"type": "check", "mind": mind, "verdict": verdict["verdict"], "label": verdict["label"],
                      "causes": verdict["causes"], "rules": {k: v for k, v in verdict.items()
                                                             if k in ("1", "2", "3", "5", "7")},
                      "disc": verdict["disc"]})
        return verdict["verdict"] == "GO", os10_runs

    def kt27(self, setting):
        """Step 6: KT-27 by KT-47's rule at the pick (KT-47, KT-92, KT-126)."""
        t = Trial("K-F", tuple(setting.items()))
        e = self.seen[t.key()]
        med_spikes, med_checks = Fraction(e["kt47"]["median_spikes"]["exact"]), \
            Fraction(e["kt47"]["median_checks"]["exact"])
        exact = Fraction(K.CHECK_NANO) * med_checks / med_spikes
        nano = kt47_nano(med_spikes, med_checks)            # whole nano-units, halves up (KT-92)
        self.log.add({"type": "kt27", "median_spikes": med_spikes, "median_checks": med_checks,
                      "spike_nano_exact": exact, "spike_nano": nano})
        return nano


def run(log_path, workers) -> int:
    head, dirty = commit_state()
    if dirty:
        print(f"the mind's code or this tool has uncommitted changes; commit them first:\n{dirty}")
        return 1
    code = code_state()
    log = Log(log_path)
    if log.old and log.old[0].get("code") != code:
        print("this log was made by other code: start a new log, or go back to that code (KT-130)")
        return 1
    spreads = json.loads((ROOT / "kill-test" / "results" / "tuning-bench.json").read_text())["mk10_spreads"]["between"]
    s = Search(log, workers, spreads, head)
    if log.measured and not s.repeats(list(log.measured.values())[-1]):
        return 1
    log.add({"type": "begin", "code": code, "search": list(SEARCH), "kept_back": list(KEPT_BACK),
             "runs_per_family": RUNS, "max_passes": MAX_PASSES, "spreads": spreads})
    s.floor("search")
    pick, passes, how = s.coordinate("K-F", KF_GRID, KF_START, range(1, MAX_PASSES + 1))
    if how != "pick":
        if how == "passes":
            log.add({"type": "stop", "why": "3 passes and no setting reached every target: the numbers go to "
                     "Aitzaz, and nothing more is tuned without Aitzaz (TUNING_PLAN.md, step 5)"})
        return 2
    nano = s.kt27(pick)                                                       # step 6
    tg, _ = s.measure(Trial("K-F", tuple(pick.items()), spike_nano=nano), {"step": "with KT-27"})
    if s.leak_stop(tg):
        return 2
    if not tg["every_target"]:
        log.add({"type": "kt27 knocked a target out", "passes_used": passes})
        if passes >= MAX_PASSES:
            log.add({"type": "stop", "why": "KT-27 knocked a target out and all 3 passes are used (step 6)"})
            return 2
        pick, more, how = s.coordinate("K-F", KF_GRID, pick, range(passes + 1, passes + 2), spike_nano=nano,
                                       label="extra pass start")
        if how != "pick":
            if how == "passes":
                log.add({"type": "stop", "why": "step 6's extra pass found no setting reaching every target"})
            return 2
        passes = more
    ok, os10_runs = s.check("K-F", pick, {}, nano)                           # step 7
    if not ok:
        log.add({"type": "stop", "why": "the pick failed the check on the kept-back half (step 7): to Aitzaz"})
        return 2
    tw7_start = {"gain": GAIN_START, "tau_ms": TAU_START}                    # step 8
    tw7, tw7_passes, how = s.coordinate("TW7", TW7_GRID, tw7_start, range(1, passes + 1),
                                        fixed=tuple(pick.items()), rate_mode=True)
    if how == "leak":                                                         # logged by the leak stop
        return 2
    ok7, _ = s.check("TW7", pick, tw7, 0, os10_runs=os10_runs)
    log.add({"type": "done", "pick": pick, "spike_nano": nano, "passes": passes, "tw7": tw7,
             "tw7_reached_every_target": how == "pick", "tw7_check_go": ok7})
    return 0


def summary(log_path) -> int:
    for line in pathlib.Path(log_path).read_text().splitlines():
        print(_line(json.loads(line)))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    r = sub.add_parser("run")
    r.add_argument("log")
    r.add_argument("--workers", type=int, default=1)
    m = sub.add_parser("summary")
    m.add_argument("log")
    a = ap.parse_args(argv)
    if a.mode == "run":
        return run(a.log, a.workers)
    return summary(a.log)


if __name__ == "__main__":
    sys.exit(main())
