"""One run's plan: every object of a run, drawn by the run key (sections 2 and 5, KT-84 to KT-87).

A run plan holds the true values of every object a mind will meet in one run,
in the frozen draw order, with every redraw logged (section 2, Certificates).
It is world-side only. A mind sees an object only through readings.py.

Places on the run's world stream (each place has its own try count, KT-32, KT-81):

    1                temperament: R, then b
    2                the trait order (KT-41)
    3                the warm-up order (KT-41)
    10               h1
    21-24            warm-up slots 1 to 4: 1 nourishing, 1 poison, 2 nothing
    100-139          warm-up items: 100 + 10 (slot - 1) + (item - 1)
    200-209          the fresh apples that warm-up poison items 1 to 10 copy
    302-304          a2 to a4
    312-318          the teaching look-alikes t2, t4, t6, t8 (310 + taste number)
    401-404          P's look-alikes modelled on h1
    411-418          P's far apples 1 to 8
    421-424          P's look-alikes modelled on far apples 1 to 4
    431-432          P's neutrals
    441-442          P's copies of h1 (no draws; the place addresses their noise)
    500              h2 (SWEET-CONTROL shares this place, KT-33)
    601-604          Q's apples near h1
    611-614          Q's apples near h2
    621-624          Q's look-alikes modelled on h1
    631-634          Q's look-alikes modelled on h2
    641-642          Q's neutrals
    651-652          Q's copies of h1

A warm-up slot's try draws, in order: its tuning family, its kind within that
family (none for the nourishing slot), its scene, its host.
"""

from dataclasses import dataclass, field

from . import constants as C
from . import keys, traits
from .certificates import far_apple_failure, h2_failure, neutral_failure, warmup_kind_failure
from .kinds import NOTHING, NOURISH, POISON, Family, Kind, generate_family, neutral_kind
from .objects import (APPLE, COPY, FAR_APPLE, LOOKALIKE, MODEL, NEUTRAL, WARMUP, WorldObject,
                      draw_lookalike, draw_member, surface_distance)
from .streams import Draws

PLACE_TEMPERAMENT = 1        # run stream places (KT-81)
PLACE_TRAIT_ORDER = 2        # (KT-81)
PLACE_WARMUP_ORDER = 3       # (KT-81)
PLACE_H1 = 10                # (KT-81)
PLACE_H2 = 500               # SWEET-CONTROL shares it (KT-33, KT-81)


def place_warmup_slot(slot):
    return 20 + slot                        # (KT-81)


def place_warmup_item(slot, item):
    return 100 + 10 * (slot - 1) + (item - 1)   # (KT-81)


def place_warmup_model(item):
    return 200 + (item - 1)                 # (KT-81)


# P's and Q's look-alikes use the pairs in this order (KT-40).
H1_HALF_PAIRS = ((1, 2), (3, 4), (1, 3), (2, 4))     # M1 then M2 (KT-40)
FAR_HALF_PAIRS = ((1, 2), (3, 4), (1, 4), (2, 3))    # M1 then M3 (KT-40)

WARMUP_NATURES = (NOURISH, POISON, NOTHING, NOTHING)

# The replica keys of the noise (W52, KT-33, KT-87). The main line is 0. Each P copy's
# key is set by its checkpoint and probe; each Q probe has one key across its
# S8, SOUR and SWEET-CONTROL copies. The two sour-apple branches share one key
# (KT-16): the main line's, since h2's place is used nowhere else.
REPLICA_MAIN = 0             # (KT-87)
CHECKPOINTS = (1, 2, 4, 6, 8)    # snapshots S1, S2, S4, S6, S8 (section 5, KT-87)
REPLICA_SOUR_BRANCHES = REPLICA_MAIN    # (KT-16, KT-87)


def replica_p(checkpoint, probe):
    if checkpoint not in CHECKPOINTS or not 1 <= probe <= 20:
        raise ValueError("P runs after tastes 1, 2, 4, 6 and 8, on probes 1 to 20")
    return 1000 * checkpoint + probe        # (KT-87)


def replica_q(probe):
    if not 1 <= probe <= 20:
        raise ValueError("Q has probes 1 to 20")
    return 9000 + probe                     # (KT-87)


class _Cascade(Exception):
    """A far apple or h2 gave no passing draw in 10,000 draws (KT-03)."""


class GeneratorStuck(RuntimeError):
    """A run drew far more often than the frozen rules ever expect. Never caught."""


# Safety stops (KT-90), not redraw rules: they end a run that would otherwise
# loop for ever, and should never fire. Each is far beyond what the redraw
# rules need: 100 redraws of h1, or 1,000 replacements of one neutral kind.
_STUCK_CASCADES = 1_000                 # (KT-90)
_STUCK_KIND_REPLACEMENTS = 1_000        # (KT-90)


