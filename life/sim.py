"""A session: one world, one or more creatures, and the loop that runs them.

Each tick, for each living creature: the body senses (life/body.py), the
mind picks one action from the percept alone, and the world applies it.
Then eaten objects regrow when their time comes.
"""

import secrets

import numpy as np

from life import config as C
from life.metrics import Recorder
from life.world3d import World

CREATURES = {}          # name -> (label, maker(seed, reserve, boldness)), filled by register()


def register(name, label, maker, colour):
    CREATURES[name] = {"label": label, "make": maker, "colour": colour}


def _load_minds():
    if CREATURES:
        return
    from life.minds import registry          # noqa: F401  (registers every creature)


def new_seed():
    """A fresh random world seed (instant randomness; every seed used is shown and logged)."""
    return secrets.randbits(31)


def character(seed, creature_seed):
    """Reserve and boldness, drawn per creature at birth (bench ranges, M33)."""
    rng = np.random.default_rng([seed, 9, creature_seed])
    return float(rng.uniform(C.RESERVE_LO, C.RESERVE_HI)), float(rng.uniform(C.BOLDNESS_LO, C.BOLDNESS_HI))


class Creature:
    def __init__(self, ident, name, world, creature_seed):
        _load_minds()
        spec = CREATURES[name]
        self.id = ident
        self.name = name
        self.label = spec["label"]
        self.colour = spec["colour"]
        self.creature_seed = creature_seed
        self.reserve, self.boldness = character(world.seed, creature_seed)
        self.body = world.new_body(ident, creature_seed)
        self.mind = spec["make"](world.seed * 1000 + creature_seed, self.reserve, self.boldness)
        self.rec = Recorder(world, self.body)
        self.last_event = None


class Session:
    def __init__(self, seed=None, creatures=("wanderer",), creature_seed=1):
        _load_minds()
        self.seed = new_seed() if seed is None else int(seed)
        self.world = World(self.seed)
        self.creatures = [Creature(i, name, self.world, creature_seed + i) for i, name in enumerate(creatures)]
        self.events = []
        self.grown = []

    @property
    def tick(self):
        return self.world.tick

    def all_dead(self):
        return all(not c.body.alive for c in self.creatures)

    def step(self):
        w = self.world
        out = []
        for c in self.creatures:
            if not c.body.alive:
                continue
            from life.body import percept
            p = percept(c.body, w, w.tick)
            c.rec.after_sense(w.tick)
            action = c.mind.act(p)
            ev = w.apply(c.body, action)
            c.rec.after_action(w.tick, ev)
            c.last_event = ev
            if ev and ("ate" in ev or "died" in ev):
                out.append(dict(ev, creature=c.id, name=c.name, tick=w.tick))
        self.grown = w.end_tick()
        self.events.extend(out)
        if len(self.events) > 200:
            del self.events[: len(self.events) - 200]
        return out

    def run(self, max_ticks=C.MAX_TICKS):
        while self.tick < max_ticks and not self.all_dead():
            self.step()
        return [c.rec.summary(c.mind) for c in self.creatures]

    # -------------------------------------------------------------- for the page

    def region_name(self, ref):
        obj = self.world.ecology.objects.get(ref)
        return None if obj is None else C.REGIONS[obj.region]

    def creature_state(self, c, chart_every=5):
        panel = c.mind.panel()
        thought = panel.get("thought", "")
        if "{where}" in thought:                     # display only: the narrator names the place for us
            where = self.region_name(panel.get("focus"))
            thought = thought.replace("{where}", f"in the {where}" if where else "here")
        s = c.rec.summary(c.mind)
        return {"id": c.id, "name": c.name, "label": c.label, "colour": c.colour,
                "x": round(c.body.x, 3), "z": round(c.body.z, 3),
                "y": round(self.world.terrain.height_at(c.body.x, c.body.z), 3),
                "heading": round(c.body.heading, 4), "energy": round(c.body.energy, 2), "alive": c.body.alive,
                "age": c.body.age, "action": c.body.last_action.get("do"),
                "reserve": round(c.reserve, 1), "boldness": round(c.boldness, 2),
                "thought": thought, "mode": panel.get("mode"), "memory": panel.get("memory"),
                "focus": panel.get("focus"), "look_target": panel.get("look_target"),
                "trail": c.body.trail[-C.TRAIL_LENGTH:],
                "energy_series": c.rec.energy[::chart_every][-600:],
                "windows": s["windows"][-120:],
                "stats": {k: s[k] for k in ("eats", "food", "poison", "nothing", "food_per_100", "poison_share",
                                            "looks", "looks_changed", "bumps", "walked")},
                "episodes": s["episodes"][-10:]}

    def state(self, with_objects=False):
        out = {"seed": self.seed, "tick": self.tick, "objects_version": self.world.ecology.version,
               "creatures": [self.creature_state(c) for c in self.creatures],
               "events": self.events[-30:]}
        if with_objects:
            out["objects"] = [o.public() for o in self.world.ecology.alive()]
        return out
