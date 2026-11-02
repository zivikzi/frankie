"""Fences, walls and a river: the obstacles between a creature and some food.

These are the classic animal problem-solving tests (the detour test), so as
tests they are conventional. The geometry is plain 2D line segments on the
ground (conventional):

- A fence is a ring of straight segments around a rich food patch with one
  segment left open (the gap). It blocks walking but not sight.
- A wall is one straight segment. It blocks walking and sight.
- A river is a wavy band across the whole map. It blocks walking except at
  its one crossing (a ford or a log), and does not block sight.

Every layout is drawn from the world's seed, so no route can be learned once
and replayed.
"""

import math

import numpy as np

from life import config as C


def _seg_dist(px, pz, ax, az, bx, bz):
    """Distance from point p to segment a-b (arrays for a and b allowed)."""
    dx, dz = bx - ax, bz - az
    L2 = dx * dx + dz * dz
    t = np.clip(((px - ax) * dx + (pz - az) * dz) / np.where(L2 == 0, 1, L2), 0.0, 1.0)
    cx, cz = ax + t * dx, az + t * dz
    return np.hypot(px - cx, pz - cz)


def _cross(ax, az, bx, bz, cx, cz):
    return (bx - ax) * (cz - az) - (bz - az) * (cx - ax)


def segments_cross(p, q, a, b):
    """True where segment p-q crosses segment(s) a-b (a, b arrays of shape (n, 2))."""
    d1 = _cross(a[:, 0], a[:, 1], b[:, 0], b[:, 1], p[0], p[1])
    d2 = _cross(a[:, 0], a[:, 1], b[:, 0], b[:, 1], q[0], q[1])
    d3 = _cross(p[0], p[1], q[0], q[1], a[:, 0], a[:, 1])
    d4 = _cross(p[0], p[1], q[0], q[1], b[:, 0], b[:, 1])
    return (d1 * d2 < 0) & (d3 * d4 < 0)


class Fence:
    kind = "fence"

    def __init__(self, ident, cx, cz, radius, gap_index, sides=C.FENCE_SIDES):
        self.id = ident
        self.cx, self.cz, self.radius = cx, cz, radius
        self.gap_index = gap_index
        pts = []
        for k in range(sides + 1):
            a = 2 * math.pi * k / sides
            pts.append((cx + radius * math.cos(a), cz + radius * math.sin(a)))
        self.corners = pts
        segs = [(pts[k], pts[k + 1]) for k in range(sides) if k != gap_index]
        self.a = np.array([s[0] for s in segs])
        self.b = np.array([s[1] for s in segs])
        g0, g1 = pts[gap_index], pts[gap_index + 1]
        self.gap = ((g0[0] + g1[0]) / 2, (g0[1] + g1[1]) / 2)

    def inside(self, x, z, margin=0.0):
        return math.hypot(x - self.cx, z - self.cz) < self.radius - margin

    def describe(self):
        return {"type": "fence", "id": self.id, "centre": [self.cx, self.cz], "radius": self.radius,
                "corners": self.corners, "gap_index": self.gap_index, "gap": list(self.gap)}


class Wall:
    kind = "wall"

    def __init__(self, ident, ax, az, bx, bz):
        self.id = ident
        self.a = np.array([[ax, az]])
        self.b = np.array([[bx, bz]])

    def describe(self):
        return {"type": "wall", "id": self.id, "a": self.a[0].tolist(), "b": self.b[0].tolist()}


