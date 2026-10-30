"""Pass and fail, fixed now (section 9): the set-level judge of the frozen analysis script.

It takes per-run measure records (scoring.py for real minds; MK10's records in
the power check, test_fixtures/mk10.py) and applies section 9 mechanically.
Every mean is the mean of the family means (section 8). Observed measures are
exact fractions and MK10's are floats, which are turned into fractions
exactly, so every pass mark is compared exactly, with no tolerance (KT-103).

Rule 3's paired family-cluster bootstrap (X31) resamples the family
differences 10,000 times. The resample indices come from a Philox stream keyed
by the frozen seed and the set (KT-105); every comparison on a set uses the
same indices. "The 2.5th percentile is above 0" is read by nearest rank: the
250th smallest of the 10,000 resampled means is above 0, so at most 249 of
them are at or below 0 (KT-105). For a bot (rule 6) the 5th percentile is used
the same way: at most 499.
"""

import hashlib
import hmac
from fractions import Fraction
from math import lcm

import numpy as np

# Section 9's pass marks
SETTLE_MIN = Fraction(95, 100)        # rule 1: at least 95% of K-F decisions settle
COPY_ACCEPT_MIN = Fraction(80, 100)   # rule 2: CopyAccept at least 0.80
MARGIN = Fraction(15, 100)            # rule 3: at least 0.15 above the floor
D_LEARN_MIN = Fraction(25, 100)       # rule 4: D_learn at least 0.25
FMN_MIN = Fraction(15, 100)           # rule 4b: FarMinusNeutral at least 0.15
LOOK_REJECT_MIN = Fraction(60, 100)   # rule 4c: LookReject at least 0.60 in each half
SOUR_DROP_MAX = Fraction(15, 100)     # rule 5: sour drop at most 0.15
Q_MIN = Fraction(25, 100)             # rule 5 (and its Q bar for bots): D on Q after SOUR at least 0.25
NOTICED_MIN = Fraction(50, 100)       # rule 5 applicability: at least 50% of runs noticed
OS10_QUIET_MIN = Fraction(90, 100)    # rule 5 applicability: OS10 not noticing in at least 90% of runs
LEAK_MAX = Fraction(15, 100)          # rule 7: D_strict at check 1 below 0.15
SUBGROUP_MIN_RUNS = 100               # a subgroup's rule applies with at least 100 runs (section 9)
RESAMPLES = 10_000                    # the bootstrap resamples 10,000 times (section 9, X31)
LEVEL_KF = 250                        # 2.5th percentile of 10,000, by nearest rank (section 9, KT-105)
LEVEL_BOT = 500                       # 5th percentile of 10,000, by nearest rank (section 9, X32, KT-105)
# The bootstrap seed, frozen in the analysis script (section 9, KT-105): the SHA-256 of this text.
BOOTSTRAP_SEED_TEXT = "FRANKIE kill test: rule 3 bootstrap seed, fixed 30 Oct 2026 before any result"
BOOTSTRAP_SEED = hashlib.sha256(BOOTSTRAP_SEED_TEXT.encode("ascii")).digest()

FLOOR_MINDS = ("B1n-bot-r", "B1n-mind")     # the floor is the higher of the two; a tie goes to the first (KT-105)


def frac(x) -> Fraction:
    """A measure as an exact fraction (MK10's floats convert exactly)."""
    if isinstance(x, bool):
        return Fraction(int(x))
    return x if isinstance(x, Fraction) else Fraction(x)


def family_means(runs: dict, field: str, families=None, keep=None) -> dict:
    """Per family, the mean of field over its runs (only runs for which keep(run) holds)."""
    by_family = {}
    for (f, r), m in runs.items():
        if families is not None and f not in families:
            continue
        if keep is not None and not keep(m):
            continue
        by_family.setdefault(f, []).append(frac(m[field]))
    return {f: sum(v, Fraction(0)) / len(v) for f, v in by_family.items()}


def set_mean(runs: dict, field: str, families=None, keep=None) -> Fraction:
    """The mean of the family means (section 8); in a subgroup, of the families that have runs in it."""
    fm = family_means(runs, field, families, keep)
    return sum(fm.values(), Fraction(0)) / len(fm)


def count_runs(runs: dict, families=None, keep=None) -> int:
    return sum(1 for (f, r), m in runs.items()
               if (families is None or f in families) and (keep is None or keep(m)))


