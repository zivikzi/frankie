"""Sets (section 3, KT-38, KT-42) and noisy readings (KT-33 to KT-35)."""

import copy
import dataclasses

import pytest

from world import constants as C
from world import keys, readings, sets, traits
from world import run_plan as rp
from world.kinds import generate_family

# A made-up block hash, used only to test the code path. It is not a kill-run
# set: those keys come from Bitcoin blocks after each code freeze (KT-14).
TEST_HASH = "5e" * 32


def test_power_check_family_numbers():
    assert sets.power_check_family_number(1, 1) == 1_001
    assert sets.power_check_family_number(2, 1) == 1_121
    assert sets.power_check_family_number(1, 120) == 1_120
    with pytest.raises(ValueError):
        sets.power_check_family_number(1, 121)
    with pytest.raises(ValueError):
        sets.practice_family(1_000)


def test_core_override_copies_only_the_core_placement():
    """KT-42: the override copies which 4 traits are core; everything else is drawn fresh."""
    n, m = C.GENERATOR_TEST_FAMILY_START + 400, C.GENERATOR_TEST_FAMILY_START + 401
    source = generate_family.__wrapped__("practice", keys.tuning_set_key(), m)
    fam = generate_family.__wrapped__("practice", keys.tuning_set_key(), n, source.H.core)
    again = generate_family.__wrapped__("practice", keys.tuning_set_key(), n, source.H.core)
    assert fam.H.core == source.H.core
    assert fam.H.bands != source.H.bands and fam.H.ranges != source.H.ranges
    assert fam.H.record() == again.H.record()
    plain = generate_family.__wrapped__("practice", keys.tuning_set_key(), n)
    assert fam.neutral_kinds[1].record() == plain.neutral_kinds[1].record()   # the rest of the family is n's own


def test_separation_passes_on_a_fresh_set():
    key = keys.kill_run_set_key(TEST_HASH)
    fams = [generate_family("test-set", key, n) for n in range(1, 6)]
    plans = [rp.generate_run("test-set", key, n, 1) for n in range(1, 6)]
    assert sets.separation_failures("test-set", key, fams, plans) == []
    sets.require_separation("test-set", key, fams, plans)


def test_separation_checks_each_runs_neutral_kinds():
    key = keys.kill_run_set_key(TEST_HASH)
    fam = generate_family("test-set", key, 2)
    plan = rp.generate_run("test-set", key, 2, 1)
    tuning_kind = generate_family("tuning", keys.tuning_set_key(), 9).neutral_kinds[2]
    bad = copy.copy(plan)
    bad.neutral_kinds = {**plan.neutral_kinds, 2: dataclasses.replace(tuning_kind, try_number=2)}
    out = sets.separation_failures("test-set", key, [fam], [bad])
    assert any("run 1 neutral-2: matches a tuning kind" in m for m in out)
    assert any("run 1 neutral-2: not drawn from" in m for m in out)


def test_separation_catches_a_tuning_kind():
    key = keys.kill_run_set_key(TEST_HASH)
    fam = generate_family("test-set", key, 1)
    tuning_kind = generate_family("tuning", keys.tuning_set_key(), 4).lookalike_kinds[6]
    bad = dataclasses.replace(fam, lookalike_kinds={**fam.lookalike_kinds, 6: tuning_kind})
    out = sets.separation_failures("test-set", key, [bad])
    assert any("matches a tuning kind" in m for m in out)
    assert any("not drawn from" in m for m in out)
    with pytest.raises(sets.SeparationError):
        sets.require_separation("test-set", key, [bad])


@pytest.fixture(scope="module")
def plan():
    return rp.generate_run("practice", keys.tuning_set_key(), C.GENERATOR_TEST_FAMILY_START + 9, 4)


def test_readings_are_the_same_for_every_mind_and_differ_by_replica(plan):
    item = plan.P[0]
    r1 = readings.read_visible(plan, item, rp.replica_p(2, 1))
    assert readings.read_visible(plan, item, rp.replica_p(2, 1)) == r1
    assert readings.read_visible(plan, item, rp.replica_p(4, 1)) != r1
    assert set(r1) == set(traits.OBSERVABLE)
    assert all(abs(r1[t] - item.values[t]) < 0.06 for t in r1)


def test_taste_is_read_apart(plan):
    t = readings.read_taste(plan, plan.h1, rp.REPLICA_MAIN)
    assert set(t) == set(traits.TASTE_INDICES)


def test_sweet_control_reads_like_h2(plan):
    """SOUR's h2 and SWEET-CONTROL share h2's place and the branches' replica key (KT-16, KT-33)."""
    v = list(plan.h2.values)
    for t, x in zip(traits.TASTE_INDICES, (0.95, 0.05, 0.3, 0.3)):
        v[t] = x
    control = dataclasses.replace(plan.h2, values=tuple(v))
    r = rp.REPLICA_SOUR_BRANCHES
    assert readings.read_visible(plan, control, r) == readings.read_visible(plan, plan.h2, r)


def test_readings_are_clipped():
    v = [0.0] * 11 + [1.0] * 11
    r = readings.read(12345, 7, 0, v, range(22))
    assert all(0.0 <= x <= 1.0 for x in r.values())
    assert any(x == 0.0 for x in r.values()) and any(x == 1.0 for x in r.values())
