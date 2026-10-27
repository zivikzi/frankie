"""Replayable randomness: keyed Philox counters (LEDGER W37, KT-31 to KT-34, KT-81, KT-82).

The generator is NumPy's Philox (Philox4x64-10), checked against Random123's
published test vectors in tests/test_philox.py. A Philox block is a pure
function of a 128-bit key and a 256-bit counter, so any number can be
recomputed on its own, in any order.

Counter layout, as four 64-bit words (W37's fields, KT-81):

    word 0  draw number = (try number << 32) | block number
    word 1  tick, which on the bench holds the place (KT-33)
    word 2  creature, always 0 on the bench, the same for every mind (KT-33)
    word 3  replica key (W52; 0 on the main line, KT-33)

Every object's place and every kind's place has its own try count, and try n
uses its own counter values (KT-32). So a redraw never changes another
place's random numbers.
"""

import math

import numpy as np

from .constants import NOISE_WIDTH

_TWO_64 = 1 << 64
_TWO_256 = 1 << 256
_UNIT = 2.0 ** -53
_BLOCKS_PER_FETCH = 8


def counter(draw: int, place: int, creature: int = 0, replica: int = 0) -> int:
    for word in (draw, place, creature, replica):
        if not 0 <= word < _TWO_64:
            raise ValueError("each counter word must fit in 64 bits")
    return draw | (place << 64) | (creature << 128) | (replica << 192)


def philox_blocks(key: int, start_counter: int, n_blocks: int) -> np.ndarray:
    """Philox4x64-10 output for counters start, start + 1, ..., as uint64 words.

    NumPy's Philox adds 1 to its counter before each block, so it is started
    one below the first counter wanted.
    """
    gen = np.random.Philox(counter=(start_counter - 1) % _TWO_256, key=key)
    return gen.random_raw(4 * n_blocks)


def to_unit(word) -> float:
    """A uniform number in [0, 1) from the top 53 bits of a 64-bit word (KT-82)."""
    return (int(word) >> 11) * _UNIT


class Draws:
    """The random numbers of one try at one place, read in a fixed order."""

    def __init__(self, key: int, place: int, try_number: int, creature: int = 0, replica: int = 0):
        if not 1 <= try_number < (1 << 32):
            raise ValueError("try numbers start at 1 and must fit in 32 bits")
        self.key = key
        self.place = place
        self.try_number = try_number
        self._next_counter = counter(try_number << 32, place, creature, replica)
        self._words = []
        self._pos = 0

    def _word(self) -> int:
        if self._pos == len(self._words):
            self._words = philox_blocks(self.key, self._next_counter, _BLOCKS_PER_FETCH).tolist()
            self._next_counter += _BLOCKS_PER_FETCH
            self._pos = 0
        word = self._words[self._pos]
        self._pos += 1
        return word

    def uniform(self) -> float:
        """Uniform in [0, 1)."""
        return to_unit(self._word())

    def between(self, lo: float, hi: float) -> float:
        """Uniform in [lo, hi)."""
        return lo + (hi - lo) * self.uniform()

    def index(self, n: int) -> int:
        """Uniform integer in 0 .. n - 1."""
        return min(int(self.uniform() * n), n - 1)

    def shuffled(self, items) -> list:
        """A uniform shuffle of items (Fisher-Yates, from the last position down)."""
        out = list(items)
        for i in range(len(out) - 1, 0, -1):
            j = self.index(i + 1)
            out[i], out[j] = out[j], out[i]
        return out

    def pick_without_replacement(self, items, k: int) -> list:
        """k items drawn uniformly without replacement, in the order drawn."""
        pool = list(items)
        return [pool.pop(self.index(len(pool))) for _ in range(k)]


def sensor_noise(noise_key: int, place: int, replica: int, trait: int) -> float:
    """One reading's noise, looked up by replica key, place and trait (KT-33).

    Gaussian with a standard deviation of one noise width (PLACEHOLDER-45),
    made from two keyed uniforms by Box-Muller (KT-34). The draw number is the
    trait's index, so every trait of every place has its own counter.
    """
    words = philox_blocks(noise_key, counter(trait, place, 0, replica), 1)
    u1 = to_unit(words[0])
    u2 = to_unit(words[1])
    return NOISE_WIDTH * math.sqrt(-2.0 * math.log(1.0 - u1)) * math.cos(2.0 * math.pi * u2)
