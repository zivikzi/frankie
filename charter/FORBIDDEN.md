# Forbidden in Frankie's mind

_FRANKIE Stage 0 · approved by Aitzaz · frozen as tag charter-v1 · 25 Oct 2026_


None of these may ever appear in Frankie's mind package. If a property never emerges without one of them, that is reported as a result. Nothing here gets added to rescue it.

## 1. Any large language model or pretrained model inside Frankie's mind

**What it is.** No chatbot, no model trained on internet data and no pre-trained vision or language network may run inside Frankie, even as a small helper. Claude helps only from outside, by writing code and describing logs.

**Why it's forbidden.** P1 (no LLM inside) and Aitzaz's core argument: today's AI 'fakes' intelligence because it was trained on the mark schemes beforehand. Anything pretrained brings the answers in with it.

**How it's checked.** Automatic: the import guard fails the build if the mind package imports anything but NumPy and Numba. Automatic: a scan for model weight files (.pt, .onnx, .safetensors, or .npz files loaded at start-up) inside the mind package. Review: every mind design note.

## 2. Gradient training of any kind (backpropagation, gradient descent on a loss)

**What it is.** Frankie's connections may not be adjusted by computing how to reduce an error score over many examples, which is how standard neural networks are trained.

**Why it's forbidden.** Hard rule: no gradient training. Learning must come from Aitzaz's rules (blame moves outward, stretch on a right guess) within one lifetime (D3). Spike-timing learning, if it is ever added, must not become a disguised gradient rule (PLACEHOLDER-18).

**How it's checked.** Automatic: the import guard (no torch, jax, tensorflow or autograd). Automatic: a scan of mind code for words such as 'grad', 'backward', 'loss' and 'optimizer', with every hit sent to review. Review: the write rule is checked against D3, and the weight and reliability steps (PLACEHOLDER-02, PLACEHOLDER-05) must be fixed steps, never sizes computed from an error score.

## 3. Machine-learning or reinforcement-learning libraries

**What it is.** Ready-made toolkits such as scikit-learn, gym or reinforcement-learning frameworks may not be used in the mind.

**Why it's forbidden.** Hard rule, and P2 (conventional methods for the world's plumbing only). These libraries carry textbook 'best method from A to B' solutions, which Aitzaz fears Claude will slip in.

**How it's checked.** Automatic: the import guard allows only NumPy and Numba in the mind package. Review: the lockfile is reviewed for every new dependency.

## 4. Novelty bonus or visit-count bonus

**What it is.** Frankie may not get extra reward or extra value just because something is new, or because it has rarely visited a place or object.

**Why it's forbidden.** Hard rule and D4: untried options are valued at the average of Frankie's own first encounters (PLACEHOLDER-34), starting from the newborn value (M25), with no novelty bonus. Curiosity must grow out of the energy economy as insurance (P6), or be reported as absent.

**How it's checked.** Automatic: a scan of mind code for 'novel', 'bonus', 'visit' and 'count' near value calculations, with hits sent to review. Behavioural: B3 (count-based novelty agent) must stay stuck on the glimmer stone in C8 (T9); if Frankie behaves like B3, that is flagged. G02 (eat-novel-first) must fail the claims that list it. Review: option valuation is checked against D4.

## 5. Prediction-error or surprise reward

**What it is.** Frankie may not be rewarded for being surprised, or for seeing something its own predictions got wrong.

**Why it's forbidden.** Hard rule: no curiosity reward. This is the textbook curiosity method that falls into the noisy-TV trap. Aitzaz wants 'patience, not persistence' to arise without it (P8).

**How it's checked.** Review: every place a mismatch is computed (objection mismatch values, wrong guesses after eating) must be shown to change only memory (D3), never the value of an option or the satisficing bar. Behavioural: C8 (T9) compares Frankie with B3 on the glimmer stone.

## 6. Learning-progress or competence reward

**What it is.** Frankie may not be rewarded for improving, or for being in situations where it is learning fast.

