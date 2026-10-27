"""Kinds and families (KT-02, KT-03, KT-04, KT-30, KT-78, KT-79, KT-83).

A family is one apple kind H with its 8 look-alike kinds and 4 neutral kinds,
all drawn by the family key (section 2, Keys). Places on the family's world
stream:

    1        H
    2        the labels c1 to c4 of H's core traits
    3        the two teaching pairs (KT-30)
    11-18    look-alike kinds 1 to 8
    21-24    neutral kinds 1 to 4 (a replacement for one run uses the next try)
"""

from dataclasses import dataclass, field
from functools import lru_cache
from itertools import combinations

from . import constants as C
from . import keys, traits
from .streams import Draws

PLACE_H = 1
PLACE_CORE_LABELS = 2
PLACE_TEACHING_PAIRS = 3


def place_lookalike_kind(k: int) -> int:
    return 10 + k


def place_neutral_kind(k: int) -> int:
    return 20 + k


NOURISH = "nourish"
POISON = "poison"
NOTHING = "nothing"


@dataclass(frozen=True)
class Kind:
    """A kind record: world-side only, never shown to any mind (FORBIDDEN 18)."""

    name: str                      # "H", "lookalike-3", "neutral-2", ...
    nature: str                    # NOURISH, POISON or NOTHING
    family: int
    set_name: str
    place: int
    try_number: int
    core: tuple                    # H's or its own 4 core trait indices, in schema order
    bands: dict                    # core trait -> (lo, hi), each 0.05 wide
    ranges: dict                   # every other trait but exact hue -> (lo, hi)
    moved: tuple = ()              # look-alike kinds: the 2 core traits whose bands moved

    def record(self) -> tuple:
        """The kind record compared by the separation certificate (KT-38)."""
        return (
            self.core,
            tuple(sorted(self.bands.items())),
            tuple(sorted(self.ranges.items())),
        )


@dataclass(frozen=True)
class Family:
    set_name: str
    number: int
    key: bytes = field(repr=False)
    H: Kind
    labels: tuple                  # (c1, c2, c3, c4) as trait indices
    teaching_pairs: tuple          # (kind 1's pair, kind 2's pair), each a sorted pair of traits
    lookalike_kinds: dict          # 1..8 -> Kind
    neutral_kinds: dict            # 1..4 -> Kind

    def check_kind_for_pair(self, pair) -> Kind:
        """The check kind (3 to 8) that moves this pair of core traits."""
        wanted = tuple(sorted(pair))
        for k in range(3, 9):
            if self.lookalike_kinds[k].moved == wanted:
                return self.lookalike_kinds[k]
        raise KeyError(pair)

    def label_pair(self, a: int, b: int) -> tuple:
        """The traits behind labels ca and cb, e.g. label_pair(1, 2) for c1c2."""
        return tuple(sorted((self.labels[a - 1], self.labels[b - 1])))


# Kinds 3 to 8 take the 6 pairs in the order the addendum lists them:
# M1 = {c1c2, c3c4}, M2 = {c1c3, c2c4}, M3 = {c1c4, c2c3} (KT-04, KT-79).
CHECK_KIND_LABEL_PAIRS = {3: (1, 2), 4: (3, 4), 5: (1, 3), 6: (2, 4), 7: (1, 4), 8: (2, 3)}


def draw_base_kind(draws: Draws, name, nature, family, set_name, core_override=None) -> Kind:
    """An apple or neutral kind: 4 core bands and a range for every other trait.

    The order of draws: the 4 core traits (unless given), then each core
    band's centre in schema order, then each free range in schema order
    (width first, then where it sits) (KT-83). Taste always ranges over 0 to 1
    and takes no draw (KT-02, KT-78).
    """
    if core_override is None:
        core = tuple(sorted(draws.pick_without_replacement(traits.CORE_ELIGIBLE, C.N_CORE)))
    else:
        core = tuple(sorted(core_override))
        if len(core) != C.N_CORE or not set(core) <= set(traits.CORE_ELIGIBLE):
            raise ValueError("a core placement is 4 of the 13 eligible traits")
    half = C.CORE_BAND_WIDTH / 2
    bands = {}
    for t in core:
        centre = draws.between(C.CORE_CENTRE_LO, C.CORE_CENTRE_HI)
        bands[t] = (centre - half, centre + half)
    ranges = {}
    for t in traits.RANGED:
        if t in bands:
            continue
        if t in traits.TASTE_INDICES:
            ranges[t] = (0.0, 1.0)
            continue
        width = draws.between(C.FREE_WIDTH_LO, C.FREE_WIDTH_HI)
        lo = draws.between(0.0, 1.0 - width)
        ranges[t] = (lo, lo + width)
    return Kind(name, nature, family, set_name, draws.place, draws.try_number, core, bands, ranges)