class River:
    """A band around the curve v = v0 + amp * sin(2 pi u / length + phase).

    For a river running north-south, u is z and v is x; for east-west, u is x
    and v is z. The crossing sits at u = ford_u.
    """

    kind = "river"

    def __init__(self, ident, vertical, v0, amp, length, phase, ford_u, crossing):
        self.id = ident
        self.vertical = vertical
        self.v0, self.amp, self.length, self.phase = v0, amp, length, phase
        self.ford_u = ford_u
        self.crossing = crossing                   # "ford" or "log", for drawing only

    def _uv(self, x, z):
        return (z, x) if self.vertical else (x, z)

    def centre_v(self, u):
        return self.v0 + self.amp * np.sin(2 * np.pi * u / self.length + self.phase)

    def offset(self, x, z):
        """Signed distance across the river (positive on one side), ignoring the curve's slope."""
        u, v = self._uv(x, z)
        return v - self.centre_v(u)

    def side(self, x, z):
        return 1 if self.offset(x, z) > 0 else -1

    def in_water(self, x, z):
        u, _ = self._uv(x, z)
        return abs(self.offset(x, z)) < C.RIVER_HALF_WIDTH and abs(u - self.ford_u) >= C.FORD_HALF_WIDTH

    def at_crossing(self, x, z):
        u, _ = self._uv(x, z)
        return abs(self.offset(x, z)) < C.RIVER_HALF_WIDTH + 0.5 and abs(u - self.ford_u) < C.FORD_HALF_WIDTH

    def point(self, u, dv=0.0):
        v = float(self.centre_v(u)) + dv
        return (v, u) if self.vertical else (u, v)

    def describe(self):
        us = np.arange(0.0, C.WORLD_SIZE + 0.01, 2.0)
        centre = [self.point(float(u)) for u in us]
        return {"type": "river", "id": self.id, "vertical": self.vertical, "centre": centre,
                "half_width": C.RIVER_HALF_WIDTH, "ford": list(self.point(self.ford_u)),
                "ford_half_width": C.FORD_HALF_WIDTH, "crossing": self.crossing}


class Obstacles:
    def __init__(self):
        self.fences = []
        self.walls = []
        self.river = None
        self._rebuild()

    def _rebuild(self):
        segs_a = [f.a for f in self.fences] + [w.a for w in self.walls]
        segs_b = [f.b for f in self.fences] + [w.b for w in self.walls]
        self.block_a = np.concatenate(segs_a) if segs_a else np.zeros((0, 2))
        self.block_b = np.concatenate(segs_b) if segs_b else np.zeros((0, 2))
        wa = [w.a for w in self.walls]
        wb = [w.b for w in self.walls]
        self.wall_a = np.concatenate(wa) if wa else np.zeros((0, 2))
        self.wall_b = np.concatenate(wb) if wb else np.zeros((0, 2))

    def add_fence(self, f):
        self.fences.append(f)
        self._rebuild()

    def add_wall(self, w):
        self.walls.append(w)
        self._rebuild()

    @property
    def any(self):
        return bool(self.fences or self.walls or self.river)

    def blocks_move(self, x0, z0, x1, z1):
        """What, if anything, stops a step from (x0, z0) to (x1, z1): None, 'fence', 'wall' or 'river'."""
        if len(self.block_a):
            a, b, r = self.block_a, self.block_b, C.CREATURE_RADIUS
            near = _seg_dist(x1, z1, a[:, 0], a[:, 1], b[:, 0], b[:, 1]) < r
            # a post (segment end) lying on the step's own path also blocks it
            ends = (_seg_dist(a[:, 0], a[:, 1], x0, z0, x1, z1) < r) | (_seg_dist(b[:, 0], b[:, 1], x0, z0, x1, z1) < r)
            crossed = segments_cross((x0, z0), (x1, z1), a, b)
            hit = near | ends | crossed
            if hit.any():
                k = int(np.argmax(hit))
                n_fence = sum(len(f.a) for f in self.fences)
                return "fence" if k < n_fence else "wall"
        if self.river is not None and self.river.in_water(x1, z1):
            return "river"
        return None

    def blocks_sight(self, x0, z0, x1, z1):
        """Only walls block sight; fences are see-through and a river is flat."""
        if not len(self.wall_a):
            return False
        return bool(segments_cross((x0, z0), (x1, z1), self.wall_a, self.wall_b).any())

    def free_spot(self, x, z, clearance=1.0):
        """True if a creature or object may stand at (x, z)."""
        if not (1.0 <= x <= C.WORLD_SIZE - 1.0 and 1.0 <= z <= C.WORLD_SIZE - 1.0):
            return False
        if len(self.block_a):
            d = _seg_dist(x, z, self.block_a[:, 0], self.block_a[:, 1], self.block_b[:, 0], self.block_b[:, 1])
            if d.min() < clearance:
                return False
        if self.river is not None and abs(self.river.offset(x, z)) < C.RIVER_HALF_WIDTH + clearance:
            return False
        return True

    def behind(self, x, z):
        """Which obstacle, if any, a point sits behind: ('fence', id) inside a fence, else None.

        River sides are handled by the caller, since 'behind a river' depends
        on where the creature is.
        """
        for f in self.fences:
            if f.inside(x, z):
                return ("fence", f.id)
        return None

    def describe(self):
        out = [f.describe() for f in self.fences] + [w.describe() for w in self.walls]
        if self.river is not None:
            out.append(self.river.describe())
        return out