**Why it's forbidden.** Hard rule: no learning-progress reward. Curiosity must be insurance for path A failing, following Aitzaz's path B idea (P6).

**How it's checked.** Review: each design note is checked against this list. Automatic: a scan for 'progress', 'improvement' and 'competence' in value code.

## 7. Uncertainty or information-gain bonus (including 'optimism in the face of uncertainty' and posterior sampling)

**What it is.** Frankie may not value an option more because it is unsure about it. A sharp look is worth paying for only when it could change a predicted energy outcome.

**Why it's forbidden.** D4 and D8: no bonus for novelty or uncertainty, ever. Sharp looks are an energy spend judged by the drive.

**How it's checked.** Review: the sharp-look rule (D8, PLACEHOLDER-33) and option valuation (D4). The 'less reliable' mark (PLACEHOLDER-05) may raise the predicted chance of a wrong guess, and so change a predicted energy outcome; it may never add value for being unsure in itself. Automatic: a scan for 'uncertainty', 'entropy', 'ucb' and 'thompson' in mind code.

## 8. Optimistic starting values, and undeclared starting beliefs

**What it is.** New, untried things may not start with a high hopeful value that pulls Frankie toward them. Any starting belief the designers choose, such as how often food sources fail, must be declared and logged.

**Why it's forbidden.** D4: newborns start neutral (expected change zero, M25); a cautious start (PLACEHOLDER-35) is also reported. Optimism is a hidden novelty bonus. A starting failure belief chosen by the designers would make exploring come from the designers rather than from what Frankie lived through.

**How it's checked.** Automatic: a test reads the newborn default from the ledger (M25) and asserts it equals the logged neutral or cautious value (newborn_start). Automatic: a test asserts that the newborn failure belief equals its ledger value, zero under M48 [Aitzaz Q3, 24 Oct]; any non-zero value is printed on the priors card as a designed prior. Review.

## 9. Habituation or boredom counters (per object, kind, place or global)

**What it is.** Frankie may not keep any number that goes up or down just because it looked at, visited or met something again, whatever happened. Losing interest must come from fading memories of what happened ('looked here, nothing came of it'), not from a tally of looks.

**Why it's forbidden.** D10: loss of interest must come from ordinary fading place-and-time memory. A counter would hand-build the patience result in C8 and make it worthless as evidence.

**How it's checked.** BOUNDARY (PLACEHOLDER-109) [Aitzaz Q2, 24 Oct]. FORBIDDEN: any stored mind quantity, at any grain (per object, per kind, per place or cell, or one global number), that grows or shrinks with the number of looks, visits or exposures whatever their outcome. This includes a per-place look count for an object that never moves, a global 'looks since last food' number, a familiarity or habituation trace bumped on each look, a novelty trace that shrinks on exposure, and any sighting tally used to discount a value. ALLOWED: (1) fading place-and-time records, each written only when an outcome is observed and carrying that outcome (for example 'investigated here, nothing came of it' or 'ate here, +14'); such records may add up; (2) a sighting record that holds what was seen where, where a repeat sighting of the same recognised kind (or 'unknown') in the same cell refreshes the existing record instead of adding a new one (PLACEHOLDER-31); (3) the sensory buffer of the current tick and the settling state inside one decision; (4) memory bookkeeping that changes only on outcomes, such as confirmed wins (PLACEHOLDER-07) and the 'less reliable' mark (PLACEHOLDER-05). Counts kept on the world side of the log (for example teacher_demonstrations_seen or visit_events) are not mind state and are allowed. REVIEWER TEST: for each stored mind quantity, imagine every write that records an observed outcome switched off, and ask 'would one more look, visit or exposure still change this value?' If yes, and the quantity is not in the allowed list, it is a counter. HOW CHECKED: Automatic, the T0(e) code check: two scripted runs end with an identical last look at the same tick and differ only in how many earlier looks they made, with the outcome-record write intercepted; any difference in mind state, apart from the sensory buffer, flags a counter. Automatic: no mind data structure is keyed by object identity (the mind never receives IDs). Review of place-and-time memory code against D10 and PLACEHOLDER-109. Behavioural: G15 (fading-everything bot) must fail C8. C8-S4 memory-slot and forget-event logs.

