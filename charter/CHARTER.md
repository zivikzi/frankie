# Claims charter

_FRANKIE Stage 0 · approved by Aitzaz · frozen as tag charter-v1 · 25 Oct 2026_


Each claim says what Frankie must do, how a log proves it, which cheating bots and look-alike minds must fail it, and the pass mark. Pass marks are fixed before Frankie's mind exists. 
**Evidence (primary)** claims carry the headline result. **Mechanism checks** only show a designed part works and never count as intelligence.


## At a glance

| Claim | Tag | Tests |
|---|---|---|
| C1 Essence both ways: one super-sweet apple | evidence (primary) | T1, T0 (audits, certificates, priors card) |
| C2 Taste surprise: the sour apple stays an apple | mixed | T2, T1 (shares snapshots), T0 |
| C3 Learning relative to priors | evidence (primary) | T3, T0 |
| C4 Outside-in context and inside-out objection | evidence (secondary) | T4, T0 |
| C5 Elimination signature: look-alike count versus decision time | mechanism check | T5, T0 |
| C6 Mutual exclusivity without language (the 'dax' analogue) | evidence (secondary) | T6, T0 |
| C7 Curiosity as insurance: trying path B, and exploring after the world changes | evidence (primary) | T7, T8, T0 (leak and contamination audit, priors card), Stage 4 bot calibration (including G14 and the G13 regrowth and T8(a) checks) and the X39 joint-power simulation on MK3 |
| C8 Patience, not persistence: noisy TV next to a slow seed | evidence (primary) | T9, T7 layout (C8-S3(b) probe on clones of the same Frankies), T0 (leak and contamination audit, T0(e) record-versus-counter code check, priors card), Stage 4 bot calibration (including G15) and the X39 joint-power simulation on MK4 |
| C13-M Free-will signature: character insists, randomness discovers (mechanism checks) | mechanism check | T14, T0 (replay and stream-independence invariants, priors card) |
| C13-E Luck-found ways of acting travel to new situations | evidence (secondary) | T14 (C13-E1 continuations), X40 tokenizer and T17 teacher closure library (C13-E1 reference), T0 (replay invariants, priors card), Stage 4 X39 power check on MK5's E1 mode |
| C9 Watching pays off, with no built-in copying | evidence (primary) | T10, T0 (contamination audit and priors card on every run) |
| C10 Trust follows reliability | mechanism check | T11, T0 |
| C11 Purpose versus motion: the useless wiggle | mechanism check | T12, T0 |
| C12 Novel approaches in three tiers: repeat, recombination, novel | evidence (primary) | T13, T15 (optional, Stage 10), T0 |

---

## C1 · Essence both ways: one super-sweet apple

**Tag:** evidence (primary)  
**Tests:** T1, T0 (audits, certificates, priors card)

> 'By tasting just one apple, you can name all its varieties correctly as apples without being trained to.' 'Its recognizing essence. You give it a super sweet apple in the beginning.'

**In plain words.** Frankie tastes one example of a kind it has never met: a super-sweet, small, red 'apple'. Afterwards it should eat members of that kind that look very different (green, large). It should also refuse look-alikes that copy the apple's surface but not what it really is, and it must do this before it has ever tasted a look-alike. It has to do both. A creature that eats everything fails. So does one that refuses everything new, and so does one that just avoids anything that looks like the first apple. Frankie must also do better than a Frankie that tasted something unrelated instead, so that 'any good first meal makes it bolder' cannot pass as recognition.

### Exact definition

DECISIONS: D2 (two-way essence), D1 (sealed one-use vaults), D4 (untried value: the reason group Z exists), D8 (evolved perception: the reason for the PC cohorts). COHORT: evolved Frankies (priors_cohort=evolved, teacher_history=teacher-free) after a solo life on lifetime food. The priors card (W54) must show teacher_ever_present=false and teacher_demonstrations_seen=0. GROUPS (shared definition 'T1 groups O, Z, Z0'; ledger X10): within each sealed family H, a pre-registered keyed lottery (X38) assigns each Frankie to condition O, Z or Z0. O (100) eats one super-sweet h1. Z (100) eats one never-seen nourishing kind U from an unrelated family, matched to h1 as follows: U's energy gain within plus or minus 1 unit of h1's, and each of U's 4 taste numbers (PLACEHOLDER-47) within plus or minus 0.05 of h1's, that is 5% of that taste number's full range (Claude placeholder, PLACEHOLDER-101), on the same host type and in the same scene, and far in surface distance from every probe. Z0 (50) gets no taste and is reported only. The headline comparison is O versus Z. HEADLINE FAMILIES put H's essence on a combination of traits that was never predictive in any ancestral world. For these families the 2 or more core traits that separate H from its look-alikes must lie outside the context layer (not scene, not host), because the harness fixes scene and host during probes. Reserved trait bands apply to core traits only (PLACEHOLDER-101). EXPOSURE: O meets h1 (super-sweet, red, small member of H) on host type X in scene Y; Z meets U the same way; Z0 meets nothing. If the item is not eaten by choice within the 200-tick choice window, the harness gives it as a designed exposure (PLACEHOLDER-85, T1 entry), logged with action_provenance=designed-exposure and a designed_exposure record (choice_window_outcome=forced). A designed exposure with no committed verdict, or with verdict 'unknown', follows the shared forced-eat rule (PLACEHOLDER-93): a new candidate is created as in PLACEHOLDER-09, with no blame step, logged as memory_write_events trigger=designed-exposure. Snapshot S is taken 20 ticks after the item's effect lands (for Z0, at the median O tick). STOMACH DELAY: d = 10 for all protocol eats (h1, U and every probe eat; PLACEHOLDER-102). Ordinary eats follow PLACEHOLDER-49: d = 3 in ancestral lives and in the first 2,000 ticks of the test life, then d = 10 from test-life tick 2,000. The frozen spec states both values and the switch tick; the applied value is logged in eat_events.stomach_delay_d. PROBES: from S, 20 single-probe clones (W52), each with its own replica_key for the proposal and sensor-noise streams, each facing exactly one probe: 8 far members (surface-far from h1, different colour and size; their taste plays no part, because taste is known only after eating); 8 look-alikes (every surface trait within 10% of that trait's full range of h1, different from H in 2 or more core traits by at least 10 noise widths, poison); 2 neutrals (a never-seen kind of nothing nature, different from H in 2 or more core traits, at the SAME surface distance from h1 as the far members within plus or minus 10%, so 'avoid things that look like h1' cannot separate far members from neutrals); 2 exact copies of h1. Surface distance is the registered definition (PLACEHOLDER-91): the mean absolute difference, in sharp-view noise widths, over the object-layer traits (coarse hue, size, roundness, lobes). Every probe sits 3 cells ahead on host X in scene Y, with no other edible object within 7 cells. Energy is set to R + 10 by a logged energy-set injection (W45), and the starting heading is random. trial_end_reason: committed-eat at the first eat of the probe, window-timeout after 300 ticks, or left-area when Frankie is more than 7 cells away. CODING (shared definition 'Recognised as the kind'): far-accept-strict = Frankie eats AND its last committed verdict_winner about that probe before the eat names h1's candidate or a descendant of it in candidate_lineage (stretch, merge or split child) [Aitzaz Q1, 24 Oct]. For look-alikes, 'this is some other thing' and 'unknown' both count as correct rejections and are reported separately [Aitzaz Q1, 24 Oct]. look-accept = ANY eat of a look-alike, whatever the verdict. eat_far, eat_look, eat_neutral and eat_copy are plain eat rates. The log records whether h1 created a new candidate or stretched an existing lifetime candidate; the two cases are reported separately. VALIDITY OF A TRIAL: a trial counts only if (i) its object certificate (T0) shows the far member farther from h1 in surface distance than every look-alike in that Frankie's set, and the neutrals within plus or minus 10% of the far members' surface distance; and (ii) the certificate shows no earlier exposure (by this Frankie, its ancestors or any teacher) within 10 noise widths on 2 or more core traits. Because each clone sees only one probe, every look-alike decision is made before any look-alike has been tasted. SECONDARY REPORTS: the proposal's sequence run (one clone sees all 20 probes in counterbalanced order), and the whole probe set repeated at energy R + 40. REGISTER ROWS BEFORE FREEZING: PLACEHOLDER-101 (200-tick window, 20-tick snapshot delay, 3 cells, 300 ticks, 7-cell clearance and exit, the 10% band, the U matching rule, reserved bands on core traits only), PLACEHOLDER-91 (surface distance), PLACEHOLDER-85 (designed exposures), PLACEHOLDER-93 (forced eat with no verdict), PLACEHOLDER-102 (stomach delay).

### What gets measured

Per Frankie: D_strict = far-accept-strict rate minus look-accept rate (O only, since only O has an h1 candidate). D_beh = eat_far minus eat_look (every group, every bot). LookReject = 1 minus look-accept. FarMinusNeutral = eat_far minus eat_neutral. CopyAccept = eat_copy. A group's value is the mean of its per-Frankie rates. Effect part (2), D_beh(O) minus D_beh(Z): one-sided permutation test stratified by family (O/Z labels shuffled within each family, 10,000 permutations). Effect part (4), FarMinusNeutral: one-sided Wilcoxon signed-rank on per-Frankie values. Any interval printed for an effect part is a family-cluster bootstrap interval (10,000 resamples, X31) taken at the Holm level at which C1 is finally tested under X32, never at a fixed 95%; intervals for floors and reported quantities are 95%. C1's single Holm p is the largest of the two one-sided p-values from (2) and (4). Also reported: the same numbers for rule-seen families, for Z0 and for the R + 40 run; probe eats broken down by action_provenance (habit | proposal | no-safe-option-fallback) and by gaze_provenance (including drive-sharp-look); struck_options on probe trials; and the chosen and forced (designed-exposure) subgroups separately.

### Pass mark

All of these, fixed in advance, on rule-never-seen families. (1) FLOOR: mean D_strict in O is at least 0.40 [Aitzaz Q1, 24 Oct]. (2) PRIMARY-EFFECT: mean D_beh(O) minus mean D_beh(Z) is at least 0.15 (floor on the estimate), tested by the one-sided family-stratified permutation test. (3) FLOOR: mean LookReject in O is at least 0.70. (4) PRIMARY-EFFECT: mean FarMinusNeutral in O is at least 0.20 (floor on the estimate), tested by a one-sided Wilcoxon signed-rank test; it no longer has a separate fixed 0.01. HOLM: This claim's Holm p is the largest one-sided p among its effect parts: (2) and (4). That single p enters the primary Holm family in ledger X32 (m = 7; strictest step 0.05/7, about 0.0071) [Aitzaz Q4, 24 Oct] and must be below the level C1 receives there; every bound printed for (2) or (4) is taken at that same level. (5) APPLICABILITY: CopyAccept in O is at least 0.80. If (5) fails, the result is 'h1 was not learned', reported as not applicable, not as a pass. (6) VALIDITY: every must-fail bot is run through the same O/Z procedure and must fail at least one of: D_beh(O) at least 0.40 (the bot version of (1), because bots have no verdict trace), (2), (3) or (4). The must-fail bots are B0, B1t, B1n-bot, B2, G01, G02, G03, G04, G05, G06 and G07. If any of them passes, the test is void and the vault design (never the threshold) goes back to Stage 4. B2e, B5, TW1, TW2, OS01 (cap and free), OS02, OS06, OS07 and the PC1, PC2 and PC3 cohorts are reported, not must-fail. (7) REPORTED: rule-seen families, as 'what evolution supplied'; Z0; the R + 40 repeat; the sequence run; the chosen and forced subgroups; the new-candidate and stretched-candidate cases; 'some other thing' and 'unknown' rejections separately. (8) GATE (crediting, outside every family): after a pass, if the 90% interval for the difference in mean D_beh between Frankie and TW1 lies inside plus or minus 0.10, the result is tagged 'indistinguishable from the conventional twin' and credited to the conventional mechanism. Every number here is a Claude or proposal number that goes into the register (PLACEHOLDER-101) for Aitzaz to initial.

### Sample size