@dataclass(frozen=True)
class WarmupSlot:
    slot: int
    nature: str
    source_family: int        # a tuning family, never H's own (KT-06, KT-39)
    kind: Kind
    model_kind: Kind | None   # the poison slot's family H, which its items' models come from
    scene: float
    host: float
    place: int
    try_number: int


@dataclass
class RunPlan:
    set_name: str
    family_number: int
    run_number: int
    family: Family
    h_is_tuning_family: bool
    reserve_milli: int
    boldness: float
    trait_order: tuple
    h1: WorldObject
    warmup_slots: list
    warmup_models: list
    warmup_items: list        # in slot order; warmup_sequence() gives the shuffled order
    warmup_order: tuple       # labels, in the order the minds taste them
    a: dict                   # 2, 3, 4 -> a2, a3, a4
    teaching: list            # t1 to t8
    P: list                   # probe order: far 1-8, look-alikes on h1, on far apples, neutrals, copies
    h2: WorldObject
    Q: list                   # probe order: near h1, near h2, look-alikes on h1, on h2, neutrals, copies
    neutral_kinds: dict       # 1..4 -> the neutral kind in use this run (KT-03 replacement)
    noise_key: int = field(repr=False)
    log: list = field(repr=False)   # every redraw, cascade, swap and replacement
    cascades: int = 0
    h1_redraws: int = 0

    @property
    def reserve(self) -> float:
        return self.reserve_milli / 1000

    def warmup_sequence(self) -> list:
        by_label = {o.label: o for o in self.warmup_items}
        return [by_label[label] for label in self.warmup_order]

    def all_objects(self) -> list:
        return ([self.h1] + self.warmup_models + self.warmup_items
                + [self.a[k] for k in (2, 3, 4)] + [o for o in self.teaching if o.role == LOOKALIKE]
                + self.P + [self.h2] + self.Q)

    def redraw_count(self) -> int:
        return sum(1 for e in self.log if e[0] == "redraw")


def tuning_family(n: int) -> Family:
    return generate_family("tuning", keys.tuning_set_key(), n)


def _away_from(d: Draws, ref: float) -> float:
    """Uniform over the values at least 40 noise widths from ref (KT-06)."""
    gap = C.WARMUP_CONTEXT_MIN_NW * C.NOISE_WIDTH
    left = max(0.0, ref - gap)
    right = max(0.0, 1.0 - (ref + gap))
    x = d.uniform() * (left + right)
    return x if x < left else min(ref + gap + (x - left), 1.0)