def resample_indices(set_name: str, n_families: int) -> np.ndarray:
    """The frozen bootstrap's 10,000 x n family indices for a set (KT-105)."""
    key = int.from_bytes(hmac.new(BOOTSTRAP_SEED, f"bootstrap/{set_name}/{n_families}".encode("ascii"),
                                  hashlib.sha256).digest()[:16], "little")
    gen = np.random.Generator(np.random.Philox(key=key))
    return gen.integers(0, n_families, size=(RESAMPLES, n_families), dtype=np.int64)


def bootstrap_at_or_below_zero(diffs: dict, indices: np.ndarray, families: list) -> int:
    """How many of the resampled means of the family differences are at or below 0, exactly."""
    vals = [diffs[f] for f in families]
    scale = lcm(*(v.denominator for v in vals))
    ints = np.array([int(v * scale) for v in vals], dtype=object)
    sums = ints[indices].sum(axis=1)
    return int(sum(1 for s in sums if s <= 0))


def paired_differences(a: dict, b: dict, field_a: str, field_b: str, families: list) -> dict:
    """Per family, the mean over its runs of a minus b, paired by run key (section 9, X31)."""
    out = {}
    for f in families:
        runs_a = {r: m for (ff, r), m in a.items() if ff == f}
        runs_b = {r: m for (ff, r), m in b.items() if ff == f}
        if set(runs_a) != set(runs_b) or not runs_a:
            raise ValueError(f"family {f}: runs are not paired by run key (section 9)")
        out[f] = sum((frac(runs_a[r][field_a]) - frac(runs_b[r][field_b]) for r in runs_a),
                     Fraction(0)) / len(runs_a)
    return out


def floor(minds: dict) -> tuple:
    """(floor mind, floor): the higher mean D_learn (D_beh) of B1n-bot-r and B1n-mind (rule 3)."""
    best = None
    for name in FLOOR_MINDS:
        v = set_mean(minds[name], "d_learn_beh")
        if best is None or v > best[1]:
            best = (name, v)
    return best


def _subgroups_hold(runs, field, test, core_groups, extra_groups=()):
    """A rule also holds in every subgroup with at least 100 runs (section 9)."""
    rows = []
    for name, families in core_groups.items():
        n = count_runs(runs, families)
        if n >= SUBGROUP_MIN_RUNS:
            v = set_mean(runs, field, families)
            rows.append((name, n, v, test(v)))
    for name, keep in extra_groups:
        n = count_runs(runs, keep=keep)
        if n >= SUBGROUP_MIN_RUNS:
            v = set_mean(runs, field, keep=keep)
            rows.append((name, n, v, test(v)))
    return rows


def discrimination(runs, prefix, core_groups, extra_groups=()):
    """Rules 4, 4b and 4c on one mind, with their subgroup checks (section 9)."""
    d_field, fmn_field = f"d_learn_{prefix}", f"fmn_{prefix}"
    out = {}
    for rule, fields, test in (("4", (d_field,), lambda v: v >= D_LEARN_MIN),
                               ("4b", (fmn_field,), lambda v: v >= FMN_MIN),
                               ("4c", ("lr_h1", "lr_far"), lambda v: v >= LOOK_REJECT_MIN)):
        whole = {f: set_mean(runs, f) for f in fields}
        subs = {f: _subgroups_hold(runs, f, test, core_groups, extra_groups) for f in fields}
        ok = all(test(v) for v in whole.values()) and all(row[3] for rows in subs.values() for row in rows)
        out[rule] = {"values": whole, "subgroups": subs, "pass": ok}
    return out


def core_groups(core_of: dict) -> dict:
    """Families by where H's core traits sit: any in the object layer, or none (section 9)."""
    return {"core: object layer": {f for f, g in core_of.items() if g == "object"},
            "core: none": {f for f, g in core_of.items() if g == "none"}}


def rule6(set_name: str, minds: dict, core_of: dict, must_fail: list) -> dict:
    """Bench validity (rule 6), judged on non-tower minds before any tower mind runs."""
    families = sorted(core_of)
    fmind, fval = floor(minds)
    idx = resample_indices(set_name, len(families))
    groups = core_groups(core_of)
    table = {}
    for label in must_fail:
        runs = minds[label]
        d = set_mean(runs, "d_learn_beh")
        diffs = paired_differences(runs, minds[fmind], "d_learn_beh", "d_learn_beh", families)
        low = bootstrap_at_or_below_zero(diffs, idx, families)
        r3 = d >= fval + MARGIN and low < LEVEL_BOT
        disc = discrimination(runs, "beh", groups)
        q = set_mean(runs, "dq_sour_beh")
        passes = {"3": r3, "4": disc["4"]["pass"], "4b": disc["4b"]["pass"], "4c": disc["4c"]["pass"],
                  "Q": q >= Q_MIN}
        table[label] = {"d_learn": d, "bootstrap_at_or_below_0": low, "discrimination": disc, "q": q,
                        "passes": passes, "fails_one": not all(passes.values())}
    return {"floor_mind": fmind, "floor": fval, "bots": table,
            "holds": all(row["fails_one"] for row in table.values())}


