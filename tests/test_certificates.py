"""The certificate checker catches every kind of broken object (section 2).

Each test breaks one rule in an otherwise valid plan and checks that
verify_run_plan names it. A checker that passes everything would fail here.
"""

import copy
import dataclasses

import pytest

from world import constants as C
from world import keys, traits
from world import run_plan as rp
from world.certificates import (far_apple_failure, neutral_failure, verify_family, verify_run_plan,
                                warmup_kind_failure)
from world.kinds import Kind

KEY = keys.tuning_set_key()


@pytest.fixture(scope="module")
def plan():
    p = rp.generate_run("practice", KEY, C.GENERATOR_TEST_FAMILY_START + 77, 2)
    assert verify_run_plan(p, rp.tuning_family) == []
    return p


def with_value(obj, trait, value):
    v = list(obj.values)
    v[trait] = value
    if trait == traits.COARSE_HUE:
        v[traits.EXACT_HUE] = min(max(value + obj.hue_offset, 0.0), 1.0)
    return dataclasses.replace(obj, values=tuple(v))


def replace_in(plan, attr, label, new):
    p = copy.copy(plan)
    setattr(p, attr, [new if o.label == label else o for o in getattr(plan, attr)])
    return p


def problems(plan):
    return verify_run_plan(plan, rp.tuning_family)


def test_far_apple_too_close_in_hue(plan):
    far = next(o for o in plan.P if o.label == "P-far-3")
    bad = with_value(far, traits.COARSE_HUE, plan.h1.values[traits.COARSE_HUE])
    out = problems(replace_in(plan, "P", "P-far-3", bad))
    assert any("P-far-3" in m and "coarse hue" in m for m in out)


def test_h1_not_super_sweet(plan):
    p = copy.copy(plan)
    p.h1 = with_value(plan.h1, traits.SWEET, 0.5)
    assert "h1 is not super-sweet" in problems(p)


def test_a_sour_above_half(plan):
    p = copy.copy(plan)
    p.a = dict(plan.a)
    p.a[3] = with_value(plan.a[3], traits.SOUR, 0.8)
    assert "a3 has sour above 0.5" in problems(p)


def test_h2_not_super_sour(plan):
    p = copy.copy(plan)
    p.h2 = with_value(plan.h2, traits.SOUR, 0.5)
    assert "h2 is not super-sour" in problems(p)


def test_neutral_inside_h_bands(plan):
    n = next(o for o in plan.P if o.label == "P-neutral-1")
    bad = n
    for t in plan.family.H.core:
        lo, hi = plan.family.H.bands[t]
        bad = with_value(bad, t, (lo + hi) / 2)
    out = problems(replace_in(plan, "P", "P-neutral-1", bad))
    assert any("P-neutral-1" in m and "neutral" in m for m in out)


def test_copy_that_is_not_exact(plan):
    c = next(o for o in plan.Q if o.label == "Q-copy-2")
    bad = with_value(c, traits.STEM if hasattr(traits, "STEM") else traits.INDEX["stem"], 0.123)
    assert "Q-copy-2 is not an exact copy of h1" in problems(replace_in(plan, "Q", "Q-copy-2", bad))


def test_lookalike_free_trait_too_far_from_model(plan):
    look = next(o for o in plan.P if o.label == "P-look-h1-2")
    t = next(t for t in traits.OBSERVABLE
             if t not in plan.family.H.core and t not in (traits.SCENE, traits.HOST, traits.EXACT_HUE))
    v = plan.h1.values[t]
    bad = with_value(look, t, v + 0.2 if v < 0.5 else v - 0.2)
    out = problems(replace_in(plan, "P", "P-look-h1-2", bad))
    assert any("P-look-h1-2" in m and "within 0.10" in m for m in out)


def test_lookalike_core_outside_its_band(plan):
    look = next(o for o in plan.Q if o.label == "Q-look-h2-1")
    t = look.kind.moved[0]
    bad = with_value(look, t, plan.family.H.bands[t][0])
    out = problems(replace_in(plan, "Q", "Q-look-h2-1", bad))
    assert any("Q-look-h2-1" in m and "core" in m for m in out)


