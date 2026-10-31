"""The cafeteria harness: schedule, energy, readings, the interface and the two hosts (section 5, KT-92 to KT-99).

Harness tests use tuning families only; practice families are for the power
check and the generator's tests (section 3).
"""

import dataclasses

import numpy as np
import pytest

from harness import agents, protocol, scoring
from harness import constants as C
from harness.readings_cache import ReadingCache
from harness.run import SOUR, SWEET, RunError, run_one, schedule
from test_fixtures import liars
from test_fixtures.stub import STUB_DIR, stub_spec
from world import keys, traits
from world.objects import clip01
from world.streams import sensor_noise
from world.readings import read
from world.run_plan import CHECKPOINTS, generate_run, replica_p, replica_q

KEY = keys.tuning_set_key()


@pytest.fixture(scope="module")
def plan():
    return generate_run("tuning", KEY, 2, 3)


@pytest.fixture(scope="module")
def cache(plan):
    return ReadingCache(plan.noise_key)


@pytest.fixture(scope="module")
def bot_records(plan, cache):
    return {s.label: run_one(plan, s, cache) for s in agents.non_tower_minds(None, 24, 24)}


@pytest.fixture(scope="module")
def stub_record(plan, cache):
    return run_one(plan, stub_spec(), cache, package_dir=STUB_DIR)


# ---------------------------------------------------------------- the schedule

def test_schedule_numbers_every_decision_once():
    s = schedule()
    assert len(s) == C.DECISIONS_PER_RUN == 210
    assert len(schedule(warmup=False)) == C.DECISIONS_PER_RUN_NOWARM == 170
    n = {key: i for i, key in enumerate(s, 1)}
    assert n[("warmup", 1)] == 1 and n[("warmup", 40)] == 40
    assert n[("teach", 1)] == 41 and n[("P", (1, 1))] == 42 and n[("P", (1, 20))] == 61
    assert n[("teach", 2)] == 62 and n[("teach", 8)] == 128 and n[("P", (8, 20))] == 148
    assert n[("branch", SOUR)] == 149 and n[("branch", SWEET)] == 150
    assert n[("Q", ("S8", 1))] == 151 and n[("Q", (SWEET, 20))] == 210
    assert sum(1 for k, _ in s if k == "P") == 100 and sum(1 for k, _ in s if k == "Q") == 60


# ---------------------------------------------------------------- readings

def test_reading_cache_equals_the_worlds_readings(plan, cache):
    objs = [(o, 0) for o in plan.warmup_sequence()[:3]] + [(plan.teaching[0], 0), (plan.h2, 0)]
    objs += [(plan.P[0], replica_p(4, 1)), (plan.Q[5], replica_q(6))]
    for obj, replica in objs:
        want = read(plan.noise_key, obj.place, replica, obj.values, traits.OBSERVABLE)
        assert cache.visible(obj, replica) == tuple(want[t] for t in traits.OBSERVABLE)
        want = read(plan.noise_key, obj.place, replica, obj.values, traits.TASTE_INDICES)
        assert cache.taste(obj.place, replica, obj.values) == tuple(want[t] for t in traits.TASTE_INDICES)


def test_sweet_control_shares_h2s_noise_not_its_values(plan, cache):
    values = list(plan.h2.values)
    values[traits.SWEET] = 0.5
    a, b = cache.taste(plan.h2.place, 0, plan.h2.values), cache.taste(plan.h2.place, 0, values)
    assert a[1:] == b[1:]
    assert b[0] == clip01(0.5 + sensor_noise(plan.noise_key, plan.h2.place, 0, traits.SWEET))


# ---------------------------------------------------------------- one run's shape and energy

def test_every_non_tower_run_has_the_full_schedule(bot_records):
    for label, rec in bot_records.items():
        assert len(rec.decisions) == 210, label
        assert len(rec.probes) == 160 and len(rec.exposures) == 50, label
        assert sorted(rec.decisions) == list(range(1, 211))
        assert sorted(i["decision"] for i in rec.injections) == list(range(1, 211))      # one reset each
        assert len(rec.injections) == 210 and not rec.partial


def test_energy_is_reset_before_every_decision_and_costs_are_charged(plan, bot_records):
    reset = plan.reserve_milli + C.RESET_ABOVE_R_MILLI
    for label, rec in bot_records.items():
        mind = rec.decisions[1]["mind"]
        for n, d in rec.decisions.items():
            assert d["energy_set_milli"] == reset
            if rec.mind_class == "bot":
                assert d["look_milli"] == 0 and d["thinking_milli"] == 0
                assert d["energy_at_choice_milli"] == reset
            else:
                assert d["look_milli"] == C.LOOK_MILLI
                count = d["mind"]["thinking"]["count"]
                assert d["thinking_milli"] == protocol.thinking_cost_milli(count, C.CHECK_NANO) == count
                assert d["energy_at_choice_milli"] == reset - C.LOOK_MILLI - count
            if "outcome_milli" in d:
                assert d["energy_after_eat_milli"] == d["energy_at_choice_milli"] + d["outcome_milli"]
        assert mind["thinking"]["count"] == 0


def test_b1n_mind_counts_one_check_per_stored_item_and_trait(bot_records):
    rec = bot_records["B1n-mind(r=24)"]
    for n in range(1, 41):
        assert rec.decisions[n]["mind"]["thinking"]["count"] == (n - 1) * 18
    assert rec.decisions[42]["mind"]["thinking"]["count"] == 41 * 18      # a probe at S1


