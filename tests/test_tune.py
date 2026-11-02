"""The logged tuning search (kill-test/tune.py, TUNING_PLAN.md, KT-126 to KT-131), on made-up measurements.

The search's own logic is checked here without running any mind: the order
numbers and values are tried in, the keep rule and its ties, the stop rules,
reuse of a setting already measured, KT-47's rounding, and the log's replay.
"""

import json
import pathlib
import sys
from fractions import Fraction

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "kill-test"))
import tune  # noqa: E402

SPREADS = json.loads((ROOT / "kill-test" / "results" / "tuning-bench.json").read_text())["mk10_spreads"]["between"]


def fake_targets(misses, shortfall=0, d1=0):
    return {"rows": [], "misses": misses, "shortfall": Fraction(shortfall), "every_target": misses == 0,
            "d_check1": Fraction(d1)}


class Fake(tune.Search):
    """A search whose measurements come from score(setting) instead of runs."""

    def __init__(self, tmp_path, score):
        super().__init__(tune.Log(tmp_path / "log.jsonl"), 1, SPREADS, "test")
        self.score = score
        self.tried = []

    def floor(self, half):
        return {"floor": Fraction(1, 4)}, None, None

    def measure(self, trial, what, keep_runs=False):
        key = trial.key()
        if key in self.seen:
            self.log.add(dict(what, type="setting", trial=key, same_as=self.seen[key]["n"]))
            return self.seen[key]["tg"], None
        values = dict(trial.rate) if trial.mind == "TW7" else dict(trial.setting)
        self.tried.append(values)
        tg = self.score(values)
        e = self.log.add(dict(what, type="setting", trial=key, misses=tg["misses"]))
        self.seen[key] = dict(e, tg=tg)
        return tg, None


def test_the_grid_is_the_agreed_table():
    assert [r for r, _, _ in tune.KF_GRID] == [f"KT-{n}" for n in range(19, 27)]
    for _, name, values in tune.KF_GRID:
        assert tune.KF_START[name] in values and list(values) == sorted(values) and len(values) == 5
    assert tune.KF_START == {"leak": 0.1, "threshold": 2.5, "refractory_ms": 2, "inhibition": 0.3125,
                             "detector_width_nw": 4, "commit_margin": 2, "objection_threshold": 0.5,
                             "new_kind_threshold": 0.5}
    assert [(r, n) for r, n, _ in tune.TW7_GRID] == [("KT-28", "gain"), ("KT-29", "tau_ms")]
    assert tune.SEARCH == tuple(range(1, 31, 2)) and tune.KEPT_BACK == tuple(range(2, 31, 2))


def test_a_pass_tries_one_number_at_a_time_in_order_and_keeps_the_fewest_misses(tmp_path):
    def score(v):                         # leak 0.4 is best; nothing else matters; never every target
        return fake_targets(3 if v["leak"] == 0.4 else 5)
    s = Fake(tmp_path, score)
    values, passes, how = s.coordinate("K-F", tune.KF_GRID, tune.KF_START, range(1, 2))
    assert how == "passes" and passes == 1 and values["leak"] == 0.4
    assert values == dict(tune.KF_START, leak=0.4)
    assert len(s.tried) == 1 + 32                                    # the start, then 4 new values per number
    assert [t["leak"] for t in s.tried[1:5]] == [0.025, 0.05, 0.2, 0.4]
    assert s.tried[5] == dict(tune.KF_START, leak=0.4, threshold=0.625)    # the kept value carries on


def test_a_tie_keeps_the_current_value_and_fewer_misses_beat_a_smaller_shortfall(tmp_path):
    def score(v):
        if v["threshold"] == 5:
            return fake_targets(2, 9)     # fewer misses, bigger shortfall: wins
        if v["threshold"] == 10:
            return fake_targets(3, 0)
        return fake_targets(3, 1)         # every other value ties the start value
    s = Fake(tmp_path, score)
    values, _, _ = s.coordinate("K-F", tune.KF_GRID, tune.KF_START, range(1, 2))
    assert values["threshold"] == 5 and values["leak"] == tune.KF_START["leak"]


def test_a_smaller_shortfall_breaks_a_tie_in_misses():
    assert tune.better(fake_targets(2, 1), fake_targets(2, 2))
    assert not tune.better(fake_targets(2, 2), fake_targets(2, 2))
    assert tune.better(fake_targets(1, 50), fake_targets(2, 0))


