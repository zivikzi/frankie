# Bench reports

Each file here is written by `tools/kill_test.py` on the frozen bench code. None is evidence about Frankie: these reports check the bench itself (KILL_TEST section 7).

| File | What | Where it came from |
|---|---|---|
| `tuning-bench.json` | The tuning set: radii (KT-101), rule 6, the positive control and MK10's spreads (section 7, steps 1 to 3). | `kill_test.py tuning`, committed with the Week 2 code. Running it again at tag `charter-killtest-bench-v1` gives the same file, byte for byte. |
| `power-check-40.json` | The official power check (section 7, step 4) at 40 families: GO in 837 of 1,000 simulated sets, so the set size is 40. | [Run 41306979771](https://github.com/zivikzi/frankie/actions/runs/41306979771) of `power-check.yml`, started by hand on 1 Nov 2026 at tag `charter-killtest-bench-v1` (commit 8981c94). |
| `power-check-40-floors.jsonl` | The floor runs that check judged: B1n-bot-r's and B1n-mind's D_learn for each of the 40,000 simulated families. | The same run. |

The two power-check files came out of that run's `power-check-report` artifact. The zip's SHA-256 is 8950f7fdfae1cac7cf8f81502131fdacd689344b2e51ec697f761d27a0f72354, as the run's judge log prints it. To check the report, run this at the tag:

    python tools/kill_test.py power kill-test/results/tuning-bench.json COPY_OF_FLOORS.jsonl OUT.json --size 40

It gives a file identical to `power-check-40.json` without running any floor mind, because every floor run is already in the store. Pass a copy of the floors file, since the store is opened for appending.
