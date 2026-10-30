"""What every bot and B1n-mind share: stored items, distances in noise widths, ties (KT-05, KT-100).

Distances are mean absolute differences, in noise widths, over the traits
named (section 4, KT-05). They are worked out one way everywhere, so they
replay bit for bit (I05, KT-100): the absolute differences are added left to
right in trait order, then divided by the number of traits and by the noise
width. That is world.objects.surface_distance's formula. "Within" and "at
most" include the bound; "above" and "farther than" exclude it.

Each item is stored at the moment it is eaten, as that decision's own reading
of the 18 visible traits and the energy the eat gave (section 4). Taste is
never stored or read.
"""

import numpy as np

from world import traits
from world.constants import NOISE_WIDTH

EXACT_NW = 5                 # "exact" means within 5 noise widths on every observable trait (KT-05)
SURFACE_NW = 10              # B2's and G05's surface-distance bound (KT-05)
CORE_NW = 8                  # B2e's per-core-trait bound: 5 for the band's width plus 3 for noise (KT-05)
RANGE_NW = 8                 # G07's and G08's "within 8 noise widths of the good items' range" (KT-05)
RARE_NW = 5                  # G06's rarity: the share of stored items within 5 noise widths (KT-05)
NEAR_COPY_NW = 10            # G17's and G18's trigger and near-copy bound (KT-05)
WARMUP_TASTES = 40           # the 40 forced warm-up tastes come first (KT-06)
TEACHING_TASTES = 8          # then t1 to t8 (KT-07); t1 is h1, the 41st item a bot stores

OBSERVABLE = traits.OBSERVABLE                                             # (KT-05)
SURFACE = traits.SURFACE                                                   # (PLACEHOLDER-91)
INNER = tuple(traits.INDEX[n] for n in traits.PARTS + traits.DETAILS)     # G16's traits (section 4)
H1_ITEM = WARMUP_TASTES      # index of h1 among the stored items


def mean_nw(stored: np.ndarray, o: np.ndarray, cols) -> np.ndarray:
    """Each stored item's mean absolute difference from o over cols, in noise widths (KT-100)."""
    acc = np.abs(stored[:, cols[0]] - o[cols[0]])
    for t in cols[1:]:
        acc = acc + np.abs(stored[:, t] - o[t])
    return acc / len(cols) / NOISE_WIDTH


def trait_nw(stored: np.ndarray, o: np.ndarray, cols) -> np.ndarray:
    """Each stored item's distance from o on each trait of cols, in noise widths."""
    return np.abs(stored[:, list(cols)] - o[list(cols)]) / NOISE_WIDTH


def exact(stored: np.ndarray, o: np.ndarray) -> np.ndarray:
    """Which stored items o exactly matches: within 5 noise widths on every observable trait (KT-05)."""
    return np.all(trait_nw(stored, o, OBSERVABLE) <= EXACT_NW, axis=1)


def nearest(dist: np.ndarray) -> int:
    """The index of the smallest distance; ties go to the most recent item (KT-05)."""
    return len(dist) - 1 - int(np.argmin(dist[::-1]))


class StoredItems:
    """Items in the order they were eaten: readings and the energy each gave."""

    def __init__(self):
        self.readings = np.zeros((0, len(OBSERVABLE)))
        self.outcomes = np.zeros(0, dtype=np.int64)

    def __len__(self):
        return len(self.outcomes)

    def add(self, reading: np.ndarray, outcome_milli: int):
        self.readings = np.vstack([self.readings, reading[None, :]])
        self.outcomes = np.append(self.outcomes, np.int64(outcome_milli))

    @property
    def good(self) -> np.ndarray:
        return self.outcomes > 0                  # "good" means outcome above 0 (KT-05)

    def dump(self):
        return {"items": [{"reading": r.tolist(), "outcome_milli": int(o)}
                          for r, o in zip(self.readings, self.outcomes)]}
