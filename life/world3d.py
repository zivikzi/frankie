"""One living world: land, obstacles, objects and the bodies walking in it.

The world applies the rules: walking (blocked by fences, walls, the river
and the map's edge), energy bookkeeping, eating, regrowth and death. Minds
never touch this object; they send actions and get percepts (life/body.py).
"""

import math

import numpy as np

from life import body as B
from life import config as C
from life.ecology import Ecology
from life.obstacles import make_obstacles
from life.terrain import Terrain


class World:
    def __init__(self, seed: int):
        self.seed = int(seed)
        rng = np.random.default_rng([self.seed, 1])
        self.terrain = Terrain(rng)
        self.obstacles = make_obstacles(np.random.default_rng([self.seed, 2]), self.terrain)
        self.ecology = Ecology(self.seed, np.random.default_rng([self.seed, 3]), self.terrain, self.obstacles)
        self.spawn_rng = np.random.default_rng([self.seed, 4])
        self.tick = 0
        self.spawn = self._spawn_point()

    # -------------------------------------------------------------- bodies

    def _spawn_point(self):
        """Where creatures start: a free spot, on the far side of the river from its rich food."""
        river = self.obstacles.river
        for _ in range(500):
            x, z = self.spawn_rng.uniform(10, C.WORLD_SIZE - 10, size=2)
            if not self.obstacles.free_spot(x, z, 2.0) or self.obstacles.behind(x, z) is not None:
                continue
            if river is not None and river.side(x, z) == self.ecology.river_food_side:
                continue
            if any(math.hypot(x - f.cx, z - f.cz) < f.radius + 6 for f in self.obstacles.fences):
                continue
            return float(x), float(z), float(self.spawn_rng.uniform(0, 2 * math.pi))
        return C.WORLD_SIZE / 2, C.WORLD_SIZE / 2, 0.0

    def new_body(self, ident, creature_seed):
        x, z, h = self.spawn
        return B.Body(ident, x, z, h, np.random.default_rng([self.seed, 100 + ident, creature_seed]))

    # -------------------------------------------------------------- actions

    def apply(self, body, action):
        """Carry out one action for one body this tick. Returns a short event dict for the log."""
        if not body.alive:
            return None
        do = action.get("do", "rest")
        event = None
        body.spend(C.TICK_COST)
        if do in ("turn", "move"):
            ang = max(-C.TURN_MAX_DEG, min(C.TURN_MAX_DEG, float(action.get("angle", 0.0))))
            body.heading = (body.heading + math.radians(ang)) % (2 * math.pi)
            if do == "turn":
                body.spend(C.TURN_COST)
        if do in ("step", "move"):
            event = self._step(body)
        elif do == "look":
            body.spend(C.LOOK_COST)
            seen = B.sharp_look(body, self, action.get("ref"))
            if seen is None:
                body.pending["failed"] = "look"
            body.pending["sharp"] = seen
            event = {"look": action.get("ref"), "ok": seen is not None}
        elif do == "eat":
            event = self._eat(body, action.get("ref"))
        body.last_action = action
        body.age += 1
        if not body.alive and body.died_at is None:
            body.died_at = self.tick
            event = dict(event or {}, died=True)
        return event

    def _step(self, body):
        nx = body.x + C.STEP_LENGTH * math.cos(body.heading)
        nz = body.z + C.STEP_LENGTH * math.sin(body.heading)
        what = None
        if not (0.5 <= nx <= C.WORLD_SIZE - 0.5 and 0.5 <= nz <= C.WORLD_SIZE - 0.5):
            what = "edge"
        else:
            what = self.obstacles.blocks_move(body.x, body.z, nx, nz)
        if what is not None:
            body.spend(C.BUMP_COST)
            body.pending["touch"] = "water" if what == "river" else "solid"
            return {"bump": what}
        h0 = self.terrain.height_at(body.x, body.z)
        h1 = self.terrain.height_at(nx, nz)
        body.spend(C.STEP_COST + C.CLIMB_COST_PER_M * max(0.0, h1 - h0))
        body.x, body.z = nx, nz
        body.walked += C.STEP_LENGTH
        body.trail.append((round(nx, 2), round(nz, 2)))
        if len(body.trail) > C.TRAIL_LENGTH:
            del body.trail[: len(body.trail) - C.TRAIL_LENGTH]
        return None

    def _eat(self, body, ref):
        obj = self.ecology.objects.get(ref)
        if obj is None or not obj.alive or math.hypot(obj.x - body.x, obj.z - body.z) > C.EAT_RANGE:
            body.pending["failed"] = "eat"
            return {"eat_failed": ref}
        self.ecology.eat(ref, self.tick)
        delta = self.ecology.energy_of(obj.nature)
        before = body.energy
        body.gain(delta)
        body.pending["ate"] = {"ref": ref, "delta": delta, "energy_after": round(body.energy, 4),
                               "taste": B.taste(body, obj)}
        return {"ate": ref, "kind": obj.kind.ident, "label": obj.kind.label, "nature": obj.nature,
                "region": obj.region, "delta": delta, "before": round(before, 3), "behind": obj.behind}

    def end_tick(self):
        grown = self.ecology.regrow(self.tick)
        self.tick += 1
        return grown

    # -------------------------------------------------------------- for the page

    def static(self):
        """Everything about the land that never changes, for drawing."""
        t = self.terrain
        return {"seed": self.seed, "size": C.WORLD_SIZE, "grid": t.n,
                "height": [round(float(v), 3) for v in t.height.ravel()],
                "region": [int(v) for v in t.region.ravel()],
                "regions": list(C.REGIONS), "obstacles": self.obstacles.describe(),
                "spawn": list(self.spawn)}
