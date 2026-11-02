# Kill-test addendum: E1 takes K-F's place

_FRANKIE · addendum to `charter/KILL_TEST.md` v3 · 2 Nov 2026 · frozen with set A's code manifest (`freeze/killtest-code-v1-set-A.sha256`), before set A's key exists_

## In plain words

K-F, the spiking tower the kill test was written for, failed its own check on the tuning set in Week 4. Exploring afterwards on the tuning set, we found a simpler elimination mind, **E1**, that beat trial and error on families it was never chosen on.

This addendum withdraws K-F, puts E1 in its place, and leaves everything else exactly as the frozen kill test wrote it: the objects, the bots, the pass marks, the judge, the set size and the way the set's key is drawn. E1 is then tested **once**, on **set A**: 40 fresh families that nobody, Claude included, can see or choose until a Bitcoin block after this freeze exists.

## 1. Why

- **K-F is withdrawn before any kill-run set existed.** In Week 4, K-F's logged tuning search found no setting that reached every target. At the setting it ended on, the check on the kept-back half gave NO-GO: settle rate 0.553, CopyAccept 0.726, D_learn 0.158 against a floor of 0.239 (`kill-test/TUNED.md`, `kill-test/results/week4-diagnosis.md`). No set-A manifest was ever pushed, so no kill-run key exists.
- **E1 was found afterwards, by exploration on the tuning set** (`explore/`, branch history from `claude/frankie-lab`). Every version was tried on the 15 odd tuning families. The 15 even ones were used only to check, once after the Lab's exploration and once after the sour fix, and never to choose. **28 logged runs on the odd half** (`explore/results/variants.jsonl`):
  - 25 Lab variants, including 2 ablations;
  - E1 measured again after its move into the `mind` package;
  - the sour fix;
  - E1-OS10, the taste-blind control.
- **Section 1 of KILL_TEST.md** says that after results are seen, no rule or number may change, and that any later kill test needs a new addendum. This is that addendum. It changes **who is judged**, never how.

## 2. The mind under test

**E1** (`src/mind/e1.py`, made by `mind.entry.make` with the birth parameter `"mind": "E1"`) is an elimination mind with kind merging. Its pieces, each labelled:

- **Memory** (conventional): a list of kinds, each with a range per trait, a relevance per trait (tenths, starting at 5 on every trait, M20) and an eat record.
- **Looking: elimination outside in** (untested). Layer by layer (context, object, parts, details), each kind adds up its relevance-weighted misses; a miss is a reading more than **10 noise widths** outside the kind's range. A kind is eliminated once its total is **above 1.0**.
  - No kind left: "unknown". Several left: the fewest misses, then the most eats, then the oldest.
  - After an eat, the 4 tastes join the details layer.
- **Writing:**
  - "unknown": a new kind (conventional);
  - an outcome matching the kind's founding outcome: a stretch, and a trait that widened by more than **10 noise widths** loses **5 tenths** (conventional);
  - otherwise a split: the parent gains **2 tenths** on every trait more than 10 noise widths outside it, and the new kind copies the parent's relevance (K-F's blame idea; untested).
- **Merging, after every write** (conventional, like merging clusters, with two untested rules). Two kinds with the same founding outcome merge when they overlap within 10 noise widths:
  - always on scene and host (untested);
  - and on every trait whose relevance is above **5 tenths**.

  The merged kind:
  - takes the union of the two kinds' ranges;
  - takes the higher relevance of the two on each trait;
  - loses 5 tenths on any trait the merge widened by more than 10 noise widths (untested);
  - keeps both kinds' records.

  The older kind survives.
- **Taste keeps its relevance** (the sour fix, untested): widening lowers relevance on the 18 visible traits only.
- **Choosing:** the bench drive unchanged (section 5, `mind/drive.py`), with reliability 1. E1 pays the look (0.03) and 0.001 per check (B14, as TW7 does); a check is one kind on one trait.

