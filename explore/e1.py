"""E1: the plainest elimination mind, with kind merging (Frankie Lab, 2 Nov 2026).

An exploration, not part of the kill test. It runs through the frozen harness
(harness.run.run_one, harness.scoring.measures) behind the same interface as
K-F (decide, land, write, dump, info), so every number it gets means what it
means on the bench. It never sees anything a bench mind may not see: the 18
visible readings, its energy, and after an eat the outcome and 4 tastes.

Pieces, each labelled as the lab brief asks:

- Memory: a list of kinds. Each kind has a range per trait, a relevance per
  trait (whole tenths, starting equal at 5), and an outcome record.
  (Conventional: rule-based categories; learned relevance is close to the
  attention weights of category models such as Kruschke's ALCOVE, 1992.)
- Looking: elimination, outside in. (Untested as a mind: Aitzaz's
  foundation.) Every kind starts as a candidate. Layer by layer (context,
  object, parts, details; after an eat the 4 tastes join details), each
  surviving candidate adds up its relevance-weighted misses. A miss is a
  reading more than TOL noise widths outside the kind's range. A candidate
  is eliminated once its running total passes the elimination threshold
  ("absolute"), or, in the "relative" variant, once it trails the best
  surviving candidate by more than that much. No survivor: "unknown". One:
  named. Several after details: the fewest weighted misses, then the most
  eats, then the oldest. The log records which layer eliminated which kind.
  With "outside_in" off, every layer is checked at once and elimination
  happens once, at the end.
- After eating, from the verdict committed before the eat:
  - "unknown": a new kind, ranges at the item's values. (Conventional.)
  - the named kind's founding outcome matches: stretch its ranges over the
    item, and lower by one tenth the relevance of each trait that had to
    widen by more than WIDEN noise widths. (Conventional.)
  - it doesn't: split. Raise by two tenths the parent's relevance on every
    trait where the item lies more than TOL outside the parent's range, and
    start a new kind from the item with the parent's raised relevance.
    (K-F's blame idea, without its layer order. Untested.)
- Merging, after every write. (Conventional, like merging clusters.) Two kinds
  with the same founding outcome merge when their ranges overlap, within
  TOL, on every trait whose relevance in either is above MERGE_CUTOFF. The
  merged kind takes the union of the ranges, the higher relevance per trait
  and both records. The kind the eat was just filed under survives a merge
  it is part of; otherwise the older survives. The frozen harness has no
  merge event (KT-74), so the absorbed kind is reported to it as a forget;
  E1's own log keeps the merge for the Lab's display.
  Two switches added while exploring (both untested): with merge_context on,
  the context traits (scene and host) must always overlap for a merge, so
  kinds met in different places never merge, whatever their relevance (the
  outermost layer limits the rest). With merge_widen on, a merge lowers the
  relevance of every trait the merge widened by more than WIDEN noise widths,
  as a stretch does: traits that vary within a kind matter less.
- Choosing: the bench drive, unchanged (mind.drive, the copy the harness tests
  against B1n-mind's), with reliability always 1. Thinking costs 0.001 per
  check (B14), a check being one candidate on one trait, like TW7.

Not used, as the brief rules: gradient descent, nearest-neighbour matching,
any language model, and anything that reads the generator's hidden essence.

The frozen protocol lets a tower mind report its neuron type only as
"spiking" or "rate". E1 has no neurons at all; it reports "rate" because its
verdicts come from graded totals, never spikes.
"""

import numpy as np

from mind import constants as K
from mind.drive import EAT, choose, share_above, thinking_milli

N = K.N_TRAITS
VISIBLE = K.N_VISIBLE
LAYERS = (("context", 0, K.OBJECT_FROM), ("object", K.OBJECT_FROM, K.PARTS_FROM),
          ("parts", K.PARTS_FROM, K.DETAILS_FROM), ("details", K.DETAILS_FROM, K.TASTE_FROM))
CHOSEN, DESIGNED = "chosen-eat", "designed-exposure"


