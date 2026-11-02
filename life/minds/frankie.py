"""Frankie: E1's recognition living in a world.

Recognition is E1's, imported read-only from the frozen src/mind/e1.py:
elimination over layered traits, outside in (context, object, parts,
details; tastes join after an eat), with kinds that stretch, split and merge
(KT-132; untested as a mind). The memory writes below are copied from
E1Mind.write, E1Mind._merge and E1Mind._pair with one change, needed because
in the world Frankie may eat something he only saw blurrily: stretching
ignores traits he never read (numpy fmin/fmax instead of minimum/maximum), so
a kind's unread traits fill in later instead of staying unknown forever. The
frozen harness's event report is left out (there is no harness here).

What Frankie is told is only what his body senses (life/body.py). He never
sees a kind, a nature or a region name.

Variants (to test Aitzaz's ideas):
- Frankie without merging: E1 with merge off.
- Frankie without context: scene and host are never read (no region
  information), so they can neither rule a kind out nor stop a merge.
"""

import numpy as np

from mind import constants as K
from mind.e1 import Kind, Settings, look, outcome_class, outside

from life.minds.forager import Forager

TRAIT_WORDS = ("scene", "what it sits on", "colour", "size", "roundness", "lobes", "stem", "leaves", "spots",
               "thorns", "sticker mark", "exact colour", "sheen", "texture", "smell 1", "smell 2", "smell 3",
               "smell 4", "sweetness", "sourness", "bitterness", "saltiness")
OUTCOME_WORDS = {1: "fed me", -1: "poisoned me", 0: "did nothing"}


def _words(traits):
    names = [TRAIT_WORDS[t] for t in traits]
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]


class E1Memory:
    """E1's kinds and its writes (copied from mind.e1.E1Mind, NaN-aware stretch). Untested as a mind."""

    def __init__(self, settings):
        self.s = settings
        self.kinds = {}
        self.born = 0

    def _lower(self, tenths, widened):
        drop = widened > self.s.widen
        if self.s.taste_keeps:
            drop[K.TASTE_FROM:] = False
        return np.maximum(tenths - drop * self.s.stretch_down, 0)

    def _new(self, values, tenths, cls, above):
        self.born += 1
        slot = 0
        while slot in self.kinds:
            slot += 1
        self.kinds[slot] = Kind(values, tenths, cls, above, self.born)
        return slot

    def write(self, verdict, values, delta, above):
        """After an eat, from the verdict committed before it. Returns (slot, what happened, merges)."""
        cls = outcome_class(delta)
        merges = []
        if not isinstance(verdict, int) or verdict not in self.kinds:
            slot = self._new(values, np.full(K.N_TRAITS, K.WEIGHT_START), cls, above)
            what = "new"
        else:
            kind = self.kinds[verdict]
            if cls == kind.founding():
                widened = np.maximum(kind.lo - values, 0.0) + np.maximum(values - kind.hi, 0.0)
                widened = np.where(np.isnan(widened), 0.0, widened)
                kind.lo = np.fmin(kind.lo, values)          # the one change: unread traits don't erase read ones
                kind.hi = np.fmax(kind.hi, values)
                kind.tenths = self._lower(kind.tenths, widened)
                kind.eats.append([cls, bool(above)])
                slot, what = verdict, "stretch"
            else:
                differ = outside(kind, values, K.N_TRAITS) > self.s.tol
                kind.tenths = np.minimum(kind.tenths + differ * self.s.split_up, K.TENTHS)
                slot = self._new(values, kind.tenths, cls, above)
                what = "split"
        if self.s.merge:
            slot, merges = self._merge(slot)
        return slot, what, merges

    def _merge(self, slot):
        merges = []
        while True:
            pair = self._pair()
            if pair is None:
                return slot, merges
            a, b = pair
            keep, gone = (a, b) if self.kinds[a].born < self.kinds[b].born else (b, a)
            kk, kg = self.kinds[keep], self.kinds[gone]
            lo, hi = np.fmin(kk.lo, kg.lo), np.fmax(kk.hi, kg.hi)
            tenths = np.maximum(kk.tenths, kg.tenths)
            if self.s.merge_widen:
                widened = (hi - lo) - np.fmax(kk.hi - kk.lo, kg.hi - kg.lo)
                tenths = self._lower(tenths, np.where(np.isnan(widened), 0.0, widened))
            kk.lo, kk.hi, kk.tenths = lo, hi, tenths
            kk.eats = kk.eats + kg.eats
            del self.kinds[gone]
            merges.append([gone, keep])
            if slot == gone:
                slot = keep

    def _pair(self):
        slots = sorted(self.kinds)
        for i, a in enumerate(slots):
            for b in slots[i + 1:]:
                ka, kb = self.kinds[a], self.kinds[b]
                if ka.founding() != kb.founding():
                    continue
                relevant = np.maximum(ka.tenths, kb.tenths) > self.s.merge_cutoff
                if self.s.merge_context:
                    relevant[:K.OBJECT_FROM] = True
                overlap = (ka.lo - self.s.tol <= kb.hi) & (kb.lo - self.s.tol <= ka.hi)
                overlap = overlap | (np.isnan(ka.lo) | np.isnan(kb.lo))
                if np.all(overlap | ~relevant):
                    return a, b
        return None


