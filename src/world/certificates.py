"""Certificates: the rules every generated object must meet (section 2).

The rules that can fail decide redraws in run_plan.py: the far-apple rule,
h2's rules, the neutral rule and the warm-up kind check. They compare
exactly, as the frozen text words them.

verify_family() and verify_run_plan() re-check every object and kind rule of
section 2, section 5 and the approved rows on a finished plan, including the
rules that hold by construction, and return the list of violations (empty
when all is well). Re-checks of drawn bounds allow C.CHECK_TOLERANCE for
float rounding (KT-91). The redraw log is an audit record of the process,
not a property of the objects; the tests check it. Certificates judge true
generated values, never noisy readings (KT-36).
"""

from itertools import combinations

from . import constants as C
from . import keys, traits
from .kinds import NOTHING, NOURISH, POISON, draw_base_kind, place_neutral_kind
from .objects import (APPLE, COPY, FAR_APPLE, LOOKALIKE, MODEL, NEUTRAL, WARMUP, band_gap, clip01, draw_member,
                      gap_outside, surface_distance, taste_distance)
from .streams import Draws

EPS = C.CHECK_TOLERANCE
NW = C.NOISE_WIDTH


# ---------------------------------------------------------------------------
# Rules that decide redraws


def far_apple_failure(values, h1_values, h1_lookalikes) -> str:
    """'' if values meet the far-apple rule, else the name of the rule broken (KT-03).

    Coarse hue and size each at least 0.3 from h1's, and a surface distance
    from h1 greater than that of every look-alike modelled on h1 in the same
    check set.
    """
    if abs(values[traits.COARSE_HUE] - h1_values[traits.COARSE_HUE]) < C.FAR_HUE_SIZE_MIN:
        return "far: coarse hue within 0.3 of h1"
    if abs(values[traits.SIZE] - h1_values[traits.SIZE]) < C.FAR_HUE_SIZE_MIN:
        return "far: size within 0.3 of h1"
    d = surface_distance(values, h1_values)
    if any(d <= surface_distance(look, h1_values) for look in h1_lookalikes):
        return "far: surface distance not above every look-alike modelled on h1"
    return ""


def h2_failure(values, h1_values, h1_lookalikes, earlier_apples) -> str:
    """h2: the far-apple rule against P's look-alikes modelled on h1, and a taste
    at least 10 noise widths from h1's and from each of a2's to a4's (KT-16)."""
    why = far_apple_failure(values, h1_values, h1_lookalikes)
    if why:
        return "h2 " + why
    for other in earlier_apples:
        if taste_distance(values, other) < C.H2_TASTE_DIST_NW:
            return "h2: taste within 10 noise widths of an earlier apple"
    return ""


def neutral_failure(values, H, h1_values, mean_far_surface: float) -> str:
    """A neutral lies at least 10 noise widths outside H's bands on 2 or more of
    H's core traits, and its surface distance from h1 is within 0.9 to 1.1
    times the mean surface distance of P's far apples (KT-03, KT-43)."""
    outside = sum(1 for t in H.core if gap_outside(values[t], H.bands[t]) >= C.NEUTRAL_OUTSIDE_NW * NW)
    if outside < C.NEUTRAL_MIN_CORE:
        return "neutral: fewer than 2 core traits 10 noise widths outside H's bands"
    d = surface_distance(values, h1_values)
    if not C.NEUTRAL_SURFACE_LO * mean_far_surface <= d <= C.NEUTRAL_SURFACE_HI * mean_far_surface:
        return "neutral: surface distance outside 0.9 to 1.1 times the far apples' mean"
    return ""


def warmup_kind_failure(kind, H) -> str:
    """No warm-up kind may have core bands within 10 noise widths of H's bands
    on 2 or more of H's core traits (KT-03). Within means a gap under 0.10
    between band edges, overlap included, counted only on H's core traits
    where the warm-up kind has a core band of its own (KT-39)."""
    close = sum(1 for t in H.core
                if t in kind.bands and band_gap(kind.bands[t], H.bands[t]) < C.WARMUP_KIND_GAP_NW * NW)
    if close >= C.WARMUP_KIND_MIN_CORE:
        return "warm-up kind: core bands within 10 noise widths of H's on 2 or more core traits"
    return ""


# ---------------------------------------------------------------------------
# Full checks


