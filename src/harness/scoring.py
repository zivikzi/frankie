"""From one run's record to its measures (section 8), in exact fractions.

Everything is measured on check copies, except the settle rate (every
decision) and the reported counts. Each count is a whole number out of a fixed
total, so every measure is an exact fraction: D at a check is a multiple of
1/8, D_learn and FarMinusNeutral of 1/32, a LookReject half of 1/4, CopyAccept
of 1/10 and the settle rate of 1/210. Pass marks are compared exactly (KT-103).

- D_strict (tower minds): far apples eaten while naming H, over 8, minus
  look-alikes eaten with any verdict, over 8. D_beh: the same from eating alone.
- D_learn: the mean of D at checks 2, 4, 6 and 8.
- FarMinusNeutral: the far-apple (strict, for tower minds) eat rate minus the
  neutrals' eat rate, averaged over checks 2, 4, 6 and 8.
- LookReject: at check 8, 1 minus the look-alike eat rate, per half.
- CopyAccept: the eat rate of the 10 copies of h1, checks 1 to 8.
- On Q, all 8 of Q's apples take the far apples' place.
- Sour drop: D_strict on Q after SWEET-CONTROL minus after SOUR.
- TASTE-NOTICED: section 8's two parts, from the record the harness kept.
"""

from fractions import Fraction

from world import traits
from world.constants import NOISE_WIDTH
from world.run_plan import CHECKPOINTS

from .run import SOUR, SWEET

LEARN_CHECKS = (2, 4, 6, 8)      # D_learn and FarMinusNeutral average checks 2, 4, 6 and 8 (section 8)
P_ROLES = {"far": 8, "look-h1": 4, "look-far": 4, "neutral": 2, "copy": 2}       # (section 5, KT-87)
Q_ROLES = {"apple": 8, "look-h1": 4, "look-h2": 4, "neutral": 2, "copy": 2}      # (section 5, KT-87)
NON_STRETCH = ("new", "split", "mark-unreliable")     # a memory write other than a stretch (section 8)


class ScoringError(RuntimeError):
    pass


def _tally(probes, roles, tower):
    seen = {r: 0 for r in roles}
    ate = {r: 0 for r in roles}
    strict = {r: 0 for r in roles}
    for p in probes:
        seen[p["role"]] += 1
        if p["ate"]:
            ate[p["role"]] += 1
            if tower and p["names_h"]:
                strict[p["role"]] += 1
    if seen != roles:
        raise ScoringError(f"a check set holds {seen}, not {roles}")
    return ate, strict


def _mean(xs):
    xs = list(xs)
    return sum(xs, Fraction(0)) / len(xs)


def taste_evidence(record, taste, detector_width_nw) -> int:
    """PLACEHOLDER-01's count over the 4 taste traits, in tenths of weight (section 8, KT-94)."""
    w = detector_width_nw * NOISE_WIDTH
    total = 0
    for (lo, hi), weight, x in zip(record["ranges"], record["weights_tenths"], taste):
        if lo - w <= x <= hi + w:
            total += weight
    return total


def taste_noticed(rec) -> dict:
    """TASTE-NOTICED (section 8). 'Stores no taste ranges' is read from the memory dump."""
    tn = rec.taste_noticed
    cand = tn[SOUR]["candidate_record"]
    clause1 = False
    if cand is not None and cand["ranges"] is not None and cand["ranges"][0] is not None:
        constants = rec.info["constants"]
        if "detector_width_nw" not in constants:
            raise ScoringError("a mind that stores taste ranges must declare its detector width (KT-23)")
        dw = constants["detector_width_nw"][0]
        e_sour = taste_evidence(cand, tn[SOUR]["taste"], dw)
        e_sweet = taste_evidence(cand, tn[SWEET]["taste"], dw)
        clause1 = e_sour < e_sweet
    sour = any(t in NON_STRETCH for t in tn[SOUR]["write_types"])
    sweet = any(t in NON_STRETCH for t in tn[SWEET]["write_types"])
    clause2 = sour and not sweet
    return {"noticed": clause1 or clause2, "clause1": clause1, "clause2": clause2}


