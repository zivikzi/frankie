"""K-F's spiking units (D12, section 6, KT-59 to KT-62, KT-125) and K-F itself through the frozen harness.

- The Numba step and the pure-NumPy reference step give the same doubles, bit
  for bit, over long random runs at every value on the tuning grid (section 6).
- Hand-worked cases fix the order inside a substep: decay, push-down, input or
  rest, threshold; the trace; push-down from the substep before; groups that
  are not live held at rest.
- At the start values, a perfect copy of a remembered kind makes its neurons
  fire and wins, an empty memory settles on "unknown", and two identical kinds
  tie and stay unsettled (the near-tie risk of section 11), which the
  stability log records (KT-127).
- K-F's entry: the per-spike cost (KT-27), settings limited to the closed
  list (KT-126), OS10 (section 4, KT-77), and the same record in its own
  process as in this one (KT-93).
"""

import dataclasses
import itertools
import pathlib
import sys

import numpy as np
import pytest

from harness import scoring
from harness.agents import tower_minds
from harness.host import InProcessHost
from harness.readings_cache import ReadingCache
from harness.run import run_one
from mind import constants as K
from mind import entry
from mind.memory import Kind, Memory
from mind.spiking import SHARES, SpikingUnits, _substep, substep_reference
from mind.tower import HOLD_BROKE, LEADS_UNKNOWN, UNKNOWN, UNSETTLED, Race
from world import keys
from world.run_plan import generate_run

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import mind_checks  # noqa: E402

GRID = {"leak": (0.025, 0.05, 0.1, 0.2, 0.4), "threshold": (0.625, 1.25, 2.5, 5, 10),
        "refractory_ms": (0, 1, 2, 4, 8), "inhibition": (0.078, 0.156, 0.3125, 0.625, 1.25)}   # TUNING_PLAN.md
POSITIONS = list(range(K.N_TRAITS))
BIRTH = {"reserve_milli": 40000, "boldness": 0.3, "trait_order": list(range(K.N_TRAITS))}


def settings(**kw):
    return K.Settings(**kw)


def numba_step(units, inputs, live):
    units.substep(np.asarray(inputs, dtype=float), np.asarray(live, dtype=bool))


def reference_step(state, inputs, live, s):
    charge, resting, trace, pending = state
    out = substep_reference(charge, resting, trace, pending, np.asarray(inputs, dtype=float),
                            np.asarray(live, dtype=bool), 1.0 - s.leak, float(s.threshold), int(s.refractory_ms),
                            float(s.inhibition))
    return out[:4], out[4]


# ------------------------------------------------------------------ the two steps agree, bit for bit

def same_bits(a, b):
    return np.asarray(a).tobytes() == np.asarray(b).tobytes()


@pytest.mark.parametrize("leak,threshold,refractory_ms,inhibition",
                         [(0.1, 2.5, 2, 0.3125)] + [tuple(v) for v in itertools.islice(
                             itertools.product(*GRID.values()), 3, None, 61)])
def test_numba_and_the_numpy_reference_agree_bit_for_bit(leak, threshold, refractory_ms, inhibition):
    s = settings(leak=leak, threshold=threshold, refractory_ms=refractory_ms, inhibition=inhibition)
    rng = np.random.default_rng(12)
    groups = 9
    units = SpikingUnits(groups, s)
    state = (units.charge.copy(), units.resting.copy(), units.trace.copy(), units.pending.copy())
    live = np.ones(groups, dtype=bool)
    spikes = 0
    for t in range(400):
        if t % 37 == 5:
            live = rng.random(groups) > 0.2
        if t % 53 == 11:
            g = int(rng.integers(groups))
            units.rest(g)
            charge, resting, trace, pending = (x.copy() for x in state)
            charge[g], resting[g], trace[g], pending[g] = 0.0, 0, 0.0, 0
            state = (charge, resting, trace, pending)
        inputs = np.round(rng.random(groups) * 6.0, 3) * (rng.random(groups) > 0.1)
        numba_step(units, inputs, live)
        state, made = reference_step(state, inputs, live, s)
        spikes += made
        assert same_bits(units.charge, state[0]) and same_bits(units.trace, state[2])
        assert np.array_equal(units.resting, state[1]) and np.array_equal(units.pending, state[3])
    assert units.spikes == spikes and spikes > 0


