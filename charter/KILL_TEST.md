# Kill test: does the core idea work?

_FRANKIE · charter addendum · version 3 · 25 Oct 2026 · frozen together with the charter, before any kill-test code exists_

On 24 Oct, Aitzaz chose to test the riskiest bet first instead of building for 9 months. This addendum fixes, in advance, what that test is and what counts as a pass or a fail. It is a **go/no-go check**. It is **not evidence of intelligence**, and it never appears in the claims report as evidence.

> **About version 3.**
> - **Version 1** was attacked by a reviewer whose job was to pass it cheaply, and checked by a second for whether it could be built.
> - **Version 2** was rewritten after Aitzaz chose **"a few tastes, same for every mind"** over a one-taste test. Aitzaz approved it on 24 Oct ("approve all").
> - **Version 3.** A final five-way check of version 2, run before the freeze, found 8 serious problems. These included a rule that made the test impossible to generate, a starting value that stopped the memory rule from raising any weight, and a sour-apple check that scored noise. A second four-way check of the fixes, with a bot-only simulation, found 4 more. The worst were that the taste check could miss a mind that does notice taste, and that the power check could never pass as written. Version 3 fixes all of them without changing the design.
>
> Section 13 lists every placeholder and says which ones changed after Aitzaz's approval.

## In plain words

The question is: **does your outside-in tower learn to tell apples from poison look-alikes faster than brute trial and error, given the same few tastes?**

Every mind is fed the same 8 items, one at a time. Four are apples that look very different from each other. Four are poison look-alikes, and each one copies the look and taste of the apple before it. After tastes 1, 2, 4, 6 and 8, we check what each mind would do with apples and look-alikes it has never seen. Each check runs on a throwaway copy of the mind, so checking teaches it nothing. Then comes the sour apple.

Brute trial and error has to be beaten by a clear margin. That means a mind that simply remembers every item it ate and copies the nearest one. A list of cheating bots also has to fail. If the tower wins, we go on to the trimmed version 1. If it doesn't, we stop and rethink it together, and nothing conventional gets bolted on to rescue it.

**Why not one taste?** In this test there's no evolution, so a newborn mind has no way to know which traits make an apple an apple. After one red apple, the red look-alike is the closer match. Every honest mind would fail, and only a mind told H's core traits in advance could pass, which the charter bans. One taste stays the headline test of version 1, where evolution gives Frankie its head start. Here, the one-taste result is kept only as a **leak check** (rule 7): a mind that does well after one taste has had the answer smuggled in somewhere.

## 1. What the kill test may and may not do