## 10. Built-in 'becomes' links (for example seed becomes tree)

**What it is.** Frankie may not be told that a seed turns into a tree, or that a spot will later have fruit.

**Why it's forbidden.** D10: the seed-to-fruit connection must be noticed from ordinary place-and-time records, or the patience test fails honestly.

**How it's checked.** Review of memory design notes. Automatic: a scan for 'seed', 'tree' and 'grow' in mind code (the mind should have no names for world things).

## 11. Temporal-difference errors, value tables and Q-learning

**What it is.** The standard reinforcement-learning machinery that estimates the long-run value of each situation and action, by passing value backward from one situation to the ones before it, is not allowed in the mind. Plain tallies of what actually happened to Frankie are allowed.

**Why it's forbidden.** Hard rule: no reinforcement learning. Choice must come from Aitzaz's spend-or-conserve drive plus satisficing (D6). Habits (M34) and the drive's counting estimator (PLACEHOLDER-21) look like value tables, so the line has to be drawn exactly.

**How it's checked.** BOUNDARY (Aitzaz confirms at initialling). ALLOWED: a stored quantity is allowed only if ALL of these hold: (1) it is a tally (a count, a sum or a ratio of counts) of Frankie's OWN observed outcomes, such as energy changes it experienced, sources it saw fail, or first-eat outcomes; (2) each update is written from an outcome observed within a fixed credit window after the choice or situation it is credited to, with the window a registered constant (30 ticks for habits, PLACEHOLDER-30; the drive horizon of 200 ticks, PLACEHOLDER-21; 300 ticks after the watched event for the trust and influence updates, PLACEHOLDER-40 and PLACEHOLDER-41); (3) there is no discounting: an outcome inside the window counts in full and one outside counts zero; (4) the update's inputs are only the observed outcome, the tally's own previous value and a registered fading rate, never another stored estimate or prediction. Computing a prediction at choice time by reading tallies (for example 'in how many similar past situations did E stay above R') is allowed, as long as that prediction is never written back into any tally. This covers M34's habit weights (logged as habit_weight_updates), PLACEHOLDER-21's counting estimator, the untried-value average (PLACEHOLDER-34) and the trust and influence updates (PLACEHOLDER-40, PLACEHOLDER-41). BANNED: anything that updates one situation's or option's value from another situation's value or estimate, including TD errors, Bellman backups, bootstrapped targets, discount factors, Q-tables, learned value functions, advantage estimates, and eligibility traces that pass value backward across situations or beyond the fixed window. REVIEWER TEST: for every write to a stored quantity in drive, habit or social code, list its inputs; if any input is another stored estimate or a predicted value, it is banned. HOW CHECKED: Review checks the habit (M34) and drive (PLACEHOLDER-21) design notes against this line. Automatic: a scan for 'td', 'q_table', 'value_function', 'bellman', 'discount', 'gamma', 'bootstrap', 'eligibility' and 'advantage'. Automatic: with every outcome event intercepted, no drive or habit tally may change except by its registered fading. Behavioural: comparison with the conventional twins (TW3, TW4).

## 12. Softmax or epsilon-greedy action selection inside Frankie

**What it is.** Frankie may not choose by the textbook 'mostly best, sometimes random' rules. Randomness only proposes; character decides.

**Why it's forbidden.** Aitzaz: 'character always insisting, randomness is discovery' (P5). D5 sets energy-dependent proposals and D6 sets satisficing. Epsilon-greedy exists only as an outside twin (TW4).

