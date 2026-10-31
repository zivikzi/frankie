"""Check order can't change any check's result (section 11, Week 2; section 5).

Every check copy is a fresh copy of its snapshot, and nothing a copy does
reaches the main line, a snapshot or another copy. So running the checks in
any order, interleaving P and Q, running Q's three states in any order, or
running no checks at all must leave every decision of the run exactly as it
was, number by number, in either host and under any hash seed.
"""

import random

import pytest

from harness import agents
from harness.readings_cache import ReadingCache
from harness.run import run_one
from test_fixtures.stub import STUB_DIR, stub_spec
from world import keys
from world.run_plan import generate_run

KEY = keys.tuning_set_key()


def _shuffled(seed):
    def order(jobs):
        jobs = list(jobs)
        random.Random(seed).shuffle(jobs)
        return jobs
    return order


def _q_first(jobs):
    return [j for j in jobs if j[0][0] == "Q"][::-1] + [j for j in jobs if j[0][0] == "P"]


def _by_state_backwards(jobs):
    return sorted(jobs, key=lambda j: (j[1], -j[0][1][1]), reverse=True)


ORDERS = {"reversed": lambda jobs: list(reversed(jobs)), "q-first": _q_first,
          "states-backwards": _by_state_backwards, "shuffle-1": _shuffled(1), "shuffle-2": _shuffled(2)}

MINDS = [
    pytest.param(stub_spec(host="in-process", restless=True), id="restless-stub"),
    pytest.param(stub_spec("taste-aware", host="in-process", max_slots=20), id="aware-stub-forgetting"),
    pytest.param(agents.b1n_mind(24), id="B1n-mind"),
    pytest.param(agents.plain_bot("G17"), id="G17"),
    pytest.param(agents.plain_bot("G07"), id="G07"),
    pytest.param(agents.b1n_bot_r(24), id="B1n-bot-r"),
]


@pytest.fixture(scope="module", params=[(1, 1), (17, 6)], ids=["family-1", "family-17"])
def plan_and_cache(request):
    f, r = request.param
    plan = generate_run("tuning", KEY, f, r)
    return plan, ReadingCache(plan.noise_key)


def _same(a, b):
    assert a.decisions == b.decisions
    assert a.probes == b.probes
    assert a.lineage_log == b.lineage_log and a.h_sets == b.h_sets
    assert a.taste_noticed == b.taste_noticed and a.exposures == b.exposures


@pytest.mark.parametrize("spec", MINDS)
def test_check_order_changes_nothing(plan_and_cache, spec):
    plan, cache = plan_and_cache
    base = run_one(plan, spec, cache)
    for name, order in ORDERS.items():
        _same(base, run_one(plan, spec, cache, order=order))


@pytest.mark.parametrize("spec", MINDS)
def test_running_no_checks_leaves_the_main_line_as_it_was(plan_and_cache, spec):
    plan, cache = plan_and_cache
    base = run_one(plan, spec, cache)
    bare = run_one(plan, spec, cache, checks=False)
    main = {n: d for n, d in base.decisions.items() if d["role"] in ("main", "h2")}
    assert bare.decisions == main
    assert bare.lineage_log == base.lineage_log and bare.taste_noticed == base.taste_noticed
    some = run_one(plan, spec, cache, checkpoints=(6,))
    assert {n: d for n, d in some.decisions.items()} == {n: d for n, d in base.decisions.items()
                                                         if n in some.decisions}


def test_check_order_and_hash_seed_change_nothing_in_the_minds_own_process(plan_and_cache):
    plan, cache = plan_and_cache
    spec = stub_spec(restless=True)
    base = run_one(plan, spec, cache, package_dir=STUB_DIR)
    _same(base, run_one(plan, spec, cache, package_dir=STUB_DIR, order=ORDERS["shuffle-1"], hash_seed="99"))
    _same(base, run_one(plan, stub_spec(host="in-process", restless=True), cache))