def test_the_search_stops_at_the_first_setting_reaching_every_target(tmp_path):
    def score(v):
        return fake_targets(0 if v["refractory_ms"] == 1 else 2)
    s = Fake(tmp_path, score)
    values, passes, how = s.coordinate("K-F", tune.KF_GRID, tune.KF_START, range(1, 4))
    assert how == "pick" and passes == 1 and values == dict(tune.KF_START, refractory_ms=1)
    assert s.tried[-1] == values and len(s.tried) == 1 + 4 + 4 + 2   # stops mid-number, before refractory 4


def test_a_leak_stops_the_search(tmp_path):
    def score(v):
        return fake_targets(2, 0, Fraction(15, 100) if v["inhibition"] == 1.25 else 0)
    s = Fake(tmp_path, score)
    _, _, how = s.coordinate("K-F", tune.KF_GRID, tune.KF_START, range(1, 4))
    events = [json.loads(x) for x in (tmp_path / "log.jsonl").read_text().splitlines()]
    assert how == "leak" and events[-1]["type"] == "stop" and "D at check 1" in events[-1]["why"]


def test_a_setting_already_measured_is_not_measured_again(tmp_path):
    s = Fake(tmp_path, lambda v: fake_targets(4))                   # nothing ever improves
    s.coordinate("K-F", tune.KF_GRID, tune.KF_START, range(1, 4))
    assert len(s.tried) == 1 + 32                                   # passes 2 and 3 meet only known settings
    events = [json.loads(x) for x in (tmp_path / "log.jsonl").read_text().splitlines()]
    assert sum(1 for e in events if e["type"] == "setting" and "same_as" in e) == 64
    assert events[-1]["type"] == "no pick"


def test_tw7_searches_only_its_two_numbers_with_k_fs_values_fixed(tmp_path):
    s = Fake(tmp_path, lambda v: fake_targets(0 if v["tau_ms"] == 20 else 1))
    pick = dict(tune.KF_START, objection_threshold=1)
    values, passes, how = s.coordinate("TW7", tune.TW7_GRID, {"gain": 1, "tau_ms": 10}, range(1, 2),
                                       fixed=tuple(pick.items()), rate_mode=True)
    assert how == "pick" and values == {"gain": 1, "tau_ms": 20} and len(s.tried) == 1 + 4 + 3


def test_tw7_with_no_passes_is_measured_at_its_start_values_only(tmp_path):
    s = Fake(tmp_path, lambda v: fake_targets(1))
    values, passes, how = s.coordinate("TW7", tune.TW7_GRID, {"gain": 1, "tau_ms": 10}, range(1, 1),
                                       fixed=tuple(tune.KF_START.items()), rate_mode=True)
    assert (values, passes, how) == ({"gain": 1, "tau_ms": 10}, 0, "passes") and len(s.tried) == 1


def test_kt27_is_matched_by_medians_in_whole_nano_units(tmp_path):
    s = Fake(tmp_path, lambda v: fake_targets(0))
    t = tune.Trial("K-F", tuple(tune.KF_START.items()))
    s.seen[t.key()] = {"kt47": {"median_spikes": {"exact": "2000", "value": 2000.0},
                                "median_checks": {"exact": "1001/2", "value": 500.5}}}
    assert s.kt27(tune.KF_START) == 250_250                       # 1,000,000 x 500.5 / 2,000, exact
    s.seen[t.key()] = {"kt47": {"median_spikes": {"exact": "3", "value": 3.0},
                                "median_checks": {"exact": "1", "value": 1.0}}}
    assert s.kt27(tune.KF_START) == 333_333                       # 333,333.33... rounds down
    s.seen[t.key()]["kt47"]["median_spikes"] = {"exact": "8", "value": 8.0}
    s.seen[t.key()]["kt47"]["median_checks"] = {"exact": "3/1000000", "value": 3e-6}
    assert s.kt27(tune.KF_START) == 0                             # 0.375 rounds to 0


def test_the_median_of_an_even_number_is_the_mean_of_the_middle_two():
    assert tune.median([4, 1, 3, 2]) == Fraction(5, 2) and tune.median([5, 1, 3]) == 3


