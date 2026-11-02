"""What grows where: kinds, their favourite regions, and the objects drawn from them.

World-side only. No creature's mind ever sees anything in this module: a
mind gets readings of an object's 22 numbers through the body's senses, and
nothing else (see life/body.py).

Kinds come from the bench's own generator (src/world, read-only), keyed by
the world's random seed instead of a tuning or kill-run key:

- apple A is family 1's H; its poison look-alikes are family 1's look-alike
  kinds 1 and 3 (2 of 4 core traits moved, everything else the same);
- apple B is family 2's H, with family 2's look-alike kind 1;
- neutrals are neutral kind 1 of families 1, 2 and 3 ("nothing" to eat);
- the context fruit is family 3's H. It nourishes in one region and poisons
  in another: the same-looking object, and only its context tells them apart
  (untested; Aitzaz's outside-in idea).

Objects are drawn with the bench's draw_member, so every object is the same
22-number object the bench uses, with its scene and host set by where it
grows: the scene is the region, the host what it sits on.
"""

import hashlib
from dataclasses import dataclass, field

import numpy as np

from world import keys
from world.kinds import NOURISH, NOTHING, POISON, generate_family
from world.objects import draw_member
from world.streams import Draws

from life import config as C

SET_NAME = "life"


@dataclass
class LifeKind:
    """A kind as the world knows it. Never shown to a mind."""

    ident: int
    label: str                      # "apple A", "look-alike A1", ...
    role: str                       # apple, lookalike, neutral, context
    base: object                    # the bench Kind record (src/world)
    regions: dict                   # region index -> weight of its patches there
    natures: dict = field(default_factory=dict)   # region index -> nature; empty means base.nature everywhere

    def nature_in(self, region):
        return self.natures.get(region, self.base.nature)

    def describe(self, region_names):
        return {"id": self.ident, "label": self.label, "role": self.role, "nature": self.base.nature,
                "natures": {region_names[r]: n for r, n in self.natures.items()},
                "regions": {region_names[r]: round(w, 3) for r, w in self.regions.items()},
                "core": [int(t) for t in self.base.core]}


@dataclass
class LifeObject:
    """One object on the ground. World-side: the mind sees only noisy readings of `values`."""

    ident: int
    kind: LifeKind
    x: float
    z: float
    y: float
    region: int
    values: tuple                   # the 22 true numbers, in the bench's schema order
    nature: str                     # what eating it does here
    patch: int
    alive: bool = True
    regrow_at: int = -1
    behind: tuple = None            # ("fence", id) or ("river", side) for food behind an obstacle

    def public(self):
        """What the page needs to draw it: position and its look (never its kind or nature)."""
        return {"id": self.ident, "x": round(self.x, 3), "z": round(self.z, 3), "y": round(self.y, 3),
                "v": [round(float(v), 4) for v in self.values[:18]], "alive": self.alive}


def set_key(seed: int) -> bytes:
    """The world's key for the bench generator: SHA-256 of 'frankie-life/<seed>' (instant randomness)."""
    return hashlib.sha256(f"frankie-life/{seed}".encode("ascii")).digest()


def region_contexts(rng):
    """A scene value and a host value per region, drawn apart enough to be told apart."""
    while True:
        scenes = rng.uniform(0.05, 0.95, size=len(C.REGIONS))
        s = np.sort(scenes)
        if np.all(np.diff(s) >= C.SCENE_MIN_GAP):
            break
    while True:
        hosts = rng.uniform(0.05, 0.95, size=len(C.REGIONS))
        s = np.sort(hosts)
        if np.all(np.diff(s) >= C.SCENE_MIN_GAP):
            break
    return [(float(a), float(b)) for a, b in zip(scenes, hosts)]


def _weights(primary, secondary, n=len(C.REGIONS)):
    rest = (1.0 - C.PRIMARY_WEIGHT - C.SECONDARY_WEIGHT) / (n - 2)
    w = {r: rest for r in range(n)}
    w[primary] = C.PRIMARY_WEIGHT
    w[secondary] = C.SECONDARY_WEIGHT
    return w