def test_q_near_apple_too_far(plan):
    q = next(o for o in plan.Q if o.label == "Q-near-h2-4")
    t = next(t for t in traits.OBSERVABLE
             if t not in plan.family.H.core and t not in (traits.SCENE, traits.HOST, traits.EXACT_HUE))
    lo, hi = plan.family.H.ranges[t]
    v = plan.h2.values[t]
    far = hi if hi - v > v - lo else lo
    if abs(far - v) <= C.Q_NEAR:
        pytest.skip("this trait's range has no room beyond 0.10")
    out = problems(replace_in(plan, "Q", "Q-near-h2-4", with_value(q, t, far)))
    assert any("Q-near-h2-4" in m and "within 0.10" in m for m in out)


def test_context_must_be_h1s(plan):
    a = copy.copy(plan)
    a.a = dict(plan.a)
    a.a[2] = with_value(plan.a[2], traits.SCENE, (plan.h1.values[traits.SCENE] + 0.5) % 1)
    assert any("a2" in m and "context" in m for m in problems(a))


def test_warmup_scene_too_close(plan):
    p = copy.copy(plan)
    s = plan.warmup_slots[2]
    p.warmup_slots = list(plan.warmup_slots)
    p.warmup_slots[2] = dataclasses.replace(s, scene=plan.h1.values[traits.SCENE])
    assert any("warm-up slot 3" in m and "40 noise widths" in m for m in problems(p))


def test_teaching_order(plan):
    p = copy.copy(plan)
    t = list(plan.teaching)
    t[2], t[4] = t[4], t[2]
    p.teaching = t
    assert any("out of order" in m for m in problems(p))


def test_temperament_and_trait_order(plan):
    p = copy.copy(plan)
    p.reserve_milli = 61_000
    p.boldness = 0.7
    p.trait_order = tuple(range(21)) + (0,)
    out = problems(p)
    assert "R outside 20 to 60" in out and "b outside 0.1 to 0.6" in out
    assert "trait order is not one shuffle of all 22 traits" in out


def test_values_outside_zero_one(plan):
    q = next(o for o in plan.Q if o.label == "Q-near-h1-1")
    bad = with_value(q, traits.INDEX["salty"], 1.5)
    assert any("not 22 numbers from 0 to 1" in m for m in problems(replace_in(plan, "Q", "Q-near-h1-1", bad)))


def test_family_with_a_broken_lookalike_kind(plan):
    fam = plan.family
    k5 = fam.lookalike_kinds[5]
    t = k5.moved[0]
    bands = dict(k5.bands)
    bands[t] = fam.H.bands[t]
    broken = dataclasses.replace(fam, lookalike_kinds={**fam.lookalike_kinds, 5: dataclasses.replace(k5, bands=bands)})
    assert any("lookalike-5" in m for m in verify_family(broken))


# The predicates on their own, with hand-made values.

def values(**named):
    v = [0.5] * traits.N_TRAITS
    for name, x in named.items():
        v[traits.INDEX[name]] = x
    return tuple(v)


def test_far_apple_rule_by_hand():
    h1 = values(coarse_hue=0.2, size=0.2)
    ok = values(coarse_hue=0.6, size=0.6)
    assert far_apple_failure(ok, h1, [values(coarse_hue=0.25, size=0.25)]) == ""
    assert "coarse hue" in far_apple_failure(values(coarse_hue=0.45, size=0.6), h1, [])
    assert "size" in far_apple_failure(values(coarse_hue=0.6, size=0.45), h1, [])
    look = values(coarse_hue=0.2, size=0.2, roundness=1.0, lobes=1.0)  # surface distance 25
    assert "surface" in far_apple_failure(ok, h1, [look])                # ok's is 20