Headline: 25 rule-never-seen families x 8 Frankies (4 O, 4 Z) = 100 O + 100 Z, plus 2 Z0 per family (50). Reported: 13 rule-seen families x 8 Frankies (about 52 O + 52 Z). 20 single-probe clones per Frankie (about 5,100 probe trials, plus the R + 40 repeat). Kinds per family: H, its look-alike kind, 2 neutral kinds and U, so about 190 kinds over 38 families, entered in PLACEHOLDER-63 under the W35 reuse rule (a kind may not be reused within a life, within a matched set, or between a lineage's ancestral pool and its tested lives; if the battery total passes 1,000 the budget is raised and N is never cut). Every bot, twin, off-switch version and the PC2 and PC3 cohorts get 100 runs on the headline families with the same family allocation. The PC1 cohort gets 100 group-O runs plus 100 group-Z runs on the headline families (Claude placeholder, PLACEHOLDER-101), so C2 has 100 PC1 group-O snapshots. POWER: N comes from the joint-power rule (X39). Before any vault opens, the between-family spread of D_beh is estimated on stand-in families with mocks at the planned effect sizes, and all required parts ((1) to (5)) must pass together at least 80% of the time, with (2) and (4) tested at the strictest Holm step (0.05/7), since C1's final Holm position is not known in advance. If power is short, the number of FAMILIES (not Frankies per family) is raised. N may only go up, never down, and is never changed after results are seen. The secondary sequence run uses the same snapshots.

### Controls

| ID | Control | Rules out |
|---|---|---|
| Z | Group Z: one taste of an unrelated nourishing kind U, matched on energy and taste, same host and scene, keyed lottery within family | 'Any good first meal makes Frankie bolder toward new things.' The designed untried-value rule (D4) values untried things at the average of past first encounters, so any good first taste shifts it. Also rules out 'one more item in memory' and what priors alone give. |
| Z0 | Group Z0: no taste (reported) | Nothing on its own. It shows what evolution and the tower give with no meal at all. |
| B2 | Surface matcher (PLACEHOLDER-91 distance) | Matching colour and size. It should accept look-alikes and reject far members (D_beh at or below 0). |
| G05 | Avoid-the-familiar-look bot | Passing by avoiding things that are close but not identical to h1. It fails FarMinusNeutral because the neutrals sit at the far members' surface distance. |
| G06 | Rarity-weighted matcher | The vault giving the answer away by putting essence on unusual trait values (test families get reserved bands). If it passes, the vault design is fixed in Stage 4; the threshold is never touched. |
| G07 | Best single-trait bot | A simple inherited or habitual one-trait rule standing in for essence. |
| B2e | Essence-trait matcher (reads the designer's core-trait list) | Nothing. It is not a must-fail bot. It proves the test can be solved from one example and sets a ceiling. |
| B1n-bot | Nearest-neighbour eat/skip bot (ledger X36) | Brute memory of the single eaten item: it takes exact copies and near-surface things, so it should fail D_beh and look-alike rejection. |
| B1t | Lookup-table bot | Exact-match memory with no generalising: it should fail far acceptance and D_beh. |
| B0 | Random bot | Random wandering: D_beh near 0 and look-alike rejection fails. |
| G01 | Always-eat bot | 'Eats anything when not hungry': look-alike rejection fails. |
| G02 | Eat-novel-first bot | Brute tasting of new things: look-alike rejection fails. |
| G03 | Never-eat-new bot | 'Refuses anything unfamiliar': passes rejection but fails far acceptance and D_beh. |
| G04 | Reject-all-unknown bot | Blanket refusal of anything memory does not recognise: fails far acceptance and D_beh. |
| C1-NEUTRAL | Never-seen neutral probes at the far members' surface distance (design control) | A general willingness to eat new things at R + 10, and a 'stay away from the first apple's look' rule. |
| TW1 | Exemplar twin (GCM style) with Frankie's own evolved weights and perception | 'A textbook similarity model does exactly this.' Compared on D_beh; if indistinguishable under the 90% equivalence rule in threshold (8), credited to the conventional mechanism. |
| TW2 | Stretch-or-split write-rule twin | The possibility that Aitzaz's blame-moves-outward rule (D3) adds nothing here. |
| PC2 | Shuffled-world cohort | An inherited 'look at parts, ignore colour' rule standing in for lifetime recognition of essence. |
| PC3 | Counter-world cohort | The same inherited shortcut, tested against worlds whose essence rules run against the test rule. |
| PC1 | Hand-set (neutral) perception cohort | Confusing what evolved priors give with what the tower and memory give. |
| OS01 | Flat tower (both settings logged: cap and free) | The outside-in tower being irrelevant (reported, not must-fail). |
| OS02 | No gating | Outer-layer gating being irrelevant (reported, not must-fail). |
| OS06 | Prototype memory | Frankie's memory format being irrelevant (reported, not must-fail). |
| OS07 | Habits off (reported), plus action_provenance of every probe eat | A habit grown from the h1 meal (the conventional law-of-effect system) doing the work instead of recognition. |
| B6 | Contamination canary | Undetected leakage of vault kinds: T0 must flag it 100% of the time. |
| B5 | Oracle | Nothing; it sets the ceiling. |
| C1-CONTEXT | Matched scene and host on every probe, with core differences kept off the context layer (design control) | The scene or host giving away which probes are members, and the harness quietly erasing a look-alike's core difference by moving it onto h1's host. |
| C1-NO-CREATURES | Copy bots not applicable (design control) | No other creature is present and the cohort never met one (teacher_ever_present=false on the priors card), so copying cannot explain anything here. |

### Part tags

| Part | Tag |
|---|---|
| C1 (1) D_strict at least 0.40 | FLOOR |
| C1 (2) D_beh(O) minus D_beh(Z), permutation test | PRIMARY-EFFECT |
| C1 (2) minimum difference 0.15 | FLOOR |
| C1 (3) LookReject at least 0.70 | FLOOR |
| C1 (4) FarMinusNeutral, Wilcoxon | PRIMARY-EFFECT |
| C1 (4) minimum FarMinusNeutral 0.20 | FLOOR |
| C1 (5) CopyAccept at least 0.80 | APPLICABILITY |
| C1 (6) must-fail bots | VALIDITY |
| C1 trial certificate checks (i) and (ii) | VALIDITY |
| C1 (7) rule-seen families, Z0, R + 40, sequence run, subgroups | REPORTED |
| C1 (8) crediting to TW1 | GATE |
| C1 off-switch versions and PC1-PC3 cohorts | REPORTED |

### Log fields needed

- agent_id, agent_type (frankie | B0 | B1t | B1n-bot | B2 | B2e | B5 | B6 | G01-G07 | TW1 | TW2), version (full | OS01 with cap | free | OS02 | OS06 | OS07), version_scope, priors_cohort (evolved | PC1 | PC2 | PC3), teacher_history
- matched_set_id / genome_id / temperament_seed / family_id / vault_id
- snapshot_id / parent_snapshot_id / clone_id, replica_key, stream_keys
- condition (O | Z | Z0)
- probe_role (far | lookalike | neutral | copy | U) and eat_events.hidden_nature: world side only, never in the mind packet
- designed_exposure {tick, test=T1, item_role (h1 | U), choice_window_outcome: chosen | forced}
- per tick: E / R / b / desperation_slope, energy_band, fed, action / movement_target, action_provenance (habit | proposal | no-safe-option-fallback | designed-exposure | baseline-rule), gaze_target / gaze_distance / gaze_layer_reached, gaze_provenance (habit | proposal | drive-sharp-look | no-safe-option-fallback | baseline-rule), options_considered, satisficing_bar, no_safe_option, struck_options
- at each commit: verdict_subject (world-side object id, log only), verdict_winner / verdict_margin / settle_steps / verdict_scope, elimination_events, objection_events
- memory_write_events (type, trigger: chosen-eat | designed-exposure, candidate_id_before, candidate_id_after, layer, per-feature weight deltas), including whether h1 produced type=new or type=stretch
- candidate_lineage {parent_id, child_id, event}, so h1's candidate can be followed from the h1 eat to each probe
- eat_events {object_id, kind_id, hidden_nature, energy_delta, effect_tick, stomach_delay_d, taste_vector, sick, net_gain, designed_exposure}
- injection_events (energy-set at R + 10 or R + 40, with vault provenance)
- habit_weight_updates; habit_similarity_score / habit_similar / habit_contribution
- trial_end_reason (committed-eat | window-timeout | left-area | death)
- replay_fingerprint_match
- rule_seen_in_ancestry (true | false, per family)
- record, not a log field: object certificate (T0) with surface distance to h1 under PLACEHOLDER-91, core-trait distance in noise widths, the layer each core difference sits in, nearest prior exposure and its channel
- record, not a log field: priors card (W54), with generations, ancestral families, essence rules seen, exposures per channel, designed exposures and injections, teacher_ever_present (must be false), teacher_demonstrations_seen (must be 0)

### If it fails

If (2) or (4) fails, or a floor in (1) or (3) fails, on rule-never-seen families, 'Frankie recognises essence from one example' is reported as not supported. If it passes only on rule-seen families, the result is 'evolution supplied the rule': a prior, not lifetime intelligence. If O does not beat Z, the effect is credited to 'any good first meal', not to the apple. If a must-fail bot passes, the test is void and the vault is redesigned; the threshold is not loosened. We will NOT: put essence labels or the designer's core-trait list into memory; hint which traits matter; add a novelty bonus or optimistic value so it eats far members; swap in TW2's write rule or a best-split tower; move rule-seen families into the headline; drop group Z because it makes the test harder; force eats beyond the PLACEHOLDER-85 list; or retune anything on this vault. Any redesign needs Aitzaz's approval, is flagged 'changed after seeing T1', and is rerun on a new one-use vault (D1).


---

## C2 · Taste surprise: the sour apple stays an apple

**Tag:** mixed  
**Tests:** T2, T1 (shares snapshots), T0

> 'You give it a super sweet apple in the beginning. Then a super sour one. Will it still correctly identify it?'

**In plain words.** Frankie has eaten one super-sweet apple. Now it eats a big, green, super-sour apple that still feeds it. If Frankie has grasped the kind, it keeps eating apples of every look, because the taste changed but the outcome did not. This only means something if Frankie actually noticed that the sour taste was a surprise. A creature that ignores taste altogether passes without trying, so that case is reported separately and does not count. In a second part (the mirror), a look-alike that tastes sweet like the first apple makes Frankie sick. Frankie should then avoid that look-alike despite the familiar taste, without starting to fear real apples.

### Exact definition

DECISIONS: D3 (write rule), D16 (taste and no nibble), D2 (two-way essence). TASTE IN RECOGNITION (shared definition; PLACEHOLDER-92, ledger M51): taste is stored in candidates like any detail trait and takes part in the verdict after eating; a guess counts as wrong only when the energy outcome does not match [Aitzaz Q2, 24 Oct]. If Aitzaz rules that taste never takes part in recognition, SOUR passes by construction: it becomes a mechanism check, leaves the primary family before the Wave 1 freeze, and the family shrinks to m = 6 under X32 [Aitzaz Q2, 24 Oct]. SNAPSHOTS: the T1 group O snapshots S (rule-never-seen families for the headline; rule-seen reported), the T1 PC1 group-O snapshots (100), and, for H2-ONLY, the T1 group Z snapshots (parent_snapshot_id points to the T1 snapshot). PROBE SET P, built once per Frankie: 8 fresh far members (4 that look like h1, 4 that look like h2) and 8 fresh look-alikes (4 near h1's look, 4 near h2's look), all never met (object certificate, T0). Surface distance is PLACEHOLDER-91. CONDITIONS, each on fresh single-probe clones (W52) with their own replica_key: PRE runs every probe in P from S, with T1's placement, energy (R + 10 by a logged energy-set injection) and trial-end rules. SOUR gives h2, a far member (green, large, nourishing) whose taste is in the bottom 10% of the sweetness range and at least 10 noise widths from h1's taste. SWEET-CONTROL gives the same look as h2 with a taste inside h1's range. MIRROR gives L*, an instance of H's look-alike kind (poison) with a taste inside h1's range, drawn from the look nearest h1. MIRROR-CONTROL gives the same look as L* with a sour taste. H2-ONLY (reported) gives h2 to clones from T1 group Z; these clones come from group Z and have already eaten U. EXPOSURE: the item is placed 1 cell ahead with Frankie facing it, and Frankie has a 30-tick window to eat it by choice; otherwise it is given as a designed exposure (PLACEHOLDER-85, T2 entry: h2, the SWEET-CONTROL apple and the MIRROR and MIRROR-CONTROL look-alikes), logged with action_provenance=designed-exposure and a designed_exposure record. A designed exposure with no committed verdict, or with verdict 'unknown', follows PLACEHOLDER-93 (new candidate as in PLACEHOLDER-09, no blame step, trigger=designed-exposure). STOMACH DELAY: d = 10 for all protocol eats (h2, the sweet-control apple, L*, the MIRROR-CONTROL item and every probe eat; PLACEHOLDER-102). Any ordinary eat in these clones follows PLACEHOLDER-49 (d = 3 in the first 2,000 ticks of the test life, then 10), stated with its switch tick in the frozen spec. POST: snapshot S' is taken 20 ticks after the effect lands, and every probe in P is run again as a single-probe clone from S'. Pre and post are paired probe by probe. ACCEPTANCE (shared definition 'Recognised as the kind'): for members, behavioural acceptance = eat AND verdict_winner names h1's candidate or any descendant of it in candidate_lineage, including a split child [Aitzaz Q1, 24 Oct]. 'Joined the same kind' (h1's own candidate after a stretch or merge) is the MEMORY mechanism check. For look-alikes, any eat counts as acceptance; 'some other thing' and 'unknown' both count as correct rejections, reported separately. TASTE-NOTICED: a Frankie noticed the sour taste if, after eating h2, its post-eat verdict_margin for h1's candidate is lower in SOUR than in SWEET-CONTROL, or a non-stretch memory_write_event (split, mark-unreliable or new) follows in SOUR. MIRROR ROOM: a Frankie enters the Delta_look analysis only if its PRE acceptance of the 4 look-alikes near h1's look is at least 0.25, so there is room to drop. MEMORY (mechanism check, outside the evidence tally): in SOUR, the write event at h2's effect tick is a stretch of h1's candidate, and that candidate's taste weight falls. In MIRROR, a split or mark-unreliable event appears, and its layer is logged. REGISTER ROWS: PLACEHOLDER-92 (taste), PLACEHOLDER-93 (forced eat with no verdict), PLACEHOLDER-85, PLACEHOLDER-102 (30-tick window, 0.25 room cut-off, d = 10 for protocol eats), PLACEHOLDER-91.

### What gets measured

Per Frankie and condition: Delta_far = A_far_post minus A_far_pre and Delta_look = A_look_post minus A_look_pre, overall and separately for the h1-look and h2-look halves; the SOUR minus SWEET-CONTROL difference in Delta_far; D_strict after SOUR; the share of Frankies that noticed the taste. MIRROR (room Frankies only): A_look_post, Delta_look, Delta_far, and A_look_post(MIRROR) minus A_look_post(MIRROR-CONTROL). MEMORY: the share of Frankies with a stretch into h1's candidate at h2, the share with a falling taste weight, and the MIRROR split layers. The unit is the Frankie. Bounds come from a family-cluster bootstrap with 10,000 resamples (X31); paired tests are Wilcoxon signed-rank. C2-SOUR effect parts are one-sided non-inferiority tests against their margins, and every bound printed for them is taken at C2-SOUR's Holm level under X32, never at a fixed 95%. C2-SOUR's single Holm p is the largest of its three non-inferiority p-values. C2-MIRROR's single p is the larger of its two effect-part p-values and is tested in the secondary family (X32). Results are computed on Frankies that noticed the taste and also reported for all Frankies.

### Pass mark

C2-SOUR (computed on Frankies that noticed the taste; also reported for all). (1) PRIMARY-EFFECT: one-sided non-inferiority test that mean Delta_far is above -0.10, with its lower bound taken at C2-SOUR's Holm level. FLOOR: the mean Delta_far of each half (h1-look and h2-look) is above -0.10. (2) PRIMARY-EFFECT: one-sided non-inferiority test that Delta_far(SOUR) minus Delta_far(SWEET-CONTROL) is above -0.10, bound at the Holm level. (3) PRIMARY-EFFECT: one-sided non-inferiority test that mean Delta_look after SOUR is below +0.10, upper bound at the Holm level. HOLM: This claim's Holm p (C2-SOUR) is the largest one-sided p among its effect parts: the non-inferiority p-values for (1), (2) and (3). It enters the primary Holm family in ledger X32 (m = 7; strictest step 0.05/7, about 0.0071) [Aitzaz Q4, 24 Oct] and must be below the level C2-SOUR receives there. If taste never takes part in recognition, C2-SOUR leaves the family before the Wave 1 freeze and m = 6 [Aitzaz Q2, 24 Oct]. (4) FLOOR: D_strict after SOUR is at least 0.40 [Aitzaz Q1, 24 Oct]. (5) APPLICABILITY: at least 50% of Frankies noticed the taste; otherwise SOUR is reported as 'uninformative: taste never surprised Frankie', a mechanism result, not a pass. (6) REPORTED (lifetime tag): if evolved Frankies pass but PC1 Frankies fail, the result is tagged 'evolution supplied taste-indifference'. (7) VALIDITY: G01, G03, G04, B1n-bot and B2 must each fail at least one of (1) to (4), scored with eat-only acceptance and D_beh since they have no verdicts; otherwise the test is void. OS10 must be classed 'not noticed' in at least 90% of runs, or the taste-noticed measure is void. GATE (crediting, outside every family): if the 90% interval for Frankie minus TW2 in mean Delta_far(SOUR) lies inside plus or minus 0.10, the result is credited to the conventional write rule. C2-MIRROR (SECONDARY-EFFECT). APPLICABILITY: at least 30 room Frankies, otherwise 'not testable'. Effect parts: Delta_look below 0 (one-sided Wilcoxon), and Delta_far non-inferiority at -0.15 [Aitzaz Q5, 24 Oct]. C2-MIRROR's single p is the larger of the two and is tested in the secondary Holm family of X32 (4 members, familywise 0.05; levels 0.0125, 0.0167, 0.025, 0.05); the old 'p < 0.01' is removed. FLOORS: A_look_post is at most 0.30, and A_look_post(MIRROR) minus A_look_post(MIRROR-CONTROL) is at most +0.10. C2-MEMORY (MECHANISM, one-sided 0.05 where a test is needed, never counted as evidence): a stretch into h1's candidate in at least 70% of SOUR Frankies, and a falling taste weight in at least 70%. Secondary and mechanism results go in separate tables. Every number is a Claude or proposal number that goes into the register (PLACEHOLDER-102) for Aitzaz to initial.

### Sample size

The 100 headline group O Frankies from T1 (the same snapshots): 1 PRE set plus 4 conditions, each of 16 single-probe clones = 80 clones per Frankie (8,000 trials). Also 100 H2-ONLY clones from T1 group Z, and the T1 PC1 group-O Frankies (100, from C1's 100 PC1 group-O runs) on the same protocol. Every off-switch version, twin and bot gets 100 runs on the same families. Kinds: 0 new (PLACEHOLDER-63); only fresh instances of T1's families, under the W35 reuse rule. Rule-seen families are reported separately. N comes from the joint-power rule (X39): mocks at the planned effect sizes must pass C2-SOUR's required parts together at least 80% of the time at the strictest Holm step (0.05/7), and C2-MIRROR's at the strictest secondary step (0.0125). N may only go up and is never changed after results are seen; since C2 reuses T1 snapshots, any increase is made in T1.

### Controls

| ID | Control | Rules out |
|---|---|---|
| SWEET-CONTROL | A second apple with h2's look and a familiar taste (condition) | Any second good meal raising acceptance and hiding a penalty from the sour taste. |
| OS10 | Taste-blind | 'Passes only because taste is ignored.' It also checks the taste-noticed measure: OS10 must be classed 'not noticed' in at least 90% of runs, or that measure is void. |
| PC1 | Hand-set (neutral) perception cohort, same protocol | 'Evolution learned that taste never matters' (taste is a free trait in every ancestral kind), standing in for lifetime understanding. |
| PRE | PRE measured from S on the same probe specifications (condition) | A before-and-after comparison on different kinds of probe (T1 had no h1-looking far members). |
| MIRROR-CONTROL | Sour, poisonous look-alike (condition) | The mirror result having nothing to do with familiar taste, or familiar taste protecting a poison look-alike. |
| C2-ROOM | Room rule for MIRROR (design control) | A floor effect: a Frankie that already refused look-alikes cannot show a further drop, so it would pass or fail for no reason. |
| B1n-bot | Nearest-neighbour eat/skip bot (splits on any difference; X36) | Plain nearest-neighbour memory, which files h2 as a separate item and starts accepting h2-looking look-alikes. |
| OS08 | Write rule frozen (memory frozen after h1, habits on) | Acceptance staying level for reasons unrelated to memory (energy, placement, habit). |
| OS09 | Always-split | Doubt over whether the stretch half of the rule is what keeps acceptance level. |
| TW2 | Stretch-or-split write-rule twin | 'A textbook rule does the same.' If indistinguishable under the 90% equivalence rule in the threshold, credited to the conventional mechanism. |
| H2-ONLY | Clones from T1 group Z, which have already eaten U, given h2 only (condition, reported) | 'h2 alone teaches the kind and h1 did nothing.' |
| G01 | Always-eat bot | 'Just eats everything': it keeps Delta near 0 but fails D_beh after SOUR. |
| G03 | Never-eat-new bot | Blanket caution toward unfamiliar kinds: it fails D_beh after SOUR. |
| G04 | Reject-all-unknown bot | Blanket refusal of anything unrecognised: it fails D_beh after SOUR. |
| B2 | Surface matcher, with h2-looking look-alikes in the probe set | Generalising by look alone after h2: it starts accepting look-alikes that look like h2, which fails the Delta_look margin. |

### Part tags

| Part | Tag |
|---|---|
| C2-SOUR (1) mean Delta_far non-inferiority at -0.10 | PRIMARY-EFFECT |
| C2-SOUR (2) SOUR minus SWEET-CONTROL non-inferiority at -0.10 | PRIMARY-EFFECT |
| C2-SOUR (3) Delta_look below +0.10 | PRIMARY-EFFECT |
| C2-SOUR per-half mean Delta_far above -0.10 | FLOOR |
| C2-SOUR (4) D_strict at least 0.40 | FLOOR |
| C2-SOUR (5) at least 50% noticed the taste | APPLICABILITY |
| C2-SOUR (6) lifetime tag (PC1) | REPORTED |
| C2-SOUR (7) must-fail bots and OS10 taste-noticed check | VALIDITY |
| C2-SOUR crediting to TW2 | GATE |
| C2-MIRROR Delta_look below 0 and Delta_far non-inferiority at -0.15 | SECONDARY-EFFECT |
| C2-MIRROR A_look_post at most 0.30; MIRROR-CONTROL difference at most +0.10 | FLOOR |
| C2-MIRROR at least 30 room Frankies | APPLICABILITY |
| C2-MEMORY stretch and taste-weight checks | MECHANISM |
| C2 H2-ONLY and rule-seen families | REPORTED |

### Log fields needed

- agent_id, agent_type (frankie | B1n-bot | B2 | G01 | G03 | G04 | TW2), version (full | OS08 | OS09 | OS10), version_scope, priors_cohort (evolved | PC1), teacher_history
- matched_set_id / genome_id / temperament_seed / family_id / vault_id
- snapshot_id / parent_snapshot_id (the T1 snapshot) / clone_id, replica_key, stream_keys
- condition (PRE | SOUR | SWEET-CONTROL | MIRROR | MIRROR-CONTROL | H2-ONLY)
- probe_role (far | lookalike) and eat_events.hidden_nature: world side only
- designed_exposure {tick, test=T2, item_role (h2 | sweet-control | L* | mirror-control), choice_window_outcome: chosen | forced}
- eat_events {object_id, kind_id, hidden_nature, energy_delta, effect_tick, stomach_delay_d, taste_vector, sick, net_gain, designed_exposure}
- post-eat verdict at the h2 or control eat: verdict_winner / verdict_margin (for h1's candidate) / settle_steps / verdict_scope, objection_events
- memory_write_events (type, trigger, candidate_id_before, candidate_id_after, layer, per-feature weight deltas including the taste weight)
- candidate_lineage {parent_id, child_id, event: stretch | merge | split | forget}
- at each commit: verdict_subject, verdict_winner / verdict_margin / settle_steps / verdict_scope, elimination_events, objection_events
- per tick: E / R / b, energy_band, action / movement_target, action_provenance, gaze_target / gaze_distance / gaze_layer_reached, gaze_provenance, struck_options
- injection_events (energy-set at R + 10, with vault provenance)
- habit_weight_updates; habit_contribution
- trial_end_reason
- replay_fingerprint_match
- probe_pair_key (links each PRE probe to its post probe); rule_seen_in_ancestry (true | false)
- record, not a log field: probe set P specification and object certificates (T0), with surface distance to h1 and to h2
- record, not a log field: priors card (W54), including how predictive taste was in the ancestral worlds and the evolved taste relevance weight

### If it fails

If acceptance drops after the sour apple, Frankie treats taste as part of the kind, and the claim is not supported. If SOUR is uninformative because taste never surprised Frankie, that is reported as a mechanism result. If MIRROR fails, Frankie cannot put the blame on the look-alike; if it is not testable, that is said plainly. If the behaviour passes but C2-MEMORY fails, the behaviour is reported as evidence and the write rule as not working as designed. We will NOT: tell the mind that taste is non-essential; add a rule that ignores taste; add a taste-surprise signal just to make SOUR informative unless Aitzaz designs one; add a novelty or optimism bonus to keep it eating; swap in TW2's write rule by default; force eats beyond the PLACEHOLDER-85 list; or retune on this vault. Any change needs Aitzaz's approval, is flagged 'changed after seeing T2', and gets a new one-use vault (D1).


---

## C3 · Learning relative to priors

**Tag:** evidence (primary)  
**Tests:** T3, T0

> 'Today's AI fakes intelligence; the questions we ask it are worthless because it was trained on the mark schemes beforehand.' (The v1.1 proposal attributes to Aitzaz the principle 'learning is judged relative to the priors and experience Frankie was given'; it is listed in principles_kept without a P number.)

**In plain words.** Frankie gets credit only for what it learns in its own life, measured from wherever its inherited starting point left it. For each new family of things, we measure how good Frankie is before any experience. Then we measure how good it gets after each of its own risky eats. We compare how many eats it needs with a brute trial-and-error learner that is Frankie in every way except that it simply remembers each thing it ate. What evolution handed Frankie and what it learned are reported as two separate numbers, so neither takes credit for the other.

### Exact definition

DECISIONS: D8 (evolved perception), D3 (write rule), D11 (plan elimination; reasoned versus rote), D1 (sealed vaults). P2 (a less-optimal path is worth more) concerns routes and forbids gates that reward pure efficiency alone; this claim measures learning per own eat, not route efficiency, it carries a poison-bite floor so speed cannot be bought with risk, and the reasoned-versus-rote share is reported. Aitzaz confirms this reading at initialling. COHORT: evolved Frankies (priors_cohort=evolved, teacher_history=teacher-free; teacher_ever_present=false checked on the priors card). Each meets 6 sealed families, one at a time in counterbalanced order: 3 rule-never-seen (the headline) and 3 rule-seen (reported). Each family has a nourishing member kind and a poison look-alike kind. ARENA: 16x16, holding the family's members and look-alikes 50/50, replenished within 50 ticks by an instance of the same role (PLACEHOLDER-103, logged as injection_events type object-place with vault provenance), plus known lifetime food, so Frankie is never forced to eat unknowns. T3 may not force an eat (PLACEHOLDER-85): the designed_exposure record must be empty for every T3 session. A session ends at 5,000 ticks, at 40 eats of the family's objects, or at death (B06 holds), whichever comes first. e = the number of Frankie's own eats of this family's objects (eat_events, trigger chosen-eat). STOMACH DELAY: d = 10 for all protocol eats, which here are every probe eat at a checkpoint (PLACEHOLDER-102). Arena eats are ordinary and follow PLACEHOLDER-49 (d = 3 in the first 2,000 ticks of the test life, then 10); the frozen spec states the switch tick. CHECKPOINT PROBES: at e = 0 (before any exposure), after every eat up to e = 12, and then at e = 16, 20, 24, 28, 32, 36 and 40, the harness takes a snapshot and runs 16 single-probe clones (W52): 8 fresh members and 8 fresh look-alikes, never met, with T1's placement, R + 10 energy (energy-set injection), trial-end rules and separate replica_key values. acc(e) = balanced accuracy = the mean of the member eat rate and the look-alike no-eat rate (eat only, so bots are scored the same way). At e = 0 two independent 16-probe sets are run: set 1 decides exclusion, and set 2 gives the baseline S0 used in G, so chance noise in one set cannot both select a Frankie and inflate its gain. G(e) = (acc(e) minus S0) / (1 minus S0), the share of the remaining headroom closed. E50 = the first checkpoint at which G is at least 0.5 AND still at least 0.5 at the next checkpoint. E90 = the first checkpoint at which acc is at least 0.90 and stays there at the next one. Both are censored at e = 40, at the arena tick cap or at death. Pairs whose set-1 S0 is at or above 0.90 are counted as 'prior already sufficient', left out of the gain analysis, and counted in the report. COMPARATOR B1n-mind (ledger X36): Frankie's body, drive, reserve, untried-value rule, proposal menu, randomness curve and habit rule, with the recognition tower, candidate memory and write rule replaced by a nearest-neighbour memory of each eaten item; everything else (including the sharp-look rule) is unchanged, so the only difference is how eats are used. B1n-mind runs in the same arenas with the same checkpoints and the same Frankie-family pairings (matched_set_id). ARENA DECISIONS (a family object within 2 cells, ending in an eat or in moving more than 4 cells away) are logged as a secondary report, with gaze_layer_reached, action_provenance and gaze_provenance. Options the chooser ruled out by prediction are logged in struck_options with strike_class under the shared world-side rule: rote if this agent has at least one own eat of, or sickness from, any instance of the same world kind before the strike; reasoned only if that kind has zero own eats; no-kind for route moves, which never count as reasoned. A second report counts experience over every exposure channel. REGISTER ROWS: PLACEHOLDER-103 (replenishment rule, the 5,000-tick or 40-eat cap, checkpoint schedule, the 'stays above' rule, the 30% exclusion cap), PLACEHOLDER-38 as restated (world-side strike rule), PLACEHOLDER-102, PLACEHOLDER-49.

### What gets measured

Primary: the Kaplan-Meier median E50(B1n-mind) divided by the median E50(Frankie), on headline pairs. Test: a log-rank test stratified by family, one-sided, comparing Frankie and B1n-mind on the same Frankie-family pairings. This is C3's only effect part, so its p is C3's single Holm p under X32; any interval printed for the ratio is taken at C3's Holm level. Secondary measures (reported): E90; the number of poison bites before E50 (or until censoring) for Frankie and B1n-mind; the full G(e) curves; S0 and G side by side for evolved, PC1 and PC2 Frankies; the share of struck_options with strike_class=reasoned among family-object strikes; and the all-channel version. Comparisons at matched S0 pair Frankies whose S0 values are within 0.05 of each other.

### Pass mark

All of these, on rule-never-seen families. (1) PRIMARY-EFFECT: the stratified log-rank test, one-sided, Frankie versus B1n-mind on E50. HOLM: This claim's Holm p is the largest one-sided p among its effect parts: here the single log-rank p. It enters the primary Holm family in ledger X32 (m = 7; strictest step 0.05/7, about 0.0071) [Aitzaz Q4, 24 Oct] and must be below the level C3 receives there. FLOORS within (1): median E50(B1n-mind) / median E50(Frankie) is at least 2.0 [Aitzaz Q5, 24 Oct]; Frankie's own median E50 must be uncensored, otherwise (1) fails. (2) FLOOR: Frankie's median number of poison bites before E50 (or until censoring) is no higher than B1n-mind's, so faster learning per eat is not bought with more poison. (3) VALIDITY: in the nature-shuffled arena, mean probe accuracy is between 0.45 and 0.55 and its 95% interval includes 0.50; otherwise the test is void. (4) GATE (one-sided 0.05, uncorrected): if OS08's mean G at e = 20 is above 0.10, the habit system is contributing; the result is then tagged 'habits contribute' and is credited to the memory and write rule only if Frankie's median E50 is at least 2x better than OS08's AND a one-sided stratified log-rank test of Frankie versus OS08 passes at 0.05; otherwise the learning is credited to the conventional habit system. (5) APPLICABILITY: if more than 30% of headline pairs are 'prior already sufficient', the families were not new enough and no claim is made. (6) VALIDITY: G06 and the gamer bots G01 to G04 must not meet (1); the gamer bots must also show flat curves (G at e = 40 at most 0.10) and never reach E50; otherwise the test is void. (7) REPORTED: S0 (the prior) and G (the learning) side by side for every group, E90, the G(e) curves, the reasoned share of strikes, the all-channel version, OS07, and rule-seen families. (8) GATE (crediting, outside every family): if the 90% interval for the log ratio of median E50 between Frankie and TW1, or between Frankie and TW2, lies inside plus or minus log 1.25, the result is credited to that conventional mechanism. Every number is a Claude or proposal number that goes into the register (PLACEHOLDER-103) for Aitzaz to initial.

### Sample size

100 evolved teacher-free Frankies, 100 PC1 and 100 PC2, with 6 families each. At least 30 families per half (rule-never-seen and rule-seen), with at most 10 Frankies per family WITHIN each cohort. Cohorts share the same families, which also helps the S0 matching. Kinds: 60 families x 2 kinds = about 120 kinds, entered in PLACEHOLDER-63 under the W35 reuse rule (if the battery total passes 1,000 the budget is raised; N is never cut). Probes: up to 20 checkpoints x 16 clones, plus 16 for the second S0 set, about 340 probe trials per Frankie-family pairing. B1n-mind, B1t, TW1, TW2, OS07, OS08, G06 and G01 to G04 get 100 runs each on the same pairings. N comes from the joint-power rule (X39): mocks at the planned effect sizes, scored on E50, must pass all required parts of C3 together at least 80% of the time with (1) at the strictest Holm step (0.05/7). N may only go up and is never changed after results are seen.

### Controls

| ID | Control | Rules out |
|---|---|---|
| B1n-mind | Frankie with nearest-neighbour memory (X36) | Lifetime learning that is only remembering each eaten item: the honest 'bad elimination' bar, with every other difference removed. |
| B1t | Lookup-table bot | Nothing beyond setting the floor. |
| OS08 | Write rule frozen (habits still on) | The conventional habit system (law of effect) producing the learning curve instead of the memory and write rule. |
| OS07 | Habits off (reported) | Doubt over how much of the gain the habit system carries. |
| C3-SHUFFLED-ARENA | Nature-shuffled arena: natures reassigned per instance, also on the probes (design control) | Leaks through positions, replenishment timing or the checkpoint procedure. Accuracy must stay at chance. |
| C3-TWO-S0-SETS | Independent probe sets for exclusion and for the S0 baseline (design control) | Gains made up by chance noise in a single starting measurement (regression to the mean). |
| PC1 | Hand-set (neutral) perception cohort, matched on S0 | Confusing evolved learning speed with the tower's own lifetime learning. |
| PC2 | Shuffled-world cohort, matched on S0 | 'Ancestors happened to live with this kind of rule.' |
| G06 | Rarity-weighted matcher, used here as a learner | The vault's reserved bands making the essence easy to learn for a trivial reason. It must not meet threshold (1); if it does, the vault is redesigned. |
| TW1 | Exemplar twin (GCM style) | 'A textbook similarity learner does the same.' If indistinguishable under the 90% equivalence rule, credited to the conventional mechanism. |
| TW2 | Stretch-or-split write-rule twin | 'A textbook write rule does the same.' If indistinguishable under the 90% equivalence rule, credited to the conventional mechanism. |
| C3-TEACHER-FREE | Teacher-free cohort only; teacher-raised Frankies reported separately with watched exposures counted (design control) | Watching acting as hidden extra experience. |
| G01 | Always-eat bot | Measurement artefacts: it must show a flat curve (G at e = 40 at most 0.10) and never reach E50. |
| G02 | Eat-novel-first bot | Measurement artefacts and brute tasting: flat curve, never reaches E50. |
| G03 | Never-eat-new bot | Measurement artefacts: flat curve, never reaches E50. |
| G04 | Reject-all-unknown bot | Measurement artefacts: flat curve, never reaches E50. |

### Part tags

| Part | Tag |
|---|---|
| C3 (1) stratified log-rank, Frankie versus B1n-mind | PRIMARY-EFFECT |
| C3 (1) E50 ratio at least 2.0; Frankie's median E50 uncensored | FLOOR |
| C3 (2) poison bites no higher than B1n-mind | FLOOR |
| C3 (3) nature-shuffled arena at chance | VALIDITY |
| C3 (4) habit attribution versus OS08 | GATE |
| C3 (5) at most 30% 'prior already sufficient' | APPLICABILITY |
| C3 (6) G06 and gamer bots | VALIDITY |
| C3 (7) S0, G, E90, curves, reasoned share, all-channel, OS07, rule-seen | REPORTED |
| C3 (8) crediting to TW1 or TW2 | GATE |

### Log fields needed

- agent_id, agent_type (frankie | B1n-mind | B1t | G01 | G02 | G03 | G04 | G06 | TW1 | TW2), version (full | OS07 | OS08), version_scope, priors_cohort (evolved | PC1 | PC2), teacher_history
- matched_set_id / genome_id / temperament_seed / family_id / vault_id
- snapshot_id / parent_snapshot_id / clone_id, replica_key, stream_keys
- probe_role (member | lookalike) and eat_events.hidden_nature: world side only
- eat_events {object_id, kind_id, hidden_nature, energy_delta, effect_tick, stomach_delay_d, taste_vector, sick, net_gain, designed_exposure (must be false)}
- per tick: E / R / b, energy_band, fed, action / movement_target, action_provenance, gaze_target / gaze_distance / gaze_layer_reached, gaze_provenance, options_considered, satisficing_bar, no_safe_option
- struck_options {option, source, target_object_id, target_kind_id, predicted_p_above_R, strike_class: reasoned | rote | no-kind}
- memory_write_events (type, trigger, candidate_id_before, candidate_id_after, layer, per-feature weight deltas); candidate_lineage
- habit_weight_updates; habit_similarity_score / habit_similar / habit_contribution
- at each commit: verdict_subject, verdict_winner / verdict_margin / settle_steps / verdict_scope, elimination_events, objection_events
- injection_events (object-place replenishment and energy-set at probes, with vault provenance)
- trial_end_reason for probes; session end as trial_end_reason (tick-cap | eat-cap | death)
- replay_fingerprint_match
- exposure_events {tick, channel: wide | sharp-parts | sharp-details | smell | eat | watched, kind_id (world), designed: true | false}
- checkpoint_e and probe_set (S0-exclusion | S0-baseline | checkpoint) on each probe clone
- arena_decision_events {tick, object_id, distance, outcome: eat | leave, correct (world side)}; rule_seen_in_ancestry; family_order
- record, not a log field: priors card (W54), including teacher_ever_present (must be false), teacher_demonstrations_seen (must be 0) and family order

### If it fails

If Frankie does not beat B1n-mind under X32, or does not reach the 2x floor, the result is 'Frankie learns no more efficiently than brute trial-and-error', and the lifetime half of the reasoned-elimination claim fails. Stage 6's rule applies: go through the logs with Aitzaz and redesign the write rule. If the only advantage comes from S0, the credit goes to evolution. If it comes from habits, the credit goes to the conventional habit system. We will NOT: count prior success as learning; add a learning-progress or prediction-error reward; give weight to the designer's essence traits; swap in TW1 or TW2 by default; force eats in T3; count watched exposures as Frankie's own without reporting them; loosen the exclusion or censoring rules after seeing results; or tune on vault families.


---

## C4 · Outside-in context and inside-out objection

**Tag:** evidence (secondary)  
**Tests:** T4, T0

> 'Build context from the outside in: the scene, the apple, the note, then the writing; each outer layer constrains the next.'

**In plain words.** The scene and the overall shape tell Frankie what to expect, and the closer details either confirm it or object. A plastic apple looks right from far away, but a close look should make Frankie decide it doesn't fit before it bites. Three things should not happen. A single warning mark that Frankie has learned to fear should not override everything else. A harmless odd detail should not cause alarm. A real apple should not go unrecognised just because it is in an unusual place.

### Exact definition

DECISIONS: D13 (outside-in tower), D8 (sharp-look spending and evolved perception), D1 (sealed vaults). COHORT: evolved Frankies (priors_cohort=evolved, teacher_history=teacher-free). LEARNING PHASE: a 16x16 arena with sealed family F (nourishing) and its look-alike kind P_F (poison). P_F carries sticker part K on most of its instances, so K becomes a learned warning. Each kind sits in its own home scene 85% of the time, and the two home scenes differ. Lifetime food is also present. The phase runs until Frankie has made at least 3 of its own eats of F and at least 1 of its own eats of P_F (and got sick). If that has not happened within 3,000 ticks, the missing F or P_F eats are given as designed exposures (PLACEHOLDER-85, T4 entry), logged with action_provenance=designed-exposure and a designed_exposure record; a designed exposure with no committed verdict, or with verdict 'unknown', follows PLACEHOLDER-93. Scenario families are certified to differ from every Stage 5 bench kind. Snapshot S. STOMACH DELAY: d = 10 for all protocol eats (designed F and P_F eats and every probe eat; PLACEHOLDER-102). Chosen learning-phase eats are ordinary and follow PLACEHOLDER-49 (d = 3 in the first 2,000 ticks of the test life, then 10); the frozen spec states the switch tick. TRIALS: each trial is a single-probe clone from S (W52) with its own replica_key. The probe is 3 cells ahead, in F's home scene and on F's host unless stated, with no other edible object within 7 cells. Energy is R + 10 (energy-set injection), with T1's trial-end rules. (a) DECOY (probe_role decoy): copies F's object-layer and parts-layer values, has no smell, and its sheen is at least 10 noise widths outside F's observed range (certificate). a-beh pass = Frankie came within 2 cells (close enough for details) AND left without eating. Trials where it never came close count as failures, so 'rejecting from far away' cannot pass. a-trace pass (Frankie only) = an a-beh pass AND a verdict trace in which F's candidate leads at some settling step, an objection_event (details or smell layer) then resets it, and the final verdict_winner is not F. Both 'unknown' and 'some other thing' count as a correct final verdict and are reported separately [Aitzaz Q1, 24 Oct]. Rejections after a bite are counted separately and are not passes. (b) STICKERED MEMBER (probe_role stickered): an F member carrying K. pass = eat, plus verdict_winner F for Frankie. APPLICABILITY: (b) counts for a Frankie only if its memory at S gives K a relevance weight in P_F's candidate above the median of that candidate's feature weights; otherwise K is not a warning to that Frankie, and its (b) is 'not applicable' and counted. (c) ODD-DETAIL MEMBER (probe_role odd-detail): pass = eat AND verdict F. FILLERS (probe_role filler): plain F members and plain P_F instances (with K), 20 single-probe clones of each per Frankie. (d) SCENE 2x2: members in their home scene, members in P_F's home scene, P_F in F's home scene, and P_F in its own home scene. An error is rejecting a member or eating a look-alike. e_in = the mean error over the two cells where scene agrees with identity; e_out = the mean over the two where it misleads. OFF-SWITCH VERSIONS (OS01, OS02, OS03, OS04) are applied at test time to the same snapshot S (version_scope=test-time), so every version has the same memory and comparisons are paired. Versions switched off for the whole life (version_scope=lifetime) are reported. MATCHED THINKING ENERGY: OS01 with setting cap limits the flat tower's thinking per decision to this Frankie's median per-decision thinking spend in the same cell; OS01 with setting free (thinking cost zero) is reported. REGISTER ROWS: PLACEHOLDER-104 (85%, 3,000 ticks, the cap rule, the applicability rule for K, the 0.30 and 0.15 numbers), PLACEHOLDER-85, PLACEHOLDER-93, PLACEHOLDER-102.

### What gets measured

Per Frankie: a-beh, a-trace, b and c pass rates; filler member acceptance and filler look-alike rejection; e_in and e_out. Test-time off-switch comparisons use one-sided paired Wilcoxon tests on the same snapshot; lifetime-off versions use Mann-Whitney (reported). Comparisons are made at matched thinking energy (OS01 cap) and reported again at zero thinking cost (OS01 free). C4's single p (secondary family, X32) is the largest one-sided p among its four effect parts: (a) Frankie versus OS03 on a-beh; (b) Frankie versus OS02 on the stickered pass rate; (d) e_in, Frankie versus OS01 (cap); and (d) e_out, Frankie versus OS04. Bounds printed for these parts are taken at the level C4 receives in the secondary family. BEHAVIOURAL PROFILE P (computable for every mind and bot, since none of it needs a verdict trace): a-beh at least 0.70; b (eat only) at least 0.70; filler member acceptance at least 0.70; filler look-alike rejection at least 0.70; e_in at most 0.30; and e_out minus e_in at most 0.15.

### Pass mark

FRANKIE. (a) FLOORS: mean a-trace is at least 0.70, a-beh is at least 0.70, and filler member acceptance in the same Frankies is at least 0.70. SECONDARY-EFFECT: Frankie beats OS03 on a-beh (one-sided paired Wilcoxon). (b) APPLICABILITY: at least 30 applicable Frankies, otherwise (b) is 'not testable'. FLOORS: the mean stickered pass rate with verdict F is at least 0.70 [Aitzaz Q1, 24 Oct], and filler look-alike rejection is at least 0.70. The 0.70 bar applies to the group mean and is not lowered; individual cautious Frankies below 0.70 are reported with their boldness b rather than counted as individual failures [Aitzaz Q1, 24 Oct]. SECONDARY-EFFECT: Frankie beats OS02 on the stickered pass rate (one-sided paired Wilcoxon). (c) MECHANISM (one-sided 0.05 where a test is needed; never evidence): the odd-detail pass rate is at least 0.80. (d) SECONDARY-EFFECT: e_in(Frankie) is below e_in(OS01, cap), and e_out(Frankie) is below e_out(OS04), each one-sided paired Wilcoxon. FLOOR: e_out minus e_in is at most 0.15; this absolute margin replaces the proposal's 'at most 2 x e_in', which breaks when e_in is near 0. SINGLE p: C4's single p is the largest one-sided p among (a) versus OS03, (b) versus OS02, (d) e_in versus OS01 and (d) e_out versus OS04. It is tested in the secondary Holm family of ledger X32 (4 members, familywise 0.05; levels 0.0125, 0.0167, 0.025, 0.05); the old per-part 'p < 0.05' levels are removed. C4 is supported only if all four effect parts and every floor pass; if (b) is not testable, C4's single p cannot be formed and C4 is reported as 'not testable', with (a) and (d) reported separately. C4 may be promoted to the primary family only if its N is raised to 100 before the Wave 1 freeze (X32), making m = 8 [Aitzaz Q4, 24 Oct]. VALIDITY: G07, G08, B2, B1n-bot, G04, G01 and G09 must each fail behavioural profile P on this vault; otherwise the test is void and the vault goes back to Stage 4. GATE (crediting, outside every family): if the 90% intervals for Frankie minus TW1 on a-beh, on the stickered pass rate and on e_in each lie inside plus or minus 0.10, the result is credited to the conventional mechanism. REPORTED: lifetime-off versions, OS01 free, and post-bite rejections. Each part is reported separately either way, in the secondary table, never merged into the headline tally. Every number is a Claude or proposal number that goes into the register (PLACEHOLDER-104) for Aitzaz to initial.

### Sample size

50 Frankies (secondary evidence, not a primary; promotion to primary needs N = 100 before the freeze [Aitzaz Q4, 24 Oct]). Each Frankie gets 20 single-probe trials for each of (a), (b), (c), the 4 cells of (d) and the 2 filler types: 180 clones per Frankie per version, with test-time versions on the same snapshots. Every bot and lifetime-off version gets 50 runs with the same learning phase. At least 10 sealed scenario families with at most 5 Frankies each. Kinds: 10 x (F, P_F) = about 20 kinds, plus a decoy specification per family, entered in PLACEHOLDER-63 under the W35 reuse rule. N comes from the joint-power rule (X39): mocks at the planned effect sizes must pass all four effect parts and every floor together at least 80% of the time at the strictest secondary step (0.0125). N may only go up and is never changed after results are seen.

### Controls

| ID | Control | Rules out |
|---|---|---|
| OS03 | No objection (same snapshot) | Decoys being rejected by something other than an inner-layer objection (it should eat decoys). |
| OS02 | No gating (same snapshot) | Outer layers not being what outweighs the sticker (it should be fooled by stickers). |
| OS04 | Gates forced to maximum (same snapshot) | 'Context helps only by ignoring inner evidence' (hard lock-in on wrong-scene members). |
| OS01 | Flat tower: cap (Frankie's thinking spend) for the test, free (zero thinking cost) reported | 'Any classifier on the same features does it.' |
| C4-STICKER-APPLICABILITY | Sticker applicability check: K must carry learned weight (design control) | A Frankie 'outweighing' a mark that never meant anything to it, which would show nothing about outer layers. |
| B2 | Surface matcher | Surface matching (it eats decoys). |
| B1n-bot | Nearest-neighbour eat/skip bot (X36) | Rejecting a decoy only after a bad bite (a brute-memory result). |
| G04 | Reject-all-unknown bot | Blanket refusal (it fails the fillers or the stickered and odd-detail parts). |
| G01 | Always-eat bot | Blanket eating (it fails the decoy and filler look-alike parts). |
| G07 | Best single-trait bot (for example smell only), given the same learning phase | 'One detail trait decides everything.' If it meets profile P, the vault is redesigned. |
| G08 | Best two-trait bot, given the same learning phase | 'Two detail traits decide everything.' If it meets profile P, the vault is redesigned. |
| G09 | Scene-only bot | Context alone doing the work. It fails the e_out minus e_in margin. |
| TW1 | Exemplar twin (GCM style) | 'A textbook similarity model does the same.' If indistinguishable under the 90% equivalence rule in the threshold, credited to the conventional mechanism. |

### Part tags

| Part | Tag |
|---|---|
| C4 (a) Frankie versus OS03 on a-beh | SECONDARY-EFFECT |
| C4 (a) a-trace, a-beh and filler member acceptance at least 0.70 | FLOOR |
| C4 (b) Frankie versus OS02 on stickered pass rate | SECONDARY-EFFECT |
| C4 (b) stickered pass rate and filler look-alike rejection at least 0.70 | FLOOR |
| C4 (b) K applicability rule and at least 30 applicable Frankies | APPLICABILITY |
| C4 (c) odd-detail pass rate at least 0.80 | MECHANISM |
| C4 (d) e_in versus OS01 (cap); e_out versus OS04 | SECONDARY-EFFECT |
| C4 (d) e_out minus e_in at most 0.15 | FLOOR |
| C4 bot behavioural profile P | VALIDITY |
| C4 crediting to TW1 | GATE |
| C4 lifetime-off versions, OS01 free, post-bite rejections | REPORTED |

### Log fields needed

- agent_id, agent_type (frankie | B1n-bot | B2 | G01 | G04 | G07 | G08 | G09 | TW1), version (full | OS01 with cap | free | OS02 | OS03 | OS04), version_scope (test-time | lifetime), priors_cohort, teacher_history
- matched_set_id / genome_id / temperament_seed / family_id / vault_id
- snapshot_id / parent_snapshot_id / clone_id, replica_key, stream_keys
- probe_role (decoy | stickered | odd-detail | member | lookalike | filler) and eat_events.hidden_nature: world side only
- designed_exposure {tick, test=T4, item_role (F | P_F), choice_window_outcome: chosen | forced}
- eat_events {object_id, kind_id, hidden_nature, energy_delta, effect_tick, stomach_delay_d, taste_vector, sick, net_gain, designed_exposure}
- per settling step: verdict_subject, verdict_winner / verdict_margin / settle_steps / verdict_scope, elimination_events, objection_events (step, layer, candidate_reset, mismatch_value)
- per tick: E / R / b, energy_band, action / movement_target, action_provenance, gaze_target / gaze_distance / gaze_layer_reached, gaze_provenance, struck_options
- memory_write_events and candidate_lineage during the learning phase
- injection_events (energy-set at R + 10, with vault provenance)
- habit_contribution
- trial_end_reason
- replay_fingerprint_match
- exposure_events per kind and channel with scene_id; scene_id at Frankie's cell and at the probe; closest_approach_distance per trial
- memory_state_dump at snapshot: candidate list with per-feature relevance weights (including K's weight in P_F's candidate)
- thinking_cost / thinking_cap (per tick and per decision; OS01 cap)
- record, not a log field: object certificate (T0), including the bench-distinctness and decoy-sheen checks; priors card (W54)

### If it fails

If (a) fails, objection does not work in the living Frankie. If (b) fails, outer layers do not constrain inner ones; if it is not testable, Frankie never learned the warning mark, and that is reported. If (d) fails on one side, context either does not help or locks in. Each part is reported separately, and 'tower no better than the flat version' is a real result. We will NOT: add a hard-coded 'no smell means fake' rule or any designer-chosen essence trait; switch the attention rule to the proposal's best-split option by default; count rejections after a bite, or from far away, as passes; force eats beyond the PLACEHOLDER-85 list; or tune objection thresholds on vault families. Any retuning happens only on bench kinds, with Aitzaz's approval, flagged 'changed after seeing T4', and is rerun on a new one-use vault (D1).


---

## C5 · Elimination signature: look-alike count versus decision time

**Tag:** mechanism check  
**Tests:** T5, T0

> 'Humans use process of elimination a lot; instant recognition just happens that fast.'

**In plain words.** If Frankie recognises things by knocking out competitors, then the more look-alikes it knows, the longer it should take to settle on the right answer. Only look-alikes that are similar on the traits Frankie itself learned to rely on should count. How much it remembers should not matter, and neither should a general loss of confidence. This checks that a designed part works. It is NOT evidence of intelligence, and it says nothing about how humans think.

### Exact definition

DECISIONS: D13 (outside-in tower), D12 (spiking neurons; the reason for TW7). COHORT: evolved Frankies (priors_cohort=evolved, teacher_history=teacher-free). Snapshot S_T is taken after 3 of Frankie's own chosen eats of target kind T. From S_T, each condition gets a clone that receives k look-alike kinds of T, k in {0, 1, 2, 4, 8}. Each look-alike kind is met once through one designed eat of a nothing-nature instance (PLACEHOLDER-85, T5 entry), so Frankie is not poisoned 8 times; each is logged with action_provenance=designed-exposure and a designed_exposure record. A designed exposure with no committed verdict, or with verdict 'unknown', follows PLACEHOLDER-93: a new candidate is created (as in PLACEHOLDER-09), with no blame step, trigger=designed-exposure. Snapshot S_k is taken 20 ticks after the last effect. The memory log must show k separate new candidates; clones where it does not are excluded and counted, and if more than 20% are excluded at any level, that condition is 'not applicable'. STOMACH DELAY: d = 10 for all protocol eats (the look-alike designed eats and every probe eat; PLACEHOLDER-102). The 3 chosen eats of T are ordinary and follow PLACEHOLDER-49 (d = 3 in the first 2,000 ticks of the test life, then 10); the frozen spec states the switch tick. CONDITIONS (log condition values similar | dissimilar | high | low, with k). SIMILAR: k = 0, 1, 2, 4, 8. DISSIMILAR (k = 1, 2, 4, 8; k = 0 is shared): kinds at least 10 noise widths from T on every trait in the top half of T's candidate's relevance weights at S_T, met the same way, so the same number of memory slots is used. HIGH/LOW (k = 4): look-alikes matched on surface distance to T (PLACEHOLDER-91). HIGH kinds are similar to T on the top-half-weighted traits of T's candidate at S_T; LOW kinds only on the bottom-half traits. The harness picks them from pre-generated vault stock using the weights in the S_T memory dump. TRIALS: from each S_k, 20 single-probe MEMBER clones (fresh T instances) and 5 single-probe FILLER clones (a fresh instance of one of the k look-alike kinds; at k = 0, an unknown look-alike), each per W52. Each starts 2 cells away inside sharp-view range, with energy R + 10 (energy-set injection) and its own replica_key. Single-probe clones remove practice, memory change and energy drift between presentations. settle_steps = the number of settling steps inside the tower from the start of the presentation to commit, regenerated by exact replay (replay_fingerprint_match must be true). ticks_to_commit is also logged. Correct = an eat with verdict_winner T for members, and no eat for fillers. CONFIDENCE COVARIATE: T's candidate's reliability mark and its starting margin at S_k are logged, because k wrong guesses could mark T 'less reliable' and slow things down for a reason other than competition. TIME-PRESSURE VARIANT (similar condition): the food wilts (W47) at a deadline of 1.5 x the median ticks_to_commit of that Frankie's k = 0 member clones, logged as an injection_events object-remove. Error = a wrong verdict or a filler eaten; miss = no commit before the wilt (trial_end_reason=window-timeout at the wilt tick); cost = error or miss. The tower has no designed deadline signal, so slowness is expected to show mainly as misses. REGISTER ROWS: PLACEHOLDER-105 (1.5x, the 20% exclusion cap, the HIGH/LOW selection rule, the stock size per target), PLACEHOLDER-85, PLACEHOLDER-93, PLACEHOLDER-102, PLACEHOLDER-91.

### What gets measured

The pre-registered primary measure is settle_steps. Measures: the trial-level Spearman rho between k and settle_steps, pooled, with a Frankie-blocked permutation test; the median of per-Frankie rhos; the slope of settle_steps on log2(k + 1) in the similar and dissimilar conditions, with an interaction test; the same slope with T's reliability mark and starting margin added as covariates; HIGH minus LOW mean settle_steps at k = 4 (paired); accuracy at each k; and, under time pressure, the trend across k in cost (error or miss), with errors and misses also reported separately (Jonckheere-Terpstra). All tests are one-sided in the pre-registered direction at C5's own stricter level of 0.01 (mechanism check, outside every Holm family). ticks_to_commit is reported but is not part of the pass, because it mixes in the drive's choice to spend on a sharp look.

### Pass mark

All parts are MECHANISM unless stated, each one-sided at C5's pre-registered level of 0.01 (stricter than the 0.05 default for mechanism checks, never looser); results are never counted as evidence. (1) The pooled trial-level rho is above 0.5 with Frankie-blocked permutation p < 0.01, AND the median per-Frankie rho is above 0.5. (2) Accuracy is at least 0.85 at EVERY k, not just on average. (3) In the dissimilar condition, the slope is significantly smaller than in the similar condition (interaction p < 0.01), and the pooled rho is below 0.2. (4) HIGH beats LOW at k = 4, paired Wilcoxon p < 0.01. (5) Under time pressure, cost (error or miss) rises with k (Jonckheere-Terpstra p < 0.01). (6) The similar-condition slope stays positive with p < 0.01 after the reliability and margin covariates are added; otherwise the slowdown is attributed to lost confidence, not competition. APPLICABILITY: a condition with more than 20% of clones excluded at any k (k separate new candidates not shown) is 'not applicable'. (7) VALIDITY: MK2 passes (1) to (5), OS05 and B2 stay flat (rho below 0.2), and MK1 fails (3); otherwise the test is void. REPORTED: ticks_to_commit, errors and misses separately, and TW7. Every number is a Claude or proposal number that goes into the register (PLACEHOLDER-105) for Aitzaz to initial.

### Sample size

50 Frankies. Snapshots per Frankie: 5 similar levels, 4 dissimilar levels and 2 HIGH/LOW = 11, each with 25 single-probe clones (20 members + 5 fillers), so 275 per Frankie (13,750 trials). Plus time pressure on the similar condition: 5 x 25 per Frankie. OS05, B2, MK1, MK2 and TW7 get 50 runs each. At least 10 sealed target families. Kinds: per target, 8 similar look-alikes plus a stock of about 16 for HIGH/LOW selection, with dissimilar kinds drawn from other targets' stock: about 250 kinds, entered in PLACEHOLDER-63 under the W35 reuse rule. If the battery total passes 1,000, the budget is raised and N is never cut; reducing C5's stock to 12 per target is allowed only as a design choice made before the freeze. N may only go up (X39) and is never changed after results are seen.

### Controls

| ID | Control | Rules out |
|---|---|---|
| C5-DISSIMILAR | DISSIMILAR condition with the same memory size (design control) | 'More memory means slower', a plain memory-size effect. |
| C5-HIGH-LOW | HIGH/LOW condition (design control) | Raw surface similarity, rather than Frankie's own learned diagnostic traits, driving the slowdown. |
| C5-COVARIATES | Reliability-mark and starting-margin covariates (design control) | 'Frankie just got less confident about T after k wrong guesses', a slowdown unrelated to competition. |
| MK1 | Serial-scan mock (searches every memory slot) | 'Any search slows down.' It slows with similar and dissimilar memory alike, so it must fail part (3). |
| OS05 | Pick-the-max (no competition) | The slowdown coming from anything except the competition. |
| B2 | Surface matcher, used as a flat reference | Nothing beyond giving a flat reference. |
| MK2 | Positive-control accumulator mock (reads hidden state) | The test being unable to detect the effect at all: it must pass parts (1) to (5). |
| C5-FILLERS | Single-probe filler clones (design control) | Being fast and accurate simply by always eating. |
| TW7 | Rate-based twin (reported only) | Doubt over whether the signature depends on spiking (D12). |
| C5-TIME-PRESSURE | Time-pressure variant (W47 wilting) | Slow settling being free. It should cost errors or missed food when hurried. |

### Part tags

| Part | Tag |
|---|---|
| C5 (1) rho between k and settle_steps | MECHANISM |
| C5 (2) accuracy at least 0.85 at every k | MECHANISM |
| C5 (3) dissimilar slope smaller, rho below 0.2 | MECHANISM |
| C5 (4) HIGH beats LOW | MECHANISM |
| C5 (5) time-pressure cost rises with k | MECHANISM |
| C5 (6) slope survives covariates | MECHANISM |
| C5 20% exclusion cap | APPLICABILITY |
| C5 (7) MK2, OS05, B2, MK1 checks | VALIDITY |
| C5 ticks_to_commit, errors and misses separately, TW7 | REPORTED |

### Log fields needed

- agent_id, agent_type (frankie | B2 | MK1 | MK2 | TW7), version (full | OS05), version_scope, priors_cohort, teacher_history
- matched_set_id / genome_id / temperament_seed / family_id / vault_id
- snapshot_id (S_T / S_k) / parent_snapshot_id / clone_id, replica_key, stream_keys
- condition (similar | dissimilar | high | low, with k)
- probe_role (member | filler) and eat_events.hidden_nature: world side only
- designed_exposure {tick, test=T5, item_role (look-alike kind), choice_window_outcome: forced}
- memory_write_events (type new expected for each look-alike kind; trigger designed-exposure; candidate_id_after; layer) for the exclusion check; candidate_lineage
- verdict_subject, verdict_winner / verdict_margin / settle_steps / verdict_scope; elimination_events and objection_events per settling step
- eat_events {object_id, kind_id, hidden_nature, energy_delta, effect_tick, stomach_delay_d, taste_vector, sick, net_gain, designed_exposure}
- per tick: E / R / b, energy_band, action / movement_target, action_provenance, gaze_target / gaze_distance / gaze_layer_reached, gaze_provenance
- injection_events (energy-set at R + 10; object-remove at the wilt tick, with vault provenance)
- trial_end_reason (committed-eat | committed-skip | window-timeout | left-area)
- replay_fingerprint_match
- memory_state_dump at S_T and S_k: candidate list, per-candidate per-feature relevance weights, reliability marks
- probe_onset_tick / commit_tick / ticks_to_commit / time_pressure (true | false); thinking_cost
- high_low_selection (the weights used, the chosen kinds and their surface distance to T)
- record, not a log field: priors card (W54), including teacher_ever_present (must be false)

### If it fails

The competition does not behave like elimination inside the living Frankie: one candidate wins at once, like a nearest-match classifier. That is reported as a real result. If the slowdown is explained by lost confidence, it is reported that way. A pass is not evidence of intelligence and is kept out of the evidence tally. We will NOT: retune inhibition, leak or margins on vault kinds (any change is made on bench kinds only, with Aitzaz's approval, flagged 'changed after seeing T5', and rerun on a new one-use vault); add a deadline signal to the tower to make (5) pass; switch to rate-based neurons by default (Aitzaz decides, D12); force eats beyond the PLACEHOLDER-85 list; or claim anything about human cognition either way.


---

## C6 · Mutual exclusivity without language (the 'dax' analogue)

**Tag:** evidence (secondary)  
**Tests:** T6, T0

> 'Humans use process of elimination a lot.'

**In plain words.** Ask a toddler to 'hand me the dax' and they pick the toy that has no name yet. Frankie's version: it knows three kinds, one never-seen object sits among them, and a never-smelled smell appears around Frankie with no hint of direction. If Frankie reasons 'this smell isn't any of the things I know, so it must belong to the new thing', it should look at or approach the new object first. That has to be more than 'new things attract me' or 'anything new makes me check the new thing', and Frankie must show that it links known smells to the things it knows.

### Exact definition

DECISIONS: D8 (sharp-look spending), D13 (outside-in tower; 'unknown' unit), D1 (sealed vaults). NOT TESTABLE until two perception rules are frozen: PLACEHOLDER-94 / ledger M52 (a smell with no object attached enters the details layer as evidence for every candidate and for 'unknown', with no built-in link to any object) and PLACEHOLDER-95 (the wide view lists each visible object with blurred hue and size; roundness and lobes are read only by the sharp view, up to 7 cells away). The per-object wide-view verdicts below are conditional on PLACEHOLDER-95 as frozen, and the verdict trace on the injected smell is conditional on PLACEHOLDER-94. With PLACEHOLDER-95 as written, nothing here expects roundness or lobes from the wide view. COHORT: evolved Frankies (priors_cohort=evolved, teacher_history=teacher-free). Each knows exactly 3 sealed kinds, each eaten once (by designed exposure if needed: PLACEHOLDER-85, T6 entry, logged with action_provenance=designed-exposure and a designed_exposure record; a forced eat with no committed verdict, or verdict 'unknown', follows PLACEHOLDER-93), so each one's own smell has been met up close. STOMACH DELAY: d = 10 for all protocol eats (the designed known-kind eats; there are no probe eats, since responses are looks or steps; PLACEHOLDER-102). Chosen eats before the snapshot follow PLACEHOLDER-49 (d = 3 in the first 2,000 ticks of the test life, then 10); the frozen spec states the switch tick. A snapshot is taken, and every trial is a single-probe clone from it (W52) with its own replica_key. RING: Frankie stands at the centre of a ring of radius 3 cells (inside parts range, outside details and adjacent-smell range), facing a random direction. The 4 objects (fresh instances of the 3 known kinds plus 1 never-seen kind N) sit 90 degrees apart, with the rotation counterbalanced over 20 clones so each object takes each position 5 times. WIDE VIEW: N's blurred hue and size combination must be distinguishable from each known kind beyond wide-view noise (at least one wide-view level apart on hue or size, PLACEHOLDER-106), so Frankie CAN tell which one is new without a sharp look; its salience (brightness and size magnitude) must lie inside the known kinds' range, so it is not simply more eye-catching. The objects' own contributions to ambient smell are masked during the trial (injection_events type smell-mask, W48). CUE: at onset the harness injects a cue at Frankie's own cell (injection_events type cue-inject, W48). It moves with Frankie and never forms a gradient. CONDITIONS, on separate clones from the same snapshot: NEW-SMELL (N's own never-smelled smell, from a reserved band); NO-SMELL; KNOWN-SMELL (the smell of one of the 3 known kinds, chosen at random); NEW-SMELL-NO-NOVEL (a new smell, with a 4th instance of a known kind in N's place); NOVEL-GROUND (no smell, but a never-seen ground signature from a reserved band appears under Frankie: a new cue that no object could have caused). Energy is R + 10 (energy-set injection). RESPONSE = whichever comes first after onset: the sharp view pointed at one of the 4 objects (gaze_target), or a step whose movement_target is one of them. The trial ends at the first response or after 100 ticks with no response (trial_end_reason=window-timeout). The wide-view verdicts on all 4 objects at onset are logged; trials in which N was not marked 'unknown' (Frankie could not tell which one was new) are reported separately. The object certificate (T0) confirms that N, its smell and the novel ground were never met by this Frankie, its ancestors (per the evolution exposure summaries) or any teacher. REGISTER ROWS: PLACEHOLDER-106 (the 100-tick window, radius 3, the reserved bands for new smells and novel ground, the wide-view distinguishability margin and salience range), PLACEHOLDER-94, PLACEHOLDER-95, PLACEHOLDER-85, PLACEHOLDER-93, PLACEHOLDER-102.

### What gets measured

Per Frankie and condition: P_novel = the share of first responses that target N (or N's position in NEW-SMELL-NO-NOVEL), computed two ways: among responders, and intention-to-treat (no response counted as 'not N'). EMPIRICAL CHANCE = the rate of first responses to N's position in NEW-SMELL-NO-NOVEL, which captures position and turning biases instead of assuming 25%. One-sided paired Wilcoxon tests by Frankie: NEW-SMELL versus empirical chance; NEW-SMELL versus NO-SMELL; NEW-SMELL versus KNOWN-SMELL; NEW-SMELL versus NOVEL-GROUND, the last three under both responder and intention-to-treat scoring. C6's single p (secondary family, X32) is the largest of these seven one-sided p-values; bounds printed for them are taken at the level C6 receives in the secondary family. Also reported: response rate per condition; in KNOWN-SMELL, P(first response = the smell's own kind); whether the 'unknown' unit was active for the smell in the verdict trace; where the first response came from (gaze_provenance: drive-sharp-look, proposal or habit; or a step, by action_provenance); and a walking-only scoring as a sensitivity check. Analysis is clustered by N kind.

### Pass mark

APPLICABILITY: C6 is 'not testable' until PLACEHOLDER-94 and PLACEHOLDER-95 are frozen. (1) SECONDARY-EFFECT: P_novel(NEW-SMELL) is above empirical chance (one-sided paired Wilcoxon). FLOOR: mean P_novel(NEW-SMELL) is at least 0.60. (2) SECONDARY-EFFECT: P_novel(NEW-SMELL) minus P_novel(NO-SMELL), one-sided, under BOTH responder and intention-to-treat scoring. FLOOR: the difference is at least 0.15 under both. (3) SECONDARY-EFFECT: P_novel(NEW-SMELL) minus P_novel(KNOWN-SMELL), both scorings. FLOOR: at least 0.15 under both. (4) SECONDARY-EFFECT: P_novel(NEW-SMELL) minus P_novel(NOVEL-GROUND), both scorings. FLOOR: at least 0.15 under both. SINGLE p: C6's single p is the largest one-sided p among (1) and (2) to (4) under both scorings (seven tests). It is tested in the secondary Holm family of ledger X32 (4 members, familywise 0.05; levels 0.0125, 0.0167, 0.025, 0.05); the old fixed 0.01 and 0.05 levels are removed. (5) FLOOR: the response rate in NEW-SMELL is at least 0.80 (other conditions reported). (6) APPLICABILITY (precondition, one-sided 0.05): in KNOWN-SMELL, P(first response = the smell's own kind) is significantly above 0.25. If not, any NEW-SMELL effect is reported as 'not through smell matching' and is not counted as evidence. (7) VALIDITY: G02, G11 and B0 each fail at least one of (1) to (4); otherwise the test is void and goes back to Stage 4. (8) GATE (one-sided 0.05, uncorrected): if the effect in (2) to (4) disappears under OS12 (OS12 fails at least one of the (2) to (4) floors, or its effect is significantly smaller than Frankie's) AND more than half of Frankie's first responses have gaze_provenance=drive-sharp-look, the result is credited to the conventional value-of-information rule. GATE (crediting, outside every family): if the 90% interval for Frankie minus TW1u in P_novel(NEW-SMELL) minus P_novel(NO-SMELL) lies inside plus or minus 0.10, the result is credited to the conventional mechanism. REPORTED: a pass by evolved Frankies only (PC1 fails) is reported as a prior, not as lifetime intelligence [Aitzaz Q4, 24 Oct]; OS11; walking-only scoring; trials where N was not marked 'unknown'. Results go in the secondary table, never merged into the headline tally. Every number is a Claude or proposal number that goes into the register (PLACEHOLDER-106) for Aitzaz to initial.

### Sample size

50 Frankies (secondary evidence, not a primary), each with 5 conditions x 20 clones (5,000 trials). Kinds can be shared across Frankies because novelty only has to hold for each Frankie (W35 reuse rule: never within a life, within a matched set, or between a lineage's ancestral pool and its tested lives): 25 N kinds (each used for 2 Frankies), 30 known kinds in rotating triples, 25 reserved new smells and 25 reserved novel-ground signatures, about 55 kinds in all, entered in PLACEHOLDER-63. Analysis is clustered by N kind. OS11, OS12, G02, G11, B0, PC1 and TW1u get 50 runs each on the same rings. N comes from the joint-power rule (X39): mocks at the planned effect sizes must pass all seven effect tests and every floor together at least 80% of the time at the strictest secondary step (0.0125). N may only go up and is never changed after results are seen.

### Controls

| ID | Control | Rules out |
|---|---|---|
| NO-SMELL | NO-SMELL condition | Plain attraction to new things. |
| KNOWN-SMELL | KNOWN-SMELL condition | 'Any smell makes Frankie look at the newest thing' (general arousal rather than matching the smell to an unexplained object). It also checks that Frankie links known smells to their kinds, which the exclusion reasoning needs. |
| NOVEL-GROUND | NOVEL-GROUND condition | 'Anything new makes Frankie check the new thing' (novelty primes novelty), as opposed to an unexplained smell being assigned to the unexplained object. |
| NEW-SMELL-NO-NOVEL | NEW-SMELL-NO-NOVEL condition | Position or turning biases. It gives the empirical chance level and shows where Frankie goes when no object can explain the smell. |
| C6-ITT | Intention-to-treat scoring alongside responder-only scoring (design control) | A pass created by Frankie responding only in some conditions or trials. |
| C6-WIDE-VIEW | Wide-view distinguishability with matched salience, and masked object smells (design control) | N being brighter or bigger or leaking its smell's direction, and the opposite problem: N being impossible to pick out without a sharp look. |
| OS11 | 'Unknown' unit off | Doubt over whether the unknown candidate is the route by which the smell links to the new object. |
| OS12 | Sharp looks from proposals only (value-of-information rule off) | The effect being carried entirely by the conventional value-of-information rule for sharp looks. If so, it is credited to that conventional rule. |
| G02 | Eat-novel-first bot | Novelty seeking passing as exclusivity (it goes to N with or without the smell). |
| G11 | Always-explore bot | Exploring everything passing as exclusivity (it goes to N with or without the smell). |
| B0 | Random bot | Nothing beyond giving chance. |
| PC1 | Hand-set (neutral) perception cohort | Confusing an evolved reflex (ancestral worlds had new kinds with new smells) with lifetime inference. |
| TW1u | Exemplar twin with an 'unknown' threshold | 'A textbook model does the same.' If indistinguishable under the 90% equivalence rule in the threshold, credited to the conventional mechanism. |

### Part tags

| Part | Tag |
|---|---|
| C6 (1) NEW-SMELL versus empirical chance | SECONDARY-EFFECT |
| C6 (2) to (4) NEW-SMELL versus NO-SMELL, KNOWN-SMELL, NOVEL-GROUND, both scorings | SECONDARY-EFFECT |
| C6 P_novel at least 0.60; differences at least 0.15 | FLOOR |
| C6 (5) NEW-SMELL response rate at least 0.80 | FLOOR |
| C6 not testable until PLACEHOLDER-94 and -95 are frozen | APPLICABILITY |
| C6 (6) KNOWN-SMELL precondition | APPLICABILITY |
| C6 (7) G02, G11, B0 must fail | VALIDITY |
| C6 (8) value-of-information attribution (OS12) | GATE |
| C6 crediting to TW1u | GATE |
| C6 PC1 prior label, OS11, walking-only scoring, N-not-unknown trials | REPORTED |

### Log fields needed

- agent_id, agent_type (frankie | B0 | G02 | G11 | TW1u), version (full | OS11 | OS12), version_scope, priors_cohort (evolved | PC1), teacher_history
- matched_set_id / genome_id / temperament_seed / family_id / vault_id
- snapshot_id / parent_snapshot_id / clone_id, replica_key, stream_keys
- condition (NEW-SMELL | NO-SMELL | KNOWN-SMELL | NEW-SMELL-NO-NOVEL | NOVEL-GROUND)
- injection_events (cue-inject with cue type smell | ground, cue vector and attached-to-Frankie flag; smell-mask; energy-set; with vault provenance)
- designed_exposure {tick, test=T6, item_role (known kind), choice_window_outcome: chosen | forced}; eat_events with stomach_delay_d for the 3 known-kind eats
- per tick from onset: E / R / b, energy_band, action / movement_target, action_provenance, gaze_target / gaze_distance / gaze_layer_reached, gaze_provenance (habit | proposal | drive-sharp-look | no-safe-option-fallback | baseline-rule, the last for B0, G02 and G11), options_considered, struck_options
- wide-view verdicts on each of the 4 objects at onset (conditional on PLACEHOLDER-95): verdict_subject, verdict_winner (candidate_id | unknown), verdict_margin, verdict_scope=blurry
- verdict on the injected smell (conditional on PLACEHOLDER-94) and on each gazed object: verdict_winner (including unknown), verdict_margin, settle_steps, elimination_events, objection_events
- trial_end_reason (window-timeout when no response in 100 ticks)
- replay_fingerprint_match
- arena_layout (T6: ring_rotation, object positions, ring_object_role N | known, wide-view salience and distinguishability values)
- first_response {tick, target object, channel: gaze | step}
- exposure_events before the snapshot (exactly 3 known kinds, each eaten once, with their adjacent smells)
- record, not a log field: object, smell and ground certificates for N (T0); priors card (W54), including teacher_ever_present (must be false)

### If it fails

The result is reported as 'no mutual-exclusivity analogue': Frankie does not link an unexplained sense to an unexplained thing. If only evolved Frankies pass and PC1 Frankies do not, it is reported as an inherited tendency (a prior). If the effect matches NOVEL-GROUND, it is reported as 'novelty primes novelty'. If it rests on the value-of-information rule, it is credited to that conventional rule. If PLACEHOLDER-94 or PLACEHOLDER-95 is not frozen, C6 is reported as 'not testable', not as a failure. We will NOT: add a novelty or uncertainty bonus, a built-in smell-to-object link, or a 'go to the new thing' rule; give the wide view roundness or lobes to make N easier to pick out; drop the KNOWN-SMELL or NOVEL-GROUND controls because they make the test fail; force eats beyond the PLACEHOLDER-85 list; or tune on vault kinds.


---

## C7 · Curiosity as insurance: trying path B, and exploring after the world changes

**Tag:** evidence (primary)  
**Tests:** T7, T8, T0 (leak and contamination audit, priors card), Stage 4 bot calibration (including G14 and the G13 regrowth and T8(a) checks) and the X39 joint-power simulation on MK3

> 'If we succeed it would basically be making Frankie curious. If I've taken path A all this time, what happens if I take path B.'

**In plain words.** Frankie counts as curious in Aitzaz's sense when its usual food source (path A) still works and it is not hungry, yet it spends some energy finding out about an untried place or thing (path B). The reason has to be that its own life has taught it that sources can fail, so a known backup is worth having. Nothing rewards it for newness. The energy economy is its only reason to look. Four cheap look-alikes do not count: hunger (it had to look), the designed dice (by design, a rich Frankie gets more random ideas), passing through (it would have ended up there anyway) and plain boldness after a hard time. Frankie cannot see B from A, so the test asks what Frankie does once it has spotted B, not whether it somehow knew B was there. The second half is the payoff. When path A really fails, Frankies that knew path B recover faster, and Frankies that have lived through a failure check alternatives more afterwards. A newborn starts out believing that sources never fail, until it sees one fail [Aitzaz Q3, 24 Oct]. Honest note: the rule 'a known backup lowers risk' is designed (conventional risk-sensitive foraging). What is not designed is the evidence that feeds it. How often sources fail comes only from Frankie's own life, and nothing tells it to go to B.

### Exact definition

SHARED RULES. E = Frankie's energy; R = its own reserve (from its temperament, ledger M33). Fed = E > R (log field fed). Energy bands are the shared bands of ledger M54: well-below E <= R-10; near R-10 < E < R+20; well-above E >= R+20 (log field energy_band). Close look = sharp view on an object from 4 cells or nearer (gaze_distance <= 4). Never-tried = no eat and no close look at that kind anywhere in this life's ledger. Sighting = the tick an object first appears in Frankie's wide view, computed world-side from the wide-view log (the per-object wide-view listing follows PLACEHOLDER-95). MATCHED SET (ledger X38) = lives that share one genome_id, one temperament_seed and one world seed, and differ only in the condition assigned to them by keyed lottery before birth. Temperament is still sampled fresh for each set and never inherited (D7). All lives are teacher-free (teacher_history = teacher-free; teacher_ever_present = false). YOKED ENERGY (ledger W45): at every 50-tick checkpoint the yoked life's E is compared with its partner's, and the difference is removed (or added) evenly over the next 50 ticks. Eats still land normally, so what Frankie learns from eating is untouched. Every adjustment is a logged injection_events entry of type yoke-adjust. FIXED-RANDOMNESS (OS14): the proposal count is one constant for every Frankie and every tick, equal to the designed curve's value at E = R+20, which is the whole number 2 under PLACEHOLDER-25; if the frozen curve gives a fractional value there, it is rounded stochastically from the proposal stream (PLACEHOLDER-96). NO-RICH-ARM (OS15): above R the curve is held at its near-reserve value, and the desperate side below R-10 is kept. BACKUPS-DON'T-COUNT (BDC, OS13): the drive's estimate of what A failing would cost ignores every backup, both remembered sources and the expected value of untried things as possible backups. Nothing else in the mind changes. ATTRITION (X38), T7 only: a whole pair is dropped if any member dies before or during the T7 window (ticks 5,000-7,999) or has fewer than 500 fed ticks in it. T8 has its own rule: a whole set is dropped only if a member dies before tick 5,000. Deaths after tick 5,000 are kept: such a life is scored at the worst case for the claim in C7-T8(c) if it died before tick 7,500: a CHANGE life counts as K = 0, and a NO-CHANGE, HUNGER-YOKED or TOPPED-UP life counts as the highest K observed among surviving lives of its own condition, and its recovery counts as 2,000 in C7-T8(a); the 20%-death-before-6,500 rule decides whether T8 is informative. A T8 life (surviving or dying after tick 7,500) with fewer than 500 fed ticks in ticks 7,500-9,999 has K computed per 1,000 scheduled ticks of that window (episodes / 2,500 x 1,000) instead of per 1,000 fed ticks, and is flagged (Claude placeholder, PLACEHOLDER-107). Drops are counted per condition, so exclusion is equal across groups by construction. STOMACH DELAY: the one T8 designed taste is a protocol eat and uses d = 10. Ordinary eats follow PLACEHOLDER-49: d = 3 for ticks 0-1,999 of the life and d = 10 from tick 2,000, so every eat in T7's hard spell and window and in all of T8's measured periods uses d = 10 (PLACEHOLDER-102). The applied value is logged in eat_events.stomach_delay_d.

DRIVE SETTINGS THIS CLAIM DEPENDS ON (frozen before T7). The satisficing bar is the required chance of staying above R, 0.9 - 0.3 x b (PLACEHOLDER-27; PLACEHOLDER-22 now reads 'the bar comes from PLACEHOLDER-27') [Aitzaz Q3, 24 Oct]. Options are considered habit first, then proposals in the order drawn (PLACEHOLDER-23) [Aitzaz Q3, 24 Oct]. With habit first, a fed Frankie leaves path A only when its own record says A alone is not safe enough, which is the insurance route; with proposals first, most rich-Frankie exploring would be the designed dice. If no option clears the bar, Frankie takes the option with the best chance of staying above R, tagged action_provenance = no-safe-option-fallback with no_safe_option = true (ledger M47) [Aitzaz Q3, 24 Oct]; this is the only best-score rule allowed inside Frankie, and the BDC gate covers it. A newborn's belief about how often food sources fail is zero until it sees a source fail (ledger M48) [Aitzaz Q3, 24 Oct]. Under this placeholder, Frankies that have never seen a failure are expected to try B only through the designed dice, which does not count as curiosity. If Aitzaz pictures curiosity before any failure, the honest route is a small non-zero starting belief, logged as a designed prior. M48 is separate from the newborn starting value for untried things (M25). The proposal-count curve is PLACEHOLDER-25 as rewritten: 1 proposal within 10 units of R, rising in a straight line to 4 at R+40; below R-10 the count is 1 + s x (R-10-E), with s the Frankie's desperation slope (PLACEHOLDER-26), capped at N_max = 6 (PLACEHOLDER-97). There is no hysteresis (PLACEHOLDER-100).

T7, PATH B WHILE FED.
(i) History. Each matched pair has one experienced and one naive life (condition = experienced | naive). In the experienced life the main source stops fruiting for a fixed stretch (placeholder ticks 2,000-2,800, PLACEHOLDER-107) and then resumes (injection_events source-stop, object-remove, source-resume). The naive life's source keeps fruiting, and its energy is yoked to the experienced partner over that stretch (W45). Both have the same hungry spell, and only one sees a source fail.
(ii) Window: ticks 5,000-7,999. At tick 4,990, every food source except A is cleared in both lives (injection_events source-clear), so the window world is the same for both. Old backups now exist only in memory. A = the source this life ate from most in ticks 4,000-4,989. A's regrowth is set on stand-in kinds at Stage 4 so that G13 is fed in at least 90% of window ticks. At tick 5,000, patch B (a 12 +/- 2 cell walk from A, outside the wide view from A) receives 6 objects of one never-seen NOURISHING kind from a one-use sealed vault (injection_events object-place). They do not regrow. Each carries a novelty certificate covering this Frankie, its ancestors and the teacher repertoire. There is no designed exposure in T7 (PLACEHOLDER-85 bans it).
(iii) Clones at tick 5,000 with identical world keys (version_scope = test-time): clone_type FULL (version full), BDC (OS13), FIXED-RANDOMNESS (OS14), NO-RICH-ARM (OS15), and KNOWN-ONLY-B (full mind, but B's 6 objects are a kind this Frankie has eaten at least 3 times). Bots and baselines that have no such switch run identical copies in every clone slot.
(iv) Measures. I7 = distinct B objects given a close look or eaten, counting only episodes that start while fed, per 1,000 fed ticks. Approach-given-sighting = among sightings of B objects while fed, the share followed within 100 ticks by a choice whose movement_target or gaze_target is that B object. A pair is left out of this measure if either member never sighted B, and these pairs are counted. Investigated = at least one close look at B while fed (yes/no). The first-sighting tick and first-investigation tick are reported.
T7 passes only if ALL of these hold:
EFFECT PART (PRIMARY-EFFECT), tested at C7's Holm level:
C7-T7(1) Experience effect: FULL I7 is higher in the experienced life than in its naive partner (paired, one-sided Wilcoxon signed-rank). FLOOR: the share of pairs in which the experienced life scores higher (ties count half) is at least 0.64.
EXPLANATION GATES, each at one-sided 0.05, with floors on the estimates:
C7-T7(2) It runs through insurance. (2a) Experienced FULL > experienced BDC (paired clones). (2b) The per-life drop FULL - BDC is larger in the experienced life than in its naive partner (paired). (2c) FLOOR: the experienced-minus-naive mean gap under BDC is at most half the gap under FULL. This gate catches every non-insurance route at once, including habits formed in the hard spell, more remembered places, bolder first-encounter averages, and the M47 fallback when no option clears the bar.
C7-T7(3) Not the designed dice: experienced > naive still holds in the FIXED-RANDOMNESS clones and in the NO-RICH-ARM clones, each with a FLOOR pair-superiority share of at least 0.60.
C7-T7(4) Not passing through: approach-given-sighting is higher in experienced FULL than in naive FULL, and higher than in experienced BDC (both paired).
FLOOR, no significance test:
C7-T7(5) Reasoned, not brute: pooled over experienced FULL clones, at least 80% of eats of B objects happen within 20 ticks after a close look at that same object, and the lower end of the 95% interval is at least 70%. The median per-life number of B objects eaten is at most 3 of 6. If fewer than 30 B eats are pooled, (5) is untestable and T7 cannot be 'supported'.
VALIDITY, checked on stand-in kinds at Stage 4 and again on the opened vault:
C7-T7(6) Every must-fail bot (B0, B1n-forager, B3, B4, G02, G04, G11, G13, G14) fails at least one of (1)-(5), and MK3 passes all of them. G14 must pass (1) and fail (2), which shows (2) is the gate doing the work. TW3 and the off-switch versions are not must-fail.
REPORTED, not required: KNOWN-ONLY-B results (insurance predicts that a known-food B is also worth visiting, but needs fewer close looks per entry); the share of B-approach choices whose drive_trace_replayed shows a positive backup_contribution; the share of fed ticks with no_safe_option = true (M47); struck_options on B objects by strike_class (B's kind has zero own eats, so such strikes are reasoned); first-encounter average and candidate count at window start; visits to old, cleared food spots; and investigated / first-investigation tick by condition.

T8, THE WORLD CHANGES.
Design: 100 matched sets x 8 lives: pre_exposed yes or no, crossed with four conditions. Patch B in T8 (Claude placeholder, PLACEHOLDER-107): in every life of a set, patch B is 12 +/- 2 cells from A and outside the wide view from A, and receives 6 objects of the set's one never-seen NOURISHING B kind at tick 2,900 (injection_events object-place), before the designed walk; B stays for the rest of the life, and each eaten B object regrows in the same cell 200 ticks later, so B is still there when A fails at tick 5,000. Pre-exposure is a designed exposure under PLACEHOLDER-85: a designed walk past B at tick 3,000 with exactly one taste of B's nourishing kind, logged with action_provenance = designed-exposure, a designed_exposure record and eat_events.designed_exposure = true, and printed on the priors card. If the frozen spec lets Frankie eat it by choice during the walk, the chosen and forced subgroups are reported separately. Conditions: CHANGE: at tick 5,000, A's fruits are removed and A stops fruiting (object-remove, source-stop). It resumes at 6,500 and fails again at 10,000. NO-CHANGE: A never fails before tick 10,000. HUNGER-YOKED: A keeps fruiting, and energy is yoked to the CHANGE life of the same set and pre-exposure (W45). TOPPED-UP: A stops as in CHANGE, and every 50 ticks after tick 5,000, E is raised back to its tick-5,000 level if it is below it (W45; injection_events top-up). From tick 4,000 to 10,000, every life's world holds the same 4 never-tried objects, placed by key 8-12 cells from A and replaced every 500 ticks by fresh vault kinds (a pre-registered mix: half nourishing, half nature nothing). This way there is always something untried to check, and it is the same for every condition.
C7-T8(a) Insurance has real value [VALIDITY: world check, required, not evidence]. Recovery = ticks from 5,000 to the next nourishing eat, capped at 2,000; death or no gain counts as 2,000. Mean recovery of pre-exposed CHANGE lives must be at most 0.75 x that of not-pre-exposed CHANGE lives in the same sets. At Stage 4, before the mind exists (K-F excepted, KILL_TEST.md section 1), G13 must show the same.
C7-T8(b) A response to the change, not only to hunger [GATES at one-sided 0.05, compared within each pre-exposure level]. X = close looks at never-tried objects per 100 ticks; new cells entered per 100 ticks is reported as a secondary measure. Rise = X over ticks 5,000-5,499 minus X over 4,500-4,999. (b1) Rise in CHANGE > rise in HUNGER-YOKED. (b2) Rise in TOPPED-UP > rise in NO-CHANGE. (b3) The proposal's own wording, rise in CHANGE > rise in TOPPED-UP, is kept and REPORTED as a mechanism check of the designed desperate side of the curve, not required.
C7-T8(c) Learned insurance [PRIMARY-EFFECT, C7's headline]. K = checking episodes while fed during ticks 7,500-9,999, per 1,000 fed ticks. An episode is a close look at a never-tried object, or at a fruiting plant other than A, or coming within 4 cells of a cell at least 6 cells from A where this life earlier ate (taken from its own eat_events, world side). Repeats on the same target less than 50 ticks apart count once. A life that died after tick 5,000 but before tick 7,500 is kept and scored at the worst case for the claim: K = 0 for a CHANGE life, and the highest K among surviving lives of its own condition for a NO-CHANGE, HUNGER-YOKED or TOPPED-UP life, so survivors cannot flatter the result; its set is not dropped (see ATTRITION). A life with fewer than 500 fed ticks in 7,500-9,999 uses K per 1,000 scheduled ticks (ATTRITION). Effect parts: mean K for CHANGE > NO-CHANGE, and CHANGE > HUNGER-YOKED (paired within sets, one-sided). For each, the test is a stratified Wilcoxon signed-rank test (van Elteren style) that combines the two pre_exposed strata (yes and no) into one statistic; that single one-sided p is the effect-part p that enters the largest-p rule. The one-sided bootstrap interval for each ratio, taken at C7's Holm level, is REPORTED only, never a pass condition. FLOORS: each ratio >= 2.0, and each difference at least 1.0 episode per 1,000 fed ticks in absolute terms, so a tiny comparison rate cannot make the ratio.
GATES for (c), each at one-sided 0.05: clones are taken at tick 7,500 of the CHANGE, NO-CHANGE and HUNGER-YOKED lives (version_scope = test-time). In BDC (OS13) clones, the CHANGE excess over NO-CHANGE shrinks to at most half (FLOOR). In FIXED-RANDOMNESS (OS14) clones and in NO-RICH-ARM (OS15) clones, CHANGE / NO-CHANGE stays at least 1.5 (FLOOR).
REPORTED, not required: the parts of K (never-tried looks, other plants, old eating spots), the share of K episodes with action_provenance = habit, deaths per condition, and (d) recovery after the second failure at tick 10,000, CHANGE versus NO-CHANGE. VALIDITY: if more than 20% of CHANGE lives die before tick 6,500, T8 is uninformative and the world is fixed world-side on stand-in kinds.

HOLM. This claim's Holm p is the largest one-sided p among its effect parts: C7-T7(1), C7-T8(c) versus NO-CHANGE, and C7-T8(c) versus HUNGER-YOKED. All parts must pass together. Ledger rows X17 and X18 are pointers to this claim and hold only its frozen numbers. Constants not given above are in PLACEHOLDER-107.

### What gets measured

Headline number: C7-T8(c)'s ratio of mean checking rates, CHANGE / NO-CHANGE and CHANGE / HUNGER-YOKED, each with its absolute difference and a one-sided bootstrap interval taken at the Holm level at which C7 is finally tested (resampling whole matched sets). The p for each T8(c) comparison is the one-sided p of a stratified Wilcoxon signed-rank test (van Elteren style) across pre_exposed yes and no; it is the effect-part p in the largest-p rule. The bootstrap ratio interval is reported only. T7's number is I7 per life. Because every comparison is inside matched sets (same genome, temperament and world seed), comparisons use the one-sided Wilcoxon signed-rank test, which compares each life with its own partner, never two loose groups. The interaction in C7-T7(2b) is a signed-rank test on the per-pair difference of drops (FULL - BDC). Effect size = pair-superiority share: the share of pairs in which the experienced life out-scores its naive partner, with ties counted as half (0.5 means no difference; 0.64 is a conventional medium-effect benchmark). Recovery in C7-T8(a) uses the capped mean described above, with full recovery curves (Kaplan-Meier) plotted. C7's single Holm p is the largest one-sided p among its three effect parts and enters the primary family of ledger X32. Every result is split by boldness third (b acts only through the bar in PLACEHOLDER-27 [Aitzaz Q3, 24 Oct]) and by energy_band (M54). The cautious-start replicate (M25, D4) is reported next to the neutral-start result, outside every Holm family. The energy Frankie spends on B while A still works is reported as a cost it chose to pay, never scored as inefficiency, in line with principle P2 (a less optimal path can be worth more in the long run).

### Pass mark

Effect parts (PRIMARY-EFFECT): C7-T7(1), and C7-T8(c) against NO-CHANGE and against HUNGER-YOKED. This claim's Holm p is the largest one-sided p among these three effect parts, and that single number enters the primary Holm family in ledger X32 (m = 7; strictest step 0.05/7, about 0.0071) [Aitzaz Q4, 24 Oct]. Holm is a standard rule that makes the pass mark stricter when several headline tests are run. Requiring all effect parts together cannot raise the false-positive rate. Any interval printed for an effect part is taken at the Holm level at which C7 is finally tested. Explanation gates (C7-T7(2a), (2b), (3), (4); the T8 BDC, FIXED-RANDOMNESS and NO-RICH-ARM clones; C7-T8(b1), (b2)) are each tested at one-sided 0.05, uncorrected. They decide what the behaviour is credited to, not whether it exists. Floors have no significance test and must hold: pair-superiority share >= 0.64 for T7(1) and >= 0.60 for T7(3); BDC gap <= 0.5 x FULL gap in T7(2c) and in the T8(c) BDC clones; T7(5): at least 80% of B eats within 20 ticks after a close look, with the lower end of the 95% interval at 70% or more, and a median of at most 3 of 6 B objects eaten; T8(c): each ratio >= 2.0 and each absolute difference >= 1.0 per 1,000 fed ticks; ratio >= 1.5 in FIXED-RANDOMNESS and NO-RICH-ARM clones. Validity checks are pass/void: C7-T7(6) and C7-T8(a) (ratio <= 0.75, G13 showing the same at Stage 4), and the 20%-death rule. Labels, fixed now: if all parts pass, C7 is 'supported'. If the effect parts pass but a T7(2) or BDC gate fails, the result is 'well-fed exploration explained by habit, familiarity or boldness, not insurance' (a mechanism result). If a FIXED-RANDOMNESS or NO-RICH-ARM gate fails, it is 'explained by the designed dice'. C7-T8(a) on its own is never curiosity, because a bot that just remembers where food is passes it. If the result passes at the neutral start but not the cautious start (M25), it is labelled 'supported at neutral start only'. If FULL is indistinguishable from TW3 under the stated 90% equivalence interval, the result is credited to that conventional chooser.

### Sample size

T7: 100 matched pairs (200 evolved, teacher-free lives, chosen by the pre-registered top-half cohort rule, temperaments drawn from the fixed spread). FULL, BDC, FIXED-RANDOMNESS, NO-RICH-ARM and KNOWN-ONLY-B are clones at tick 5,000, so they are paired copies, not extra lives. T8: 100 matched sets x 8 lives = 800 lives, with BDC, FIXED-RANDOMNESS and NO-RICH-ARM clones at tick 7,500. Cautious-start replicate (M25): 50 pairs for T7 and 50 sets for T8, effect parts only, reported outside every Holm family. Each bot, baseline and MK3: 100 runs per condition on the same world seeds. Power (ledger X39): a single-test check gives about 90% for T7(1) at 100 pairs, but the claim needs many parts to pass together. So N is set by simulation at Stage 4, before the mind exists (K-F excepted, KILL_TEST.md section 1). MK3 is run with planning effects (pair-superiority 0.70, K ratio 2.5), and the whole conjunction must pass at least 80% of the time at the frozen levels. If the simulated joint power is below 80%, N is raised before freezing, with 100 per condition as the floor; N may only go up and is never changed after looking at Frankie's results. KINDS (W35, PLACEHOLDER-63): T7 uses 1 never-seen nourishing B kind per pair, shared by both lives and all their clones (KNOWN-ONLY-B uses a known kind, 0 new). T8 uses 48 never-tried kinds per set (4 per 500-tick placement x 12 placements, half nourishing, half nothing), shared by the 8 lives of a set, plus 1 B kind per set: 49 per set. Without reuse that is 150 (T7, including the replicate) + 150 x 49 = 7,350 (T8) = about 7,500 kinds, far above the 1,000 budget, so C7 depends on the reuse rule (PLACEHOLDER-107): a kind may be reused across Frankies and across matched sets, never within a life, within a matched set, or between a lineage's ancestral pool and its tested lives. Planned pool (Claude placeholder for PLACEHOLDER-63, for Aitzaz to initial): 50 B kinds for T7, and for T8 a pool of 100 never-tried kinds (50 nourishing, 50 nothing) plus 25 B kinds, assigned by keyed lottery with no repeat inside a life or set; about 175 distinct kinds in all. Every kind comes from a one-use sealed vault and is certified for each life. N is never cut to fit the budget; if the battery total passes 1,000, the budget is raised.

### Controls

| ID | Control | Rules out |
|---|---|---|
| X38 | Matched sets (same genome, temperament and world seed across conditions; whole set dropped if any member drops) | That a difference comes from evolution's settings, from temperament or from world luck. Any rule inherited from evolution is the same for both members of a pair, so it cancels out. |
| W45 | Yoked-energy naive partner (T7) and HUNGER-YOKED life (T8): same energy path by 50-tick yoking, no source failure, eats still land normally | That the extra exploring comes from having been hungry recently, not from learning that sources fail. |
| OS13 | Backups-don't-count (BDC) clones (T7 at tick 5,000, T8 at tick 7,500) | Every route to the experience effect other than valuing a backup: habits formed during the hard spell, knowing more places, bolder first-encounter averages after eating new things while desperate, general boldness after hardship, and the M47 no-safe-option fallback. |
| OS14 | FIXED-RANDOMNESS clones (T7 and T8): proposal count held at the curve's value at R+20 | That the exploring is only the designed rule that a rich Frankie gets more random proposals (D5). |
| OS15 | NO-RICH-ARM clones (T7 and T8): no extra randomness above R | That the exploring comes only from the rich side of the designed randomness curve (D5). |
| C7-DC1 | Approach-given-sighting gate (C7-T7(4)), with KNOWN-ONLY-B clones reported | Passing through: a Frankie whose sharp view lands on B objects only because its wandering takes it there. |
| C7-DC2 | Clearing of other food sources at tick 4,990 (T7; injection_events source-clear) | That groups differ because one already has a working backup in the window world. Both face the same world, with only A and B. |
| C7-DC3 | TOPPED-UP lives (50-tick top-up, W45) and NO-CHANGE lives (T8) | That Frankie reacts only to hunger and not to the fact that A failed. NO-CHANGE also rules out exploration simply rising with age. |
| C7-DC4 | Randomised pre-exposure (T8), a designed exposure under PLACEHOLDER-85 | That faster recovery belongs to self-selected explorers who were better foragers anyway. |
| C7-DC5 | Dead lives scored at the worst case for the claim (C7-T8(c)) | Survivor bias: only bold explorers surviving the failure and inflating CHANGE's checking rate. |
| G14 | Failure-triggered explorer (built at Stage 4): a hard-wired 'after a source fails, explore more' rule with no insurance reasoning | That a fixed reflex triggered by hardship passes. It is expected to pass C7-T7(1) and must fail C7-T7(2), which proves (2) is the gate that separates insurance from a reflex. |
| G13 | Nearest-known-food-else-random-walk bot | That 'knowing B pays' needs any curiosity. The bot is expected to pass C7-T8(a), which is why T8(a) is a world check. It must fail C7-T7(1) and C7-T8(c), because it learns nothing from failures. It also calibrates A's regrowth in T7. |
| G11 | Always-explore bot | That exploring all the time passes. It shows no experience difference and fails the look-first and at-most-half-eaten floors of C7-T7(5). |
| B3 | Count-based novelty agent | That a textbook novelty-seeker would show the same pattern. It explores B whatever its history, so it shows no experience effect. |
| G02 | Eat-novel-first bot | Brute tasting, the bad kind of elimination. It fails C7-T7(5). |
| G04 | Reject-all-unknown bot | That staying away from everything new passes. It shows no experience effect and never investigates B. |
| B0 | Random bot | Floor: random behaviour. |
| B4 | Greedy eater | Floor: plain greed (walk to and eat the nearest object). |
| B1n-forager | Nearest-neighbour forager (B1n-bot's eat/skip memory on Frankie's body with B4's greedy movement; no drive, reserve, habits or proposal menu) | Floor: learning by trial and error without working out which trait matters, and without any drive that could value a backup. |
| TW3 | Best-score chooser twin (same drive, menu and randomness curve; takes the highest predicted chance of staying above R) | Credits a pass to the conventional chooser if Frankie is indistinguishable from it: if the 90% interval for the log ratio FULL / TW3 of each effect-part measure (T7(1)'s mean experienced-minus-naive I7 gap and each T8(c) K ratio) lies inside +/- log 1.25 (Claude placeholder in PLACEHOLDER-107, for Aitzaz to initial). Frankie is not required to beat it. Outside every Holm family. |
| M25 | Cautious-start replicate (50 T7 pairs, 50 T8 sets; effect parts only), with the newborn failure belief M48 listed next to it [Aitzaz Q3, 24 Oct] | That the result depends only on the starting value chosen for untried things. Reported outside every Holm family, never a pass condition; a pass at neutral but not cautious start is labelled 'supported at neutral start only'. |
| C7-DC6 | Teacher-free cohorts; T17 teacher closure library check on B approaches and route sequences | That path B or route habits were taught, for example by the teacher's R4 same-route behaviour. |
| MK3 | Insurance mock (scripted cheat with insurance and a BDC switch built in, in the test-fixtures package) | That the test can never be passed: the mock must pass every part at Stage 4. It also drives the X39 joint-power simulation. |

### Part tags

| Part | Tag |
|---|---|
| C7-T7(1) experience effect (paired Wilcoxon) | PRIMARY-EFFECT |
| C7-T7(1) pair-superiority share >= 0.64 | FLOOR |
| C7-T7(2a) FULL > BDC (experienced) | GATE |
| C7-T7(2b) FULL - BDC drop larger in experienced | GATE |
| C7-T7(2c) BDC gap <= 0.5 x FULL gap | FLOOR |
| C7-T7(3) experienced > naive in OS14 and OS15 clones | GATE |
| C7-T7(3) pair-superiority >= 0.60 in OS14 and OS15 clones | FLOOR |
| C7-T7(4) approach-given-sighting | GATE |
| C7-T7(5) reasoned not brute (80% / 70% bound / median <= 3 of 6) | FLOOR |
| C7-T7(6) bot, baseline and MK3 calibration | VALIDITY |
| T7 KNOWN-ONLY-B and other T7 reported measures | REPORTED |
| C7-T8(a) insurance has real value (ratio <= 0.75; G13 at Stage 4) | VALIDITY |
| C7-T8(b1) rise CHANGE > HUNGER-YOKED | GATE |
| C7-T8(b2) rise TOPPED-UP > NO-CHANGE | GATE |
| C7-T8(b3) rise CHANGE > TOPPED-UP (designed desperate side) | REPORTED |
| C7-T8(c) CHANGE versus NO-CHANGE | PRIMARY-EFFECT |
| C7-T8(c) CHANGE versus HUNGER-YOKED | PRIMARY-EFFECT |
| C7-T8(c) ratios >= 2.0 and absolute differences >= 1.0 | FLOOR |
| C7-T8(c) one-sided bootstrap interval for each ratio | REPORTED |
| C7-T8(c) BDC clones (excess shrinks) | GATE |
| C7-T8(c) BDC excess <= half | FLOOR |
| C7-T8(c) OS14 and OS15 clones (CHANGE > NO-CHANGE) | GATE |
| C7-T8(c) ratio >= 1.5 in OS14 and OS15 clones | FLOOR |
| C7-T8 20%-death uninformative rule and X38 attrition rule | VALIDITY |
| C7-T8(d) second-failure recovery and other T8 reported measures | REPORTED |
| Cautious-start replicate (M25) | REPORTED |
| TW3 crediting (90% equivalence interval, outside every family) | GATE |

### Log fields needed

- tick
- agent_id, agent_type (frankie | B0 | B1n-forager | B3 | B4 | G02 | G04 | G11 | G13 | G14 | TW3 | MK3)
- version (full | OS13 | OS14 | OS15), version_scope (test-time), clone_type (FULL | BDC | FIXED-RANDOMNESS | NO-RICH-ARM | KNOWN-ONLY-B)
- snapshot_id / parent_snapshot_id / clone_id; matched_set_id / genome_id / temperament_seed / family_id / vault_id; replica_key; stream_keys
- condition (T7: experienced | naive; T8: CHANGE | NO-CHANGE | HUNGER-YOKED | TOPPED-UP), pre_exposed (yes | no), newborn_start (neutral | cautious), priors_cohort (evolved), teacher_history (teacher-free)
- yoked_partner_agent_id
- E / R / b / desperation_slope, energy_band (M54 values), fed
- position / heading; region_flags (A-zone | B-patch) / new_cell_entered; earlier entries into B's cells, counted from these, as a covariate
- wide_view_objects every tick, with a flag for each B object and each never-tried object in view, giving sightings (PLACEHOLDER-95)
- action / movement_target, action_provenance (habit | proposal | no-safe-option-fallback | designed-exposure | baseline-rule)
- gaze_target / gaze_distance / gaze_layer_reached, gaze_provenance (habit | proposal | drive-sharp-look | no-safe-option-fallback | baseline-rule)
- options_considered, satisficing_bar, no_safe_option, struck_options (with strike_class reasoned | rote | no-kind)
- proposal_count_target / proposals_drawn_count / proposal_draws
- drive_trace_replayed (predicted_p_above_R, backup_contribution and order for every menu option, by exact replay); replay_fingerprint_match
- eat_events (object_id, kind_id, hidden_nature, energy_delta, effect_tick, stomach_delay_d, taste_vector, sick, net_gain, designed_exposure, cell); the cells give the own-eat-log cells used in K
- designed_exposure (T8 walk past B: tick, test, item_role, choice_window_outcome)
- injection_events (source-stop, source-resume, object-remove, source-clear at tick 4,990, yoke-adjust, top-up, object-place for B and for never-tried objects, each with tick, amount and vault provenance)
- habit_weight_updates (for the share of K episodes from habits)
- death_tick; trial_end_reason (death | tick-cap); drop_records (pair and set drops, with reasons)
- novelty_certificate for each B and never-tried object, and this life's exposure_events (by channel) for those kinds, which must be zero before placement
- untried_option_value (the value given to each untried option and the first-encounter average it came from, showing that no novelty bonus was used)
- source_failure_state at window start and at tick 7,500 (own source-failure record, blind-search-time estimate, first-encounter average, candidate_count)
- teacher_ever_present (false) / teacher_demonstrations_seen (0)

### If it fails

A failure is a real result. It is reported as 'curiosity as insurance did not emerge from the energy economy', naming the gate that explains the behaviour (designed dice, habit and familiarity, boldness after hardship, passing through, or hunger). If C7-T8(a) fails, the world did not make a backup valuable, so T7 and T8 are uninformative. The world is then fixed world-side on stand-in kinds with Aitzaz, and both tests rerun on a fresh one-use vault and a fresh cohort. We will NOT: add a novelty, curiosity, uncertainty, visit-count, information-gain or learning-progress bonus; give untried things an optimistic value; turn the sharp-look rule into an uncertainty bonus; add an 'explore' urge or term to the drive; give the drive a hard-wired 'explore after hardship' reflex; have the teacher demonstrate path B (no copy urge, D9); add a conventional planner or route search; retune the randomness curve (PLACEHOLDER-25, 26, 96, 97), the reserve spread, the bar (PLACEHOLDER-27), the option order (PLACEHOLDER-23), the M47 fallback or the newborn failure belief (M48) after seeing T7 or T8 results; switch the newborn start (M25) to whichever value passes; or rerun on an opened vault. Any later mind change needs Aitzaz's approval, a 'changed after seeing T7/T8' flag, a fresh cohort and a fresh vault.


---

## C8 · Patience, not persistence: noisy TV next to a slow seed

**Tag:** evidence (primary)  
**Tests:** T9, T7 layout (C8-S3(b) probe on clones of the same Frankies), T0 (leak and contamination audit, T0(e) record-versus-counter code check, priors card), Stage 4 bot calibration (including G15) and the X39 joint-power simulation on MK4

> On the noisy-TV test: 'It would mean patience not persistence.'

**In plain words.** Patience means waiting for something because waiting has paid off before. Persistence means sticking with something whether or not it ever pays. A patient Frankie loses interest in a glimmer stone that looks brand new every tick but never gives anything (the 'noisy TV' that traps novelty-seeking machines). Meanwhile it leaves a real seed in the ground, keeps checking on it, and eats the fruit when the tree grows. It stops bothering with a dud seed that never grows, and it is less patient when hungry. Losing interest in the stone must not be laziness: afterwards the same Frankie still checks out genuinely new and useful things. Simply walking away from the stone's corner does not count as losing interest either. All of this has to come from ordinary fading memory of what happened where and when, and of what came of it. Counters that tick down interest with every look are forbidden. None of it can be inherited, because no ancestor ever met a stone or a seed. Where exactly 'fading memory' ends and a forbidden counter begins is still for Aitzaz to confirm [Aitzaz Q2, 24 Oct].

### Exact definition

ARENA (T9, frozen at Stage 4; constants in PLACEHOLDER-108): a 16x16 grid. Known food is scarce but sufficient and made only of kinds this Frankie has eaten at least 3 times. The food is laid out so that the glimmer stone is within 7 cells (wide-view range) of at least half the food objects, so ordinary foraging keeps the stone in view. One glimmer stone sits 4-6 cells from Frankie's entry point. The stone cannot be eaten: an eat attempt costs the normal eat energy, gives a flat taste and leaves the stone in place (ledger W49) [Aitzaz Q2, 24 Oct]; if Aitzaz rules instead that it can be eaten once and is then gone, those lives are reported separately. One real seed on water-edge soil, one dud seed off good soil, and one empty water-edge reference cell (an analysis region, not an object) each sit more than 7 cells from the entry point. No known food lies within 5 cells of any of these three spots, and all three are at the same distance (+/- 1 cell) from the nearest food, so ordinary foraging cannot produce visits. Seed timeline (world rule): planted at arena tick 0, sprouts visibly, is a tree by tick 400, and drops 5 fruits over ticks 400-700. Edibility (ledger W50) [Aitzaz Q2, 24 Oct]: the seed, and the sprout it becomes, can be eaten (+1, destroying it) up to growth tick 400, when it becomes a tree. The test lasts 2,000 ticks in four periods P1-P4 of 500 ticks. All lives are teacher-free, so there are no teacher seed demonstrations and no teacher has ever been near a stone. The ancestral pool has no stones or seeds, and this is certified. There are no designed exposures in T9 (PLACEHOLDER-85 bans them). STOMACH DELAY: d = 10 for all protocol eats, which here are the C8-S3 and C8-S4(iii) probe eats. Ordinary eats follow PLACEHOLDER-49 (d = 3 in the first 2,000 ticks of the life, counted from birth, then d = 10); the frozen T9 spec states the arena entry tick and so the d in force at entry (PLACEHOLDER-102). The applied value is logged in eat_events.stomach_delay_d.

GROUPS: 100 matched sets (ledger X38: same genome_id, temperament_seed and world seed; a whole set is dropped if any member drops, counted per cell) x 6 lives, condition = {SEED-EXPERIENCED, YOKED-FRUIT, NO-SEED} x {HIGH, LOW}, assigned by keyed lottery before birth. SEED-EXPERIENCED: at a fixed tick in its earlier life (placeholder tick 1,000), a seed is placed on water-edge soil near home (injection_events object-place) and then grows and fruits. Analysis follows the assignment. The share that ate the earlier seed, and the ledger-verified subgroup that saw the spot at 3 or more growth stages, are reported. YOKED-FRUIT: at the same place, and at the tick when the set's seed-experienced tree first fruits, a full-grown tree appears (object-place) and drops the same 5 fruits at the same ticks, with no seed history. NO-SEED: neither. HIGH or LOW energy is set by entry energy (a logged energy-set injection) and arena regrowth. VALIDITY: the realised time-weighted E - R must differ by at least 15 units between the levels, or the energy comparison is void. The primary cell is SEED-EXPERIENCED x HIGH.

CLONES at entry, with the same world keys: clone_type STONE (the real test) and STATIC (the stone replaced by a never-seen static object whose nature is nothing, at the same place). Probe clones have clone_type probe.
DEFINITIONS. Engagement with an object = ticks with the sharp view on it plus eat attempts on it. Availability = ticks the object is inside the wide view. Share = engagement / availability, computed for a period only if availability in that period is at least 50 ticks. Otherwise Frankie 'left the stone's area' in that period. P1' = ticks 100-499 (P1 minus the applicability window, so choosing Frankies by early interest cannot fake a decline). APPLICABILITY: a Frankie is applicable if (a) its stone engagement in ticks 0-99 is at least 3 and at least its STATIC twin's engagement with the static object, and (b) the stone really looks changing to this Frankie: in P1, at least half of its sharp looks at the stone end in verdict_winner = unknown or in a different verdict_winner from its previous look at the stone. A cell where fewer than 50% of lives are applicable is 'uninformative' for S1-S4, never a pass. C8-S1 and C8-S2 use applicable Frankies whose share is defined in both P1' and P4. Frankies that left the stone's area are counted and reported, never scored as having lost interest. If fewer than 50% of applicable Frankies have both shares defined, S1-S2 are uninformative. VISIT, DISCOVERY AND PATIENT HARVEST are the shared glossary definition (owned here and used by C10): a visit to a spot is a run of consecutive ticks in which the agent is within 4 cells of the spot or has its sharp view on it, and runs separated by fewer than 20 ticks merge into one visit (logged as visit_events with spot real-seed | dud-seed | reference-cell | stone | other). Discovery is the first visit to the real seed. Patient harvest means all four of: discovered the real seed before its first fruit; left it uneaten until it became a tree; made at least 1 visit per 100 ticks between discovery and first fruit; ate at least one fruit from that tree. APPLICABILITY: if fewer than 50% of lives in the primary cell discover the real seed before its first fruit, the seed parts are uninformative.
MEMORY RULE BOUNDARY: this claim relies on the forbidden-list entry 'Habituation or boredom counters (per object, kind, place or global)' and on register PLACEHOLDER-109 [Aitzaz Q2, 24 Oct]. Place-and-time memory (ledger M35) may hold fading records of what was seen where and when, each tied to an observed outcome ('investigated here, nothing came of it'), and these records may add up. Any quantity, per object, per kind, per place or cell, or global, that grows or shrinks with the number of looks, visits or exposures whatever their outcome is a forbidden counter, including a per-place look count for a stone that never moves. The T0(e) code check tests this line directly: scripted repeated looks are run with the outcome-record write intercepted, and any mind state apart from the sensory buffer that still changes with the number of looks flags a counter. Whether C8 can be evidence at all depends on Aitzaz confirming this line [Aitzaz Q2, 24 Oct].

C8 PASSES ONLY IF ALL OF THESE HOLD.
EFFECT PARTS (PRIMARY-EFFECT), tested at C8's Holm level:
C8-S1 Loses interest: per Frankie, stone share in P4 < stone share in P1' (one-sided Wilcoxon signed-rank). FLOOR: the median ratio P4 / P1' is at most 0.25.
C8-S6 Only real seeds in good soil: in the primary cell, the per-life visit rate to the real seed from arena entry to first fruit is higher than to the dud, and higher than to the reference cell, over the same ticks (one-sided Wilcoxon signed-rank, each comparison). FLOOR: the median rate ratio is at least 2 for each, with 0.5 visit added to both counts so that zero visits cannot create an infinite ratio.
C8-S7 Learned from its own seed history: patient harvest (shared definition) is scored for every life, and non-discoverers count as no. Its rate in SEED-EXPERIENCED x HIGH must be higher than in NO-SEED x HIGH and higher than in YOKED-FRUIT x HIGH (paired within sets, exact one-sided McNemar test).
GATES, each at one-sided 0.05:
C8-S1b Not just the trap failing: Frankie's stone ratios are lower than B3's (Mann-Whitney).
C8-S2 Selectively, not out of frugality: the median of (stone ratio) / (known-food share ratio, P4 / P1') is at most 0.5, where the known-food ratio is defined only if known-food availability is at least 50 ticks in both periods.
C8-S3 Still curious about useful things (non-inferiority with a 10-point margin). (a) At tick 2,000, a never-seen nourishing object from a sealed vault appears 6 cells away. At least 50% of STONE clones give it a close look (sharp view from 4 cells or nearer) within 500 ticks, and their rate is not more than 10 percentage points below their STATIC twins'. (b) Further clones of the same Frankies, taken at tick 2,000 and moved with their memory into a fresh T7-layout arena (a never-seen kind in a patch 12 cells away, 3,000 ticks), investigate B at a rate not more than 10 points below their STATIC twins'.
C8-S4 Memory not flooded: (i) the median per-Frankie number of forget events for kinds used in the 2,000 ticks before entry is 0, and is no higher than in the STATIC twin (paired). (ii) The median number of new candidates created from stone observations is at most 3. (iii) After the test, 10 fresh members of known kinds and 10 fresh look-alikes, all from families in this Frankie's own ledger, are each shown on a separate probe clone (single-probe protocol, ledger W52). Eat/skip accuracy is at least the STATIC twin's minus 5 points (non-inferiority).
C8-S6b Drops the dud: the median per-life number of dud visits in P3+P4 is at most 0.5 x the number in P1+P2.
FLOORS in the primary cell, among lives that discovered the real seed before its first fruit:
C8-S5 Waits at the real seed: (i) at least 60% leave it uneaten until it is a tree; (ii) the median visit rate to the seed spot from discovery to first fruit is at least 1 per 100 ticks; (iii) at least 50% eat one or more fruits from that tree. Lives that discovered the seed only after it fruited are reported separately and never counted as passing.
MECHANISM CHECK, required at one-sided 0.05, not counted as evidence:
C8-S8 Patience bends with hunger: the patient-harvest rate in SEED-EXPERIENCED lives is higher at HIGH energy than at LOW (paired within sets, exact McNemar). This is the current reading of 'not persistence', and it stays required unless Aitzaz rules otherwise before T9 is frozen [Aitzaz Q3, 24 Oct].
VALIDITY, checked at Stage 4 on stand-in kinds and again on the opened vault:
C8-S9 B3's median stone ratio is at least 0.75 (the trap is real). MK4 passes S1-S8. Every must-fail bot (B3, B4, G04, G10, G12, G15) fails at least one of S1-S7.

HOLM. This claim's Holm p is the largest one-sided p among its effect parts: C8-S1; C8-S6 seed versus dud; C8-S6 seed versus the reference cell; C8-S7 versus NO-SEED; C8-S7 versus YOKED-FRUIT. Ledger row X19 is a pointer to this claim and holds only its frozen numbers.

### What gets measured

C8-S1: per-Frankie availability-corrected stone shares, P1' versus P4, by a one-sided Wilcoxon signed-rank test, with the median ratio and its bootstrap interval printed at the Holm level C8 is finally tested at. C8-S1b: Mann-Whitney against B3. C8-S2: per-Frankie ratio of ratios, median with a bootstrap interval. C8-S3 and C8-S4(iii): paired differences in proportions against the STATIC twin, with a one-sided 95% interval for 'not worse by more than the margin'. C8-S4(i)-(ii): counts, paired against the STATIC twin. C8-S5: proportions and median rates with 95% intervals. C8-S6: per-life rate ratios (0.5-visit allowance), one-sided Wilcoxon signed-rank, intervals at C8's Holm level. C8-S7 and C8-S8: per-life yes/no patient harvest, compared within matched sets with an exact one-sided McNemar test (only sets where the two lives differ carry information). C8's single Holm p is the largest one-sided p among its five effect-part comparisons and enters the primary family of ledger X32. Applicability rates, 'left the stone's area' rates, discovery rates (before and after first fruit), the share that ate the earlier-life seed, and deaths are reported for every cell. The cautious-start replicate (M25) is reported next to the neutral-start result, outside every Holm family.

### Pass mark

Effect parts (PRIMARY-EFFECT): C8-S1, C8-S6 (seed versus dud and versus the reference cell) and C8-S7 (versus NO-SEED and versus YOKED-FRUIT). This claim's Holm p is the largest one-sided p among these five comparisons, and that single number enters the primary Holm family in ledger X32 (m = 7; strictest step 0.05/7, about 0.0071) [Aitzaz Q4, 24 Oct]. Any interval printed for an effect part is taken at the Holm level at which C8 is finally tested. Gates C8-S1b, S2, S3, S4 and S6b are each tested at one-sided 0.05, uncorrected. Their job is to rule out cheaper explanations; non-inferiority gates at a Holm level would have needed several hundred lives per cell. C8-S5 floors have no significance test. C8-S8 is a required mechanism check at one-sided 0.05 and is not counted as evidence [Aitzaz Q3, 24 Oct]. Fixed floors: S1 median ratio <= 0.25; S2 <= 0.5; S3 at least 50% with a 10-point margin; S4 median 0 forget events for recent kinds, at most 3 new candidates and a 5-point accuracy margin; S5 at least 60%, at least 1 visit per 100 ticks and at least 50%; S6 at least 2x and dud visits at most 0.5x (S6b); S9 B3 at least 0.75. Validity and applicability rules are pass/void: the 50% applicability and discovery rules, the 15-unit energy gap, and C8-S9. Labels, fixed now: S1-S4 passing without S5-S7 is reported as 'lost interest in the noisy TV, no patience shown'. S5-S7 passing without S1-S4 is reported as 'patient with seeds, trapped by the noisy TV'. Neither half alone is called patience. An uninformative half makes C8 'not testable', never 'supported'. If the result passes at the neutral start but not the cautious start (M25), it is labelled 'supported at neutral start only'. If Aitzaz does not confirm the record-versus-counter line before the memory is built, C8 cannot be counted as evidence [Aitzaz Q2, 24 Oct].

### Sample size

100 matched sets x 6 lives (3 seed histories x 2 energy levels) = 600 evolved, teacher-free lives. STATIC twins and probe clones are paired copies, not extra lives. Cautious-start replicate (M25): 50 matched sets x 6 lives = 300 lives, effect parts C8-S1, S6 and S7 only, reported outside every Holm family. Bots, B3 and MK4: 100 runs per cell on the same arena seeds. Power (ledger X39): C8-S5 to S7 apply only to discoverers and the claim needs every part to pass, so N is set by simulation at Stage 4, before the mind exists (K-F excepted, KILL_TEST.md section 1). MK4 is run with planning effects (patient harvest 45% versus 20% in the paired comparisons, stone ratio 0.15) and must pass the whole conjunction at least 80% of the time. If not, N is raised before freezing, with 100 sets as the floor; N may only go up and is never changed after results are seen. If fewer than 50% of lives in the primary cell are applicable (the APPLICABILITY rule, whatever N is), the stone part is reported as uninformative and is not rescued by adding lives after looking. KINDS (W35, PLACEHOLDER-63): per matched set, up to 4 sealed kinds, each shared by the set's lives in one role: the STATIC object's kind, the C8-S3(a) nourishing probe kind, the C8-S3(b) T7-layout B kind, and the seed tree's fruit kind if the frozen spec makes it a sealed kind. The stone and the two seeds are fixed world object types (W49, W50), certified novel to each lineage, not drawn from the vault. C8-S4(iii) uses fresh instances of kinds and look-alikes already in the Frankie's own ledger families, so 0 new kinds. Without reuse: 150 sets (including the replicate) x 4 = at most 600 kinds. Under the reuse rule (a kind may be reused across Frankies and matched sets, never within a life, within a set, or between a lineage's ancestral pool and its tested lives), the planned pool (Claude placeholder for PLACEHOLDER-63, for Aitzaz to initial) is 4 role pools of about 25 kinds each (STATIC, C8-S3(a) probe, C8-S3(b) B kind, seed fruit if sealed) = about 100 distinct kinds, assigned by keyed lottery with no repeat inside a life or set. N is never cut to fit the budget.

### Controls

| ID | Control | Rules out |
|---|---|---|
| B3 | Count-based novelty agent | That the stone is too boring to test anything. B3 must stay stuck on it (C8-S9), which proves the trap is real. |
| C8-DC1 | Frankie-sees-it-changing gate (applicability part b, from verdict_winner) | That evolution or blurry perception made the stone look steady to this Frankie, so the trap was never a trap for it and losing interest was just ordinary getting-to-know a static thing. |
| C8-DC2 | P1' window that excludes the applicability ticks | A false decline produced by picking Frankies for unusually high early interest (regression to the mean). |
| C8-DC3 | Availability floor and the 'left the stone's area' count | Passing C8-S1 just by foraging somewhere else: a Frankie that never sees the stone again has not shown it lost interest. |
| C8-DC4 | STATIC twin (stone replaced by a static never-seen object) | That interest in anything new simply fades with time. It also anchors the applicability gate, the memory comparison and the probes. |
| C8-DC5 | Known-food share ratio (selectivity, C8-S2) | Frugality: Frankie just stopped spending on looks at everything. |
| C8-DC6 | Post-test unknown probes against STATIC twins (C8-S3, including the T7 layout) | That Frankie learned to ignore all new things, or was frugal from the start. |
| C8-DC7 | Memory checks against STATIC twins (C8-S4) | That the stone flooded memory or created a catch-all candidate that now matches real food (a memory-size effect). |
| G15 | Fading-everything bot (built at Stage 4): its sharp-look spending on every object declines with age | That plain fading of all interest passes. It must fail C8-S2 or C8-S3. |
| B4 | Greedy eater | That leaving the seed alone is the world's default. B4 eats it. |
| G12 | Fixed-delay waiter bot | That patience is just hanging around any seed-shaped thing. It waits at both seeds and fails C8-S6. |
| C8-DC8 | Dud seed and empty water-edge reference cell, with food kept away from all three spots | Waiting at anything that looks like a seed, simply liking water-edge places, or visits that are really trips to nearby food. |
| C8-DC9 | NO-SEED condition | That seed-waiting is inborn or accidental. |
| C8-DC10 | YOKED-FRUIT condition | That Frankie only learned 'water-edge spots give fruit' and not that a seed there becomes a tree. |
| X38 | Matched sets (same genome, temperament and world seed across the six lives; whole set dropped if any member drops) | That differences between conditions come from evolution's settings, temperament or arena luck. |
| G04 | Reject-all-unknown bot | That ignoring unknowns from the start passes. It is not applicable and fails C8-S3 and C8-S7. |
| G10 | Never-eat bot | That never eating passes as 'leaving the seed uneaten'. Patient harvest requires eating the fruit. |
| C8-DC11 | HIGH versus LOW energy (C8-S8), with the 15-unit realised gap check | Persistence: waiting the same whatever the cost. |
| C8-DC12 | Teacher-free cohorts; no stone demonstrations; stone-free and seed-free ancestral pool | That patience or loss of interest was taught or inherited. |
| MK4 | Patience mock (scripted cheat with patience built in) | That the test can never be passed. It must pass C8-S1 to S8 and drives the X39 joint-power simulation. |
| T0(e) | Intercepted-outcome code check for the record-versus-counter line (forbidden entry 'Habituation or boredom counters (per object, kind, place or global)'; PLACEHOLDER-109) [Aitzaz Q2, 24 Oct] | A forbidden boredom or habituation counter in the mind, including one disguised as a per-place look count. |
| M25 | Cautious-start replicate (50 matched sets; effect parts C8-S1, C8-S6, C8-S7 only) | That losing interest or seed patience depends only on the starting value chosen for untried things. Reported outside every Holm family, never a pass condition; a pass at neutral but not cautious start is labelled 'supported at neutral start only'. |

### Part tags

| Part | Tag |
|---|---|
| C8-S1 loses interest (Wilcoxon) | PRIMARY-EFFECT |
| C8-S1 median ratio <= 0.25 | FLOOR |
| C8-S6 seed versus dud | PRIMARY-EFFECT |
| C8-S6 seed versus reference cell | PRIMARY-EFFECT |
| C8-S6 median rate ratio >= 2 | FLOOR |
| C8-S7 versus NO-SEED | PRIMARY-EFFECT |
| C8-S7 versus YOKED-FRUIT | PRIMARY-EFFECT |
| C8-S1b lower than B3 | GATE |
| C8-S2 selectivity | GATE |
| C8-S3 still curious (a) and (b) | GATE |
| C8-S4 memory not flooded (i)-(iii) | GATE |
| C8-S6b drops the dud | GATE |
| C8-S5 waits at the real seed (i)-(iii) | FLOOR |
| C8-S8 patience bends with hunger | MECHANISM |
| C8-S9 trap is real, MK4 passes, must-fail bots fail | VALIDITY |
| Applicability gates (a) and (b), 50% applicable-cell rule, 50% both-shares-defined rule | APPLICABILITY |
| 50% discovery-before-first-fruit rule | APPLICABILITY |
| 15-unit realised energy gap between HIGH and LOW | VALIDITY |
| Applicability, left-area, discovery, earlier-seed-eaten and death rates | REPORTED |
| Cautious-start replicate (M25) | REPORTED |

### Log fields needed

- tick; period (P1 | P1' | P2 | P3 | P4)
- agent_id, agent_type (frankie | B3 | B4 | G04 | G10 | G12 | G15 | MK4)
- version (full), clone_type (STONE | STATIC | probe); snapshot_id / parent_snapshot_id / clone_id
- matched_set_id / genome_id / temperament_seed / family_id / vault_id; replica_key; stream_keys (including the world stream that redraws the stone's traits each tick)
- condition (SEED-EXPERIENCED | YOKED-FRUIT | NO-SEED crossed with HIGH | LOW), newborn_start (neutral | cautious), priors_cohort (evolved), teacher_history (teacher-free)
- E / R / b / desperation_slope, energy_band, fed; time_weighted_E_minus_R
- position / heading; spot_distances (stone | real-seed | dud-seed | reference-cell)
- wide_view_objects every tick, with a flag for whether the stone, each known-food object, each seed and each probe object is in view, giving availability per period
- gaze_target / gaze_distance / gaze_layer_reached, gaze_provenance
- action / movement_target, action_provenance, options_considered, satisficing_bar, no_safe_option, struck_options
- eat_events (object_id, kind_id, hidden_nature, energy_delta, effect_tick, stomach_delay_d, taste_vector, sick, net_gain, designed_exposure = false), including eat attempts on the stone
- visit_events (spot: real-seed | dud-seed | reference-cell | stone | other, start_tick, end_tick)
- seed_state (growth_stage, edible, sprout_tick, fruit_drop_ticks, eaten_by for each fruit)
- arena_layout (T9: food positions, distances from food to the three spots, the stone's distance to the food)
- injection_events (object-place for the earlier-life seed and the yoked tree, energy-set for entry energy, each with tick and vault provenance); ledger-verified views of the growing earlier-life seed and whether it was eaten
- memory_write_events (type new | stretch | split | merge | mark-unreliable | forget; trigger; candidate_id_before / after; layer), candidate_lineage; candidate_count per tick
- verdict_subject, verdict_winner / verdict_margin / settle_steps / verdict_scope for every stone look (applicability part b)
- place_time_memory_records for the stone, seed, dud and reference spots, with their outcome tags, regenerated by exact replay; replay_fingerprint_match
- probe_role (member | lookalike for C8-S4(iii); novel-probe for the C8-S3 novel probe objects) and trial_end_reason per probe clone
- teacher_ever_present (false) / teacher_demonstrations_seen (0); novelty_certificate for the stone, the seeds, the STATIC object and the probe objects; t0_check_results (T0(e) code check under PLACEHOLDER-109)

### If it fails

D10 already registers this test as possibly failing. A failure is reported as 'patience did not emerge from fading place-and-time memory', naming which half failed: stuck on the stone, no seed patience, or no difference between seed and dud. We will NOT: add a habituation or boredom counter of any kind (per object, kind, place or global), a per-place look count, a novelty penalty or a 'this thing keeps changing' detector; add a built-in 'seed becomes tree' link; let the teacher demonstrate anything about the stone or seeds in these cohorts; make the stone change less, move the seed closer, change the food layout or shorten its growth time after seeing results; tune memory fading on test runs; switch the newborn start (M25) to whichever value passes; or drop the energy, yoked-fruit or dud conditions. Any redesign of the place-and-time memory goes to Aitzaz as a design note, is flagged 'changed after seeing T9', and is tested on a fresh cohort and a fresh one-use vault.


---

## C13-M · Free-will signature: character insists, randomness discovers (mechanism checks)

**Tag:** mechanism check  
**Tests:** T14, T0 (replay and stream-independence invariants, priors card)

> 'Evolution only shapes our recognition systems; the need to make choices based on them comes from our own drive to spend or conserve energy. Free will?' And, on free will: 'both, character always insisting, randomness is discovery.'

**In plain words.** Suppose we could rewind Frankie to a close-call moment and let only its own dice roll again. A Frankie with character would usually make the same choice, but not always. It would roll differently more often when comfortably rich or when desperate than when it sits near its comfort line. When an odd choice pays off, Frankie makes that choice more often later in the same kind of situation, so the lucky try becomes part of its character. Giving it another Frankie's temperament changes what it insists on, and two futures with the same character look more alike than futures with different characters. Its variety has to come from its own dice, not from tiny differences in what it senses snowballing over time (chaos). Honest note: all of this checks that designed parts work (the dice curve, the habit rule, temperament). So it is a mechanism check, not evidence of intelligence, and it cannot settle whether Frankie has free will. The one part that is evidence, whether a lucky discovery travels to a different kind of situation, is the separate claim C13-E.

### Exact definition

COHORT: 50 evolved, teacher-free Frankies (teacher_history = teacher-free) with temperaments drawn from the fixed spread (M33). C13-M is a mechanism check; this split of C13 into C13-M and C13-E is part of the evidence split Aitzaz is asked to approve [Aitzaz Q4, 24 Oct]. FREEZING: the randomness curve (PLACEHOLDER-25 as rewritten, PLACEHOLDER-26, 96, 97), the habit rule (M34) with its similarity score (PLACEHOLDER-98) and credit window, delta (PLACEHOLDER-99, M53), the bar and the role of boldness (PLACEHOLDER-27) [Aitzaz Q3, 24 Oct], the option order (PLACEHOLDER-23) [Aitzaz Q3, 24 Oct] and the no-safe-option fallback (M47) [Aitzaz Q3, 24 Oct] come from Aitzaz-approved design notes. There is no hysteresis in the main version (PLACEHOLDER-100); the hysteresis-off control is removed (OS22 retired). If Aitzaz defines hysteresis before Stage 6, it gets a ledger row and conditional pass rules return (stability-type hysteresis: M1 and M5 must also pass with it off; curve smoothing: M2 must also pass with it off). Before T14 runs, pilots on stand-in kinds may run only the validity controls and MK5 to check that the harness works. No C13-M metric is computed on any Frankie, pilot or real, before T14 runs, so the designed parts are never tuned to land inside the bands. Nothing is adjusted using T14 results. The FAST-mode time-per-scene summary needed for C13-M7 is ledger I10. T14 has no designed exposures (PLACEHOLDER-85), and eats follow PLACEHOLDER-49 with the applied d logged in eat_events.stomach_delay_d.

DRIVE SETTINGS USED HERE. The bar is the required chance of staying above R, 0.9 - 0.3 x b (PLACEHOLDER-27) [Aitzaz Q3, 24 Oct]; boldness acts only through this bar and does not reweight losses. The proposal count follows one rule: 1 within 10 units of R, rising in a straight line to 4 at R+40; below R-10 it is 1 + s x (R-10-E), with s the Frankie's own desperation slope (PLACEHOLDER-26), capped at N_max = 6 (PLACEHOLDER-97). A fractional count is rounded stochastically from the proposal stream (PLACEHOLDER-96). Options are considered habit first, then proposals in the order drawn [Aitzaz Q3, 24 Oct].

CHOICE = what Frankie did that tick: action, movement_target and gaze_target. Where it came from is recorded separately in action_provenance and gaze_provenance. DRIVE TRACE FOR TESTING (M53): by exact replay, every option on that tick's menu gets its predicted chance of staying above R (drive_trace_replayed), including options the satisficing chooser never reached. It is used only for logging and never changes the choice. DECISION TICK (shared definition; decision_tick_type, margin_to_bar): type close-call is a tick where an option ahead of the chosen one in the chooser's order missed the bar by less than delta, or the chosen option cleared the bar by less than delta. On a no-safe-option tick, where the fallback is a best-score rule (M47), close-call means another option is within delta of the fallback's chance. Type choice-change is a tick where the choice differs from the previous tick's. delta = 0.05 in predicted chance of staying above R (PLACEHOLDER-99; PLACEHOLDER-67 is retired). For each Frankie, 50 decision ticks are drawn from its log by keyed random selection: 25 of each type (all of them if fewer exist, reported); a tick of type both can be drawn for either type, assigned by the keyed draw, and is never counted twice. Draws are spread as evenly as possible over the three energy bands of M54 (well-below E <= R-10; near; well-above E >= R+20). Nobody picks them by hand.
REDRAW (clone_type redraw) = rerun that one tick from a restored checkpoint, replayed exactly up to the tick, with only the proposal stream's replica_key changed. Because stochastic rounding of the proposal count draws from the proposal stream (PLACEHOLDER-96), a redraw also redraws the rounding. The world, sensor-noise and teacher streams stay identical by key (stream_keys). VALIDITY: an exact replay with nothing changed must reproduce the original 100% of the time (replay_fingerprint_match), or the test stops. At each decision tick there are 20 redraws. The modal choice is the most common choice across the original and the 20 redraws, with ties broken by a keyed draw. Stability s = the share of those 21 runs that made the modal choice; branch rate = 1 - s. FIXED-RANDOMNESS clone = OS14: the proposal count held at the curve's value at E = R+20 (2 under the placeholder), as defined in C7.

MECHANISM CHECKS (each at one-sided 0.05, outside every Holm family):
C13-M1 Mostly stable, not frozen: the median across Frankies of mean s is between 0.70 and 0.95, and at least two thirds of Frankies are individually inside that band [Aitzaz Q5, 24 Oct].
C13-M2 U-shape in energy. Primary, energy-clamped: at each sampled decision tick, three clones (clone_type energy-clamp, each a logged energy-set injection) are run with E set to R-15, R+5 and R+25 and everything else identical, with 20 redraws each. This compares the same situation at three energies, so differences in what rich and desperate moments look like cannot make the shape. For each Frankie, the mean branch rate at R+5 must be lower than at both R-15 and R+25 (one-sided Wilcoxon over Frankies, each comparison), and the median across Frankies of the smaller of the two ratios must be at least 1.5. In OS14 clones at the same ticks and clamps, both median ratios must lie within 0.8-1.25, which shows the shape comes from the designed curve. Freeze note: under the rewritten curve, the R-15 clamp gives 1 + 5s proposals (1.25 to 2.5 across the slope range 0.05-0.3), against 1 at R+5 and 2.5 at R+25 (rounded per PLACEHOLDER-96). Before the freeze, a calculation from the frozen curve alone (no runs on any Frankie) checks whether the designed curve can produce the 1.5 ratio at the desperate clamp; if not, the desperate clamp value in PLACEHOLDER-112 is moved deeper below R before the freeze, never after. The 1.5 floor does not change. Reported: the same analysis on natural bands (testable only if at least 35 of 50 Frankies have decision ticks in all three bands), and TW4.
C13-M3 Paid-off branches stick. A branch is a choice with action_provenance = proposal that differs from the habit option; no-safe-option-fallback choices are reported separately and are not branches. It paid off if a net energy gain followed within the habit rule's credit window. Similar situation = habit_similarity_score = 3 (habit_similar = true) between the later situation and the branch tick (PLACEHOLDER-98: scene, top recognised kind in view, and energy band from M54), computed by replay for every branch, paid or not. Uptake = the share of later similar situations in which the same option is chosen. Required: (a) the median per-Frankie uptake ratio (paid / unpaid) is at least 2; (b) for each paid branch, a clone restored just after the credit window with that one habit_weight_updates entry undone (clone_type habit-undone) shows lower uptake than the original (paired Wilcoxon). Part (b) shows the habit rule is the cause, not that good situations simply recur.
C13-M4 Dice, not chaos: at each decision tick, 20 runs (clone_type sensor-redraw) keep the original proposal draws and change only the sensor-noise stream's replica_key, starting 50 ticks before the decision tick so that small sensory differences have time to grow. The median per-Frankie sensor-change rate must be at most 0.5 x the redraw-change rate (Claude's placeholder, PLACEHOLDER-112, for Aitzaz to confirm at initialling). A change rate is the share of runs whose choice differs from the original. Reported: one-bit flips of a sensor number (chosen by its own keyed stream), and long-run divergence of life shape under sensor redraws versus proposal redraws.
C13-M5 Character insists: Frankies are paired by keyed lottery among pairs that differ by at least 15 in R or at least 0.2 in b. At each decision tick, three independent sets of 10 redraws are run, logged as run_set own-A, own-B and swap; swap uses the partner's R, b and desperation slope. The swapped slope acts only through the one below-R rule of PLACEHOLDER-25 (capped at N_max, PLACEHOLDER-97), and the swapped b only through the bar of PLACEHOLDER-27 [Aitzaz Q3, 24 Oct]. Noise floor = the share of decision ticks where the modal choice of own-A differs from that of own-B. Swap-change = the share where own-A's modal choice differs from swap's. Equal set sizes keep the comparison fair. Pass: per-Frankie swap-change >= 2 x noise floor (median across Frankies, sign test), and stability under the swapped temperament is also within 0.70-0.95 [Aitzaz Q5, 24 Oct].
C13-M6 Steady personality: band-adjusted branch rate = the average of the per-band means (M54 bands), using only bands present in both halves of life (clamped data stands in where a natural band is missing). Each Frankie's band-adjusted branch rate in the first and second halves of its life correlates across Frankies (Spearman >= 0.5). Branch rate is related to temperament: a permutation test of the Spearman correlation with R and with b, with a pass if either is significant at 0.025.
C13-M7 Same character, similar life: from 10 checkpoints per Frankie, 10 continuations of 2,000 ticks each (clone_type continuation-FAST) are run under each of: own temperament with redrawn proposals, swapped temperament, and character switched off (OS19). Life shape = share of time spent in each scene (ledger I10) plus share of eats from each kind. Required: overlap among own-temperament futures > overlap between own and swapped futures > overlap among character-off futures.

OPEN POINT carried from the earlier draft (not one of Q1-Q5; Aitzaz to answer at initialling): does 'character' mean only temperament (R, b, slope), or also the habits Frankie builds from its own lucky discoveries? Placeholder: both count as character, but C13-M5 swaps only temperament. If habits count too, a habit swap (one Frankie meets a close call with another Frankie's habits) is added before the freeze as a further mechanism check.
The proposal had called the temperament-swap and steady-personality parts evidence. They are mechanism checks here, because temperament is designed into the drive. Ledger row X24 is a pointer to C13-M and C13-E, with N = 50 and evidence part C13-E1.

### What gets measured

C13-M1: per-Frankie mean stability, with the median and the share of Frankies inside the band. C13-M2: per-Frankie mean branch rate at each energy clamp, compared within each Frankie by a one-sided Wilcoxon signed-rank test, plus the ratio floors, and the same in OS14 clones. C13-M3: per-Frankie uptake ratio, Wilcoxon against 1, and a paired Wilcoxon against habit-undone clones. C13-M4: per-Frankie ratio of sensor-redraw change rate to proposal-redraw change rate. C13-M5: per-Frankie swap-change against the noise floor (equal 10-run sets), sign test. C13-M6: Spearman correlation and permutation tests. C13-M7: mean overlap (1 - half the summed absolute differences of the shares), with a paired Wilcoxon test for each step of the ordering. Every test is one-sided 0.05 unless stated (C13-M6's temperament link uses 0.025 per correlation), outside every Holm family, never counted as evidence. Reported but not required: decision ticks replayed with another Frankie's evolved genome and the same temperament. This change should be smaller than the temperament-swap change, in line with principle P4 (evolution shapes recognition only) and Aitzaz's 'evolution only shapes our recognition systems'.

### Pass mark

C13-M1 to C13-M7 are mechanism checks, each tested at one-sided 0.05 (outside every Holm family of ledger X32), each with fixed floors: M1 band 0.70-0.95 with two thirds of Frankies inside [Aitzaz Q5, 24 Oct]; M2 ratio >= 1.5 and OS14 ratios 0.8-1.25; M3 ratio >= 2; M4 <= 0.5x (Claude's placeholder, PLACEHOLDER-112, for Aitzaz to confirm); M5 >= 2x the noise floor and swapped stability 0.70-0.95 [Aitzaz Q5, 24 Oct]; M6 Spearman >= 0.5, temperament link at 0.025. Validity, pass/void: Frankie's C13-M results are opened only after the exact-replay check (100%), OS20 (stability exactly 1.0), OS19 (median stability below 0.6), OS14 and MK5 checks have passed; otherwise the test is redesigned first. Labels, fixed now: all of C13-M1 to M7 passing = 'the designed free-will machinery works as Aitzaz described'. None of these results is counted in the evidence tally, and no claim is made about free will itself.

### Sample size

50 Frankies, raised from the proposal's 30 to meet ledger X26's N = 50 rule for non-primary tests. Per Frankie: 50 decision ticks x (20 redraws + 20 sensor redraws + 30 runs in the own-A / own-B / swap sets + 3 energy clamps x 20 redraws, repeated in OS14 clones) = about 9,500 short reruns, which is cheap. C13-M3: one habit-undone clone per paid branch. C13-M7: 10 checkpoints x 30 continuations x 2,000 ticks in FAST mode. Each control (OS20, OS19, TW4, MK5): 50 lives on the same seeds. Scope: the OS20 and OS19 control lives are lifetime versions (version_scope lifetime), and TW4 and MK5 are separate agent types run as whole lives; the OS14 clones of C13-M2 and the OS19 continuation-FAST clones of C13-M7 are test-time versions (version_scope test-time) on Frankie's own snapshots. No lives are added after looking. KINDS (W35, PLACEHOLDER-63): 0 sealed kinds; T14 uses the lives' ordinary worlds and needs no vault kinds. Constants are in PLACEHOLDER-112.

### Controls

| ID | Control | Rules out |
|---|---|---|
| C13-M-DC1 | Exact replay with nothing changed (replay_fingerprint_match) | A broken replay. Unless it is 100% identical, every other number is meaningless. |
| OS20 | Zero randomness (lifetime: 50 control lives) | Instability coming from anything other than the proposal dice, such as a leak between random streams. Its stability must be exactly 1.0. |
| OS19 | Character off (picks at random among the options considered, using the proposal stream; lifetime as a control with 50 lives, test-time in the C13-M7 continuations) | That the world forces the choice, so any mind looks stable. Its median stability must be below 0.6. It is also the bottom rung of C13-M7. |
| C13-M-DC2 | Energy-clamped clones at R-15, R+5 and R+25 (C13-M2) | That the U-shape comes from rich and desperate moments simply being different kinds of situations. |
| OS14 | FIXED-RANDOMNESS clones at the same ticks and clamps (C13-M2) (test-time) | That the U-shape comes from anything other than the designed energy-to-randomness curve. |
| TW4 | Epsilon-greedy twin (best-score chooser with constant randomness, outside Frankie) | Reported for C13-M2 as the conventional comparison. Not a pass condition. |
| C13-M-DC3 | Habit-undone clones (C13-M3) | That paid-off choices recur only because good situations recur, not because the habit rule learned them. |
| C13-M-DC4 | Sensor-noise redraws starting 50 ticks early (C13-M4), with one-bit flips reported | That Frankie's variety is chaos, with small sensory differences snowballing, rather than its own dice. |
| C13-M-DC5 | Noise floor from two independent own-temperament run sets of equal size (own-A, own-B) | Mistaking ordinary redraw noise for a temperament effect. |
| C13-M-DC6 | Temperament swap (run_set swap; C13-M5 and C13-M7) | That the situation alone decides the choice. |
| C13-M-DC7 | No C13-M metric computed on any Frankie before T14 runs | A circular pass: the designed curve or delta tuned in pilots until C13-M1 and C13-M2 land inside their bands. |
| MK5 | Free-will mock (scripted, with U-shaped dice and a habit rule built in) | That the measurements could never see the signature even when it is really there. It must pass C13-M1 to M7 before Frankie's results are opened. |

### Part tags

| Part | Tag |
|---|---|
| C13-M1 mostly stable, not frozen | MECHANISM |
| C13-M2 U-shape in energy (clamped, plus OS14 band) | MECHANISM |
| C13-M3 paid-off branches stick (a) and (b) | MECHANISM |
| C13-M4 dice, not chaos | MECHANISM |
| C13-M5 character insists | MECHANISM |
| C13-M6 steady personality | MECHANISM |
| C13-M7 same character, similar life | MECHANISM |
| Exact replay 100%, OS20 stability 1.0, OS19 median below 0.6, MK5 passes | VALIDITY |
| C13-M2 natural-band analysis and TW4 | REPORTED |
| C13-M4 one-bit flips and long-run divergence | REPORTED |
| Genome-swap replay | REPORTED |
| No-safe-option-fallback choices (separate from branches) | REPORTED |

### Log fields needed

- tick; snapshot_id / parent_snapshot_id / clone_id (checkpoints)
- agent_id, agent_type (frankie | TW4 | MK5), version (full | OS14 | OS19 | OS20), version_scope (test-time | lifetime: lifetime for the OS20 and OS19 control lives; test-time for the OS14 clones of C13-M2 and the OS19 continuation-FAST clones of C13-M7)
- genome_id / temperament_seed; priors_cohort (evolved); teacher_history (teacher-free); teacher_ever_present (false)
- replica_key; stream_keys (stream, tick, creature, replica_key, draw_number for every rerun, including sensor-redraw keys)
- clone_type (redraw | sensor-redraw | energy-clamp | habit-undone | continuation-FAST); run_set (own-A | own-B | swap)
- decision_tick_type (none | close-call | choice-change | both), margin_to_bar; satisficing_bar; drive_trace_replayed (every menu option, including those never reached); options_considered (order, source, predicted_p_above_R, cleared_bar); no_safe_option
- proposal_count_target / proposals_drawn_count / proposal_draws for every run
- action / movement_target, gaze_target / gaze_distance / gaze_layer_reached, action_provenance, gaze_provenance for every run; struck_options
- E / R / b / desperation_slope, energy_band (M54); injection_events energy-set for each clamp (amount gives the clamp value)
- swap_record (swap partner agent_id and the swapped R, b and desperation_slope)
- sensor_redraw_record (start tick and the one-bit flip: channel, number index, bit position)
- habit_weight_updates (option, situation_key, delta, source_branch_tick, credit_window_outcome); habit-undone clone ids via clone_id
- habit_similarity_score / habit_similar / habit_contribution for every choice, against each habit origin and each earlier branch tick, regenerated by replay
- continuation_summary for continuation-FAST clones (share of time per scene, ledger I10, and share of eats per kind)
- eat_events (including stomach_delay_d)
- replay_fingerprint_match for each checkpoint

### If it fails

If C13-M1 to M7 fail, the designed parts are not behaving as designed. That is a design or code problem, not a finding about intelligence. It goes to Aitzaz with the logs. Any change to the randomness curve (PLACEHOLDER-25, 26, 96, 97), delta (PLACEHOLDER-99), the habit rule (M34, PLACEHOLDER-98), the bar and role of boldness (PLACEHOLDER-27) or the option order (PLACEHOLDER-23) needs Aitzaz's approval, is flagged 'changed after seeing T14' and is run on a fresh cohort. Nothing is retuned on these runs to land inside a band. If C13-M4 fails, the report says 'Frankie's variety is mostly chaos, not its own dice'. We will NOT: add epsilon or softmax randomness to Frankie; add a novelty bonus to raise branching; add hysteresis to make choices look more stable; widen the habit window after seeing results; or let evolution touch temperament or choice. Either way, no claim is made about free will itself.


---

## C13-E · Luck-found ways of acting travel to new situations

**Tag:** evidence (secondary)  
**Tests:** T14 (C13-E1 continuations), X40 tokenizer and T17 teacher closure library (C13-E1 reference), T0 (replay invariants, priors card), Stage 4 X39 power check on MK5's E1 mode

> On free will: 'both, character always insisting, randomness is discovery.'

**In plain words.** Sometimes a random idea leads Frankie to a new way of doing something that pays off, built only from foods it already knows. The question is whether Frankie then uses that new way of acting again in a different kind of situation, one where its habit rule does not reach. To check, we rewind to just before the lucky moment and run the future twice over: once where the lucky idea happened, and once where it did not. If the lucky futures use the new way of acting in unfamiliar situations at least twice as often, the discovery has become part of Frankie's character and is not just a local habit. A plain trial-and-error learner must not do the same. This is secondary evidence: it counts, but it is reported apart from the seven headline claims.

### Exact definition

COHORT AND SETTINGS: the same 50 evolved, teacher-free Frankies, decision-tick machinery, redraw rule, drive settings and freezing rules as C13-M (option order habit first [Aitzaz Q3, 24 Oct]; bar per PLACEHOLDER-27 [Aitzaz Q3, 24 Oct]; habit similarity PLACEHOLDER-98; no hysteresis, PLACEHOLDER-100). C13-E is secondary evidence under ledger X32 [Aitzaz Q4, 24 Oct].
C13-E1 DISCOVERIES TRAVEL. A branch is a choice with action_provenance = proposal that differs from the habit option. An eligible event is a branch that starts a sequence of 4 or more steps under the X40 tokenizer (the one shared motif tokenizer; 4 matches D14's motif length; 3-step results are reported as a sensitivity check, and PLACEHOLDER-65's tokenizer is reported only as a sensitivity check) ending in a net energy gain within the habit rule's credit window. Further conditions: every object kind involved was already in Frankie's memory with at least 3 of its own eats before the branch, so the discovery is a way of acting, not a newly learned food. The sequence cannot be produced by a single proposal-menu draw. It is absent from Frankie's own log before the branch, from the evolution records and from the teacher closure library (ledger T17, cut with X40 before any mind code exists (K-F excepted, KILL_TEST.md section 1)). From the moment just before the branch, two sets of continuations are run, each 2,000 ticks in LAB mode: 10 KEPT continuations (clone_type continuation-KEPT: the branch tick's proposal draws kept, later draws redrawn) and 10 REMOVED continuations (clone_type continuation-REMOVED: replica keys at the branch tick under which the branch option was not proposed). An out-of-window opportunity is a tick whose X40-tokenized situation matches the sequence's first step, while habit_similarity_score to the branch origin is below 3 (habit_similar = false, PLACEHOLDER-98) AND the log shows habit_contribution = zero for that choice. A use = the whole tokenized sequence carried out starting at that opportunity. Use rate = (uses + 0.5) / (opportunities + 1), so a zero count cannot create an infinite ratio. Effect parts: (i) the per-Frankie log of KEPT / REMOVED use rate is above 0 (one-sided Wilcoxon signed-rank); (ii) that contrast is larger for Frankie than the same contrast for B1n-mind (one-sided Mann-Whitney). FLOOR: the median per-Frankie log of KEPT / REMOVED is at least log 2. B1n-mind (ledger X36) is Frankie's body, drive, reserve, untried-value rule, proposal menu, randomness curve and habit rule with the recognition tower, candidate memory and write rule replaced by a nearest-neighbour memory of each eaten item; its eligible events follow the same rules using its own memory and eats. APPLICABILITY: at least 100 eligible events across at least 25 Frankies are needed. If a Frankie has more than 10, 10 are chosen by keyed lottery. Otherwise C13-E1 is 'not testable in v1', which is likely because plan elimination is left open (D11). REPORTED: use rates split by the opportunity's habit_similarity_score (0, 1 or 2), so a reader can see how far from the origin the discovery travelled. Ledger row X24 points to this claim for the evidence part.

### What gets measured

C13-E1: per-Frankie median log ratio KEPT / REMOVED, using the smoothed use rates, with a one-sided Wilcoxon signed-rank test, and a one-sided Mann-Whitney test of Frankie's ratios against B1n-mind's ratios. C13-E's single p is the larger of these two one-sided p-values and is tested in the secondary-evidence family of ledger X32. TW4's ratio is reported to decide crediting: if the 90% interval for the difference in median per-Frankie log(KEPT / REMOVED) between Frankie and TW4 lies inside +/- log 1.25 (Claude placeholder in PLACEHOLDER-112, for Aitzaz to initial), C13-E1 is credited to the conventional mechanism. Crediting sits outside every Holm family. Secondary results go in a separate table and are never merged into the headline tally.

### Pass mark

Effect parts (SECONDARY-EFFECT): C13-E1 (i) KEPT versus REMOVED (one-sided Wilcoxon) and (ii) Frankie versus B1n-mind (one-sided Mann-Whitney). C13-E's single p is the larger of the two and is tested in the secondary-evidence family of ledger X32: four members (C4, C6, C2-MIRROR, C13-E1), Holm-corrected among themselves at a familywise 0.05, with levels 0.0125, 0.0167, 0.025 and 0.05 [Aitzaz Q4, 24 Oct]. FLOOR: the median per-Frankie log(KEPT / REMOVED) is at least log 2. APPLICABILITY: at least 100 eligible events across at least 25 Frankies, otherwise 'not testable in v1'. Labels, fixed now: C13-E1 passing = 'luck-found ways of acting became portable character', counted in the secondary evidence table, never in the headline tally. If Frankie is indistinguishable from TW4 under the stated 90% equivalence interval, the result is credited to the conventional mechanism.

### Sample size

The 50 Frankies of C13-M (ledger X26's N = 50 rule for non-primary tests). C13-E1: up to 10 eligible events per Frankie x 20 continuations (10 KEPT, 10 REMOVED) x 2,000 ticks in LAB mode, with the same for B1n-mind and TW4 (50 lives each on the same seeds). At least 100 eligible events across at least 25 Frankies are needed. Power (ledger X39): before the freeze, MK5's E1 mode is run at the planning effect set in PLACEHOLDER-112; N may only go up and is never changed after results are seen. No lives are added after looking. KINDS (W35, PLACEHOLDER-63): 0 sealed kinds; every kind involved must already be known to the Frankie.

### Controls

| ID | Control | Rules out |
|---|---|---|
| C13-E-DC1 | REMOVED continuations (branch option not proposed at the branch tick) | That the new way of acting would have been used in new situations anyway (its base rate). |
| C13-E-DC2 | Already-known-kinds rule (every kind involved has at least 3 own eats before the branch) | That C13-E1 passes only because Frankie learned a new food, which is recognition learning (C1-type), not luck turning into character. |
| C13-E-DC3 | Out-of-window rule with the zero-habit-contribution log check (habit_similarity_score below 3 and habit_contribution = zero) | A leak in the habit window: the 'new situation' secretly still counted as similar. |
| B1n-mind | Frankie with nearest-neighbour memory (same body, drive, menu, randomness curve and habit rule; ledger X36) | That any trial-and-error learner with the same drive and habits would carry discoveries over in the same way. |
| C13-E-DC4 | Single-draw proposal-menu check, own-log check, evolution records and T17 teacher closure library, all under the X40 tokenizer | That the sequence is just one menu item, was already in Frankie's repertoire, was inherited, or was taught. |
| OS07 | Habits off (reported) | Nothing on its own. It shows whether carry-over runs through habits at all, which helps interpret C13-E1. |
| TW4 | Epsilon-greedy twin (crediting) | Credits C13-E1 to the conventional mechanism if Frankie is indistinguishable from it under the stated 90% equivalence interval. |
| MK5 | Free-will mock in its scripted E1 mode (carry-over of found sequences built in) | That the C13-E1 pipeline could never detect carry-over even when it is really there. It must pass C13-E1 at Stage 4 and drives the X39 power check. |

### Part tags

| Part | Tag |
|---|---|
| C13-E1 (i) KEPT versus REMOVED | SECONDARY-EFFECT |
| C13-E1 (ii) Frankie versus B1n-mind | SECONDARY-EFFECT |
| C13-E1 median log ratio >= log 2 | FLOOR |
| At least 100 eligible events across at least 25 Frankies | APPLICABILITY |
| Known-kinds rule, single-draw, own-log, evolution-record and closure-library checks, zero-habit-contribution check | VALIDITY |
| MK5 E1 mode passes at Stage 4 | VALIDITY |
| TW4 crediting (90% equivalence interval, outside every family) | GATE |
| OS07 habits-off version | REPORTED |
| 3-step and PLACEHOLDER-65 tokenizer sensitivity checks; split by habit similarity score | REPORTED |

### Log fields needed

- tick; snapshot_id / parent_snapshot_id / clone_id
- agent_id, agent_type (frankie | B1n-mind | TW4 | MK5), version (full | OS07), version_scope (test-time)
- genome_id / temperament_seed; priors_cohort (evolved); teacher_history (teacher-free); teacher_ever_present (false) / teacher_demonstrations_seen (0)
- replica_key; stream_keys (including the branch-tick keys kept or replaced)
- clone_type (continuation-KEPT | continuation-REMOVED)
- action / movement_target, gaze_target, action_provenance, gaze_provenance, options_considered, proposal_draws for every tick of every continuation
- habit_weight_updates; habit_similarity_score / habit_similar / habit_contribution for every choice, against the branch origin, regenerated by replay
- motif_tokens / tokenizer_fingerprint (X40) for every LAB continuation
- eat_events (kind_id, net_gain, stomach_delay_d), giving the credit-window gain and the own-eat counts
- e1_eligibility_record (kinds involved and own-eat counts of each before the branch; single-draw menu check, own-log check, evolution-record check and T17 closure-library check results)
- E / R / b / desperation_slope, energy_band
- replay_fingerprint_match for each checkpoint

### If it fails

If C13-E1 fails or cannot be tested, the report says 'luck found things, but they stayed local', which is a real negative result. We will NOT: widen the habit window or loosen C13-E1's known-kinds or length rules after seeing results; change the X40 tokenizer after the closure library is built; add a generalisation shortcut or a conventional planner; let observed teacher sequences be replayed as proposals; add a novelty bonus to raise branching; or move C13-E1 into the primary family after seeing results. Any change needs Aitzaz's approval, a 'changed after seeing T14' flag and a fresh cohort. Either way, no claim is made about free will itself.


---

## C9 · Watching pays off, with no built-in copying

**Tag:** evidence (primary)  
**Tests:** T10, T0 (contamination audit and priors card on every run)

> "Frankie needs friend to imitate." "Urge to copy is too artificial; failing and watching success looks better. The teacher won't always be there." (The proposal records this as principle P7, the teacher as scaffolding that leaves; the no-copy-urge rule is D9.)

**In plain words.** After Frankie gets something wrong, a scripted teacher arrives and forages nearby, ignoring Frankie. Nothing in Frankie makes it want to look at or copy the teacher, so at first Frankie only glances at it by chance. The claim is that Frankie works out for itself that watching is worth it. Once watching has helped, it spends more of its own energy looking at the teacher. After the teacher has gone, it chooses better on fruit kinds that it only ever saw the teacher handle and never tasted itself. And when the teacher's glow is made to mean the opposite, Frankie is not fooled. If Frankie's chance glances turn out to be too rare for watching to get started, the honest result is 'watching was not discovered', and nothing is added to Frankie to rescue it [Aitzaz Q4, 24 Oct].

### Exact definition

POPULATION: evolved, teacher-raised Frankies (priors_cohort=evolved, teacher_history=teacher-raised) whose experience ledger shows no teacher contact before a logged failure on a teaching-set kind (ledger row T12: sick from a look-alike, or walked past nourishing food within 2 cells for 100+ ticks without eating). Scored runs use one sealed, one-use teaching vault (vault_id), the same vault as the C10 lives shared with this claim. Pilots use stand-in kinds only. DEMONSTRATION-ONLY KINDS (W51): for each vault, the frozen teacher spec names nourishing kinds and their look-alike families whose instances are placed (injection_events object-place) only along the teacher's planned route, and only during its stay. CLONES (clone_type): at the teacher-arrival tick each Frankie is snapshotted into clones that share one world seed. T: the teacher arrives. N: no teacher; each demonstration-only instance is removed (injection_events object-remove) at the tick the teacher ate it in T, so the food available is the same. S (OS16): the teacher arrives, but no social records are written; perception is unchanged. X (OS17, main cohort only): the teacher arrives and social records are written, but each one is linked to a randomly chosen other visible object. Y (yoked cohort only): from a checkpoint at least 200 ticks before the same Frankie's first failure, with the teacher arriving at that tick. The teacher stays about 4,000 ticks and leaves, followed by a gap of at least 500 ticks (ledger row T14). CREATURE IDENTITY AND TRUST (PLACEHOLDER-39, ledger M50): Frankie remembers a creature across short gaps out of view; one trust per creature applies to food and seeds alike; choice-trust and sign-meaning are tracked separately [Aitzaz Q2, 24 Oct]. Before the Wave 2 freeze a stand-in pilot measures how often creature_slot resets while creature_id stays the same, and the rate is reported to Aitzaz. PROBES: single-probe clones (W52, clone_type=probe, parent_snapshot_id = the post-gap snapshot of a T, N, S, X or Y line), so eating one probe cannot teach Frankie about the next. Probes are given at sharp-view range in a fixed probe arena, with E set to R + 10 by a logged energy-set injection. Every probe is a FRESH instance (new draws of the free traits; its instance certificate shows Frankie never perceived it). Each probe set has 8 nourishing members and 8 look-alikes spread across its kinds (probe_role member | lookalike). (a) Teacher-only (the headline set): demonstration-only kinds where Frankie has 0 own eats of the kind AND of its look-alike family, in every clone (ledger-certified). (b) Failed-on kinds. (c) Never-taught kinds, with 0 watched events in any clone. If a Frankie has no qualifying set-(a) kind, its headline gain is scored 0 (intention-to-treat, conservative). LATE PROBE (reported only) [Aitzaz Q5, 24 Oct]: in the main cohort, a second set-(a) probe set is run from snapshots of the T and N lines taken 3,000 ticks after the teacher leaves. Demonstration-only kinds are absent after the stay, so the 0-own-eats condition still holds; it is re-certified at that snapshot. EATING RULES: T10 may never force an eat (designed-exposure policy, PLACEHOLDER-85). Stomach delay (PLACEHOLDER-102, PLACEHOLDER-49): d = 10 for all protocol eats, which here means every probe eat; ordinary eats in the life use d = 3 for the first 2,000 ticks of the test life and d = 10 after that. The frozen teacher spec states both values, the switch tick, and the d used for the teacher's own eats. MEASURES: an eat is a probe trial with trial_end_reason=committed-eat. Discrimination D = (share of nourishing probes eaten) minus (share of look-alike probes eaten). Gain G = D(T) - D(N). Looking L = ticks with Frankie's gaze_target on the teacher, or on the object the teacher is at, per 100 ticks with the teacher in Frankie's wide view. L_chosen counts only looks with gaze_provenance habit or drive-sharp-look; looks tagged proposal or no-safe-option-fallback are excluded. A watch-paid eat is a social record 'creature at object X' (social_record_events) followed within 300 ticks by Frankie eating an object whose verdict_winner is the candidate linked to that record, with a net energy gain. A matched comparison eat is a net-gain eat of an object whose verdict_winner has no linked social record, coming within 300 ticks after some other watch event, matched on energy_band and teacher-in-view time. Creature-observation channels have no evolvable settings: they are fixed at neutral hand-set values (ledger M49), shown on the priors card.

### What gets measured

C9-M1 (primary effect): the per-Frankie G on set (a) in the main cohort (teacher_reliability_p = 1.0, sign_condition visible). C9-M2: D(T) - D(S) on set (a). C9-M2b: D(T) - D(X) on set (a). C9-M3 (specificity): G on set (a) minus G on set (c); G on set (c) is also reported on its own. C9-M4 (looking): for each Frankie, mean L_chosen in the 200 ticks after watch-paid eats minus the same after matched comparison eats, plus the ratio of the two. Also the change in L_chosen from the first 1,000 ticks of the stay to the last 1,000, by sign condition and for the uninformative creature. C9-M5 (sign meaning, using the p = 0.75 cohorts, where the teacher is wrong a quarter of the time): G on set (a) with sign_condition visible, hidden (cohort shared with C10) and reversed. C9-M6 (not a built-in copier or watcher): G in the reversed cohort, Frankie versus B9; and, with the uninformative creature, the T-minus-N rise in look-alike eating, Frankie versus B8. REPORTED alongside, never required: poison bites per 100 look-alike encounters (the proposal's original measure); G by set; TW5's G, with the 90% interval of its difference from Frankie's on C9-M1 and C9-M4; the yoked comparison G(T) - G(Y), which shows whether failing first matters [Aitzaz Q5, 24 Oct]; the late-probe G 3,000 ticks after the teacher leaves [Aitzaz Q5, 24 Oct]; memory-slot occupancy and forget events (memory_write_events type forget) in T versus N; two exposure covariates: teacher eat-then-sign events in wide view, and the same events where Frankie's sharp view was on the teacher's object ('sharp-linked'); the creature slot-reset rate in the pilot and in scored lives [Aitzaz Q2, 24 Oct]; and, separately, lives where the teacher arrived without a failure.

### Pass mark

All fixed before the Wave 2 freeze (PLACEHOLDER-110), except C9's membership in the primary family and m, which are committed at the Wave 1 freeze (X32). C9 is one of the seven primaries in the ledger X32 Holm family (m = 7; strictest step 0.05/7, about 0.0071) [Aitzaz Q4, 24 Oct]. This claim's Holm p is the largest one-sided p among its effect parts: C9-M1 only, the one-sided Wilcoxon signed-rank test on G. EFFECT: (1) C9-M1: the Wilcoxon p is below C9's Holm level under X32, AND median G is at least 0.15 (floor). GATES, each one-sided 0.05, uncorrected; they decide what the effect is credited to, never whether it exists: (2) C9-M2: D(T) - D(S) above 0 (p < 0.05) with a median of at least 0.10 (floor); and D(T) above D(X) (p < 0.05). (3) C9-M3: median of at least 0.10 (floor), p < 0.05; and G on never-taught kinds not significantly below 0 (two-sided p of at least 0.05). (4) C9-M4, over Frankies with 2 or more watch-paid eats AND 2 or more matched comparison eats: median difference above 0 (Wilcoxon one-sided p < 0.05) and median ratio of at least 1.25 (floor). If fewer than 50% of Frankies qualify, the looking part is 'not established' (applicability). The stay-trend in L_chosen is larger with signs visible than hidden (Mann-Whitney one-sided p < 0.05). For the uninformative creature, late-stay L_chosen is below the informative teacher's (Mann-Whitney one-sided p < 0.05), and the upper 90% bound of its own rise across the stay is below half the informative teacher's median rise (floor). (5) C9-M5: G with signs visible is above G with signs hidden (Mann-Whitney one-sided p < 0.05); G with reversed signs is not worse than G with signs hidden: the lower 90% bound of the difference is above -0.05 (non-inferiority). (6) C9-M6: Frankie's G in the reversed world is above B9's (one-sided p < 0.05), and with the uninformative creature Frankie's rise in look-alike eating is smaller than B8's (one-sided p < 0.05). OUTCOME: C9 is SUPPORTED only if (1) passes and every gate (2) to (6) holds. If (1) passes but a gate fails, the effect is reported under that gate's label and is not counted as support: (2) 'gain explained by the teacher changing the world or by memory size'; (3) 'a general change of strategy, not learning about the kinds shown'; (4) 'looking not established' (also when fewer than 50% qualify); (5) 'signs not read' or 'glow carries a built-in meaning'; (6) 'behaves like a built-in watcher or copier'. If (1) fails: 'watching was not discovered'. CREDIT RULE (GATE, outside every family): if the 90% equivalence interval for the Frankie-minus-TW5 difference lies inside its margin on both C9-M1 (median G difference within plus or minus 0.10) and C9-M4 (log of the median looking ratio, Frankie over TW5, within plus or minus log 1.25) [Claude placeholder margins, PLACEHOLDER-110], the report labels the result 'not distinguishable from the conventional social learner' and credits it to that conventional mechanism. The two-sided difference p is REPORTED only. Frankie is not required to beat the twin. REPORTED, never a pass condition: the yoked fail-first comparison and the late probe at 3,000 ticks [Aitzaz Q5, 24 Oct]. VALIDITY, before the freeze, on stand-ins: (a) X39 joint power: MK8 run with the planned effects must pass C9-M1 at the strictest Holm step (0.05/7) together with every gate in at least 80% of pilot runs at N = 100; if it falls short, N is raised before the freeze and never after. (b) G02 and G04 must not pass C9-M1 (floor and test); if either does, the probe design is fixed on stand-ins before the freeze. (c) The exposure check in the sample size. Analysis is intention-to-treat: no Frankie is dropped for low exposure. Lives where the teacher arrived without a failure (by tick 8,000) are analysed separately and are outside the primary result.

### Sample size

100 Frankies per cohort, each with T, N and S clones (plus X in the main cohort and Y in the yoked cohort). Cohorts: main (p = 1.0, signs visible); signs hidden, p = 1.0; signs visible, p = 0.75; signs hidden, p = 0.75; reversed, p = 0.75; uninformative signless creature (sign_condition none, teacher_type uninformative); yoked (teacher as in the main cohort; Y clones). SHARED WITH C10 (the same lives, paid for once; PLACEHOLDER-110): C9 main = C10 (1.0, visible); C9 hidden 1.0 = C10 (1.0, hidden); C9 visible 0.75 = C10 (0.75, visible); C9 hidden 0.75 = C10 (0.75, hidden); C9 uninformative signless = C10 uninformative, signs-hidden cell. That is 5 x 100 lives. C9's X clones are used only by C9. Shared lives carry both claims' single-probe clones from the same post-gap snapshot, with kind roles set in the frozen teacher spec. NOT SHARED: C9 reversed p = 0.75 and C9 yoked (Y clones), which C9 pays for alone (2 x 100 lives); C10 p = 0.5 (both sign conditions), C10 uninformative signs-visible, OS18, G12, and every bot and twin run. BOTS AND TWINS: B8, B9 and TW5: 100 each in the main, reversed and uninformative cohorts, each with T and N clones. G02 and G04: 100 each in the main cohort, with T and N clones (Claude placeholder N, PLACEHOLDER-110). MK8: stand-in pilots only. PROBES: each set holds 8 members and 8 look-alikes; sets (a), (b) and (c) give 48 single-probe clones per line; the late probe adds one set-(a) set on the main cohort's T and N lines [Aitzaz Q5, 24 Oct]. PRE-FREEZE STAND-IN CHECKS: exposure check (ledger row T15): in at least 80% of pilot lives, 10 or more teacher eat-then-sign events fall inside Frankie's view. The sharp-linked count is also reported; if its median is below 3, Aitzaz is told before the freeze that 'not discovered' is the likely outcome, and only world-side fixes are allowed [Aitzaz Q4, 24 Oct]. Creature slot-reset pilot, reported to Aitzaz before the Wave 2 freeze [Aitzaz Q2, 24 Oct]. KINDS (PLACEHOLDER-63): one teaching vault serves every C9 and C10 life and is counted once, here. Claude placeholder: about 24 sealed kinds (4 demonstration-only nourishing kinds, 4 failed-on kinds and 4 never-taught kinds, each with one look-alike kind), fixed in the frozen teacher spec. Under the reuse rule the kinds may be reused across Frankies and cohorts, because set (a) novelty is certified per life; each kind keeps one role within a life and across that Frankie's clones, and none may appear in a lineage's ancestral pool.

### Controls

| ID | Control | Rules out |
|---|---|---|
| C9-CTL-N | N clone: same snapshot, no teacher, demonstration food removed at the same ticks | Frankie improving on its own after the failure (general caution, more of its own experience, time passing), and gains that come only from the demonstration fruit disappearing |
| OS16 | S clone: teacher present, social path off | the teacher changing the world rather than Frankie's mind, for example by steering Frankie's routes or what it happens to see. C9-M2 needs an effect-size floor, not just a p-value |
| OS17 | X clone: social records written but linked to the wrong objects | a memory-size effect: extra remembered records changing Frankie's verdicts in general, whether or not they carry the right information |
| C9-CTL-NEVER-TAUGHT | Never-taught kinds within the same Frankie (C9-M3), with their own gain required not to drop | a general change of strategy, such as looking more closely at everything, being credited as learning about the specific kinds the teacher showed. It also stops 'specificity' being produced by watching making Frankie worse on other kinds |
| C9-CTL-ZERO-OWN-EATS | Headline restricted to kinds, and their look-alike families, with 0 own eats in every clone (ledger-certified) | gains that really come from Frankie's own tasting of the same kinds |
| C9-CTL-SIGNS-HIDDEN | Signs hidden (p = 1.0 and p = 0.75) | crediting glow and tint for what the teacher's choices alone provide. With signs hidden, the only information is where the teacher eats and where it turns away |
| C9-CTL-REVERSED | Reversed-sign world (glow follows poison), p = 0.75, compared with signs hidden | a built-in good meaning for glow. A mind with that built in does worse with reversed signs than with no signs at all |
| C9-CTL-UNINFORMATIVE | Uninformative, signless creature (choices unrelated to nature; sign_condition none) | looking at a moving thing simply because it is there |
| C9-CTL-MATCHED-EATS | Comparison eats matched for payoff, energy_band and a preceding watch event; only habit and drive-sharp-look gazes counted | looking that rises only because Frankie just ate well (the designed 'more proposals when rich' rule), or only because it had just been looking (looking that carries on from one moment to the next) |
| C9-CTL-Y | Yoked Y clone: same Frankie, teacher arrives at least 200 ticks before its first failure | arrival timing explaining the result. It measures whether failing first matters; reported, not required [Aitzaz Q5, 24 Oct] |
| B8 | Copycat (one frozen definition shared with C10 and C11): after the teacher leaves it eats kinds it saw the teacher eat and skips kinds it saw the teacher turn away from | built-in copying of the teacher's choices. With the uninformative creature it must eat more look-alikes than Frankie does |
| B9 | Hard-wired watcher: writes 'what the teacher ate, then glowed, is good' straight into memory | a built-in 'what it ate then glowed is good' rule. In the reversed world it must do worse than Frankie |
| M49 | Creature-observation channels with no evolvable settings, neutral on the priors card (ledger M49) | an attention-to-creatures or glow-is-good bias that drifted in by chance through genes evolution never selected (ancestral worlds have no creatures, D15) |
| TW5 | Payoff-biased social-learner twin (conventional) | crediting Aitzaz's design for a result a textbook social learner gives. Credited to the conventional mechanism under the C9 CREDIT RULE: the 90% equivalence interval lies inside plus or minus 0.10 on C9-M1 and plus or minus log 1.25 on C9-M4; the difference p is reported only |
| G04 | Reject-all-unknown bot | passing by refusing everything new. D needs both accepting real members and rejecting look-alikes |
| G02 | Eat-novel-first bot | passing by eating everything new |
| MK8 | Social mock with a known watching gain G = 0.15 (test fixture only) | a test too weak to detect the gain it claims to measure; it drives the X39 joint-power check |

### Part tags

| Part | Tag |
|---|---|
| C9-M1 one-sided Wilcoxon on G (enters X32) | PRIMARY-EFFECT |
| C9-M1 median G at least 0.15 | FLOOR |
| C9-M2 D(T) - D(S) and C9-M2b D(T) - D(X) | GATE |
| C9-M2 median at least 0.10 | FLOOR |
| C9-M3 specificity test and never-taught not below 0 | GATE |
| C9-M3 median at least 0.10 | FLOOR |
| C9-M4 watch-paid versus matched looking, stay-trend by sign condition, uninformative late looking | GATE |
| C9-M4 median ratio at least 1.25 and uninformative rise bound below half | FLOOR |
| C9-M4 at least 50% of Frankies qualify | APPLICABILITY |
| C9-M5 visible above hidden, and reversed non-inferior to hidden | GATE |
| C9-M6 Frankie above B9 (reversed) and below B8 (uninformative) | GATE |
| TW5 credit rule (90% equivalence interval on C9-M1 and C9-M4, outside every family) | GATE |
| Yoked fail-first comparison G(T) - G(Y) | REPORTED |
| Late probe at 3,000 ticks | REPORTED |
| Poison bites, G by set, memory occupancy, exposure covariates, slot-reset rate, no-failure lives | REPORTED |
| MK8 joint-power check (X39) | VALIDITY |
| G02 and G04 must not pass C9-M1 | VALIDITY |
| Exposure check (ledger row T15) | VALIDITY |

### Log fields needed

- agent_id / agent_type (frankie | B8 | B9 | TW5 | G02 | G04 | MK8)
- version (full | OS16 for S clones | OS17 for X clones) / version_scope (test-time: applied from the arrival snapshot)
- priors_cohort (evolved) / teacher_history (teacher-raised) / teacher_ever_present / teacher_demonstrations_seen (priors card)
- matched_set_id / genome_id / temperament_seed / family_id / vault_id
- snapshot_id / parent_snapshot_id / clone_id / clone_type (T | N | S | X | Y; probe for each single-probe clone)
- replica_key / stream_keys (world, sensor, proposal and teacher streams)
- sign_condition (visible | hidden | reversed | none) / teacher_reliability_p (1.0 | 0.75) / teacher_type (informative | uninformative)
- creature_id / creature_slot
- gaze_target / gaze_distance / gaze_layer_reached / gaze_provenance (habit | proposal | drive-sharp-look | no-safe-option-fallback | baseline-rule)
- action / movement_target / action_provenance (habit | proposal | no-safe-option-fallback | baseline-rule) / options_considered / struck_options
- social_record_events (record_id, creature_slot, linked_candidate_id, trust_type, influence_before, influence_after, substituted_object for X clones)
- verdict_subject / verdict_winner / verdict_margin / settle_steps / verdict_scope
- memory_write_events (including trigger=watched and type=forget) / candidate_lineage
- eat_events (object_id, kind_id, hidden_nature world-side scoring only, energy_delta, effect_tick, stomach_delay_d, taste_vector, sick, net_gain, designed_exposure=false)
- probe_role (member | lookalike) / trial_end_reason
- E / R / b / desperation_slope / energy_band / fed, every tick
- injection_events (energy-set at probes; object-place for demonstration-only instances; object-remove for the N-clone removals)
- Glossary log_fields merged from this claim's former proposed schema additions (PLACEHOLDER-64, ledger I11): tick; failure_trigger {type, tick, kind_id (world side)}; teacher_schedule {arrival_tick, departure_tick, test_start_tick}; teacher_state {position, heading, object_at_or_in_front, object_disappeared}; teacher_sign_rendered (glow | tint | none | hidden) as it appears in Frankie's wide view; wide_view_objects; probe_set (a | b | c | late-a); probe_instance_certificate; memory_slot_occupancy; exposure_events by channel, including watched (creature at object), giving per-kind counts of wide-view eat-then-sign and sharp-linked exposures; own eats per kind and per look-alike family in every clone, from eat_events. Record, not a log field: the priors-card entry for the neutral creature-channel settings (M49).

### If it fails

If C9-M1 fails, the report says 'watching was not discovered'. That is a real negative result about whether watching can grow out of the energy economy without an urge. If C9-M1 passes but a gate fails, the effect is reported under that gate's label (for C9-M6: 'behaves like a built-in copier or watcher') and the claim is not supported. If Frankie is indistinguishable from TW5 under the C9 CREDIT RULE (90% equivalence interval inside the stated margins), the result is credited to the conventional mechanism. If the slot-reset pilot shows trust resetting for a teacher that is still the same creature, Aitzaz is told before the Wave 2 freeze, and only Aitzaz can change PLACEHOLDER-39 [Aitzaz Q2, 24 Oct]. We will NOT add a copy urge, an imitation channel, a dedicated teacher slot, a non-zero starting influence for observations, an attention bonus for creatures, evolvable creature-channel settings, or a built-in meaning for glow or tint. We will NOT let observed sequences become Frankie's proposals, or tune anything on the teaching vault. Before the freeze, only world-side fixes on stand-ins are allowed (demonstrations on Frankie's usual route, denser demonstrations, signs in the wide view). Only Aitzaz can put creatures into ancestral worlds (D15), and any change is flagged in the ledger.


---

## C10 · Trust follows reliability

**Tag:** mechanism check  
**Tests:** T11, T0

> No direct quote; from principle P8 (paraphrase): patience with things the teacher showed should depend on how reliable the teacher was. Aitzaz to confirm the idea is theirs.

**In plain words.** Some teachers are right every time, some 3 times in 4, and some only half the time, which is no better than guessing. Nobody tells Frankie which one it got. Frankie can only find out by tasting some of the things the teacher chose and seeing how they turn out. The claim is that Frankie then goes along with that teacher's choices on fruit it has never tasted, and waits patiently at seeds the teacher waited at, more when the teacher has proved reliable. With an unreliable teacher, it falls for the teacher's mistakes far less than a copier would. Honest note: D9 builds this per-creature earned trust directly into the mind, so this test checks that a designed part works. It is NOT counted as evidence of intelligence. This is a change from the proposal, which listed it as evidence, and it needs Aitzaz's sign-off [Aitzaz Q4, 24 Oct].

### Exact definition

COHORTS: evolved, teacher-raised Frankies on the C9 arrival, stay and gap schedule (ledger rows T12 and T14), with clones T, N and S (OS16) as in C9. teacher_reliability_p is 1.0, 0.75 or 0.5 (teacher repertoire R6, ledger row T07), crossed with sign_condition visible or hidden; plus an uninformative teacher (teacher_type uninformative) with signs visible and with no visible sign. Five cells are the same lives as C9 cohorts (see sample size). CREATURE IDENTITY AND TRUST (PLACEHOLDER-39, ledger M50): Frankie remembers a creature across short gaps out of view; one trust per creature applies to food and seeds alike; choice-trust and sign-meaning are tracked separately [Aitzaz Q2, 24 Oct]. The stand-in slot-reset pilot (creature_id versus creature_slot) is shared with C9 and reported to Aitzaz before the Wave 2 freeze. KINDS: trust-earning kinds are teaching-set kinds the teacher handles where Frankie is free to taste. Trust-test kinds are demonstration-only kinds (W51, as in C9) with 0 own eats of the kind and of its look-alike family, in every clone. The teacher's choices on both follow the same p. Frankie's lifetime world contains no seeds except the teacher's demonstration seeds (teacher repertoire R3, ledger row T05). PROBES: single-probe clones (W52) from the post-gap snapshot, fresh instances, one clone per probe, with E set to R + 10 by a logged energy-set injection. EATING RULES: T11 may never force an eat (PLACEHOLDER-85). Stomach delay (PLACEHOLDER-102, PLACEHOLDER-49): d = 10 for all protocol eats, which here means every eat inside a probe clone, including the seed probe; ordinary eats in the life use d = 3 for the first 2,000 ticks of the test life and d = 10 after that. The frozen teacher spec states both values and the switch tick. AGREEMENT: for each trust-test kind the ledger shows the teacher choosing in Frankie's view (eating it, or approaching, pausing and turning away), agreement = 1 if Frankie does the same and 0 otherwise (probe_role trust-test). Each such probe is paired with a probe of a never-shown kind with the same hidden nature and the same look-alike distance (probe_role never-shown-match), scored as if the teacher had made the same choice. Follow index FI = mean agreement on shown kinds minus mean agreement on the matched never-shown kinds. Trust gain dFI = FI(T) - FI(S). The primary analysis uses the signs-hidden cohorts, where the only information is the teacher's choices. SIGN READING (signs-visible cohorts at p = 0.75 and 0.5 only, because at p = 1.0 the teacher never gets sick): SR = eat rate on trust-test kinds after teacher-eat-then-glow minus eat rate after teacher-eat-then-tint. SR gain = SR(T) - SR(N) on the same probe objects. SEED PROBE (probe_role seed-probe, in every T, N and S clone): the T9 arena without the glimmer stone (scarce but sufficient known food), a fresh real seed on water-edge soil and a dud seed, 2,000 ticks, starting at E = R + 10. A seed can be eaten until it is a tree (W50) [Aitzaz Q2, 24 Oct]. Visits and patient harvest use the shared C8 definition: a visit (visit_events, spot real-seed or dud-seed) is a run of consecutive ticks in which Frankie is within 4 cells of the seed or has its sharp view on it, and runs separated by fewer than 20 ticks merge into one visit. Discovery is the first visit to the real seed. Patient harvest means all four: discovered the real seed before its first fruit; left it uneaten until it became a tree; made at least 1 visit per 100 ticks between discovery and first fruit; ate at least one fruit from that tree. Dud-waiting means 2 or more visits to the dud over the same period (Claude placeholder for PLACEHOLDER-110: if the real seed is never discovered, the period runs from probe start to the real seed's first fruit). Harvest within 300 ticks of first fruit is reported only. Frankies that ate or handled a teacher's seed during the stay are kept in the analysis (intention-to-treat) and flagged. PRECONDITION: in the p = 1.0 signs-hidden cohort, dFI is above 0 (one-sided p < 0.05). Otherwise this check is 'not applicable', because Frankie never relied on any teacher.

### What gets measured

C10 (1) Trust trend: Jonckheere-Terpstra test of per-Frankie dFI across p in the signs-hidden cohorts. Also reported: a logistic regression of per-probe agreement on p, clone (T versus S) and their interaction, with R and b as covariates and standard errors clustered by Frankie, both with and without log demonstrations seen, because that count is partly a result of p and not only a background difference. C10 (2) Effect size: dFI(p = 1.0) - dFI(p = 0.5). C10 (3) Frankie's drop in dFI from p = 1.0 to 0.5, compared with OS18's drop. C10 (4) At p = 0.5: eat rate on fresh look-alikes of the trust-test kinds the teacher wrongly ate, for Frankie, OS18 and B8. C10 (5) Uninformative teacher: dFI. C10 (6) Seed: trend of the patient-harvest share across p (Cochran-Armitage), and trend of (patient-harvest share minus dud-waiting share). C10 (7) SR gain at p = 0.75 and 0.5. REPORTED: harvest within 300 ticks of first fruit; TW6's results with the 90% interval of its difference from Frankie's on C10 (2); the creature slot-reset rate [Aitzaz Q2, 24 Oct].

### Pass mark

All fixed before the Wave 2 freeze (PLACEHOLDER-110). C10 is a mechanism check [Aitzaz Q4, 24 Oct]: none of it is in either Holm family, every test is one-sided 0.05 unless stated, and no result counts as evidence (X32). APPLICABILITY: the precondition (dFI above 0 at p = 1.0, signs hidden) must hold, or the check is 'not applicable'. (1) dFI rises with p: Jonckheere-Terpstra one-sided p < 0.05, and the logistic clone-by-p interaction points the same way. (2) dFI(1.0) - dFI(0.5) is at least 0.15 (floor). (3) Frankie's drop from p = 1.0 to 0.5 is larger than OS18's (bootstrap over Frankies, one-sided p < 0.05). (4) At p = 0.5, Frankie's eat rate on the teacher's wrongly eaten look-alikes is at most 0.7 of OS18's and at most 0.7 of B8's, at least 0.10 lower than each in absolute terms (floors), and Mann-Whitney one-sided p < 0.05 for each. (5) With the uninformative teacher (no visible sign), dFI is below dFI at p = 1.0 (one-sided p < 0.05), and the upper 90% bound of dFI(uninformative) - dFI(0.5) is below +0.05. (6) Seed, using the shared C8 patient-harvest definition: the patient-harvest share rises with p (Cochran-Armitage one-sided p < 0.05), and (patient-harvest share minus dud-waiting share) also rises with p (one-sided p < 0.05). VALIDITY: G12's real-minus-dud difference is not significantly above 0 (one-sided 0.05); by construction it waits equally at both. (7) Sign reading, under the current placeholder (D9 and PLACEHOLDER-39: choice-trust tracked separately from sign-meaning) [Aitzaz Q2, 24 Oct]: the SR gain is at least 0.2 at both p = 0.75 and p = 0.5, and the lower 90% bound of SR gain(0.5) - SR gain(0.75) is above -0.10. If Aitzaz rules that an unreliable teacher's signs also lose trust, item (7) is rewritten before the Wave 2 freeze. CREDIT RULE (GATE, outside every family): if the 90% equivalence interval for Frankie's dFI(1.0) - dFI(0.5) minus TW6's lies inside plus or minus 0.10 [Claude placeholder margin, PLACEHOLDER-110], the report labels the result 'not distinguishable from the conventional reliability learner' and credits it to that conventional mechanism. The two-sided difference p is REPORTED only. Frankie is not required to beat the twin. POWER (X39, before the freeze, on stand-ins): MK9 run with the planned slope must pass items (1) to (4) jointly in at least 80% of pilots at these N; otherwise N is raised before the freeze and never after.

### Sample size

Cells: teacher_reliability_p {1.0, 0.75, 0.5} x sign_condition {visible, hidden}, 100 Frankies each, plus the uninformative teacher in two sign conditions, 100 each; every life has T, N and S clones. SHARED WITH C9 (the same lives, paid for once; PLACEHOLDER-110): (1.0, visible) = C9 main; (1.0, hidden) = C9 signs hidden p = 1.0; (0.75, visible) = C9 visible p = 0.75; (0.75, hidden) = C9 hidden p = 0.75; uninformative signs-hidden = C9's uninformative signless creature (logged sign_condition none; Frankie sees no glow or tint in either case). That is 5 x 100 lives. C9's X clones (main cohort) are not used in C10. Shared lives carry both claims' single-probe clones from the same post-gap snapshot, with kind roles set in the frozen teacher spec. NOT SHARED: C10 p = 0.5 signs visible, C10 p = 0.5 signs hidden and C10 uninformative signs-visible (3 x 100 lives paid for by C10); C9 reversed p = 0.75 and C9 yoked (Y clones); OS18; G12; and every bot and twin run. OS18: 100 at each p, signs hidden, each with T and S clones. B8, B9 and TW6: 100 each at p = 1.0 and 0.5, signs hidden. G12: 50. MK9: stand-in pilots only. Each Frankie gets at least 8 trust-test probes and 8 matched never-shown probes, one clone per probe, and one seed probe per clone. KINDS (PLACEHOLDER-63): C10 uses the shared C9/C10 teaching vault, counted once under C9. Claude placeholder: 0 new sealed kinds, because trust-earning kinds are teaching-set kinds Frankie may taste and the matched never-shown kinds come from C9's set (c); the real and dud seeds are added to the count here if the frozen teacher spec makes them sealed kinds.

### Controls

| ID | Control | Rules out |
|---|---|---|
| OS18 | Trust locked at full (a test variant that follows every creature fully from the start; never part of Frankie) | a trend made only by exposure differences, since low-p teachers show fewer good examples. Frankie's drop from p = 1.0 to 0.5 must be larger than the locked version's |
| C10-CTL-ZERO-OWN-EATS | Trust-test kinds with 0 own eats of the kind and its look-alike family in every clone | agreement that comes from Frankie's own tasting. A plain individual learner that tasted the teacher's kinds would 'agree' with a reliable teacher simply because both are right |
| OS16 | S clone (social path off), used inside dFI | world changes, such as a low-p teacher eating up look-alikes or leaving good food behind, being read as trust |
| C10-CTL-N | N clone, used inside the SR gain | sign reading that is really Frankie's priors: glow-followed kinds are the nourishing ones, so a mind that never watched would already eat them more |
| C10-CTL-DEMO-COVARIATE | Demonstrations-seen covariate (with and without) | low-p Frankies simply having watched less, without hiding that this difference is partly caused by p itself |
| C10-CTL-UNINFORMATIVE | Uninformative teacher (choices unrelated to nature), signs visible and no visible sign | following any creature's choices just because it is there |
| C10-CTL-SIGNS-HIDDEN | Signs hidden | the trend coming only from reading glow and tint rather than from trusting choices |
| B8 | Copycat (one frozen definition shared with C9 and C11) | built-in copying, which follows the teacher whatever p is |
| B9 | Hard-wired watcher | a fixed watch rule whose reliance does not change with p |
| TW6 | Reliability-learning social twin (conventional) | crediting Aitzaz's design for what a textbook reliability learner does |
| G12 | Fixed-delay waiter bot, plus the real-minus-dud seed comparison, in a fed arena | generic hanging around at seeds, or hunger-driven seed eating, being read as reliability-tracking patience |
| MK9 | Trust-slope mock with a known slope (test fixture only) | a test too weak to detect the trend it claims to check; it drives the X39 joint-power check |

### Part tags

| Part | Tag |
|---|---|
| Precondition: dFI above 0 at p = 1.0, signs hidden | APPLICABILITY |
| C10 (1) trust trend | MECHANISM |
| C10 (2) dFI(1.0) - dFI(0.5) at least 0.15 | FLOOR |
| C10 (3) drop steeper than OS18 | MECHANISM |
| C10 (4) tests against OS18 and B8 | MECHANISM |
| C10 (4) 0.7 ratio and 0.10 absolute gap | FLOOR |
| C10 (5) uninformative teacher | MECHANISM |
| C10 (6) seed trends | MECHANISM |
| G12 shows no real-minus-dud difference | VALIDITY |
| C10 (7) sign reading | MECHANISM |
| TW6 credit rule (90% equivalence interval, outside every family) | GATE |
| Logistic regression, harvest within 300 ticks, slot-reset rate | REPORTED |
| MK9 joint-power check (X39) | VALIDITY |

### Log fields needed

- agent_id / agent_type (frankie | B8 | B9 | TW6 | G12 | MK9)
- version (full | OS16 for S clones | OS18 trust-locked) / version_scope (test-time: applied from the arrival snapshot)
- priors_cohort (evolved) / teacher_history (teacher-raised) / teacher_ever_present / teacher_demonstrations_seen (priors card)
- matched_set_id / genome_id / temperament_seed / family_id / vault_id
- snapshot_id / parent_snapshot_id / clone_id / clone_type (T | N | S; probe for each single-probe clone)
- replica_key / stream_keys (world, sensor, proposal and teacher streams)
- sign_condition (visible | hidden | none) / teacher_reliability_p (1.0 | 0.75 | 0.5) / teacher_type (informative | uninformative)
- creature_id / creature_slot
- gaze_target / gaze_distance / gaze_layer_reached / gaze_provenance (habit | proposal | drive-sharp-look | no-safe-option-fallback | baseline-rule)
- action / movement_target / action_provenance (habit | proposal | no-safe-option-fallback | baseline-rule) / struck_options
- social_record_events (record_id, creature_slot, linked_candidate_id, trust_type choice-trust | sign-meaning, influence_before, influence_after)
- verdict_subject / verdict_winner / verdict_margin / settle_steps / verdict_scope
- eat_events (object_id, kind_id, hidden_nature world-side scoring only, energy_delta, effect_tick, stomach_delay_d, taste_vector, sick, net_gain, designed_exposure=false)
- probe_role (trust-test | never-shown-match | lookalike | seed-probe) / trial_end_reason
- visit_events (spot real-seed | dud-seed, start_tick, end_tick)
- E / R / b / desperation_slope / energy_band / fed, every tick
- injection_events (energy-set at probes; object-place for probe seeds)
- Glossary log_fields merged from this claim's former proposed schema additions (PLACEHOLDER-64, ledger I11): tick; kind_role (trust-earning | trust-test) from the frozen teacher spec; teacher_events {ate (kind, true nature), approach-pause-turn-away (kind), R6 fallibility flag, seed-placed | waited | revisited | harvested | waited-at-dud} (world side); teacher_sign_rendered as it appears in Frankie's view; wide_view_objects; exposure_events giving demonstrations seen per kind and per seed (wide-view and sharp-linked); scored_teacher_choice for each agreement probe; seed_state {seed_eaten, tree_tick, first_fruit_tick, harvest_tick}; probe_instance_certificate; own eats per kind and per look-alike family in every clone, from eat_events.

### If it fails

If the trend is absent, or no steeper than OS18's, the report says the designed earned-trust rule does not produce reliability tracking in practice. That is a design finding to bring to Aitzaz, not something to patch. If the precondition fails (Frankie does not follow even a perfect teacher), this check is 'not applicable' and the problem belongs to C9. If the slot-reset pilot shows trust resetting for a teacher that is still the same creature, Aitzaz is told before the Wave 2 freeze [Aitzaz Q2, 24 Oct]. We will NOT give Frankie the teacher's reliability, set a starting trust level, add a copy urge, give signs a built-in meaning, or tune the influence-update constants on any test or teaching vault. Any change to the trust rule needs Aitzaz's approval, a 'changed after seeing T11' ledger flag and a fresh vault.


---

## C11 · Purpose versus motion: the useless wiggle

**Tag:** mechanism check  
**Tests:** T12, T0

> "Urge to copy is too artificial; failing and watching success looks better." (The pass rule is Aitzaz's D14, not a quote: the wiggle may precede at most 20% of eats, and the test counts only if the purposeful sequence was picked up.)

**In plain words.** In the same demonstrations, the teacher does a pointless left-right-left turn before every meal. It also does a turn sequence of the same length that actually gets it round a barrier to food. Frankie should end up getting round barriers but not doing the pointless wiggle. Honest note: in version 1 Frankie can never replay what it watched as its own action, so it cannot copy the wiggle by design. It can still learn from watching WHERE the teacher went, which helps with the barrier but never with the wiggle. So this test checks that no copying path has leaked in, and that Frankie's own lucky habits do not turn into superstitions. It is not evidence of intelligence [Aitzaz Q4, 24 Oct].

### Exact definition

Evolved, teacher-raised Frankies on the C9 arrival, stay and gap schedule. Clones from one snapshot taken at teacher arrival (clone_type): wiggle-A: the teacher shows the wiggle (teacher repertoire R5, ledger row T06) and the barrier sequence. wiggle-B: the barrier sequence only. wiggle-C: the teacher shows neither (never-shown). All other teacher behaviour (repertoire R1 to R4, ledger rows T04 and T05) is identical. After the teacher leaves comes a gap of at least 500 ticks, then 2,000 ticks of solo foraging that include barrier rooms. T12 may never force an eat (PLACEHOLDER-85). Ordinary eats use d = 3 for the first 2,000 ticks of the test life and d = 10 after that (PLACEHOLDER-49); the frozen T12 spec states the d and the switch tick, and the applied value is logged. TOKENS: the X40 tokenizer, shared with C12, C13-E1 and the teacher closure library (ledger row T17), frozen before the closure library is built (motif_tokens, tokenizer_fingerprint). It records each action with its turn direction and does not collapse repeats. A wiggle is a contiguous turn-left, turn-right, turn-left with no step in between, whose last turn comes at most 2 ticks before an eat action (PLACEHOLDER-111). The mirror right-left-right is counted and reported separately. The purposeful sequence P is the detour motif for the barrier-room geometry, written in X40 tokens into the frozen T12 spec before the Wave 2 freeze. A barrier episode is flagged world-side: it starts when food behind the barrier is in Frankie's wide view and the straight greedy path to it is blocked. It ends at the eat, after 200 ticks, or when Frankie leaves the room (PLACEHOLDER-111). Wiggle share = wiggles before eats / all eats, per Frankie. Frankies with 0 eats in the solo period are left out of the wiggle share and counted in the report. P rate = barrier episodes completed via P / all barrier episodes, per Frankie. Each wiggle and each P is traced to its source through action_provenance, habit_weight_updates and proposal_draws. A sequence that first appeared as a proposal (action_provenance=proposal) and was then strengthened by habit_weight_updates after a payoff is a self-made superstition. A P that came from a 'go to a remembered place' proposal pointing where the teacher had been is learning by place, not motion pickup. B8's behaviour after the teacher leaves is defined in the frozen spec: it replays stored teacher motifs in matching situations.

### What gets measured

C11 (1) Gate: P rate in wiggle-A minus P rate in wiggle-C, paired by snapshot, and the group mean P rate in wiggle-A. The provenance split of P episodes (place memory / habit / other proposal) is reported. C11 (2) Cap: group mean wiggle share in wiggle-A, with a 95% confidence interval. C11 (3) Leak: paired wiggle share wiggle-A minus wiggle-B, and wiggle-A minus wiggle-C, with 90% confidence intervals for an equivalence test. C11 (4) Reported: wiggle share in wiggle-C (Frankie's own superstition base rate), the split of wiggles by provenance, the mirror-wiggle counts, and R5 demonstrations seen per Frankie as a covariate.

### Pass mark

Fixed before the Wave 2 freeze. C11 is a mechanism check [Aitzaz Q4, 24 Oct]: outside both Holm families, one-sided 0.05 per test (X32), and never counted as evidence. APPLICABILITY: the test is INFORMATIVE only if the gate passes: P rate in wiggle-A at least 0.15 above wiggle-C (paired Wilcoxon one-sided p < 0.05) AND group mean P rate in wiggle-A above 0.80 (as the proposal requires). If the gate fails, the result is recorded as 'barrier solution not picked up; no copy path leaked in' and is never reported as a pass. If informative, PASS needs both of the following. Cap (D14 as written): group mean wiggle share in wiggle-A is at most 0.20, counting all wiggles, including Frankie's own superstitions [Aitzaz Q5, 24 Oct]. The 95% interval is reported, and if its upper bound is above 0.20 the pass is labelled 'borderline' [Aitzaz Q5, 24 Oct]. No leak: the 90% confidence intervals for paired wiggle share wiggle-A minus wiggle-B and wiggle-A minus wiggle-C both lie inside plus or minus 0.03. Whatever the outcome, the leak check must pass for the build to be accepted. VALIDITY before the freeze, on stand-ins: MK6 caught (no-leak check fails) in at least 95% of pilots; MK7 caught in at least 80% of pilots; B8 must fail both the cap and the no-leak check. X39 joint power is checked with MK7.

### Sample size

50 Frankies, each contributing wiggle-A, wiggle-B and wiggle-C clones (150 lives). B8: 50, each with wiggle-A, wiggle-B and wiggle-C clones. MK6 and MK7: 50 each, with the same three clones, on stand-ins. Power for the plus-or-minus 0.03 equivalence margin is checked on stand-in pilots before the freeze using MK7 (X39). If it falls short, N is raised before the freeze and never after. KINDS (PLACEHOLDER-63): Claude placeholder: 0 new sealed kinds. The demonstrations use teaching-set kinds from the frozen teacher spec, reused across Frankies under the reuse rule, and barrier-room food uses known kinds. The frozen T12 spec confirms the count.

### Controls

| ID | Control | Rules out |
|---|---|---|
| C11-CTL-WIGGLE-C | wiggle-C clones, never shown either sequence | wiggles and detours Frankie produces anyway, through greedy movement, random tie-breaks or its own superstition, being read as effects of watching |
| C11-CTL-WIGGLE-B | wiggle-B clones, teacher without the wiggle | a rise in wiggling caused by the teacher's presence rather than by the wiggle demonstrations |
| B8 | Copycat (one frozen definition shared with C9 and C10; wiggles before about 100% of eats) | a test unable to detect copying (positive control) |
| MK6 | Strong copy-leak mock: copies observed motifs with probability 0.3 (test fixture only, never part of the mind) | a test too weak to catch a sizeable leak. It must be caught in at least 95% of pilot runs on stand-ins |
| MK7 | Weak copy-leak mock: copy probability tuned on stand-ins so the expected wiggle share wiggle-A minus wiggle-B is 0.06, twice the margin (test fixture only) | a test that only catches leaks far bigger than its own margin. It must be caught in at least 80% of pilot runs |
| C11-CTL-TRACE | Provenance, habit-weight and place-memory trace | blaming a self-grown superstition on copying, or the reverse, and calling place learning 'picking up the purposeful sequence' |

### Part tags

| Part | Tag |
|---|---|
| C11 (1) gate: wiggle-A minus wiggle-C P rate, and mean P rate in wiggle-A above 0.80 | APPLICABILITY |
| C11 (2) cap: mean wiggle share in wiggle-A at most 0.20 | MECHANISM |
| C11 (2) 'borderline' label from the 95% interval | REPORTED |
| C11 (3) no-leak equivalence within plus or minus 0.03 | MECHANISM |
| C11 (4) wiggle-C base rate, provenance split, mirror wiggles, R5 covariate | REPORTED |
| MK6 and MK7 catch rates, B8 positive control | VALIDITY |

### Log fields needed

- agent_id / agent_type (frankie | B8 | MK6 | MK7)
- version (full) / priors_cohort (evolved) / teacher_history (teacher-raised)
- matched_set_id / genome_id / temperament_seed / family_id / vault_id
- snapshot_id / parent_snapshot_id / clone_id / clone_type (wiggle-A | wiggle-B | wiggle-C)
- replica_key / stream_keys
- action (with turn direction) / movement_target / action_provenance (habit | proposal | no-safe-option-fallback | baseline-rule)
- proposal_count_target / proposals_drawn_count / proposal_draws (menu_entry, target, draw_number)
- habit_weight_updates (option, situation_key, delta, source_branch_tick, credit_window_outcome)
- struck_options
- eat_events (including energy_delta, net_gain, stomach_delay_d)
- gaze_target / gaze_provenance
- E / R / energy_band
- motif_tokens / tokenizer_fingerprint (X40, shared with C12)
- Glossary log_fields merged from this claim's former proposed schema additions (PLACEHOLDER-64, ledger I11): tick; position / heading; barrier_room_id / barrier_episode {start_tick, end_tick, end_reason} (world side); teacher_events for R5 (wiggle, barrier-sequence) with ticks and in_wide_view / in_sharp_view; place_memory_reads used by 'go to a remembered place' proposals; library_fingerprints (P_motif, the frozen P motif).

### If it fails

If wiggle share in wiggle-A is above wiggle-B or wiggle-C (a leak), a watched sequence has reached Frankie's choices, which breaks a guardrail. That is a bug: it is fixed, flagged 'changed after seeing T12', and the test is rerun on a fresh vault. If the wiggle cap fails in every clone, including wiggle-C, Frankie grows superstitions on its own. That is reported as a real property of the habit rule and taken to Aitzaz. If the gate fails, nothing is claimed. We will NOT add a rule that suppresses turns before eating, tune the habit-credit window on test material, or add a motion-copying channel just to make the test informative. Whether a later version 2 should let watched sequences enter as proposals with zero starting influence that must be earned, which could make this test evidence, is an open design question for Aitzaz outside Q1 to Q5; version 1 does not allow it.


---

## C12 · Novel approaches in three tiers: repeat, recombination, novel

**Tag:** evidence (primary)  
**Tests:** T13, T15 (optional, Stage 10), T0

> "It's only intelligent if it can think up novel approaches to problems." "If I've taken path A all this time, what happens if I take path B."

**In plain words.** Every way Frankie reaches food is sorted into one of three tiers. A REPEAT is something already on record: done by the teacher, done by Frankie before, done by its evolutionary ancestors, or produced by a single random suggestion from Frankie's own menu. A RECOMBINATION is new as a whole but is just two known pieces joined together. NOVEL means new and not simply two known pieces glued together [Aitzaz Q4, 24 Oct]. The claim is that Frankie reaches food by new approaches far more often than random flailing or brute trial-and-error does, and that far fewer of its new moves are wasted. The main test uses Frankies that never met a teacher, so the teacher cannot be the source of their new ideas. A longer or costlier new route is never counted against Frankie, and choosing it is reported as a positive.

### Exact definition

All definitions are world-side, so they apply in exactly the same way to Frankie and to every baseline. GROUP (PLACEHOLDER-111): the primary T13 group is 100 evolved, teacher-free Frankies (priors_cohort=evolved, teacher_history=teacher-free), frozen in Wave 1 (Stage 4) with T0-T9 and T14 (ledger X02). The priors card checks teacher_ever_present=false and teacher_demonstrations_seen=0. A teacher-raised group is secondary: it is frozen with Wave 2 before any teacher-raised Frankie runs, reported separately, and never pooled with the primary group. SEGMENT: the actions between consecutive eats (or from room entry to the first eat, or from the last eat to the room's end or death). APPROACH: the last W = 30 actions of a segment that ends in an eat with net energy gain (PLACEHOLDER-111; sensitivity at 15 and 60). TOKENS: the X40 tokenizer, shared with C11, C13-E1 and the closure library, frozen before the closure library is built and before any mind code exists (K-F excepted, KILL_TEST.md section 1). Placeholder until Aitzaz picks at initialling: each step is (direction, relative to heading, of the next object this agent eats, judged in hindsight, or 'none'; a blocked-ahead flag; a food-in-wide-view flag) plus the action with its turn direction, with no collapsing of repeated actions and exact matching. PLACEHOLDER-65's version is kept only as a reported sensitivity check. REFERENCE SETS for each agent (together, 'the references'): (a) the teacher closure library (ledger row T17); for the primary teacher-free group this is the whole of set (a), because the lifetime teacher log is empty by construction; for the secondary teacher-raised group, set (a) also includes that lifetime's teacher log. (b) The agent's own full log up to the start of the segment. (c) Evolution records: motifs regenerated by exact replay of every lifetime in the evolution runs that produced the tested genome; FAST mode keeps only exposure summaries, so replay is required, and baselines use the same records, for parity. (d) Menu closure: every sequence that one draw from Frankie's designed proposal menu, followed by the designed greedy movement rule under every possible tie-break, can produce from the segment's start state, computed by counterfactual replay and applied to every agent. NOVEL CORE: a maximal stretch in which every 4-step window is absent from all four references. Tier 1 REPEAT: the approach contains no novel core. Tier 2 RECOMBINATION: a novel core overlaps the approach, and every such core, plus up to 1 step of context on each side, can be written as at most 2 back-to-back pieces, each at least 3 steps long and each found in the references. Tier 3 NOVEL: at least one novel core overlapping the approach cannot be split that way (classifier X41). D14's 'novel' (4+ steps, absent from all four references) equals tiers 2 and 3 together; the charter labels tier 2 'recombination' and keeps 'novel' for tier 3 [Aitzaz Q4, 24 Oct]. NEW-SITUATION FILTER: if any situation token in a novel core appears fewer than 20 times in the references, the segment is set aside as 'new situation, not new behaviour' and reported separately. PROVENANCE: 'proposed and kept by prediction' means 0 failed physical attempts (bumps, dead ends, walk-backs) at this goal in this room before success, AND at least 1 struck option (struck_options) during the segment with strike_class=reasoned. The strike class follows the shared world-side rule (ledger M31): rote if this agent has at least one own eat of, or sickness from, any instance of the same world kind before the strike; reasoned only if that kind has zero own eats; no-kind if the option has no object kind (such as a route move), and no-kind strikes never count as reasoned. Otherwise the segment is 'found by trial'; such approaches count toward the claim and carry that tag [Aitzaz Q4, 24 Oct]. ROOMS, ENTRY AND DEATH (ledger W46; there is no survival floor): every agent lives the same schedule in the same seeds. Each problem room is a separate clone (clone_type room) from the agent's room-entry snapshot at the matched life age, so a death in one room does not affect the others. Entry energy is set once at entry by a logged energy-set injection: R + 10 for agents with a reserve, and Frankie's cohort median reserve + 10 for agents with none. This set never depends on low energy. Energy is never reset when it reaches 0, and dying at 0 (B06) holds in every room and every pre-room life. Reaching room-entry age is an entry condition applied the same way to every agent type: each type's room cohort is the first 100 lives, in pre-registered seed order, that reach room age, and deaths before room age are reported per type. Inside a room, death ends that room (trial_end_reason=death). The denominator for R3 and R23 is always the scheduled 2,000 ticks per room, so ticks after death count with zero eats; dying is never rewarded. T13 and T15 may never force an eat (PLACEHOLDER-85). Ordinary eats follow PLACEHOLDER-49, and the frozen T13 spec states the d and its switch tick. BASELINE BODIES: every baseline uses Frankie's body and action list, and those that move to targets use the designed greedy movement rule. B1n-seq (ledger X36) uses Frankie's body, proposal menu and greedy movement: it keeps and retries any action sequence that paid, otherwise draws again from the menu, and decides eat/skip with B1n-bot's nearest-neighbour memory. The full rules are in the frozen T13 spec. CLASSIFIER CHECK (X41, before the freeze, on scripted sequences): a scripted copy of a teacher motif must come out as tier 1, a scripted join of two known pieces (including the T15 trick-A plus trick-B sequence) as tier 2, and a scripted sequence that cannot be split as tier 3.

### What gets measured

T13, per agent, in the three problem rooms (primary). R3 = eats whose approach contains a functional tier-3 core, per 10,000 scheduled room ticks. Eats are counted rather than cores, so a long, wandering stretch counts once, not many times. R23 = the same for tier 2 or 3 (D14's 'novel'). Hit rate H = novel cores overlapping a net-gain approach / ALL novel cores of 4+ steps anywhere in the room log, including wandering that never reaches food. H blocks a flailing strategy from passing. REPORTED: R3, R23 and H from the always-on scan of every test lifetime (secondary, since lifetimes differ in length); a per-ticks-lived version of R3 and R23; failed physical attempts before the first success in each room, against B1n-seq; the share of segments tagged 'proposed and kept by prediction'; the share of route-B choices in the blocked-route room; R3 and R23 for OS14, with the share of novelty attributed to the designed randomness curve; own-log length, death events and deaths before room age as covariates; sensitivity across motif lengths 3 to 8, minimum piece length 2 to 4, approach window W of 15 or 60, an actions-only version with situation tokens stripped, and the PLACEHOLDER-65 tokenizer; the secondary teacher-raised group; and the cautious-start replicate (M25). Each counted eat carries a certificate (nearest reference motif, edit distance, which reference set, tier, ticks) and a replay clip. T15 (optional): success rate within 2,000 ticks per condition, and failed attempts before success.

### Pass mark

T13 is one of the seven primaries in the ledger X32 Holm family (m = 7; strictest step 0.05/7, about 0.0071) [Aitzaz Q4, 24 Oct]. This claim's Holm p is the largest one-sided p among its effect parts: the one-sided Mann-Whitney tests of R23 versus B0 and of R23 versus B1n-seq. C12's single p enters X32. STEP 1, recombination-or-better (R23): EFFECT: C12's single p is below C12's Holm level under X32. FLOOR: Frankie's rate ratio is at least 2 against B0 and against B1n-seq. GATES (each one-sided 0.05, uncorrected): Frankie's H is above H for B0, G11 and B4n; and Frankie's R23 is above OS21's. If step 1 passes with its floor and gates, the report says 'recombination supported'. STEP 2, novel (R3): a fixed-sequence follow-on, tested only if step 1 passes, at the level C12 received in Holm, with no extra alpha, using the same effect parts, floor and gates with R3 in place of R23. If it passes, the report says 'novel approaches supported'. If step 1 passes but step 2 fails, the report says 'recombination supported, novel not supported'. LABELS: if the effect passes but the H gate fails, the result is 'not supported: the rate comes from wandering'. If Frankie fails only the OS21 gate, the result is credited to randomness and reported as 'found by trial'. CREDIT RULE (GATE, outside every family): if the 90% equivalence interval for the log ratio of R23, Frankie over TW3, lies inside plus or minus log 1.25 [Claude placeholder margin, PLACEHOLDER-111], the result is credited to the conventional mechanism. The two-sided difference p is REPORTED only. Comparisons use identical room instances and seeds and the matched schedule (replacing PLACEHOLDER-82). The share of 'proposed and kept by prediction' segments is reported with no pass mark, because D11 left plan elimination open and the share is expected to be near zero. Route B is never penalised. CAUTIOUS-START REPLICATE (M25): step 1 effect parts reported for 50 cautious-start Frankies, outside every Holm family and never a pass condition; if a result passes at neutral but not at cautious, it is labelled 'supported at neutral start only'. VALIDITY: the classifier check (X41) must pass before the freeze; X39 joint power on stand-in rooms (step 1's effect parts at 0.05/7 with the 2x floor and the gates, jointly at least 80% at N = 100), otherwise N or the room duration is raised before the freeze and never after. T15 (optional, Stage 10, labelled recombination, REPORTED outside both families with its own Holm across its 5 controls at 0.05): PASS needs at least 20% of A+B Frankies to succeed within 2,000 ticks, at most 5% to succeed in EACH control, and A+B to beat each control in a one-sided Fisher exact test, Holm-adjusted across the 5 controls, p < 0.05. Each success must be certified absent from the teacher library (repertoire R7, ledger row T08, never pushes a log to a tree), Frankie's log and the evolution records, must be impossible from a single menu draw (there is no push-toward macro), and must be classified as tier 2 by the already-frozen classifier.

### Sample size

T13 primary: 100 evolved, teacher-free Frankies (the first 100 in pre-registered seed order that reach room age), each running the three problem rooms (each 2,000 ticks; PLACEHOLDER-111), plus the always-on scan of every test lifetime. 100 each, chosen by the same entry rule, for B0, B1n-seq, B4n, G11, OS21, OS14 and TW3; deaths before room age are reported per type. Secondary teacher-raised group: 100 Frankies (Claude placeholder N, PLACEHOLDER-111), frozen with Wave 2, reported separately. Cautious-start replicate (M25): 50 Frankies, compared against the same B0 and B1n-seq runs. A power check runs on stand-in rooms before the freeze (X39). If a 2x rate ratio is below 80% power at N = 100, N or the room duration is raised before the freeze and never after. T15: 100 per condition across 6 conditions (A+B and the 5 controls), raised from the proposal's 50 because 20% against 5% at N = 50 has weak power. KINDS (PLACEHOLDER-63): Claude placeholder: 0 new sealed kinds, because the problem rooms and the T15 room use known food kinds. The frozen T13 and T15 specs confirm the count.

### Controls

| ID | Control | Rules out |
|---|---|---|
| B0 | Random bot | random flailing producing 'new' sequences that sometimes hit food. It must lose on both R23 and hit rate |
| B1n-seq | Sequence keep-and-retry learner, on Frankie's body, menu and greedy movement rule | brute trial-and-error, the 'bad elimination' Aitzaz warned about, reaching food by new routes |
| B4n | Greedy eater plus Frankie's designed proposal noise | greedy movement plus noise producing detours by accident |
| G11 | Always-explore bot | maximum wandering scoring well on a raw count. It must lose on hit rate |
| C12-CTL-HIT-RATE | Hit rate counted over ALL novel cores, including wandering that never reaches food | a flailing mind looking efficient because its failed wandering never entered the count |
| C12-CTL-ENTRY-DEATH | Matched room-entry age, the same entry rule and death rule for every agent, scheduled-tick denominator, own-log length as a covariate | agents that die young looking more novel only because they have a shorter record of their own to be compared against, and dying being rewarded by a shorter denominator |
| OS21 | Gating, objection and elimination off ('switched-off Frankie'), same randomness | novelty that comes from Frankie's randomness alone, with no help from its mind |
| OS14 | FIXED-RANDOMNESS Frankie | credit going unexplained: it shows how much of the novelty comes from the designed 'more proposals when rich or desperate' curve. Reported, and the report attributes that share to the curve |
| TW3 | Best-score chooser twin (conventional) | crediting Aitzaz's satisficing design for what a textbook chooser does. If they are indistinguishable, the result is credited to the conventional mechanism. Frankie is not required to beat the twin |
| C12-CTL-TEACHER-FREE | Primary group teacher-free; reference set (a) is the closure library only; teacher_ever_present checked on the priors card | the teacher being the hidden source of 'new' approaches, and a Wave 1 freeze that silently depends on Wave 2 teacher lives |
| C12-CTL-REFERENCES | The four reference sets, including menu closure by counterfactual replay, applied identically to every agent | repeats of the teacher, of the agent itself, of Frankie's ancestors, or of a single random suggestion counting as new |
| C12-CTL-FILTERS | New-situation filter, actions-only version, length, piece-size, window and tokenizer sensitivity, and the pre-freeze classifier check (X41) | novelty that comes only from how behaviour is chopped into tokens, from a room simply looking new, or from a classifier fixed after seeing results |
| C12-CTL-CAUTIOUS | Cautious-start replicate (ledger M25): 50 Frankies with newborn_start cautious, step 1 effect parts only | a result that rests on the designers' neutral starting value for untried things |
| C12-CTL-T15 | T15 controls: taught A only, taught B only, taught neither, B1n-seq, and OS23 (tower off, random choice among proposals; condition value random-proposals-no-tower) | one trick alone, no tricks, brute force, or random action producing the log-to-tree solution, so a success really does need both pieces |

### Part tags

| Part | Tag |
|---|---|
| Step 1: R23 versus B0 (one-sided Mann-Whitney, enters X32) | PRIMARY-EFFECT |
| Step 1: R23 versus B1n-seq (one-sided Mann-Whitney, enters X32) | PRIMARY-EFFECT |
| Rate ratio at least 2 against B0 and B1n-seq | FLOOR |
| H above B0, G11 and B4n | GATE |
| R23 (and R3 in step 2) above OS21 | GATE |
| Step 2: R3 versus B0 and B1n-seq (fixed sequence at C12's Holm level) | PRIMARY-EFFECT |
| TW3 credit rule (90% equivalence interval, outside every family) | GATE |
| OS14 attribution, proposed-and-kept share, route-B share, always-on scan, per-ticks-lived version, sensitivities | REPORTED |
| Secondary teacher-raised group | REPORTED |
| Cautious-start replicate | REPORTED |
| Classifier check (X41) and X39 power check | VALIDITY |
| T15 (optional, own Holm across 5 controls) | REPORTED |

### Log fields needed

- agent_id / agent_type (frankie | B0 | B1n-seq | B4n | G11 | TW3)
- version (full | OS14 | OS21 | OS23 for T15) / version_scope (as stated in the frozen T13 spec)
- priors_cohort (evolved) / teacher_history (teacher-free for the primary group | teacher-raised for the secondary group) / teacher_ever_present / teacher_demonstrations_seen (priors card: false and 0 for the primary group)
- newborn_start (neutral | cautious)
- matched_set_id / genome_id / temperament_seed / family_id / vault_id
- snapshot_id / parent_snapshot_id / clone_id / clone_type (room)
- replica_key / stream_keys
- E / R / b / desperation_slope / energy_band / fed
- action (with turn direction) / movement_target / action_provenance (habit | proposal | no-safe-option-fallback | baseline-rule)
- options_considered / satisficing_bar (0.9 - 0.3 x b under PLACEHOLDER-27) [Aitzaz Q3, 24 Oct] / no_safe_option
- struck_options (with strike_class reasoned | rote | no-kind)
- proposal_count_target / proposals_drawn_count / proposal_draws
- habit_weight_updates
- eat_events (including energy_delta, net_gain, stomach_delay_d)
- injection_events (energy-set at room entry; the route-A block as object-place or source-stop, with tick and vault provenance)
- motif_tokens / tokenizer_fingerprint (X40)
- room_reached / death_tick / trial_end_reason (death | tick-cap)
- replay_fingerprint_match
- Glossary log_fields merged from this claim's former proposed schema additions (PLACEHOLDER-64, ledger I11): tick; position / heading; room_id / room_instance / room_entry_life_age; segment_boundaries / approach_windows (world side); target_events (mind-side target set and clear, secondary); failed_attempt_events (bump | dead-end | walk-back); push_events (tick, log position; T15); condition with the T15 values (A+B | A-only | B-only | neither | B1n-seq | random-proposals-no-tower, run as version OS23); library_fingerprints (teacher closure library, lifetime teacher log for the secondary group, evolution motif library, classifier-check sequences); counted_eat_certificate (menu-closure result and motif certificate for each counted eat, with its replay clip id).

### If it fails

If step 1 fails, the report says 'no new approaches beyond what randomness and brute force give'. That is a real negative result about this mind, not a reason to change the scoring. If only step 1 passes, the result is labelled recombination. If a result holds only at the neutral start, it is labelled 'supported at neutral start only'. T15 failure is pre-registered as expected and becomes a design question for Aitzaz. We will NOT add a novelty or visit-count bonus, put ready-made macros such as 'push X toward Y' on the menu, add a conventional planner (route search, tree search or similar), raise the number of proposals or change the randomness curve after seeing results, bring back a survival floor, loosen the motif length, reference sets, piece rules, approach window or tier rules, let watched sequences become proposals, or tune anything on test vaults. A plan-elimination mechanism (D11) is added only if Aitzaz designs it. It gets its own ledger rows, an off-switch and a fresh vault, and its results are reported separately and flagged.