- It may not touch, generate or peek at any sealed test vault.
- It may not tune anything on a kill-run set.
- It may not use any mechanism in [FORBIDDEN.md](FORBIDDEN.md).
- After results are seen, no rule or number here may change. Any later kill test needs a new addendum (section 9).
- **Exception to X01, X40 and T17.** These rows say no Frankie mind code may exist until the test battery, the motif tokenizer and the teacher's closure library are frozen. K-F (section 4) is a bench-only prototype with no body, no movement and no action repertoire, so it can't contaminate the tokenizer or the closure library. K-F may therefore exist before Wave 1, on these conditions:
  - Every kill-test bot and the analysis script are frozen and fingerprinted before any K-F code ("brute baseline first", X01).
  - Every register row closed after the first K-F run, except section 7's tuned-value rows and the edits of section 9's one design change, is flagged "closed after K-F existed". It needs Aitzaz's initials and may not cite K-F results.
  - The exception covers K-F only, never v1 Frankie (section 12).
  - Wherever the charter says "before any mind code exists", "before the mind exists" or "before Frankie's mind exists" (X01, X40, T17, C7, C8, C12, C13-E and the glossary's motif-tokenizer entry), it means before any Frankie mind code other than K-F.
- **The kill test replaces neither Stage 5 nor Stage 6.** It is an early, practice-only run of the Stage 5 bench. Their gates (X29, M44), and every register row they need, are still met in order before Stage 7.

## 2. The objects

**Practice only.** Every kind comes from practice generators, and sealed vaults are never generated. Development-vault families go only to the tuning set.

**Traits** (PLACEHOLDER-57, KT-01). Each object has 22 numbers, each from 0 to 1:

| Group | Traits |
|---|---|
| Context | scene, host |
| Object | coarse hue, size, roundness, lobes |
| Parts | 5 traits |
| Details | 7 traits, including exact hue |
| Taste | sweet, sour, bitter and salty (PLACEHOLDER-47), known only after eating |

- **Exact hue** has no range of its own and is never checked against one. It is the object's coarse hue plus a hue offset, clipped to 0 to 1, so it changes whenever coarse hue does. Apples, neutrals and members of the warm-up kinds draw their offset uniformly within ±0.05. A look-alike, in teaching, warm-up or checks, takes its model's offset, and a copy takes h1's. So a look-alike's exact hue differs from its model's by no more than its coarse hue does.
- For the tower and the memory rule, the 4 taste traits are **detail traits** (M51, PLACEHOLDER-92). They join the details layer once known and are blamed with it (M11). They are listed apart only because they are never visible before eating.
- Sensor noise is 1% of each trait's range (PLACEHOLDER-45). One noise width is one standard deviation of that noise.
- Every object is seen at sharp range, so all four layers are visible.

**Kinds** (KT-02).

- **Core traits.** Every kind has exactly 4 core traits. They are drawn uniformly, without replacement, from 13 eligible traits: roundness, lobes, the 5 parts traits, and the 6 details traits other than exact hue. Each core band is 0.05 wide, with its centre drawn uniformly from 0.025 to 0.975.
- **Free traits.** Every other trait except exact hue has a range whose width is drawn uniformly from 0.6 to 1.0 and which is placed uniformly inside 0 to 1.
- **Taste.** H's 4 taste traits always range over the full 0 to 1, so a super-sweet and a super-sour apple can both belong to H. Taste is never core.
- **Why random layers.** If core traits always sat in one layer, a tower that simply weighed that layer more would win without learning anything. With random placement, no layer is guaranteed free except context.
- **Why exactly 4.** With 2 or 3 core traits, a bot that learns one single trait can pass (see G07 and rule 4c).

**Roles in each family H** (KT-03):

- **Apple** (a member of H). Every core trait lies inside H's bands. Every free trait, taste included, is drawn uniformly from H's free ranges, except that every apple other than h1 takes h1's scene and host (Context, below).
- **Far apple** (used only in checks). An apple whose coarse hue and size are each at least 0.3 of range from h1's. That part always leaves some room, since every free range is at least 0.6 wide, though sometimes very little. Its surface distance from h1 (PLACEHOLDER-91) is also greater than that of every look-alike modelled on h1 in the same check set. Look-alikes modelled on far apples have no surface-distance condition.
- **Look-alike.** A member of a poison kind built around H. It copies a named apple, its "model": every free trait other than scene, host and exact hue, **taste included**, is the model's value plus an independent offset drawn uniformly within ±0.10, clipped to 0 to 1 (PLACEHOLDER-59). Its scene and host are h1's (Context, below), and its exact hue follows the Traits rule above.
  - Its kind keeps H's bands on 2 of H's core traits (its values are drawn inside them) and moves the other 2.
  - Each moved band is 0.05 wide. The gap between its near edge and H's band edge is drawn uniformly from 20 to 30 noise widths first. The band then goes on whichever side has room for it at that gap (at random when both do). At least one side always has room, since the two sides of H's band add up to 0.95 of range.
  - So each core difference from the model (at least 20 noise widths) is clearly larger than any free-trait difference (at most 10). A well-tuned detector width can therefore tell them apart.
  - Taste is copied too, so taste alone can never explain why a look-alike was poison, and the mistake has to be traced to the core traits.
- **Look-alike kinds** (KT-04). The family key labels H's core traits c1 to c4. Each family has 8 look-alike kinds:
  - Kinds 1 and 2 are used only for teaching. Each moves a different pair of core traits, drawn by the family key.
  - Kinds 3 to 8 are used only in checks, one for each of the 6 possible pairs. The pairs fall into three sets of 2 non-overlapping pairs: M1 = {c1c2, c3c4}, M2 = {c1c3, c2c4} and M3 = {c1c4, c2c3}.
- **Neutral.** A member of a never-seen kind of nature "nothing". Each family has 4 neutral kinds: P's 2 neutrals come from kinds 1 and 2, and Q's 2 from kinds 3 and 4. Each neutral lies at least 10 noise widths outside H's bands on 2 or more of H's core traits, and its surface distance from h1 is within ±10% of the mean surface distance of P's far apples. Like every check item, it carries h1's scene and host.
- **Copy.** h1's exact trait values, with fresh sensor noise.

**Context.** Every teaching item and every check carries h1's scene and host (C1-CONTEXT). Each warm-up kind has its own scene and host, each drawn once per run, uniformly from the values at least 40 noise widths from h1's, and fixed for that kind. That is always possible, since every value has a point at least 0.5 of range away. So the scene layer can set warm-up kinds aside for every mind alike, and context carries no information about H versus its look-alikes or neutrals.

**Keys.**

- The family key draws H itself, its look-alike kinds, its neutral kinds and the core-trait labels c1 to c4.
- The run key draws everything else:
  - R and b;
  - the warm-up kinds and items;
  - h1, a2 to a4 and the teaching look-alikes;
  - P, h2, Q and SWEET-CONTROL;
  - the trait order in section 6;
  - all sensor noise.

**Certificates.** Every generated object is checked against the rules above.

- **Draw order.** Within a run, objects are drawn in this order: h1; the warm-up kinds and items; a2 to a4; the teaching look-alikes; P's 4 look-alikes modelled on h1; P's far apples; P's other look-alikes; P's neutrals; h2; Q's objects.
- A failing object is redrawn with the next draw number of the same key. When a rule compares two objects, the later-drawn one is redrawn.
- If a far apple or h2 gives no passing draw in 10,000 draws, every object from P's 4 look-alikes modelled on h1 onward in the draw order is drawn again with its next draw numbers, and this is logged. Every 10th time that happens in one run (the 10th, the 20th and so on), h1 is drawn again with its next draw number, every later object in the draw order is drawn again, and this is logged.
- **Taste limits are part of the draw.** Each taste limit on h1, a2 to a4 and h2 (section 5) is met by drawing that taste uniformly within its limit, not by redrawing.
- If a warm-up or neutral kind gives no passing object in 1,000 draws, that kind is replaced, for that run only, by the next kind draw of the same key, and this is logged.
- h2 must also meet the far-apple rule against P's 4 look-alikes modelled on h1.
- A warm-up item is drawn from its own kind's core bands and free ranges, with its kind's scene and host (a poison item is modelled as in section 5). No role rule of the bench family applies to it.
- No warm-up kind may have core bands within 10 noise widths of H's bands on 2 or more of H's core traits. This is checked at kind level.
- Every redraw is counted and logged, and nothing is ever dropped after a run.

## 3. Sets, keys and the order of runs

- **Tuning set: 30 families.** They are generated from a tuning key committed in Week 0. Looking at results here is allowed, within the limits of section 7. Throwaway practice families from the same key (numbers 1,001 and up) may be used only to test the generator and for the power check (section 7).
- **Kill-run sets A, B and C.** Each has 40 families, or more if the power check in section 7 asks for it, never fewer. The size is fixed before set A's key exists.
- **Kill-run keys** (KT-14).
  - Each set's key is the SHA-256 of the block hash, as hex text, of the Bitcoin block at height N + 6.
  - Each set has its own code-freeze manifest, which names the set (A, B or C), so no two sets share a manifest. Each freeze writes one manifest, for the next unused set only, and it is pushed only after every earlier set has been run or retired. The first manifest pushed in turn that names a set is that set's only manifest. Any other manifest naming that set, whether pushed earlier (out of turn) or later, is void, makes no key, and is listed in the report.
  - When the manifest is pushed, the repository's GitHub Action stamps it with the OpenTimestamps client's default calendars and, in the same workflow run, commits the pending proof to `freeze/`. The proof names every calendar that answered. Only the first proof committed for a manifest, and the Action's upgrades of that proof, count. If the Action's run fails, it is re-run, and the first proof it commits counts.
  - Every 6 hours the same Action upgrades a fresh copy of that first proof, asking every calendar with a pending attestation in it, and commits the result to `freeze/` as a new file named for the run, whether or not it changed. N is read from the first such upgrade, committed within 7 days of the push, in which every calendar with a pending attestation in the first proof has given its Bitcoin attestation. If there is none, N is read from the last upgrade committed within those 7 days that holds any Bitcoin attestation, or, if none does, from the first later upgrade that does. N is the lowest block height among the Bitcoin attestations in that upgrade, and it is then fixed. The report names that commit, and anyone can check each attestation in it against Bitcoin, so trimming a proof, stamping again or a later upgrade can't change N.
  - So nobody, Claude included, can generate, preview or choose a kill-run set before the code is frozen. (Conventional: a public randomness beacon.)
  - No other kill-run sets exist. The report lists every freeze manifest ever pushed, with its Action run.
- **Separation from tuning.** The look-alike and neutral kinds in kill-run checks never appear in the tuning set, and the certificate checks this. Warm-up kinds always come from the tuning set.
- **Order on each set.** One frozen script generates the set, runs every non-tower mind first, and judges rule 6 (bench validity) before any tower mind runs.
  - If rule 6 fails, the set is retired without any tower having seen it, and the cause is traced with Aitzaz, as in rule 7:
    - **If the bench code departs from this addendum,** the code is fixed on the tuning set. Every bot, rule 6, the positive control and the power check are re-run and re-frozen before the next set's key exists. The re-freeze is tagged `charter-killtest-code-v1.1`, `v1.2` and so on. The re-run uses the set size already fixed. If rule 6 fails on the tuning set, the positive control fails, or the power check doesn't reach 80% at that size, section 1 applies and a new addendum is needed.
    - **If no departure is found,** the next set is used with nothing changed, under its own manifest.
    - **If the cause lies in a rule or number of this addendum,** the object design included, section 1 applies and a new addendum is needed.
    - In no case is K-F's frozen configuration changed or re-tuned, and the one design change (section 9) is not used up.
  - Otherwise the tower minds run, and the script prints the verdict table before anyone sees a per-family result.
- **K-F is judged on at most two sets.** On the second one, GO needs every rule, and any other outcome is NO-GO. If no set is left, the result is NO-GO ("the bench could not be built").
- Every report lists every kill run ever made, with its outcome. Used sets are retired.

## 4. The minds

All minds see the same objects, in the same order, with the same keys (X38 matching). Tower minds also share the temperament draw and stream keys for each run.

| ID | Mind | Role |
|---|---|---|
| K-F | **Frankie tower.** A spiking (D12) outside-in elimination tower (D13, section 6), "blame moves outward" memory (D3), and a satisficing eat/skip choice through the drive (section 5). Neutral hand-set perception: every relevance weight starts at 0.5. That is equal (M20) and the middle of the 0-to-1 range (KT-10). Memory is empty at birth. | The thing being tested |
| B1n-bot-r | B1n-bot plus one acceptance radius r (rules below) | **Must be beaten** (brute trial and error, tuned) |
| B1n-mind | Frankie's drive (section 5) with the tower and memory replaced by a nearest-neighbour memory of each eaten item (X36) | **Must be beaten** (brute trial and error inside Frankie's drive) |
| B1n-bot | Plain nearest neighbour, with no radius (X36) | Reported |
| G08 | Best two-trait bot (X33) | Reported. A simple rule-finder can learn this bench, so it shows whether the tower beats a simple rule-finder, not only brute force. |
| TW7 | K-F with ordinary rate neurons in place of spiking ones (M43) | Reported (spiking vs ordinary, D12) |
| TW2 | K-F with the conventional stretch-or-split memory rule (M16, section 6) | Reported (blame-outward vs textbook) |
| OS01 | K-F with all layers at once, no outside-in order. Runs in both settings: cap (thinking spend capped to K-F's) and free (thinking costs nothing). | Reported (does outside-in order help?) |
| K-F-NOWARM | K-F with no warm-up | Reported (how much the warm-up matters) |
| OS10 | K-F with taste removed from memory and from the verdict after eating | Validity check for the sour apple |
| B2e | Essence-trait matcher: reads H's core traits from the generator (X03) | Positive control: shows the bench can be solved at all |
| B1t, B2, G01, G04, G05, G06, G07, G09, G16, G17, G18 | Cheating and shortcut bots (below) | **Must fail** (rule 6) |

**Bot rules** (KT-05). These hold for every bot:

- Distances are mean absolute differences, in noise widths, over the traits named. "Observable" means context, object, parts and details, never taste.
- Bots store each item at the moment they eat it. At the check after teaching taste k, a bot holds the 40 warm-up items and teaching tastes 1 to k, so it holds all 48 forced items only at check 8.
- "Good" means outcome above 0, and "bad" means any other outcome. Ties go to the most recent item.
- "Exact" means within 5 noise widths on every observable trait.
- A bot's choices never read energy. (B1n-mind is not a bot: it chooses through Frankie's drive.)

