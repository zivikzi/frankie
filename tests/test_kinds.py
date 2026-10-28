"""Families: H, its look-alike kinds and its neutral kinds (KT-02 to KT-04, KT-30, KT-37)."""

from itertools import combinations

from hypothesis import given, settings
from hypothesis import strategies as st

from world import constants as C
from world import keys, traits
from world.certificates import band_gap, verify_family
from world.kinds import CHECK_KIND_LABEL_PAIRS, generate_family

KEY = keys.tuning_set_key()
FAMILIES = st.integers(C.GENERATOR_TEST_FAMILY_START, C.GENERATOR_TEST_FAMILY_START + 10**6)


def fresh(n):
    return generate_family.__wrapped__("practice", KEY, n)


@settings(max_examples=300, deadline=None)
@given(FAMILIES)
def test_every_family_passes_its_certificates(n):
    assert verify_family(fresh(n)) == []


def test_the_tuning_families_pass_their_certificates():
    for n in range(1, C.N_TUNING_FAMILIES + 1):
        assert verify_family(generate_family("tuning", KEY, n)) == []


@settings(max_examples=50, deadline=None)
@given(FAMILIES)
def test_a_family_is_a_pure_function_of_its_key(n):
    a, b = fresh(n), fresh(n)
    assert a.H.record() == b.H.record()
    assert a.labels == b.labels and a.teaching_pairs == b.teaching_pairs
    assert [k.record() for k in a.lookalike_kinds.values()] == [k.record() for k in b.lookalike_kinds.values()]
    assert fresh(n + 1).H.record() != a.H.record()


def test_check_kinds_take_the_pairs_in_the_listed_order():
    fam = fresh(C.GENERATOR_TEST_FAMILY_START)
    c = fam.labels
    for k, (x, y) in CHECK_KIND_LABEL_PAIRS.items():
        assert fam.lookalike_kinds[k].moved == tuple(sorted((c[x - 1], c[y - 1])))
    assert {fam.lookalike_kinds[k].moved for k in range(3, 9)} == set(combinations(fam.H.core, 2))


def test_draw_statistics_over_many_families():
    fams = [fresh(C.GENERATOR_TEST_FAMILY_START + i) for i in range(2000)]
    # KT-30: the two teaching pairs share a trait in 4 of 5 families.
    share = sum(1 for f in fams if set(f.teaching_pairs[0]) & set(f.teaching_pairs[1])) / len(fams)
    assert abs(share - 0.8) < 0.03
    # KT-02: each of the 13 eligible traits is core in 4/13 of kinds.
    for t in traits.CORE_ELIGIBLE:
        rate = sum(1 for f in fams if t in f.H.core) / len(fams)
        assert abs(rate - 4 / 13) < 0.04
    # KT-03: when both sides fit, a moved band goes on each side half the time,
    # so it takes the side with less room half the time too.
    shorter = n = 0
    for f in fams:
        for k in range(1, 9):
            look = f.lookalike_kinds[k]
            for t in look.moved:
                lo, hi = f.H.bands[t]
                if lo - 0.35 >= 0 and hi + 0.35 <= 1 and lo != 1 - hi:
                    n += 1
                    went_below = look.bands[t][1] <= lo
                    shorter += went_below == (lo < 1 - hi)
    assert n > 1000 and abs(shorter - n / 2) < 5 * n ** 0.5 / 2


def test_taste_ranges_full_for_h_drawn_for_neutral_kinds():
    """Section 2: H's taste ranges over 0 to 1; any other kind's taste is a free trait (KT-78)."""
    widths = []
    for i in range(300):
        f = fresh(C.GENERATOR_TEST_FAMILY_START + i)
        assert all(f.H.ranges[t] == (0.0, 1.0) for t in traits.TASTE_INDICES)
        for look in f.lookalike_kinds.values():
            assert all(look.ranges[t] == (0.0, 1.0) for t in traits.TASTE_INDICES)
        for kind in [f.H] + list(f.neutral_kinds.values()) + list(f.lookalike_kinds.values()):
            assert set(kind.core).isdisjoint(traits.TASTE_INDICES)
        for kind in f.neutral_kinds.values():
            for t in traits.TASTE_INDICES:
                lo, hi = kind.ranges[t]
                assert 0.0 <= lo and hi <= 1.0
                widths.append(hi - lo)
    assert 0.6 <= min(widths) < 0.61 and 0.99 < max(widths) < 1.0
    assert abs(sum(widths) / len(widths) - 0.8) < 0.01


def test_natures():
    f = fresh(C.GENERATOR_TEST_FAMILY_START + 3)
    assert f.H.nature == "nourish"
    assert {k.nature for k in f.lookalike_kinds.values()} == {"poison"}
    assert {k.nature for k in f.neutral_kinds.values()} == {"nothing"}


def test_band_gap_sign():
    assert band_gap((0.1, 0.15), (0.3, 0.35)) == 0.3 - 0.15
    assert band_gap((0.1, 0.15), (0.12, 0.17)) < 0