**How it's checked.** Automatic: a scan for 'softmax', 'epsilon', 'boltzmann' and 'temperature'. Automatic: the mind may not import from the twins package. Review: randomness may set only how many proposals are drawn and which menu entries they are (PLACEHOLDER-25, PLACEHOLDER-96), never which option is chosen. C13 (T14) reports Frankie next to TW4. OS18 (trust locked at full), OS19 (character off) and OS23 (tower off, random choice) are test-only flags kept in a test-fixtures module, never in the mind package; the harness refuses any of them in a run labelled 'full', and the 'randomness never chooses' rule applies to version full only.

## 13. Best-score (argmax) chooser as Frankie's main choice rule

**What it is.** Frankie's main chooser must take the first option that keeps it safely above reserve, not the best-scoring one. The single exception is when no option is safe: then it takes the option with the best chance of staying above reserve, and every such tick is flagged.

**Why it's forbidden.** D6, and Aitzaz's point that a less-optimal path is worth more to life in the long run (P2). The fallback is allowed only because some rule is needed when nothing clears the bar (M47) [Aitzaz Q3, 24 Oct].

**How it's checked.** Review: the main chooser is checked against D6 and M29. Automatic: the configuration test asserts the chooser mode is 'satisficing' in every claim run. Automatic: a best-score rule is allowed only as the M47 fallback when no option clears the bar; every use is logged with action_provenance=no-safe-option-fallback and no_safe_option=true, and a test asserts that on every such tick each entry in options_considered has cleared_bar=false. Its share is reported in C7, and the backups-don't-count gate (OS13) covers it. Automatic: the replayed drive trace (M53) is log-only; the interface test fails the build if the mind reads it.

## 14. Copy urge, imitation channel or dedicated teacher slot

**What it is.** Frankie has no built-in desire to copy, no special input for 'what the teacher is doing', and no memory set aside for the teacher.

**Why it's forbidden.** Aitzaz: 'urge to copy is too artificial; failing and watching success looks better' (P7). D9: watching enters as ordinary events with zero starting influence.

**How it's checked.** Review against D9. Automatic: the observation packet schema test (the teacher appears only as raw visual features, with no action labels). Behavioural: C9 (T10) must beat B8 (copycat) and B9 (hard-wired watcher), with OS16 (social path off) as the floor.

## 15. Replaying observed action sequences as Frankie's own proposals

**What it is.** Frankie may not take a sequence it watched another creature perform and feed it into its own list of things to try.

**Why it's forbidden.** D9 and the novelty definition (D14): copying would make 'novel' approaches secondhand.

**How it's checked.** Review of the proposal code: proposals may draw only from the frozen menu and Frankie's own habits. Automatic: the novelty certificates check every motif, cut with the X40 tokenizer, against the teacher closure library (T17) and that lifetime's teacher log. Behavioural: C11's copy-leak mocks (MK6, MK7) must be caught at their stated rates, which shows the check can see copying.

## 16. Social influence that starts above zero

**What it is.** Records of what others did may not affect Frankie's choices until they have predicted Frankie's own outcomes.

**Why it's forbidden.** D9: influence is earned per creature (M37).

**How it's checked.** Automatic: a test that a newborn's social influence and trust values are all exactly zero (PLACEHOLDER-40, PLACEHOLDER-41). OS18 (trust locked at full) is a test-only flag in the test-fixtures module, and the import guard keeps it out of Frankie; the harness refuses it in any run labelled 'full'. Review.

## 17. Built-in meanings for taste, glow or tint

**What it is.** Frankie may not be told that sweet is good, bitter is bad, or that glowing means a creature ate well.

**Why it's forbidden.** Hard rule, D9 and D16: meanings must be learned from Frankie's own energy outcomes.

**How it's checked.** Behavioural: the reversed-sign world in C9 (glow follows poison) must invert Frankie's reading. Review: no sign or taste input has a fixed weight in the drive; taste enters only as a detail trait in candidates and in the verdict after eating (PLACEHOLDER-92, M51) [Aitzaz Q2, 24 Oct].

