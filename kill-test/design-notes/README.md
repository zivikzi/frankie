# Kill test design notes (Week 0)

These four one-page notes say how four parts of the kill test will work, before any code exists. Each shows the textbook method beside at least one untested alternative. Aitzaz T approved all four as written on 25 Oct 2026. They work inside the frozen charter (tag `charter-v1`) and change none of its files.

## The four notes

| Note | What it settles | Picks that move K-F's odds most | Status |
|---|---|---|---|
| [1. Object generator](1-object-generator.md) | How objects, keys and sensor noise are made | Teaching look-alikes may move overlapping core traits (the plain reading; the other reading would probably help K-F) | Approved 25 Oct 2026 |
| [2. Drive](2-drive.md) | Small gaps in the eat-or-skip bookkeeping | Counting checks once per decision, which keeps thinking costs small; counting every step would lower K-F's odds | Approved 25 Oct 2026 |
| [3. Tower](3-tower.md) | When candidates are dropped, how layers join in, objections, "unknown" | The elimination rule; "unknown" as a full rival, with rule 2 (accepting copies of h1, needed for GO) at risk | Approved 25 Oct 2026 |
| [4. Memory rule](4-memory-rule.md) | What a "matching" outcome is, where the blame's weight goes, merges | Outcome classes and where the +0.2 goes (likely help); no merges (may hurt) | Approved 25 Oct 2026 |

Each note's small fill-ins for the coder are in [RULES.md](../RULES.md), as rows KT-30 to KT-77.

## Found in the frozen text

The drafting and checking turned up four main gaps in the frozen text. The notes and [RULES.md](../RULES.md) settle smaller ones, such as the clash between two cost targets in note 2. I propose working within all of them, so no new addendum is written.

- **Elimination is named but never defined.** It is the heart of your tower idea, so note 3's first choice, row KT-52, proposes the rule.
- **One of the two ways of "noticing" the sour apple can never fire.** Both sour-apple branches always make the same kind of memory write. So noticing rests on one test: whether the sour taste fits the apple kind worse than its usual taste. Only a new addendum could fix this, and I suggest living with it. I expect the test to fire in most runs, since the sour taste lies outside the apple kinds' stored sourness, but that is my estimate. If fewer than half of runs notice, rule 5 can't count, and the best result left is INCONCLUSIVE.
- **Most tuned numbers have no stated goal.** Section 7 says what may be tuned, but not what the tuning should aim for. This will likely move K-F's odds more than any pick in these notes, so I will bring you a short tuning plan before any tower code exists.
- **KT-14's wording for turning a Bitcoin block into a key was loose.** Note 1 fixes the exact reading before any kill-run set's key can exist.
