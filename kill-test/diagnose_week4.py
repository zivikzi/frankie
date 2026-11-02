"""Why K-F falls short after the Week 4 search: a read-only diagnosis (Aitzaz chose "Diagnose first", 2 Nov 2026).

    python kill-test/diagnose_week4.py OUT.json [--workers N]

Runs K-F at the setting the search ended on (the fewest misses after 3 passes,
kill-test/results/tuning-search.jsonl), and TW7 at the same values with its own
start values, on the search half only (the 15 odd tuning families, 10 runs
each). The kept-back half stays untouched. Nothing is tuned and no value in the
mind's code changes: it only reads the runs' own records.

It reads each run's record on the harness's side, where the world's facts
(which traits are core, which look-alike moved which pair) are known. The
mind never sees any of it (FORBIDDEN 18). For each run it counts:

- warm-up: how its 40 forced tastes were written (new kinds, stretches,
  splits, marks), and how many kinds they made;
- the teaching apples a2 to a4: their verdict before eating (an H-set kind,
  another kind, "unknown" or unsettled) and their write;
- the teaching look-alikes: their verdict, their write, the layer blamed,
  and whether any trait that gained weight is one of the 2 core traits the
  look-alike's kind moved;
- at check 8: the far apples' and the look-alikes' verdicts and eats;
- objections, resets and removals per decision, and the size of the race.
"""

import argparse
import json
import pathlib
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "kill-test"))

import tune  # noqa: E402
from harness import judge, scoring  # noqa: E402
from harness.readings_cache import ReadingCache  # noqa: E402
from harness.run import run_one  # noqa: E402
from world import keys, traits  # noqa: E402
from world.run_plan import generate_run  # noqa: E402

LOOK_PAIR = {"t2": 0, "t4": 1, "t6": 0, "t8": 1}       # teaching look-alikes use kind 1, 2, 1, 2 (KT-07)
APPLES = ("t3", "t5", "t7")


def ended_on(log_path):
    events = [json.loads(line) for line in pathlib.Path(log_path).read_text().splitlines()]
    last = [e for e in events if e["type"] == "no pick" and e["mind"] == "K-F"]
    if not last:
        raise SystemExit("the log has no K-F 'no pick' event")
    return last[-1]["values"]


def verdict_kind(lid, h):
    if lid in ("unknown", "unsettled"):
        return lid
    return "H set" if lid in h else "other kind"


def one(job):
    trial, family, run = job
    plan = generate_run("tuning", keys.tuning_set_key(), family, run)
    rec = run_one(plan, tune.spec_for(trial), ReadingCache(plan.noise_key))
    core = set(plan.family.H.core)
    pairs = plan.family.teaching_pairs
    out = Counter()
    h8 = rec.h_sets["S8"]
    for d in rec.decisions.values():
        lg = d["mind"]["log"]
        out["decisions"] += 1
        out["objections"] += len(lg["objections"])
        out["resets"] += sum(1 for o in lg["objections"] if o[3] == "reset")
        out["removals"] += sum(1 for o in lg["objections"] if o[3] == "removed")
        out["eliminated"] += len(lg["eliminated"])
        out["race_at_end"] += 1 + len(lg["within_margin"])
        item = d.get("item", "")
        events = [e for e in d.get("write", {}).get("events", []) if e["type"] != "forget"]
        kind = events[0]["type"] if events else None
        if item.startswith("warmup"):
            out[f"warmup write {kind}"] += 1
        if item in APPLES:
            out[f"apple verdict {verdict_kind(d['verdict_lid'], h8)}"] += 1
            out[f"apple write {kind}"] += 1
        if item in LOOK_PAIR:
            moved = set(pairs[LOOK_PAIR[item]])
            out[f"look-alike verdict {verdict_kind(d['verdict_lid'], h8)}"] += 1
            out[f"look-alike write {kind}"] += 1
            if kind == "split":
                ev = events[0]
                out[f"look-alike blamed {ev['layer']}"] += 1
                raised = {t for _, t, ch in ev["weight_deltas"] if ch > 0}
                out["look-alike split raised a moved core trait"] += bool(raised & moved)
                out["look-alike split raised only other traits"] += bool(raised) and not (raised & moved)
                out["look-alike split traits raised"] += len(raised)
                out["look-alike split raised a taste trait"] += bool(raised & set(traits.TASTE_INDICES))
    for p in rec.probes:
        if p["state"] != "S8":
            continue
        if p["role"] == "far":
            out[f"S8 far verdict {verdict_kind(p['verdict'], h8)}"] += 1
            out["S8 far eaten naming H"] += p["ate"] and p["names_h"]
            if p["verdict"] == "unsettled":
                both = rec.decisions[p["decision"]]["leader_and_runner_up_in_h"]
                out["S8 far unsettled, leader and a runner-up both apple kinds"] += bool(both)
        if p["role"].startswith("look"):
            out[f"S8 look-alike verdict {verdict_kind(p['verdict'], h8)}"] += 1
            out["S8 look-alike eaten"] += p["ate"]
        if p["role"] == "copy":
            out[f"S8 copy verdict {verdict_kind(p['verdict'], h8)}"] += 1
    warm = [e for e in rec.lineage_log if e["item"].startswith("warmup") and e["type"] in ("new", "split")]
    out["kinds made in warm-up"] += len(warm)
    out["core traits in object layer"] += sum(1 for t in core if traits.LAYER_OF[traits.TRAITS[t]] == "object")
    return family, run, scoring.measures(rec), dict(out)


def look(trial, workers):
    jobs = [(trial, f, r) for f in tune.SEARCH for r in range(1, tune.RUNS + 1)]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        done = list(pool.map(one, jobs, chunksize=1))
    runs, total = {}, Counter()
    for f, r, m, c in done:
        runs[(f, r)] = m
        total.update(c)
    fields = ("settle_rate", "copy_accept", "d_learn_strict", "fmn_strict", "lr_h1", "lr_far", "dq_sour_strict",
              "sour_drop_strict", "noticed", "d_strict_1", "d_learn_beh")
    return {"measures": {f: float(judge.set_mean(runs, f)) for f in fields}, "counts": dict(sorted(total.items())),
            "runs": len(runs)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("out")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    best = ended_on(ROOT / "kill-test" / "results" / "tuning-search.jsonl")
    setting = tuple((name, best[name]) for _, name, _ in tune.KF_GRID)
    report = {"what": "read-only diagnosis on the search half (Aitzaz's choice, 2 Nov 2026)", "setting": best}
    report["K-F"] = look(tune.Trial("K-F", setting), a.workers)
    report["TW7"] = look(tune.Trial("TW7", setting, rate=(("gain", tune.GAIN_START), ("tau_ms", tune.TAU_START))),
                         a.workers)
    pathlib.Path(a.out).write_text(json.dumps(report, indent=1, sort_keys=True) + "\n")
    for mind in ("K-F", "TW7"):
        print(mind, {k: round(v, 3) for k, v in report[mind]["measures"].items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
