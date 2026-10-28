"""Whole run plans: the draw order, the redraw rules and replay (sections 2 and 5, KT-32)."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from world import constants as C
from world import keys, traits
from world import run_plan as rp
from world.certificates import verify_run_plan
from world.kinds import NOURISH, POISON, generate_family, neutral_kind
from world.objects import COPY, LOOKALIKE, WARMUP, draw_lookalike, draw_member
from world.streams import Draws

KEY = keys.tuning_set_key()
FAMILIES = st.integers(C.GENERATOR_TEST_FAMILY_START, C.GENERATOR_TEST_FAMILY_START + 10**6)
RUNS = st.integers(1, C.RUNS_PER_FAMILY)


def practice_run(n, run):
    return rp.generate_run("practice", KEY, n, run)


@settings(max_examples=150, deadline=None)
@given(FAMILIES, RUNS)
def test_every_run_plan_passes_every_certificate(n, run):
    plan = practice_run(n, run)
    assert verify_run_plan(plan, rp.tuning_family) == []


def test_every_tuning_run_passes_every_certificate():
    for n in range(1, C.N_TUNING_FAMILIES + 1):
        for run in range(1, C.RUNS_PER_FAMILY + 1):
            plan = rp.generate_run("tuning", KEY, n, run)
            assert verify_run_plan(plan, rp.tuning_family) == [], (n, run)
            assert n not in [s.source_family for s in plan.warmup_slots]


def test_a_run_makes_210_decisions():
    plan = practice_run(C.GENERATOR_TEST_FAMILY_START, 1)
    assert len(plan.warmup_items) == 40 and len(plan.teaching) == 8
    assert len(plan.P) == 20 and len(plan.Q) == 20
    assert 40 + 8 + 5 * len(plan.P) + 2 + 3 * len(plan.Q) == 210
    assert sorted(o.label for o in plan.warmup_sequence()) == sorted(o.label for o in plan.warmup_items)
    places = [o.place for o in plan.all_objects()]
    assert len(places) == len(set(places)), "every object has its own place"


def test_replay_gives_identical_plans():
    a = practice_run(C.GENERATOR_TEST_FAMILY_START + 5, 3)
    generate_family.cache_clear()
    b = practice_run(C.GENERATOR_TEST_FAMILY_START + 5, 3)
    assert [o.values for o in a.all_objects()] == [o.values for o in b.all_objects()]
    assert (a.reserve_milli, a.boldness, a.trait_order, a.warmup_order, a.log) == \
           (b.reserve_milli, b.boldness, b.trait_order, b.warmup_order, b.log)


def recompute(plan, obj, models):
    """An object rebuilt from nothing but the run key, its place and its logged try."""
    world = keys.stream_key(keys.run_key(plan.family.key, plan.run_number), keys.STREAM_WORLD)
    d = Draws(world, obj.place, obj.try_number)
    if obj.model and obj.role in (LOOKALIKE, WARMUP):
        m = models[obj.model]
        ctx = (obj.values[traits.SCENE], obj.values[traits.HOST])
        return draw_lookalike(d, obj.kind, m.values, m.hue_offset, ctx)[0]
    limits = {}
    if obj.label == "h1":
        limits = {traits.SWEET: (C.H1_SWEET_MIN, 1.0), traits.SOUR: (0.0, C.H1_SOUR_MAX)}
    elif obj.label in ("a2", "a3", "a4"):
        limits = {traits.SOUR: (0.0, C.A_SOUR_MAX)}
    elif obj.label == "h2":
        limits = {traits.SWEET: (0.0, C.H2_SWEET_MAX), traits.SOUR: (C.H2_SOUR_MIN, 1.0)}
    ctx = None if obj.label == "h1" or obj.label.startswith("warmup-model") else \
        (obj.values[traits.SCENE], obj.values[traits.HOST])
    near = None
    if obj.label.startswith("Q-near"):
        ref = plan.h1 if "h1" in obj.label else plan.h2
        near_traits = [t for t in traits.OBSERVABLE
                       if t not in plan.family.H.bands and t not in (traits.SCENE, traits.HOST, traits.EXACT_HUE)]
        near = (near_traits, ref.values)
    return draw_member(d, obj.kind, ctx, limits, near)[0]


@settings(max_examples=40, deadline=None)
@given(FAMILIES, RUNS)
def test_any_object_can_be_recomputed_from_its_place_and_try(n, run):
    plan = practice_run(n, run)
    models = {o.label: o for o in plan.all_objects()}
    for o in plan.all_objects():
        if o.role == COPY:
            assert o.try_number == 0 and o.values == plan.h1.values
            continue
        assert recompute(plan, o, models) == o.values, o.label


@settings(max_examples=40, deadline=None)
@given(FAMILIES, RUNS)
def test_every_redraw_is_logged(n, run):
    plan = practice_run(n, run)
    if plan.cascades:
        return
    for o in plan.all_objects():
        if o.try_number:
            fails = sum(1 for e in plan.log if e[0] == "redraw" and e[1] == o.label)
            assert o.try_number == 1 + fails, o.label


def test_cascades_and_h1_redraws(monkeypatch):
    monkeypatch.setattr(C, "FAR_MAX_DRAWS", 20)
    seen_h1_redraw = False
    for i in range(30):
        plan = practice_run(C.GENERATOR_TEST_FAMILY_START + 1000 + i, 1)
        assert verify_run_plan(plan, rp.tuning_family) == []
        cascade_entries = [e for e in plan.log if e[0] == "cascade"]
        assert len(cascade_entries) == plan.cascades
        assert plan.h1_redraws == plan.cascades // C.H1_REDRAW_EVERY
        assert sum(1 for e in plan.log if e[0] == "h1 redrawn") == plan.h1_redraws
        # Try accounting: P's far apples and h2 move by one try per cascade that
        # reached them, plus their own logged failures.
        fails = {o.label: sum(1 for e in plan.log if e[0] == "redraw" and e[1] == o.label) for o in plan.all_objects()}
        h1_fails_free = [plan.h1] + plan.warmup_models + plan.warmup_items + [plan.a[k] for k in (2, 3, 4)]
        assert all(o.try_number == 1 + plan.h1_redraws + fails[o.label] for o in h1_fails_free)
        assert all(o.try_number <= 1 + plan.cascades + fails[o.label] for o in plan.P + [plan.h2] + plan.Q
                   if o.try_number)
        assert plan.h1.try_number == 1 + plan.h1_redraws
        # Each cascade redraws everything from P's look-alikes on h1 onward once;
        # each 10th also redraws h1 and everything after it (warm-up, teaching).
        assert all(o.try_number == 1 + plan.cascades for o in plan.P if o.label.startswith("P-look-h1"))
        assert all(plan.a[k].try_number == 1 + plan.h1_redraws for k in (2, 3, 4))
        assert all(o.try_number == 1 + plan.h1_redraws for o in plan.warmup_items)
        # h1 is redrawn right after the 10th, 20th, ... cascade and after no other (section 2)
        for j, e in enumerate(plan.log):
            if e[0] == "cascade":
                follows = j + 1 < len(plan.log) and plan.log[j + 1][0] == "h1 redrawn"
                assert follows == (e[3] % C.H1_REDRAW_EVERY == 0), (plan.family_number, e)
            if e[0] == "h1 redrawn":
                assert j > 0 and plan.log[j - 1][0] == "cascade"
        # temperament, trait order and warm-up order are drawn once, before any cascade (KT-86)
        assert_drawn_once_before_the_loop(plan)
        assert_redraw_counts(plan)
        assert_warmup_slots_are_the_run_keys_draws(plan)
        seen_h1_redraw |= plan.h1_redraws > 0
    assert seen_h1_redraw


def assert_drawn_once_before_the_loop(plan):
    world = keys.stream_key(keys.run_key(plan.family.key, plan.run_number), keys.STREAM_WORLD)
    d = Draws(world, rp.PLACE_TEMPERAMENT, 1)
    assert plan.reserve_milli == C.R_MILLI_LO + d.index(C.R_MILLI_HI - C.R_MILLI_LO + 1)
    assert plan.boldness == d.between(C.BOLDNESS_LO, C.BOLDNESS_HI)
    assert plan.trait_order == tuple(Draws(world, rp.PLACE_TRAIT_ORDER, 1).shuffled(range(traits.N_TRAITS)))
    labels = [f"warmup-{j}-{i:02d}" for j in range(1, C.N_WARMUP_KINDS + 1) for i in range(1, C.N_WARMUP_PER_KIND + 1)]
    assert plan.warmup_order == tuple(Draws(world, rp.PLACE_WARMUP_ORDER, 1).shuffled(labels))


FAR_LABELS = {f"P-far-{i}" for i in range(1, 9)} | {"h2"}
NEUTRAL_ITEM_KIND = {"P-neutral-1": 1, "P-neutral-2": 2, "Q-neutral-1": 3, "Q-neutral-2": 4}


def assert_redraw_counts(plan):
    """Walk the log (section 2, KT-32, KT-85).

    A cascade follows exactly 10,000 failed draws of the far apple or h2 it
    names, and no far apple or h2 fails that often without one. A neutral
    kind is replaced after exactly 1,000 failed draws of its item. Both counts
    start again at each cascade, and a neutral's count at each replacement.
    """
    far, neutral = {}, {}
    for e in plan.log:
        if e[0] == "redraw" and e[1] in FAR_LABELS:
            far[e[1]] = far.get(e[1], 0) + 1
            assert far[e[1]] <= C.FAR_MAX_DRAWS, (plan.family_number, e)
        elif e[0] == "redraw" and e[1] in NEUTRAL_ITEM_KIND:
            k = NEUTRAL_ITEM_KIND[e[1]]
            neutral[k] = neutral.get(k, 0) + 1
            assert neutral[k] <= C.KIND_MAX_DRAWS, (plan.family_number, e)
        elif e[0] == "cascade":
            assert far.get(e[1], 0) == C.FAR_MAX_DRAWS, (plan.family_number, e)
            far, neutral = {}, {}
        elif e[0] == "neutral kind replaced":
            k = int(e[1].split("-")[1])
            assert neutral.get(k, 0) == C.KIND_MAX_DRAWS, (plan.family_number, e)
            neutral[k] = 0
    assert all(n < C.FAR_MAX_DRAWS for n in far.values())


def assert_warmup_slots_are_the_run_keys_draws(plan):
    """Each warm-up slot is the run key's draw at its last try, in KT-84's order:
    family among those left, kind, scene, host. Its try counts h1 redraws and
    its own logged swaps. The models move with h1 (KT-86)."""
    assert all(m.try_number == 1 + plan.h1_redraws for m in plan.warmup_models), plan.family_number
    world = keys.stream_key(keys.run_key(plan.family.key, plan.run_number), keys.STREAM_WORLD)
    gap = C.WARMUP_CONTEXT_MIN_NW * C.NOISE_WIDTH

    def away(u, ref):          # uniform over [0, ref - gap] and [ref + gap, 1], written out from KT-06
        left, right = max(0.0, ref - gap), max(0.0, 1.0 - (ref + gap))
        x = u * (left + right)
        return x if x < left else min(ref + gap + (x - left), 1.0)

    used = []
    for s in plan.warmup_slots:
        swaps = sum(1 for e in plan.log if e[0] == "warm-up kind swapped" and e[1] == f"warmup-slot-{s.slot}")
        assert s.place == rp.place_warmup_slot(s.slot) and s.try_number == 1 + plan.h1_redraws + swaps
        d = Draws(world, s.place, s.try_number)
        left = [f for f in range(1, C.N_TUNING_FAMILIES + 1)
                if f not in used and not (plan.h_is_tuning_family and f == plan.family_number)]
        source = left[d.index(len(left))]
        fam = rp.tuning_family(source)
        if s.nature == NOURISH:
            kind = fam.H
        elif s.nature == POISON:
            kind = fam.lookalike_kinds[1 + d.index(C.N_LOOKALIKE_KINDS)]
        else:
            kind = fam.neutral_kinds[1 + d.index(C.N_NEUTRAL_KINDS)]
        scene = away(d.uniform(), plan.h1.values[traits.SCENE])
        host = away(d.uniform(), plan.h1.values[traits.HOST])
        assert (s.source_family, s.kind.record(), s.scene, s.host) == (source, kind.record(), scene, host), \
            (plan.family_number, s.slot)
        used.append(source)


def test_warmup_slots_on_tuning_runs():
    """Tuning runs exclude H's own family and swap kinds often (KT-39)."""
    swaps = 0
    for n in range(1, C.N_TUNING_FAMILIES + 1):
        plan = rp.generate_run("tuning", KEY, n, 1 + n % C.RUNS_PER_FAMILY)
        assert_warmup_slots_are_the_run_keys_draws(plan)
        assert_redraw_counts(plan)
        swaps += sum(1 for e in plan.log if e[0] == "warm-up kind swapped")
    assert swaps > 0


