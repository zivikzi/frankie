# Tuning plan for K-F

Agreed by Aitzaz T on 1 Nov 2026, before any of K-F's brain was written. Aitzaz made the plan's three choices that day (listed at the end). This file is committed before any tuning-set measurement, so the plan is on record before the search starts. The search itself runs in Week 4, once the spiking neurons exist.

## What this plan is for

Tuning aims at the values the power check assumed, takes the first setting that reaches them, and stops after at most 3 passes through the list. Section 7 of [KILL_TEST.md](../charter/KILL_TEST.md) lists which 9 numbers may be tuned on the tuning set, but not what the tuning should aim for. That aim will likely move K-F's odds more than any design pick, so it is fixed here.

Week 3 builds the tower, the memory rules and the drive, first with rate neurons (the TW7 version), and checks them on hand-made cases. Nothing in Week 3 changes a tuned number.

## The numbers that may be tuned

The list is closed: K-F has 9 numbers, set in this order, and TW7 has 2 of its own. Each number is shared by every trait and every layer, and each start value is fixed now, before any tuning-set run.

| Row | Number | What it controls | Start | Values tried | Label |
|---|---|---|---|---|---|
| KT-19 | Leak | How much of a neuron's charge fades each millisecond | 0.1 | 0.025, 0.05, 0.1, 0.2, 0.4 | Conventional (a 10 ms memory, as in real neurons) |
| KT-20 | Threshold | The charge at which a neuron fires | 2.5 | 0.625, 1.25, 2.5, 5, 10 | Untested: half the charge one fitting trait builds up |
| KT-21 | Refractory period | How long a neuron rests after firing | 2 ms | 0, 1, 2, 4, 8 ms | Conventional |
| KT-22 | Inhibition strength | How hard each spike pushes rival ideas down | 0.3125 | 0.078, 0.156, 0.3125, 0.625, 1.25 | Untested: one full volley of 8 spikes pushes a rival down by one threshold |
| KT-23 | Detector width | How far a reading reaches along a trait's scale | 4 noise widths | 3.5, 4, 5, 6.5, 8 | Untested: just wide enough that every reading lights a detector |
| KT-24 | Commit margin | How far ahead the leading idea must be to win | 2 | 0.5, 1, 2, 4, 8 | Untested: about two recent spikes' worth |
| KT-25 | Objection threshold | How much mismatch makes a part or detail object | 0.5 | 0.125, 0.25, 0.5, 1, 2 | Untested: one trait at the starting weight |
| KT-26 | New-kind threshold | How strong "I don't know" is from the start | 0.5 | 0.125, 0.25, 0.5, 1, 2 | Untested: one trait's worth of evidence |
| KT-27 | Per-spike cost | The energy one spike costs | Worked out | Not searched | Set by KT-47's rule, after the other 8 |
| KT-28 | TW7 gain | How fast a rate unit responds to its input | 1 | 0.25, 0.5, 1, 2, 4 | Untested |
| KT-29 | TW7 time constant | How quickly a rate unit settles | 10 ms | 2.5, 5, 10, 20, 40 ms | Untested: matches the 10 ms smoothing |

KT-47's rule sets the per-spike cost so that K-F's median thinking cost per decision equals 0.001 per check, the brute-force bots' price. If Week 3's hand-made cases show that a start value can't work at all (for example, a perfect copy never makes a neuron fire), Claude brings Aitzaz a replacement before any tuning-set run.

## What tuning aims at

Tuning aims at the power check's planned values, which sit a little above each rule's pass mark. The power check showed that a mind reaching exactly these values gets GO on 84% of kill-run sets of 40 families. Aiming at the bare pass marks leaves each rule a coin toss on new families, and all of them together worse. Aiming higher squeezes the 30 tuning families harder, and the gain may not carry over to new families. (Untested as a tuning goal; the conventional habit is to design to the effect size a power analysis assumed.)

| Rule | Measure | Pass mark | Tuning target |
|---|---|---|---|
| 1 | Settle rate | 0.95 | 0.97 |
| 2 | CopyAccept | 0.80 | 0.90 |
| 3 and 4 | D_learn (strict) | Floor + 0.15, and 0.25 | 0.35, or floor + 0.20 if higher (about 0.44 here) |
| 4b | FarMinusNeutral | 0.15 | 0.25 |
| 4c | LookReject, each half | 0.60 | 0.70 |
| 5 | Q after SOUR (strict) | 0.25 | 0.35 |
| 5 | Sour drop | At most 0.15 | At most 0.05 |
| 5 | Runs that notice the taste | 0.50 | 0.70 |

