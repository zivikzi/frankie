"""E1: the elimination mind with kind merging (kill-test/E1_ADDENDUM.md, KT-132 to KT-138).

E1 was found by exploration on the tuning set after K-F's Week 4 check
(explore/, explore/results/variants.jsonl). It runs behind the same interface
as K-F (decide, land, write, dump, info) and is told only what every bench
mind is told: the 18 visible readings and its energy before each decision,
and after an eat the outcome, the energy after it and the 4 tastes.

Pieces, each labelled:

- Memory: a list of kinds. Each kind has a range per trait, a relevance per
  trait (whole tenths, starting equal at 5, M20) and its eat record.
  (Conventional: rule-based categories; learned relevance is close to the
  attention weights of category models such as Kruschke's ALCOVE, 1992.)
- Looking: elimination, outside in. (Untested as a mind.) Every kind starts
  as a candidate. Layer by layer (context, object, parts, details; after an
  eat the 4 tastes join details), each surviving candidate adds up its
  relevance-weighted misses, a miss being a reading more than TOL noise
  widths outside the kind's range. A candidate is eliminated once its
  running total passes the elimination threshold. No survivor: "unknown".
  Several after details: the fewest weighted misses, then the most eats, then
  the oldest. The log records which layer eliminated which kind.
- After eating, from the verdict committed before the eat:
  - "unknown": a new kind at the item's values. (Conventional.)
  - the named kind's founding outcome matches: stretch it over the item; a
    trait that had to widen by more than WIDEN noise widths loses relevance.
    (Conventional.)
  - it doesn't: split. The parent's relevance rises on every trait where the
    item lies more than TOL outside its range, and a new kind starts from the
    item with the parent's raised relevance. (K-F's blame idea without its
    layer order. Untested.)
- Merging, after every write. (Conventional, like merging clusters.) Two
  kinds with the same founding outcome merge when their ranges overlap,
  within TOL, on the context traits (always: the outermost layer limits the
  rest; untested) and on every other trait whose relevance in either is
  above the merge cut-off. The merged kind takes the union of the ranges, the
  higher relevance per trait and both records, and a trait the merge widened
  by more than WIDEN noise widths loses relevance (untested). The older kind
  survives.
- Taste keeps its relevance (KT-135; untested): widening lowers relevance on
  the 18 visible traits only, never on the 4 tastes. A kind's tastes vary,
  but how it usually tastes is what lets a surprising taste stand out.
- Choosing: the bench drive unchanged (mind.drive), with reliability always
  1. Thinking costs 0.001 per check (B14), a check being one candidate on one
  trait.

E1-OS10 (section 4's OS10, KT-136) stores no taste at all and reads none in
the verdict after eating.

The frozen harness knows no merge (KT-74). An eat whose own kind is absorbed
into an older kind in the same write is reported as a stretch of that older
kind, which is where the eat now sits; any other kind absorbed is reported
as a forget (KT-133). The frozen protocol lets a tower mind report its
neuron type only as "spiking" or "rate": E1 has no neurons and reports
"rate", its verdicts coming from weighted totals (KT-134).

Not used: weights fitted by error slopes, nearest-neighbour matching, any language model,
anything that reads the generator's hidden labels.
"""

import numpy as np

from mind import constants as K
from mind.drive import EAT, choose, share_above, thinking_milli

E1_TOL_NW = 10            # a miss: a reading more than this many noise widths outside a range (KT-132)
E1_THRESHOLD = 1.0        # relevance-weighted misses, in relevance units, that eliminate a kind (KT-132)
E1_WIDEN_NW = 10          # widening a trait by more than this many noise widths lowers its relevance (KT-132)
E1_SPLIT_UP = 2           # tenths a split adds on each trait that differed (KT-132)
E1_STRETCH_DOWN = 5       # tenths a big widening takes off a trait (KT-132)
E1_MERGE_CUTOFF = 5       # tenths: a trait above this must overlap for two kinds to merge (KT-132)

