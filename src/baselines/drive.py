"""B1n-mind's copy of Frankie's drive on the bench (section 5, KT-08, KT-44 to KT-50).

This is the first of the drive's two copies (KT-44). It is written here from
section 5 and frozen with the bots in Week 2. The mind package writes its own
copy from section 5 in Week 3, without reading this one, and a test outside
both packages requires the two to give identical chances, choices and
no-safe-option flags on a frozen grid of inputs (tests/data/drive_grid.json).

Each object is one decision between eat and skip, considered in that order.
Habits are off (OS07) and there are no proposals, so every option's source is
"bench" (KT-49).

- An "unknown" or "unsettled" verdict is always a skip. The chooser does not
  run: no option is listed and no fallback is taken (section 5, KT-102).
- Eat's chance for a named candidate = 1 - (1 - share) x (2 - reliability),
  never below 0 (PLACEHOLDER-05). share is the share of the candidate's eats
  on record after which energy stayed at or above R.
- Skip's chance is 1 if energy minus the thinking cost is at least R, else 0.
- The bar is 0.9 - 0.3 x b (PLACEHOLDER-27). The first option whose chance
  reaches the bar is taken. If neither does, the M47 fallback takes the
  higher chance, equal chances meaning skip (KT-50), logged with
  no_safe_option = true and every option's cleared_bar = false.

All arithmetic is in IEEE double precision, in exactly the order written in
drive() below; energies are whole milli-units (KT-48, KT-102).
"""

BAR_TOP = 0.9               # the bar is 0.9 - 0.3 x b (PLACEHOLDER-27)
BAR_SLOPE = 0.3             # (PLACEHOLDER-27)
WRONG_FACTOR_TOP = 2.0      # the chance of being wrong is multiplied by (2 - reliability) (PLACEHOLDER-05)
VERDICT_STATES = ("named", "unknown", "unsettled")


def drive(verdict_state: str, share, reliability, energy_milli: int, thinking_milli: int,
          reserve_milli: int, boldness: float) -> dict:
    """One bench decision by the drive. Returns the drive trace (KT-49).

    share and reliability are ignored unless the verdict names a candidate.
    """
    if verdict_state not in VERDICT_STATES:
        raise ValueError(f"unknown verdict state {verdict_state!r}")
    bar = BAR_TOP - BAR_SLOPE * boldness
    skip_chance = 1.0 if energy_milli - thinking_milli >= reserve_milli else 0.0
    trace = {"eat_chance": None, "skip_chance": skip_chance, "bar": bar, "pick": "skip",
             "options_considered": [], "no_safe_option": False}
    if verdict_state != "named":
        return dict(trace, provenance="bench")
    eat_chance = max(0.0, 1.0 - (1.0 - share) * (WRONG_FACTOR_TOP - reliability))
    trace["eat_chance"] = eat_chance
    for order, (option, chance) in enumerate((("eat", eat_chance), ("skip", skip_chance)), 1):
        cleared = chance >= bar
        trace["options_considered"].append({"order": order, "source": "bench", "option": option,
                                            "predicted_p_above_R": chance, "cleared_bar": cleared})
        if cleared:
            return dict(trace, pick=option, provenance="bench")
    pick = "eat" if eat_chance > skip_chance else "skip"     # equal chances mean skip (KT-50)
    return dict(trace, pick=pick, no_safe_option=True, provenance="no-safe-option-fallback")
