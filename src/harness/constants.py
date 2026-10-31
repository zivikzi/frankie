"""Every number the cafeteria harness uses, each with the row it comes from.

Rows: charter/KILL_TEST.md (KT-01 to KT-18), kill-test/RULES.md (KT-30 onward),
charter/REGISTER.md (PLACEHOLDER-nn) and charter/LEDGER.md. Energy is kept in
whole milli-units (KT-48): 1 unit of energy is 1,000 milli-units.
"""

# Energy (section 5, KT-48)
MILLI = 1_000                    # milli-units per energy unit (KT-48)
START_ENERGY_MILLI = 60_000      # start energy is 60 (section 5, B06)
NOURISH_MILLI = 15_000           # nourish gives +15 (section 5)
NOTHING_MILLI = 0                # nothing gives 0 (section 5)
POISON_MILLI = -20_000           # poison gives -20 (section 5)
RESET_ABOVE_R_MILLI = 10_000     # energy is set to R + 10 by a logged injection (section 5, W45 kill-test entry)
LOOK_MILLI = 30                  # one sharp look costs 0.03 per object (B13, KT-46)
CHECK_NANO = 1_000_000           # one check costs 0.001 (B14, KT-45, KT-46), in nano-units (KT-92)
NANO_PER_MILLI = 1_000_000       # thinking costs are summed exactly in nano-units (KT-48, KT-92)

# The run's schedule (section 5)
N_WARMUP = 40                    # 40 forced warm-up tastes (KT-06)
N_TEACHING = 8                   # 8 forced teaching tastes, t1 to t8 (KT-07)
N_PROBES = 20                    # P and Q each hold 20 probes (section 5)
DECISIONS_PER_RUN = 210          # 40 + 8 + 5 x 20 + 2 + 3 x 20 (section 5)
DECISIONS_PER_RUN_NOWARM = 170   # K-F-NOWARM skips the warm-up only (section 5)

# H-set rule (KT-12, section 8): which teaching tastes' new candidates join.
H_JOINING_TASTES = (3, 5, 7)     # a2, a3 and a4 are tastes t3, t5 and t7 (KT-07, KT-12)