def measures(rec) -> dict:
    """One run's measures, as exact fractions (and booleans)."""
    if rec.partial:
        return partial_measures(rec)
    tower = rec.mind_class == "tower"
    by_state = {}
    for p in rec.probes:
        by_state.setdefault(p["state"], []).append(p)
    m = {"family": rec.family_number, "run": rec.run_number, "label": rec.label,
         "agent_type": rec.agent_type, "mind_class": rec.mind_class}
    d_beh, d_strict, fmn_beh, fmn_strict, copies = {}, {}, {}, {}, 0
    for c in CHECKPOINTS:
        ate, strict = _tally(by_state[f"S{c}"], P_ROLES, tower)
        look = ate["look-h1"] + ate["look-far"]
        d_beh[c] = Fraction(ate["far"], 8) - Fraction(look, 8)
        d_strict[c] = Fraction(strict["far"], 8) - Fraction(look, 8)
        fmn_beh[c] = Fraction(ate["far"], 8) - Fraction(ate["neutral"], 2)
        fmn_strict[c] = Fraction(strict["far"], 8) - Fraction(ate["neutral"], 2)
        copies += ate["copy"]
        if c == 8:
            m["lr_h1"] = 1 - Fraction(ate["look-h1"], 4)
            m["lr_far"] = 1 - Fraction(ate["look-far"], 4)
    for c in CHECKPOINTS:
        m[f"d_beh_{c}"] = d_beh[c]
        if tower:
            m[f"d_strict_{c}"] = d_strict[c]
    m["d_learn_beh"] = _mean(d_beh[c] for c in LEARN_CHECKS)
    m["fmn_beh"] = _mean(fmn_beh[c] for c in LEARN_CHECKS)
    m["copy_accept"] = Fraction(copies, 10)
    q_beh, q_strict = {}, {}
    for state in ("S8", SOUR, SWEET):
        ate, strict = _tally(by_state[f"Q-{state}"], Q_ROLES, tower)
        look = ate["look-h1"] + ate["look-h2"]
        q_beh[state] = Fraction(ate["apple"], 8) - Fraction(look, 8)
        q_strict[state] = Fraction(strict["apple"], 8) - Fraction(look, 8)
    m["dq_s8_beh"], m["dq_sour_beh"], m["dq_sweet_beh"] = q_beh["S8"], q_beh[SOUR], q_beh[SWEET]
    m["sour_drop_beh"] = q_beh[SWEET] - q_beh[SOUR]
    if tower:
        m["d_learn_strict"] = _mean(d_strict[c] for c in LEARN_CHECKS)
        m["fmn_strict"] = _mean(fmn_strict[c] for c in LEARN_CHECKS)
        m["dq_s8_strict"], m["dq_sour_strict"], m["dq_sweet_strict"] = (q_strict["S8"], q_strict[SOUR],
                                                                        q_strict[SWEET])
        m["sour_drop_strict"] = q_strict[SWEET] - q_strict[SOUR]
        settled = sum(1 for d in rec.decisions.values() if d["mind"]["verdict"] != "unsettled")
        m["settle_rate"] = Fraction(settled, len(rec.decisions))
        m["h1_new"] = rec.h1_new
    m.update(taste_noticed(rec))
    m.update(reported(rec))
    return m


def partial_measures(rec) -> dict:
    """A floor run cut short after S8's checks (power check only, KT-104): D_learn alone."""
    by_state = {}
    for p in rec.probes:
        by_state.setdefault(p["state"], []).append(p)
    d = {}
    for c in LEARN_CHECKS:
        ate, _ = _tally(by_state[f"S{c}"], P_ROLES, False)
        d[c] = Fraction(ate["far"], 8) - Fraction(ate["look-h1"] + ate["look-far"], 8)
    return {"family": rec.family_number, "run": rec.run_number, "label": rec.label,
            "agent_type": rec.agent_type, "mind_class": rec.mind_class,
            "d_learn_beh": _mean(d[c] for c in LEARN_CHECKS)}


def reported(rec) -> dict:
    """Section 10's counts: poison bites, forced tastes, h2's own verdict, decision times."""
    out = {}
    main = [d for d in rec.decisions.values() if d["role"] in ("main", "h2")]
    out["forced_skip_picks"] = sum(1 for d in main if d["role"] == "main" and d["mind"]["action"] == "skip")
    out["h2_forced"] = any(d.get("forced") for d in main if d["role"] == "h2")
    out["poison_picked_on_forced"] = sum(1 for d in main if d["role"] == "main" and d["mind"]["action"] == "eat"
                                         and d["outcome_milli"] < 0)
    out["lookalike_eats_on_checks"] = sum(1 for p in rec.probes if p["ate"] and p["role"].startswith("look"))
    if rec.mind_class == "tower":
        h2 = next(d for d in main if d["role"] == "h2")
        v = h2["verdict_lid"]
        out["h2_verdict"] = (v if v in ("unknown", "unsettled")
                             else "H set" if v in rec.h_sets["S8"] else "other")
        steps = [d["mind"]["settle_step"] for d in rec.decisions.values()
                 if d["mind"]["verdict"] == "unknown" and d["mind"]["settle_step"] is not None]
        out["unknown_settled_before_step_7"] = sum(1 for s in steps if s < 7)
        out["unknown_settled"] = len(steps)
        made_at_h2 = {e["lid"] for e in rec.lineage_log if e["type"] in ("new", "split")
                      and e["item"] in ("h2", "sweet")}
        after = [p for p in rec.probes if p["state"] in (f"Q-{SOUR}", f"Q-{SWEET}") and p["ate"]]
        out["eats_after_h2"] = len(after)
        out["eats_after_h2_naming_h2_candidate"] = sum(1 for p in after if p["verdict"] in made_at_h2)
    return out


assert traits.TASTE_INDICES == (18, 19, 20, 21)