# ------------------------------------------------------------------ hand-worked cases (KT-59 to KT-62, KT-125)

def test_the_shares_run_from_an_eighth_to_fifteen_eighths_and_average_one():
    assert list(SHARES) == [(2 * k + 1) / 8 for k in range(8)] and float(np.mean(SHARES)) == 1.0


def test_one_group_by_hand():
    """leak 0.5, threshold 1, refractory 2, input 0.8: neuron k gets (2k + 1)/10."""
    s = settings(leak=0.5, threshold=1.0, refractory_ms=2, inhibition=0.25)
    u = SpikingUnits(1, s)
    made, n2 = [], []
    for _ in range(4):
        before = u.spikes
        numba_step(u, [0.8], [True])
        made.append(u.spikes - before)
        n2.append(float(u.charge[0, 2]))
    # substep 1: neurons 5-7 reach 1.1, 1.3, 1.5 and spike; 2: neurons 3 and 4 reach 1.05 and 1.35;
    # 3: neurons 5-7 still resting, 3 and 4 resting; 4: neurons 5-7 take input again and spike
    assert made == [3, 2, 0, 3]
    assert n2 == [0.5, 0.75, 0.875, 0.9375]                       # charge x 0.5 + 0.5, never firing
    d = K.TRACE_DECAY
    assert float(u.trace[0]) == ((3 * d + 2) * d + 0) * d + 3


def test_a_resting_neuron_ignores_its_input_for_the_refractory_period():
    for refractory in (0, 1, 4):
        u = SpikingUnits(1, settings(leak=0.5, threshold=1.0, refractory_ms=refractory, inhibition=0.25))
        times = []
        for t in range(12):
            numba_step(u, [8.0], [True])            # every neuron fires whenever it may
            if u.charge[0, 7] == 0.0 and u.resting[0, 7] == refractory:
                times.append(t)
        assert times == list(range(0, 12, refractory + 1))


def test_push_down_lands_in_the_next_substep_and_only_on_other_groups():
    s = settings(leak=0.5, threshold=1.0, refractory_ms=2, inhibition=0.25)
    u = SpikingUnits(2, s)
    numba_step(u, [8.0, 0.1], [True, True])          # group 0: all 8 spike; group 1: none
    assert int(u.pending[0]) == 8 and int(u.pending[1]) == 0
    assert float(u.charge[1, 7]) == 0.1 * SHARES[7]  # not pushed in the same substep
    numba_step(u, [0.0, 0.1], [True, True])
    assert float(u.charge[1, 7]) == 0.1 * SHARES[7] * 0.5 - 0.25 * 8 + 0.1 * SHARES[7]
    assert float(u.charge[0, 0]) == 0.0              # its own spikes never push it down (all were resting)


def test_a_group_that_is_not_live_is_held_at_rest_and_pushes_nothing():
    s = settings(leak=0.5, threshold=1.0, refractory_ms=2, inhibition=0.25)
    u = SpikingUnits(2, s)
    numba_step(u, [8.0, 0.1], [True, True])
    numba_step(u, [8.0, 0.1], [False, True])         # group 0 eliminated: its pending spikes are dropped
    assert float(u.trace[0]) == 0.0 and int(u.pending[0]) == 0 and not u.charge[0].any()
    u2 = SpikingUnits(2, s)
    numba_step(u2, [8.0, 0.1], [True, True])
    u2.rest(0)                                       # a knock-down: pending spikes go too (KT-125)
    numba_step(u2, [0.0, 0.1], [True, True])
    assert float(u2.charge[1, 7]) == 0.1 * SHARES[7] * 0.5 + 0.1 * SHARES[7]