The bots:

- **B1n-bot:** finds the nearest stored item over all observable traits, and eats if it was good.
- **B1n-bot-r:** B1n-bot that eats only if the nearest stored item is good and lies within r. r is chosen from the grid {2, 4, 6, 8, 12, 16, 24, unlimited} noise widths to maximise its mean D_learn on the tuning set. It is registered and frozen before any K-F code.
- **B1n-mind:** its "named candidate" is the nearest stored item, and that item's own outcome is its whole record. It judges an object "unknown" when the nearest stored item is farther than its own radius, chosen like B1n-bot-r's. Its reliability is always 1. Otherwise it chooses exactly as section 5 says.
- **B1t:** skips exact matches of bad items and eats everything else.
- **B2:** eats if the surface distance (object layer only, PLACEHOLDER-91) to the nearest stored good item is at most 10.
- **B2e:** eats only if some stored good item lies within 8 noise widths of the object on every one of H's 4 core traits. That allows 5 for the band's width plus 3 for noise. It reads no other trait.
- **G01:** always eats.
- **G04:** eats only exact matches of a stored good item.
- **G05:** eats exact copies of h1, and anything whose surface distance from h1 is above 10, and refuses the rest.
- **G06:** B1n-bot with each trait weighted by its rarity, which is 1 minus the share of stored items within 5 noise widths on that trait.
- **G07:** using only the stored teaching items, picks the single observable trait whose rule "within 8 noise widths of the good items' range" classifies the most of them correctly. Ties go to the lower trait number. It eats only if the object is within 8 noise widths of that range on that trait.
- **G08:** the same, using the best pair of traits. It eats only if the object is within on both.
- **G09:** eats in h1's scene and refuses elsewhere. Every check is in h1's scene, so it eats everything.
- **G16:** B1n-bot-r computed over parts and details traits only (an inner-layer matcher), with its own r chosen the same way.
- **G17:** a near-copy refuser. It acts as B1n-bot until a stored bad item lies within 10 noise widths of a stored good item, over all observable traits. From then on, it also refuses any object that lies within 10 noise widths of some stored good item, over all observable traits, and is not an exact match of any stored good item.
- **G18:** G16, with G16's r, that also applies G17's trigger and near-copy refusal, over all observable traits.

**Thinking costs.** K-F pays the frozen per-spike cost (M42). TW7 and OS01 in its cap setting pay 0.001 per candidate-feature check (B14), and OS01 in its free setting pays nothing for thinking. In its cap setting, OS01's spend in each decision is limited to K-F's median per-decision thinking spend in the same run, as in C4's cap rule (PLACEHOLDER-104). Once it reaches the limit, it makes no more checks in that decision and settles on what it has, by section 6's rules. Every tower mind pays one sharp-look cost of 0.03 per object (B13). Bots pay nothing, since their choices never read energy.

## 5. One run

Each family gets **10 runs per mind**, each with a different run key. So a set of 40 families gives 400 runs per mind.

**Energy.**

- For each run, the reserve R is drawn from 20 to 60 and boldness b from 0.1 to 0.6, using the run key. Both are the same for every mind (M33).
- Start energy is 60.
- Eating gives nourish +15, poison −20 and nothing 0. The outcome lands at once, with no stomach delay or sickness.
- Energy is set to R + 10 by a logged injection (W45, kill-test entry) at these points:
  - before every warm-up and teaching taste;
  - before h2 and SWEET-CONTROL are offered;
  - at the start of every check copy.

**How the drive chooses on the bench** (KT-08). This is built from M22, M47, PLACEHOLDER-05 and PLACEHOLDER-27. Each object is one decision between eat and skip, considered in that order. Habits are off, as in off-switch OS07, and this is recorded in the version field with version_scope = lifetime.