def kind(core_bands):
    core = tuple(sorted(core_bands))
    return Kind("k", "nothing", 1, "test", 1, 1, core, dict(core_bands), {})


def test_warmup_kind_rule_by_hand():
    st, lv, sp = traits.INDEX["stem"], traits.INDEX["leaves"], traits.INDEX["spots"]
    H = kind({st: (0.40, 0.45), lv: (0.40, 0.45), sp: (0.40, 0.45), traits.INDEX["sheen"]: (0.4, 0.45)})
    far = kind({st: (0.56, 0.61), lv: (0.56, 0.61)})              # gaps of 0.11
    near = kind({st: (0.50, 0.55), lv: (0.42, 0.47)})             # a gap of 0.05 and an overlap
    one = kind({st: (0.50, 0.55), lv: (0.60, 0.65)})              # only one close
    elsewhere = kind({traits.INDEX["texture"]: (0.40, 0.45), traits.INDEX["smell_1"]: (0.40, 0.45)})
    assert warmup_kind_failure(far, H) == ""
    assert warmup_kind_failure(near, H) != ""
    assert warmup_kind_failure(one, H) == ""
    assert warmup_kind_failure(elsewhere, H) == ""                 # no core band on H's core traits


def test_neutral_rule_by_hand():
    st, lv = traits.INDEX["stem"], traits.INDEX["leaves"]
    H = kind({st: (0.40, 0.45), lv: (0.40, 0.45), traits.INDEX["spots"]: (0.4, 0.45),
              traits.INDEX["sheen"]: (0.4, 0.45)})
    h1 = values()
    outside = values(stem=0.6, leaves=0.2, coarse_hue=0.9, size=0.9)  # surface distance 20
    assert neutral_failure(outside, H, h1, 20.0) == ""
    assert neutral_failure(outside, H, h1, 21.0) == ""                # within 10%
    assert "surface" in neutral_failure(outside, H, h1, 25.0)
    assert "fewer than 2" in neutral_failure(values(stem=0.6, coarse_hue=0.9, size=0.9), H, h1, 20.0)


# Gaps found by the independent review, each closed and kept closed.

def test_an_apple_with_the_wrong_kind(plan):
    far = next(o for o in plan.P if o.label == "P-far-3")
    bad = dataclasses.replace(far, kind=plan.family.neutral_kinds[1])
    assert any("P-far-3 is not a far apple of H" in m for m in problems(replace_in(plan, "P", "P-far-3", bad)))
    p = copy.copy(plan)
    p.h2 = dataclasses.replace(plan.h2, kind=plan.family.lookalike_kinds[3])
    assert "h2 is not a far apple of H" in problems(p)
    q = next(o for o in plan.Q if o.label == "Q-near-h1-2")
    bad = dataclasses.replace(q, kind=plan.family.lookalike_kinds[3])
    assert any("Q-near-h1-2 is not an apple of H" in m for m in problems(replace_in(plan, "Q", "Q-near-h1-2", bad)))


def test_kinds_with_the_wrong_nature(plan):
    fam = plan.family
    assert "H is not a nourishing kind" in verify_family(dataclasses.replace(fam, H=dataclasses.replace(fam.H, nature="nothing")))
    looks = {**fam.lookalike_kinds, 4: dataclasses.replace(fam.lookalike_kinds[4], nature="nothing")}
    assert "a look-alike kind is not poison" in verify_family(dataclasses.replace(fam, lookalike_kinds=looks))
    p = copy.copy(plan)
    p.warmup_slots = list(plan.warmup_slots)
    p.warmup_slots[0] = dataclasses.replace(plan.warmup_slots[0], kind=dataclasses.replace(plan.warmup_slots[0].kind, nature="poison"))
    assert any("warm-up slot 1: its kind's nature" in m for m in problems(p))