def make_kinds(seed, rng):
    """The kinds of one world, with their favourite regions. Returns (kinds, patch weights)."""
    key = set_key(seed)
    f1 = generate_family(SET_NAME, key, 1)
    f2 = generate_family(SET_NAME, key, 2)
    f3 = generate_family(SET_NAME, key, 3)
    n = len(C.REGIONS)
    kinds = []

    def pick2():
        a, b = rng.choice(n, size=2, replace=False)
        return int(a), int(b)

    pa, sa = pick2()
    pb, sb = pick2()
    kinds.append(LifeKind(0, "apple A", "apple", f1.H, _weights(pa, sa)))
    kinds.append(LifeKind(1, "look-alike A1", "lookalike", f1.lookalike_kinds[1], _weights(sa, pa)))
    kinds.append(LifeKind(2, "look-alike A2", "lookalike", f1.lookalike_kinds[3], _weights(sa, pa)))
    kinds.append(LifeKind(3, "apple B", "apple", f2.H, _weights(pb, sb)))
    kinds.append(LifeKind(4, "look-alike B1", "lookalike", f2.lookalike_kinds[1], _weights(sb, pb)))
    for i, fam in enumerate((f1, f2, f3)):
        p, s = pick2()
        kinds.append(LifeKind(5 + i, f"neutral {i + 1}", "neutral", fam.neutral_kinds[1], _weights(p, s)))
    good, bad = pick2()
    ctx = LifeKind(8, "context fruit", "context", f3.H, {good: 0.5, bad: 0.5}, {good: NOURISH, bad: POISON})
    kinds.append(ctx)
    # How often each kind founds a patch (apples a little commoner than the rest).
    weights = np.array([0.17, 0.08, 0.08, 0.13, 0.09, 0.08, 0.08, 0.08, 0.21])
    return kinds, weights / weights.sum()