class _Builder:
    def __init__(self, set_name, set_key, family_number, run_number, family, tuning_family, h_is_tuning):
        self.set_name = set_name
        self.set_key = set_key
        self.family_number = family_number
        self.family = family
        self.H = family.H
        self.tuning_family = tuning_family
        self.h_is_tuning = h_is_tuning
        rk = keys.run_key(family.key, run_number)
        self.world = keys.stream_key(rk, keys.STREAM_WORLD)
        self.noise_key = keys.stream_key(rk, keys.STREAM_SENSOR_NOISE)
        self.tries = {}
        self.log = []
        self.neutral_kinds = dict(family.neutral_kinds)
        self.neutral_kind_try = {k: 1 for k in self.neutral_kinds}

    def draws(self, place) -> Draws:
        n = self.tries.get(place, 0) + 1
        self.tries[place] = n
        return Draws(self.world, place, n)

    def failed(self, label, place, why):
        self.log.append(("redraw", label, place, self.tries[place], why))

    # -- objects that cannot fail ------------------------------------------

    def member(self, label, place, role, kind, context=None, limits=None, near=None):
        d = self.draws(place)
        values, offset = draw_member(d, kind, context, limits, near)
        return WorldObject(label, place, d.try_number, role, kind, values, offset)

    def lookalike(self, label, place, kind, model, context, role=LOOKALIKE):
        d = self.draws(place)
        values, offset = draw_lookalike(d, kind, model.values, model.hue_offset, context)
        return WorldObject(label, place, d.try_number, role, kind, values, offset, model=model.label)

    # -- objects that can fail ---------------------------------------------

    def far_apple(self, label, place, h1, look_h1, limits=None, earlier=None):
        fails = 0
        while True:
            d = self.draws(place)
            values, offset = draw_member(d, self.H, (h1.values[traits.SCENE], h1.values[traits.HOST]), limits)
            if earlier is None:
                why = far_apple_failure(values, h1.values, look_h1)
            else:
                why = h2_failure(values, h1.values, look_h1, earlier)
            if not why:
                return WorldObject(label, place, d.try_number, FAR_APPLE, self.H, values, offset)
            self.failed(label, place, why)
            fails += 1
            if fails == C.FAR_MAX_DRAWS:
                raise _Cascade(label)

    def neutral(self, label, place, k, h1, mean_far):
        ctx = (h1.values[traits.SCENE], h1.values[traits.HOST])
        fails = 0
        while True:
            d = self.draws(place)
            kind = self.neutral_kinds[k]
            values, offset = draw_member(d, kind, ctx)
            why = neutral_failure(values, self.H, h1.values, mean_far)
            if not why:
                return WorldObject(label, place, d.try_number, NEUTRAL, kind, values, offset)
            self.failed(label, place, why)
            fails += 1
            if fails == C.KIND_MAX_DRAWS:
                fails = 0
                self.neutral_kind_try[k] += 1
                if self.neutral_kind_try[k] > _STUCK_KIND_REPLACEMENTS:
                    raise GeneratorStuck(f"neutral kind {k} replaced {_STUCK_KIND_REPLACEMENTS} times")
                self.neutral_kinds[k] = neutral_kind(self.set_name, self.set_key, self.family_number, k,
                                                     self.neutral_kind_try[k])
                self.log.append(("neutral kind replaced", f"neutral-{k}", place, self.neutral_kind_try[k],
                                 "no passing object in 1,000 draws"))

    # -- the steps of the draw order -----------------------------------------

    def h1(self):
        limits = {traits.SWEET: (C.H1_SWEET_MIN, 1.0), traits.SOUR: (0.0, C.H1_SOUR_MAX)}
        return self.member("h1", PLACE_H1, APPLE, self.H, limits=limits)

    def warmup(self, h1):
        slots, used = [], set()
        for j, nature in enumerate(WARMUP_NATURES, start=1):
            place = place_warmup_slot(j)
            while True:
                d = self.draws(place)
                allowed = [f for f in range(1, C.N_TUNING_FAMILIES + 1)
                           if f not in used and not (self.h_is_tuning and f == self.family_number)]
                source = allowed[d.index(len(allowed))]
                fam = self.tuning_family(source)
                model_kind = None
                if nature == NOURISH:
                    kind = fam.H
                elif nature == POISON:
                    kind = fam.lookalike_kinds[1 + d.index(C.N_LOOKALIKE_KINDS)]
                    model_kind = fam.H
                else:
                    kind = fam.neutral_kinds[1 + d.index(C.N_NEUTRAL_KINDS)]
                scene = _away_from(d, h1.values[traits.SCENE])
                host = _away_from(d, h1.values[traits.HOST])
                why = warmup_kind_failure(kind, self.H)
                if not why:
                    break
                self.log.append(("warm-up kind swapped", f"warmup-slot-{j}", place, d.try_number,
                                 f"tuning family {source} {kind.name}: {why}"))
            used.add(source)
            slots.append(WarmupSlot(j, nature, source, kind, model_kind, scene, host, place, d.try_number))

        models, items = [], []
        for s in slots:
            ctx = (s.scene, s.host)
            for i in range(1, C.N_WARMUP_PER_KIND + 1):
                label, place = f"warmup-{s.slot}-{i:02d}", place_warmup_item(s.slot, i)
                if s.nature == POISON:
                    m = self.member(f"warmup-model-{i:02d}", place_warmup_model(i), MODEL, s.model_kind)
                    models.append(m)
                    items.append(self.lookalike(label, place, s.kind, m, ctx, role=WARMUP))
                else:
                    items.append(self.member(label, place, WARMUP, s.kind, context=ctx))
        return slots, models, items

    def teaching(self, h1):
        ctx = (h1.values[traits.SCENE], h1.values[traits.HOST])
        a = {k: self.member(f"a{k}", 300 + k, APPLE, self.H, context=ctx,
                            limits={traits.SOUR: (0.0, C.A_SOUR_MAX)}) for k in (2, 3, 4)}
        kinds = self.family.lookalike_kinds
        t2 = self.lookalike("t2", 312, kinds[1], h1, ctx)
        t4 = self.lookalike("t4", 314, kinds[2], a[2], ctx)
        t6 = self.lookalike("t6", 316, kinds[1], a[3], ctx)
        t8 = self.lookalike("t8", 318, kinds[2], a[4], ctx)
        return a, [h1, t2, a[2], t4, a[3], t6, a[4], t8]

    def checks(self, h1, a):
        fam = self.family
        ctx = (h1.values[traits.SCENE], h1.values[traits.HOST])

        def kind_for(pair):
            return fam.check_kind_for_pair(fam.label_pair(*pair))

        look_h1 = [self.lookalike(f"P-look-h1-{i}", 400 + i, kind_for(p), h1, ctx)
                   for i, p in enumerate(H1_HALF_PAIRS, start=1)]
        look_h1_values = [o.values for o in look_h1]
        far = [self.far_apple(f"P-far-{i}", 410 + i, h1, look_h1_values) for i in range(1, 9)]
        look_far = [self.lookalike(f"P-look-far-{i}", 420 + i, kind_for(p), far[i - 1], ctx)
                    for i, p in enumerate(FAR_HALF_PAIRS, start=1)]
        mean_far = sum(surface_distance(o.values, h1.values) for o in far) / len(far)
        p_neutrals = [self.neutral(f"P-neutral-{i}", 430 + i, k, h1, mean_far) for i, k in ((1, 1), (2, 2))]
        p_copies = [_copy(f"P-copy-{i}", 440 + i, h1) for i in (1, 2)]
        P = far + look_h1 + look_far + p_neutrals + p_copies

        limits = {traits.SWEET: (0.0, C.H2_SWEET_MAX), traits.SOUR: (C.H2_SOUR_MIN, 1.0)}
        earlier = [h1.values] + [a[k].values for k in (2, 3, 4)]
        h2 = self.far_apple("h2", PLACE_H2, h1, look_h1_values, limits=limits, earlier=earlier)

        near_traits = tuple(t for t in traits.OBSERVABLE
                            if t not in self.H.bands and t not in (traits.SCENE, traits.HOST, traits.EXACT_HUE))
        q_near_h1 = [self.member(f"Q-near-h1-{i}", 600 + i, APPLE, self.H, context=ctx,
                                 near=(near_traits, h1.values)) for i in range(1, 5)]
        q_near_h2 = [self.member(f"Q-near-h2-{i}", 610 + i, APPLE, self.H, context=ctx,
                                 near=(near_traits, h2.values)) for i in range(1, 5)]
        q_look_h1 = [self.lookalike(f"Q-look-h1-{i}", 620 + i, kind_for(p), h1, ctx)
                     for i, p in enumerate(H1_HALF_PAIRS, start=1)]
        q_look_h2 = [self.lookalike(f"Q-look-h2-{i}", 630 + i, kind_for(p), h2, ctx)
                     for i, p in enumerate(FAR_HALF_PAIRS, start=1)]
        q_neutrals = [self.neutral(f"Q-neutral-{i}", 640 + i, k, h1, mean_far) for i, k in ((1, 3), (2, 4))]
        q_copies = [_copy(f"Q-copy-{i}", 650 + i, h1) for i in (1, 2)]
        Q = q_near_h1 + q_near_h2 + q_look_h1 + q_look_h2 + q_neutrals + q_copies
        return P, h2, Q


