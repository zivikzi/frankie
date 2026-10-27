"""NumPy's Philox against Random123's published test vectors (W37, KT-31)."""

from pathlib import Path

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from philox_reference import philox4x64, words
from world.streams import philox_blocks

KAT = Path(__file__).parent / "data" / "random123_philox4x64_kat.txt"


def kat_rows():
    rows = []
    for line in KAT.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        name, rounds, *hexes = line.split()
        assert name == "philox4x64"
        vals = [int(h, 16) for h in hexes]
        rows.append((int(rounds), tuple(vals[0:4]), tuple(vals[4:6]), tuple(vals[6:10])))
    return rows


def test_kat_file_has_all_six_vectors():
    assert sorted(r[0] for r in kat_rows()) == [7, 7, 7, 10, 10, 10]


@pytest.mark.parametrize("rounds,ctr,key,expected", kat_rows())
def test_reference_matches_random123(rounds, ctr, key, expected):
    assert philox4x64(ctr, key, rounds) == expected


@pytest.mark.parametrize("rounds,ctr,key,expected", [r for r in kat_rows() if r[0] == 10])
def test_numpy_philox_matches_random123(rounds, ctr, key, expected):
    counter = sum(w << (64 * i) for i, w in enumerate(ctr))
    key_int = key[0] | (key[1] << 64)
    assert tuple(int(w) for w in philox_blocks(key_int, counter, 1)) == expected


@settings(max_examples=200, deadline=None)
@given(st.integers(0, (1 << 256) - 1), st.integers(0, (1 << 128) - 1), st.integers(1, 5))
def test_numpy_philox_matches_reference_on_any_counter(counter, key, n):
    got = philox_blocks(key, counter, n)
    for b in range(n):
        want = philox4x64(words((counter + b) % (1 << 256), 4), words(key, 2))
        assert tuple(int(w) for w in got[4 * b: 4 * b + 4]) == want


def test_numpy_is_philox4x64_10():
    assert np.random.Philox().state["bit_generator"] == "Philox"