- **Eat's chance** for a named candidate. Take the eats on record under that candidate itself, and the share of them after which energy stayed at or above R. Then eat's chance = 1 − (1 − share) × (2 − reliability), as in PLACEHOLDER-05, and never below 0.
  - An eat is on record under the candidate that memory files it under after the write, including the eat that created it.
  - Records never cross a split in either direction. A split child starts with only the eat that created it (PLACEHOLDER-04), and its parent keeps its own. So a look-alike split off into a new kind takes its poison record with it.
  - A merge keeps the records of both candidates.
  - Lineage (X46) is used only for naming H (section 8), never for eat's chance.
- **An "unknown" or "unsettled" verdict is always a skip** on the bench. This departs on purpose from M24 and PLACEHOLDER-34. Every eat that teaches is forced here, so their untried-value tally would be set by the bench design, not by recognition. The tally is still logged.
- **Skip's chance** is 1 if energy minus the thinking cost is at least R, and 0 otherwise.
- **The bar** is 0.9 − 0.3 × b. The first option that clears the bar is taken. If neither does, the M47 fallback applies, logged with no_safe_option = true.
- PLACEHOLDER-21's 200-tick horizon becomes "right after the eat". PLACEHOLDER-37's strike rule doesn't apply on the bench.

**Steps.**

1. **Warm-up: 40 forced tastes** (KT-06). There are 10 items from each of 4 kinds, drawn by the run key from 4 different tuning families other than H:
   - 1 nourishing kind, which is another family's H;
   - 1 poison kind, which is one of another family's 8 look-alike kinds, with each item modelled on a fresh apple of that family;
   - 2 "nothing" kinds, each one of another family's neutral kinds.

   The order is shuffled by the run key. Each mind looks, commits a verdict and is then made to eat, so every mind gets identical experience. K-F-NOWARM skips this step.
2. **Teaching: 8 forced tastes, in this order** (KT-07):
   - t1 = h1, a super-sweet apple (sweet at least 0.9, sour at most 0.1);
   - t2 = a kind-1 look-alike modelled on h1;
   - t3 = apple a2;
   - t4 = a kind-2 look-alike modelled on a2;
   - t5 = apple a3;
   - t6 = a kind-1 look-alike modelled on a3;
   - t7 = apple a4;
   - t8 = a kind-2 look-alike modelled on a4.

   Apples a2 to a4 have sour at most 0.5, so the later sour apple is a real surprise. For each item, in this order: the mind looks and commits a verdict, is made to eat, the outcome lands, a tower mind makes its verdict after eating (section 6), and the mind's own memory rule updates. A forced eat judged "unknown", or with no settled verdict, follows PLACEHOLDER-93.
3. **Checks.** Snapshots S1, S2, S4, S6 and S8 are taken right after tastes 1, 2, 4, 6 and 8, once that taste's outcome has landed and the mind's memory write for it is complete (for bots, once the item is stored), with no time passing in between. So a restored copy has no write pending. From each snapshot, check set P runs on 20 fresh copies of the mind, one item per copy. Each copy has its own replica key (W52). P stays the same at every checkpoint in a run. It contains:
   - 8 far apples;
   - 8 look-alikes, in two halves:
     - **the h1 half:** 4 modelled on h1, from the kinds for the pairs in M1 and M2;
     - **the far half:** 4 modelled on far apples 1 to 4, from the kinds for the pairs in M1 and M3.

     So each core trait is moved in exactly 2 of the 4 look-alikes in each half.
   - 2 neutrals;
   - 2 copies of h1.