def draw_lookalike_kind(draws: Draws, H: Kind, k: int, pair: tuple) -> Kind:
    """A poison kind that keeps H's bands on 2 core traits and moves the other 2.

    Each moved band is 0.05 wide. Its gap from H's band is drawn from 20 to 30
    noise widths first; the band then goes on whichever side has room (at
    random when both do) (KT-03). Per moved trait, in schema order: the gap,
    then a side draw, which is taken even when only one side has room.
    """
    width = C.CORE_BAND_WIDTH
    bands = dict(H.bands)
    for t in sorted(pair):
        gap = draws.between(C.MOVED_GAP_LO_NW * C.NOISE_WIDTH, C.MOVED_GAP_HI_NW * C.NOISE_WIDTH)
        side = draws.uniform()
        lo, hi = H.bands[t]
        below_ok = lo - gap - width >= 0.0
        above_ok = hi + gap + width <= 1.0
        if below_ok and (not above_ok or side < 0.5):
            bands[t] = (lo - gap - width, lo - gap)
        else:
            bands[t] = (hi + gap, hi + gap + width)
    return Kind(f"lookalike-{k}", POISON, H.family, H.set_name, draws.place, draws.try_number,
                H.core, bands, dict(H.ranges), moved=tuple(sorted(pair)))


def neutral_kind(set_name: str, set_key: bytes, family_number: int, k: int, try_number: int) -> Kind:
    """Neutral kind k of a family; try 1 is the family's own, later tries replace it for one run."""
    world = keys.stream_key(keys.family_key(set_key, family_number), keys.STREAM_WORLD)
    d = Draws(world, place_neutral_kind(k), try_number)
    return draw_base_kind(d, f"neutral-{k}", NOTHING, family_number, set_name)


@lru_cache(maxsize=4096)
def generate_family(set_name: str, set_key: bytes, family_number: int, core_override=None) -> Family:
    """Everything the family key draws (section 2, Keys)."""
    fam_key = keys.family_key(set_key, family_number)
    world = keys.stream_key(fam_key, keys.STREAM_WORLD)

    H = draw_base_kind(Draws(world, PLACE_H, 1), "H", NOURISH, family_number, set_name, core_override)

    labels = tuple(Draws(world, PLACE_CORE_LABELS, 1).shuffled(H.core))

    d = Draws(world, PLACE_TEACHING_PAIRS, 1)
    pairs = list(combinations(H.core, 2))
    first = pairs.pop(d.index(len(pairs)))
    second = pairs.pop(d.index(len(pairs)))
    teaching_pairs = (first, second)

    lookalikes = {}
    for k in (1, 2):
        lookalikes[k] = draw_lookalike_kind(Draws(world, place_lookalike_kind(k), 1), H, k, teaching_pairs[k - 1])
    for k, (a, b) in CHECK_KIND_LABEL_PAIRS.items():
        pair = tuple(sorted((labels[a - 1], labels[b - 1])))
        lookalikes[k] = draw_lookalike_kind(Draws(world, place_lookalike_kind(k), 1), H, k, pair)

    neutrals = {k: neutral_kind(set_name, set_key, family_number, k, 1) for k in range(1, C.N_NEUTRAL_KINDS + 1)}

    return Family(set_name, family_number, fam_key, H, labels, teaching_pairs, lookalikes, neutrals)
