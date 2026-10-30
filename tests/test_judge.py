"""The set-level judge (section 9), on hand-made measure records."""

import hashlib
from fractions import Fraction as F

import numpy as np
import pytest

from harness import judge


def runs(families, runs_per_family=10, **fields):
    """Measure records with the same values in every run; a field may be a function of (family, run)."""
    out = {}
    for f in families:
        for r in range(1, runs_per_family + 1):
            out[(f, r)] = {k: (v(f, r) if callable(v) else v) for k, v in fields.items()}
    return out


FAMS = list(range(1, 41))
CORE = {f: ("object" if f % 3 else "none") for f in FAMS}       # 27 object families, 13 none


def kf_records(**over):
    base = dict(settle_rate=F(97, 100), copy_accept=F(9, 10), d_learn_strict=F(1, 2), fmn_strict=F(1, 4),
                lr_h1=F(7, 10), lr_far=F(7, 10), sour_drop_strict=F(1, 20), dq_sour_strict=F(35, 100),
                noticed=lambda f, r: r <= 7, d_strict_1=F(0), h1_new=lambda f, r: r % 2 == 0)
    base.update(over)
    return runs(FAMS, **base)


def floor_runs(value=F(1, 4)):
    return runs(FAMS, d_learn_beh=value)


OS10 = runs(FAMS, noticed=False)


def go(**over):
    return judge.judge("test", kf_records(**over), floor_runs(), F(1, 4), OS10, CORE)


def test_the_seeds_are_the_sha256_of_their_texts():
    assert judge.BOOTSTRAP_SEED == hashlib.sha256(judge.BOOTSTRAP_SEED_TEXT.encode()).digest()


def test_every_mean_is_the_mean_of_family_means():
    r = {(1, 1): {"x": F(1)}, (2, 1): {"x": F(0)}, (2, 2): {"x": F(0)}, (2, 3): {"x": F(0)}}
    assert judge.set_mean(r, "x") == F(1, 2)
    assert judge.set_mean(r, "x", keep=lambda m: True) == F(1, 2)
    assert judge.set_mean(r, "x", families={2}) == 0


def test_a_subgroup_mean_is_over_families_with_runs_in_it():
    r = {(1, 1): {"x": F(1), "g": True}, (1, 2): {"x": F(0), "g": False},
         (2, 1): {"x": F(0), "g": False}, (3, 1): {"x": F(1, 2), "g": True}, (3, 2): {"x": F(0), "g": True}}
    assert judge.set_mean(r, "x", keep=lambda m: m["g"]) == (F(1) + F(1, 4)) / 2


def test_floats_count_exactly():
    assert judge.frac(0.1) == F(3602879701896397, 36028797018963968)
    assert judge.frac(True) == 1


def test_floor_takes_the_higher_mind_and_a_tie_goes_to_b1n_bot_r():
    minds = {"B1n-bot-r": floor_runs(F(1, 4)), "B1n-mind": floor_runs(F(1, 4))}
    assert judge.floor(minds) == ("B1n-bot-r", F(1, 4))
    minds["B1n-mind"] = floor_runs(F(26, 100))
    assert judge.floor(minds) == ("B1n-mind", F(26, 100))


def test_resample_indices_are_fixed_per_set_and_size():
    a = judge.resample_indices("A", 40)
    assert a.shape == (10_000, 40) and a.min() >= 0 and a.max() == 39
    assert np.array_equal(a, judge.resample_indices("A", 40))
    assert not np.array_equal(a, judge.resample_indices("B", 40))
    assert not np.array_equal(a[:, :40], judge.resample_indices("A", 60)[:, :40])


def test_the_bootstrap_counts_exactly():
    fams = [1, 2, 3, 4]
    idx = np.array([[0, 0, 0, 0], [0, 1, 2, 3], [1, 1, 1, 3], [3, 3, 3, 3]])
    diffs = {1: F(1, 3), 2: F(-1, 3), 3: F(0), 4: F(-1, 7)}
    # sums: 4/3 > 0; 1/3-1/3+0-1/7 < 0; -1-1/7 < 0; -4/7 < 0
    assert judge.bootstrap_at_or_below_zero(diffs, idx, fams) == 3
    diffs = {1: F(1), 2: F(-1), 3: F(0), 4: F(0)}
    assert judge.bootstrap_at_or_below_zero(diffs, np.array([[0, 1, 2, 3]]), fams) == 1    # exactly 0 counts


def test_runs_must_pair_by_run_key():
    with pytest.raises(ValueError):
        judge.paired_differences(runs([1], 10, x=F(1)), runs([1], 9, x=F(0)), "x", "x", [1])


def test_the_planned_mock_reaches_go():
    res = go()
    assert res["verdict"] == "GO" and res["causes"] == []
    assert res["3"]["bootstrap_at_or_below_0"] == 0


@pytest.mark.parametrize("over,verdict,cause", [
    (dict(settle_rate=F(94, 100)), "NO-GO", "decisions don't settle"),
    (dict(copy_accept=F(79, 100)), "NO-GO", "h1 wasn't learned"),
    (dict(d_learn_strict=F(1, 4)), "NO-GO", "not better than brute trial and error"),
    (dict(d_learn_strict=F(39, 100)), "INCONCLUSIVE", "rule 3 margin"),
    (dict(fmn_strict=F(14, 100)), "INCONCLUSIVE", "rule 4b"),
    (dict(lr_far=F(59, 100)), "INCONCLUSIVE", "rule 4c"),
    (dict(sour_drop_strict=F(16, 100)), "INCONCLUSIVE", "rule 5"),
    (dict(noticed=lambda f, r: r <= 4), "INCONCLUSIVE", "rule 5 uninformative"),
    (dict(d_strict_1=F(15, 100)), "INCONCLUSIVE", "rule 7 (possible essence leak: trace it with Aitzaz)"),
])
def test_the_verdict_order(over, verdict, cause):
    res = go(**over)
    assert res["verdict"] == verdict
    assert cause in (res["label"], *res["causes"])


