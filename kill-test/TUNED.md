# The tuned values (KT-19 to KT-29), set on the KT tuning set

_2 Nov 2026. Section 7 of [KILL_TEST.md](../charter/KILL_TEST.md) gives each tuned value its own register row, marked "set on KT tuning set", together with the log. This file is that register. The log is [`results/tuning-search.jsonl`](results/tuning-search.jsonl)._

**No setting reached every tuning target.** The logged search of [TUNING_PLAN.md](TUNING_PLAN.md) measured 57 settings on the search half over 3 passes and stopped as step 5 says. On 2 Nov 2026 at 10:53 UTC Aitzaz chose to go on to the kill test with the setting the search ended on, though it reached no target ("Run the kill test"). [`tune_continue.py`](tune_continue.py) then carried out steps 6 to 8 from that setting, appending to the same log. Why K-F falls short: [`results/week4-diagnosis.md`](results/week4-diagnosis.md).

| Row | Number | Start value | Set on KT tuning set | How |
|---|---|---|---|---|
| KT-19 | Leak | 0.1 | **0.4** | Pass 1 kept it (fewest misses) |
| KT-20 | Threshold | 2.5 | **10** | Pass 1 kept it |
| KT-21 | Refractory period | 2 ms | **8 ms** | Pass 1 kept it |
| KT-22 | Inhibition strength | 0.3125 | **0.625** | Pass 1 kept it |
| KT-23 | Detector width | 4 noise widths | **5 noise widths** | Pass 1 kept it |
| KT-24 | Commit margin | 2 | **2** | Unchanged in every pass |
| KT-25 | Objection threshold | 0.5 | **2** | Pass 1 kept it |
| KT-26 | New-kind threshold | 0.5 | **0.5** | Unchanged in every pass |
| KT-27 | Per-spike cost | worked out | **2,915,888 nano-units** (0.002915888 per spike) | KT-47's rule at that setting: 0.001 × 312 median checks ÷ 107 median spikes, rounded (KT-129) |
| KT-28 | TW7 gain | 1 | **0.25** | TW7's 3 passes, with K-F's values (KT-131) |
| KT-29 | TW7 time constant | 10 ms | **10 ms** | Unchanged in every pass |

Passes 2 and 3 changed nothing for K-F or TW7. These values are in [`src/mind/constants.py`](../src/mind/constants.py) and [`src/twins/entry.py`](../src/twins/entry.py). TW2, OS01, OS10 and K-F-NOWARM reuse K-F's (section 7). None enters Frankie's M17 settings (FORBIDDEN 20).

## What the values give on the tuning set

The search half is the 15 odd families. The kept-back half is the 15 even ones, judged by the frozen judge exactly as a kill-run set.

| Measure | K-F, search half | K-F, kept-back | TW7, search half | TW7, kept-back | Pass mark |
|---|---|---|---|---|---|
| Settle rate | 0.571 | 0.553 | 0.983 | 0.984 | 0.95 |
| CopyAccept | 0.751 | 0.726 | 0.995 | 0.983 | 0.80 |
| D_learn (strict) | 0.136 | 0.158 | −0.058 | −0.058 | floor + 0.15, and 0.25 |
| The floor (B1n-bot-r) | 0.251 | 0.239 | 0.251 | 0.239 | |
| FarMinusNeutral | 0.271 | 0.296 | 0.003 | 0.005 | 0.15 |
| LookReject, h1 / far | 0.720 / 0.842 | 0.755 / 0.813 | 0.893 / 1.000 | 0.873 / 1.000 | 0.60 |
| Q after SOUR (strict) | −0.047 | −0.045 | 0.069 | 0.096 | 0.25 |
| Noticed share | 1.00 | 0.993 | | 1.00 | 0.50 |
| D at check 1 | −0.235 | −0.195 | | −0.107 | below 0.15 |

**The kept-back check (step 7):**
- **K-F: NO-GO**, "decisions don't settle; h1 wasn't learned". Rule 3's bootstrap had 9,948 of 10,000 resampled means at or below 0. OS10 never noticed the taste (1.00 quiet).
- **TW7: NO-GO**, "not better than brute trial and error".

Both checks are recorded, not stops, since Aitzaz chose to go on knowing the targets were not reached.

Measured again with KT-27's cost, K-F gave exactly the numbers it gave at a cost of 0, and its costliest decision came to 2.07 units (KT-126).

The search ran from `main` at c0b0814. `tune.py` now writes the agreed start values out in full, since `mind.constants` holds these values instead, so its code id differs from the log's. To replay the log, check out c0b0814.
