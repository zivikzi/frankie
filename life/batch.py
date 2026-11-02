"""Run every creature in the same fresh random worlds and measure how each one does.

    uv run python life/batch.py [--seeds 50] [--ticks 3000] [--workers N] [--creatures a,b,...]
                                [--seed-file FILE] [--out life/results/batch.json]

Every world comes from a fresh random seed (instant randomness), and every
creature runs on exactly the same seeds. Each seed is written to the output
and appended to life/results/seeds.log, so every reported number can be
traced to its worlds and re-run. --seed-file re-runs a saved list instead.
"""

import argparse
import json
import os
import pathlib
import secrets
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
if sys.path and pathlib.Path(sys.path[0]).resolve() == HERE:
    sys.path.pop(0)
sys.path.insert(0, str(ROOT))

from life import config as C  # noqa: E402

DEFAULT_CREATURES = ("frankie", "trial", "wanderer", "frankie-no-merge", "frankie-no-context")


def one(job):
    seed, name, ticks = job
    from life.sim import Session
    t = time.perf_counter()
    s = Session(seed, [name])
    r = s.run(ticks)[0]
    w = s.world
    r["seed"] = seed
    r["creature"] = name
    r["world"] = {"fences": len(w.obstacles.fences), "walls": len(w.obstacles.walls),
                  "river": w.obstacles.river is not None}
    r["reserve"] = round(s.creatures[0].reserve, 2)
    r["boldness"] = round(s.creatures[0].boldness, 3)
    r["seconds"] = round(time.perf_counter() - t, 2)
    mind = s.creatures[0].mind
    if hasattr(mind, "cost"):
        r["llm"] = mind.cost()
    return r


def settled_after(seq, clean=10):
    """Eats needed before the poison share stayed under 10%: the eats up to and including his last
    poisoning, counted only if at least `clean` eats follow it, all poison-free (so every later window
    of 10 eats is under 10%). None if that never happened in his life."""
    last = max((i for i, x in enumerate(seq) if x == "p"), default=-1)
    if len(seq) - (last + 1) < clean:
        return None
    return last + 1


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.fmean(xs), 4) if xs else None


def _median(xs):
    xs = [x for x in xs if x is not None]
    return round(statistics.median(xs), 2) if xs else None


