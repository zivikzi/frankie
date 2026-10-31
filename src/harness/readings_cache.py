"""Readings computed once per run key and shared by every mind (KT-33, KT-35).

Every mind of a run sees the same objects with the same keys, so their
readings are the same numbers. This cache holds the noise, never the value
plus noise: SWEET-CONTROL shares h2's place and replica key and so its noise,
but not its taste values (KT-33). Each look's 18 visible traits, or each
eat's 4 taste traits, come from one Philox call over their consecutive
counters (trait, place, 0, replica); every number equals
world.streams.sensor_noise for that trait, which tests/test_harness.py checks.
"""

from world import traits
from world.objects import clip01
from world.streams import box_muller, counter, philox_blocks, to_unit


class ReadingCache:
    def __init__(self, noise_key: int):
        self.noise_key = noise_key
        self._noise = {}

    def _block(self, place: int, replica: int, first: int, n: int) -> tuple:
        key = (place, replica, first)
        out = self._noise.get(key)
        if out is None:
            w = philox_blocks(self.noise_key, counter(first, place, 0, replica), n).tolist()
            out = tuple(box_muller(to_unit(w[4 * k]), to_unit(w[4 * k + 1])) for k in range(n))
            self._noise[key] = out
        return out

    def visible(self, obj, replica: int) -> tuple:
        """The 18 visible traits of obj, in schema order (one look, KT-35)."""
        noise = self._block(obj.place, replica, traits.OBSERVABLE[0], len(traits.OBSERVABLE))
        return tuple(clip01(obj.values[t] + n) for t, n in zip(traits.OBSERVABLE, noise))

    def taste(self, place: int, replica: int, values) -> tuple:
        """The 4 taste traits of an item with these true values, read at the eat (KT-35)."""
        noise = self._block(place, replica, traits.TASTE_INDICES[0], len(traits.TASTE_INDICES))
        return tuple(clip01(values[t] + n) for t, n in zip(traits.TASTE_INDICES, noise))


assert traits.OBSERVABLE == tuple(range(18)) and traits.TASTE_INDICES == (18, 19, 20, 21)
