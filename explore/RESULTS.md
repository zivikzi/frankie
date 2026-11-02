# Frankie Lab: results, 2 Nov 2026

## In one paragraph

E1 is a plain elimination mind that can merge kinds. It beat trial and error on families it was never tuned on: D_learn **0.45**, against trial and error's 0.24 and K-F's 0.16. It refused 88% of the look-alikes and ate every copy of the first apple. Turning merging off dropped it to **−0.14**, so merging is what makes it work. Checking the layers outside in versus all at once made **no difference** to E1 as chosen, though it did matter in a variant that compares kinds with each other (see below). E1 still misses one check: it notices the sour apple's taste in only 26% of runs, where the kill test needs 50%.

This is an exploration, not the kill test. The families are the tuning set's, and E1's settings were chosen by trying 25 variants on the odd half. The even half is an honest check, because nothing was tuned on it. A formal claim still needs a new charter version and fresh, sealed families.

## The numbers

Each figure is the mean over 15 families × 10 runs, through the frozen harness (`harness.run.run_one`, `harness.scoring.measures`), with the kill test's own pass marks. The floor is the better of B1n-bot-r and B1n-mind.

### The check half (even families, never tuned on)

| Mind | Settle | CopyAccept | D_learn | FarMinusNeutral | LookReject h1 / far | Q after SOUR | Sour drop | Noticed | D at check 1 |
|---|---|---|---|---|---|---|---|---|---|
| Pass mark | ≥ 0.95 | ≥ 0.80 | ≥ 0.389 (floor + 0.15) and ≥ 0.25 | ≥ 0.15 | ≥ 0.60 each | ≥ 0.25 | ≤ 0.15 | ≥ 0.50 | < 0.15 |
| **E1** | **1.00** | **1.00** | **0.452** | **0.518** | **0.875 / 0.885** | **0.786** | **−0.004** | 0.260 | −0.265 |
| E1, merging off | 1.00 | 1.00 | −0.140 | 0.001 | 0.742 / 1.000 | 0.086 | 0.000 | 1.000 | −0.265 |
| E1, all layers at once | 1.00 | 1.00 | 0.452 | 0.518 | 0.875 / 0.885 | 0.786 | −0.004 | 0.260 | −0.265 |
| E1 as first written | 1.00 | 0.985 | 0.000 | 0.000 | 1.000 / 1.000 | 0.000 | 0.000 | 1.000 | 0.000 |
| K-F (Week 4) | 0.553 | 0.726 | 0.158 | 0.296 | 0.755 / 0.813 | −0.045 | 0.000 | 0.993 | −0.195 |
| B1n-bot-r (trial and error) | — | 1.00 | 0.238 | 0.485 | 0.157 / 0.425 | 0.085 | 0.000 | — | −0.026 |
| B1n-mind (trial and error) | — | 1.00 | 0.239 | 0.453 | 0.157 / 0.397 | 0.085 | 0.000 | — | 0.004 |
| B2e (reads the answer) | — | 1.00 | 0.992 | 0.982 | 0.992 / 0.990 | 0.991 | 0.000 | — | 0.993 |

The frozen judge's own tests on E1, check half ([`results/judge-E1-even.json`](results/judge-E1-even.json)):
- **Rule 3's bootstrap against trial and error:** 0 of 10,000 resampled means at or below 0, so the gap is not chance.
- **The 0.15 margin:** only 195 of 10,000 resamples fall below it.
- **Rules 4, 4b and 4c** hold in every subgroup with 100 or more runs.
- **Rule 5's applicability fails** (noticed 0.26, against 0.50 needed), so on a kill-run set this would be INCONCLUSIVE, not GO.

### The search half (odd families, where E1 was developed)

| Mind | Settle | CopyAccept | D_learn | FarMinusNeutral | LookReject h1 / far | Q after SOUR | Noticed | D at check 1 |
|---|---|---|---|---|---|---|---|---|
| **E1** | 1.00 | 1.00 | **0.434** | 0.505 | 0.875 / 0.895 | 0.750 | 0.367 | −0.285 |
| E1, merging off | 1.00 | 1.00 | −0.144 | 0.000 | 0.710 / 1.000 | 0.087 | 1.000 | −0.260 |
| E1, all layers at once | 1.00 | 1.00 | 0.434 | 0.505 | 0.875 / 0.895 | 0.750 | 0.367 | −0.285 |
| K-F (Week 4) | 0.571 | 0.751 | 0.136 | 0.271 | 0.720 / 0.842 | −0.047 | 1.000 | −0.235 |
| B1n-bot-r | — | 1.00 | 0.251 | 0.573 | 0.210 / 0.433 | 0.113 | — | −0.040 |
| B1n-mind | — | 1.00 | 0.247 | 0.433 | 0.210 / 0.392 | 0.113 | — | −0.007 |
| B2e | — | 1.00 | 0.990 | 0.994 | 0.990 / 0.988 | 0.985 | — | 0.992 |

K-F's numbers match the Week 4 log exactly, as they should: same code, same families.

### The learning curve (D after 1, 2, 4, 6 and 8 tastes, check half)

| Mind | After 1 | After 2 | After 4 | After 6 | After 8 |
|---|---|---|---|---|---|
| E1 | −0.27 | −0.16 | 0.43 | 0.74 | **0.80** |
| Trial and error (B1n-bot-r) | −0.03 | 0.13 | 0.26 | 0.28 | 0.28 |
| K-F | −0.20 | 0.16 | 0.20 | 0.14 | 0.13 |