def _in(v, lo, hi) -> bool:
    return lo - EPS <= v <= hi + EPS


def verify_base_kind(kind, out: list, full_taste: bool) -> None:
    """An apple kind (full_taste) or a neutral kind (taste ranges drawn as free traits)."""
    name = f"{kind.set_name}/{kind.family}/{kind.name}"
    if len(kind.core) != C.N_CORE or len(set(kind.core)) != C.N_CORE:
        out.append(f"{name}: not exactly 4 distinct core traits")
    if not set(kind.core) <= set(traits.CORE_ELIGIBLE):
        out.append(f"{name}: a core trait outside the 13 eligible")
    if set(kind.bands) != set(kind.core):
        out.append(f"{name}: bands do not match the core traits")
    for t, (lo, hi) in kind.bands.items():
        centre = (lo + hi) / 2
        if abs((hi - lo) - C.CORE_BAND_WIDTH) > EPS or not _in(centre, C.CORE_CENTRE_LO, C.CORE_CENTRE_HI):
            out.append(f"{name}: core band on {traits.TRAITS[t]} has the wrong width or centre")
    expected_free = set(traits.RANGED) - set(kind.core)
    if set(kind.ranges) != expected_free:
        out.append(f"{name}: free ranges missing or extra")
    for t, (lo, hi) in kind.ranges.items():
        if full_taste and t in traits.TASTE_INDICES:
            if (lo, hi) != (0.0, 1.0):
                out.append(f"{name}: taste {traits.TRAITS[t]} does not range over 0 to 1")
            continue
        if not (_in(hi - lo, C.FREE_WIDTH_LO, C.FREE_WIDTH_HI) and lo >= -EPS and hi <= 1 + EPS):
            out.append(f"{name}: free range on {traits.TRAITS[t]} has the wrong width or place")


def verify_lookalike_kind(kind, H, out: list) -> None:
    name = f"{kind.set_name}/{kind.family}/{kind.name}"
    if kind.core != H.core or kind.ranges != H.ranges:
        out.append(f"{name}: core traits or free ranges differ from H's")
    if len(kind.moved) != 2 or not set(kind.moved) <= set(H.core):
        out.append(f"{name}: does not move exactly 2 of H's core traits")
    for t in H.core:
        if t in kind.moved:
            lo, hi = kind.bands[t]
            gap = band_gap(kind.bands[t], H.bands[t])
            if abs((hi - lo) - C.CORE_BAND_WIDTH) > EPS or lo < -EPS or hi > 1 + EPS:
                out.append(f"{name}: moved band on {traits.TRAITS[t]} has the wrong width or leaves 0 to 1")
            if not _in(gap, C.MOVED_GAP_LO_NW * NW, C.MOVED_GAP_HI_NW * NW):
                out.append(f"{name}: moved band on {traits.TRAITS[t]} is not 20 to 30 noise widths from H's")
        elif kind.bands[t] != H.bands[t]:
            out.append(f"{name}: kept band on {traits.TRAITS[t]} differs from H's")


def verify_family(fam) -> list:
    out = []
    H = fam.H
    verify_base_kind(H, out, full_taste=True)
    if H.nature != NOURISH or H.name != "H":
        out.append("H is not a nourishing kind")
    kinds = [H] + list(fam.lookalike_kinds.values()) + list(fam.neutral_kinds.values())
    if any(k.family != fam.number or k.set_name != fam.set_name or k.try_number != 1 for k in kinds):
        out.append("a kind is not the family's own first draw")
    if sorted(fam.lookalike_kinds) != list(range(1, C.N_LOOKALIKE_KINDS + 1)) or \
            sorted(fam.neutral_kinds) != list(range(1, C.N_NEUTRAL_KINDS + 1)):
        out.append("the family does not have look-alike kinds 1 to 8 and neutral kinds 1 to 4")
        return out
    if any(k.nature != POISON for k in fam.lookalike_kinds.values()):
        out.append("a look-alike kind is not poison")
    if any(k.nature != NOTHING for k in fam.neutral_kinds.values()):
        out.append("a neutral kind is not of nature nothing")
    if sorted(fam.labels) != list(H.core):
        out.append("labels c1 to c4 are not a relabelling of H's core traits")
    pairs = set(combinations(H.core, 2))
    p1, p2 = fam.teaching_pairs
    if p1 not in pairs or p2 not in pairs or p1 == p2:
        out.append("teaching pairs are not two different pairs of H's core traits")
    for k in (1, 2):
        if fam.lookalike_kinds[k].moved != fam.teaching_pairs[k - 1]:
            out.append(f"look-alike kind {k} does not move teaching pair {k}")
    check_pairs = []
    for k, (a, b) in ((3, (1, 2)), (4, (3, 4)), (5, (1, 3)), (6, (2, 4)), (7, (1, 4)), (8, (2, 3))):
        want = fam.label_pair(a, b)
        check_pairs.append(fam.lookalike_kinds[k].moved)
        if fam.lookalike_kinds[k].moved != want:
            out.append(f"look-alike kind {k} does not move c{a}c{b}")
    if set(check_pairs) != pairs:
        out.append("check kinds 3 to 8 do not cover the 6 pairs once each")
    for k in range(1, C.N_LOOKALIKE_KINDS + 1):
        verify_lookalike_kind(fam.lookalike_kinds[k], H, out)
    for k in range(1, C.N_NEUTRAL_KINDS + 1):
        verify_base_kind(fam.neutral_kinds[k], out, full_taste=False)
    return out