def test_pass_marks_are_inclusive_and_rule_7_strict():
    assert go(settle_rate=F(95, 100), copy_accept=F(8, 10), d_learn_strict=F(40, 100), fmn_strict=F(15, 100),
              lr_h1=F(6, 10), lr_far=F(6, 10), sour_drop_strict=F(15, 100), dq_sour_strict=F(25, 100),
              d_strict_1=F(149, 1000))["verdict"] == "GO"


def test_rule_4_holds_in_every_subgroup_of_at_least_100_runs():
    # FarMinusNeutral fails only in families with no object-layer core trait (13 families, 130 runs)
    res = go(fmn_strict=lambda f, r: F(1, 10) if CORE[f] == "none" else F(1, 2))
    assert res["disc"]["4b"]["values"]["fmn_strict"] >= judge.FMN_MIN
    assert res["verdict"] == "INCONCLUSIVE" and "rule 4b" in res["causes"]
    # ...and fails only for runs where h1 stretched an old candidate
    res = go(lr_h1=lambda f, r: F(9, 10) if r % 2 == 0 else F(55, 100))
    assert res["verdict"] == "INCONCLUSIVE" and "rule 4c" in res["causes"]


def test_a_subgroup_under_100_runs_does_not_apply():
    core = {f: ("object" if f > 9 else "none") for f in FAMS}       # none: 9 families, 90 runs
    res = judge.judge("test", kf_records(fmn_strict=lambda f, r: F(0) if f <= 9 else F(1, 2)), floor_runs(),
                      F(1, 4), OS10, core)
    assert res["verdict"] == "GO"
    names = [row[0] for row in res["disc"]["4b"]["subgroups"]["fmn_strict"]]
    assert names == ["core: object layer", "h1: new candidate", "h1: old candidate"]


def test_os10_must_mostly_not_notice():
    os10 = runs(FAMS, noticed=lambda f, r: r == 1 and f <= 5)       # 5 of 400 notice
    assert judge.judge("test", kf_records(), floor_runs(), F(1, 4), os10, CORE)["verdict"] == "GO"
    os10 = runs(FAMS, noticed=lambda f, r: r <= 2)                   # 20% notice
    res = judge.judge("test", kf_records(), floor_runs(), F(1, 4), os10, CORE)
    assert res["verdict"] == "INCONCLUSIVE" and "rule 5 uninformative" in res["causes"]


def test_the_judge_accepts_differences_outside_minus_one_to_one():
    assert go(d_learn_strict=lambda f, r: 1.7 if r == 1 else 0.4)["verdict"] == "GO"


def test_rule_6_needs_every_must_fail_bot_to_fail_something():
    bench_minds = {"B1n-bot-r": floor_runs(F(1, 4)), "B1n-mind": floor_runs(F(1, 5))}
    good = dict(d_learn_beh=F(1, 2), fmn_beh=F(1, 2), lr_h1=F(1), lr_far=F(1), dq_sour_beh=F(1, 2))
    bench_minds["G01"] = runs(FAMS, **dict(good, dq_sour_beh=F(0)))
    res = judge.rule6("test", bench_minds, CORE, ["G01"])
    assert res["holds"] and res["bots"]["G01"]["passes"] == {"3": True, "4": True, "4b": True, "4c": True,
                                                            "Q": False}
    bench_minds["G01"] = runs(FAMS, **good)
    assert not judge.rule6("test", bench_minds, CORE, ["G01"])["holds"]


def test_a_bot_passes_rule_3_at_the_5th_percentile():
    bench_minds = {"B1n-bot-r": floor_runs(F(0)), "B1n-mind": floor_runs(F(0))}
    # family differences 0.4 except a few strongly negative families: the bot's mean clears the margin
    bad = {1, 2, 3, 4, 5, 6}
    bench_minds["G07"] = runs(FAMS, d_learn_beh=lambda f, r: F(-1) if f in bad else F(9, 10), fmn_beh=F(0),
                              lr_h1=F(0), lr_far=F(0), dq_sour_beh=F(0))
    row = judge.rule6("test", bench_minds, CORE, ["G07"])["bots"]["G07"]
    assert row["d_learn"] >= judge.MARGIN
    assert row["passes"]["3"] == (row["bootstrap_at_or_below_0"] < judge.LEVEL_BOT)


def test_positive_control():
    b2e = runs(FAMS, d_learn_beh=F(99, 100), fmn_beh=F(99, 100), lr_h1=F(1), lr_far=F(1), dq_sour_beh=F(9, 10))
    assert judge.positive_control(b2e, CORE)["pass"]
    b2e = runs(FAMS, d_learn_beh=F(99, 100), fmn_beh=F(99, 100), lr_h1=F(1), lr_far=F(1), dq_sour_beh=F(1, 5))
    assert not judge.positive_control(b2e, CORE)["pass"]


def test_the_second_evaluation_is_final():
    assert judge.programme_outcome("INCONCLUSIVE", 1) == "INCONCLUSIVE"
    assert judge.programme_outcome("INCONCLUSIVE", 2) == "NO-GO"
    assert judge.programme_outcome("GO", 2) == "GO"
    with pytest.raises(ValueError):
        judge.programme_outcome("GO", 3)
