"""The part of a mind that turns recognition into action in the world: the drive, attention and place memory.

Frankie and the trial-and-error baseline both use this, so they differ only
in how they recognise things (life/minds/frankie.py, life/minds/trial.py).
Every choice is labelled.

- The drive is spend-or-conserve (from the design: "randomness proposes,
  character decides"; the numbers are untested). Below his reserve R the
  creature is hungry and seeks food he believes is good. At or above R he is
  fed: he mostly rests, eats good food that is right in front of him if he
  has room, and now and then randomness proposes something (try that unknown
  thing, or walk off somewhere), which his character accepts with chance
  equal to his boldness b. R and b are drawn at birth. There is no novelty
  reward.
- Attention follows recognition (untested: Aitzaz's "attention carried
  between layers"). The recogniser says what each blurry object could be. A
  sharp look is taken only when it could change the decision: the blurry
  view leaves candidates that disagree about the outcome, or leaves none and
  the creature means to try it anyway (so the new memory gets every trait).
- "Believes is good": the kind's own record says it fed him at least as often
  as the bar 0.9 - 0.3 b (the bench's bar, PLACEHOLDER-27; the record here
  is "fed me", not the bench's "stayed above R").
- Place memory (conventional: a coarse grid of counts, like a hand-drawn
  map). Each 16 m square remembers how often he was fed or poisoned there
  and which kinds he found there. When hungry with nothing he trusts in view,
  he walks straight towards the remembered square that fed him most (minus
  poisonings), discounted by distance, skipping squares he searched lately.
- Movement is straight-line steering. There is no route-finder and no detour
  code: bumping into a fence is felt (touch) and written in the thought, and
  nothing else.
"""

import math

import numpy as np

from life import config as C
from life.minds.common import EAT_REACH, RandomWalk, angle_to, dist, steer

CELL = 16.0                  # place memory squares, metres (untested)
IGNORE_TICKS = 300           # after deciding not to eat something, leave it alone this long (untested)
PROPOSAL_RATE = 0.08         # chance per tick that randomness proposes something while fed (untested)
ASSESS_NEAREST = 10          # recognise only the nearest this many objects each tick (speed)
FED_REACH = 6.0              # a fed creature eats good food only this close (untested)
WANDER_STEPS = (8, 30)       # an accepted "walk off somewhere" lasts this many steps
SEARCH_FORGET = 200          # a square searched without luck is skipped for this many ticks

HUE_WORDS = ((0.04, "red"), (0.10, "orange"), (0.18, "yellow"), (0.45, "green"), (0.55, "teal"),
             (0.72, "blue"), (0.83, "purple"), (0.95, "pink"), (1.01, "red"))


def hue_word(h):
    for top, w in HUE_WORDS:
        if h < top:
            return w
    return "red"


def size_word(s):
    return "small" if s < 0.33 else "big" if s > 0.67 else ""