N = K.N_TRAITS
VISIBLE = K.N_VISIBLE
LAYERS = (("context", 0, K.OBJECT_FROM), ("object", K.OBJECT_FROM, K.PARTS_FROM),
          ("parts", K.PARTS_FROM, K.DETAILS_FROM), ("details", K.DETAILS_FROM, K.TASTE_FROM))
CHOSEN, DESIGNED = "chosen-eat", "designed-exposure"
E1 = "E1"
OS10_RECORD = {"switch": "OS10", "setting": None, "scope": "lifetime"}     # (section 4, KT-49, KT-136)
NUMBERS = ("tol_nw", "threshold", "widen_nw", "split_up", "stretch_down", "merge_cutoff")
SWITCHES = ("merge", "outside_in", "merge_context", "merge_widen", "taste_keeps")
BIRTH = ("mind", "name", "OS10")


class Settings:
    """One E1 version. The defaults are E1 as frozen (KT-132); the reported versions switch one idea off."""

    def __init__(self, tol_nw=E1_TOL_NW, threshold=E1_THRESHOLD, widen_nw=E1_WIDEN_NW, split_up=E1_SPLIT_UP,
                 stretch_down=E1_STRETCH_DOWN, merge_cutoff=E1_MERGE_CUTOFF, merge=True, outside_in=True,
                 merge_context=True, merge_widen=True, taste_keeps=True):
        self.tol_nw = tol_nw
        self.tol = tol_nw * K.NOISE_WIDTH
        self.threshold = threshold
        self.widen_nw = widen_nw
        self.widen = widen_nw * K.NOISE_WIDTH
        self.split_up = split_up
        self.stretch_down = stretch_down
        self.merge = merge
        self.merge_cutoff = merge_cutoff
        self.outside_in = outside_in
        self.merge_context = merge_context
        self.merge_widen = merge_widen
        self.taste_keeps = taste_keeps

    @classmethod
    def from_params(cls, params):
        given = {k: v for k, v in params.items() if k not in BIRTH}
        unknown = sorted(set(given) - set(NUMBERS) - set(SWITCHES))
        if unknown:
            raise ValueError(f"E1 takes no setting {unknown}")
        for k, v in given.items():
            if k in SWITCHES and not isinstance(v, bool):
                raise ValueError(f"{k} is a switch: true or false")
            if k in NUMBERS and (isinstance(v, bool) or not isinstance(v, (int, float)) or not np.isfinite(v)
                                 or v < 0):
                raise ValueError(f"{k} must be one finite number, 0 or more")
        return cls(**given)

    def table(self):
        out = {}
        for k in NUMBERS:
            out[k] = [float(self._get(k)), "KT-132"]
        for k in SWITCHES:
            out[k] = [1 if self._get(k) else 0, "KT-132"]
        return out

    def _get(self, k):
        return {"tol_nw": self.tol_nw, "threshold": self.threshold, "widen_nw": self.widen_nw,
                "split_up": self.split_up, "stretch_down": self.stretch_down, "merge_cutoff": self.merge_cutoff,
                "merge": self.merge, "outside_in": self.outside_in, "merge_context": self.merge_context,
                "merge_widen": self.merge_widen, "taste_keeps": self.taste_keeps}[k]


def outcome_class(delta_milli):
    return 1 if delta_milli > 0 else (-1 if delta_milli < 0 else 0)


class Kind:
    def __init__(self, values, tenths, cls, above, born):
        self.lo = np.array(values, dtype=np.float64)
        self.hi = np.array(values, dtype=np.float64)
        self.tenths = np.array(tenths, dtype=np.int64)
        self.eats = [[cls, bool(above)]]
        self.born = born                         # creation order: "the older"

    def founding(self):
        return self.eats[0][0]


def outside(kind, values, known):
    """Per trait, how far the reading lies outside the kind's range (0 inside), for known traits only."""
    gap = np.maximum(kind.lo - values, 0.0) + np.maximum(values - kind.hi, 0.0)
    gap[known:] = 0.0
    return np.where(np.isnan(gap), 0.0, gap)


