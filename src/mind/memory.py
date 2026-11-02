"""K-F's memory and its write rule: blame moves outward (section 6, D3, M10 to M15, KT-70 to KT-77).

Memory starts empty (M09). Each remembered kind keeps, for all 22 traits,
taste included (M10, M51): a stored range and a relevance weight. It also
keeps its eat record, its confirmed wins and a reliability mark.

- Weights are whole tenths from 0 to 10, starting at 5 (M20, KT-94), and
  move only by PLACEHOLDER-02's fixed steps: +2 or -1 tenths.
- Reliability is whole twentieths from 0 to 20, starting at 20 (1.0), and
  moves by +1 (0.05) or -5 (0.25) (PLACEHOLDER-05).
- Each eat on record holds its outcome's class and whether energy was at or
  above R right after it (KT-70). The class is the outcome's sign: above 0,
  exactly 0 or below 0, the outcome being the energy the item gives as it
  lands, without the look or thinking costs.
- A guess is right when its class equals that of the eat that founded the
  named kind, and a confirmed win uses the same test (KT-70, PLACEHOLDER-07).

After each eat, the write works from the verdict committed before the eat
(section 6):

- "unknown", or no settled verdict (KT-74, PLACEHOLDER-93): a brand-new kind,
  every weight 5 tenths and every range the item's value plus or minus one
  detector width, not clipped (section 6, KT-77).
- A right guess: the kind stretches exactly to include the item
  (PLACEHOLDER-06). A trait more than one detector width outside the old
  range "varied" and loses 1 tenth (M14, KT-71). Reliability rises by one
  twentieth, to at most 1.
- A wrong guess: blame starts at details, taste included, then parts, object
  and context (M11, KT-77). The first layer holding a trait more than one
  detector width outside the guessed kind's range explains it (PLACEHOLDER-03,
  KT-71). Those differing traits gain 2 tenths on the guessed kind, to at most
  10; a split child then copies the guessed kind's weights, with ranges of
  this item's values plus or minus one detector width, this eat alone on its
  record, reliability 1 and no confirmed wins (M12, PLACEHOLDER-04, KT-72).
- A wrong guess no layer explains: the guessed kind's reliability falls by 5
  twentieths, to at least 0, and the eat goes on its record; its ranges and
  weights stay as they are (M13, KT-73).
- No two kinds ever merge (KT-74).
- OS10 (section 4) stores no taste at all: none in storage, stretch, blame
  or splits (KT-77). Its kinds dump no taste range and no taste weight.
- A new kind or split child takes the lowest empty slot. When memory already
  holds 48 kinds, one is forgotten first, after a split child has copied its
  parent: the one with the fewest confirmed wins, then the oldest last
  confirmed win, then the lowest slot. Kinds with no confirmed win tie on
  their last win, so the lowest slot decides. This holds even when it picks
  the kind the verdict named (PLACEHOLDER-07, KT-75).
"""

import numpy as np

from mind import constants as K

# The layers blame walks through, innermost first (M11): (name, first trait, end); details include taste (KT-77)
BLAME_ORDER = (("details", K.DETAILS_FROM, K.N_TRAITS), ("parts", K.PARTS_FROM, K.DETAILS_FROM),
               ("object", K.OBJECT_FROM, K.PARTS_FROM), ("context", 0, K.OBJECT_FROM))

NEW = "new"
STRETCH = "stretch"
SPLIT = "split"
MARK = "mark-unreliable"
FORGET = "forget"


def outcome_class(delta_milli: int) -> int:
    """+1 for an outcome above 0, 0 for exactly 0, -1 below 0 (KT-70)."""
    if delta_milli > 0:
        return 1
    if delta_milli < 0:
        return -1
    return 0


class Kind:
    """One remembered kind (M10)."""

    def __init__(self, values, width, tenths, eat_class, above):
        self.lo = values - width                 # (section 6, PLACEHOLDER-04, KT-77)
        self.hi = values + width
        self.tenths = np.array(tenths, dtype=np.int64)
        self.reliability = K.TWENTIETHS
        self.eats = [[eat_class, bool(above)]]   # the founding eat comes first
        self.wins = 0
        self.last_win = 0                        # the write number of the last confirmed win

    def founding_class(self) -> int:
        return self.eats[0][0]

    def above_flags(self) -> list:
        return [above for _, above in self.eats]

    def reliability_share(self) -> float:
        return self.reliability / K.TWENTIETHS

    def outside(self, values, width):
        """Traits lying more than one detector width outside the stored range (PLACEHOLDER-03, KT-71)."""
        return (values < self.lo - width) | (values > self.hi + width)