class Places:
    """Place memory: per 16 m square, fed / poisoned / nothing counts and the kinds found there."""

    def __init__(self):
        self.cells = {}

    def key(self, x, z):
        return int(x // CELL), int(z // CELL)

    def note(self, x, z, outcome, kind=None):
        c = self.cells.setdefault(self.key(x, z), {"fed": 0, "poisoned": 0, "nothing": 0, "kinds": {},
                                                   "searched": -10**9})
        c[{1: "fed", -1: "poisoned", 0: "nothing"}[outcome]] += 1
        if kind is not None:
            c["kinds"][str(kind)] = c["kinds"].get(str(kind), 0) + 1

    def best(self, x, z, tick):
        best, score_best = None, 0.0
        for (i, j), c in self.cells.items():
            if tick - c["searched"] < SEARCH_FORGET:
                continue
            score = c["fed"] - 2 * c["poisoned"]
            if score <= 0:
                continue
            cx, cz = (i + 0.5) * CELL, (j + 0.5) * CELL
            s = score / (1.0 + math.hypot(cx - x, cz - z) / 30.0)
            if s > score_best:
                best, score_best = (cx, cz, (i, j)), s
        return best

    def searched(self, cell, tick):
        if cell in self.cells:
            self.cells[cell]["searched"] = tick

    def view(self):
        out = []
        for (i, j), c in sorted(self.cells.items(), key=lambda kv: -(kv[1]["fed"] + kv[1]["poisoned"])):
            out.append({"name": f"square {i},{j}", "x": (i + 0.5) * CELL, "z": (j + 0.5) * CELL, "size": CELL,
                        "fed": c["fed"], "poisoned": c["poisoned"], "nothing": c["nothing"],
                        "kinds": c["kinds"]})
        return out


class Forager:
    """Drive, attention, place memory and steering around a recogniser.

    A subclass provides:
      judge(values, known) -> dict with "status" in {"good", "bad", "mixed", "unknown"}, "leader_good",
                              "candidates", "says" (plain words)
      learn(values, delta, taste) -> plain words about what memory did
      kinds_view() -> list for the panel
      always_look: bool
    """

    always_look = False
    use_places = True

    def __init__(self, seed, reserve, boldness):
        self.rng = np.random.default_rng([seed, 11])
        self.reserve = float(reserve)
        self.boldness = float(boldness)
        self.bar = 0.9 - 0.3 * self.boldness
        self.walk = RandomWalk(self.rng, turn_chance=0.08)
        self.places = Places()
        self.sharp = {}               # ref -> 18 sharp readings (objects never change while they stand)
        self.ignore = {}              # ref -> tick until which to leave it alone
        self.target = None            # {"ref", "x", "z", "intent": "eat" | "try", "looked": bool}
        self.goal = None              # a place-memory square to walk to
        self.wander_left = 0
        self.pending_eat = None
        self.pending_look = None
        self.look_log = []            # [{"before", "after", "changed"}] for every look that fed a decision
        self.thought = "Just born. Looking around."
        self.focus = None
        self.mode = "fed"
        self.meal = C.NOURISH_GAIN    # what a good meal is worth, from his own experience
        self.meals = []
        self.tick = 0
        self.last_seen = {}

    # -------------------------------------------------------------- helpers

    def values_for(self, s):
        """The reading of a seen object: sharp if he looked at it, else blurry. NaN where unknown."""
        v = np.full(22, np.nan)
        if s["ref"] in self.sharp:
            v[:18] = self.sharp[s["ref"]]
            return v, 18
        v[:6] = s["traits"]
        return v, 6

    def describe(self, s):
        t = s["traits"]
        w = " ".join(x for x in (size_word(t[3]), hue_word(t[2])) if x)
        return f"something {w}"

    # -------------------------------------------------------------- one tick

    def act(self, p):
        self.tick = p["tick"]
        e = p["energy"]
        self.mode = "hungry" if e < self.reserve else "fed"
        self.last_seen = {s["ref"]: s for s in p["seen"]}
        if p.get("ate"):
            self._after_eat(p)
        if p.get("sharp") is not None and self.pending_look is not None:
            self.sharp[p["sharp"]["ref"]] = list(p["sharp"]["traits"])
        if p.get("failed") == "look" and self.pending_look is not None:
            self.ignore[self.pending_look] = self.tick + 20
            self.target = None
        self.pending_look = None
        if p.get("touch"):
            what = "water" if p["touch"] == "water" else "something solid"
            aim = f" I still want what's ahead." if self.target else ""
            self.thought = f"Bumped into {what}.{aim}"
        # randomness proposes, character decides: now and then, walk off somewhere for a while
        if self.wander_left > 0:
            self.wander_left -= 1
            return self.walk.act(p)
        if self.rng.random() < PROPOSAL_RATE and self.rng.random() < self.boldness * (0.5 if self.mode == "hungry" else 1):
            self.wander_left = int(self.rng.integers(*WANDER_STEPS))
            self.target = None
            self.goal = None
            self.thought = "A whim: walking off somewhere new for a while."
            return self.walk.act(p)
        if self.target is not None:
            return self._pursue(p)
        return self._choose(p)

    # -------------------------------------------------------------- choosing what to do next

    def _assess(self, p):
        seen = [s for s in p["seen"] if self.ignore.get(s["ref"], -1) < self.tick][:ASSESS_NEAREST]
        out = []
        for s in seen:
            v, known = self.values_for(s)
            out.append((s, self.judge(v, known)))
        return out

    def _choose(self, p):
        e = p["energy"]
        seen = self._assess(p)
        good = [(s, j) for s, j in seen if j["status"] == "good"]
        mixed = [(s, j) for s, j in seen if j["status"] == "mixed"]
        unknown = [(s, j) for s, j in seen if j["status"] == "unknown"]
        room = e <= C.ENERGY_MAX - 0.8 * self.meal
        if self.mode == "hungry":
            pick = good[:1] or mixed[:1]
            if pick:
                s, j = pick[0]
                return self._set_target(p, s, j, "eat", f"Hungry. Saw {self.describe(s)} {{where}}: {j['says']}")
            if unknown and self.rng.random() < self.boldness:
                s, j = unknown[int(self.rng.integers(len(unknown)))]
                return self._set_target(p, s, j, "try", f"Hungry, and nothing I trust in sight. Saw {self.describe(s)} "
                                                        f"{{where}} I've never seen the like of. Risking it.")
            return self._wander_to_memory(p, "Hungry (energy {:.0f}, reserve {:.0f}). Nothing I trust in sight; ".format(e, self.reserve))
        # fed
        if room:
            near = [(s, j) for s, j in good if s["dist"] <= FED_REACH]
            if near:
                s, j = near[0]
                return self._set_target(p, s, j, "eat", f"Not hungry, but {self.describe(s)} right here {{where}}: "
                                                        f"{j['says']}")
        if self.rng.random() < PROPOSAL_RATE and unknown and room:
            s, j = unknown[int(self.rng.integers(len(unknown)))]
            if self.rng.random() < self.boldness:
                return self._set_target(p, s, j, "try", f"Well fed and feeling bold. Saw {self.describe(s)} {{where}} "
                                                        f"I don't know: going to try it.")
            self.thought = f"Saw {self.describe(s)} I don't know. Not bold enough to try it right now."
            return {"do": "rest"}
        if not p.get("touch"):
            self.thought = f"Well fed (energy {e:.0f}, reserve {self.reserve:.0f}). Resting to save energy."
        return {"do": "rest"}

    def _set_target(self, p, s, j, intent, thought):
        self.target = {"ref": s["ref"], "x": s["x"], "z": s["z"], "intent": intent, "since": self.tick,
                       "before": None}
        self.focus = s["ref"]
        self.goal = None
        self.thought = thought
        return self._pursue(p)

    def _wander_to_memory(self, p, prefix):
        if self.use_places:
            if self.goal is None:
                b = self.places.best(p["x"], p["z"], self.tick)
                if b is not None:
                    self.goal = b
            if self.goal is not None:
                gx, gz, cell = self.goal
                if dist(p, gx, gz) < 3.0:
                    self.places.searched(cell, self.tick)
                    self.goal = None
                else:
                    self.thought = prefix + f"heading back to square {cell[0]},{cell[1]}, where I was fed before."
                    self.focus = None
                    return steer(p, gx, gz)
        self.thought = prefix + "searching at random."
        self.focus = None
        return self.walk.act(p)

    # -------------------------------------------------------------- going after one object

    def _pursue(self, p):
        t = self.target
        s = self.last_seen.get(t["ref"])
        if s is not None:
            t["x"], t["z"] = s["x"], s["z"]
            t["since"] = self.tick
        d = dist(p, t["x"], t["z"])
        if s is None and d < 3.0 and abs(angle_to(p, t["x"], t["z"])) < 50:
            self.thought = "It's gone. Something else must have eaten it."
            self.target = None
            return {"do": "rest"}
        if s is None and self.tick - t["since"] > 40:
            self.target = None                         # lost sight of it for good
            return {"do": "rest"}
        if d > EAT_REACH:
            if s is not None and d <= C.SHARP_RANGE and t["ref"] not in self.sharp and self._worth_look(s, t):
                return self._look(t, s)
            return steer(p, t["x"], t["z"])
        if s is None:                                  # right there but not in view: turn to it
            return {"do": "turn", "angle": max(-45, min(45, angle_to(p, t["x"], t["z"])))}
        if t["ref"] not in self.sharp and self._worth_look(s, t):
            return self._look(t, s)
        return self._decide(p, s, t)

    def _worth_look(self, s, t):
        if self.always_look:
            return True
        v, known = self.values_for(s)
        j = self.judge(v, known)
        if j["status"] == "mixed":
            return True
        return j["status"] == "unknown" and t["intent"] == "try"

    def _look(self, t, s):
        v, known = self.values_for(s)
        j = self.judge(v, known)
        t["before"] = self._would_eat(j, t)
        t["blurry"] = j
        self.pending_look = t["ref"]
        self.thought = f"{j['says']} Taking a closer look…"
        return {"do": "look", "ref": t["ref"]}

    def _would_eat(self, j, t):
        if j["status"] == "good":
            return True
        if j["status"] == "mixed":
            return bool(j["leader_good"])
        if j["status"] == "unknown":
            return t["intent"] == "try"
        return False

    def _decide(self, p, s, t):
        v, known = self.values_for(s)
        j = self.judge(v, known)
        eat = self._would_eat(j, t)
        if t.get("before") is not None:
            self.look_log.append({"tick": self.tick, "before": t["before"], "after": eat, "changed": t["before"] != eat})
            ruled = j.get("ruled_out") or ""
            prefix = f"Closer look: {ruled} " if ruled else "Closer look: "
        else:
            prefix = ""
        self.target = None
        if eat:
            self.pending_eat = {"ref": s["ref"], "values": v, "known": known, "x": p["x"], "z": p["z"], "judged": j}
            word = "Trying it" if j["status"] == "unknown" else "Eating"
            self.thought = prefix + f"{j['says']} {word}."
            return {"do": "eat", "ref": s["ref"]}
        self.ignore[s["ref"]] = self.tick + IGNORE_TICKS
        self.thought = prefix + f"{j['says']} Leaving it."
        return {"do": "rest"}

    def _after_eat(self, p):
        a = p["ate"]
        pe = self.pending_eat
        self.pending_eat = None
        if pe is None or pe["ref"] != a["ref"]:
            return
        delta = a["delta"]
        outcome = 1 if delta > 0 else -1 if delta < 0 else 0
        if delta > 0:
            self.meals.append(delta)
            self.meal = float(np.mean(self.meals[-20:]))
        v = pe["values"].copy()
        v[18:] = a["taste"]
        said = self.learn(v, pe["known"], delta, pe["judged"])
        if self.use_places:
            self.places.note(pe["x"], pe["z"], outcome, said.get("kind"))
        feel = {1: f"That fed me (+{delta:g}).", -1: f"Poisoned! ({delta:g}).", 0: "That did nothing for me."}[outcome]
        self.thought = f"{feel} {said['words']}"
        self.sharp.pop(a["ref"], None)

    # -------------------------------------------------------------- the panel

    def panel(self):
        return {"thought": self.thought, "mode": self.mode, "focus": self.focus,
                "look_target": self.pending_look,
                "memory": {"kinds": self.kinds_view(), "places": self.places.view() if self.use_places else []}}