def test_neutral_kind_replacements_chain_through_cascades(monkeypatch):
    """Each replacement is the next kind draw, and a replacement outlives a cascade (section 2, KT-85)."""
    monkeypatch.setattr(C, "FAR_MAX_DRAWS", 20)
    monkeypatch.setattr(C, "KIND_MAX_DRAWS", 3)
    both = 0
    for i in range(60):
        plan = practice_run(C.GENERATOR_TEST_FAMILY_START + 1000 + i, 1)
        assert verify_run_plan(plan, rp.tuning_family) == []
        for k, kind in plan.neutral_kinds.items():
            tries = [e[3] for e in plan.log if e[0] == "neutral kind replaced" and e[1] == f"neutral-{k}"]
            assert tries == list(range(2, kind.try_number + 1)), (plan.family_number, k, tries)
        assert_redraw_counts(plan)
        assert_warmup_slots_are_the_run_keys_draws(plan)
        both += plan.cascades > 0 and any(k.try_number > 1 for k in plan.neutral_kinds.values())
    assert both > 0


def test_neutral_kind_replacement(monkeypatch):
    monkeypatch.setattr(C, "KIND_MAX_DRAWS", 1)
    replaced = 0
    for i in range(20):
        n = C.GENERATOR_TEST_FAMILY_START + 2000 + i
        plan = practice_run(n, 1)
        assert verify_run_plan(plan, rp.tuning_family) == []
        for k, kind in plan.neutral_kinds.items():
            if kind.try_number > 1:
                replaced += 1
                assert kind.record() == neutral_kind("practice", KEY, n, k, kind.try_number).record()
                assert any(e[0] == "neutral kind replaced" and e[1] == f"neutral-{k}" for e in plan.log)
        # the family itself never changes
        assert all(k.try_number == 1 for k in plan.family.neutral_kinds.values())
    assert replaced > 0


