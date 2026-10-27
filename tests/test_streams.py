"""Keyed Philox streams and their noise (W37, KT-32 to KT-34)."""

import math

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from philox_reference import philox4x64, words
from world.streams import Draws, counter, sensor_noise, to_unit

KEY = 0x0123456789ABCDEF_FEDCBA9876543210


def test_counter_layout():
    assert counter(1, 2, 3, 4) == 1 | (2 << 64) | (3 << 128) | (4 << 192)
    with pytest.raises(ValueError):
        counter(1 << 64, 0)
    with pytest.raises(ValueError):
        counter(0, -1)


def test_to_unit_is_in_zero_one():
    assert to_unit(0) == 0.0
    assert 0.0 < to_unit((1 << 64) - 1) < 1.0
    assert to_unit(1 << 63) == 0.5


@settings(max_examples=100, deadline=None)
@given(st.integers(1, 1000), st.integers(1, (1 << 32) - 1), st.integers(0, 2), st.integers(0, 10_000))
def test_draws_read_the_counters_of_their_place_and_try(place, try_number, creature, replica):
    d = Draws(KEY, place, try_number, creature, replica)
    got = [d.uniform() for _ in range(70)]          # crosses two fetches of 8 blocks
    first = counter(try_number << 32, place, creature, replica)
    want = []
    for b in range(18):
        want += [to_unit(w) for w in philox4x64(words(first + b, 4), words(KEY, 2))]
    assert got == want[:70]


def test_a_place_and_try_give_the_same_numbers_whatever_was_drawn_before():
    a = [Draws(KEY, 5, 2).uniform() for _ in range(3)]
    for p in range(1, 50):
        Draws(KEY, p, 1).uniform()
    assert [Draws(KEY, 5, 2).uniform() for _ in range(3)] == a
    assert Draws(KEY, 5, 2).uniform() != Draws(KEY, 5, 3).uniform()
    assert Draws(KEY, 5, 2).uniform() != Draws(KEY, 6, 2).uniform()


def test_try_numbers_start_at_one():
    with pytest.raises(ValueError):
        Draws(KEY, 1, 0)


def test_index_shuffle_and_pick():
    d = Draws(KEY, 9, 1)
    assert all(0 <= d.index(7) < 7 for _ in range(500))
    items = list(range(22))
    s = d.shuffled(items)
    assert sorted(s) == items and s != items
    p = d.pick_without_replacement(range(13), 4)
    assert len(set(p)) == 4 and all(0 <= x < 13 for x in p)


def test_shuffle_is_uniform_on_three_items():
    d = Draws(KEY, 11, 1)
    counts = {}
    for _ in range(6000):
        key = tuple(d.shuffled("abc"))
        counts[key] = counts.get(key, 0) + 1
    assert len(counts) == 6
    assert all(abs(c - 1000) < 150 for c in counts.values())


def test_sensor_noise_is_gaussian_with_sd_one_noise_width():
    x = np.array([sensor_noise(KEY, place, 0, trait) for place in range(1, 1001) for trait in range(20)])
    assert abs(x.mean()) < 0.0003
    assert abs(x.std() - 0.01) < 0.0003
    assert abs(np.mean(np.abs(x) < 0.01) - 0.6827) < 0.015


def test_sensor_noise_is_a_pure_lookup():
    a = sensor_noise(KEY, 300, 1002, 4)
    sensor_noise(KEY, 300, 1003, 4)
    assert sensor_noise(KEY, 300, 1002, 4) == a
    assert sensor_noise(KEY, 300, 1003, 4) != a
    assert sensor_noise(KEY, 301, 1002, 4) != a
    assert sensor_noise(KEY, 300, 1002, 5) != a
    assert math.isfinite(a)