def summarise(runs, ticks):
    out = {}
    names = sorted({r["creature"] for r in runs}, key=lambda n: (list(DEFAULT_CREATURES) + [n]).index(n))
    for name in names:
        rs = [r for r in runs if r["creature"] == name]
        eats = sum(r["eats"] for r in rs)
        poison = sum(r["poison"] for r in rs)
        n_win = max(len(r["windows"]) for r in rs)
        curve = []
        for k in range(n_win):
            e = sum(r["windows"][k][0] for r in rs if k < len(r["windows"]))
            p = sum(r["windows"][k][1] for r in rs if k < len(r["windows"]))
            alive = sum(1 for r in rs if k < len(r["windows"]))
            curve.append({"window": k, "eats": e, "poison": p, "share": round(p / e, 4) if e else None,
                          "alive": alive})
        by_eat = []
        for k0 in range(0, 60, 5):
            seg = [x for r in rs for x in r["eat_seq"][k0:k0 + 5]]
            if not seg:
                break
            by_eat.append({"eats": f"{k0 + 1}-{k0 + 5}", "n": len(seg),
                           "poison_share": round(sum(1 for x in seg if x == "p") / len(seg), 4),
                           "food_share": round(sum(1 for x in seg if x == "f") / len(seg), 4)})
        settle = [settled_after(r["eat_seq"]) for r in rs]
        # the context rule: is a context-fruit eat in the region where it poisons? his first one against later ones
        ctx_early = [r["ctx_eats"][0][1] for r in rs if r["ctx_eats"]]
        ctx_late = [n for r in rs for _, n in r["ctx_eats"][1:]]
        looks = sum(r["looks_judged"] for r in rs)
        changed = sum(r["looks_changed"] for r in rs)
        eps = [e for r in rs for e in r["episodes"]]
        first = [r["episodes"][0] for r in rs if r["episodes"]]
        later = [e for r in rs for e in r["episodes"][1:]]

        def ep_stats(es):
            reached = [e for e in es if e["reached"]]
            return {"n": len(es), "reached": len(reached),
                    "reached_share": round(len(reached) / len(es), 4) if es else None,
                    "median_ticks": _median([e["ticks"] for e in reached]),
                    "median_metres": _median([e["metres"] for e in reached]),
                    "median_start_dist": _median([e["start_dist"] for e in es])}

        obstacle_worlds = [r for r in rs if r["world"]["fences"] or r["world"]["river"]]
        plain_worlds = [r for r in rs if not (r["world"]["fences"] or r["world"]["walls"] or r["world"]["river"])]
        out[name] = {
            "runs": len(rs),
            "lifespan_mean": _mean([r["lifespan"] for r in rs]),
            "lifespan_median": _median([r["lifespan"] for r in rs]),
            "survived_share": round(sum(1 for r in rs if not r["died"]) / len(rs), 4),
            "food_per_100": _mean([r["food_per_100"] for r in rs]),
            "eats_mean": _mean([r["eats"] for r in rs]),
            "poison_share_all": round(poison / eats, 4) if eats else None,
            "curve": curve,
            "by_eat": by_eat,
            "settled_runs": sum(1 for x in settle if x is not None),
            "settled_median_eats": _median(settle),
            "looks_per_life": _mean([r["looks"] for r in rs]),
            "looks_changed_share": round(changed / looks, 4) if looks else None,
            "looks_judged": looks,
            "ctx_bad_share_early": round(sum(1 for n in ctx_early if n == "poison") / len(ctx_early), 4) if ctx_early else None,
            "ctx_bad_share_late": round(sum(1 for n in ctx_late if n == "poison") / len(ctx_late), 4) if ctx_late else None,
            "ctx_eats": len(ctx_early) + len(ctx_late), "ctx_first_n": len(ctx_early), "ctx_later_n": len(ctx_late),
            "episodes_all": ep_stats(eps),
            "episodes_first": ep_stats(first),
            "episodes_later": ep_stats(later),
            "bumps_fence_mean": _mean([r["bumps"]["fence"] for r in rs]),
            "bumps_wall_mean": _mean([r["bumps"]["wall"] for r in rs]),
            "bumps_river_mean": _mean([r["bumps"]["river"] for r in rs]),
            "lifespan_obstacle_worlds": _mean([r["lifespan"] for r in obstacle_worlds]),
            "lifespan_plain_worlds": _mean([r["lifespan"] for r in plain_worlds]),
            "n_obstacle_worlds": len(obstacle_worlds), "n_plain_worlds": len(plain_worlds),
        }
        if any("llm" in r for r in rs):
            out[name]["llm"] = {k: sum(r["llm"][k] for r in rs) for k in ("calls", "input_tokens", "output_tokens",
                                                                          "refusals", "errors")}
            out[name]["llm"]["model"] = rs[0]["llm"]["model"]
            out[name]["llm"]["history_lines_budget"] = rs[0]["llm"]["history_lines_budget"]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seeds", type=int, default=50)
    ap.add_argument("--ticks", type=int, default=C.MAX_TICKS)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--creatures", default=",".join(DEFAULT_CREATURES))
    ap.add_argument("--seed-file", default=None, help="re-run the seeds listed in this file (one per line, or a batch json)")
    ap.add_argument("--out", default=str(HERE / "results" / "batch.json"))
    ap.add_argument("--label", default="")
    ap.add_argument("--llm-model", default=None, help="the model for the LLM creature (or set FRANKIE_LLM_MODEL)")
    ap.add_argument("--llm-fake", action="store_true", help="run the LLM creature on the scripted fake (no API calls)")
    a = ap.parse_args(argv)
    names = [n.strip() for n in a.creatures.split(",") if n.strip()]
    if a.llm_model:
        os.environ["FRANKIE_LLM_MODEL"] = a.llm_model
    if a.llm_fake:
        os.environ["FRANKIE_LLM_FAKE"] = "1"
    if "llm" in names:
        from life.minds import llm
        if not (a.llm_fake or llm.available()):
            raise SystemExit("the LLM creature needs ANTHROPIC_API_KEY and a model (--llm-model or FRANKIE_LLM_MODEL), "
                             "or --llm-fake")
    if a.seed_file:
        text = pathlib.Path(a.seed_file).read_text()
        seeds = json.loads(text)["seeds"] if text.lstrip().startswith("{") else [int(x) for x in text.split()]
    else:
        seeds = [secrets.randbits(31) for _ in range(a.seeds)]
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    log = HERE / "results" / "seeds.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a") as f:
        f.write(f"# {started} batch {a.label or '-'} -> {a.out}; creatures {','.join(names)}; ticks {a.ticks}\n")
        f.write(" ".join(str(s) for s in seeds) + "\n")
    jobs = [(s, n, a.ticks) for s in seeds for n in names]
    t0 = time.time()
    runs = []
    with ProcessPoolExecutor(a.workers) as pool:
        for k, r in enumerate(pool.map(one, jobs, chunksize=2)):
            runs.append(r)
            if (k + 1) % 25 == 0 or k + 1 == len(jobs):
                print(f"  {k + 1}/{len(jobs)} runs, {time.time() - t0:.0f}s", flush=True)
    summary = summarise(runs, a.ticks)
    out = {"started": started, "label": a.label, "ticks": a.ticks, "seeds": seeds, "creatures": names,
           "runs": len(runs), "seconds": round(time.time() - t0, 1), "summary": summary,
           "per_run": [{k: r.get(k) for k in ("seed", "creature", "lifespan", "died", "food", "poison", "nothing",
                                          "food_per_100", "looks", "looks_changed", "bumps", "walked", "world",
                                          "reserve", "boldness", "eat_seq", "episodes", "ctx_eats", "windows", "llm")}
                       for r in runs]}
    p = pathlib.Path(a.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, separators=(",", ":")) + "\n")
    print_table(summary)
    print(f"seeds: {len(seeds)} fresh random worlds, listed in {p} and {log}")
    return out


def print_table(summary):
    cols = ("lifespan_mean", "survived_share", "food_per_100", "poison_share_all", "settled_runs",
            "looks_changed_share", "ctx_bad_share_early", "ctx_bad_share_late")
    print(f"{'creature':22s}" + "".join(f"{c[:14]:>15s}" for c in cols))
    for name, s in summary.items():
        print(f"{name:22s}" + "".join(f"{str(s[c]):>15s}" for c in cols))
        be = " ".join(f"{b['eats']}:{b['poison_share']:.2f}" for b in s["by_eat"][:6])
        print(f"{'':22s}poison share by eat number: {be}")
        e1, el = s["episodes_first"], s["episodes_later"]
        print(f"{'':22s}obstacles first: {e1['reached']}/{e1['n']} reached, median {e1['median_ticks']} ticks; "
              f"later: {el['reached']}/{el['n']}, median {el['median_ticks']} ticks")


if __name__ == "__main__":
    main()