class Memory:
    def __init__(self, settings, taste_blind=False):
        self.width = settings.detector_width
        self.taste_blind = taste_blind           # OS10: no taste in storage, stretch, blame or splits (KT-77)
        self.kinds = {}                          # slot -> Kind
        self.writes = 0                          # eats written so far, the clock for "oldest last win"

    def slots(self) -> list:
        return sorted(self.kinds)

    def _empty_slot(self) -> int:
        slot = 0
        while slot in self.kinds:
            slot += 1
        return slot

    def _forget_one(self) -> int:
        def order(slot):
            k = self.kinds[slot]
            return (k.wins, k.last_win, slot)
        slot = min(self.kinds, key=order)
        del self.kinds[slot]
        return slot

    def _take_slot(self, kind, events, trigger) -> int:
        while len(self.kinds) >= K.SLOTS:
            events.append(_event(FORGET, self._forget_one(), trigger))
        slot = self._empty_slot()
        self.kinds[slot] = kind
        return slot

    def write(self, verdict, values, delta_milli: int, above: bool, trigger: str) -> list:
        """Apply the write rule for one eat; returns its memory write events (KT-70 to KT-77).

        verdict is the verdict committed before the eat: a slot, "unknown" or
        "unsettled". values are the decision's 18 readings and the eat's 4
        tastes, in schema order (KT-35).
        """
        values = np.array(values, dtype=np.float64)
        if self.taste_blind:                               # OS10 stores no taste at all (KT-77)
            values[K.TASTE_FROM:] = np.nan                 # a missing taste is never outside, never stretched
        self.writes += 1
        cls = outcome_class(delta_milli)
        events = []
        if not isinstance(verdict, int):                   # "unknown", or nothing settled (KT-74, PLACEHOLDER-93)
            kind = Kind(values, self.width, np.full(K.N_TRAITS, K.WEIGHT_START), cls, above)
            slot = self._take_slot(kind, events, trigger)
            ev = _event(NEW, slot, trigger)
            ev["placeholder_93"] = trigger == "designed-exposure"
            return events + [ev]
        kind = self.kinds[verdict]
        if cls == kind.founding_class():                   # a right guess: stretch (M14, PLACEHOLDER-06)
            varied = kind.outside(values, self.width)
            kind.lo = np.minimum(kind.lo, values)
            kind.hi = np.maximum(kind.hi, values)
            old = kind.tenths.copy()
            kind.tenths = np.maximum(kind.tenths - varied * K.WEIGHT_DOWN, 0)
            kind.reliability = min(kind.reliability + K.RELIABILITY_UP, K.TWENTIETHS)
            kind.eats.append([cls, bool(above)])
            kind.wins += 1
            kind.last_win = self.writes
            return [_event(STRETCH, verdict, trigger, deltas=_deltas(verdict, old, kind.tenths))]
        outside = kind.outside(values, self.width)
        for layer, first, end in BLAME_ORDER:              # blame moves outward (M11, M12)
            differing = np.zeros(K.N_TRAITS, dtype=bool)
            differing[first:end] = outside[first:end]
            if differing.any():
                old = kind.tenths.copy()
                kind.tenths = np.minimum(kind.tenths + differing * K.WEIGHT_UP, K.TENTHS)
                child = Kind(values, self.width, kind.tenths, cls, above)        # copies the weights (KT-72)
                slot = self._take_slot(child, events, trigger)                  # forgetting comes after the copy (KT-75)
                return events + [_event(SPLIT, slot, trigger, parent=verdict, layer=layer,
                                        deltas=_deltas(verdict, old, kind.tenths))]
        kind.reliability = max(kind.reliability - K.RELIABILITY_DOWN, 0)        # unexplained (M13, KT-73)
        kind.eats.append([cls, bool(above)])
        return [_event(MARK, verdict, trigger)]

    def dump(self) -> dict:
        """memory_state_dump (KT-94): every kind's slot, 22 ranges, 22 weights in tenths, reliability and eats."""
        out = []
        for slot in self.slots():
            k = self.kinds[slot]
            stored = [not (np.isnan(lo) or np.isnan(hi)) for lo, hi in zip(k.lo, k.hi)]
            out.append({"slot": slot,
                        "ranges": [[float(lo), float(hi)] if ok else None for lo, hi, ok in zip(k.lo, k.hi, stored)],
                        "weights_tenths": [int(t) if ok else None for t, ok in zip(k.tenths, stored)],
                        "reliability": k.reliability_share(), "eats": len(k.eats)})
        return {"candidates": out}


def _deltas(slot, old, new) -> list:
    """[slot, trait, change in tenths] for every weight that moved."""
    return [[slot, t, int(new[t] - old[t])] for t in range(K.N_TRAITS) if new[t] != old[t]]


def _event(kind_of_write, slot, trigger, parent=None, layer=None, deltas=None) -> dict:
    return {"type": kind_of_write, "trigger": trigger, "slot": slot, "parent_slot": parent, "layer": layer,
            "weight_deltas": deltas or []}