The floor is B1n-bot-r's or B1n-mind's mean D_learn on the same families, whichever is higher. Rules 4, 4b and 4c must also hold in every subgroup of at least 100 runs, as in the judge.

Rule 7 is not a target. It catches a leak of the essence into the mind, so tuning never aims at it. If any setting tried shows D at check 1 of 0.15 or more, tuning stops and Claude traces it with Aitzaz.

## How the search runs

The search changes one number at a time, keeps a change only when it brings K-F closer to the targets, and stops at the first setting that reaches them all. Picking the first setting that is good enough, rather than the best one found, matches K-F's own satisficing chooser and squeezes the tuning families less. (Untested for tuning; the conventional way is to search a grid for the best score.)

1. **Split the tuning set.** The 15 odd-numbered families are searched on and the 15 even-numbered ones are kept back for a check. Each half holds 10 families with a core trait in the object layer and 5 without, like the whole set. (Conventional: a held-out check.)
2. **Measure the start values** on the search half: 10 runs per family, 150 runs in all.
3. **One pass** goes through KT-19 to KT-26 in order. For each number, it tries the values in the table with the other numbers held, and keeps the value that misses the fewest targets. If two values miss the same number, it keeps the one that misses by less, with each shortfall measured in that measure's spread between families. A tie keeps the current value. (Conventional: one number at a time.)
4. **Stop early.** The moment a setting reaches every target on the search half, the search stops. That setting is the pick.
5. **At most 3 passes.** If no setting reaches every target after 3 passes, Claude stops and brings Aitzaz the numbers. Nothing more is tuned without Aitzaz.
6. **Set the per-spike cost** by KT-47's rule, then measure again. If the cost knocks a target out, one more pass runs, counted within the 3.
7. **Check on the kept-back half.** The pick runs on the 15 even-numbered families, with OS10 beside it. It must pass every GO rule there at the rule's own pass mark, judged as on a kill-run set. If it fails, Claude stops and brings it to Aitzaz.
8. **TW7** gets the same number of passes K-F used, over its gain and time constant only, with the same targets, stop rule and check. TW2, OS01, OS10 and K-F-NOWARM reuse K-F's values.
9. **Register** each chosen value as its row, KT-19 to KT-29, marked "set on KT tuning set", together with the log.

Every setting tried is written to a log in the repo, with all its measures. The report states how many settings were tried, so nothing is hidden. One pass tries at most 32 new settings, so 3 passes try at most about 100, each on 150 runs.

## Guardrails

The frozen rules of section 7 hold throughout. This plan adds three guardrails of its own and notes one limit.

- **From the frozen rules.** Only the 30 tuning families are used, and no kill-run set exists until the freeze. Every relevance weight starts at 0.5 and moves only by its fixed steps. No number differs by trait or by layer, and both are checked automatically. No tuned value enters Frankie's evolved settings (M17).
- **The limit: shared numbers can still fit the tuning set.** They set how sensitive the whole tower is, not what any kind looks like, so tuning can't teach K-F the tuning families' apples. They can still suit the tuning families' general conditions too closely, which is what the kept-back half checks.
- **No tuning toward a bot.** The floor's number enters only as rule 3's target. Nothing is tuned to make K-F act like B2e or any other bot.
- **No changes outside the search.** While Claude builds and debugs in Weeks 3 and 4, K-F runs only at the start values. A number changes only through the logged search.
- **The search is fixed before it runs.** The order, the values tried, the split and the stop rule are written here and can't change once the first tuning-set measurement is made. Changing any of them needs Aitzaz's OK, and the log records it.

## Aitzaz's three choices (1 Nov 2026)

1. **What tuning aims at:** the power check's planned values. The alternatives were each rule's bare pass mark (more likely to fall short on new families), or the most room above the pass marks (squeezes the tuning set harder).
2. **Which setting is picked:** the first setting that reaches every target. The alternative was the best setting after all 3 passes, which tries more settings and fits the tuning set more closely.
3. **Whether half the tuning set is kept back:** yes, search on 15 families and check on the other 15. The alternative was to search on all 30, which gives each setting more runs but leaves no check that the pick carries over.