class Params:
    """One E1 variant. Every number is one value for every trait and layer."""

    def __init__(self, name="E1", tol_nw=3.0, threshold=1.0, widen_nw=10.0, split_up=2, stretch_down=1,
                 merge=True, merge_cutoff=4, outside_in=True, elimination="absolute", merge_context=False,
                 merge_widen=False):
        self.name = name
        self.tol_nw = tol_nw                    # a miss: more than this many noise widths outside a range
        self.tol = tol_nw * K.NOISE_WIDTH
        self.threshold = threshold              # weighted misses (relevance units) that eliminate
        self.widen_nw = widen_nw                # a stretch wider than this lowers that trait's relevance
        self.widen = widen_nw * K.NOISE_WIDTH
        self.split_up = split_up                # tenths a split adds on the traits that differed
        self.stretch_down = stretch_down        # tenths a big stretch takes off
        self.merge = merge
        self.merge_cutoff = merge_cutoff        # tenths: a trait above this must overlap for two kinds to merge
        self.outside_in = outside_in
        if elimination not in ("absolute", "relative"):
            raise ValueError("elimination is 'absolute' or 'relative'")
        self.elimination = elimination
        self.merge_context = merge_context      # untested: the outermost layer (scene, host) must always overlap
        self.merge_widen = merge_widen          # untested: a merge lowers relevance where it widens, like a stretch

    def table(self):
        return {"tol_nw": self.tol_nw, "threshold": self.threshold, "widen_nw": self.widen_nw,
                "split_up": self.split_up, "stretch_down": self.stretch_down, "merge": self.merge,
                "merge_cutoff": self.merge_cutoff, "outside_in": self.outside_in,
                "elimination": self.elimination, "merge_context": self.merge_context,
                "merge_widen": self.merge_widen}

    @classmethod
    def from_params(cls, given):
        known = set(cls().table()) | {"name"}
        if not set(given) <= known:
            raise ValueError(f"E1 takes no setting {sorted(set(given) - known)}")
        return cls(**given)


def outcome_class(delta_milli):
    return 1 if delta_milli > 0 else (-1 if delta_milli < 0 else 0)


class Kind:
    def __init__(self, values, tenths, cls, above, born):
        self.lo = np.array(values, dtype=np.float64)
        self.hi = np.array(values, dtype=np.float64)
        self.tenths = np.array(tenths, dtype=np.int64)
        self.eats = [[cls, bool(above)]]
        self.born = born                         # creation order, for "the older"

    def founding(self):
        return self.eats[0][0]


class Memory:
    def __init__(self, p):
        self.p = p
        self.kinds = {}
        self.born = 0

    def _slot(self):
        s = 0
        while s in self.kinds:
            s += 1
        return s

    def add(self, kind):
        slot = self._slot()
        self.kinds[slot] = kind
        return slot

    def new_kind(self, values, tenths, cls, above):
        self.born += 1
        return self.add(Kind(values, tenths, cls, above, self.born))

    def outside(self, kind, values, known):
        """Per trait, how far the reading lies outside the kind's range (0 inside), for known traits."""
        gap = np.maximum(kind.lo - values, 0.0) + np.maximum(values - kind.hi, 0.0)
        gap[known:] = 0.0
        return gap


def look(memory, values, known, p):
    """One verdict by elimination (see the module docstring). Returns (verdict, checks, log)."""
    slots = sorted(memory.kinds)
    layers = [list(range(a, b)) for _, a, b in LAYERS]
    if known > VISIBLE:
        layers[3] = layers[3] + list(range(K.TASTE_FROM, K.N_TRAITS))
    names = [n for n, _, _ in LAYERS]
    totals = {s: 0.0 for s in slots}
    missed = {s: [] for s in slots}
    alive = list(slots)
    log = {"layers": [], "eliminated": {}}
    checks = 0
    stages = list(zip(names, layers)) if p.outside_in else [("all", [t for ts in layers for t in ts])]
    for name, traits in stages:
        entering = list(alive)
        for s in alive:
            k = memory.kinds[s]
            gap = memory.outside(k, values, known)
            for t in traits:
                checks += 1
                if gap[t] > p.tol:
                    totals[s] += k.tenths[t] / K.TENTHS
                    missed[s].append(t)
        if p.elimination == "absolute":
            out = [s for s in alive if totals[s] > p.threshold]
        else:
            best = min((totals[s] for s in alive), default=0.0)
            out = [s for s in alive if totals[s] - best > p.threshold]
        alive = [s for s in alive if s not in out]
        for s in out:
            log["eliminated"][str(s)] = name
        log["layers"].append({"layer": name, "traits": traits, "entering": entering,
                              "out": [[s, round(totals[s], 6), [t for t in missed[s] if t in traits]] for s in out],
                              "kept": [[s, round(totals[s], 6)] for s in alive]})
    if not alive:
        verdict = "unknown"
    else:
        alive.sort(key=lambda s: (totals[s], -len(memory.kinds[s].eats), memory.kinds[s].born))
        verdict = alive[0]
        log["tie"] = len(alive) > 1 and totals[alive[0]] == totals[alive[1]]
    log["totals"] = {str(s): round(v, 6) for s, v in totals.items()}
    log["missed"] = {str(s): v for s, v in missed.items()}
    return verdict, checks, log


