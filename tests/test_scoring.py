"""From a run's record to its measures (section 8), on hand-made records."""

from fractions import Fraction

import pytest

from harness import scoring
from harness.run import SOUR, SWEET, RunRecord
from world.run_plan import CHECKPOINTS

P_ORDER = ["far"] * 8 + ["look-h1"] * 4 + ["look-far"] * 4 + ["neutral"] * 2 + ["copy"] * 2
Q_ORDER = ["apple"] * 8 + ["look-h1"] * 4 + ["look-h2"] * 4 + ["neutral"] * 2 + ["copy"] * 2


def probes(state, order, eat_roles, h_roles=None, counts=None):
    """20 probes; counts[role] says how many of that role eat (default: all in eat_roles)."""
    out, seen = [], {}
    for i, role in enumerate(order, 1):
        k = seen.get(role, 0)
        seen[role] = k + 1
        n = (counts or {}).get(role, 99 if role in eat_roles else 0)
        ate = k < n
        names_h = ate and (h_roles is None or role in h_roles)
        out.append({"decision": 0, "state": state, "probe": i, "label": "", "role": role, "ate": ate,
                    "verdict": "c1" if names_h else "c9", "names_h": names_h, "settled": True})
    return out


def record(mind_class="tower", p=None, q=None, decisions=None, noticed=None, info=None):
    rec = RunRecord("tuning", 1, 1, "x", "x", mind_class)
    rec.info = info or {"constants": {}}
    rec.probes = []
    for c in CHECKPOINTS:
        rec.probes += (p or {}).get(c, probes(f"S{c}", P_ORDER, ()))
    for s in ("S8", SOUR, SWEET):
        rec.probes += (q or {}).get(s, probes(f"Q-{s}", Q_ORDER, ()))
    rec.decisions = decisions or {n: {"role": "main", "mind": {"verdict": 0, "action": "eat", "settle_step": 3},
                                      "outcome_milli": 15000} for n in range(1, 211)}
    if mind_class == "tower":
        rec.decisions[149] = {"role": "h2", "mind": {"verdict": 0, "action": "eat", "settle_step": 3},
                              "verdict_lid": "c1", "forced": False, "outcome_milli": 15000}
        rec.h_sets = {"S8": ["c1"]}
    rec.lineage_log = []
    rec.taste_noticed = noticed or {SOUR: {"candidate_record": None, "taste": [0.5] * 4, "write_types": ["stretch"]},
                                    SWEET: {"candidate_record": None, "taste": [0.5] * 4,
                                            "write_types": ["stretch"]}}
    rec.h1_new = True
    return rec


def test_d_strict_and_d_beh_at_each_check():
    # at every check: 6 far apples eaten, 4 naming H; 2 h1-half and 1 far-half look-alikes eaten
    p = {c: probes(f"S{c}", P_ORDER, (), h_roles={"far"},
                   counts={"far": 6, "look-h1": 2, "look-far": 1}) for c in CHECKPOINTS}
    for c in CHECKPOINTS:
        for x in p[c][4:6]:
            x["names_h"] = False          # far apples 5 and 6 are eaten under another verdict
    m = scoring.measures(record(p=p))
    assert m["d_beh_2"] == Fraction(6, 8) - Fraction(3, 8)
    assert m["d_strict_2"] == Fraction(4, 8) - Fraction(3, 8)
    assert m["d_learn_strict"] == Fraction(1, 8) and m["d_learn_beh"] == Fraction(3, 8)
    assert m["lr_h1"] == Fraction(1, 2) and m["lr_far"] == Fraction(3, 4)


def test_d_learn_averages_checks_2_4_6_and_8_only():
    p = {c: probes(f"S{c}", P_ORDER, ("far",)) for c in CHECKPOINTS}
    p[1] = probes("S1", P_ORDER, ("look-h1", "look-far"))
    p[4] = probes("S4", P_ORDER, ())
    m = scoring.measures(record("bot", p=p))
    assert m["d_beh_1"] == -1 and m["d_beh_4"] == 0
    assert m["d_learn_beh"] == Fraction(3, 4)


