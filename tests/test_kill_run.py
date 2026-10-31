"""The kill-run order on a made-up set (sections 3 and 9).

Tests never make or preview a real kill-run set: they use a made-up block
hash, which no Bitcoin block has, and the stub in K-F's and OS10's places.
"""

import dataclasses
from fractions import Fraction

import pytest

from harness import agents, judge, kill_run
from test_fixtures.stub import STUB_DIR, stub_spec

FAKE_HASH = "5e" * 32


def test_the_median_thinking_spend():
    class R:
        decisions = {i: {"mind": {"thinking": {"count": c}}} for i, c in enumerate([5, 1, 3, 2])}
    assert kill_run.median_thinking_nano(R, 10) == Fraction(25)
    R.decisions[9] = {"mind": {"thinking": {"count": 9}}}
    assert kill_run.median_thinking_nano(R, 10) == Fraction(30)


def test_only_sets_a_b_and_c_are_kill_run_sets():
    with pytest.raises(ValueError):
        kill_run.run_kill_set("tuning", FAKE_HASH, 2, [], {})


def test_a_made_up_set_runs_in_the_frozen_order(monkeypatch):
    seen = []
    real_rule6 = judge.rule6

    def rule6(*a, **k):
        seen.append("rule 6")
        return real_rule6(*a, **k)
    real_tower = kill_run._tower_run

    def tower(job):
        seen.append("tower")
        return real_tower(job)
    monkeypatch.setattr(judge, "rule6", rule6)
    monkeypatch.setattr(kill_run, "_tower_run", tower)
    kf = dataclasses.replace(stub_spec(), label="K-F")
    os10 = dataclasses.replace(stub_spec(), label="OS10")
    res = kill_run.run_kill_set("A", FAKE_HASH, 2, [kf, os10], {"mind": STUB_DIR}, runs=2)
    assert seen[0] == "rule 6"
    if res["retired"]:
        assert "tower" not in seen and res["verdict"] is None
    else:
        assert seen[1:] == ["tower"] * 4
        assert res["verdict"] in ("GO", "NO-GO", "INCONCLUSIVE")
    assert kill_run.verdict_table(res).startswith("Set A:")


def test_k_f_must_run_first(monkeypatch):
    monkeypatch.setattr(judge, "rule6", lambda *a, **k: {"holds": True, "floor_mind": "B1n-bot-r",
                                                         "floor": Fraction(0), "bots": {}})
    os10 = dataclasses.replace(stub_spec(), label="OS10")
    with pytest.raises(ValueError):
        kill_run.run_kill_set("A", FAKE_HASH, 1, [os10], {"mind": STUB_DIR}, runs=1)


def test_the_registered_radii():
    labels = [s.label for s in agents.bench_minds()]
    assert labels[:2] == ["B1n-bot-r(r=unlimited)", "B1n-mind(r=24)"]
    assert labels[-2:] == ["G16(r=24)", "G18(r=24)"]
