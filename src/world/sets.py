"""Sets of families: tuning, practice and kill-run (section 3, KT-14, KT-38, KT-42).

The tuning set is families 1 to 30 of the tuning key. Throwaway practice
families from the same key are numbered 1,001 and up. A kill-run set's key
comes from a Bitcoin block hash (keys.kill_run_set_key), which does not exist
until that set's code is frozen.
"""

from . import constants as C
from . import keys
from .kinds import generate_family, neutral_kind


class SeparationError(RuntimeError):
    """A kill-run check kind failed the separation certificate (KT-38)."""


def tuning_families() -> list:
    key = keys.tuning_set_key()
    return [generate_family("tuning", key, n) for n in range(1, C.N_TUNING_FAMILIES + 1)]


def practice_family(number: int, core_override=None):
    """A throwaway practice family from the tuning key (section 3)."""
    if number < C.PRACTICE_FAMILY_START:
        raise ValueError("practice families are numbered 1,001 and up")
    return generate_family("practice", keys.tuning_set_key(), number, core_override)


def power_check_family_number(simulated_set: int, place: int) -> int:
    """Simulated set s, place i uses practice family 1,000 + (s - 1) x 120 + i (KT-42)."""
    if simulated_set < 1 or not 1 <= place <= 120:
        raise ValueError("simulated sets start at 1, places run from 1 to 120")
    return 1_000 + (simulated_set - 1) * 120 + place


def kill_run_families(set_name: str, block_hash_hex: str, n_families: int) -> list:
    key = keys.kill_run_set_key(block_hash_hex)
    return [generate_family(set_name, key, n) for n in range(1, n_families + 1)]


def _all_kinds(family) -> list:
    return ([family.H] + [family.lookalike_kinds[k] for k in range(1, C.N_LOOKALIKE_KINDS + 1)]
            + [family.neutral_kinds[k] for k in range(1, C.N_NEUTRAL_KINDS + 1)])


def separation_failures(set_name: str, set_key: bytes, families, plans=(), tuning=None) -> list:
    """The separation certificate for a kill-run set (section 3, KT-38).

    Every check kind (look-alike kinds 3 to 8, and every neutral kind a run
    used, replacements included) must have been drawn from its own set's key,
    and must not match any tuning kind's whole record exactly. Returns the
    failures; empty when the set passes.
    """
    tuning = tuning if tuning is not None else tuning_families()
    tuning_records = {k.record() for fam in tuning for k in _all_kinds(fam)}
    out = []

    def check(kind, fresh, where):
        if kind.record() != fresh.record() or kind.set_name != set_name:
            out.append(f"{where}: not drawn from {set_name}'s key")
        if kind.record() in tuning_records:
            out.append(f"{where}: matches a tuning kind")

    for fam in families:
        fresh = generate_family.__wrapped__(set_name, set_key, fam.number)
        for k in range(3, C.N_LOOKALIKE_KINDS + 1):
            check(fam.lookalike_kinds[k], fresh.lookalike_kinds[k], f"family {fam.number} lookalike-{k}")
        for k in range(1, C.N_NEUTRAL_KINDS + 1):
            check(fam.neutral_kinds[k], fresh.neutral_kinds[k], f"family {fam.number} neutral-{k}")
    for plan in plans:
        for k, kind in plan.neutral_kinds.items():
            fresh = neutral_kind(set_name, set_key, plan.family_number, k, kind.try_number)
            check(kind, fresh, f"family {plan.family_number} run {plan.run_number} neutral-{k}")
    return out


def require_separation(set_name: str, set_key: bytes, families, plans=(), tuning=None) -> None:
    """Stop with an error if the separation certificate fails (KT-38, KT-88)."""
    failures = separation_failures(set_name, set_key, families, plans, tuning)
    if failures:
        raise SeparationError("; ".join(failures))