def test_far_minus_neutral_copy_accept_and_look_reject():
    p = {c: probes(f"S{c}", P_ORDER, ("far", "neutral", "copy"), counts={"neutral": 1, "copy": 1})
         for c in CHECKPOINTS}
    m = scoring.measures(record("bot", p=p))
    assert m["fmn_beh"] == 1 - Fraction(1, 2)
    assert m["copy_accept"] == Fraction(5, 10)
    assert m["lr_h1"] == m["lr_far"] == 1


def test_q_uses_all_8_apples_and_the_sour_drop_is_paired():
    q = {"S8": probes("Q-S8", Q_ORDER, ("apple",)),
         SOUR: probes(f"Q-{SOUR}", Q_ORDER, ("apple", "look-h2"), counts={"apple": 2}),
         SWEET: probes(f"Q-{SWEET}", Q_ORDER, ("apple",), counts={"apple": 7})}
    m = scoring.measures(record(q=q))
    assert m["dq_s8_strict"] == 1
    assert m["dq_sour_strict"] == Fraction(2, 8) - Fraction(4, 8)
    assert m["dq_sweet_strict"] == Fraction(7, 8)
    assert m["sour_drop_strict"] == Fraction(7, 8) - Fraction(-2, 8)


def test_settle_rate_counts_every_decision():
    rec = record()
    for n in range(1, 22):
        rec.decisions[n]["mind"]["verdict"] = "unsettled"
    assert scoring.measures(rec)["settle_rate"] == Fraction(189, 210)


def test_a_check_set_of_the_wrong_shape_is_an_error():
    p = {1: probes("S1", P_ORDER[:-1] + ["far"], ())}
    with pytest.raises(scoring.ScoringError):
        scoring.measures(record("bot", p=p))


def _noticed(sour_taste, sweet_taste, ranges, weights, sour_writes=("stretch",), sweet_writes=("stretch",)):
    cand = {"slot": 3, "ranges": ranges, "weights_tenths": weights}
    return {SOUR: {"candidate_record": cand, "taste": sour_taste, "write_types": list(sour_writes)},
            SWEET: {"candidate_record": cand, "taste": sweet_taste, "write_types": list(sweet_writes)}}


INFO = {"constants": {"detector_width_nw": [2, "KT-20"]}}


def test_taste_evidence_widens_ranges_by_the_detector_width():
    cand = {"ranges": [[0.4, 0.6]] * 4, "weights_tenths": [5, 5, 3, 0]}
    assert scoring.taste_evidence(cand, [0.5, 0.615, 0.625, 0.5], 2) == 5 + 5 + 0 + 0
    assert scoring.taste_evidence(cand, [0.5, 0.5, 0.5, 0.5], 2) == 13


def test_taste_noticed_by_evidence():
    n = _noticed([0.5, 0.9, 0.5, 0.5], [0.5] * 4, [[0.4, 0.6]] * 4, [5] * 4)
    m = scoring.measures(record(noticed=n, info=INFO))
    assert m["noticed"] and m["clause1"] and not m["clause2"]


def test_a_zero_weight_taste_trait_is_not_noticed_by_evidence():
    n = _noticed([0.5, 0.9, 0.5, 0.5], [0.5] * 4, [[0.4, 0.6]] * 4, [5, 0, 5, 5])
    assert not scoring.measures(record(noticed=n, info=INFO))["noticed"]


def test_taste_noticed_by_writes():
    n = _noticed([0.5] * 4, [0.5] * 4, [None] * 4, [None] * 4, sour_writes=("split",))
    m = scoring.measures(record(noticed=n))
    assert m["noticed"] and m["clause2"] and not m["clause1"]
    n = _noticed([0.5] * 4, [0.5] * 4, [None] * 4, [None] * 4, sour_writes=("new",), sweet_writes=("new",))
    assert not scoring.measures(record(noticed=n))["noticed"]
    n = _noticed([0.5] * 4, [0.5] * 4, [None] * 4, [None] * 4, sour_writes=("forget", "stretch"))
    assert not scoring.measures(record(noticed=n))["noticed"]


def test_a_mind_with_taste_ranges_must_declare_its_detector_width():
    n = _noticed([0.5] * 4, [0.5] * 4, [[0.4, 0.6]] * 4, [5] * 4)
    with pytest.raises(scoring.ScoringError):
        scoring.measures(record(noticed=n))


def test_bots_are_never_noticed_and_have_no_strict_measures():
    m = scoring.measures(record("bot"))
    assert not m["noticed"] and "d_learn_strict" not in m and "settle_rate" not in m
