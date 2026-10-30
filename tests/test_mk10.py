"""MK10, the power check's mock mind (section 7, step 4; KT-106)."""

import math
import numpy as np
import pytest

from test_fixtures import mk10

SPREADS = {"between": {"d_learn": 0.1, "d_check1": 0.1, "fmn": 0.14, "lr_h1": 0.12, "lr_far": 0.12, "q_sour": 0.1,
                       "sour_drop": 0.1, "copy_accept": 0.1, "settle": 0.1, "noticed": 0.1},
           "within": {"d_learn": 0.13, "d_check1": 0.19, "fmn": 0.29, "lr_h1": 0.15, "lr_far": 0.25, "q_sour": 0.07}}


def test_the_seed_is_the_sha256_of_its_text():
    import hashlib
    assert mk10.SEED == hashlib.sha256(mk10.SEED_TEXT.encode()).digest()


def test_draws_are_fixed_by_set_and_place():
    a, _ = mk10.family_runs(3, 7, 1367, 0.24, SPREADS)
    b, _ = mk10.family_runs(3, 7, 1367, 0.24, SPREADS)
    c, _ = mk10.family_runs(3, 8, 1368, 0.24, SPREADS)
    assert a == b
    assert [m["fmn_strict"] for m in a.values()] != [m["fmn_strict"] for m in c.values()]


def test_only_d_learn_moves_with_the_floor():
    low, _ = mk10.family_runs(2, 5, 1125, 0.10, SPREADS)       # planned D_learn 0.35
    high, _ = mk10.family_runs(2, 5, 1125, 0.30, SPREADS)      # planned D_learn 0.50
    for key in low:
        for field, v in low[key].items():
            if field == "d_learn_strict":
                assert high[key][field] - v == pytest.approx(0.15, abs=1e-12)
            else:
                assert high[key][field] == v


def test_os10_never_notices_and_every_run_has_a_record():
    kf, os10 = mk10.family_runs(1, 1, 1001, 0.24, SPREADS)
    assert sorted(kf) == sorted(os10) == [(1001, r) for r in range(1, 11)]
    assert not any(m["noticed"] for m in os10.values())
    for m in kf.values():
        assert m["sour_drop_strict"] == kf[(1001, 1)]["sour_drop_strict"]     # no spread between runs
        assert (m["settle_rate"] * 210).denominator == 1 and (m["copy_accept"] * 10).denominator == 1


def test_the_mock_draws_around_its_planned_values():
    fams = [mk10.family_runs(s, 1, 1000 + 120 * (s - 1) + 1, 0.24, SPREADS)[0] for s in range(1, 401)]
    allruns = [m for f in fams for m in f.values()]

    def mean(field):
        return math.fsum(float(m[field]) for m in allruns) / len(allruns)
    assert mean("d_learn_strict") == pytest.approx(0.44, abs=0.02)
    assert mean("d_strict_1") == pytest.approx(0.0, abs=0.02)
    assert mean("fmn_strict") == pytest.approx(0.25, abs=0.02)
    assert mean("lr_h1") == pytest.approx(0.70, abs=0.02) and mean("lr_far") == pytest.approx(0.70, abs=0.02)
    assert mean("dq_sour_strict") == pytest.approx(0.35, abs=0.02)
    assert mean("sour_drop_strict") == pytest.approx(0.05, abs=0.02)
    assert mean("settle_rate") == pytest.approx(0.97, abs=0.02)
    assert mean("copy_accept") == pytest.approx(0.90, abs=0.02)
    assert mean("noticed") == pytest.approx(0.70, abs=0.03)
    assert mean("h1_new") == pytest.approx(0.5, abs=0.03)
    fam_d = [math.fsum(m["d_learn_strict"] for m in f.values()) / 10 for f in fams]
    sd = float(np.std(fam_d, ddof=1))
    assert sd == pytest.approx(math.sqrt(0.1 ** 2 + 0.13 ** 2 / 10), rel=0.15)
    assert min(m["fmn_strict"] for m in allruns) < -0.5      # differences are kept as drawn, never clipped


def test_a_beta_too_wide_for_its_mean_is_cut():
    gen = np.random.Generator(np.random.Philox(key=1))
    xs = [mk10._beta(gen, 0.9, 0.5) for _ in range(20000)]
    assert np.mean(xs) == pytest.approx(0.9, abs=0.01)
    assert np.std(xs) == pytest.approx(0.9 * math.sqrt(0.09), abs=0.01)
    assert mk10._beta(gen, 1.0, 0.2) == 1.0 and mk10._beta(gen, 0.0, 0.2) == 0.0
    assert mk10._beta(gen, 0.7, 0.0) == 0.7


def test_spreads_from_tuning():
    # 3 families of 2 runs: family means 0, 1 and 2 (sample SD 1); each family's run variance is 2
    def runs(vals):
        return {(f, r): {q: v for q in mk10.SPREAD_FROM.values()} for (f, r), v in vals.items()}
    bot = runs({(1, 1): -1.0, (1, 2): 1.0, (2, 1): 0.0, (2, 2): 2.0, (3, 1): 1.0, (3, 2): 3.0})
    flat = runs({(f, r): 0.5 for f in (1, 2, 3) for r in (1, 2)})
    s = mk10.spreads_from_tuning(bot, flat)
    assert s["between"]["d_learn"] == pytest.approx(1.0)
    assert s["within"]["d_learn"] == pytest.approx(math.sqrt(2))
    assert "sour_drop" not in s["within"]
    s = mk10.spreads_from_tuning(flat, flat)
    assert s["between"]["fmn"] == mk10.MIN_BETWEEN_SD and s["within"]["fmn"] == 0.0
    assert s["between"]["copy_accept"] == s["between"]["settle"] == s["between"]["noticed"] == 0.10