class Frankie(Forager):
    name = "frankie"
    label = "Frankie"

    def __init__(self, seed, reserve, boldness, merge=True, context=True):
        super().__init__(seed, reserve, boldness)
        self.memory = E1Memory(Settings(merge=merge))
        self.context = context

    def values_for(self, s):
        v, known = super().values_for(s)
        if not self.context:
            v[:2] = np.nan                                  # never reads scene or host
        return v, known

    def _fed_share(self, g):
        eats = self.memory.kinds[g].eats
        return sum(1 for c, _ in eats if c == 1) / len(eats)

    def judge(self, values, known):
        kinds = self.memory.kinds
        verdict, _, log = look(kinds, values, known, self.memory.s)
        alive = [g for g, _ in log["layers"][-1]["kept"]] if log["layers"] else []
        alive.sort(key=lambda g: (log["totals"][str(g)], -len(kinds[g].eats), kinds[g].born))
        good = [g for g in alive if self._fed_share(g) >= self.bar]
        ruled = []
        for layer in log["layers"]:
            for g, _, traits in layer["out"]:
                if traits and len(kinds[g].eats) >= 1:
                    ruled.append(f"ruled out kind {g} by its {_words(traits[:3])}.")
        j = {"verdict": verdict, "candidates": alive, "leader_good": bool(alive) and alive[0] in good,
             "ruled_out": " ".join(ruled[:2])}
        if not alive:
            j["status"] = "unknown"
            j["says"] = "Nothing I know matches it." if kinds else "I don't know anything yet."
        elif len(good) == len(alive):
            j["status"] = "good"
            j["says"] = self._say(alive, "could be")
        elif not good:
            j["status"] = "bad"
            j["says"] = self._say(alive, "could be")
        else:
            j["status"] = "mixed"
            j["says"] = self._say(alive, "could be")
        return j

    def _say(self, alive, verb):
        if len(alive) == 1:
            g = alive[0]
            k = self.memory.kinds[g]
            return f"Looks like kind {g}, which {OUTCOME_WORDS[k.founding()]} ({len(k.eats)} eaten)."
        parts = [f"kind {g} ({OUTCOME_WORDS[self.memory.kinds[g].founding()]})" for g in alive[:3]]
        more = f" or {len(alive) - 3} more" if len(alive) > 3 else ""
        return f"It {verb} {', '.join(parts[:-1]) + ' or ' + parts[-1] if len(parts) > 1 else parts[0]}{more}."

    def learn(self, values, known, delta, judged):
        verdict = judged["verdict"] if isinstance(judged["verdict"], int) else "unknown"
        slot, what, merges = self.memory.write(verdict, values, delta, delta >= 0)
        words = {"new": f"Remembering it as a new kind, kind {slot}.",
                 "stretch": f"Kind {slot} was right; it now covers this one too.",
                 "split": f"Kind {verdict} was wrong about this one: splitting off kind {slot}, and paying more "
                          f"attention to what differed."}[what]
        if merges:
            words += " " + " ".join(f"Kind {a} and kind {b} look like one kind: merged into kind {b}." for a, b in merges[:2])
        if not self.context:
            pass
        return {"kind": slot, "words": words}

    def kinds_view(self):
        out = []
        for g in sorted(self.memory.kinds):
            k = self.memory.kinds[g]
            fed = sum(1 for c, _ in k.eats if c == 1)
            bad = sum(1 for c, _ in k.eats if c == -1)
            watch = [TRAIT_WORDS[t] for t in np.argsort(-k.tenths) if k.tenths[t] > K.WEIGHT_START][:3]
            out.append({"name": f"kind {g}", "outcome": OUTCOME_WORDS[k.founding()], "eats": len(k.eats),
                        "fed": fed, "poisoned": bad,
                        "note": ("watches " + ", ".join(watch)) if watch else ""})
        return out


class FrankieNoMerge(Frankie):
    name = "frankie-no-merge"
    label = "Frankie, no merging"

    def __init__(self, seed, reserve, boldness):
        super().__init__(seed, reserve, boldness, merge=False)


class FrankieNoContext(Frankie):
    name = "frankie-no-context"
    label = "Frankie, no context"

    def __init__(self, seed, reserve, boldness):
        super().__init__(seed, reserve, boldness, context=False)