class Ecology:
    """Every object in the world, their patches, eating and regrowth."""

    def __init__(self, seed, rng, terrain, obstacles):
        self.seed = seed
        self.rng = rng
        self.terrain = terrain
        self.obstacles = obstacles
        self.contexts = region_contexts(rng)
        self.kinds, self.kind_weights = make_kinds(seed, rng)
        self.stream = keys.stream_key(set_key(seed), keys.STREAM_WORLD)
        self.serial = 1000                      # Draws places for objects start here (families use 1 to 24)
        self.objects = {}
        self.spots = []                         # (x, z, kind, patch, behind) for every growing spot
        self.version = 0
        self._place_patches()

    # -------------------------------------------------------------- placing

    def _random_cell(self, region, clearance=1.5):
        cells = self.terrain.cells_of(region)
        if len(cells) == 0:
            return None
        for _ in range(60):
            x, z = cells[int(self.rng.integers(len(cells)))]
            x += float(self.rng.uniform(-0.5, 0.5))
            z += float(self.rng.uniform(-0.5, 0.5))
            if self.obstacles.free_spot(x, z, clearance) and self.obstacles.behind(x, z) is None:
                return float(x), float(z)
        return None

    def _patch_spots(self, cx, cz, count, kind, patch, behind=None, radius=C.PATCH_RADIUS, inside=None, region=None):
        """Up to `count` growing spots around (cx, cz); with `region`, only spots inside that region."""
        made = 0
        for _ in range(count * 20):
            if made >= count:
                break
            a = self.rng.uniform(0, 2 * np.pi)
            r = radius * np.sqrt(self.rng.uniform(0, 1))
            x, z = cx + r * np.cos(a), cz + r * np.sin(a)
            if inside is not None:
                if not inside.inside(x, z, margin=1.2):
                    continue
                ok = 1.0 <= x <= C.WORLD_SIZE - 1 and 1.0 <= z <= C.WORLD_SIZE - 1
            else:
                ok = self.obstacles.free_spot(x, z, 0.8) and self.obstacles.behind(x, z) is None
            if region is not None and self.terrain.region_at(x, z) != region:
                ok = False
            if not ok or any(abs(x - s[0]) < 0.7 and abs(z - s[1]) < 0.7 for s in self.spots[-12:]):
                continue
            self.spots.append((float(x), float(z), kind, patch, behind))
            made += 1

    def _place_patches(self):
        patch = 0
        for _ in range(C.N_PATCHES):
            kind = self.kinds[int(self.rng.choice(len(self.kinds), p=self.kind_weights))]
            regions = list(kind.regions)
            w = np.array([kind.regions[r] for r in regions])
            region = regions[int(self.rng.choice(len(regions), p=w / w.sum()))]
            cell = self._random_cell(region)
            if cell is None:
                continue
            size = int(self.rng.integers(C.PATCH_SIZE_LO, C.PATCH_SIZE_HI + 1))
            self._patch_spots(cell[0], cell[1], size, kind, patch, region=region)
            patch += 1
        # Rich food behind each fence: apples, the most nourishing thing in the world.
        apples = [k for k in self.kinds if k.role == "apple"]
        for f in self.obstacles.fences:
            kind = apples[int(self.rng.integers(len(apples)))]
            self._patch_spots(f.cx, f.cz, C.RICH_PATCH_SIZE, kind, patch, ("fence", f.id),
                              radius=f.radius - 1.2, inside=f)
            patch += 1
        # Rich food across the river, on a random side.
        river = self.obstacles.river
        if river is not None:
            side = 1 if self.rng.random() < 0.5 else -1
            self.river_food_side = side
            kind = apples[int(self.rng.integers(len(apples)))]
            for _ in range(100):
                u = float(self.rng.uniform(0.15, 0.85) * C.WORLD_SIZE)
                if abs(u - river.ford_u) < 25:          # not right beside the crossing
                    continue
                x, z = river.point(u, side * float(self.rng.uniform(7.0, 12.0)))
                if self.obstacles.free_spot(x, z, 2.0):
                    self._patch_spots(x, z, C.RICH_PATCH_SIZE, kind, patch, ("river", side))
                    patch += 1
                    break
        else:
            self.river_food_side = 0
        for spot in range(len(self.spots)):
            self._grow(spot)

    def _grow(self, spot):
        x, z, kind, patch, behind = self.spots[spot]
        region = self.terrain.region_at(x, z)
        scene, host = self.contexts[region]
        scene += float(self.rng.uniform(-C.CONTEXT_JITTER, C.CONTEXT_JITTER))
        host += float(self.rng.uniform(-C.CONTEXT_JITTER, C.CONTEXT_JITTER))
        self.serial += 1
        values, _ = draw_member(Draws(self.stream, self.serial, 1), kind.base,
                                context=(min(max(scene, 0.0), 1.0), min(max(host, 0.0), 1.0)))
        nature = kind.nature_in(region)
        obj = LifeObject(self.serial, kind, x, z, self.terrain.height_at(x, z), region, values, nature, patch,
                         behind=behind)
        obj.spot = spot
        self.objects[obj.ident] = obj
        self.version += 1
        return obj

    # -------------------------------------------------------------- living

    def eat(self, ident, tick):
        """Remove an object; it regrows at the same spot later as a fresh draw. Returns it."""
        obj = self.objects.get(ident)
        if obj is None or not obj.alive:
            return None
        obj.alive = False
        obj.regrow_at = tick + int(self.rng.integers(C.REGROW_TICKS_LO, C.REGROW_TICKS_HI + 1))
        self.version += 1
        return obj

    def regrow(self, tick):
        grown = []
        for ident in [i for i, o in self.objects.items() if not o.alive and o.regrow_at <= tick]:
            old = self.objects.pop(ident)
            grown.append(self._grow(old.spot))
        return grown

    def alive(self):
        return [o for o in self.objects.values() if o.alive]

    def energy_of(self, nature):
        return {NOURISH: C.NOURISH_GAIN, POISON: C.POISON_LOSS, NOTHING: C.NOTHING_GAIN}[nature]
