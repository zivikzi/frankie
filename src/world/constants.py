"""Every number the bench generator uses, each with the row it comes from.

Rows: charter/KILL_TEST.md (KT-01 to KT-18), kill-test/RULES.md (KT-30 to
KT-77, approved 25 Oct 2026), charter/REGISTER.md (PLACEHOLDER-nn) and
charter/LEDGER.md. Nothing here is tuned.
"""

# Units
NOISE_WIDTH = 0.01            # one noise width = one standard deviation of sensor noise, 1% of range (PLACEHOLDER-45)

# Kinds (KT-02, PLACEHOLDER-57)
N_CORE = 4                    # exactly 4 core traits per kind (KT-02)
CORE_BAND_WIDTH = 0.05        # each core band is 0.05 wide (KT-02, PLACEHOLDER-57)
CORE_CENTRE_LO = 0.025        # core band centre drawn uniformly from 0.025 ... (KT-02)
CORE_CENTRE_HI = 0.975        # ... to 0.975 (KT-02)
FREE_WIDTH_LO = 0.6           # free-range width drawn uniformly from 0.6 ... (KT-02, PLACEHOLDER-57)
FREE_WIDTH_HI = 1.0           # ... to 1.0 (KT-02)
N_LOOKALIKE_KINDS = 8         # 2 teaching kinds + 6 check kinds (KT-04)
N_NEUTRAL_KINDS = 4           # 4 neutral kinds per family (KT-02)

# Exact hue (KT-01)
HUE_OFFSET_MAX = 0.05         # apples, neutrals and warm-up members draw their hue offset within +-0.05 (KT-01)

# Look-alikes (KT-03)
LOOKALIKE_FREE_OFFSET = 0.10  # free traits copy the model within +-0.10 of range (KT-03, PLACEHOLDER-59)
MOVED_GAP_LO_NW = 20          # moved band's gap from H's band, in noise widths, from 20 ... (KT-03)
MOVED_GAP_HI_NW = 30          # ... to 30 (KT-03)

# Far apples and h2 (KT-03, KT-16)
FAR_HUE_SIZE_MIN = 0.3        # far apple's coarse hue and size each at least 0.3 from h1's (KT-03)

# Neutrals (KT-03, KT-43)
NEUTRAL_OUTSIDE_NW = 10       # at least 10 noise widths outside H's band ... (KT-03)
NEUTRAL_MIN_CORE = 2          # ... on 2 or more of H's core traits (KT-03)
NEUTRAL_SURFACE_LO = 0.9      # surface distance from h1 within 0.9 ... (KT-03 "within +-10%", KT-43)
NEUTRAL_SURFACE_HI = 1.1      # ... to 1.1 times the mean for P's far apples (KT-43)

# Warm-up (KT-06, KT-39)
N_WARMUP_KINDS = 4            # 1 nourishing, 1 poison, 2 "nothing" kinds (KT-06)
N_WARMUP_PER_KIND = 10        # 10 items from each kind, 40 forced tastes (KT-06)
WARMUP_CONTEXT_MIN_NW = 40    # warm-up scene and host at least 40 noise widths from h1's (KT-06)
WARMUP_KIND_GAP_NW = 10       # no warm-up core band within 10 noise widths of H's band ... (KT-03, KT-39)
WARMUP_KIND_MIN_CORE = 2      # ... on 2 or more of H's core traits (KT-03, KT-39)

# Taste limits, met by drawing inside them (KT-03, KT-07, KT-16)
H1_SWEET_MIN = 0.9            # t1 = h1 is super-sweet: sweet at least 0.9 ... (KT-07)
H1_SOUR_MAX = 0.1             # ... and sour at most 0.1 (KT-07)
A_SOUR_MAX = 0.5              # a2 to a4 have sour at most 0.5 (KT-07)
H2_SWEET_MAX = 0.1            # h2 is super-sour: sweet at most 0.1 ... (KT-16)
H2_SOUR_MIN = 0.9             # ... and sour at least 0.9 (KT-16)
H2_TASTE_DIST_NW = 10         # h2's taste at least 10 noise widths from h1's and a2's to a4's (KT-16)

# Check set Q (KT-16, section 5)
Q_NEAR = 0.10                 # Q's apples draw observable free traits within 0.10 of h1's or h2's (KT-03, section 5)

# Redraw exits (KT-03)
FAR_MAX_DRAWS = 10_000        # a far apple or h2 with no passing draw in 10,000 draws starts a cascade (KT-03)
H1_REDRAW_EVERY = 10          # every 10th cascade in a run redraws h1 (KT-03)
KIND_MAX_DRAWS = 1_000        # a neutral or warm-up kind with no passing object in 1,000 draws is replaced (KT-03)

# Runs (section 5)
R_MILLI_LO = 20_000           # reserve R drawn from 20 ... (M33), in whole milli-units (KT-48)
R_MILLI_HI = 60_000           # ... to 60 (M33, KT-48)
BOLDNESS_LO = 0.1             # boldness b drawn from 0.1 ... (M33)
BOLDNESS_HI = 0.6             # ... to 0.6 (M33)

# Sets (section 3, KT-42)
N_TUNING_FAMILIES = 30        # tuning set: 30 families (KT-43, section 3)
RUNS_PER_FAMILY = 10          # 10 runs per mind per family (KT-91, section 5)
PRACTICE_FAMILY_START = 1_001     # throwaway practice families are numbered 1,001 and up (KT-42, section 3)
GENERATOR_TEST_FAMILY_START = 200_001  # generator tests use practice families 200,001 and up (KT-42)

# Certificate re-checks (KT-91)
CHECK_TOLERANCE = 1e-12       # float rounding allowed when a finished plan's drawn bounds are re-checked; redraw rules compare exactly (KT-91)
