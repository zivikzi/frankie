"""Trial and error: the bench's B1n idea in the world (a baseline).

Conventional: nearest-neighbour memory. He remembers every item he ate,
exactly as his sharp look read it, with what eating it did. A new object
counts as a remembered item if it is close to one (mean difference over the
traits he can read at most RADIUS_NW noise widths); then he expects the same
outcome. Anything else is unknown. He looks at everything closely before
eating, since his memory is of exact items. Otherwise he has Frankie's body,
drive and place memory (life/minds/forager.py), so the comparison is about
recognition only.
"""

import numpy as np

from life.minds.forager import Forager

RADIUS_NW = 10.0             # "close to a remembered item": mean difference within 10 noise widths
NOISE_WIDTH = 0.01
WORDS = {1: "fed me", -1: "poisoned me", 0: "did nothing"}


class TrialAndError(Forager):
    name = "trial"
    label = "Trial and error"
    always_look = True

    def __init__(self, seed, reserve, boldness):
        super().__init__(seed, reserve, boldness)
        self.items = np.zeros((0, 18))
        self.outcomes = []

    def judge(self, values, known):
        v = values[:18]
        if not len(self.outcomes):
            return {"status": "unknown", "candidates": [], "leader_good": False, "verdict": None,
                    "says": "I don't know anything yet."}
        mask = ~np.isnan(v)
        diff = np.abs(self.items[:, mask] - v[mask])
        diff = np.where(np.isnan(diff), np.nan, diff)
        d = np.nanmean(diff, axis=1) / NOISE_WIDTH
        d = np.where(np.isnan(d), np.inf, d)
        i = int(np.argmin(d))
        if d[i] > RADIUS_NW:
            return {"status": "unknown", "candidates": [], "leader_good": False, "verdict": None,
                    "says": f"Nothing I've eaten is this close (nearest is {d[i]:.0f} noise widths off)."}
        o = self.outcomes[i]
        good = o == 1
        return {"status": "good" if good else "bad", "candidates": [i], "leader_good": good, "verdict": i,
                "says": f"Very like item {i + 1} I ate, which {WORDS[o]}."}

    def learn(self, values, known, delta, judged):
        o = 1 if delta > 0 else -1 if delta < 0 else 0
        self.items = np.vstack([self.items, values[:18]])
        self.outcomes.append(o)
        return {"kind": None, "words": f"Remembering this exact item (item {len(self.outcomes)})."}

    def kinds_view(self):
        n = len(self.outcomes)
        if not n:
            return []
        return [{"name": f"{n} items", "outcome": "fed me", "eats": sum(1 for o in self.outcomes if o == 1), "note": ""},
                {"name": "", "outcome": "poisoned me", "eats": sum(1 for o in self.outcomes if o == -1), "note": ""},
                {"name": "", "outcome": "did nothing", "eats": sum(1 for o in self.outcomes if o == 0), "note": ""}]