def look(kinds, values, known, s):
    """One verdict by elimination. Returns (verdict, checks, log)."""
    slots = sorted(kinds)
    layers = [list(range(a, b)) for _, a, b in LAYERS]
    if known > VISIBLE:
        layers[-1] = layers[-1] + list(range(K.TASTE_FROM, N))
    names = [n for n, _, _ in LAYERS]
    totals = {g: 0.0 for g in slots}
    missed = {g: [] for g in slots}
    alive = list(slots)
    log = {"layers": [], "eliminated": {}}
    checks = 0
    stages = list(zip(names, layers)) if s.outside_in else [("all", [t for ts in layers for t in ts])]
    for name, traits in stages:
        entering = list(alive)
        for g in alive:
            k = kinds[g]
            gap = outside(k, values, known)
            for t in traits:
                checks += 1
                if gap[t] > s.tol:
                    totals[g] += k.tenths[t] / K.TENTHS
                    missed[g].append(t)
        out = [g for g in alive if totals[g] > s.threshold]
        alive = [g for g in alive if g not in out]
        for g in out:
            log["eliminated"][str(g)] = name
        log["layers"].append({"layer": name, "traits": traits, "entering": entering,
                              "out": [[g, totals[g], [t for t in missed[g] if t in traits]] for g in out],
                              "kept": [[g, totals[g]] for g in alive]})
    if not alive:
        verdict = "unknown"
    else:
        alive.sort(key=lambda g: (totals[g], -len(kinds[g].eats), kinds[g].born))
        verdict = alive[0]
        log["tie"] = len(alive) > 1 and totals[alive[0]] == totals[alive[1]]
    log["totals"] = {str(g): v for g, v in totals.items()}
    log["missed"] = {str(g): v for g, v in missed.items()}
    return verdict, checks, log