def test_forced_tastes_are_logged_as_designed_exposures(bot_records):
    rec = bot_records["G04"]
    for e in rec.exposures:
        d = rec.decisions[e["decision"]]
        assert d["ate"] and e["test"] == "KILL_TEST"
        if d["role"] == "main":
            assert d["forced"] and e["choice_window_outcome"] == "forced"
            assert d["action_provenance"] == "designed-exposure"
    skips = [d for d in rec.decisions.values() if d["role"] == "main" and d["mind"]["action"] == "skip"]
    assert skips, "G04 skips some forced tastes, and they are eaten anyway"


def test_check_copies_never_eat_or_write(bot_records):
    for rec in bot_records.values():
        for p in rec.probes:
            d = rec.decisions[p["decision"]]
            assert "outcome_milli" not in d and "write" not in d and "landing" not in d


def test_bots_find_h1_by_counting_their_own_eats(plan, bot_records):
    rec = bot_records["G05"]
    assert rec.decisions[41]["label"] == plan.teaching[0].label
    # before h1 is stored, G05's rule is undefined, so its would-be pick is "eat"
    assert rec.decisions[41]["mind"]["log"] == {"undefined": True}
    assert "undefined" not in rec.decisions[42]["mind"]["log"]


# ---------------------------------------------------------------- the stub, the H set and the hosts

def test_stub_runs_in_its_own_process_like_k_f(stub_record):
    rec = stub_record
    assert len(rec.decisions) == 210 and rec.mind_class == "tower"
    assert rec.h_sets["S1"] == [rec.h1_lid]
    for state in ("S2", "S4", "S6", "S8"):
        assert set(rec.h_sets["S1"]) <= set(rec.h_sets[state])
    assert rec.taste_noticed["candidate"] in rec.h_sets["S8"]


def test_both_hosts_give_identical_records(plan, cache, stub_record):
    a = run_one(plan, stub_spec(host="in-process"), cache)
    assert a.decisions == stub_record.decisions
    assert a.probes == stub_record.probes and a.lineage_log == stub_record.lineage_log
    assert a.taste_noticed == stub_record.taste_noticed


def test_hash_seed_changes_nothing(plan, cache, stub_record):
    b = run_one(plan, stub_spec(), cache, package_dir=STUB_DIR, hash_seed="12345")
    assert b.decisions == stub_record.decisions and b.probes == stub_record.probes


def test_a_taste_blind_stub_never_notices_and_a_taste_aware_one_does(cache, plan, stub_record):
    assert not scoring.measures(stub_record)["noticed"]
    aware = run_one(plan, stub_spec("taste-aware", host="in-process"), cache)
    m = scoring.measures(aware)
    assert m["noticed"] and m["clause1"]


def test_forgetting_reuses_slots_under_new_lineage_ids(plan, cache):
    rec = run_one(plan, stub_spec(host="in-process", max_slots=12), cache)
    forgets = [e for e in rec.lineage_log if e["type"] == "forget"]
    assert forgets
    lids = [e["lid"] for e in rec.lineage_log if e["type"] in ("new", "split") and e["line"] == "main"]
    assert len(lids) == len(set(lids))
    slots = [e["slot"] for e in rec.lineage_log if e["type"] in ("new", "split") and e["line"] == "main"]
    assert len(slots) > len(set(slots))


# ---------------------------------------------------------------- departures stop the run (KT-95)

@pytest.mark.parametrize("brk", ["eat-unknown", "cost", "extra-field", "fallback-cleared", "chooser", "nan"])
def test_a_departure_from_the_interface_stops_the_run(plan, cache, brk):
    spec = dataclasses.replace(agents.b1n_mind(24), label=f"liar-{brk}", entry="test_fixtures.liars:Liar",
                               params={"break": brk}, test_only=True)
    with pytest.raises(RunError):
        run_one(plan, spec, cache)


def test_the_mind_gets_a_fresh_read_only_packet(plan, cache):
    liars.SEEN.clear()
    spec = dataclasses.replace(agents.b1n_mind(24), label="grabber", entry="test_fixtures.liars:Grabber",
                               params={"break": None}, test_only=True)
    run_one(plan, spec, cache, checks=False, branches=False)
    assert len({id(v) for v in liars.SEEN}) == len(liars.SEEN) == 48
    for v in liars.SEEN:
        assert v.dtype == np.float64 and v.shape == (18,) and not v.flags.writeable


def test_partial_runs_stop_after_the_checks_asked_for(plan, cache):
    rec = run_one(plan, agents.b1n_bot_r(None), cache, checkpoints=(2, 4, 6, 8), branches=False)
    assert rec.partial and len(rec.probes) == 80
    assert {p["state"] for p in rec.probes} == {"S2", "S4", "S6", "S8"}
    m = scoring.measures(rec)
    full = scoring.measures(run_one(plan, agents.b1n_bot_r(None), cache))
    assert m["d_learn_beh"] == full["d_learn_beh"]


assert CHECKPOINTS == (1, 2, 4, 6, 8)


def test_the_stubs_noise_width_is_the_worlds():
    from test_fixtures import stub_inprocess
    from world.constants import NOISE_WIDTH
    assert stub_inprocess._entry.NOISE_WIDTH == NOISE_WIDTH


def test_the_per_run_file_holds_the_key_record_trace_exposures_and_injections(tmp_path, plan, stub_record):
    import json

    from harness import files
    path = files.write_run(stub_record, plan, tmp_path)
    data = json.loads(path.read_text())
    assert data["key_record"]["family"] == plan.family_number and data["key_record"]["run"] == plan.run_number
    assert len(data["verdict_trace"]) == 210 and len(data["injections"]) == 210
    assert len(data["designed_exposures"]) == 50
    assert path.read_text() == json.dumps(files.run_file(stub_record, plan), sort_keys=True,
                                          separators=(",", ":")) + "\n"