4. **Sour apple** (KT-16). From S8 there are two branches. They share one replica key, so everything up to the moment the taste lands is identical in both.
   - **SOUR** gives h2, a new far apple (not one of P's) that is super-sour:
     - sweet at most 0.1 and sour at least 0.9;
     - a taste at least 10 noise widths from h1's and from each of a2's to a4's, as the mean absolute difference over the 4 taste traits.

     It still nourishes +15.
   - **SWEET-CONTROL** gives h2 itself with its 4 taste values replaced by the centres of one candidate's stored taste ranges. That candidate is the one h2's verdict named, if it is in the H set (section 8), and h1's candidate otherwise. The verdict comes before the taste and is the same in both branches, so the candidate is known before SWEET-CONTROL is built. It also nourishes +15. For a mind that stores no taste ranges (OS10, B1n-mind and every bot), the 4 taste values are h1's.
   - Each is forced if skipped, and flagged.
   - These shared keys depart on purpose from W52's own key for each clone (section 13, edit 6).

   Check set Q then runs on copies taken from S8 itself, and from each branch once its memory write for h2 or SWEET-CONTROL is complete. Each probe uses the same replica key in all three, so they are compared probe by probe. Q contains:
   - 4 apples whose observable free traits are within 10% of range of h1's, and 4 within 10% of h2's. Each draws every observable free trait other than scene, host and exact hue uniformly from the part of H's free range within 0.10 of h1's value (or h2's), and draws its core traits and taste as any apple does. These limits are part of the draw, not a certificate;
   - 8 look-alikes from kinds 3 to 8: 4 modelled on h1 (from the M1 and M2 kinds) and 4 modelled on h2 (from the M1 and M3 kinds);
   - 2 neutrals, made by the neutral rule using P's far apples;
   - 2 copies of h1.

   The far-apple certificate doesn't apply to Q.

That is 210 decisions per run: 40 + 8 + 5 × 20 + 2 + 3 × 20.

## 6. Pieces of the tower fixed for the bench

All of these are Claude placeholders (KT-09 to KT-11, KT-16 and KT-17).

- **Rows inherited as written** (KT-17). Every Stage 5 and 6 register value that applies to a bench decision holds as written, unless this addendum replaces it. That includes PLACEHOLDER-01, -03, -05, -07, -08, -09, -10, -13, -14, -15, -18, -92 and -93.
  - Where a row says "evolved", it means the value tuned under section 7.
  - PLACEHOLDER-14 has no evolved check order on the bench. Ties among relevance weights are broken by a trait order drawn once per run from the run key. The order is the same for every tower mind, and it is logged.
  - On the bench, "the current tick" in M07 and PLACEHOLDER-13 means the current decision, or the current verdict after eating: every candidate eliminated earlier in it comes back after a reset.
  - Before an eat, PLACEHOLDER-14's 3 traits are picked from the visible traits only. Its 3-trait limit doesn't hold taste out of the verdict after eating (below).
- **The verdict after eating** (M51, PLACEHOLDER-92, KT-16).
  - Right after each eat's outcome lands, and before that eat's memory write, the tower settles once more on the same item for 30 steps, with its 4 taste traits now known.
  - Its details layer reads all 4 taste traits as well as the up to 3 visible traits PLACEHOLDER-14 picks, so taste takes part for every candidate that reaches the details layer. (TASTE-NOTICED scores the chosen candidate's taste even if it did not, section 8.)
  - This settle chooses no action, pays no thinking cost and isn't counted in the settle rate.
  - It never changes whether the guess was right or wrong, which depends only on the energy outcome (M51). The memory write still works from the verdict committed before the eat.
  - It is logged, and TASTE-NOTICED reads it (section 8).
- **Starting weights.** Every relevance weight starts at 0.5, at birth and in every brand-new candidate. That is equal on every trait (M20) and the middle of PLACEHOLDER-02's 0-to-1 range (KT-10). So PLACEHOLDER-02's +0.2 and −0.1 steps can both act.
- **A brand-new candidate** has no parent (it is made from "unknown" or by a forced eat). It starts with every relevance weight at 0.5, every range at the observed value plus or minus one detector width, a count of 1, and the outcome just experienced. PLACEHOLDER-04's "copy the parent's weights" applies only to splits.
- **Time base** (replaces PLACEHOLDER-17 on the bench).
  - One settling step is 10 leaky integrate-and-fire substeps of 1 ms each, with 8 neurons per candidate group.
  - Detectors inject steady currents in proportion to their coarse-coded response. The neurons themselves add no noise; the only randomness is sensor noise from the sensor-noise stream (W37).
  - A candidate's activation, which the commit and objection rules read, is its group's spike trace, smoothed with a 10 ms time constant.
  - Every neuron and trace starts each decision, and each verdict after eating, from rest.
- **Settling** (KT-10).
  - **Winning.** A candidate wins at step s if it leads every other candidate, and "unknown", by the commit margin at steps s − 1 and s (PLACEHOLDER-12). "Unknown" wins the same way. A new win after an objection reset counts.
  - **Settling.** A win settles if the winner stays the leader, with no objection reset, through step s + 4. The action is taken then.
  - **No winner by step 30.** If no candidate leads "unknown" by the commit margin at step 30, the verdict is "unknown", and that counts as settled (PLACEHOLDER-10, X29). Otherwise the decision is "unsettled": the action is skip, and it never counts as naming H.
  - **Cap.** The cap is 34 steps: a win by step 30, as in X29, plus the hold. This replaces M02's 16 steps per tick over up to 2 ticks.
- **TW2's memory rule** (KT-11).
  - After a right guess, the kind stretches, as in M14 and PLACEHOLDER-06.
  - After a wrong guess, a new candidate is made from the item, with weights copied from the guessed kind. Every trait, in any layer, that lies more than one detector width outside the guessed kind's range gains +0.2 weight (PLACEHOLDER-02).
  - There is no layer order and no "less reliable" mark.
  - TW2 and TW7 live in the twins package behind the same interface (M16, M43). They import K-F's code and are fingerprinted with it, and K-F's code never imports them (FORBIDDEN 26).
- **Code rules.** The mind's inner loops are written as plain loops in Numba. NumPy linear algebra isn't used inside compiled code, and SciPy is never a mind dependency (I02). No fastmath (I05). A pure-NumPy reference version of the neuron step is kept for tests.

## 7. Tuning, the brute baseline first, and the freeze

**What may be tuned on the tuning set** (a closed list, KT-13):

- the spiking constants: leak, threshold, refractory period and inhibition strength (the 10 substeps and the 10 ms smoothing time constant are fixed by KT-09, section 6);
- one detector width, in noise widths, shared by every trait;
- the commit margin, the objection threshold and the new-kind threshold;
- the per-spike cost.

Limits on that tuning:

- Every relevance weight starts equal at 0.5, and this is checked automatically (M20). After that, weights change only by PLACEHOLDER-02's fixed steps.
- No constant may differ by trait or by layer, and this is also checked automatically.
- TW7 may tune only its own rate-unit gain and time constant, with the same number of tuning sweeps as K-F. TW2, OS01, OS10 and K-F-NOWARM reuse K-F's values.
- Each tuned value gets its own register row, marked "set on KT tuning set": KT-19 to KT-27 for the closed list, in its order, then KT-28 and KT-29 for TW7's rate-unit gain and time constant.
- No kill-test-tuned value enters Frankie's M17 settings, which evolve from random genomes (FORBIDDEN 20), and PC1 keeps PLACEHOLDER-88's values. A tuned value outside M17, such as the refractory period or the per-spike cost, may be reused only as a designed prior printed on the priors card.

**Before any K-F code exists:**

1. Every bot and B1n-mind is built, run on the tuning set, frozen and fingerprinted. Every radius is chosen and registered.
2. Rule 6 holds on the tuning set.
3. **Positive control.** B2e passes rules 4, 4b and 4c, and rule 5's Q bar (rule 6), on the tuning set. If it can't, the bench is redesigned on the tuning set.
4. **Power check** (test fixture MK10, specified under PLACEHOLDER-90, KT-15). A mock mind is run through the frozen analysis script, so every GO rule and every subgroup rule is applied.
   - **Families.** Each simulated set is drawn from the tuning key's practice families (numbers 1,001 and up, section 3). Family i takes the core-trait placement of tuning family ((i − 1) mod 30) + 1. 1,000 sets are simulated at each size, with the seed frozen in the analysis script. Rule 6 is not applied to simulated sets.
   - **Planned values for each family:**
     - D_learn is the larger of 0.35 and the set's floor + 0.20, with D at check 1 = 0;
     - CopyAccept 0.90;
     - LookReject 0.70 in each half;
     - FarMinusNeutral 0.25;
     - D_strict on Q after SOUR 0.35, and a sour drop of 0.05;
     - settle rate 0.97;
     - 70% of runs notice the taste, and OS10 never does;
     - equal effects in every subgroup.
   - **Floor.** Each simulated set's floor is the higher of B1n-bot-r's and B1n-mind's mean D_learn on that set's own families, so the planned D_learn is set per set.
   - **Spread between families.** D_learn, D at check 1, FarMinusNeutral, each LookReject half, D_strict on Q after SOUR and the sour drop each vary by the larger of B1n-bot-r's and B2e's between-family standard deviations for the matching quantity on the tuning set (the D_beh version for D and for Q), and by at least 0.10. CopyAccept, the settle rate and the noticed share vary by 0.10.
   - **Spread between runs.** D_learn, D at check 1, FarMinusNeutral, each LookReject half and D_strict on Q vary by B1n-bot-r's within-family standard deviation. The sour drop doesn't vary between runs. Each run's settle rate is a binomial share of its 210 decisions at the family's rate, its CopyAccept a binomial share of its 10 copy checks at the family's rate, and noticing a yes/no draw at the family's rate.
   - **How values are drawn.** Every draw has the planned value (between runs, the family's value) as its mean. A share is drawn from a beta distribution, so it stays inside 0 to 1, with its standard deviation cut to 0.9 × √(m(1 − m)) wherever a beta of mean m can't reach the stated one. A difference is drawn from a normal distribution and kept as drawn, even outside −1 to 1, and the analysis script accepts it. Nothing is clipped. OS10's noticed share is exactly 0.
   - **Subgroups.** Each mock run falls in the "h1 made a new candidate" subgroup with probability 0.5, independently.
   - **Pass mark.** The mock must reach GO in at least 80% of simulated sets. The set size starts at 40 families and rises in steps of 20 until it does (X39: N only goes up). If 120 isn't enough, the bench is redesigned on the tuning set.
5. **The charter's automatic mind checks** are built and pass on a stub mind:
   - the import guard;
   - the word and file scans of FORBIDDEN 1, 2, 4, 6, 7, 10, 11, 12, 21 and 22;
   - the interface test that no object id, role, nature, kind id or core label reaches the mind, the leak test that swapped natures give identical observations until the first eat, and the code check for references to essence, core or free labels in mind code (all FORBIDDEN 18);
   - the observation test that taste values reach the mind only after an eat (FORBIDDEN 29);
   - the test that memory is empty at birth (FORBIDDEN 20);
   - the configuration test that the chooser is satisficing, and the test that every M47 fallback has cleared_bar = false for every option considered (FORBIDDEN 13);
   - the intercepted-outcome counter check (FORBIDDEN 9, X43(e));
   - the no-unlisted-constants test (FORBIDDEN 28, I06);
   - a test that every mind constant has one value, shared by every trait and every layer;
   - a test that a taste-blind stub is classed as not noticing in 100% of runs.

   They run again at every freeze.

**The freeze.** It happens before the set's key exists.

- One K-F configuration (code plus constants) gets a single fingerprint. OS01, OS10 and K-F-NOWARM are switch settings of K-F's code, and TW2 and TW7 live in the twins package (section 6).
- Every file's SHA-256 goes into a manifest in `freeze/`, for the next unused set only, named for that set (section 3).
- The code is tagged `charter-killtest-code-v1`, pushed and timestamped (I04). A bench-code re-freeze after rule 6 gets `-v1.1`, `-v1.2` and so on (section 3), and a re-freeze after INCONCLUSIVE gets `-v2`.

## 8. What gets measured

Everything is measured on check copies. Every mean is the mean of the family means.

- **The H set** (KT-12). It starts as h1's candidate. When a memory write creates a candidate:
  - one created at a2, a3 or a4 joins the H set;
  - one created at t2, t4, t6, t8, h2 or SWEET-CONTROL never joins;
  - any other new candidate joins if its parent is in the set;
  - a merged candidate joins if either input is in it.

  **Naming H** means that the last committed verdict before an eat names a member of the H set. This widens X46's strict reading [Aitzaz Q1, 24 Oct] for the bench only; C1 and C2 keep X46 unchanged. The h1-lineage-only version is reported.
- **D_strict** (tower minds): the share of far apples eaten while naming H, minus the share of look-alikes eaten with any verdict.
- **D_beh** (bots, and every mind for comparison): the same, from eating alone.
- **D_learn:** the mean of D at checks 2, 4, 6 and 8. It measures how sharply the mind tells apples from look-alikes, averaged over its learning, so faster learning scores higher. This is the judged number. D at every check is reported, so the learning curve is visible.
- **D at check 1** is the leak check (rule 7).
- **FarMinusNeutral:** the far-apple strict eat rate minus the share of neutrals eaten with any verdict, averaged over checks 2, 4, 6 and 8. For bots, the far-apple eat rate replaces the strict rate.
- **LookReject:** at check 8, 1 minus the look-alike eat rate, computed separately for the h1 half and the far half.
- **CopyAccept:** the eat rate of exact copies of h1, averaged over checks 1 to 8.
- **Settle rate:** the share of all K-F decisions in the run that settle (section 6). That covers warm-up, teaching, h2, SWEET-CONTROL and every check, but not the verdicts after eating.
- **On Q,** D_strict uses all 8 of Q's apples in place of far apples, as C2 does.
- **Sour drop:** D_strict on Q after SWEET-CONTROL minus D_strict on Q after SOUR, paired probe by probe.
- **TASTE-NOTICED** (from C2, made exact for the bench). A run noticed the sour taste if either of these holds:
  - the candidate chosen for SWEET-CONTROL (section 5) has strictly lower taste evidence in SOUR than in SWEET-CONTROL. Taste evidence is PLACEHOLDER-01's count over the 4 taste traits alone: each taste trait inside that candidate's stored range, widened by the detector width, adds its relevance weight. It uses the candidate's ranges and weights as they stand in the verdict after eating (section 6), and it is computed whether or not an outer layer eliminated the candidate. The scoring changes nothing in the mind. For a mind that stores no taste ranges (OS10, B1n-mind and every bot), this part never holds;
  - a memory write other than a stretch (a split, a mark-unreliable or a new kind) follows h2 in SOUR, and no such write follows the SWEET-CONTROL apple.

  Because the two branches share their keys, a taste-blind mind can never be classed as noticing. SWEET-CONTROL's tastes sit at the centres of that candidate's stored taste ranges, so the first part holds whenever, in SOUR, a taste trait with weight above 0 falls outside that candidate's range for it, widened by the detector width.

## 9. Pass and fail, fixed now

**GO**, meaning continue to the trimmed version 1, needs **all** of these on a kill-run set:

1. **Settle rate.** At least 95% of K-F decisions settle (section 6). This is deliberately below X29's 99%, which still applies at Stage 5.
2. **Applicability.** K-F's CopyAccept is at least 0.80. Otherwise the result is "h1 wasn't learned".
3. **Edge over brute trial and error.**
   - The floor is whichever of B1n-bot-r and B1n-mind has the higher mean D_learn (D_beh) on that set. It is known before any tower runs.
   - K-F's mean D_learn (D_strict) must be at least 0.15 above the floor.
   - The paired family-cluster bootstrap (X31) for K-F minus the floor mind must have its 2.5th percentile above 0. This is a one-sided 0.025 level for the bench only, outside every X32 family. Runs are paired by run key within each family. The family differences are resampled 10,000 times, with the seed frozen in the analysis script.
4. **Real discrimination.** K-F's mean D_learn (D_strict) is at least 0.25.
   - **4b. Apples beat strangers.** K-F's mean FarMinusNeutral is at least 0.15.
   - **4c. Look-alikes refused.** K-F's mean LookReject is at least 0.60 in the h1 half and, separately, at least 0.60 in the far half. Each core trait is moved in exactly 2 of the 4 look-alikes in each half. So G07, which uses one trait, sits near 0.50 in each half. G05 and G17, which refuse near-copies of a good item, fail the far half. G18 adds that refusal to G16's inner-layer matcher and can clear both halves. Rule 5's Q bar stops it, because Q's apples are near-copies of h1 and h2.
5. **Sour apple.** K-F's mean sour drop is at most 0.15, and its mean D_strict on Q after SOUR is at least 0.25.
   - Applicability: at least 50% of runs noticed the taste, and OS10 is classed as not noticing in at least 90% of its runs.
   - If either applicability check fails, rule 5 is "uninformative" and the result is INCONCLUSIVE.
6. **The bench is valid.** This is judged before any tower mind runs on the set.
   - B1t, B2, G01, G04, G05, G06, G07, G09, G16, G17 and G18 are each scored with D_beh, and each must fail at least one of rules 3, 4, 4b and 4c and rule 5's Q bar.
   - For a bot, passing rule 3 means beating the floor by 0.15 with the bootstrap's 5th percentile above 0. That is one-sided 0.05, X32's level for validity checks.
   - For a bot, rule 5's Q bar means D_beh on Q after h2 of at least 0.25. Bots don't taste, so SOUR and SWEET-CONTROL are the same for them.
   - For a bot, including B2e in the positive control (section 7), rules 4, 4b and 4c count as passed only if they also hold in every core-placement subgroup with at least 100 runs, as for K-F. The candidate subgroup doesn't apply to bots.
   - If any of them passes all five, the set is retired (section 3).
7. **No head start.** K-F's mean D_strict at check 1, after one taste, is below 0.15. A higher value means an essence hint has leaked in. The result is then INCONCLUSIVE, and the leak is traced with Aitzaz:
   - **If it lies in K-F,** its fix is the one design change.
   - **If it lies in the bench code** (a departure from this addendum), the code is fixed to match this addendum on the tuning set. Every bot, rule 6, the positive control and the power check are re-run and re-frozen before the next set's key exists, at the set size already fixed. If rule 6 fails on the tuning set, the positive control fails, or the power check doesn't reach 80% at that size, section 1 applies and a new addendum is needed. This doesn't use up the one design change.
   - **If it lies in a rule or number of this addendum,** section 1 applies and a new addendum is needed.
   - In no case does a threshold or GO rule change.

**Subgroups.** Results are also reported by where H's core traits sit (any in the object layer, or none), and by whether h1 made a new candidate or stretched an old one. Rules 4, 4b and 4c must also hold in every subgroup with at least 100 runs.

**Verdict order on each set:**

1. Rule 6 fails: the set is retired, with no verdict, since K-F never ran on it.
2. Rule 1 or 2 fails: **NO-GO**.
3. Rule 3's bootstrap isn't above 0: **NO-GO**. The tower is not better than brute trial and error.
4. Every rule passes: **GO**.
5. Anything else is **INCONCLUSIVE**: K-F beats brute force but misses rule 3's margin, or rule 4, 4b, 4c, 5 or 7.

**After INCONCLUSIVE.** Aitzaz approves **one** design change, written as a list of ledger and register edits that Aitzaz initials as one item.

- It is made and checked on the tuning set only.
- Nothing else changes at the same time: not the bench, the bots or these rules, except a bench-code leak fix under rule 7.
- It may not adopt a twin, an off-switch version or rate neurons. This is stricter than FORBIDDEN 26 and 27. A fallback that Aitzaz approves under M44 is open only after NO-GO, through a new addendum.
- The code is frozen again and the next kill-run set is used. That second evaluation is final.

**After NO-GO.** We stop and rethink the design with Aitzaz, and nothing conventional gets bolted on to rescue it. Any later kill test needs a new addendum, frozen before the code changes.

## 10. Reported, not judged

- **TW7 vs K-F** (spiking vs ordinary neurons). If TW7 beats K-F on settle rate or D_learn, that goes to Aitzaz under D12. Nothing switches automatically.
- **TW2 vs K-F** (blame-outward vs textbook memory). Every teaching look-alike copies its apple's look and taste. Until a mind has learned the poison kind, each one is eaten after a confident wrong guess, so blame has to travel to the core traits in every run.
- OS01 (cap and free) vs K-F: does outside-in order help?
- K-F-NOWARM vs K-F, and B1n-mind vs B1n-bot-r.
- K-F against each bot, including G08 (the simple rule-finder), and B2e's ceiling.
- D on the far half alone, next to D.
- Poison bites, decision times, forced-taste counts and redraw counts.
- h2's own verdict (H set, other or unknown), and the share of eats after h2 that name a candidate created at h2.

## 11. Schedule and compute

About **6 weeks part-time**, roughly 90 hours at 15 hours a week:

| Week | Work |
|---|---|
| 0 | Close this addendum and get Aitzaz's OK. Commit the tuning key. Write the one-page design notes (I09) for the generator, the drive, the tower, and the memory and write rule, so approvals run in parallel with Week 1. |
| 1 | Repo skeleton with the import guard. Keyed random streams. Trait schema, kind and role generator, certificate checker, property tests. |
| 2 | The cafeteria harness: energy, forced tastes, snapshots and check copies. Scoring, every bot, B1n-mind and the analysis script. A test that check order can't change any check's result. The automatic mind checks on a stub. Then bench validity, the positive control and the power check on the tuning set, and the bots are frozen. |
| 3 | Tower logic and memory rules, built first with rate neurons (this is TW7), plus the drive. Hand-made unit cases. |
| 4 | Spiking neurons, stability logging, and tuning of the closed list on the tuning set. |
| 5 | TW2, OS01, OS10 and K-F-NOWARM. A full dry run on the tuning set. Then freeze, tag and timestamp. |
| 6 | Buffer first (almost always spiking stability). Then wait for set A's block, a few hours after the freeze. Run the kill run once, run the frozen analysis, and write the report. |

- **Compute** is not a constraint. A run is 210 decisions. The seven tower configurations (K-F, TW7, TW2, OS01 cap, OS01 free, OS10 and K-F-NOWARM) at 400 runs each take well under an hour on a laptop in the realistic case, and a few hours in the worst case. It costs no money.
- **Risks.**
  - The biggest is spiking stability on near-ties, which can add 1 to 2 weeks.
  - Each repeat run adds at least a week, so 7 to 8 weeks with one repeat.
  - Design-note approvals also take calendar time.
- **Kept lean.** The bench keeps plain per-run files: the verdict trace, the key record, and the list of designed exposures and injections, which stands in for the priors card. The full log schema and the Parquet chain wait for Stage 1.

## 12. Trimmed version 1 (if GO)

- **In v1:** C1, C2-SOUR, C3, C7 and C8, tested in the frozen X32 primary family.
  - That family stays at m = 7. C9 and C12 remain committed members and enter the Holm correction with p = 1 until v2 reports. Holm-adjusted results can only improve when a member's p falls, so nothing that passes in v1 can be undone by v2.
  - The secondary family stays at X32's four: C4, C6, C2-MIRROR and C13-E1, with C13-E1 at p = 1 until v2.
  - C5, C2-MEMORY, C4(c), C8-S8 and every T0 check run as mechanism checks.
  - Power (X39) stays at 0.05/7 for the primary family and 0.0125 for the secondary.
- **Moved to v2:** the runs and reports for the teacher (C9, C10, C11), novel approaches (C12) and free will (C13-M, C13-E). Their charter text stays frozen as written.
- **What still happens in v1.** Moving a claim to v2 moves only its runs and its report. X01, X02, X40 and T17 still hold. So these are built and frozen in v1's Stage 4, before any Frankie mind code other than K-F:
  - the teacher script;
  - the X40 tokenizer;
  - the T17 closure library;
  - everything the Wave 1 freeze of T13's teacher-free group and T14 needs: their specs; every bot, twin, off-switch flag and fixture those specs name (for example B1n-seq, B4n, G11, TW4 and MK5); C12's X41 classifier check; MK5's E1-mode validity check; and the X39 power checks for C12 and C13-E1. All of this is done before any v1 vault opens (X01, X02, X39).
- **Order:**
  1. this kill test;
  2. the world and logging (charter Stages 1-3, trimmed);
  3. tests and bots for the v1 claims, plus the teacher script, tokenizer, closure library and everything the T13/T14 Wave 1 freeze needs (Stage 4, X02, X39);
  4. the Stage 5 and 6 gates (X29, M44);
  5. evolution of perception (Stage 7);
  6. the v1 battery.
- **Timing:** a first v1 result in about 5 months part-time, including the kill test. This gets re-estimated once the Stage 4 teacher work is sized. If it runs longer, the timing changes, not the order.

## 13. Placeholders, approvals and what changed

These are Claude's proposals, made to close gaps the reviewers found. Aitzaz approved version 2's list in bulk on 24 Oct ("approve all"), and KT-14 separately ("good idea"). Rows marked **changed in v3** or **new in v3** were altered by the checks after that approval, and they need Aitzaz's OK again before the freeze. Each row becomes a register row in the freeze commit. Aitzaz gave that OK on 25 Oct 2026, before the freeze.

| ID | What | Where | Status |
|---|---|---|---|
| KT-01 | The 22-trait schema; exact hue tied to coarse hue, with no range of its own; taste (sweet, sour, bitter, salty) counts as a detail trait | §2 | changed in v3 |
| KT-02 | Exactly 4 core traits from 13 eligible; free-range widths and placement; taste has the full range and is never core; 4 neutral kinds per family | §2 | changed in v3 |
| KT-03 | Apples redraw every free trait. Look-alikes copy their model's look **and taste**, keep h1's context and their model's hue offset, with a core shift of 20-30 noise widths. The far-apple distance rule applies only against look-alikes modelled on h1. The draw order, which object is redrawn, the exits when nothing passes, and taste limits and Q's apples drawn inside their limits. | §2, §5 | changed in v3 |
| KT-04 | 8 look-alike kinds (2 for teaching, 6 for checks) and the M1/M2/M3 halves | §2, §5 | changed in v3 |
| KT-05 | Exact bot rules, including B2e, B1n-mind, G06, G07 and G08 (G07 and G08 on teaching items only), G16, G17 and G18; "exact" means within 5 noise widths; OS01's thinking cap | §4 | changed in v3 |
| KT-06 | Warm-up: 40 forced tastes from 1 nourishing, 1 poison and 2 "nothing" kinds of 4 other families, each with its own context at least 40 noise widths from h1's | §2, §5 | changed in v3 |
| KT-07 | Teaching: 8 forced tastes, apple then look-alike, in the order given | §5 | Aitzaz, 24 Oct (bulk) |
| KT-08 | How the drive scores eat and skip: own records only, with the reliability factor, never below 0; "unknown" is a skip | §5 | changed in v3 |
| KT-09 | Spiking time base (10 substeps, 10 ms smoothing, no neuron noise, every decision starts from rest); these two constants are fixed, not tuned | §6 | changed in v3 |
| KT-10 | Settling rule ("unknown" can settle, cap 34) and a brand-new candidate's starting values (weights 0.5) | §6 | changed in v3 |
| KT-11 | TW2's memory rule; the twins live in their own package | §6 | changed in v3 (package only) |
| KT-12 | The H set: kinds made from the teaching apples count, and kinds made from look-alikes never do | §8 | changed in v3 |
| KT-13 | The closed list of what may be tuned; weights start at 0.5; tuned values never enter M17; tuned values get rows KT-19 to KT-29 | §7 | changed in v3 |
| KT-14 | Kill-run keys from Bitcoin block N + 6, where N is the lowest attestation in the upgraded proof the GitHub Action commits; one manifest per set, pushed only when that set is next | §3 | Aitzaz, 24 Oct ("good idea"); changed in v3 |
| KT-15 | Power check (MK10) with every GO value, how its values are drawn, and its families; LookReject 0.60 per half; leak check 0.15; set size in steps of 20 | §7, §9 | changed in v3 |
| KT-16 | Sour apple: shared keys for both branches; SWEET-CONTROL is h2 with the named kind's taste; the verdict after eating; TASTE-NOTICED made exact | §5, §6, §8 | new in v3 |
| KT-17 | Stage 5 and 6 register values inherited as written; check-order ties broken by a run-key order; "tick" means the decision on the bench | §6 | new in v3 |
| KT-18 | How a leak found by rule 7, or a set failing rule 6, gets traced and fixed; rule 6 also scores rule 5's Q bar and the subgroups | §3, §9 | new in v3 |

**Edits made in the freeze commit.** The freeze commit also makes these edits, in the charter files and their `data/` copies. The tag is not made without them.

1. REGISTER PLACEHOLDER-85 gains a kill-test entry. Forced eats are allowed only for the 40 warm-up tastes and the 8 teaching tastes, and for h2 and SWEET-CONTROL if skipped.
2. LEDGER W45 gains a kill-test energy-set, E = R + 10, at the points listed in section 5. FORBIDDEN 31's list of injections names it.
3. LEDGER X01, X40 and T17 each point to the exception in section 1.
4. KT-01 to KT-18 become register rows.
5. GLOSSARY gains K-F, K-F-NOWARM, B1n-bot-r, G16, G17, G18 and MK10. Its ID rule and FORBIDDEN 26's lists read G01-G18 and MK1-MK10.
6. LEDGER W52 gains a kill-test exception: the SOUR and SWEET-CONTROL copies share one replica key, and each Q probe uses one replica key in S8, SOUR and SWEET-CONTROL (KT-16).
7. REGISTER PLACEHOLDER-92 gains a note for the Stage 4 freeze. Charter C2's TASTE-NOTICED has the same holes that KT-16 closes here (its own replica key for each clone, a write clause on SOUR alone, and an undefined verdict after eating), and they must be closed before C2 is frozen.
8. LEDGER X34 and REGISTER PLACEHOLDER-90 add MK10, the kill-test power mock. Its spec is KT-15, approved with this addendum, and it lives in the test-fixtures package like MK1 to MK9. LEDGER X03's "the other three B1n variants are in X36" becomes "the other B1n variants are in X36, plus the kill test's B1n-bot-r".
9. GLOSSARY's agent_type values add K-F, K-F-NOWARM and B1n-bot-r, and read G01-G18 and MK1-MK10. Its designed-exposure policy gets edit 1's kill-test entry, and its motif-tokenizer entry gets edit 3's pointer.
10. CHARTER C12's TOKENS sentence, C13-E's T17 parenthesis, C7's two Stage 4 sentences and C8's Stage 4 sentence each gain "(K-F excepted, KILL_TEST.md section 1)".
11. FORBIDDEN 28's automatic check reads "each constant must cite its register row (PLACEHOLDER-nn or KT-nn) or ledger row".

Edits 3 and 5 to 11, and the wording of edits 1 and 2, are new in v3, so they need Aitzaz's OK again too. Each row they change keeps its 24 Oct approval for its original text and gains a separate approval for the kill-test addition.

The freeze commit also makes the README's pre-freeze tidy-ups, and Aitzaz's OK covers them too. PLACEHOLDER-107 and PLACEHOLDER-112 gain the TW3 and TW4 crediting margins exactly as C7 and C13-E state them. PLACEHOLDER-47 gains "Each taste number runs from 0 to 1, like every other trait (PLACEHOLDER-57)." FORBIDDEN 26 gains "The test-only flags OS18, OS19 and OS23 are applied by a wrapper on the test side of the mind's interface, never by code inside the mind package."
