# FRANKIE Stage 0: the charter

_Approved by Aitzaz · frozen as tag `charter-v1` in [zivikzi/frankie](https://github.com/zivikzi/frankie) · 25 Oct 2026_

This folder holds Stage 0. It says what each claim about Frankie means, how a log would prove it, and what may never go into Frankie's mind. It was all written before any of Frankie's code existed. It is committed to a public GitHub repository and timestamped, so anyone can check that the tests weren't changed to flatter Frankie.

## What to read first (about 30 minutes)

1. **[CHARTER.md](CHARTER.md):** the "At a glance" table, then the **In plain words** paragraph under each claim. There are 14 claims. The free-will claim is split in two: C13-M checks that the mechanism works, and C13-E is evidence.
2. **[FORBIDDEN.md](FORBIDDEN.md):** just the headings. These are 31 things that may never go into Frankie's mind.
3. **[LEDGER.md](LEDGER.md):** the **Mind** section, the 29 rows marked *Claude proposal*. Those are the places where my textbook habits could creep in, so they deserve your closest look. Aitzaz approved every row in bulk on 24 Oct ("approve all").
4. **[KILL_TEST.md](KILL_TEST.md):** the **In plain words** section, then the table of 18 placeholders at the end (KT-01 to KT-18). These fill gaps the reviewers found. Aitzaz approved version 2 in bulk on 24 Oct, and the version 3 changes on 25 Oct 2026.

Everything else is precise detail that makes the freeze airtight: exact definitions, the glossary of bot and log names, and the register of open details. You don't need to read it line by line.

## The headline claims

Seven claims carry the main result. Together they're held to a strict statistics standard (Holm correction across 7, strictest level 0.05/7).

| Claim | In short |
|---|---|
| C1 | After one taste of a sweet apple, Frankie accepts very different-looking apples and refuses look-alikes before tasting any. |
| C2 | A sour apple stays an apple: the sour taste doesn't make Frankie drop the kind. |
| C3 | Frankie learns at least twice as much per meal as brute trial and error, starting from what it was born with. |
| C7 | Curiosity as insurance: a Frankie that has lived through a food source failing checks path B more, and recovers faster when A fails. |
| C8 | Patience, not persistence: it loses interest in the flickering stone but waits for the slow seed. |
| C9 | Watching the teacher starts to pay off, with no built-in urge to copy. |
| C12 | New approaches that are in neither the teacher's repertoire nor Frankie's past, labelled repeat, recombination or novel. |

Supporting evidence: C4 (the plastic and stickered apples), C6 (the "dax" test) and C13-E (lucky ways of acting that carry into new situations). Mechanism checks, which never count as intelligence: C5, C10, C11 and C13-M.

## Your decisions built into this

- **The 16 design decisions** (24 Oct). Tests are frozen first. Essence is steady core traits. Memory uses "blame moves outward". Brains use spiking neurons. The rest follow the recommendations. The full list is on the [FRANKIE page](https://claude.ai/artifact/GBMug1krG6oUHrJSnQytyp).
- **Q1, what counts as recognizing.** Frankie must eat it AND think "same kind as the sweet apple". The bar after one taste is 40 points.
- **Q2, four rules for the mind.** Taste counts like any detail, and a guess is wrong only when the energy outcome surprises Frankie. Nothing counts looks. The flickering stone can't be eaten, and a seed can be eaten until it's a tree. Frankie remembers creatures through short gaps.
- **Q3, how the drive chooses.** Boldness lowers the safety bar. Habit is checked first. With no safe option, Frankie takes the best long shot. A newborn trusts that food never fails.
- **Q4, the evidence split.** As in the table above.
- **Q5, the pass marks.** Learning 2x, free-will stability 70–95%, wiggle at most 20%, at most 15 points of extra caution, and a watching benefit still visible 500 ticks after the teacher leaves.

Inside the files, these appear as `[Aitzaz Qn, 24 Oct]`. Anything marked "Claude placeholder" was Claude's suggestion. Each row's approval is in its Initials or Approved column.

## How the freeze works

1. This folder is committed to [zivikzi/frankie](https://github.com/zivikzi/frankie) and tagged `charter-v1`.
2. Every file's fingerprint (SHA-256) is listed in `freeze/charter-v1.sha256`.
3. A GitHub Action anchors that list with OpenTimestamps, a free public timestamp in the Bitcoin blockchain, and keeps the proofs in `freeze/`.
4. Any later change to a pass mark, control or rule shows up as "changed after seeing results", and comes with a fresh set of sealed test material.

## Files

| File | What's in it |
|---|---|
| [CHARTER.md](CHARTER.md) | The 14 claims: plain meaning, exact definition, measure, pass mark, sample size, controls, and what happens if a claim fails |
| [FORBIDDEN.md](FORBIDDEN.md) | 31 mechanisms banned from Frankie's mind, and how each ban is checked |
| [LEDGER.md](LEDGER.md) | 215 design parts and constants, with where each came from, whether it's conventional or untested, and Aitzaz's initials |
| [REGISTER.md](REGISTER.md) | 130 details the plan leaves open (112 from Stage 0 and the kill test's KT-01 to KT-18), each with a placeholder and who decides, so no gap gets filled silently |
| [GLOSSARY.md](GLOSSARY.md) | One name for every bot, control and log field, plus the statistics policy |
| [KILL_TEST.md](KILL_TEST.md) | The 6-week kill test of the core idea that runs before everything else, with its pass and fail rules |
| `data/` | The same content as JSON, for the code to read later |

## How it was checked

Each claim was drafted, then attacked by a reviewer whose job was to pass it cheaply. It was tried against bots that reject everything unknown, eat everything new, copy blindly or wander at random, against an inherited rule, and against the designed dice. Every hole that turned up was fixed (94 fixes). A cross-check found 32 mismatches between documents, and all were fixed. Two more verification rounds then caught and fixed 17 smaller slips, including 3 that would have let a test be passed cheaply. The kill test had five review rounds of its own, including bot-only simulations of the bench, before it was frozen (KILL_TEST.md, "About version 3").

## Small items, frozen as written

None of these lets a test be passed cheaply. They are noted here so nobody mistakes them for later changes.

- Ledger row X18 is correct but hard to read, because the 2 × 4 group layout needs rewriting.
- In C7-T8(a), the world check scores a death as a slow recovery for both groups. That's fine for a world check, but it isn't symmetric.

The other pre-freeze tidy-ups (the TW3 and TW4 margins in PLACEHOLDER-107 and -112, the 0-to-1 taste range in PLACEHOLDER-47, and the test-side wrapper for OS18, OS19 and OS23 in FORBIDDEN 26) were made in the freeze commit, together with the kill test's edits (KILL_TEST.md section 13).

## What comes next

On 24 Oct you chose to test the riskiest bet first. [KILL_TEST.md](KILL_TEST.md) is frozen together with this charter. It's a 6-week bench test of whether your outside-in tower learns apples from look-alikes faster than brute trial and error, given the same few tastes. Its **In plain words** section is the place to start.

If the tower wins, the trimmed version 1 follows (essence, sour apple, learning, curiosity and patience). The teacher, novel approaches and free will move to version 2. If it loses, we rethink it together before writing any more code.
