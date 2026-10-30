"""MK10: the power check's mock mind (section 7, step 4; PLACEHOLDER-90, KT-15).

MK10 makes no decisions. For each run of a simulated set it draws the
per-run summary record that scoring.measures() would give a tower mind, with
the planned values of every GO quantity, and the frozen judge (harness/judge.py)
judges those records exactly as it will judge K-F's, with rule 6 off.

Planned values, per family (section 7):

- D_learn: the larger of 0.35 and the set's floor + 0.20. D at check 1: 0.
- CopyAccept 0.90; LookReject 0.70 in each half; FarMinusNeutral 0.25.
- D_strict on Q after SOUR 0.35, and a sour drop of 0.05.
- Settle rate 0.97. 70% of runs notice the taste; OS10 never does.
- Equal effects in every subgroup: nothing depends on core placement, and
  each run makes h1 a new candidate with probability 0.5, independently.

Spreads (spreads_from_tuning, from the tuning set's B1n-bot-r and B2e runs):

- Between families: D_learn, D at check 1, FarMinusNeutral, each LookReject
  half, D on Q after SOUR and the sour drop vary by the larger of B1n-bot-r's
  and B2e's between-family SDs (the sample SD of the 30 family means) and
  0.10. CopyAccept, the settle rate and the noticed share vary by 0.10.
- Between runs: D_learn, D at check 1, FarMinusNeutral, each LookReject half
  and D on Q vary by B1n-bot-r's within-family SD (pooled over the 30
  families). The sour drop doesn't vary. The settle rate is a binomial share
  of 210 decisions, CopyAccept of 10 copy checks, noticing a yes/no draw.

A share is drawn from a beta with the planned mean, its SD cut to
0.9 x sqrt(m(1 - m)) wherever a beta of mean m can't reach the stated SD, and
equal to m if m is exactly 0 or 1. A difference is drawn from a normal and
kept as drawn. Nothing is clipped.

Every draw for a family comes from its own stream, keyed by the frozen seed,
the simulated set and the family's place in it (KT-106). The draws are made
in a fixed order, and only D_learn's mean depends on the set (through its
floor), so the 60-family set keeps the 40-family set's first 40 families'
values, and D_learn moves only by the change in its planned mean.
"""

import hashlib
import hmac
import math
from fractions import Fraction

import numpy as np

# The planned values (section 7, step 4)
D_LEARN_MIN = 0.35
D_LEARN_ABOVE_FLOOR = 0.20
D_CHECK1 = 0.0
COPY_ACCEPT = 0.90
LOOK_REJECT = 0.70
FAR_MINUS_NEUTRAL = 0.25
Q_AFTER_SOUR = 0.35
SOUR_DROP = 0.05
SETTLE = 0.97
NOTICED = 0.70
NEW_CANDIDATE = 0.5
MIN_BETWEEN_SD = 0.10        # spreads between families are at least 0.10
SHARE_BETWEEN_SD = 0.10      # CopyAccept, settle rate and noticed share vary by 0.10
BETA_CUT = 0.9               # an unreachable beta SD is cut to 0.9 x sqrt(m(1 - m))
DECISIONS = 210              # a run's settle rate is a share of its 210 decisions
COPY_CHECKS = 10             # CopyAccept is a share of its 10 copy checks
# The seed, frozen in the analysis script (KT-106): the SHA-256 of this text.
SEED_TEXT = "FRANKIE kill test: MK10 power check seed, fixed 30 Oct 2026 before any result"
SEED = hashlib.sha256(SEED_TEXT.encode("ascii")).digest()

# The quantities that vary between families by the bots' spreads, and the bot measure each comes from
# (the D_beh version for D and for Q, section 7)
SPREAD_FROM = {
    "d_learn": "d_learn_beh",
    "d_check1": "d_beh_1",
    "fmn": "fmn_beh",
    "lr_h1": "lr_h1",
    "lr_far": "lr_far",
    "q_sour": "dq_sour_beh",
    "sour_drop": "sour_drop_beh",
}
VARY_BETWEEN_RUNS = ("d_learn", "d_check1", "fmn", "lr_h1", "lr_far", "q_sour")


def _family_values(runs: dict, field: str) -> list:
    by_family = {}
    for (f, r), m in runs.items():
        by_family.setdefault(f, []).append(float(m[field]))
    return [by_family[f] for f in sorted(by_family)]


def between_sd(runs: dict, field: str) -> float:
    """The sample SD (n - 1) of the family means (KT-106)."""
    means = [math.fsum(v) / len(v) for v in _family_values(runs, field)]
    mu = math.fsum(means) / len(means)
    return math.sqrt(math.fsum((x - mu) ** 2 for x in means) / (len(means) - 1))


