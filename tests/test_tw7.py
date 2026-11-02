"""TW7 (K-F's tower, memory and drive on rate units) through the frozen harness, and the mind checks that can run now.

These tests host TW7 in this process, which is quicker: every answer still
passes every check in harness/protocol.py, and the run is the frozen run
order of section 5. Since bench v1.1, TW7 also runs in its own process
beside a copy of K-F's code, and gives the same record there
(tests/test_bench_v1_1.py).
"""

import pathlib
import sys

import pytest

from harness import child, protocol, scoring
from harness import constants as C
from harness.agents import OS07, AgentSpec, tower_minds
from harness.host import InProcessHost
from harness.readings_cache import ReadingCache
from harness.run import _Run, birth_config, run_one
from world import keys
from world.run_plan import generate_run

import twins.entry as tw

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import mind_checks  # noqa: E402

SPEC = AgentSpec(agent_type="TW7", label="TW7", mind_class="tower", entry="twins.entry:make", host="in-process",
                 pays_look=True, thinking_unit="check", unit_nano=C.CHECK_NANO, unit_row="B14, KT-45, KT-46",
                 version=(OS07,), params={"twin": "TW7"})


@pytest.fixture(scope="module")
def plan():
    return generate_run("tuning", keys.tuning_set_key(), 3, 2)


@pytest.fixture(scope="module")
def record(plan):
    return run_one(plan, SPEC, ReadingCache(plan.noise_key), host=InProcessHost(tw.make))


def test_the_registry_entry_and_this_one_agree():
    reg = tower_minds(None)[-1]
    assert (reg.agent_type, reg.thinking_unit, reg.unit_nano, reg.version, reg.params) == \
           (SPEC.agent_type, SPEC.thinking_unit, SPEC.unit_nano, SPEC.version, SPEC.params)


def test_a_whole_run_passes_every_interface_check(record):
    assert len(record.decisions) == C.DECISIONS_PER_RUN and not record.partial
    protocol.check_info(record.info, tower_minds(None)[-1])
    assert record.info["neuron"] == "rate" and record.info["chooser"] == "satisficing"
    assert record.info["constants"]["detector_width_nw"] == [4, "KT-23"]
    assert record.birth_dump == {"candidates": []}                       # empty at birth (M09, FORBIDDEN 20)


def test_the_harness_charges_what_the_mind_counted(record):
    for d in record.decisions.values():
        th = d["mind"]["thinking"]
        assert th["unit"] == "check" and th["cost_milli"] == th["count"] == d["mind"]["log"]["checks"]
        assert d["thinking_milli"] == th["cost_milli"]


def test_every_eat_is_filed_once_and_new_kinds_start_at_half_weight(record):
    for d in record.decisions.values():
        if "write" in d:
            filings = [e for e in d["write"]["events"] if e["type"] != "forget"]
            assert len(filings) == 1
            if filings[0]["type"] == "new":
                assert filings[0]["placeholder_93"] and filings[0]["trigger"] == "designed-exposure"


def test_the_run_scores(record):
    m = scoring.measures(record)
    assert 0 <= m["settle_rate"] <= 1 and "noticed" in m


def test_the_same_run_twice_gives_the_same_record(plan, record):
    again = run_one(plan, SPEC, ReadingCache(plan.noise_key), host=InProcessHost(tw.make))
    assert again.decisions == record.decisions and again.lineage_log == record.lineage_log


def test_looks_with_no_outcome_change_nothing(plan):
    """The counter check (FORBIDDEN 9, X43(e)), run in this process."""
    cache = ReadingCache(plan.noise_key)
    host = InProcessHost(tw.make)
    run = _Run(plan, SPEC, host, cache, birth_config(plan, SPEC))
    host.new("main", run.birth)
    for i, obj in enumerate(plan.warmup_sequence()[:20], 1):
        run._main_taste(i, f"warmup-{i}", obj)
    e = run.reset_to
    host.copy("main", "a")
    host.copy("main", "b")
    for k, obj in enumerate(plan.P[:7]):
        host.decide("b", cache.visible(obj, 1000 + k), e)
    last = cache.visible(plan.P[-1], 1)
    assert host.decide("a", last, e) == host.decide("b", last, e)
    assert child.state_fingerprint(host._minds["a"]) == child.state_fingerprint(host._minds["b"])


def test_k_f_refuses_to_run_until_it_has_a_per_spike_cost():
    """K-F's spiking units exist since Week 4; KT-27 is set after the search, so until then it must be handed one."""
    from mind import entry
    with pytest.raises(ValueError, match="KT-27"):
        entry.make({"reserve_milli": 40000, "boldness": 0.3, "params": {}, "trait_order": list(range(22))})


def test_only_tw7_is_built_among_the_twins():
    with pytest.raises(ValueError, match="Week 5"):
        tw.make({"reserve_milli": 40000, "boldness": 0.3, "params": {"twin": "TW2"}, "trait_order": list(range(22))})


@pytest.mark.parametrize("package", ["src/mind", "src/twins"])
def test_the_static_mind_checks_find_nothing(package):
    """The import guard, the file and word scans and the no-unlisted-constants test (section 7, step 5)."""
    assert [str(f) for f in mind_checks.static_checks(ROOT / package)] == []