def test_warmup_kind_swaps_are_logged_and_pass():
    swaps = 0
    for n in range(1, C.N_TUNING_FAMILIES + 1):
        plan = rp.generate_run("tuning", KEY, n, 1)
        for s in plan.warmup_slots:
            entries = [e for e in plan.log if e[0] == "warm-up kind swapped" and e[1] == f"warmup-slot-{s.slot}"]
            assert s.try_number == 1 + len(entries)
            swaps += len(entries)
    assert swaps > 0


def test_replica_keys():
    assert rp.replica_p(1, 1) == 1001 and rp.replica_p(8, 20) == 8020
    assert rp.replica_q(1) == 9001
    keys_used = {rp.replica_p(c, p) for c in rp.CHECKPOINTS for p in range(1, 21)} | \
                {rp.replica_q(p) for p in range(1, 21)} | {rp.REPLICA_MAIN}
    assert len(keys_used) == 5 * 20 + 20 + 1
    with pytest.raises(ValueError):
        rp.replica_p(3, 1)


def test_noise_is_keyed_by_the_run_key():
    n = C.GENERATOR_TEST_FAMILY_START + 33
    a, b = practice_run(n, 1), practice_run(n, 2)
    rk = keys.run_key(a.family.key, 1)
    assert a.noise_key == keys.stream_key(rk, keys.STREAM_SENSOR_NOISE)
    assert a.noise_key != keys.stream_key(rk, keys.STREAM_WORLD)
    assert a.noise_key != b.noise_key
    from world import readings
    assert readings.read_visible(a, a.P[0], 0) != readings.read_visible(b, a.P[0], 0)
