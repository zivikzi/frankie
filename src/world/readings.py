"""Noisy readings: the only way a mind sees an object (KT-33 to KT-36).

A reading is the true value plus keyed Gaussian noise, clipped to 0 to 1. The
noise is looked up by the replica key, the item's place and the trait, never
by role, kind or nature (KT-33), so every mind, and both sour-apple branches,
read the same item identically. Taste readings use the eaten item's place.
"""

from . import traits
from .objects import clip01
from .streams import sensor_noise


def read(noise_key: int, place: int, replica: int, values, trait_indices=traits.OBSERVABLE) -> dict:
    """One reading of the listed traits of an object: trait index -> value."""
    return {t: clip01(values[t] + sensor_noise(noise_key, place, replica, t)) for t in trait_indices}


def read_visible(plan, obj, replica: int) -> dict:
    """The 18 visible traits of an object in a run plan (one look, KT-35)."""
    return read(plan.noise_key, obj.place, replica, obj.values, traits.OBSERVABLE)


def read_taste(plan, obj, replica: int) -> dict:
    """The 4 taste traits, read once at a real eat (KT-35, FORBIDDEN 29)."""
    return read(plan.noise_key, obj.place, replica, obj.values, traits.TASTE_INDICES)
