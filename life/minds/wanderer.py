"""The wanderer: walks at random and eats anything he bumps into (a baseline: the luck level).

Conventional: a random walk. He has the same body as Frankie, never takes a
sharp look and remembers nothing.
"""

import numpy as np

from life.minds.common import EAT_REACH, RandomWalk


class Wanderer:
    name = "wanderer"
    label = "Wanderer"

    def __init__(self, seed, reserve=None, boldness=None):
        self.rng = np.random.default_rng([seed, 7])
        self.walk = RandomWalk(self.rng)
        self.thought = "Walking wherever my feet go."
        self.eats = 0
        self.looks = []

    def act(self, p):
        if p.get("ate"):
            self.eats += 1
            d = p["ate"]["delta"]
            self.thought = f"Ate something: energy {'+' if d >= 0 else ''}{d:g}. I won't remember it."
        for s in p["seen"]:
            if s["dist"] <= EAT_REACH:
                return {"do": "eat", "ref": s["ref"]}
        if p.get("touch"):
            self.thought = "Bumped into something. Turning somewhere at random."
        return self.walk.act(p)

    def panel(self):
        return {"thought": self.thought, "memory": {"kinds": [], "places": []},
                "character": {}, "mode": "wander"}