**Controls and reported versions** (section 4's roles, for E1):

| Mind | What | Role |
|---|---|---|
| E1-OS10 | E1 with taste out of memory and out of the verdict after eating (section 4's OS10) | Rule 5's validity check: it must be classed as not noticing in at least 90% of its runs |
| E1 no merging | E1 with merging off | Reported |
| E1 all at once | E1 checking every layer at once (OS01's idea) | Reported |
| B1n-bot-r, B1n-mind | Trial and error, at their registered radii | The floor, as in section 9 |
| B2e and every must-fail bot | Unchanged | Positive control and rule 6, as in section 9 |

## 3. What stays exactly as frozen

Everything in `charter/KILL_TEST.md` v3 and bench v1.1 (`freeze/killtest-bench-v1.1.sha256`, tag `charter-killtest-bench-v1.1`) holds as written:

- the objects, the generator and every certificate;
- the run (section 5), the checks P and Q, and SOUR and SWEET-CONTROL;
- every bot, rule 6 and the positive control;
- every measure (section 8), every pass mark and GO rule (section 9), and the verdict order;
- the frozen judge (`src/harness/judge.py`): its bootstrap, its seed, its subgroups, and nearest-rank reading;
- the set size, **40 families** of 10 runs each (section 7's power check);
- the key procedure (section 3, KT-14, KT-31): set A's key is the SHA-256 of the hash of Bitcoin block N + 6, where N is read from the timestamp Action's upgrades of this manifest's first proof (`kill-test/read_set_a_key.py` applies section 3's rule; anyone can check it with the `ots` client and a block explorer);
- the limit of at most two sets (section 3).

**Where E1 takes K-F's place,** word for word:

- In sections 3 and 9, every "K-F" is E1, and section 9's "OS10" is E1-OS10.
- Rule 1 (settle rate) judges E1's decisions, which always settle (it decides by elimination, with no race). The rule is applied as written.
- Rule 2, rule 3 (the floor, the margin and the bootstrap), rules 4, 4b and 4c (with their subgroups), rule 5 and rule 7 judge E1 exactly as they would have judged K-F.
- Section 10's "TW7 vs K-F", "TW2 vs K-F", OS01 and K-F-NOWARM are not run: they are K-F's twins and switches. E1's reported versions take their place.

## 4. The set and the run

- **Set A,** under this manifest. It is unused: no set-A manifest has ever been pushed (section 3).
- **The run** (`kill-test/e1_kill_run.py kill-run A <block hash> kill-test/results/E1-set-A.json`) runs once, in section 3's frozen order:
  1. it generates the set from its key and certifies every plan, including the separation from the tuning set;
  2. it runs every non-tower mind, then judges rule 6 before any tower mind runs, and retires the set with no verdict if rule 6 fails;
  3. it runs E1, E1-OS10 and the reported versions, each in its own sandboxed process;
  4. it calls the frozen judge;
  5. it prints the verdict table before any per-family result.
- **Before running,** it checks that every file still matches this manifest. It never writes over a result.
- **The report** goes to `kill-test/results/E1-set-A.md`.

## 5. What the verdict means for E1

- **GO.** Every rule holds on set A. E1's elimination with merging beats trial and error on fresh families, and the design goes forward to a trimmed version 1 (section 12), with E1 in K-F's place.
- **NO-GO.** Rule 1, rule 2 or rule 3's bootstrap fails. E1 is not better than trial and error on fresh families, and we stop and rethink with Aitzaz.
- **INCONCLUSIVE.** E1 beats trial and error but misses another rule (rule 3's margin, 4, 4b, 4c, 5 or 7). Aitzaz may approve exactly one design change; E1 is then frozen again and judged on set B, and that second evaluation is final (sections 3 and 9).

## 6. Before the freeze: E1 on the tuning set

Each figure is the mean of 15 family means, 10 runs each. The floor is the better of B1n-bot-r and B1n-mind.

| Measure | Odd half (chosen on) | Even half (checked once) | Pass mark |
|---|---|---|---|
| Settle rate | 1.000 | 1.000 | 0.95 |
| CopyAccept | 0.999 | 1.000 | 0.80 |
| D_learn | 0.428 (floor 0.251) | 0.435 (floor 0.239) | floor + 0.15, and 0.25 |
| FarMinusNeutral | 0.511 | 0.506 | 0.15 |
| LookReject h1 / far | 0.867 / 0.897 | 0.858 / 0.890 | 0.60 each |
| Q after SOUR | 0.826 | 0.820 | 0.25 |
| Sour drop | 0.010 | 0.004 | at most 0.15 |
| Noticed (E1-OS10 not noticing) | 0.993 (1.000) | 0.993 (1.000) | 0.50 (0.90) |
| D at check 1 | −0.282 | −0.276 | below 0.15 |

The dry run on all 30 tuning families, made by the same driver in the same order, gave **GO** (`kill-test/results/E1-dry-run-tuning.json`). It is not an independent check, since the odd half was used to choose E1:

| Rule | Result |
|---|---|
| 1. Settle rate | 1.000 |
| 2. CopyAccept | 0.999 |
| 3. D_learn against the floor | 0.431 against B1n-bot-r's 0.2445; bootstrap 0 of 10,000 at or below 0 |
| 4b. FarMinusNeutral | 0.508 |
| 4c. LookReject | 0.863 / 0.893 |
| 5. Sour test | sour drop 0.007, Q 0.823, noticed 0.993, E1-OS10 quiet 1.000 |
| 7. D at check 1 | −0.279 |

Rules 4, 4b and 4c held in every subgroup. Rule 6 held.

## 7. New rows (KT-132 to KT-138)

These rows are frozen with this addendum. Aitzaz approves them together with the freeze.

| Row | Rule |
|---|---|
| KT-132 | **E1 and its settings,** as section 2 states them. Each number is one value for every trait and layer: miss tolerance 10 noise widths, elimination above 1.0 weighted misses, widening line 10 noise widths, split +2 tenths, widening −5 tenths, merge cut-off 5 tenths. The switches are merging on, outside-in on, context gating on, merge widening on, and taste keeps its relevance. All were set by exploration on the odd tuning half (section 1), not by section 7's closed list, which belonged to K-F. |
| KT-133 | **Merges in the frozen harness's words.** The harness knows no merge (KT-74). An eat whose own new kind or split child is absorbed in the same write is reported as a stretch of the older kind it joined, which is where the eat now sits. Any other kind absorbed is reported as a forget. The older kind always survives, so h1's kind, the oldest in its scene, is never forgotten, and the harness's H set (KT-12, KT-98) stays right. |
| KT-134 | **E1 reports its neuron type as "rate".** The frozen protocol accepts only "spiking" or "rate" for a tower mind. E1 has no neurons; its verdicts come from weighted totals, never spikes. |
| KT-135 | **The sour fix.** A trait that widens a lot loses relevance (KT-132), except the 4 tastes: a kind's tastes vary, but how it usually tastes is what lets a surprising taste stand out. Without it, E1 noticed the sour apple in 47% of runs on the odd half; with it, 99%. D_learn moved from 0.434 to 0.428. (Untested.) |
| KT-136 | **E1-OS10.** E1 with the birth parameter `"OS10": true`. It stores no taste (its dumps show no taste ranges or weights), its verdict after eating reads no taste, and blame never reaches a taste. |
| KT-137 | **The driver.** `kill-test/e1_kill_run.py` runs as section 4 of this addendum says, calling only frozen pieces: `bench.run_set`, `judge.rule6`, `run_one` in each mind's own process, `scoring.measures`, `judge.judge` with E1's runs, the floor mind's runs and E1-OS10's runs, `judge.programme_outcome`, and `kill_run.verdict_table`. The bootstrap's resamples are keyed by the set's name, "A". It doesn't use the frozen `kill_run.run_kill_set`, which requires a tower mind labelled K-F. The dry run on the tuning set uses the name "tuning". |
| KT-138 | **The mind checks for E1** (section 7, step 5). They run through `tools/mind_checks.run_checks` with E1's own entry, because the frozen command line only knows the registry's labels. Every check passes for E1 and E1-OS10, with no findings: the import guard, the word and constant scans, the interface and leak checks, the birth check (with KT-133's reporting), and the counter check (`tests/test_e1.py`). E1's records in its own process match its records in-process, decision for decision. |

## 8. What is frozen

Set A's code manifest covers:
- the bench (`freeze/killtest-bench-v1.1.sha256`'s paths);
- `src/mind` (E1, and K-F's untouched code) and `src/twins`;
- `kill-test/e1_kill_run.py`, `kill-test/read_set_a_key.py` (which reads N from the committed proofs by section 3's rule, calendar by calendar) and this addendum.

The manifest names set A, so it fixes set A's key. Pushing it to `main` starts the timestamp, and that cannot be undone.