def make_obstacles(rng, terrain):
    """A random layout. About a third of worlds get none, so a batch can compare."""
    obs = Obstacles()
    if rng.random() >= C.OBSTACLE_WORLD_SHARE:
        return obs
    want_river = rng.random() < 0.5
    n_fences = int(rng.integers(1, 3))
    n_walls = int(rng.integers(0, 3))
    if want_river:
        vertical = bool(rng.random() < 0.5)
        v0 = float(rng.uniform(0.35, 0.65) * C.WORLD_SIZE)
        amp = float(rng.uniform(3.0, 9.0))
        length = float(rng.uniform(0.7, 1.4) * C.WORLD_SIZE)
        phase = float(rng.uniform(0, 2 * np.pi))
        ford_u = float(rng.uniform(0.15, 0.85) * C.WORLD_SIZE)
        obs.river = River(0, vertical, v0, amp, length, phase, ford_u, "ford" if rng.random() < 0.5 else "log")
    ident = 1
    tries = 0
    while len(obs.fences) < n_fences and tries < 200:
        tries += 1
        cx, cz = rng.uniform(C.FENCE_RADIUS + 4, C.WORLD_SIZE - C.FENCE_RADIUS - 4, size=2)
        if obs.river is not None and abs(obs.river.offset(cx, cz)) < C.FENCE_RADIUS + C.RIVER_HALF_WIDTH + 3:
            continue
        if any(math.hypot(cx - f.cx, cz - f.cz) < 2 * C.FENCE_RADIUS + 6 for f in obs.fences):
            continue
        obs.add_fence(Fence(ident, float(cx), float(cz), C.FENCE_RADIUS, int(rng.integers(0, C.FENCE_SIDES))))
        ident += 1
    tries = 0
    while len(obs.walls) < n_walls and tries < 200:
        tries += 1
        ax, az = rng.uniform(8, C.WORLD_SIZE - 8, size=2)
        ang = rng.uniform(0, np.pi)
        L = rng.uniform(C.WALL_LENGTH_LO, C.WALL_LENGTH_HI)
        bx, bz = ax + L * math.cos(ang), az + L * math.sin(ang)
        if not (4 < bx < C.WORLD_SIZE - 4 and 4 < bz < C.WORLD_SIZE - 4):
            continue
        mid = ((ax + bx) / 2, (az + bz) / 2)
        if any(math.hypot(mid[0] - f.cx, mid[1] - f.cz) < C.FENCE_RADIUS + L / 2 + 3 for f in obs.fences):
            continue
        if obs.river is not None and (abs(obs.river.offset(ax, az)) < C.RIVER_HALF_WIDTH + 3
                                      or abs(obs.river.offset(bx, bz)) < C.RIVER_HALF_WIDTH + 3
                                      or obs.river.side(ax, az) != obs.river.side(bx, bz)):
            continue
        obs.add_wall(Wall(ident, float(ax), float(az), float(bx), float(bz)))
        ident += 1
    return obs
