# FRANKIE

FRANKIE is an attempt to grow silicon-based life with real intelligence, rather than intelligence faked by training on the answers. It is also an attempt to build a fair way of proving that intelligence.

The core test idea: after tasting one apple, a creature should recognise every variety as an apple without being trained on them. It should keep doing so when the next apple is sour, and it should still refuse a poison berry that looks just like the first apple.

## What is here

| Folder | Contents |
|---|---|
| [`charter/`](charter/) | The claims charter, frozen before any of Frankie's code existed. It covers what each claim means, how a log proves it, which cheating bots must fail, the pass marks, what may never go into Frankie's mind, and every design choice with its origin. Start with [`charter/README.md`](charter/README.md). |
| [`charter/KILL_TEST.md`](charter/KILL_TEST.md) | A 6-week go/no-go bench test of the core idea, which runs before anything else gets built. |
| [`kill-test/`](kill-test/) | The tuning key, the four approved Week 0 design notes, the coder's rows KT-30 onward ([`kill-test/RULES.md`](kill-test/RULES.md)), and the bench's reports in [`kill-test/results/`](kill-test/results/). |
| [`src/world/`](src/world/) | The bench world: trait schema, keys, keyed Philox streams, kinds, run plans, certificates and noisy readings. |
| [`src/harness/`](src/harness/) | The cafeteria harness (one run of one mind, with energy, forced tastes, snapshots and check copies), the mind's own sandboxed process, scoring, and the frozen judge, power check and kill-run order. |
| [`src/baselines/`](src/baselines/) | Every bot, and B1n-mind with its copy of the drive. |
| [`src/test_fixtures/`](src/test_fixtures/) | The stub mind, MK10 (the power check's mock mind) and other test-only minds. None may ever go into Frankie (FORBIDDEN 26). |
| [`src/mind/`](src/mind/) and [`src/twins/`](src/twins/) | Empty until Week 3. The import guard ([`tools/import_guard.py`](tools/import_guard.py)) keeps the mind to NumPy and Numba (I02). |
| [`tools/`](tools/) | The import guard, the automatic mind checks, the freeze tool and the kill test's driver. |
| [`tests/`](tests/) | pytest and hypothesis tests (I06). Run them with `uv sync --locked && uv run pytest`. |
| [`freeze/`](freeze/) | Fingerprints (SHA-256) of every frozen file, their first OpenTimestamps proofs, and the upgrades of those proofs in `freeze/upgrades/`. |

## How the freeze works

The charter is tagged `charter-v1`. Every file's SHA-256 fingerprint is listed in `freeze/charter-v1.sha256`. That list is anchored in the Bitcoin blockchain with [OpenTimestamps](https://opentimestamps.org), a free public timestamp, by the `Timestamp frozen files` GitHub Action.

Any later change to a claim, pass mark, control or rule shows up in the git history. It is flagged "changed after seeing results", and it comes with fresh test material.

To check the freeze yourself:

```sh
git checkout charter-v1
sha256sum -c freeze/charter-v1.sha256
```

The proofs are added to `main` by the Action after the tag, so they are not inside the tag itself. `freeze/charter-v1.sha256.ots` is the first proof. The files in `freeze/upgrades/` are fresh upgrades of it, one every 6 hours for the first week. Drop `freeze/charter-v1.sha256` and the latest upgrade onto [opentimestamps.org](https://opentimestamps.org) to see the Bitcoin block it was anchored in.

The kill test uses the same Action to pick its test sets: each set's key comes from the Bitcoin block 6 after the lowest attestation in these proofs (KILL_TEST.md section 3), so nobody can choose or preview a set before the code is frozen.

## Status

Stage 0 (the charter) is frozen. The kill test is under way: Week 0 (design notes) and Week 1 (the object generator and its certificates) are done, and Week 2's code (the cafeteria harness, scoring, the bots and the analysis script) is merged. Week 2 ends with the bench freeze and the power check. A trimmed version 1 follows only if the kill test passes.