def positive_control(runs: dict, core_of: dict) -> dict:
    """B2e passes rules 4, 4b and 4c, with subgroups, and rule 5's Q bar (section 7, step 3)."""
    disc = discrimination(runs, "beh", core_groups(core_of))
    q = set_mean(runs, "dq_sour_beh")
    ok = disc["4"]["pass"] and disc["4b"]["pass"] and disc["4c"]["pass"] and q >= Q_MIN
    return {"discrimination": disc, "q": q, "pass": ok}


def judge(set_name: str, kf: dict, floor_runs: dict, floor_value, os10: dict, core_of: dict) -> dict:
    """Rules 1 to 5 and 7 on K-F's runs, and the verdict order (section 9)."""
    families = sorted(core_of)
    idx = resample_indices(set_name, len(families))
    out = {}
    out["1"] = {"value": set_mean(kf, "settle_rate")}
    out["1"]["pass"] = out["1"]["value"] >= SETTLE_MIN
    out["2"] = {"value": set_mean(kf, "copy_accept")}
    out["2"]["pass"] = out["2"]["value"] >= COPY_ACCEPT_MIN
    d = set_mean(kf, "d_learn_strict")
    diffs = paired_differences(kf, floor_runs, "d_learn_strict", "d_learn_beh", families)
    low = bootstrap_at_or_below_zero(diffs, idx, families)
    out["3"] = {"value": d, "floor": floor_value, "margin_pass": d >= floor_value + MARGIN,
                "bootstrap_at_or_below_0": low, "bootstrap_pass": low < LEVEL_KF}
    cand = (("h1: new candidate", lambda m: bool(m["h1_new"])), ("h1: old candidate", lambda m: not m["h1_new"]))
    out["disc"] = discrimination(kf, "strict", core_groups(core_of), cand)
    sour = set_mean(kf, "sour_drop_strict")
    q = set_mean(kf, "dq_sour_strict")
    noticed = set_mean(kf, "noticed")
    quiet = 1 - set_mean(os10, "noticed")
    applicable = noticed >= NOTICED_MIN and quiet >= OS10_QUIET_MIN
    out["5"] = {"sour_drop": sour, "q": q, "noticed": noticed, "os10_not_noticing": quiet,
                "applicable": applicable, "pass": applicable and sour <= SOUR_DROP_MAX and q >= Q_MIN}
    leak = set_mean(kf, "d_strict_1")
    out["7"] = {"value": leak, "pass": leak < LEAK_MAX}
    causes = []
    if not out["3"]["margin_pass"]:
        causes.append("rule 3 margin")
    for rule in ("4", "4b", "4c"):
        if not out["disc"][rule]["pass"]:
            causes.append(f"rule {rule}")
    if not applicable:
        causes.append("rule 5 uninformative")
    elif not out["5"]["pass"]:
        causes.append("rule 5")
    if not out["7"]["pass"]:
        causes.append("rule 7 (possible essence leak: trace it with Aitzaz)")
    if not out["1"]["pass"] or not out["2"]["pass"]:
        verdict = "NO-GO"
        label = "; ".join(t for t, ok in (("decisions don't settle", out["1"]["pass"]),
                                          ("h1 wasn't learned", out["2"]["pass"])) if not ok)
    elif not out["3"]["bootstrap_pass"]:
        verdict, label = "NO-GO", "not better than brute trial and error"
    elif not causes:
        verdict, label = "GO", ""
    else:
        verdict, label = "INCONCLUSIVE", "; ".join(causes)
    out["verdict"], out["label"], out["causes"] = verdict, label, causes
    return out


def programme_outcome(verdict: str, evaluation: int) -> str:
    """Section 3: on K-F's second judged set, GO needs every rule and anything else is NO-GO."""
    if evaluation not in (1, 2):
        raise ValueError("K-F is judged on at most two sets (section 3)")
    if evaluation == 2 and verdict != "GO":
        return "NO-GO"
    return verdict
