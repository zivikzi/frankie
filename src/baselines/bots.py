"""The kill-test bots (section 4, KT-05, X33, X36).

Every bot stores each item at the moment it eats it, and chooses by a fixed
rule that never reads energy. Bots pay nothing and have no chooser: their
choices carry action_provenance = baseline-rule (glossary). A bot is told
nothing but the reading in front of it and, after an eat, the energy it gave;
the schedule of a run is fixed and public, so a bot that needs h1 or the
teaching items finds them by counting its own eats (KT-97): the 41st item it
stores is h1, and the 41st to 48th are t1 to t8.

When a rule refers to something a bot has not stored yet (any item at all, h1
or a teaching item), its would-be pick is "eat", as X36 says of an empty
memory. That happens only on forced tastes, so it changes only the log.
"""

import itertools

import numpy as np

from world import traits

from . import rules as K


class Bot:
    agent_type = ""

    def __init__(self, config):
        self.params = dict(config["params"])
        self.items = K.StoredItems()
        self._pending = None
        self._landed = None
        self.setup()

    def setup(self):
        pass

    # the interface (harness/protocol.py)
    def decide(self, visible, energy_milli):
        o = np.array(visible, dtype=np.float64)
        if len(self.items) == 0:
            eat, log = True, {"undefined": True}
        else:
            eat, log = self.rule(o)
        self._pending, self._landed = o, None
        return {"action": "eat" if eat else "skip", "verdict": None, "settle_step": None,
                "thinking": {"unit": "none", "count": 0, "cost_milli": 0}, "drive": None,
                "provenance": "baseline-rule", "log": log}

    def land(self, delta_milli, energy_after_milli, taste):
        self._landed = int(delta_milli)
        return {"verdict": None, "settle_step": None}

    def write(self):
        self.items.add(self._pending, self._landed)
        self.stored()
        self._pending, self._landed = None, None
        return {"events": []}

    def stored(self):
        pass

    def dump(self):
        return self.items.dump()

    def info(self):
        return {"version": [], "constants": self.constants(), "chooser": None, "neuron": None}

    def constants(self):
        return {}

    # the rule
    def rule(self, o):
        raise NotImplementedError


class B1nBot(Bot):
    """Nearest stored item over all observable traits; eats if it was good (X36)."""
    agent_type = "B1n-bot"
    cols = K.OBSERVABLE

    def rule(self, o):
        d = K.mean_nw(self.items.readings, o, self.cols)
        i = K.nearest(d)
        return self.accept(i, d[i]), {"nearest": i, "distance_nw": float(d[i])}

    def accept(self, i, dist):
        return bool(self.items.good[i])


class B1nBotR(B1nBot):
    """B1n-bot that eats only if the nearest item is good and lies within r (section 4)."""
    agent_type = "B1n-bot-r"

    def accept(self, i, dist):
        r = self.params["radius"]
        return bool(self.items.good[i]) and (r is None or dist <= r)

    def constants(self):
        return {"radius_nw": [self.params["radius"], "KT-05, KT-101"]}


class B1t(Bot):
    """Skips exact matches of bad items and eats everything else."""
    agent_type = "B1t"

    def rule(self, o):
        bad_match = bool(np.any(K.exact(self.items.readings, o) & ~self.items.good))
        return not bad_match, {"exact_bad": bad_match}


class B2(Bot):
    """Eats if the surface distance to the nearest stored good item is at most 10 (PLACEHOLDER-91)."""
    agent_type = "B2"

    def rule(self, o):
        good = self.items.good
        if not good.any():
            return False, {"surface_nw": None}
        d = K.mean_nw(self.items.readings[good], o, K.SURFACE)
        best = float(d.min())
        return best <= K.SURFACE_NW, {"surface_nw": best}


class B2e(Bot):
    """Eats only if some stored good item lies within 8 noise widths on every one of H's 4 core traits."""
    agent_type = "B2e"

    def setup(self):
        self.core = tuple(int(t) for t in self.params["core"])   # handed in by the harness (X03)
        if len(self.core) != 4 or not all(t in K.OBSERVABLE for t in self.core):
            raise ValueError("B2e needs H's 4 core traits")

    def rule(self, o):
        good = self.items.good
        if not good.any():
            return False, {"core_match": False}
        hit = bool(np.any(np.all(K.trait_nw(self.items.readings[good], o, self.core) <= K.CORE_NW, axis=1)))
        return hit, {"core_match": hit}


class G01(Bot):
    """Always eats."""
    agent_type = "G01"

    def rule(self, o):
        return True, {}


class G04(Bot):
    """Eats only exact matches of a stored good item."""
    agent_type = "G04"

    def rule(self, o):
        hit = bool(np.any(K.exact(self.items.readings, o) & self.items.good))
        return hit, {"exact_good": hit}