def within_sd(runs: dict, field: str) -> float:
    """The pooled within-family SD: the root of the mean of each family's sample variance (KT-106)."""
    variances = []
    for v in _family_values(runs, field):
        mu = math.fsum(v) / len(v)
        variances.append(math.fsum((x - mu) ** 2 for x in v) / (len(v) - 1))
    return math.sqrt(math.fsum(variances) / len(variances))


def spreads_from_tuning(b1n_bot_r: dict, b2e: dict) -> dict:
    """The mock's spreads, from B1n-bot-r's and B2e's runs on the tuning set (section 7)."""
    between, within, source = {}, {}, {}
    for q, field in SPREAD_FROM.items():
        a, b = between_sd(b1n_bot_r, field), between_sd(b2e, field)
        between[q] = max(a, b, MIN_BETWEEN_SD)
        source[q] = {"measure": field, "B1n-bot-r": a, "B2e": b}
        if q in VARY_BETWEEN_RUNS:
            within[q] = within_sd(b1n_bot_r, field)
            source[q]["B1n-bot-r within"] = within[q]
    for q in ("copy_accept", "settle", "noticed"):
        between[q] = SHARE_BETWEEN_SD
    return {"between": between, "within": within, "source": source}


def _beta(gen, m, sd):
    """A beta draw with mean m and SD sd, cut where unreachable (section 7)."""
    if m <= 0.0 or m >= 1.0 or sd == 0.0:
        return m
    top = m * (1.0 - m)
    if sd * sd >= top:
        sd = BETA_CUT * math.sqrt(top)
    nu = top / (sd * sd) - 1.0
    return float(gen.beta(m * nu, (1.0 - m) * nu))


def _stream(simulated_set: int, place: int):
    msg = f"mk10/{simulated_set}/{place}".encode("ascii")
    key = int.from_bytes(hmac.new(SEED, msg, hashlib.sha256).digest()[:16], "little")
    return np.random.Generator(np.random.Philox(key=key))


def family_runs(simulated_set: int, place: int, family: int, floor: float, spreads: dict,
                runs: int = 10) -> tuple:
    """The mock K-F's and the mock OS10's run records for one family. Returns (kf, os10)."""
    gen = _stream(simulated_set, place)
    sb, sw = spreads["between"], spreads["within"]
    d_mean = max(D_LEARN_MIN, floor + D_LEARN_ABOVE_FLOOR)
    # family values, always in this order
    fam = {
        "d_learn": d_mean + sb["d_learn"] * float(gen.standard_normal()),
        "d_check1": D_CHECK1 + sb["d_check1"] * float(gen.standard_normal()),
        "fmn": FAR_MINUS_NEUTRAL + sb["fmn"] * float(gen.standard_normal()),
        "lr_h1": _beta(gen, LOOK_REJECT, sb["lr_h1"]),
        "lr_far": _beta(gen, LOOK_REJECT, sb["lr_far"]),
        "q_sour": Q_AFTER_SOUR + sb["q_sour"] * float(gen.standard_normal()),
        "sour_drop": SOUR_DROP + sb["sour_drop"] * float(gen.standard_normal()),
        "copy_accept": _beta(gen, COPY_ACCEPT, sb["copy_accept"]),
        "settle": _beta(gen, SETTLE, sb["settle"]),
        "noticed": _beta(gen, NOTICED, sb["noticed"]),
    }
    kf, os10 = {}, {}
    for r in range(1, runs + 1):
        rec = {
            "family": family, "run": r, "label": "MK10", "agent_type": "K-F", "mind_class": "tower",
            "d_learn_strict": fam["d_learn"] + sw["d_learn"] * float(gen.standard_normal()),
            "d_strict_1": fam["d_check1"] + sw["d_check1"] * float(gen.standard_normal()),
            "fmn_strict": fam["fmn"] + sw["fmn"] * float(gen.standard_normal()),
            "lr_h1": _beta(gen, fam["lr_h1"], sw["lr_h1"]),
            "lr_far": _beta(gen, fam["lr_far"], sw["lr_far"]),
            "dq_sour_strict": fam["q_sour"] + sw["q_sour"] * float(gen.standard_normal()),
            "sour_drop_strict": fam["sour_drop"],
            "settle_rate": _binomial_share(gen, DECISIONS, fam["settle"]),
            "copy_accept": _binomial_share(gen, COPY_CHECKS, fam["copy_accept"]),
            "noticed": bool(gen.random() < fam["noticed"]),
            "h1_new": bool(gen.random() < NEW_CANDIDATE),
        }
        kf[(family, r)] = rec
        os10[(family, r)] = {"family": family, "run": r, "label": "MK10-OS10", "noticed": False}
    return kf, os10


def _binomial_share(gen, n, p):
    return Fraction(int(gen.binomial(n, p)), n)
