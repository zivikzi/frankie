"""A creature's body: where it stands, its energy, and its senses.

The body is the only door between the world and a mind. Every sense returns
plain numbers (no kind, no nature, no label), and taste comes only from
eating (bench rule FORBIDDEN 29). The senses:

- The wide blurry view: a cone in front of the eyes, VIEW_RANGE metres deep
  and VIEW_HALF_ANGLE_DEG either side, blocked by hills and walls (not by
  fences). For each object in it: its distance, its bearing, and readings of
  its context and object-layer traits (scene, host, coarse hue, size,
  roundness, lobes), with noise that grows with distance. (Aitzaz's "wide
  blurry view"; the geometry is conventional.)
- The sharp look: one object within SHARP_RANGE, all 18 visible traits at the
  bench's 1-noise-width clarity, for LOOK_COST energy. (Aitzaz's "sharp view
  that costs energy to point".)
- Touch: whether the last step bumped into something solid or into water.
- Taste: the 4 taste traits of an object, only when it is eaten, with the
  energy change that eating caused.
- The body also knows its own position and heading (path integration;
  conventional) and its energy.
"""

import math

import numpy as np

from life import config as C

N_BLURRY = 6        # context (2) + object (4) traits
N_VISIBLE = 18      # context, object, parts and details
TASTE_FROM = 18


class Body:
    def __init__(self, ident, x, z, heading, rng):
        self.id = ident
        self.x, self.z = float(x), float(z)
        self.heading = float(heading)       # radians; 0 points along +x, pi/2 along +z
        self.energy = C.ENERGY_START
        self.alive = True
        self.age = 0
        self.died_at = None
        self.rng = rng                      # sensor noise only
        self.trail = [(round(self.x, 2), round(self.z, 2))]
        self.walked = 0.0
        self.pending = {}                   # results of the last action, delivered with the next percept
        self.last_action = {"do": "rest"}
        self.seen_ids = []                  # world-side copy of what the view held, for measures only

    def spend(self, amount):
        self.energy -= amount
        if self.energy <= 0 and self.alive:
            self.energy = 0.0
            self.alive = False

    def gain(self, amount):
        self.energy = min(C.ENERGY_MAX, self.energy + amount)
        if self.energy <= 0 and self.alive:
            self.energy = 0.0
            self.alive = False


def _noisy(rng, values, sd):
    v = np.asarray(values, dtype=float) + rng.normal(0.0, sd, size=len(values))
    return np.clip(v, 0.0, 1.0)


def blurry_view(body, world):
    """Everything in the view cone, as plain numbers."""
    out = []
    ids = []
    eye_y = world.terrain.height_at(body.x, body.z) + C.EYE_HEIGHT
    half = math.radians(C.VIEW_HALF_ANGLE_DEG)
    for obj in world.ecology.alive():
        dx, dz = obj.x - body.x, obj.z - body.z
        d = math.hypot(dx, dz)
        if d > C.VIEW_RANGE or d < 1e-6:
            continue
        bearing = (math.atan2(dz, dx) - body.heading + math.pi) % (2 * math.pi) - math.pi
        if abs(bearing) > half:
            continue
        if world.obstacles.blocks_sight(body.x, body.z, obj.x, obj.z):
            continue
        if not world.terrain.line_of_sight(body.x, body.z, eye_y, obj.x, obj.z, obj.y + 0.25):
            continue
        sd = (C.BLUR_NOISE_NW + C.BLUR_NOISE_PER_M_NW * d) * C.NOISE_WIDTH
        traits = _noisy(body.rng, obj.values[:N_BLURRY], sd)
        out.append({"ref": obj.ident, "dist": round(d, 3), "bearing": round(bearing, 4),
                    "x": round(obj.x, 3), "z": round(obj.z, 3), "traits": [float(t) for t in traits]})
        ids.append(obj.ident)
    out.sort(key=lambda s: s["dist"])
    body.seen_ids = ids
    return out


def sharp_look(body, world, ref):
    obj = world.ecology.objects.get(ref)
    if obj is None or not obj.alive:
        return None
    if math.hypot(obj.x - body.x, obj.z - body.z) > C.SHARP_RANGE:
        return None
    if world.obstacles.blocks_sight(body.x, body.z, obj.x, obj.z):
        return None
    traits = _noisy(body.rng, obj.values[:N_VISIBLE], C.SHARP_NOISE_NW * C.NOISE_WIDTH)
    return {"ref": ref, "traits": [float(t) for t in traits]}


def taste(body, obj):
    t = _noisy(body.rng, obj.values[TASTE_FROM:], C.TASTE_NOISE_NW * C.NOISE_WIDTH)
    return [float(v) for v in t]


def percept(body, world, tick):
    """What the mind is told this tick: plain numbers only."""
    p = {"tick": tick, "energy": round(body.energy, 4), "x": round(body.x, 3), "z": round(body.z, 3),
         "heading": round(body.heading, 5), "seen": blurry_view(body, world),
         "touch": body.pending.get("touch"), "sharp": body.pending.get("sharp"),
         "ate": body.pending.get("ate"), "failed": body.pending.get("failed")}
    body.pending = {}
    return p
