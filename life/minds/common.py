"""Small pieces every creature's mind may use: steering and a random walk.

Steering towards a point in a straight line is conventional. There is no
route-finder anywhere in life/: no A*, Dijkstra, flow field or navigation
mesh, and no map a creature did not build itself (BRIEF, "No route-finder").
"""

import math

from life import config as C

EAT_REACH = C.EAT_RANGE - 0.15       # how close a mind walks before it tries to eat (a little inside the range)


def angle_to(p, x, z):
    """Turn (degrees, + is towards +z from +x) needed to face (x, z) from the percept's position and heading."""
    want = math.atan2(z - p["z"], x - p["x"])
    d = (want - p["heading"] + math.pi) % (2 * math.pi) - math.pi
    return math.degrees(d)


def steer(p, x, z):
    """One tick of walking straight at (x, z): turn as far as allowed, then step."""
    a = angle_to(p, x, z)
    if abs(a) > 100:                     # facing away: turn on the spot first
        return {"do": "turn", "angle": max(-C.TURN_MAX_DEG, min(C.TURN_MAX_DEG, a))}
    return {"do": "move", "angle": max(-C.TURN_MAX_DEG, min(C.TURN_MAX_DEG, a))}


def dist(p, x, z):
    return math.hypot(x - p["x"], z - p["z"])


class RandomWalk:
    """Keep going mostly straight; now and then, and after every bump, pick a new direction at random."""

    def __init__(self, rng, turn_chance=0.12):
        self.rng = rng
        self.turn_chance = turn_chance
        self.turn_left = 0.0

    def act(self, p):
        if p.get("touch"):
            self.turn_left = float(self.rng.uniform(60, 180)) * (1 if self.rng.random() < 0.5 else -1)
        elif self.rng.random() < self.turn_chance:
            self.turn_left = float(self.rng.uniform(-60, 60))
        if abs(self.turn_left) > C.TURN_MAX_DEG:
            a = math.copysign(C.TURN_MAX_DEG, self.turn_left)
            self.turn_left -= a
            return {"do": "turn", "angle": a}
        a, self.turn_left = self.turn_left, 0.0
        return {"do": "move", "angle": a}