def _verify_neutral_kind_in_use(plan, k, out):
    """A neutral kind a run uses: the family's own, or its next tries (KT-03, KT-85)."""
    kind = plan.neutral_kinds.get(k)
    if kind is None:
        out.append(f"neutral kind {k} missing from the run")
        return
    verify_base_kind(kind, out, full_taste=False)
    if kind.nature != NOTHING or kind.family != plan.family_number or kind.set_name != plan.family.set_name:
        out.append(f"neutral kind {k} in use is not this family's")
    if kind.try_number < 1:
        out.append(f"neutral kind {k} in use has no valid try number")
        return
    if kind.try_number == 1 and kind is not plan.family.neutral_kinds[k]:
        out.append(f"neutral kind {k} in use is not the family's own")
    world = keys.stream_key(plan.family.key, keys.STREAM_WORLD)
    fresh = draw_base_kind(Draws(world, place_neutral_kind(k), kind.try_number), f"neutral-{k}", NOTHING,
                           plan.family_number, plan.family.set_name)
    if fresh.record() != kind.record():
        out.append(f"neutral kind {k} in use was not drawn by the family key")


def _check_member(obj, kind, out, context=None):
    v = obj.values
    for t in range(traits.N_TRAITS):
        if t == traits.EXACT_HUE:
            continue
        if context is not None and t in (traits.SCENE, traits.HOST):
            want = context[0] if t == traits.SCENE else context[1]
            if v[t] != want:
                out.append(f"{obj.label}: {traits.TRAITS[t]} is not the required context value")
            continue
        lo, hi = kind.bands[t] if t in kind.bands else kind.ranges[t]
        if not _in(v[t], lo, hi):
            out.append(f"{obj.label}: {traits.TRAITS[t]} outside its kind's band or range")
    if abs(obj.hue_offset) > C.HUE_OFFSET_MAX + EPS:
        out.append(f"{obj.label}: hue offset beyond +-0.05")
    _check_exact_hue(obj, out)


def _check_exact_hue(obj, out):
    v = obj.values
    if v[traits.EXACT_HUE] != clip01(v[traits.COARSE_HUE] + obj.hue_offset):
        out.append(f"{obj.label}: exact hue is not coarse hue plus its offset, clipped")


def _check_lookalike(obj, kind, model, context, out):
    v = obj.values
    if obj.role not in (LOOKALIKE, WARMUP) or kind.nature != POISON:
        out.append(f"{obj.label}: not a poison look-alike")
    if obj.hue_offset != model.hue_offset:
        out.append(f"{obj.label}: does not take its model's hue offset")
    for t in range(traits.N_TRAITS):
        if t == traits.EXACT_HUE:
            continue
        if t in (traits.SCENE, traits.HOST):
            want = context[0] if t == traits.SCENE else context[1]
            if v[t] != want:
                out.append(f"{obj.label}: {traits.TRAITS[t]} is not the required context value")
        elif t in kind.bands:
            if not _in(v[t], *kind.bands[t]):
                out.append(f"{obj.label}: core {traits.TRAITS[t]} outside its kind's band")
        else:
            lo = clip01(model.values[t] - C.LOOKALIKE_FREE_OFFSET)
            hi = clip01(model.values[t] + C.LOOKALIKE_FREE_OFFSET)
            if not _in(v[t], lo, hi):
                out.append(f"{obj.label}: {traits.TRAITS[t]} not within 0.10 of its model")
    _check_exact_hue(obj, out)


