# Week 4: why K-F falls short on the tuning set

_2 Nov 2026. A read-only look Aitzaz asked for ("Diagnose first", 10:44 UTC) after the tuning search stopped. Nothing was tuned and no value in K-F's code changed. Every number here comes from the search half (the 15 odd tuning families, 10 runs each, 150 runs). The kept-back half is untouched. Script: [`kill-test/diagnose_week4.py`](../diagnose_week4.py). Raw counts: [`week4-diagnosis.json`](week4-diagnosis.json). Search log: [`tuning-search.jsonl`](tuning-search.jsonl)._

## In short

K-F fails mainly because **its memories of the same kind of apple compete with each other instead of adding up**. After a few tastes, K-F holds several "apple" kinds: one from the first apple, one from each later apple that didn't fit, and poison kinds split off from look-alikes. A new apple fits two or three of the apple kinds about equally. A winner must lead *every* rival by the commit margin, so they stall each other, and the decision ends unsettled, which means skip. **78% of the new apples K-F leaves unsettled at check 8 are stalled between two apple kinds.** Design notes 3 and 4 named this as the main risk on 25 Oct ("a later apple can fit several of them about equally"; "never merge ... may lower K-F's odds").

Spiking neurons make the stall worse but are not its root. TW7, K-F's rate-neuron twin, at the same values settles 99% of its decisions, but it settles on "I don't know" for new apples. Its D_learn is −0.09, worse than K-F's 0.14.

## The search's end point against the targets

The setting the search ended on: leak 0.4, threshold 10, refractory 8 ms, inhibition 0.625, detector width 5, commit margin 2, objection threshold 2, new-kind threshold 0.5. Passes 2 and 3 changed nothing.

| Measure | K-F | TW7 (same values) | Pass mark | Target |
|---|---|---|---|---|
| Decisions that settle | 0.571 | **0.991** | 0.95 | 0.97 |
| CopyAccept | 0.751 | **0.996** | 0.80 | 0.90 |
| D_learn (strict) | **0.136** | −0.092 | 0.401 (floor 0.251 + 0.15), and 0.25 | 0.451 |
| FarMinusNeutral | 0.271 | 0.084 | 0.15 | 0.25 |
| LookReject, h1 half / far half | 0.720 / 0.842 | 0.652 / 0.995 | 0.60 | 0.70 |
| Q after the sour apple | −0.047 | 0.112 | 0.25 | 0.35 |
| Sour drop | 0.000 | 0.000 | at most 0.15 | at most 0.05 |
| Runs that noticed the taste | 1.00 | 1.00 | 0.50 | 0.70 |
| D at check 1 (leak check) | −0.235 | −0.223 | below 0.15 | (not a target) |

The floor is plain trial and error, B1n-bot-r, on the same 15 families: 0.251. Both towers sit below it.

## What happens inside, per run (K-F, 150 runs)

**1. Same-kind items are rarely recognised as the same kind.** In warm-up, 40 tastes of 4 kinds make 25.6 new kinds per run, with only 14.4 stretches. Members of one kind differ widely on their free traits (each free range covers 60 to 100% of the scale), while a new kind stores only its first item's value ± one detector width (± 0.05 here). So the next member usually fits poorly. Memory fills with near-duplicates of the same few kinds. TW7 is worse: 37 new kinds from 40 tastes.

**2. The teaching apples a2 to a4** are named as an apple kind 41% of the time (stretching it). The rest of the time the decision is unsettled (44%) or "unknown" (15%), and each such apple starts a kind of its own. TW7 names an apple kind for only 6% of them.

**3. The teaching look-alikes** are mistaken for an apple 58% of the time, eaten and found poisonous. Blame then works as designed: 87% of those splits raise the weight of one of the 2 core traits the look-alike moved, usually in the details layer. But each split leaves a poison kind that is a close copy of the apple kind it came from.

**4. At check 8**, out of 8 far apples per run, K-F eats 2.4 while naming an apple kind, leaves 5.3 unsettled and calls 0.3 "unknown". **For 78% of the unsettled ones, the leader and a runner-up are both apple kinds.** Out of 8 look-alikes, it eats 1.8 and leaves 4.8 unsettled. At the end of an average decision, 6.8 groups sit within the commit margin of the leader.

**5. Objections are rare at this setting** (0.01 per decision, against nearly every decision at the start values). The search moved the objection threshold to 2, which mostly stops objections from firing. That removed the "everyone comes back after a reset" crowding of the start values, but not the stall between sibling apple kinds.

## What this means

- **This isn't a tuning problem.** The search converged in pass 1, and passes 2 and 3 changed nothing. When a setting made K-F settle more, it also ate more look-alikes: one setting reached D_learn 0.27 and ate half the look-alikes.
- **It isn't mainly a spiking problem.** Rate neurons settle, but learn less.
- **The block is in the design.** "Taste one apple, know them all" needs the first apple's kind to widen to cover different-looking apples. That widening (a stretch) happens only when K-F already recognises the new apple as that kind. A different-looking apple usually isn't recognised, so it starts a kind of its own. Its own kind then competes with the first one, and with no merges they never combine.
- **Under section 10, TW7 beats K-F on the settle rate** (0.99 against 0.57). That goes to Aitzaz under D12. Nothing switches automatically, and section 9's one design change may never adopt rate neurons.

## What the frozen rules allow next

- **Run the kill test as designed.** That means Week 5 (twins, a dry run), a freeze at this setting with KT-27 set by KT-47, then set A with Aitzaz's OK at each step. On these numbers the expected verdict is **NO-GO**: rule 1 (settle 0.95) and rule 2 (CopyAccept 0.80) both fail. After NO-GO, section 9 says "we stop and rethink the design with Aitzaz"; any later kill test needs a new addendum, frozen before the code changes.
- **Stop before the kill run.** Treat this tuning-set evidence as the answer for this design, and go straight to a rethink and a new addendum. That saves the Week 5 and 6 work, but the result is not a pre-registered kill-run verdict.
- **Not open within this addendum: a design change now.** Section 1 says a register row closed after the first K-F run "may not cite K-F results". Section 9's one design change exists only after an INCONCLUSIVE verdict, and these numbers point to NO-GO. Changing the design because of these results (for example, the merge rule note 4 set aside) belongs in a new addendum.
