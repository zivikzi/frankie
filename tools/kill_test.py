"""The kill test's driver (sections 3 and 7). Every step writes a plain JSON report.

    python tools/kill_test.py tuning OUT.json [--workers N]
        Every bot and B1n-mind on the 30 tuning families, 10 runs each, with
        B1n-bot-r, B1n-mind, G16 and G18 at every grid radius. Chooses the
        radii (section 4), then judges rule 6 and the positive control, and
        works out MK10's spreads (section 7, steps 1 to 3).

    python tools/kill_test.py power TUNING.json STORE.jsonl OUT.json [--size N] [--sets S] [--workers N]
           [--shard K/M]
        The power check (section 7, step 4) on the frozen code. The floor runs
        are kept in STORE, one line per simulated family, so a long check can
        stop and resume, or be split into M shards whose stores are joined.
        With no --size, sizes 40, 60, ... are tried until one passes (X39).

    python tools/kill_test.py kill-run SET BLOCK_HASH OUT.json [--families N]
        One kill-run set in the frozen order (section 3). Needs K-F (Week 3
        on); until then it stops.
"""

import argparse
import json
import pathlib
import sys
import time
from fractions import Fraction

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from harness import agents, bench, judge, power  # noqa: E402
from test_fixtures import mk10  # noqa: E402
from world import keys  # noqa: E402


def plain(x):
    """Fractions as exact "p/q" strings beside their decimal value; everything else as JSON."""
    if isinstance(x, Fraction):
        return {"exact": str(x), "value": float(x)}
    if isinstance(x, dict):
        return {str(k): plain(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [plain(v) for v in x]
    return x


def _progress(what):
    t0 = time.time()

    def show(k, n):
        if k == n or k % 25 == 0:
            print(f"{what}: {k}/{n} ({time.time() - t0:.0f} s)", flush=True)
    return show


def tuning(out, workers):
    specs = bench.radius_grid_specs() + [agents.plain_bot(t) for t in agents.PLAIN_BOTS]
    measures, core_of, _ = bench.run_set("tuning", keys.tuning_set_key(), range(1, 31), specs, workers=workers,
                                         progress=_progress("tuning runs"))
    radii = {}
    tables = {}
    for name, make in (("B1n-bot-r", agents.b1n_bot_r), ("B1n-mind", agents.b1n_mind), ("G16", agents.g16)):
        radii[name], tables[name] = bench.choose_radius(measures, make)
    _, tables["G18"] = bench.choose_radius(measures, agents.g18)
    chosen = {"B1n-bot-r": agents.b1n_bot_r(radii["B1n-bot-r"]), "B1n-mind": agents.b1n_mind(radii["B1n-mind"]),
              "G16": agents.g16(radii["G16"]), "G18": agents.g18(radii["G16"])}
    minds = {t: measures[chosen[t].label] if t in chosen else measures[t]
             for t in ("B1n-bot-r", "B1n-mind") + agents.MUST_FAIL}
    r6 = judge.rule6("tuning", minds, core_of, list(agents.MUST_FAIL))
    pc = judge.positive_control(measures["B2e"], core_of)
    spreads = mk10.spreads_from_tuning(minds["B1n-bot-r"], measures["B2e"])
    registered = (agents.RADIUS_B1N_BOT_R, agents.RADIUS_B1N_MIND, agents.RADIUS_G16)
    report = {
        "what": "kill-test tuning set: radii, rule 6, the positive control and MK10's spreads (section 7, steps 1-3)",
        "families": 30, "runs_per_family": bench.RUNS_PER_FAMILY,
        "core_placement": {g: sum(1 for v in core_of.values() if v == g) for g in ("object", "none")},
        "radius_tables": {name: {agents.radius_label(r): v for r, v in t.items()} for name, t in tables.items()},
        "radii": {name: agents.radius_label(r) for name, r in radii.items()},
        "radii_match_the_registry": (radii["B1n-bot-r"], radii["B1n-mind"], radii["G16"]) == registered,
        "rule6": r6, "positive_control": pc, "mk10_spreads": spreads,
        "means": {label: {f: judge.set_mean(measures[label], f) for f in
                          ("d_learn_beh", "fmn_beh", "lr_h1", "lr_far", "dq_sour_beh", "copy_accept", "d_beh_1")}
                  for label in [s.label for s in agents.bench_minds()]},
    }
    pathlib.Path(out).write_text(json.dumps(plain(report), indent=1, sort_keys=True) + "\n")
    print(f"radii {report['radii']}; rule 6 holds: {r6['holds']}; positive control: {pc['pass']}")
    return 0 if r6["holds"] and pc["pass"] and report["radii_match_the_registry"] else 1


def _spreads(tuning_report):
    s = json.loads(pathlib.Path(tuning_report).read_text())["mk10_spreads"]
    return {"between": s["between"], "within": s["within"], "source": s["source"]}


def power_check(tuning_report, store_path, out, size, n_sets, workers, shard):
    spreads = _spreads(tuning_report)
    store = power.FloorStore(store_path)
    specs = power.floor_specs(agents.RADIUS_B1N_BOT_R, agents.RADIUS_B1N_MIND)
    sizes = [size] if size else list(power.SIZES)
    show = _progress("floor families")
    if shard:
        k, m = (int(x) for x in shard.split("/"))
        for s in sizes:
            power.run_floors(store, n_sets, s, specs, workers, show, shard=(k, m))
        print(f"shard {k}/{m}: floor runs done")
        return 0
    report = dict(power.report_header(spreads), sizes=[], simulated_sets=n_sets,
                  official=n_sets == power.SIMULATED_SETS)
    for s in sizes:
        power.run_floors(store, n_sets, s, specs, workers, show)
        res = power.power_at(store, s, spreads, n_sets)
        detail = res.pop("sets_detail")
        res["floors"] = [{"set": d["set"], "floor_mind": d["floor_mind"], "floor": d["floor"], "verdict": d["verdict"],
                          "label": d["label"]} for d in detail]
        report["sizes"].append(res)
        print(f"size {s}: GO in {res['go']} of {n_sets} ({float(res['go_share']):.3f}); fails {res['fails']}")
        if res["passes"]:
            report["set_size"] = s
            break
    else:
        report["set_size"] = None
    pathlib.Path(out).write_text(json.dumps(plain(report), indent=1, sort_keys=True) + "\n")
    return 0 if report["set_size"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)
    t = sub.add_parser("tuning")
    t.add_argument("out")
    t.add_argument("--workers", type=int, default=1)
    p = sub.add_parser("power")
    p.add_argument("tuning_report")
    p.add_argument("store")
    p.add_argument("out")
    p.add_argument("--size", type=int)
    p.add_argument("--sets", type=int, default=power.SIMULATED_SETS)
    p.add_argument("--workers", type=int, default=1)
    p.add_argument("--shard")
    k = sub.add_parser("kill-run")
    k.add_argument("set")
    k.add_argument("block_hash")
    k.add_argument("out")
    k.add_argument("--families", type=int)
    a = ap.parse_args(argv)
    if a.mode == "tuning":
        return tuning(a.out, a.workers)
    if a.mode == "power":
        if a.size and a.size not in power.SIZES:
            ap.error(f"--size must be one of {power.SIZES}")
        return power_check(a.tuning_report, a.store, a.out, a.size, a.sets, a.workers, a.shard)
    print("The kill run needs K-F, its frozen configuration and its set's manifest (Weeks 3 to 6).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