def test_warmup_order_must_be_a_shuffle_of_the_40_items(plan):
    p = copy.copy(plan)
    order = list(plan.warmup_order)
    order[5] = order[6]
    p.warmup_order = tuple(order)
    assert "warm-up order is not one shuffle of the 40 warm-up items" in problems(p)
    p.warmup_order = plan.warmup_order[:39]
    assert "warm-up order is not one shuffle of the 40 warm-up items" in problems(p)


def test_teaching_apples_are_the_runs_own(plan):
    p = copy.copy(plan)
    t = list(plan.teaching)
    t[2] = with_value(plan.a[2], traits.SOUR, 0.95)
    p.teaching = t
    assert "teaching item a2 is not the run's a2" in problems(p)
    t = list(plan.teaching)
    t[0] = with_value(plan.h1, traits.SWEET, 0.2)
    p.teaching = t
    assert "teaching item h1 is not the run's h1" in problems(p)


def test_neutral_kind_in_use_is_checked(plan):
    p = copy.copy(plan)
    k1 = plan.neutral_kinds[1]
    wide = {t: (max(0.0, lo - 0.15), min(1.0, hi + 0.15)) for t, (lo, hi) in k1.bands.items()}
    p.neutral_kinds = {**plan.neutral_kinds, 1: dataclasses.replace(k1, bands=wide)}
    out = problems(p)
    assert any("wrong width" in m for m in out)
    assert "neutral kind 1 in use is not the family's own" in out
    other = rp.tuning_family(7).neutral_kinds[1]
    p.neutral_kinds = {**plan.neutral_kinds, 1: dataclasses.replace(other, try_number=2)}
    out = problems(p)
    assert "neutral kind 1 in use is not this family's" in out


def test_warmup_models_come_from_the_source_family(plan):
    p = copy.copy(plan)
    p.warmup_slots = list(plan.warmup_slots)
    p.warmup_slots[1] = dataclasses.replace(plan.warmup_slots[1], model_kind=plan.family.H)
    out = problems(p)
    assert any("models are not apples of tuning family" in m for m in out)
    # all 10 poison items copying one model
    first = plan.warmup_models[0].label
    p = copy.copy(plan)
    p.warmup_items = [dataclasses.replace(o, model=first) if o.label.startswith("warmup-2-") else o
                      for o in plan.warmup_items]
    assert "warm-up poison items do not each copy a different fresh model" in problems(p)
    # a missing model is reported, not a crash
    p.warmup_items = [dataclasses.replace(o, model="nobody") if o.label == "warmup-2-01" else o
                      for o in plan.warmup_items]
    assert "warmup-2-01: its model is missing" in problems(p)


def test_neutral_rule_upper_bound_by_hand():
    st, lv = traits.INDEX["stem"], traits.INDEX["leaves"]
    H = kind({st: (0.40, 0.45), lv: (0.40, 0.45), traits.INDEX["spots"]: (0.4, 0.45),
              traits.INDEX["sheen"]: (0.4, 0.45)})
    outside = values(stem=0.6, leaves=0.2, coarse_hue=0.9, size=0.9)   # surface distance 20
    assert "surface" in neutral_failure(outside, H, values(), 15.0)     # 20 > 16.5
    assert neutral_failure(outside, H, values(), 20.0 / 1.1 + 1e-9) == ""
    assert "surface" in neutral_failure(outside, H, values(), 20.0 / 1.1 - 1e-6)


def test_warmup_models_are_ten_different_draws(plan):
    """Second review: 10 relabelled copies of one model apple must not pass."""
    m1 = plan.warmup_models[0]
    p = copy.copy(plan)
    p.warmup_models = [dataclasses.replace(m1, label=f"warmup-model-{i:02d}") for i in range(1, 11)]
    out = problems(p)
    assert sum("not drawn at its own place" in m for m in out) == 9
    # right places and tries, but one apple's values everywhere
    p.warmup_models = [dataclasses.replace(m, values=m1.values, hue_offset=m1.hue_offset)
                       for m in plan.warmup_models]
    out = problems(p)
    assert sum("not the run key's draw at its place and try" in m for m in out) == 9
