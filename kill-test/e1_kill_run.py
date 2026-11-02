"""E1's kill run, in the frozen order (kill-test/E1_ADDENDUM.md, KILL_TEST.md sections 3 and 9, KT-137).

    python kill-test/e1_kill_run.py dry-run OUT.json [--workers N]
        The whole run on the tuning set's 30 families, as KILL_TEST's Week 5
        asks: never a kill-run set.

    python kill-test/e1_kill_run.py kill-run A BLOCK_HASH OUT.json [--workers N]
        Set A, once, from the hash of Bitcoin block N + 6 (KT-14, KT-31). It
        runs only when set A's code manifest is in freeze/ and every file
        still matches it, and it never overwrites a result.

It changes no frozen file and calls only frozen pieces, in the frozen order
(section 3): the set is generated from its key and every plan passes its
certificates; every non-tower mind runs, and rule 6 is judged before any
tower mind runs (a set that fails it is retired, with no verdict); then the
tower minds run: E1, E1-OS10 and E1's reported versions, each in its own
sandboxed process (KT-93); then the frozen judge (harness/judge.judge) gives
the verdict for E1 against the floor mind, with E1-OS10 as rule 5's OS10.
The verdict table is printed before any per-family result.

The frozen harness/kill_run.run_kill_set is not used because it insists
that the first tower mind is labelled "K-F" and judges the mind so labelled;
E1 is never relabelled K-F (E1_ADDENDUM.md).
"""

import argparse
import dataclasses
import json
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

import freeze  # noqa: E402

from harness import agents, bench, judge, kill_run, scoring  # noqa: E402
from harness import constants as C  # noqa: E402
from harness.readings_cache import ReadingCache  # noqa: E402
from harness.run import run_one  # noqa: E402
from mind import e1  # noqa: E402
from world import keys, sets  # noqa: E402
from world.run_plan import generate_run  # noqa: E402

SET_SIZE = 40                         # families in a kill-run set: fixed by the power check (section 7, KT-15)
MANIFEST = ROOT / "freeze" / "killtest-code-v1-set-A.sha256"
PACKAGE = ROOT / "src" / "mind"
# E1 and its controls, as E1_ADDENDUM.md names them: label -> E1's own birth settings
TOWER = (("E1", {}), ("E1-OS10", {"OS10": True}), ("E1 no merging", {"merge": False}),
         ("E1 all at once", {"outside_in": False}))


def tower_spec(label, settings):
    """E1 in its own sandboxed process, paying 0.001 per check, habits off (KT-46, KT-49, KT-132)."""
    return agents.AgentSpec(agent_type="E1", label=label, mind_class="tower", entry="mind", host="subprocess",
                            pays_look=True, thinking_unit="check", unit_nano=C.CHECK_NANO, unit_row="B14, KT-46",
                            version=tuple(e1.version_of(label, bool(settings.get("OS10")))),
                            params=dict(settings, mind=e1.E1, name=label))


def _tower_run(job):
    set_name, set_key, family, run = job
    plan = generate_run(set_name, set_key, family, run)           # certified already, when the bench ran on it
    cache = ReadingCache(plan.noise_key)
    out = {}
    for label, settings in TOWER:
        rec = run_one(plan, tower_spec(label, settings), cache, package_dir=PACKAGE)
        out[label] = scoring.measures(rec)
    return family, run, out


