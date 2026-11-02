# Bench reports

Each file here is written by `tools/kill_test.py` on the frozen bench code. None is evidence about Frankie: these reports check the bench itself (KILL_TEST section 7).

| File | What | Where it came from |
|---|---|---|
| `tuning-bench.json` | The tuning set: radii (KT-101), rule 6, the positive control and MK10's spreads (section 7, steps 1 to 3). | `kill_test.py tuning`, committed with the Week 2 code. Running it again at tag `charter-killtest-bench-v1`, or on bench v1.1's code (commit 9212ac8), gives the same file, byte for byte. |
| `power-check-40.json` | The official power check (section 7, step 4) at 40 families: GO in 837 of 1,000 simulated sets, so the set size is 40. | [Run 41306979771](https://github.com/zivikzi/frankie/actions/runs/41306979771) of `power-check.yml`, started by hand on 1 Nov 2026 at tag `charter-killtest-bench-v1` (commit 8981c94). |
| `power-check-40-floors.jsonl` | The floor runs that check judged: B1n-bot-r's and B1n-mind's D_learn for each of the 40,000 simulated families. | The same run. |

The two power-check files came out of that run's `power-check-report` artifact. The zip's SHA-256 is 8950f7fdfae1cac7cf8f81502131fdacd689344b2e51ec697f761d27a0f72354, as the run's judge log prints it. To check the report, run this at the tag:

    python tools/kill_test.py power kill-test/results/tuning-bench.json COPY_OF_FLOORS.jsonl OUT.json --size 40

It gives a file identical to `power-check-40.json` without running any floor mind, because every floor run is already in the store. Pass a copy of the floors file, since the store is opened for appending.

## Bench v1.1

Week 3 found six gaps in the frozen bench, and bench v1.1 fixes them (rows KT-117 to KT-124 in [RULES.md](../RULES.md)). As section 3 asks of a bench fix, every bot, rule 6, the positive control and the power check were re-run on the fixed code before it was re-frozen:

- `kill_test.py tuning` on commit 9212ac8 gives `tuning-bench.json` byte for byte: the same radii, rule 6 holds and the positive control passes.
- [Run 41332007416](https://github.com/zivikzi/frankie/actions/runs/41332007416) of `power-check.yml`, started by hand on 1 Nov 2026 on commit 9212ac8, gives GO in 837 of 1,000 at 40 families, with the same failures as v1 (rule 1: 131, rule 4b: 24, rule 4c: 12, rule 3's margin: 2). Its report zip has SHA-256 cbd4beba73ff286a5cb37556cfe3a01d10c55470b54862aa81c019d5c05c0ca8, as its judge log prints it. Aitzaz uploaded the zip on 2 Nov 2026, and both its files are the ones above, byte for byte (SHA-256 ce5a7d92… for `power-check-40.json` and 14885fbf… for the floors file).

So the two power-check files above stand for v1.1 too, and no new report is added.