class G05(Bot):
    """Eats exact copies of h1, and anything whose surface distance from h1 is above 10."""
    agent_type = "G05"

    def rule(self, o):
        if len(self.items) <= K.H1_ITEM:
            return True, {"undefined": True}
        h1 = self.items.readings[K.H1_ITEM:K.H1_ITEM + 1]
        copy = bool(K.exact(h1, o)[0])
        surface = float(K.mean_nw(h1, o, K.SURFACE)[0])
        return copy or surface > K.SURFACE_NW, {"h1_copy": copy, "surface_nw": surface}


class G06(Bot):
    """B1n-bot with each trait weighted by its rarity among the stored items (X33)."""
    agent_type = "G06"

    def rule(self, o):
        s = self.items.readings
        near = K.trait_nw(s, o, K.OBSERVABLE) <= K.RARE_NW
        w = 1.0 - near.sum(axis=0) / len(s)              # 1 minus the share within 5 noise widths (section 4)
        cols = K.OBSERVABLE
        acc = w[0] * np.abs(s[:, cols[0]] - o[cols[0]])
        for k, t in enumerate(cols[1:], 1):
            acc = acc + w[k] * np.abs(s[:, t] - o[t])
        i = K.nearest(acc)
        return bool(self.items.good[i]), {"nearest": i}


def _outside_nw(values: np.ndarray, lo: float, hi: float) -> np.ndarray:
    """How far each value lies outside [lo, hi], in noise widths (0 inside)."""
    return np.maximum(np.maximum(lo - values, values - hi), 0.0) / K.NOISE_WIDTH


class G07(Bot):
    """The single observable trait whose range rule best sorts the stored teaching items (X33)."""
    agent_type = "G07"
    width = 1

    def rule(self, o):
        teach = slice(K.WARMUP_TASTES, K.WARMUP_TASTES + K.TEACHING_TASTES)
        s, good = self.items.readings[teach], self.items.good[teach]
        if len(s) == 0:
            return True, {"undefined": True}
        best, best_score, best_ranges = None, -1, None
        for combo in itertools.combinations(K.OBSERVABLE, self.width):   # lower trait numbers first
            inside = np.ones(len(s), dtype=bool)
            ranges = []
            for t in combo:
                lo, hi = float(s[good, t].min()), float(s[good, t].max())
                ranges.append((lo, hi))
                inside &= _outside_nw(s[:, t], lo, hi) <= K.RANGE_NW
            score = int(np.sum(inside == good))
            if score > best_score:                      # ties keep the earlier, lower-numbered choice
                best, best_score, best_ranges = combo, score, ranges
        eat = all(float(_outside_nw(np.array([o[t]]), lo, hi)[0]) <= K.RANGE_NW
                  for t, (lo, hi) in zip(best, best_ranges))
        return eat, {"traits": list(best), "score": best_score}


class G08(G07):
    """G07 with the best pair of observable traits; eats only if within on both."""
    agent_type = "G08"
    width = 2


class G09(Bot):
    """Eats in h1's scene and refuses elsewhere."""
    agent_type = "G09"

    def rule(self, o):
        if len(self.items) <= K.H1_ITEM:
            return True, {"undefined": True}
        d = abs(float(o[traits.SCENE]) - float(self.items.readings[K.H1_ITEM, traits.SCENE])) / K.NOISE_WIDTH
        return d <= K.EXACT_NW, {"scene_nw": d}      # "in h1's scene": KT-05's exact bound on scene (KT-100)


class G16(B1nBotR):
    """B1n-bot-r over the parts and details traits only, with its own r (section 4)."""
    agent_type = "G16"
    cols = K.INNER


class G17(B1nBot):
    """A near-copy refuser over all observable traits (section 4)."""
    agent_type = "G17"

    def setup(self):
        self.triggered = False

    def stored(self):
        if not self.triggered:
            s, good = self.items.readings, self.items.good
            if good.any() and (~good).any():
                bad = s[~good]
                self.triggered = any(bool(np.any(K.mean_nw(s[good], b, K.OBSERVABLE) <= K.NEAR_COPY_NW))
                                     for b in bad)

    def near_copy(self, o):
        s = self.items.readings[self.items.good]
        if len(s) == 0:
            return False
        close = bool(np.any(K.mean_nw(s, o, K.OBSERVABLE) <= K.NEAR_COPY_NW))
        return close and not bool(np.any(K.exact(s, o)))

    def rule(self, o):
        eat, log = super().rule(o)
        refused = self.triggered and self.near_copy(o)
        log.update({"triggered": self.triggered, "near_copy_refused": refused})
        return eat and not refused, log


class G18(G17):
    """G16, with G16's r, plus G17's trigger and near-copy refusal over all observable traits."""
    agent_type = "G18"
    cols = K.INNER

    def accept(self, i, dist):
        return B1nBotR.accept(self, i, dist)

    def constants(self):
        return {"radius_nw": [self.params["radius"], "KT-05, KT-101"]}