def test_every_spike_is_paid_for_unknown_included():
    u = SpikingUnits(3, K.Settings())
    made = np.zeros(3, dtype=np.int64)
    for _ in range(50):
        numba_step(u, [0.0, 0.0, K.NEW_KIND_THRESHOLD], [True, True, True])     # "unknown" alone has input
        made += u.pending
    assert made[2] > 0 and made[0] == made[1] == 0 and u.spikes == int(made.sum())


# ------------------------------------------------------------------ the start values on hand-made cases

def memory_of(*values):
    m = Memory(K.Settings())
    for i, v in enumerate(values):
        m.kinds[i] = Kind(np.asarray(v, dtype=float), K.Settings().detector_width,
                          np.full(K.N_TRAITS, K.WEIGHT_START), 1, True)
    return m


def settle(memory, values, s=None):
    s = s or K.Settings()
    r = Race(memory, np.asarray(values, dtype=float), False, POSITIONS, s, SpikingUnits(len(memory.kinds) + 1, s))
    return r.run(), r


def an_object(seed=3):
    v = np.random.default_rng(seed).random(K.N_TRAITS) * 0.8 + 0.1
    v[K.TASTE_FROM:] = 0.0
    return v


def test_an_empty_memory_settles_on_unknown():
    out, r = settle(memory_of(), an_object())
    assert out.verdict == UNKNOWN and out.settle_step is not None and out.settle_step <= 10
    assert out.spikes > 0 and r.log["unsettled_why"] is None


def test_a_perfect_copy_makes_its_kind_fire_and_win():
    v = an_object()
    out, r = settle(memory_of(v), v)
    assert out.verdict == 0 and out.settle_step < K.LAST_WIN_STEP
    assert set(r.log["leaders"][-3:]) == {0}


def test_a_copy_among_strangers_names_its_own_kind():
    v = an_object()
    out, _ = settle(memory_of(an_object(5), v, an_object(9)), v)
    assert out.verdict == 1


def test_two_identical_kinds_tie_and_the_stability_log_shows_it():
    """Two kinds the reading fits identically get identical inputs: no noise breaks the tie (section 11's risk)."""
    v = an_object()
    out, r = settle(memory_of(v, v), v)
    assert out.verdict == UNSETTLED and out.settle_step is None
    assert r.log["unsettled_why"] == LEADS_UNKNOWN
    assert r.log["near_ties"] >= 20 and None in r.log["leaders"]


def test_the_stability_log_has_one_leader_per_step():
    out, r = settle(memory_of(an_object(5)), an_object())
    assert len(r.log["leaders"]) == r.log["last_step"]
    assert all(isinstance(x, (int, str)) or x is None for x in r.log["leaders"])
    assert HOLD_BROKE != LEADS_UNKNOWN


# ------------------------------------------------------------------ K-F's entry (KT-27, KT-126, OS10)

def born(**params):
    return entry.make(dict(BIRTH, params=params))


def test_k_f_runs_on_spiking_units_and_pays_per_spike():
    mind = born(spike_nano=40_000)
    info = mind.info()
    assert info["neuron"] == "spiking" and info["chooser"] == "satisficing"
    assert info["constants"]["unit_nano"][0] == 40_000 and info["version"] == [K.OS07]
    assert info["constants"]["group_neurons"] == [8, "D12, KT-61"]


@pytest.mark.parametrize("params,why", [
    ({}, "KT-27"), ({"spike_nano": -1}, "whole number"), ({"spike_nano": 1.5}, "whole number"),
    ({"spike_nano": 0, "tuned": {"gain": 2}}, "closed list"), ({"spike_nano": 0, "tuned": {"leak": "0.1"}}, "one number"),
    ({"spike_nano": 0, "tuned": {"leak": True}}, "one number"), ({"spike_nano": 0, "OS01": "cap"}, "Week 5"),
    ({"spike_nano": 0, "habits": 1}, "no birth parameter")])