## 18. Access to object IDs, hidden natures, kind names or the world's essence/surface split

**What it is.** The mind may never see which object is which in the world's books, whether something is poison, or which traits the world calls 'core'.

**Why it's forbidden.** Aitzaz's contamination argument: if the mind sees the answers, nothing it does is real.

**How it's checked.** Automatic: the interface test fails the build if an ID or nature field reaches the mind package. It checks by name every world-side log field in the schema (PLACEHOLDER-64), including gaze_target, verdict_subject, probe_role, hidden_nature, kind_id and creature_id. Automatic: the leak test (swapped natures give identical observations until the first eat). Automatic: a code check for references to essence, core or free labels in mind code. Behavioural: B6 (contamination canary) must be flagged by T0 every time.

## 19. Recognition caches keyed on world objects

**What it is.** Frankie may not remember 'object number 17 is food'; it may only remember what it observed.

**Why it's forbidden.** Keying on identity would let Frankie skip recognition.

**How it's checked.** Automatic: follows from the interface test (no IDs reach the mind). Review of any cache.

## 20. Designer-chosen essence weights or a pre-loaded memory

**What it is.** Claude or Aitzaz may not set which traits matter. Hand-set perception must be neutral, and memory starts empty.

**Why it's forbidden.** Designer knowledge of the answer may not become the starting point. Essence must come from evolution and lifetime learning (P3, P4).

**How it's checked.** Automatic: a test that hand-set relevance weights are all equal (PLACEHOLDER-88, cohort PC1) and that memory is empty at birth. Evolution starts from random genomes, checked against the run log.

## 21. Textbook best-split attention ('check whichever trait best separates the candidates')

**What it is.** Inner layers may not pick the most informative trait the way a decision tree does. The outer layers' guesses fix which traits get checked.

**Why it's forbidden.** D13 chose Aitzaz's outside-in option over the textbook optimum.

**How it's checked.** Review of the tower design note against PLACEHOLDER-14. Automatic: a scan for 'information_gain', 'gini' and 'entropy' in tower code.

## 22. Shortest-path planners, or a conventional planner patched in

**What it is.** Frankie moves by greedy steps. No route-finding algorithm (such as A* or breadth-first search) and no multi-step planner may be added.

**Why it's forbidden.** D11 leaves plan elimination open for Aitzaz to design. The hard rule says a missing property is reported, never rescued with a conventional mechanism (P2).

**How it's checked.** Automatic: a scan for 'astar', 'dijkstra', 'bfs' and 'plan'. Review: any new mechanism needs its own ledger row and Aitzaz's approval.

## 23. Macro actions in the proposal menu

**What it is.** The menu holds only small primitive moves, with no ready-made routines such as 'push X toward Y' or 'go around the barrier'.

**Why it's forbidden.** Macros would let a single proposal draw count as a 'novel approach'. D14 excludes anything one menu draw can produce (PLACEHOLDER-66).

**How it's checked.** Automatic: the proposal menu is listed in a frozen file, and a test compares the code's menu with it. Review.

## 24. Evolved or inherited choice settings (temperament, reserve, sharp-look spending, randomness curve, creature-observation channels)

**What it is.** Evolution may tune only perception. It may not shape how Frankie chooses, its temperament, when it pays for a look, or how it perceives other creatures.

**Why it's forbidden.** Aitzaz: 'evolution only shapes our recognition systems' (P4). D7 and D8. M49 keeps creature-observation channels out of the genome.

**How it's checked.** Automatic: the genome schema test lists the allowed fields, and any other field fails the build. Stage 7 gate: temperament must matter more than genome.

## 25. Fitness terms other than net food energy

**What it is.** Evolution may score creatures only by food energy gained minus poison energy lost, and nothing else.

**Why it's forbidden.** Hard rule. A curiosity, imitation or novelty term would breed the very behaviours the tests are meant to discover.

**How it's checked.** Automatic: the fitness function is fingerprinted before the first run and its fingerprint is checked every run. Review.

