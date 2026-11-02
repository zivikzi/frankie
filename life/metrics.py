"""What we measure about a creature's life. World-side: these numbers read the truth; the mind never does.

Measures (BRIEF, "What learning the rules should look like, measured"):
- lifespan, in ticks;
- food found per 100 ticks (nourishing eats);
- the share of poison among eats, in windows of 50 ticks (the learning curve), and by eat number;
- the share of sharp looks that changed the decision;
- the context rule: context-fruit eats in its good region against its bad region, early and late;
- obstacle episodes: from the first sight of food behind a fence or across the river (while on the wrong
  side) to getting inside the fence or across, in ticks and metres walked.
"""

import math

from life import config as C


class Recorder:
    def __init__(self, world, body):
        self.world = world
        self.body = body
        self.eats = []
        self.bumps = {"fence": 0, "wall": 0, "river": 0, "edge": 0}
        self.looks = 0
        self.energy = []
        self.episodes = []
        self.open = {}
        self.bump_ticks = []

    # -------------------------------------------------------------- per tick

    def after_action(self, tick, event):
        if self.body.alive or self.body.died_at == tick:
            self.energy.append(round(self.body.energy, 2))
        if not event:
            return
        if "bump" in event:
            self.bumps[event["bump"]] = self.bumps.get(event["bump"], 0) + 1
            self.bump_ticks.append((tick, event["bump"]))
        if event.get("look") is not None:
            self.looks += 1
        if "ate" in event:
            self.eats.append({"tick": tick, "nature": event["nature"], "kind": event["kind"],
                              "label": event["label"], "region": event["region"], "delta": event["delta"],
                              "behind": event["behind"]})

    def after_sense(self, tick):
        """Open and close obstacle episodes from what the body could see and where it stands."""
        b, obs, eco = self.body, self.world.obstacles, self.world.ecology
        # close
        for key, ep in list(self.open.items()):
            if self._reached(key):
                ep["end"] = tick
                ep["ticks"] = tick - ep["start"]
                ep["metres"] = round(b.walked - ep["walked0"], 2)
                ep["reached"] = True
                del self.open[key]
        # open
        river = obs.river
        my_side = river.side(b.x, b.z) if river is not None else 0
        for ref in b.seen_ids:
            obj = eco.objects.get(ref)
            if obj is None:
                continue
            if obj.behind is not None and obj.behind[0] == "fence":
                key = ("fence", obj.behind[1])
            elif river is not None and river.side(obj.x, obj.z) != my_side and obj.nature == "nourish":
                key = ("river", river.side(obj.x, obj.z))      # good food across the river, from this side
            else:
                continue
            if key in self.open or self._reached(key) or not self._clear_of(key):
                continue
            ep = {"obstacle": key[0], "id": key[1], "order": len(self.episodes) + 1, "start": tick,
                  "walked0": round(b.walked, 2), "start_dist": round(math.hypot(obj.x - b.x, obj.z - b.z), 2),
                  "end": None, "ticks": None, "metres": None, "reached": False}
            self.episodes.append(ep)
            self.open[key] = ep

    def _clear_of(self, key, margin=4.0):
        """An episode starts only when the creature is at least `margin` metres outside the fence or off the bank."""
        b, obs = self.body, self.world.obstacles
        if key[0] == "fence":
            f = next(f for f in obs.fences if f.id == key[1])
            return math.hypot(b.x - f.cx, b.z - f.cz) > f.radius + margin
        return abs(obs.river.offset(b.x, b.z)) > C.RIVER_HALF_WIDTH + margin

    def _reached(self, key):
        b, obs = self.body, self.world.obstacles
        if key[0] == "fence":
            f = next(f for f in obs.fences if f.id == key[1])
            return f.inside(b.x, b.z, margin=0.5)
        river = obs.river
        return river.side(b.x, b.z) == key[1] and abs(river.offset(b.x, b.z)) > C.RIVER_HALF_WIDTH

    # -------------------------------------------------------------- summary

    def summary(self, mind=None):
        b = self.body
        life = b.died_at + 1 if b.died_at is not None else b.age
        food = [e for e in self.eats if e["nature"] == "nourish"]
        poison = [e for e in self.eats if e["nature"] == "poison"]
        windows = []
        for w0 in range(0, max(life, 1), C.WINDOW_TICKS):
            es = [e for e in self.eats if w0 <= e["tick"] < w0 + C.WINDOW_TICKS]
            windows.append([len(es), sum(1 for e in es if e["nature"] == "poison")])
        ctx = [e for e in self.eats if e["label"] == "context fruit"]
        look_log = list(getattr(mind, "look_log", []) or [])
        return {
            "lifespan": life, "died": b.died_at is not None, "energy_end": round(b.energy, 2),
            "eats": len(self.eats), "food": len(food), "poison": len(poison),
            "nothing": len(self.eats) - len(food) - len(poison),
            "food_per_100": round(100.0 * len(food) / max(life, 1), 4),
            "poison_share": round(len(poison) / len(self.eats), 4) if self.eats else None,
            "windows": windows,                                   # [eats, poison eats] per 50 ticks
            "eat_seq": ["f" if e["nature"] == "nourish" else "p" if e["nature"] == "poison" else "0"
                        for e in self.eats],
            "ctx_eats": [[e["tick"], e["nature"]] for e in ctx],
            "looks": self.looks,
            "looks_changed": sum(1 for x in look_log if x.get("changed")),
            "looks_judged": len(look_log),
            "bumps": dict(self.bumps),
            "walked": round(b.walked, 1),
            "episodes": [{k: v for k, v in ep.items() if k != "walked0"} for ep in self.episodes],
        }