class E1:
    def __init__(self, config):
        params = dict(config.get("params", {}))
        params.pop("mind", None)
        self.p = Params.from_params(params)
        self.reserve_milli = int(config["reserve_milli"])
        self.boldness = float(config["boldness"])
        self.memory = Memory(self.p)
        self.pending = None
        self.landed = None
        self.untried_milli = 0
        self.untried_eats = 0

    def _tally(self):
        return None if self.untried_eats == 0 else self.untried_milli / self.untried_eats / K.MILLI_PER_UNIT

    def decide(self, visible, energy_milli):
        values = np.zeros(N)
        values[:VISIBLE] = np.asarray(visible, dtype=np.float64)
        verdict, checks, log = look(self.memory, values, VISIBLE, self.p)
        cost = thinking_milli(checks, K.CHECK_NANO)
        named = isinstance(verdict, int)
        share = reliability = None
        if named:
            share, reliability = share_above([a for _, a in self.memory.kinds[verdict].eats]), 1.0
        trace, provenance = choose(named, share, reliability, int(energy_milli), cost, self.reserve_milli,
                                   self.boldness, self._tally())
        self.pending = {"values": values, "verdict": verdict, "pick": trace["pick"]}
        self.landed = None
        log["checks"] = checks
        return {"action": trace["pick"], "verdict": verdict, "settle_step": len(log["layers"]),
                "thinking": {"unit": "check", "count": checks, "cost_milli": cost}, "drive": trace,
                "provenance": provenance, "log": log}

    def land(self, delta_milli, energy_after_milli, taste):
        if self.pending is None:
            raise ValueError("an eat landed with no decision before it")
        values = self.pending["values"].copy()
        values[K.TASTE_FROM:] = np.asarray(taste, dtype=np.float64)
        verdict, _, log = look(self.memory, values, N, self.p)
        self.landed = {"values": values, "delta": int(delta_milli),
                       "above": int(energy_after_milli) >= self.reserve_milli}
        return {"verdict": verdict, "settle_step": len(log["layers"]), "log": log}

    def write(self):
        if self.pending is None or self.landed is None:
            raise ValueError("a memory write needs a decision and its eat")
        verdict, values = self.pending["verdict"], self.landed["values"]
        trigger = CHOSEN if self.pending["pick"] == EAT else DESIGNED
        cls, above = outcome_class(self.landed["delta"]), self.landed["above"]
        m, p = self.memory, self.p
        events, own = [], {"kind": None, "merges": []}
        if not isinstance(verdict, int):
            slot = m.new_kind(values, np.full(N, K.WEIGHT_START), cls, above)
            events.append(_event("new", slot, trigger, placeholder_93=trigger == DESIGNED))
            own["kind"] = "new"
            self.untried_milli += self.landed["delta"]
            self.untried_eats += 1
        else:
            kind = m.kinds[verdict]
            old = kind.tenths.copy()
            if cls == kind.founding():
                widened = np.maximum(kind.lo - values, 0.0) + np.maximum(values - kind.hi, 0.0)
                kind.lo = np.minimum(kind.lo, values)
                kind.hi = np.maximum(kind.hi, values)
                kind.tenths = np.maximum(kind.tenths - (widened > p.widen) * p.stretch_down, 0)
                kind.eats.append([cls, bool(above)])
                slot = verdict
                events.append(_event("stretch", slot, trigger, deltas=_deltas(slot, old, kind.tenths)))
                own["kind"] = "stretch"
            else:
                differ = m.outside(kind, values, N) > p.tol
                kind.tenths = np.minimum(kind.tenths + differ * p.split_up, K.TENTHS)
                slot = m.new_kind(values, kind.tenths, cls, above)
                events.append(_event("split", slot, trigger, parent=verdict,
                                     deltas=_deltas(verdict, old, kind.tenths)))
                own["kind"] = "split"
        if p.merge:
            slot = self._merge(slot, events, trigger, own)
        own["filed"] = slot
        self.pending = self.landed = None
        return {"events": events, "log": own}

    def _merge(self, filed, events, trigger, own):
        m, p = self.memory, self.p
        while True:
            pair = None
            slots = sorted(m.kinds)
            for i, a in enumerate(slots):
                for b in slots[i + 1:]:
                    ka, kb = m.kinds[a], m.kinds[b]
                    if ka.founding() != kb.founding():
                        continue
                    relevant = np.maximum(ka.tenths, kb.tenths) > p.merge_cutoff
                    if p.merge_context:
                        relevant[:K.OBJECT_FROM] = True
                    overlap = (ka.lo - p.tol <= kb.hi) & (kb.lo - p.tol <= ka.hi)
                    if np.all(overlap | ~relevant):
                        pair = (a, b)
                        break
                if pair:
                    break
            if pair is None:
                return filed
            a, b = pair
            if filed in pair:
                keep = filed
            else:
                keep = a if m.kinds[a].born < m.kinds[b].born else b
            gone = b if keep == a else a
            kk, kg = m.kinds[keep], m.kinds[gone]
            lo, hi = np.minimum(kk.lo, kg.lo), np.maximum(kk.hi, kg.hi)
            tenths = np.maximum(kk.tenths, kg.tenths)
            if p.merge_widen:                    # traits that vary across the two kinds matter less (untested)
                widened = np.maximum((hi - lo) - np.maximum(kk.hi - kk.lo, kg.hi - kg.lo), 0.0)
                tenths = np.maximum(tenths - (widened > p.widen) * p.stretch_down, 0)
            kk.lo, kk.hi, kk.tenths = lo, hi, tenths
            kk.eats = kk.eats + kg.eats
            del m.kinds[gone]
            events.append(_event("forget", gone, trigger))
            own["merges"].append([gone, keep])

    def dump(self):
        out = []
        for slot in sorted(self.memory.kinds):
            k = self.memory.kinds[slot]
            out.append({"slot": slot, "ranges": [[float(a), float(b)] for a, b in zip(k.lo, k.hi)],
                        "weights_tenths": [int(t) for t in k.tenths], "reliability": 1.0, "eats": len(k.eats),
                        "log": {"record": [c for c, _ in k.eats], "born": k.born}})
        return {"candidates": out}

    def info(self):
        table = {name: [value if isinstance(value, (int, float)) and not isinstance(value, bool) else
                        (1 if value is True else 0 if value is False else None), f"E1 {name} (explore/e1.py)"]
                 for name, value in self.p.table().items()}
        table["detector_width_nw"] = [self.p.tol_nw, "E1 miss tolerance (explore/e1.py), read as the detector width"]
        table["unit_nano"] = [K.CHECK_NANO, "B14, KT-46"]
        return {"version": [dict(v) for v in version_of(self.p.name)], "constants": table,
                "chooser": "satisficing", "neuron": "rate", "log": {"variant": self.p.name}}


def version_of(name):
    return [dict(K.OS07), {"switch": "E1", "setting": name, "scope": "lifetime"}]


def _deltas(slot, old, new):
    return [[slot, t, int(new[t] - old[t])] for t in range(N) if new[t] != old[t]]


def _event(kind, slot, trigger, parent=None, deltas=None, placeholder_93=None):
    e = {"type": kind, "trigger": trigger, "slot": slot, "parent_slot": parent, "layer": None,
         "weight_deltas": deltas or []}
    if placeholder_93 is not None:
        e["placeholder_93"] = placeholder_93
    return e


def make(config):
    return E1(config)