## 26. Promoting a baseline, twin, off-switch version or test fixture into Frankie

**What it is.** Comparison minds and cheating mocks may never become part of Frankie, even if they work better.

**Why it's forbidden.** Guardrail: conventional twins can never be promoted by default, and any fallback after a failed gate needs Aitzaz's approval.

**How it's checked.** Automatic: the import guard forbids the mind from importing the baselines (B0-B9, G01-G18), twins (TW1-TW7) or test-fixtures (MK1-MK10) packages. Automatic: off-switch versions (OS01-OS21 and OS23; OS22 retired) exist only as configuration flags recorded in the version field, and a claim run labelled 'full' is refused if any flag is set. OS18 (trust locked at full), OS19 (character off) and OS23 (tower off, random choice) are test-only flags kept in a test-fixtures module, never in the mind package; the harness refuses any of them in a run labelled 'full', and the 'randomness never chooses' rule applies to version full only. Review: any fallback is logged with Aitzaz's initials. The test-only flags OS18, OS19 and OS23 are applied by a wrapper on the test side of the mind's interface, never by code inside the mind package.

## 27. Automatic switch from spiking to rate-based neurons

**What it is.** If spiking neurons fail a check, the code may not quietly swap to ordinary neurons.

**Why it's forbidden.** D12: Aitzaz decides what happens next.

**How it's checked.** Automatic: claim runs record the neuron type in the log header, and the harness refuses a rate-based mind (TW7) for claims unless the ledger holds Aitzaz's approval. Review.

## 28. Unlisted constants or rules in the mind

**What it is.** No number or rule may appear in mind code unless it has a ledger row or a register row.

**Why it's forbidden.** Aitzaz's fear that Claude fills gaps with textbook defaults. The register of unspecified details is the defence.

**How it's checked.** Automatic: the test that no unlisted constants appear in mind code (from the proposal); each constant must cite its register row (PLACEHOLDER-nn or KT-nn) or ledger row. Review against the register.

## 29. A cheap taste action (nibble), or any taste without a real eat

**What it is.** Frankie may not learn taste without the full risk of eating.

**Why it's forbidden.** D16.

**How it's checked.** Automatic: the action-set test lists the allowed actions; taste values appear in the observation packet only on the tick after an eat.

## 30. Tuning the mind on sealed test material

**What it is.** No one may adjust Frankie after seeing how it does on real test kinds.

**Why it's forbidden.** Aitzaz's contamination argument; D1.

**How it's checked.** Automatic: the vault-open log (each vault opened once, with its seed revealed publicly). 'Changed after seeing test X' flags in the ledger. The mind and genomes are frozen before the final vault is generated. No pass mark, N or design constant changes after results are seen (X39).

## 31. Forced eats or harness energy changes outside the registered policy

**What it is.** The test harness may force Frankie to eat something, or change its energy, only at the points listed in advance. There is no hidden help, and no energy reset to keep a struggling Frankie alive.

**Why it's forbidden.** A forced eat makes 'Frankie chose to eat' untrue and plants an experience Frankie did not choose; an unlisted energy change does the same for hunger. Both would blur what Frankie earned by itself (D1, contamination argument).

**How it's checked.** Automatic: the harness refuses a designed exposure unless its test and point are on the PLACEHOLDER-85 list (T7, T9, T10 and T13 may never force an eat), and refuses any energy change that is not one of the injections listed in W45 (type and point: energy-set at probes, including C1's R + 40 repeat, at T9 arena entry for C8 HIGH/LOW, at C13-M2 energy clamps and at T13 room entry; yoke-adjust; top-up). Every forced eat is logged with action_provenance=designed-exposure and every energy change as an injection_events row with vault provenance; both are printed on the priors card. There is no survival floor (W46): energy is never reset at 0. T0 audit: the log is compared with the frozen spec. On the kill-test bench, the only injection allowed is the kill-test energy-set listed in W45.