def plain(x):
    if isinstance(x, Fraction):
        return {"exact": str(x), "value": float(x)}
    if isinstance(x, dict):
        return {str(k): plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [plain(v) for v in x]
    return x


def run_set(set_name, set_key, numbers, workers, runs=bench.RUNS_PER_FAMILY, progress=print):
    """The frozen order on one set. Returns the result record (and the per-run measures)."""
    t0 = time.time()
    non_tower = agents.bench_minds()
    measures, core_of, _ = bench.run_set(set_name, set_key, numbers, non_tower, runs=runs, workers=workers)
    by_type = {s.agent_type: measures[s.label] for s in non_tower}
    r6 = judge.rule6(set_name, by_type, core_of, list(agents.MUST_FAIL))
    progress(f"non-tower minds done ({time.time() - t0:.0f} s); rule 6 holds: {r6['holds']}")
    out = {"set": set_name, "families": len(numbers), "runs_per_family": runs, "rule6": r6,
           "floor_mind": r6["floor_mind"], "floor": r6["floor"], "per_run": {"non_tower": measures}}
    if not r6["holds"]:
        out.update(retired=True, verdict=None)
        return out
    jobs = [(set_name, set_key, f, r) for f in numbers for r in range(1, runs + 1)]
    tower = {label: {} for label, _ in TOWER}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for k, (f, r, res) in enumerate(pool.map(_tower_run, jobs, chunksize=1), 1):
            for label, m in res.items():
                tower[label][(f, r)] = m
            if k % 50 == 0 or k == len(jobs):
                progress(f"tower runs: {k}/{len(jobs)} ({time.time() - t0:.0f} s)")
    verdict = judge.judge(set_name, tower["E1"], by_type[r6["floor_mind"]], r6["floor"], tower["E1-OS10"], core_of)
    out.update(retired=False, verdict=verdict["verdict"], label=verdict["label"], judged=verdict,
               programme_outcome=judge.programme_outcome(verdict["verdict"], 1),
               reported={label: {f: judge.set_mean(m, f) for f in
                                 ("settle_rate", "copy_accept", "d_learn_strict", "fmn_strict", "lr_h1", "lr_far",
                                  "dq_sour_strict", "sour_drop_strict", "noticed", "d_strict_1")}
                         for label, m in tower.items()},
               core_of=core_of)
    out["per_run"]["tower"] = tower
    return out


def write(result, out_path):
    table = kill_run.verdict_table(result)
    print(table, flush=True)                              # before any per-family result (section 3)
    record = dict(result, verdict_table=table)
    per_run = record.pop("per_run")
    flat = {"non_tower": {label: {f"{f}/{r}": m for (f, r), m in runs.items()}
                          for label, runs in per_run["non_tower"].items()},
            "tower": {label: {f"{f}/{r}": m for (f, r), m in runs.items()}
                      for label, runs in per_run.get("tower", {}).items()}}
    record["per_run"] = flat
    pathlib.Path(out_path).write_text(json.dumps(plain(record), indent=1, sort_keys=True) + "\n")


def dry_run(out_path, workers):
    numbers = list(range(1, 31))
    result = run_set("tuning", keys.tuning_set_key(), numbers, workers)
    write(result, out_path)
    return 0


def frozen_ok():
    if not MANIFEST.exists():
        return f"set A's code manifest freeze/{MANIFEST.name} is not there: the code is not frozen"
    head = MANIFEST.read_text().splitlines()[0]
    if "set A" not in head:
        return f"{MANIFEST.name} does not name set A"
    diffs = freeze.verify(MANIFEST)
    if diffs:
        return "files differ from set A's manifest: " + "; ".join(diffs[:10])
    return None


def kill(set_name, block_hash, out_path, workers):
    if set_name != "A":
        print("E1_ADDENDUM.md uses set A only; a second set needs its own manifest and Aitzaz's OK")
        return 1
    why = frozen_ok()
    if why:
        print(why)
        return 1
    if pathlib.Path(out_path).exists():
        print(f"{out_path} exists: set A runs once")
        return 1
    if len(block_hash) != 64 or any(c not in "0123456789abcdef" for c in block_hash):
        print("the block hash is 64 lowercase hex characters, as Bitcoin Core shows it (KT-31)")
        return 1
    set_key = keys.kill_run_set_key(block_hash)
    families = sets.kill_run_families(set_name, block_hash, SET_SIZE)
    sets.require_separation(set_name, set_key, families)
    result = run_set(set_name, set_key, [f.number for f in families], workers)
    result["block_hash"] = block_hash
    write(result, out_path)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    d = sub.add_parser("dry-run")
    d.add_argument("out")
    d.add_argument("--workers", type=int, default=4)
    k = sub.add_parser("kill-run")
    k.add_argument("set")
    k.add_argument("block_hash")
    k.add_argument("out")
    k.add_argument("--workers", type=int, default=4)
    a = ap.parse_args(argv)
    if a.mode == "dry-run":
        return dry_run(a.out, a.workers)
    return kill(a.set, a.block_hash, a.out, a.workers)


if __name__ == "__main__":
    sys.exit(main())