E1 starts worse than trial and error. After one apple it eats look-alikes, because nothing has yet told it which traits matter. From the fourth taste on, it pulls far ahead. Trial and error levels off at about 0.28.

## Why E1 works where K-F didn't

Week 4 found that K-F's apple kinds stall each other: each new apple started a kind of its own, and they never merge. E1 fixes that with two untested rules on top of conventional merging:

1. **Kinds met in the same scene, with the same outcome, merge.** They merge unless they disagree on a trait that has proved relevant. The context layer (scene and host) always has to agree, which is the outermost layer limiting the rest.
2. **When a merge or stretch widens a trait a lot, that trait stops counting.** Here "a lot" means more than 10 noise widths. Free traits vary from apple to apple, so they drop out; core traits stay narrow, so they keep counting.

Blame does the rest. When E1 mistakes a look-alike for an apple and is poisoned, it raises the relevance of the traits that didn't fit, more than 10 noise widths out. Those are almost always the look-alike's two moved core traits, because look-alikes copy everything else to within 10 noise widths.

So after the eight teaching tastes, E1's apple kind holds narrow ranges on the core traits and ignores the free ones. That is the "essence" the test is about, learned from experience rather than read from the answer.

## What each idea contributes

- **Merging: essential.** With it off, D_learn is −0.14 on both halves. Without merging, every apple stays a separate kind, and nothing learns that free traits vary.
- **Outside-in: no effect on E1 as chosen.** E1 eliminates a kind once its relevance-weighted misses pass a fixed total. A total is the same in any order, so checking all layers at once gives identical verdicts; only the amount of checking differs.
  - **Outside-in matters when elimination is relative,** that is, when a kind is dropped for trailing the best surviving kind at each layer. On the search half, relative elimination outside in scored D_learn 0.194, and all at once −0.126. But relative elimination is worse than the fixed threshold overall (0.194 against 0.434).
  - So in these experiments, outside-in helps a mind that compares candidates as it goes, but the best mind found doesn't need it. **Untested** whether that holds for other designs.
- **Context gating of merges: helps a lot.** Turning only that off in the chosen E1 dropped D_learn from 0.434 to 0.130 on the search half. Kinds met in other scenes (the warm-up's) then merge into the apple kind and blur it.
- **Merge widening: essential.** Turning off only the rule that a merge stops counting the traits it widens dropped D_learn to 0.039. Merged kinds then cover the look-alikes too, because nothing tells them which traits vary.

## Every variant tried (25, all on the search half)

Each row is in [`results/variants.jsonl`](results/variants.jsonl) with all its numbers. The chosen E1 is "E1 ctx down5". Its settings are: miss tolerance 10 noise widths; elimination at 1.0 relevance-weighted misses; a stretch or merge that widens a trait by more than 10 noise widths drops that trait's relevance by 5 tenths (to 0); merging with the cut-off at 5 tenths; context always gating merges.

| # | Variant | D_learn |
|---|---|---|
| 1 | E1 as first written (the brief's starting design) | 0.000 (refuses everything) |
| 2 | threshold 3 | −0.005 |
| 3 | threshold 6 | −0.542 |
| 4 | threshold 10 | −0.730 |
| 5 | tolerance 10, threshold 3 | −0.480 |
| 6 | tolerance 10, threshold 6 | −0.673 |
| 7 | … plus a stronger relevance drop (3) | −0.254 |
| 8 | … plus merge cut-off 5 | −0.729 |
| 9 | tolerance 10, relative elimination 2 | −0.740 |
| 10 | tolerance 10, threshold 6, drop 3, cut-off 5 | −0.328 |
| 11 | ctx: context-gated, widening merges (drop 2) | 0.054 |
| 12 | ctx, drop 3 | 0.128 |
| 13 | ctx, threshold 1.5 | −0.111 |
| 14 | ctx, tolerance 6 | 0.047 |
| 15 | ctx, drop 3, threshold 0.9 | 0.189 |
| 16 | **ctx, drop 5 (chosen E1)** | **0.434** |
| 17 | ctx, drop 3, tolerance 8 | 0.129 |
| 18 | ctx, drop 3, split +3 | 0.130 |
| 19 | ctx, drop 5, threshold 0.9 | 0.376 |
| 20 | chosen E1 with relative elimination | 0.194 |
| 21 | … all at once | −0.126 |
| 22 | relative elimination, threshold 2 | −0.097 |
| 23 | … all at once | −0.126 |
| 24 | chosen E1 without context gating (an ablation) | 0.130 |
| 25 | chosen E1 without merge widening (an ablation) | 0.039 |

## Honest limits

- **Not a pre-registered test.** E1 was shaped by 25 tries on the odd half. The even half wasn't used to choose anything, but it comes from the same tuning key, the same bench and the same kind of families.
- **It learns slowly at first.** After one taste it is worse than trial and error (D −0.27). It needs 3 or 4 tastes before it beats it.
- **It rarely notices the sour taste** (26%). Its merged apple kind has wide taste ranges, because apples' tastes vary, so a sour apple rarely looks new. The kill test needs 50% of runs to notice, so rule 5 would be "uninformative".
- **The bench's numbers are synthetic.** An "apple" is 22 numbers with 4 hidden core traits in a narrow band. E1's success says the elimination-plus-merging idea can find those core traits from 8 tastes. It doesn't yet say anything about the real world.
