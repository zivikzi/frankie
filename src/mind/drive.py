"""K-F's drive on the bench: eat or skip, from the verdict, the named kind's record and energy (section 5).

This is the second of the drive's two copies (KT-44), written in Week 3 from
section 5's text and rows KT-44 to KT-50. A test outside the mind package
requires it to give the same chances, picks and no-safe-option flags as
B1n-mind's copy on the frozen grid (tests/data/drive_grid.json, KT-102).

Section 5, as this copy reads it:

- An "unknown" or "unsettled" verdict is a skip, and the chooser does not
  run: no option is listed and no fallback is taken (KT-102).
- Otherwise eat is considered first, then skip (KT-08). Habits are off
  (OS07) and there are no proposals, so each option's source is "bench"
  (KT-49).
- Eat's chance = 1 - (1 - share) x (2 - reliability), and never below 0
  (PLACEHOLDER-05). The share is the part of the named kind's own eats on
  record after which energy stayed at or above R.
- Skip's chance is 1 if energy, less this decision's thinking cost, is at
  least R, and 0 if not.
- The bar is 0.9 - 0.3 x b (PLACEHOLDER-27). The first option whose chance
  reaches it is taken (M29). If none does, the higher chance is taken and
  the choice is tagged as the M47 fallback; equal chances mean skip (KT-50).

Every chance is an IEEE double worked out in the order section 5 writes it
(KT-102). Energies and costs are whole milli-units (KT-48, KT-92).
"""

from mind import constants as K

EAT = "eat"
SKIP = "skip"
BENCH = "bench"                          # an ordinary bench choice (KT-49)
FALLBACK = "no-safe-option-fallback"     # the M47 fallback's tag (glossary, KT-49)


def share_above(above_flags) -> float:
    """The part of a kind's eats on record after which energy stayed at or above R (section 5)."""
    eats = len(above_flags)
    if eats == 0:
        raise ValueError("a named kind with no eats on record has no chance to give (KT-50, FORBIDDEN 8)")
    return sum(1 for a in above_flags if a) / eats


def choose(named: bool, share, reliability, energy_milli: int, thinking_milli: int, reserve_milli: int,
           boldness: float, untried_tally=None) -> tuple:
    """One bench decision. Returns (the drive trace of KT-49, its provenance).

    share and reliability are read only when the verdict names a kind.
    """
    bar = K.BAR_TOP - K.BAR_SLOPE * boldness
    if energy_milli - thinking_milli >= reserve_milli:
        skip_chance = 1.0
    else:
        skip_chance = 0.0
    trace = {"eat_chance": None, "skip_chance": skip_chance, "bar": bar, "pick": SKIP, "options_considered": [],
             "no_safe_option": False, "untried_tally": untried_tally}
    if not named:
        return trace, BENCH
    eat_chance = 1.0 - (1.0 - share) * (K.WRONG_FACTOR_TOP - reliability)
    if eat_chance < 0.0:
        eat_chance = 0.0
    trace["eat_chance"] = eat_chance
    listed = trace["options_considered"]
    for option, chance in ((EAT, eat_chance), (SKIP, skip_chance)):
        reaches = chance >= bar
        listed.append({"order": len(listed) + 1, "source": BENCH, "option": option,
                       "predicted_p_above_R": chance, "cleared_bar": reaches})
        if reaches:
            trace["pick"] = option
            return trace, BENCH
    trace["no_safe_option"] = True
    if eat_chance > skip_chance:
        trace["pick"] = EAT
    else:
        trace["pick"] = SKIP                # equal chances mean skip (KT-50)
    return trace, FALLBACK


def thinking_milli(units: int, unit_nano: int) -> int:
    """units x unit cost, summed exactly, rounded to the nearest milli-unit with halves up (KT-48, KT-92)."""
    return (units * unit_nano + K.HALF_MILLI_NANO) // K.NANO_PER_MILLI
