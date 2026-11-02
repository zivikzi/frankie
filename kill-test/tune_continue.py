"""After the search stopped: Aitzaz's decision of 2 Nov 2026, carried out on the same log.

    python kill-test/tune_continue.py LOG.jsonl [--workers N]

The search (kill-test/tune.py) stopped after 3 passes with no setting reaching
every target, as TUNING_PLAN.md's step 5 says. Aitzaz then chose, on 2 Nov
2026 at 10:53 UTC, "Run the kill test": K-F is frozen at the setting the
search ended on, though it reached no target. This tool carries out the rest
of the plan from that setting, appending to the same append-only log:

1. Aitzaz's decision, as an event;
2. step 6: KT-27 by KT-47's rule at that setting, and the setting measured
   again on the search half with it;
3. step 7: the setting and OS10 on the kept-back half, judged as on a kill-run
   set. It is recorded, not a stop, since Aitzaz chose to go on knowing the
   targets were not reached;
4. step 8: TW7's search over its gain and time constant, with as many passes
   as K-F used (3), from K-F's values, and TW7's check.

It changes no value in the mind's code; registering the values (step 9) is a
separate commit. It runs only from committed code, on the same code the
search ran on (git's ids for src/, tune.py, uv.lock and the spreads file),
and, if it stops part-way, it picks up where it stopped by replaying its own
events, as tune.py does (KT-130).
"""

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kill-test"))

import tune  # noqa: E402

DECISION = {
    "type": "decision", "by": "Aitzaz", "when": "2026-11-02 10:53 UTC", "choice": "Run the kill test",
    "consequence": "I merge the search log and report into main, then freeze K-F at the setting the search ended "
                   "on, though it reached no target. I set its spike cost, run TW7's search, and do Week 5 "
                   "(twins, dry run). The freeze push and the kill run each still wait for your OK. Expected: "
                   "NO-GO, a pre-registered answer.",
}


def own_id():
    import subprocess
    return subprocess.run(["git", "rev-parse", "HEAD:kill-test/tune_continue.py"], cwd=ROOT, capture_output=True,
                          text=True).stdout.strip()


def proceed(log_path, workers) -> int:
    head, dirty = tune.commit_state()
    mine = tune.subprocess.run(["git", "status", "--porcelain", "kill-test/tune_continue.py"], cwd=ROOT,
                               capture_output=True, text=True).stdout.strip()
    if dirty or mine:
        print(f"uncommitted changes; commit them first:\n{dirty}\n{mine}")
        return 1
    log = tune.Log(log_path)
    if not log.old or log.old[0].get("code") != tune.code_state():
        print("this log was made by other code: the search's own code must be checked out (KT-130)")
        return 1
    stops = [e["n"] for e in log.old if e["type"] == "stop" and "3 passes" in e.get("why", "")]
    if not stops:
        print("the log has no step-5 stop to continue from")
        return 1
    spreads = log.old[0]["spreads"]
    s = tune.Search(log, workers, spreads, head)
    for e in log.old[:stops[0] + 1]:                       # what the search measured, ready for reuse
        if e["type"] == "setting" and "measures" in e:
            s.seen[e["trial"]] = e
        if e["type"] == "floor" and e["half"] == "search":
            s.floors["search"] = ({"floor": tune.Fraction(e["floor"]["exact"])}, None, None)
    ended = [e for e in log.old[:stops[0]] if e["type"] == "no pick" and e["mind"] == "K-F"][-1]
    pick = {name: ended["values"][name] for _, name, _ in tune.KF_GRID}
    passes = ended["passes"]
    log.n = stops[0] + 1                                   # continue after the stop, replaying anything after it
    if log.measured and len(log.old) > log.n and not s.repeats(list(log.measured.values())[-1]):
        return 1
    log.add(dict(DECISION, values=pick, tool=own_id()))
    nano = s.kt27(pick)                                                       # step 6
    tg, _ = s.measure(tune.Trial("K-F", tuple(pick.items()), spike_nano=nano), {"step": "with KT-27"})
    log.add({"type": "step 6", "every_target": tg["every_target"], "misses": tg["misses"],
             "note": "recorded; Aitzaz chose to go on knowing the targets were not reached"})
    ok, os10_runs = s.check("K-F", pick, {}, nano)                           # step 7, recorded
    tw7_start = {"gain": tune.GAIN_START, "tau_ms": tune.TAU_START}          # step 8
    tw7, tw7_passes, how = s.coordinate("TW7", tune.TW7_GRID, tw7_start, range(1, passes + 1),
                                        fixed=tuple(pick.items()), rate_mode=True)
    ok7 = None
    if how != "leak":
        ok7, _ = s.check("TW7", pick, tw7, 0, os10_runs=os10_runs)
    log.add({"type": "done", "kf": pick, "spike_nano": nano, "kf_kept_back_go": ok, "tw7": tw7,
             "tw7_how": how, "tw7_passes": tw7_passes, "tw7_kept_back_go": ok7})
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("log")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args(argv)
    return proceed(a.log, a.workers)


if __name__ == "__main__":
    sys.exit(main())