def test_k_f_refuses_what_it_may_not_take(params, why):
    with pytest.raises(ValueError, match=why):
        born(**params)


def test_a_setting_the_search_tries_reaches_the_tower():
    mind = born(spike_nano=0, tuned={"leak": 0.2, "commit_margin": 4})
    table = mind.info()["constants"]
    assert table["leak"] == [0.2, "KT-19"] and table["commit_margin"] == [4, "KT-24"]
    assert table["threshold"] == [K.THRESHOLD, "KT-20"]


def test_os10_stores_no_taste_and_reads_none_after_eating():
    mind = born(spike_nano=0, OS10=True)
    assert mind.info()["version"] == [K.OS07, entry.OS10_RECORD]
    v = an_object()
    mind.decide(list(v[:K.N_VISIBLE]), 50_000)
    after = mind.land(15_000, 64_000, [0.9, 0.1, 0.2, 0.3])
    assert not set(after["log"]["checked"]["details"]) & set(range(K.TASTE_FROM, K.N_TRAITS))
    mind.write()
    c = mind.dump()["candidates"][0]
    assert c["ranges"][K.TASTE_FROM:] == [None] * 4 and c["weights_tenths"][K.TASTE_FROM:] == [None] * 4
    assert all(r is not None for r in c["ranges"][:K.TASTE_FROM])


def test_k_f_with_taste_reads_all_four_after_eating():
    mind = born(spike_nano=0)
    v = an_object()
    mind.decide(list(v[:K.N_VISIBLE]), 50_000)
    after = mind.land(15_000, 64_000, [0.9, 0.1, 0.2, 0.3])
    assert after["log"]["checked"]["details"][-4:] == list(range(K.TASTE_FROM, K.N_TRAITS))
    mind.write()
    assert all(r is not None for r in mind.dump()["candidates"][0]["ranges"])


# ------------------------------------------------------------------ through the frozen harness (KT-93)

def kf_spec(params, host="subprocess"):
    spec = tower_minds(params.get("spike_nano"))[0]
    if host == "in-process":
        return dataclasses.replace(spec, host="in-process", entry="mind.entry:make", params=params)
    return dataclasses.replace(spec, params=params)


@pytest.fixture(scope="module")
def plan():
    return generate_run("tuning", keys.tuning_set_key(), 3, 2)


def test_k_f_in_its_own_process_gives_the_in_process_record(plan):
    params = {"spike_nano": 25_000}
    a = run_one(plan, kf_spec(params), ReadingCache(plan.noise_key), package_dir=ROOT / "src" / "mind")
    b = run_one(plan, kf_spec(params, "in-process"), ReadingCache(plan.noise_key), host=InProcessHost(entry.make))
    assert a.decisions == b.decisions and a.lineage_log == b.lineage_log and a.info == b.info
    m = scoring.measures(a)
    assert 0 <= m["settle_rate"] <= 1 and a.info["neuron"] == "spiking"
    for d in a.decisions.values():
        th = d["mind"]["thinking"]
        assert th["unit"] == "spike" and th["count"] == d["mind"]["log"]["spikes"]
        assert d["thinking_milli"] == th["cost_milli"] == (2 * th["count"] * 25_000 + 10**6) // (2 * 10**6)


def test_the_mind_checks_pass_k_f_and_os10(plan):
    for params in ({"spike_nano": 25_000}, {"spike_nano": 25_000, "OS10": True}):
        spec = kf_spec(params)
        if params.get("OS10"):
            spec = dataclasses.replace(tower_minds(25_000)[3], params=params)
        res = mind_checks.run_checks(ROOT / "src" / "mind", spec, plans=[plan])
        assert res["failed"] == [] and res["review"] == [], [str(f) for f in res["failed"] + res["review"]]