def test_targets_count_every_rule_and_subgroup_against_the_planned_values():
    runs = {}
    for f in range(1, 31, 2):
        for r in range(1, 11):
            runs[(f, r)] = {"settle_rate": Fraction(98, 100), "copy_accept": Fraction(1), "d_learn_strict":
                            Fraction(1, 2), "fmn_strict": Fraction(1, 4), "lr_h1": Fraction(3, 4), "lr_far":
                            Fraction(1, 2), "dq_sour_strict": Fraction(1, 2), "sour_drop_strict": Fraction(0),
                            "noticed": True, "d_strict_1": Fraction(1, 8), "h1_new": r <= 5}
    core_of = {f: "object" if f <= 19 else "none" for f in range(1, 31, 2)}
    tg = tune.targets(runs, core_of, Fraction(1, 4), SPREADS)
    missed = [(row["measure"], row["group"]) for row in tg["rows"] if not row["met"]]
    # D_learn's aim is the floor + 0.20 = 0.45 here; LookReject's far half misses everywhere it is judged
    groups = {row["group"] for row in tg["rows"]}
    assert groups == {"all runs", "core: object layer", "h1: new candidate"} or \
        groups == {"all runs", "core: object layer"}
    assert ("lr_far", "all runs") in missed and ("lr_far", "core: object layer") in missed
    assert all(m == "lr_far" for m, _ in missed)
    far = next(r for r in tg["rows"] if r["measure"] == "lr_far" and r["group"] == "all runs")
    assert far["shortfall"] == Fraction(1, 5) / Fraction(SPREADS["lr_far"])
    assert tg["d_check1"] == Fraction(1, 8) and not tg["every_target"]


def test_the_log_replays_and_refuses_a_different_history(tmp_path):
    path = tmp_path / "log.jsonl"
    log = tune.Log(path)
    log.add({"type": "begin", "x": Fraction(1, 3)})
    log.add({"type": "keep", "value": 2})
    again = tune.Log(path)
    again.add({"type": "begin", "x": Fraction(1, 3)})
    again.add({"type": "keep", "value": 2})
    again.add({"type": "done"})
    assert len(path.read_text().splitlines()) == 3
    third = tune.Log(path)
    with pytest.raises(SystemExit, match="not replaying"):
        third.add({"type": "begin", "x": Fraction(1, 2)})


class Rec:
    def __init__(self, logs):
        self.decisions = {k: {"mind": {"verdict": 0, "log": dict(last_step=len(lg), near_ties=0, holds_broken=[],
                                                                  unsettled_why=None, leaders=lg)}}
                          for k, lg in enumerate(logs)}


def test_a_tie_breaks_a_lead_so_leading_again_after_one_is_oscillating():
    rec = Rec([[None, 3, 3, None, 3], [None, 3, 3, 4, 4], [3, 4, 3], [None, None, "unknown", "unknown"]])
    assert tune.stability(rec)["oscillating"] == 2          # the first (lost to a tie) and the third


def test_the_costliest_decision_is_priced_at_the_settings_own_kt47_rate():
    t = tune.Trial("K-F", tuple(tune.KF_START.items()))
    c = tune.costliest(t, [10, 2000, 30], Fraction(1000), Fraction(500))
    assert c == {"most_in_one_decision": 2000, "unit_nano": 500_000, "milli": 1000}
    paid = tune.Trial("K-F", tuple(tune.KF_START.items()), spike_nano=7)
    assert tune.costliest(paid, [3], Fraction(1), Fraction(1))["unit_nano"] == 7
    tw7 = tune.Trial("TW7", tuple(tune.KF_START.items()), rate=(("gain", 1), ("tau_ms", 10)))
    assert tune.costliest(tw7, [600], Fraction(1), Fraction(1)) == {"most_in_one_decision": 600,
                                                                    "unit_nano": 1_000_000, "milli": 600}


def test_a_half_written_last_line_stops_the_resume_with_a_clear_message(tmp_path):
    path = tmp_path / "log.jsonl"
    path.write_text('{"type": "begin", "n": 0}\n{"type": "floo')
    with pytest.raises(SystemExit, match="not a whole event"):
        tune.Log(path)


def test_the_continuation_records_aitzazs_decision_word_for_word():
    import tune_continue
    d = tune_continue.DECISION
    assert d["by"] == "Aitzaz" and d["when"] == "2026-11-02 10:53 UTC" and d["choice"] == "Run the kill test"
    assert d["consequence"].startswith("I merge the search log and report into main, then freeze K-F at the setting")
    assert d["consequence"].endswith("Expected: NO-GO, a pre-registered answer.")


def test_the_continuation_needs_a_step_5_stop(tmp_path, monkeypatch):
    import tune_continue
    monkeypatch.setattr(tune, "commit_state", lambda: ("x", ""))
    monkeypatch.setattr(tune, "code_state", lambda: {"src": "a"})

    class Quiet:
        stdout = ""
    monkeypatch.setattr(tune.subprocess, "run", lambda *a, **k: Quiet())
    path = tmp_path / "log.jsonl"
    path.write_text(json.dumps({"type": "begin", "n": 0, "code": {"src": "a"}, "spreads": {}}) + "\n")
    assert tune_continue.proceed(path, 1) == 1