def verify_run_plan(plan, tuning_family=None) -> list:
    """Every rule of the run plan, re-checked from scratch. Returns violations."""
    out = []
    fam, H = plan.family, plan.family.H
    out += verify_family(fam)
    h1 = plan.h1
    ctx = (h1.values[traits.SCENE], h1.values[traits.HOST])

    # Run draws
    if not C.R_MILLI_LO <= plan.reserve_milli <= C.R_MILLI_HI:
        out.append("R outside 20 to 60")
    if not _in(plan.boldness, C.BOLDNESS_LO, C.BOLDNESS_HI):
        out.append("b outside 0.1 to 0.6")
    if sorted(plan.trait_order) != list(range(traits.N_TRAITS)):
        out.append("trait order is not one shuffle of all 22 traits")

    # h1 and a2 to a4
    _check_member(h1, H, out)
    if h1.role != APPLE or h1.kind is not H:
        out.append("h1 is not an apple of H")
    if not (h1.values[traits.SWEET] >= C.H1_SWEET_MIN - EPS and h1.values[traits.SOUR] <= C.H1_SOUR_MAX + EPS):
        out.append("h1 is not super-sweet")
    for k in (2, 3, 4):
        a = plan.a[k]
        _check_member(a, H, out, context=ctx)
        if a.role != APPLE or a.kind is not H:
            out.append(f"a{k} is not an apple of H")
        if a.values[traits.SOUR] > C.A_SOUR_MAX + EPS:
            out.append(f"a{k} has sour above 0.5")

    # Teaching order (KT-07)
    t = plan.teaching
    expected = [("h1", None, None), ("t2", 1, "h1"), ("a2", None, None), ("t4", 2, "a2"),
                ("a3", None, None), ("t6", 1, "a3"), ("a4", None, None), ("t8", 2, "a4")]
    by_label = {"h1": h1, "a2": plan.a[2], "a3": plan.a[3], "a4": plan.a[4]}
    for item, (label, kind_k, model) in zip(t, expected):
        if item.label != label:
            out.append(f"teaching item {label} out of order")
            continue
        if kind_k is None:
            if item is not by_label[label]:
                out.append(f"teaching item {label} is not the run's {label}")
        else:
            if item.kind is not fam.lookalike_kinds[kind_k] or item.model != model:
                out.append(f"{label} is not a kind-{kind_k} look-alike modelled on {model}")
            _check_lookalike(item, item.kind, by_label[model], ctx, out)
    if len(t) != 8:
        out.append("teaching does not have 8 items")

    # Warm-up (KT-06, KT-39)
    out += _verify_warmup(plan, tuning_family, ctx)

    # P (section 5)
    P = {o.label: o for o in plan.P}
    look_h1 = [P[f"P-look-h1-{i}"] for i in range(1, 5)]
    far = [P[f"P-far-{i}"] for i in range(1, 9)]
    for i, pair in enumerate(((1, 2), (3, 4), (1, 3), (2, 4)), start=1):
        o = P[f"P-look-h1-{i}"]
        if o.kind is not fam.check_kind_for_pair(fam.label_pair(*pair)) or o.model != "h1":
            out.append(f"P-look-h1-{i} is not modelled on h1 from the c{pair[0]}c{pair[1]} kind")
        _check_lookalike(o, o.kind, h1, ctx, out)
    for o in far:
        _check_member(o, H, out, context=ctx)
        if o.role != FAR_APPLE or o.kind is not H:
            out.append(f"{o.label} is not a far apple of H")
        why = far_apple_failure(o.values, h1.values, [x.values for x in look_h1])
        if why:
            out.append(f"{o.label}: {why}")
    for i, pair in enumerate(((1, 2), (3, 4), (1, 4), (2, 3)), start=1):
        o = P[f"P-look-far-{i}"]
        if o.kind is not fam.check_kind_for_pair(fam.label_pair(*pair)) or o.model != f"P-far-{i}":
            out.append(f"P-look-far-{i} is not modelled on far apple {i} from the c{pair[0]}c{pair[1]} kind")
        _check_lookalike(o, o.kind, P[f"P-far-{i}"], ctx, out)
    mean_far = sum(surface_distance(o.values, h1.values) for o in far) / len(far)
    for k in range(1, C.N_NEUTRAL_KINDS + 1):
        _verify_neutral_kind_in_use(plan, k, out)
    for i, k in ((1, 1), (2, 2)):
        _verify_neutral(P[f"P-neutral-{i}"], plan.neutral_kinds[k], H, h1, ctx, mean_far, out)
    for i in (1, 2):
        _verify_copy(P[f"P-copy-{i}"], h1, out)
    if len(plan.P) != 20:
        out.append("P does not have 20 items")

    # h2 (KT-16)
    h2 = plan.h2
    _check_member(h2, H, out, context=ctx)
    if h2.role != FAR_APPLE or h2.kind is not H:
        out.append("h2 is not a far apple of H")
    if not (h2.values[traits.SWEET] <= C.H2_SWEET_MAX + EPS and h2.values[traits.SOUR] >= C.H2_SOUR_MIN - EPS):
        out.append("h2 is not super-sour")
    why = h2_failure(h2.values, h1.values, [x.values for x in look_h1],
                     [h1.values] + [plan.a[k].values for k in (2, 3, 4)])
    if why:
        out.append(why)

    # Q (section 5)
    Q = {o.label: o for o in plan.Q}
    near_traits = [t for t in traits.OBSERVABLE
                   if t not in H.bands and t not in (traits.SCENE, traits.HOST, traits.EXACT_HUE)]
    for base, ref in (("h1", h1), ("h2", h2)):
        for i in range(1, 5):
            o = Q[f"Q-near-{base}-{i}"]
            _check_member(o, H, out, context=ctx)
            if o.role != APPLE or o.kind is not H:
                out.append(f"{o.label} is not an apple of H")
            for tr in near_traits:
                if abs(o.values[tr] - ref.values[tr]) > C.Q_NEAR + EPS:
                    out.append(f"{o.label}: {traits.TRAITS[tr]} not within 0.10 of {base}'s")
    for base, ref, pairs in (("h1", h1, ((1, 2), (3, 4), (1, 3), (2, 4))),
                             ("h2", h2, ((1, 2), (3, 4), (1, 4), (2, 3)))):
        for i, pair in enumerate(pairs, start=1):
            o = Q[f"Q-look-{base}-{i}"]
            if o.kind is not fam.check_kind_for_pair(fam.label_pair(*pair)) or o.model != base:
                out.append(f"{o.label} is not modelled on {base} from the c{pair[0]}c{pair[1]} kind")
            _check_lookalike(o, o.kind, ref, ctx, out)
    for i, k in ((1, 3), (2, 4)):
        _verify_neutral(Q[f"Q-neutral-{i}"], plan.neutral_kinds[k], H, h1, ctx, mean_far, out)
    for i in (1, 2):
        _verify_copy(Q[f"Q-copy-{i}"], h1, out)
    if len(plan.Q) != 20:
        out.append("Q does not have 20 items")

    # Every object is 22 numbers from 0 to 1 (KT-01)
    for o in plan.all_objects():
        if len(o.values) != traits.N_TRAITS or not all(0.0 <= x <= 1.0 for x in o.values):
            out.append(f"{o.label}: not 22 numbers from 0 to 1")
    return out


