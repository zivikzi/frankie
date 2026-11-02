"""Judge E1 against trial and error on one half with the frozen judge's own statistics (Frankie Lab).

    uv run python explore/judge_lab.py [--half even] [--mind E1]

Not a kill-run verdict: these are tuning families, and E1 was developed on
the odd half. It applies rule 3's paired family-cluster bootstrap and rules
4, 4b and 4c with their subgroups (harness/judge.py, unchanged) to show how
far the result is from chance. Rule 5's applicability needs a taste-blind
version (OS10), which E1 does not have, so rule 5 is shown without it.
"""

import argparse
import json
import pathlib
import sys
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import minds  # noqa: E402

from harness import judge  # noqa: E402


def runs_of(name, fams, workers=4):
    jobs = [(name, None, f, r) for f in fams for r in range(1, minds.RUNS + 1)]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        done = list(pool.map(minds.one, jobs, chunksize=2))
    return {(f, r): m for _, f, r, _, m in done}, {f: core for _, f, _, core, _ in done}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--half", default="even", choices=("odd", "even"))
    ap.add_argument("--mind", default="E1")
    a = ap.parse_args(argv)
    fams = list(minds.ODD if a.half == "odd" else minds.EVEN)
    mind, core_of = runs_of(a.mind, fams)
    floors = {n: runs_of(n, fams)[0] for n in ("B1n-bot-r", "B1n-mind")}
    floor_name, floor_value = judge.floor(floors)
    idx = judge.resample_indices(f"frankie-lab-{a.half}", len(fams))
    diffs = judge.paired_differences(mind, floors[floor_name], "d_learn_strict", "d_learn_beh", fams)
    low = judge.bootstrap_at_or_below_zero(diffs, idx, fams)
    margin = judge.set_mean(mind, "d_learn_strict") - floor_value
    low_margin = judge.bootstrap_at_or_below_zero({f: d - judge.MARGIN for f, d in diffs.items()}, idx, fams)
    cand = (("h1: new candidate", lambda m: bool(m["h1_new"])), ("h1: old candidate", lambda m: not m["h1_new"]))
    disc = judge.discrimination(mind, "strict", judge.core_groups(core_of), cand)
    out = {"half": a.half, "mind": a.mind, "floor_mind": floor_name, "floor": float(floor_value),
           "d_learn": float(judge.set_mean(mind, "d_learn_strict")), "margin_over_floor": float(margin),
           "rule3_bootstrap_at_or_below_0_of_10000": low, "rule3_bootstrap_pass": low < judge.LEVEL_KF,
           "bootstrap_means_at_or_below_floor_plus_0.15": low_margin,
           "rule4": {r: {"pass": v["pass"], "values": {k: float(x) for k, x in v["values"].items()},
                         "subgroups": {k: [[n, c, float(x), ok] for n, c, x, ok in rows] for k, rows in v["subgroups"].items()}}
                     for r, v in disc.items()},
           "rule1_settle": float(judge.set_mean(mind, "settle_rate")), "rule2_copy": float(judge.set_mean(mind, "copy_accept")),
           "rule5_sour_drop": float(judge.set_mean(mind, "sour_drop_strict")), "rule5_q": float(judge.set_mean(mind, "dq_sour_strict")),
           "rule5_noticed": float(judge.set_mean(mind, "noticed")), "rule7_d1": float(judge.set_mean(mind, "d_strict_1"))}
    path = minds.ROOT / "explore" / "results" / f"judge-{a.mind.replace(' ', '_')}-{a.half}.json"
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