class E1Mind:
    def __init__(self, config):
        params = dict(config.get("params", {}))
        self.s = Settings.from_params(params)
        self.name = params.get("name", E1)
        self.blind = bool(params.get("OS10"))
        self.reserve_milli = int(config["reserve_milli"])
        self.boldness = float(config["boldness"])
        self.kinds = {}
        self.born = 0
        self.pending = None
        self.landed = None
        self.untried_milli = 0
        self.untried_eats = 0

    def _tally(self):
        return None if self.untried_eats == 0 else self.untried_milli / self.untried_eats / K.MILLI_PER_UNIT

    # ------------------------------------------------------------ the interface

    def decide(self, visible, energy_milli):
        values = np.zeros(N)
        values[:VISIBLE] = np.asarray(visible, dtype=np.float64)
        verdict, checks, log = look(self.kinds, values, VISIBLE, self.s)
        cost = thinking_milli(checks, K.CHECK_NANO)
        named = isinstance(verdict, int)
        share = reliability = None
        if named:
            share, reliability = share_above([a for _, a in self.kinds[verdict].eats]), 1.0
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
        values[K.TASTE_FROM:] = np.nan if self.blind else np.asarray(taste, dtype=np.float64)
        verdict, _, log = look(self.kinds, values, VISIBLE if self.blind else N, self.s)
        self.landed = {"values": values, "delta": int(delta_milli),
                       "above": int(energy_after_milli) >= self.reserve_milli}
        return {"verdict": verdict, "settle_step": len(log["layers"]), "log": log}

    def _lower(self, tenths, widened):
        """A trait widened by more than WIDEN loses relevance; with taste_keeps, the tastes never do (KT-135)."""
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

    def write(self):
        if self.pending is None or self.landed is None:
            raise ValueError("a memory write needs a decision and its eat")
        verdict, values = self.pending["verdict"], self.landed["values"]
        trigger = CHOSEN if self.pending["pick"] == EAT else DESIGNED
        cls, above = outcome_class(self.landed["delta"]), self.landed["above"]
        before = {g: k.tenths.copy() for g, k in self.kinds.items()}
        own = {"kind": None, "merges": [], "parent": None}
        if not isinstance(verdict, int):
            slot = self._new(values, np.full(N, K.WEIGHT_START), cls, above)
            own["kind"] = "new"
            self.untried_milli += self.landed["delta"]
            self.untried_eats += 1
        else:
            kind = self.kinds[verdict]
            if cls == kind.founding():
                widened = np.maximum(kind.lo - values, 0.0) + np.maximum(values - kind.hi, 0.0)
                widened = np.where(np.isnan(widened), 0.0, widened)
                kind.lo = np.minimum(kind.lo, values)       # a missing taste stays missing (OS10)
                kind.hi = np.maximum(kind.hi, values)
                kind.tenths = self._lower(kind.tenths, widened)
                kind.eats.append([cls, bool(above)])
                slot = verdict
                own["kind"] = "stretch"
            else:
                differ = outside(kind, values, VISIBLE if self.blind else N) > self.s.tol
                kind.tenths = np.minimum(kind.tenths + differ * self.s.split_up, K.TENTHS)
                slot = self._new(values, kind.tenths, cls, above)
                own["kind"], own["parent"] = "split", verdict
        made = slot if own["kind"] in ("new", "split") else None
        absorbed = []
        if self.s.merge:
            slot, absorbed = self._merge(slot, own)
        return self._report(slot, made, absorbed, own, before, trigger)

    def _merge(self, slot, own):
        """Merge until no pair qualifies. Returns the slot now holding the eat, and every kind absorbed."""
        absorbed = []
        while True:
            pair = self._pair()
            if pair is None:
                return slot, absorbed
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
            absorbed.append(gone)
            own["merges"].append([gone, keep])
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

    def _report(self, slot, made, absorbed, own, before, trigger):
        """The write in the frozen harness's words: new, stretch, split and forget (KT-74, KT-133)."""
        deltas = []
        for g in sorted(self.kinds):
            old = before.get(g)
            if old is not None:
                deltas += [[g, t, int(self.kinds[g].tenths[t] - old[t])] for t in range(N)
                           if self.kinds[g].tenths[t] != old[t]]
        own_absorbed = made is not None and made in absorbed
        if own_absorbed:                                    # its own new kind or split child merged away
            filing = _event("stretch", slot, trigger, deltas=deltas)
        elif own["kind"] == "new":
            filing = _event("new", slot, trigger, deltas=deltas, placeholder_93=trigger == DESIGNED)
        elif own["kind"] == "split":
            filing = _event("split", slot, trigger, parent=own["parent"], deltas=deltas)
        else:
            filing = _event("stretch", slot, trigger, deltas=deltas)
        forgets = [_event("forget", g, trigger) for g in absorbed if g != made]
        own["filed"] = slot
        self.pending = self.landed = None
        return {"events": [filing] + forgets, "log": own}

    def dump(self):
        out = []
        for g in sorted(self.kinds):
            k = self.kinds[g]
            stored = [not (np.isnan(a) or np.isnan(b)) for a, b in zip(k.lo, k.hi)]
            out.append({"slot": g,
                        "ranges": [[float(a), float(b)] if ok else None for a, b, ok in zip(k.lo, k.hi, stored)],
                        "weights_tenths": [int(t) if ok else None for t, ok in zip(k.tenths, stored)],
                        "reliability": 1.0, "eats": len(k.eats),
                        "log": {"record": [c for c, _ in k.eats], "born": k.born}})
        return {"candidates": out}

    def info(self):
        table = self.s.table()
        table["detector_width_nw"] = [self.s.tol_nw, "KT-132: E1's miss tolerance, read as its detector width"]
        table["unit_nano"] = [K.CHECK_NANO, "B14, KT-46"]
        return {"version": version_of(self.name, self.blind), "constants": table, "chooser": "satisficing",
                "neuron": "rate", "log": {"version": self.name}}


def version_of(name=E1, blind=False):
    out = [dict(K.OS07), {"switch": "E1", "setting": name, "scope": "lifetime"}]
    if blind:
        out.append(dict(OS10_RECORD))
    return out


def _event(kind, slot, trigger, parent=None, deltas=None, placeholder_93=None):
    e = {"type": kind, "trigger": trigger, "slot": slot, "parent_slot": parent, "layer": None,
         "weight_deltas": deltas or []}
    if placeholder_93 is not None:
        e["placeholder_93"] = placeholder_93
    return e


def make(config):
    return E1Mind(config)