def _verify_neutral(o, kind, H, h1, ctx, mean_far, out):
    if o.role != NEUTRAL or kind.nature != NOTHING:
        out.append(f"{o.label} is not a neutral")
    if o.kind is not kind:
        out.append(f"{o.label} is not from the neutral kind in use")
    _check_member(o, kind, out, context=ctx)
    why = neutral_failure(o.values, H, h1.values, mean_far)
    if why:
        out.append(f"{o.label}: {why}")


def _verify_copy(o, h1, out):
    if o.role != COPY or o.values != h1.values or o.hue_offset != h1.hue_offset or o.kind is not h1.kind:
        out.append(f"{o.label} is not an exact copy of h1")


def _verify_warmup(plan, tuning_family, ctx) -> list:
    out = []
    H = plan.family.H
    slots = plan.warmup_slots
    if [s.nature for s in slots] != [NOURISH, POISON, NOTHING, NOTHING] or [s.slot for s in slots] != [1, 2, 3, 4]:
        out.append("warm-up kinds are not 1 nourishing, 1 poison and 2 nothing kinds")
        return out
    fams = [s.source_family for s in slots]
    if len(set(fams)) != 4 or not all(1 <= f <= C.N_TUNING_FAMILIES for f in fams):
        out.append("warm-up kinds do not come from 4 different tuning families")
    if plan.h_is_tuning_family and plan.family_number in fams:
        out.append("a warm-up kind comes from H's own family")
    for s in slots:
        if s.kind.nature != s.nature:
            out.append(f"warm-up slot {s.slot}: its kind's nature is not {s.nature}")
        if (s.model_kind is not None) != (s.nature == POISON):
            out.append(f"warm-up slot {s.slot}: only the poison slot has a model kind")
        if tuning_family is not None:
            src = tuning_family(s.source_family)
            expected = {NOURISH: [src.H], POISON: list(src.lookalike_kinds.values()),
                        NOTHING: list(src.neutral_kinds.values())}[s.nature]
            if s.kind.record() not in [k.record() for k in expected]:
                out.append(f"warm-up slot {s.slot}: kind is not one of tuning family {s.source_family}'s")
            if s.nature == POISON and (s.model_kind is None or s.model_kind.record() != src.H.record()):
                out.append(f"warm-up slot {s.slot}: models are not apples of tuning family {s.source_family}")
        why = warmup_kind_failure(s.kind, H)
        if why:
            out.append(f"warm-up slot {s.slot}: {why}")
        for v, ref in ((s.scene, ctx[0]), (s.host, ctx[1])):
            if abs(v - ref) < C.WARMUP_CONTEXT_MIN_NW * NW - EPS or not 0.0 <= v <= 1.0:
                out.append(f"warm-up slot {s.slot}: scene or host within 40 noise widths of h1's")

    items = plan.warmup_items
    labels = [o.label for o in items]
    want = [f"warmup-{j}-{i:02d}" for j in range(1, C.N_WARMUP_KINDS + 1) for i in range(1, C.N_WARMUP_PER_KIND + 1)]
    if labels != want:
        out.append("warm-up does not have 10 items from each of its 4 kinds")
    if len(plan.warmup_order) != len(want) or sorted(plan.warmup_order) != sorted(want):
        out.append("warm-up order is not one shuffle of the 40 warm-up items")

    models = {m.label: m for m in plan.warmup_models}
    want_models = [f"warmup-model-{i:02d}" for i in range(1, C.N_WARMUP_PER_KIND + 1)]
    if [m.label for m in plan.warmup_models] != want_models:
        out.append("warm-up poison items do not have 10 fresh models")
    from .run_plan import place_warmup_model      # here, since run_plan imports this module
    poison = slots[1]
    world = keys.stream_key(keys.run_key(plan.family.key, plan.run_number), keys.STREAM_WORLD)
    for i, m in enumerate(plan.warmup_models, start=1):
        if m.role != MODEL or m.kind is not poison.model_kind:
            out.append(f"{m.label}: not a fresh apple of the poison slot's family")
        if poison.model_kind is None:
            continue
        _check_member(m, poison.model_kind, out)
        # each model is its own draw of the run key at its own place (KT-81), so 10 copies of one apple fail
        if m.place != place_warmup_model(i) or m.try_number < 1:
            out.append(f"{m.label}: not drawn at its own place")
        elif draw_member(Draws(world, m.place, m.try_number), poison.model_kind) != (m.values, m.hue_offset):
            out.append(f"{m.label}: not the run key's draw at its place and try")
    used_models = []
    for s in slots:
        for o in (o for o in items if o.label.startswith(f"warmup-{s.slot}-")):
            if o.kind is not s.kind or o.role != WARMUP:
                out.append(f"{o.label}: not from its warm-up kind")
            if s.nature == POISON:
                model = models.get(o.model)
                if model is None:
                    out.append(f"{o.label}: its model is missing")
                    continue
                used_models.append(o.model)
                _check_lookalike(o, s.kind, model, (s.scene, s.host), out)
            else:
                _check_member(o, s.kind, out, context=(s.scene, s.host))
    if sorted(used_models) != want_models:
        out.append("warm-up poison items do not each copy a different fresh model")
    return out