def _copy(label, place, h1):
    return WorldObject(label, place, 0, COPY, h1.kind, h1.values, h1.hue_offset, model="h1")


def generate_run(set_name: str, set_key: bytes, family_number: int, run_number: int,
                 family: Family | None = None, tuning_family=tuning_family) -> RunPlan:
    """The plan of run run_number of a family (sections 2 and 5)."""
    if family is None:
        family = generate_family(set_name, set_key, family_number)
    h_is_tuning = set_name == "tuning" and 1 <= family_number <= C.N_TUNING_FAMILIES
    b = _Builder(set_name, set_key, family_number, run_number, family, tuning_family, h_is_tuning)

    d = b.draws(PLACE_TEMPERAMENT)
    reserve_milli = C.R_MILLI_LO + d.index(C.R_MILLI_HI - C.R_MILLI_LO + 1)
    boldness = d.between(C.BOLDNESS_LO, C.BOLDNESS_HI)
    trait_order = tuple(b.draws(PLACE_TRAIT_ORDER).shuffled(range(traits.N_TRAITS)))
    warmup_labels = [f"warmup-{j}-{i:02d}" for j in range(1, C.N_WARMUP_KINDS + 1)
                     for i in range(1, C.N_WARMUP_PER_KIND + 1)]
    warmup_order = tuple(b.draws(PLACE_WARMUP_ORDER).shuffled(warmup_labels))

    cascades = h1_redraws = 0
    while True:
        h1 = b.h1()
        slots, models, items = b.warmup(h1)
        a, teaching = b.teaching(h1)
        redraw_h1 = False
        while not redraw_h1:
            try:
                P, h2, Q = b.checks(h1, a)
                break
            except _Cascade as stop:
                cascades += 1
                b.log.append(("cascade", str(stop), 0, cascades, "no passing draw in 10,000 draws"))
                if cascades >= _STUCK_CASCADES:
                    raise GeneratorStuck(f"{cascades} cascades in one run") from None
                redraw_h1 = cascades % C.H1_REDRAW_EVERY == 0
        if not redraw_h1:
            break
        h1_redraws += 1
        b.log.append(("h1 redrawn", "h1", PLACE_H1, b.tries[PLACE_H1] + 1, f"cascade {cascades}"))

    return RunPlan(set_name, family_number, run_number, family, h_is_tuning, reserve_milli, boldness,
                   trait_order, h1, slots, models, items, warmup_order, a, teaching, P, h2, Q,
                   dict(b.neutral_kinds), b.noise_key, b.log, cascades, h1_redraws)
