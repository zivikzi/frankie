"""Drawing single objects from a kind (KT-01, KT-03, KT-37, KT-83).

The order of draws within one try is fixed by these functions: every trait in
schema order (exact hue excepted), then the hue offset. A trait whose value is
set from outside (h1's scene and host, a warm-up kind's scene and host) takes
no draw.
"""

from dataclasses import dataclass

from . import constants as C
from . import traits
from .kinds import Kind
from .streams import Draws

# Roles (section 2). World-side only: no mind ever sees these (FORBIDDEN 18).
APPLE = "apple"
FAR_APPLE = "far_apple"
LOOKALIKE = "lookalike"
NEUTRAL = "neutral"
COPY = "copy"
WARMUP = "warmup"
MODEL = "model"          # a fresh apple that a warm-up poison item copies; never shown


@dataclass(frozen=True)
class WorldObject:
    label: str               # "h1", "a2", "t2", "warmup-2-07", "P-far-3", "Q-look-h2-1", ...
    place: int               # its place in the run plan (streams.py)
    try_number: int          # the try that passed; 0 for a copy, which takes no draw
    role: str
    kind: Kind
    values: tuple            # the 22 true values, in schema order
    hue_offset: float
    model: str = ""          # label of the model, for look-alikes and copies

    @property
    def nature(self) -> str:
        return self.kind.nature


def clip01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def draw_member(draws: Draws, kind: Kind, context=None, limits=None, near=None) -> tuple:
    """A member of kind: core values inside its bands, free values inside its ranges.

    context: (scene, host) to use instead of drawing them.
    limits:  trait -> (lo, hi), a limit the draw meets by drawing inside it
             (taste limits, KT-03).
    near:    (traits, values), draw each listed trait inside its range and
             within Q_NEAR of the given value (Q's apples, section 5).
    Returns (values, hue_offset).
    """
    limits = limits or {}
    near_traits, near_values = near if near else ((), None)
    values = [0.0] * traits.N_TRAITS
    for t in range(traits.N_TRAITS):
        if t == traits.EXACT_HUE:
            continue
        if context is not None and t in (traits.SCENE, traits.HOST):
            values[t] = context[0] if t == traits.SCENE else context[1]
            continue
        lo, hi = kind.bands[t] if t in kind.bands else kind.ranges[t]
        if t in limits:
            lo, hi = max(lo, limits[t][0]), min(hi, limits[t][1])
        if t in near_traits:
            lo, hi = max(lo, near_values[t] - C.Q_NEAR), min(hi, near_values[t] + C.Q_NEAR)
        if lo > hi:
            raise ValueError(f"empty draw interval on {traits.TRAITS[t]}")
        values[t] = draws.between(lo, hi)
    offset = draws.between(-C.HUE_OFFSET_MAX, C.HUE_OFFSET_MAX)
    values[traits.EXACT_HUE] = clip01(values[traits.COARSE_HUE] + offset)
    return tuple(values), offset


def draw_lookalike(draws: Draws, kind: Kind, model_values, model_offset: float, context) -> tuple:
    """A look-alike of kind, copying its model (KT-03).

    Core values are drawn inside the kind's bands (2 kept from H, 2 moved).
    Every other trait but scene, host and exact hue, taste included, is the
    model's value plus an offset within +-0.10, clipped to 0 to 1. Scene and
    host are given; exact hue is the look-alike's coarse hue plus the model's
    hue offset (KT-01).
    Returns (values, hue_offset).
    """
    values = [0.0] * traits.N_TRAITS
    for t in range(traits.N_TRAITS):
        if t == traits.EXACT_HUE:
            continue
        if t in (traits.SCENE, traits.HOST):
            values[t] = context[0] if t == traits.SCENE else context[1]
        elif t in kind.bands:
            values[t] = draws.between(*kind.bands[t])
        else:
            off = draws.between(-C.LOOKALIKE_FREE_OFFSET, C.LOOKALIKE_FREE_OFFSET)
            values[t] = clip01(model_values[t] + off)
    values[traits.EXACT_HUE] = clip01(values[traits.COARSE_HUE] + model_offset)
    return tuple(values), model_offset


def surface_distance(a, b) -> float:
    """Mean absolute difference over the object-layer traits, in noise widths (PLACEHOLDER-91)."""
    return sum(abs(a[t] - b[t]) for t in traits.SURFACE) / len(traits.SURFACE) / C.NOISE_WIDTH


def taste_distance(a, b) -> float:
    """Mean absolute difference over the 4 taste traits, in noise widths (KT-16)."""
    return sum(abs(a[t] - b[t]) for t in traits.TASTE_INDICES) / len(traits.TASTE_INDICES) / C.NOISE_WIDTH


def gap_outside(value: float, band) -> float:
    """How far a value lies outside a band (0 if inside)."""
    lo, hi = band
    return lo - value if value < lo else value - hi if value > hi else 0.0


def band_gap(a, b) -> float:
    """The gap between two bands' edges; negative when they overlap (KT-39)."""
    return max(a[0] - b[1], b[0] - a[1])
