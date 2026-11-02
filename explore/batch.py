"""Run minds over a half of the tuning set and write the Lab's scoreboard.

    uv run python explore/batch.py [--half odd|even|both] [--minds NAME,NAME,...] [--workers N]
    uv run python explore/batch.py --variant NAME --set key=value ... [--half odd]

The first form writes explore/results/scoreboard.json (merging with what is
there). The second tries one E1 variant on a half and appends it, with its
numbers, to explore/results/variants.jsonl: every variant tried is logged.
Develop on the odd families only; the even half is reported as a check and
never tuned on.
"""

import argparse
import json
import pathlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import minds  # noqa: E402

RESULTS = minds.ROOT / "explore" / "results"
DEFAULT = ("B1n-bot-r", "B1n-mind", "B2e", "K-F", "E1", "E1-OS10", "E1 no merging", "E1 all at once",
           "E1 without the sour fix", "E1 as first written")


def run_mind(name, families, workers, params=None, progress=None):
    jobs = [(name, params, f, r) for f in families for r in range(1, minds.RUNS + 1)]
    runs, core_of = {}, {}
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            done = list(pool.map(minds.one, jobs, chunksize=2))
    else:
        done = [minds.one(j) for j in jobs]
    for _, f, r, core, m in done:
        runs[(f, r)] = m
        core_of[f] = core
    tower = minds.spec(name, params).mind_class == "tower"
    return minds.summary(runs, tower), {f"{f}/{r}": {k: (float(v) if not isinstance(v, str) else v)
                                                     for k, v in m.items() if not isinstance(v, (list, dict))}
                                        for (f, r), m in runs.items()}


def floor(board_half):
    return max(board_half.get("B1n-bot-r", {}).get("d_learn", float("-inf")),
               board_half.get("B1n-mind", {}).get("d_learn", float("-inf")))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--half", default="both", choices=("odd", "even", "both"))
    ap.add_argument("--minds", default=",".join(DEFAULT))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--variant")
    ap.add_argument("--set", nargs="*", default=[])
    a = ap.parse_args(argv)
    halves = ("odd", "even") if a.half == "both" else (a.half,)
    RESULTS.mkdir(parents=True, exist_ok=True)
    if a.variant:
        params = {}
        for kv in a.set:
            k, v = kv.split("=", 1)
            params[k] = (v == "true") if v in ("true", "false") else (float(v) if any(c.isdigit() for c in v)
                                                                      and v.replace(".", "", 1).lstrip("-").isdigit()
                                                                      else v)
        for half in halves:
            fams = minds.ODD if half == "odd" else minds.EVEN
            t0 = time.time()
            s, _ = run_mind(a.variant if a.variant.startswith("E1") else "E1 " + a.variant, fams, a.workers, params)
            line = {"variant": a.variant, "params": params, "half": half, "summary": s,
                    "seconds": round(time.time() - t0, 1), "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            with (RESULTS / "variants.jsonl").open("a") as f:
                f.write(json.dumps(line, sort_keys=True) + "\n")
            print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()}))
        return 0
    path = RESULTS / "scoreboard.json"
    board = json.loads(path.read_text()) if path.exists() else {"halves": {}, "runs": {}}
    for half in halves:
        fams = minds.ODD if half == "odd" else minds.EVEN
        for name in a.minds.split(","):
            t0 = time.time()
            s, per_run = run_mind(name, fams, a.workers)
            board["halves"].setdefault(half, {})[name] = s
            board["runs"].setdefault(half, {})[name] = per_run
            print(f"{half} {name}: " + ", ".join(f"{k} {v:.3f}" for k, v in s.items() if isinstance(v, float))
                  + f" ({time.time() - t0:.0f} s)", flush=True)
        board["halves"][half]["floor"] = floor(board["halves"][half])
    board["variants"] = {n: p for n, p in minds.VARIANTS.items()}
    path.write_text(json.dumps(board, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
