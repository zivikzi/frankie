"""The 'drawn uniformly' rules, checked as distributions over many practice runs.

A certificate can only check that each value is in range. These tests check
that values fill their ranges the way the frozen text says. Every draw is
keyed, so each test sees the same numbers every time: none is flaky. Each
bound below is at least 5 standard errors from the expected value.
"""

import statistics
from collections import Counter

import pytest

from world import constants as C
from world import keys, traits
from world import run_plan as rp
from world.kinds import generate_family

KEY = keys.tuning_set_key()
START = C.GENERATOR_TEST_FAMILY_START + 50_000


@pytest.fixture(scope="module")
def plans():
    return [rp.generate_run("practice", KEY, START + i, 1 + i % 10) for i in range(300)]


@pytest.fixture(scope="module")
def families():
    return [generate_family.__wrapped__("practice", KEY, START + 100_000 + i) for i in range(2000)]


def test_lookalike_offsets_fill_plus_minus_point_one(plans):
    offsets, taste_offsets = [], []
    for p in plans:
        models = {o.label: o for o in p.all_objects()}
        for o in [x for x in p.P + p.Q + p.teaching if x.role == "lookalike"]:
            m = models[o.model]
            for t in range(traits.N_TRAITS):
                if t in o.kind.bands or t in (traits.SCENE, traits.HOST, traits.EXACT_HUE):
                    continue
                if 0.1 < m.values[t] < 0.9:          # no clipping possible
                    (taste_offsets if t in traits.TASTE_INDICES else offsets).append(o.values[t] - m.values[t])
    for xs in (offsets, taste_offsets):
        assert min(xs) < -0.099 and max(xs) > 0.099 and all(abs(x) <= 0.1 for x in xs)
        assert abs(statistics.fmean(abs(x) for x in xs) - 0.05) < 0.002
        assert abs(statistics.fmean(xs)) < 0.002
        assert sum(1 for x in xs if x == 0.0) == 0


def test_moved_gaps_fill_20_to_30_noise_widths(families):
    gaps = []
    for f in families:
        for look in f.lookalike_kinds.values():
            for t in look.moved:
                a, b = look.bands[t], f.H.bands[t]
                gaps.append(max(a[0] - b[1], b[0] - a[1]))
    assert 0.2 <= min(gaps) < 0.201 and 0.299 < max(gaps) <= 0.3
    assert abs(statistics.fmean(gaps) - 0.25) < 0.001


def test_core_values_fill_their_bands(plans):
    pos = []
    for p in plans:
        for o in [p.h1] + [p.a[k] for k in (2, 3, 4)] + [x for x in p.P if x.role == "far_apple"]:
            for t, (lo, hi) in o.kind.bands.items():
                pos.append((o.values[t] - lo) / (hi - lo))
    assert abs(statistics.fmean(pos) - 0.5) < 0.02
    assert abs(statistics.pstdev(pos) - 12 ** -0.5) < 0.01
    assert min(pos) < 0.01 and max(pos) > 0.99


def test_hue_offsets_fill_plus_minus_point_05(plans):
    offs = [o.hue_offset for p in plans for o in [p.h1] + p.Q[:8] + p.warmup_items]
    assert -0.05 <= min(offs) < -0.0495 and 0.0495 < max(offs) < 0.05
    assert abs(statistics.fmean(offs)) < 0.002


def test_kind_ranges_and_centres(families):
    widths, starts_free, centres = [], [], []
    for f in families:
        for kind in [f.H] + list(f.neutral_kinds.values()):
            for t, (lo, hi) in kind.ranges.items():
                if kind is f.H and t in traits.TASTE_INDICES:
                    continue
                widths.append(hi - lo)
                starts_free.append(lo / (1 - (hi - lo)))
            centres += [(lo + hi) / 2 for lo, hi in kind.bands.values()]
    assert abs(statistics.fmean(widths) - 0.8) < 0.003 and min(widths) < 0.601 and max(widths) > 0.999
    assert abs(statistics.fmean(starts_free) - 0.5) < 0.005
    assert abs(statistics.fmean(centres) - 0.5) < 0.005
    assert min(centres) < 0.03 and max(centres) > 0.97


def test_temperament(plans):
    rs = [p.reserve_milli for p in plans]
    bs = [p.boldness for p in plans]
    # 300 runs: the standard error of the mean is 667 milli-units for R and 0.0083 for b
    assert min(rs) < 21_000 and max(rs) > 59_000 and abs(statistics.fmean(rs) - 40_000) < 3_400
    assert min(bs) < 0.11 and max(bs) > 0.59 and abs(statistics.fmean(bs) - 0.35) < 0.042


def test_q_window_fills_point_one_either_side(plans):
    d = []
    for p in plans:
        H = p.family.H
        for o in p.Q:
            if not o.label.startswith("Q-near"):
                continue
            ref = p.h1 if "h1" in o.label else p.h2
            for t in traits.OBSERVABLE:
                if t in H.bands or t in (traits.SCENE, traits.HOST, traits.EXACT_HUE):
                    continue
                lo, hi = H.ranges[t]
                if lo + 0.1 <= ref.values[t] <= hi - 0.1:      # window not cut by the range
                    d.append(o.values[t] - ref.values[t])
    assert min(d) < -0.099 and max(d) > 0.099 and abs(statistics.fmean(abs(x) for x in d) - 0.05) < 0.002


def test_warmup_context_uses_both_sides(plans):
    """Where both sides have room, each side is taken in proportion to its length (KT-06)."""
    below = expected = var = 0.0
    n = 0
    for p in plans:
        for t, attr in ((traits.SCENE, "scene"), (traits.HOST, "host")):
            ref = p.h1.values[t]
            left, right = max(0.0, ref - 0.4), max(0.0, 1 - (ref + 0.4))
            if left > 0.02 and right > 0.02:
                q = left / (left + right)
                for s in p.warmup_slots:
                    n += 1
                    below += getattr(s, attr) < ref
                    expected += q
                    var += q * (1 - q)
    assert n > 100
    assert abs(below - expected) < 5 * var ** 0.5


def test_keyed_shuffles_and_choices_are_uniform(plans, families):
    # trait order: each trait in each position equally often (KT-41)
    first = Counter(p.trait_order[0] for p in plans)
    assert len(first) == 22 and max(first.values()) < 35
    # warm-up order: the first item comes from each slot about equally (KT-41)
    first_slot = Counter(p.warmup_order[0][7] for p in plans)
    assert set(first_slot) == {"1", "2", "3", "4"} and min(first_slot.values()) > 37
    # the poison slot's kind is any of the 8 look-alike kinds (KT-41)
    poison_kind = Counter(p.warmup_slots[1].kind.name for p in plans)
    assert len(poison_kind) == 8 and min(poison_kind.values()) > 9
    # labels c1 to c4: H's lowest core trait takes each label equally often (KT-41)
    label_of_lowest = Counter(f.labels.index(f.H.core[0]) for f in families)
    assert all(abs(n - 500) < 110 for n in label_of_lowest.values())
    # kind 1's teaching pair is any of the 6 pairs (KT-30)
    from itertools import combinations
    pair_index = Counter(list(combinations(f.H.core, 2)).index(f.teaching_pairs[0]) for f in families)
    assert len(pair_index) == 6 and all(abs(n - 2000 / 6) < 100 for n in pair_index.values())
