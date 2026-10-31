"""The stub mind: a tower-shaped fixture for the harness and the automatic mind checks.

It speaks the tower interface (harness/protocol.py) the way K-F will, so the
harness, scoring and the mind checks can be tested before K-F exists. Its
inner workings are deliberately crude and are not a design for K-F: it is a
range matcher chosen only because it is easy to check by hand.

- Each candidate stores, per trait, a range: the readings it was filed with,
  widened by the detector width. Every weight is 5 tenths and never moves.
- An object names the candidate with the most visible traits inside its
  ranges, if that is at least NAME_MIN of the 18. Two candidates tied on that
  number leave it "unsettled"; none reaching it leaves it "unknown".
- After an eat, a named candidate whose record agrees with the outcome is
  stretched; one whose record disagrees gets a split child. Anything else is
  a new candidate, in the lowest empty slot. Past max_slots candidates, the
  one with the fewest eats is forgotten first (lowest slot on a tie).
- The drive is section 5's, written out here for the fixture alone.

Variants, set by params["variant"] at birth:

- "taste-blind" (the default): no taste is stored, so it can never be
  classed as noticing the taste (section 7, step 5's last test).
- "taste-aware": it stores taste ranges, and an eat whose taste falls
  outside the named candidate's taste ranges is a split. It is the positive
  control for TASTE-NOTICED.

Other params, each breaking or stressing one thing for a test:

- max_slots lowers the slot cap, so forgetting happens;
- restless makes every look change the mind's state (the check-order test
  must still pass; the outcome-intercepted check must catch it);
- preloaded gives it one candidate at birth (the empty-at-birth check must
  catch it);
- uneven starts each new candidate's first weight at 6 tenths (the
  equal-weights check must catch it).

It imports NumPy alone and passes the import guard and the scans, like the
mind package must.
"""

import numpy as np

VISIBLE = 18                 # the 18 visible traits, in schema order (KT-01)
TASTE_TRAITS = 4             # the 4 taste traits, which arrive only after an eat (KT-01)
NOISE_WIDTH = 0.01           # one noise width (PLACEHOLDER-45)
DETECTOR_WIDTH_NW = 3        # the stub's detector width, in noise widths (KT-93, the stub's own)
NAME_MIN = 15                # traits inside a candidate's ranges needed to name it (KT-93, the stub's own)
MAX_SLOTS = 64               # candidates kept before the fewest-eats one is forgotten (KT-93, the stub's own)
WEIGHT_TENTHS = 5            # every relevance weight starts at 0.5 (M20, KT-94)
UNEVEN_TENTHS = 6            # the "uneven" variant's first weight (KT-93, the stub's own)
AGREE_SHARE = 0.5            # a record agrees with a good outcome at this share of good eats (KT-93, the stub's own)
SPIKE_NANO = 100_000         # the stub's per-spike cost, 0.0001 of energy (KT-92, the stub's own)
NANO_PER_MILLI = 1_000_000   # (KT-92)
HALF_MILLI_NANO = 500_000    # half a milli-unit: costs round halves up (KT-92)
SETTLE_NAMED = 4             # the step a named verdict settles at (KT-93, the stub's own)
SETTLE_UNKNOWN = 7           # the step an "unknown" verdict settles at (KT-93, the stub's own)
BAR_TOP = 0.9                # the drive's bar is 0.9 - 0.3 x b (PLACEHOLDER-27)
BAR_SLOPE = 0.3              # (PLACEHOLDER-27)
WRONG_FACTOR_TOP = 2.0       # eat's chance = 1 - (1 - share) x (2 - reliability) (PLACEHOLDER-05)
RELIABILITY = 1.0            # the stub never marks a candidate less reliable (KT-93, the stub's own)
OS07 = {"switch": "OS07", "setting": "habits off", "scope": "lifetime"}


def _cost_milli(spikes):
    return (spikes * SPIKE_NANO + HALF_MILLI_NANO) // NANO_PER_MILLI


class Candidate:
    def __init__(self, reading, taste, above, aware):
        w = DETECTOR_WIDTH_NW * NOISE_WIDTH
        self.lo = reading - w
        self.hi = reading + w
        self.taste_lo = taste - w if aware else None
        self.taste_hi = taste + w if aware else None
        self.eats = [above]
        self.weights = [WEIGHT_TENTHS] * VISIBLE

    def inside(self, visible):
        return int(np.sum((visible >= self.lo) & (visible <= self.hi)))

    def stretch(self, reading, taste, above):
        w = DETECTOR_WIDTH_NW * NOISE_WIDTH
        self.lo = np.minimum(self.lo, reading - w)
        self.hi = np.maximum(self.hi, reading + w)
        if self.taste_lo is not None:
            self.taste_lo = np.minimum(self.taste_lo, taste - w)
            self.taste_hi = np.maximum(self.taste_hi, taste + w)
        self.eats.append(above)

    def share(self):
        return sum(1 for e in self.eats if e) / len(self.eats)

    def taste_outside(self, taste):
        if self.taste_lo is None:
            return False
        return bool(np.any((taste < self.taste_lo) | (taste > self.taste_hi)))


class StubMind:
    def __init__(self, config):
        params = config["params"]
        self.reserve_milli = int(config["reserve_milli"])
        self.boldness = float(config["boldness"])
        self.trait_order = list(config["trait_order"])
        self.aware = params.get("variant", "taste-blind") == "taste-aware"
        self.max_slots = int(params.get("max_slots", MAX_SLOTS))
        self.restless = bool(params.get("restless", False))
        self.uneven = bool(params.get("uneven", False))
        self.looks = 0
        self.slots = {}
        self.pending = None
        self.landed = None
        self.trigger_pick = None
        if params.get("preloaded", False):
            self.slots[0] = Candidate(np.full(VISIBLE, AGREE_SHARE), np.full(TASTE_TRAITS, AGREE_SHARE), True,
                                      self.aware)

    # ------------------------------------------------------------ recognition

    def _recognise(self, visible):
        hits = [(slot, c.inside(visible)) for slot, c in sorted(self.slots.items())]
        spikes = VISIBLE * len(hits)
        if not hits:
            return "unknown", SETTLE_UNKNOWN, spikes, None, []
        best = max(n for _, n in hits)
        leaders = [slot for slot, n in hits if n == best]
        near = [slot for slot, n in hits if n >= best - 1 and slot != leaders[0]]
        if best < NAME_MIN:
            return "unknown", SETTLE_UNKNOWN, spikes, leaders[0], near
        if len(leaders) > 1:
            return "unsettled", None, spikes, leaders[0], near
        return leaders[0], SETTLE_NAMED, spikes, leaders[0], near

    # ------------------------------------------------------------ the drive

    def _drive(self, verdict, energy_milli, thinking_milli):
        bar = BAR_TOP - BAR_SLOPE * self.boldness
        skip = 1.0 if energy_milli - thinking_milli >= self.reserve_milli else 0.0
        tr = {"eat_chance": None, "skip_chance": skip, "bar": bar, "pick": "skip", "options_considered": [],
              "no_safe_option": False, "untried_tally": None}
        if not isinstance(verdict, int):
            return tr, "bench"
        eat = max(0.0, 1.0 - (1.0 - self.slots[verdict].share()) * (WRONG_FACTOR_TOP - RELIABILITY))
        tr["eat_chance"] = eat
        for order, (option, chance) in enumerate((("eat", eat), ("skip", skip)), 1):
            cleared = chance >= bar
            tr["options_considered"].append({"order": order, "source": "bench", "option": option,
                                             "predicted_p_above_R": chance, "cleared_bar": cleared})
            if cleared:
                tr["pick"] = option
                return tr, "bench"
        tr["pick"] = "eat" if eat > skip else "skip"
        tr["no_safe_option"] = True
        return tr, "no-safe-option-fallback"

    # ------------------------------------------------------------ the interface

    def decide(self, visible, energy_milli):
        reading = np.array(visible, dtype=np.float64)
        verdict, step, spikes, leader, near = self._recognise(reading)
        if self.restless:              # a mind whose state changes as it looks
            self.looks += 1
            spikes += self.looks
        cost = _cost_milli(spikes)
        tr, provenance = self._drive(verdict, int(energy_milli), cost)
        self.pending = (reading, verdict, tr["pick"])
        self.landed = None
        log = {}
        if leader is not None:
            log = {"last_leader": leader, "within_margin": near}
        return {"action": tr["pick"], "verdict": verdict, "settle_step": step,
                "thinking": {"unit": "spike", "count": spikes, "cost_milli": cost},
                "drive": tr, "provenance": provenance, "log": log}

    def land(self, delta_milli, energy_after_milli, taste):
        reading, verdict, pick = self.pending
        t = np.array(taste, dtype=np.float64)
        self.landed = (int(delta_milli), int(energy_after_milli) >= self.reserve_milli, t)
        after = verdict
        if self.aware and isinstance(verdict, int) and self.slots[verdict].taste_outside(t):
            after = "unknown"
        return {"verdict": after, "settle_step": SETTLE_NAMED if isinstance(after, int) else SETTLE_UNKNOWN}

    def _empty_slot(self):
        n = 0
        while n in self.slots:
            n += 1
        return n

    def _forget(self, keep):
        events = []
        while len(self.slots) >= self.max_slots:
            slot = min((s for s in self.slots if s != keep), key=lambda s: (len(self.slots[s].eats), s))
            del self.slots[slot]
            events.append(self._event("forget", slot))
        return events

    def _event(self, kind, slot, parent=None, layer=None):
        # The stub knows only its own pick: an eat it skipped was forced on it.
        trigger = "chosen-eat" if self.trigger_pick == "eat" else "designed-exposure"
        return {"type": kind, "trigger": trigger, "slot": slot, "parent_slot": parent, "layer": layer,
                "weight_deltas": []}

    def _add(self, reading, taste, above):
        c = Candidate(reading, taste, above, self.aware)
        if self.uneven:
            c.weights[0] = UNEVEN_TENTHS
        slot = self._empty_slot()
        self.slots[slot] = c
        return slot

    def write(self):
        (reading, verdict, self.trigger_pick), (delta, above, taste) = self.pending, self.landed
        self.pending, self.landed = None, None
        if isinstance(verdict, int):
            c = self.slots[verdict]
            agrees = (c.share() >= AGREE_SHARE) == above
            if agrees and not c.taste_outside(taste):
                c.stretch(reading, taste, above)
                return {"events": [self._event("stretch", verdict)]}
            layer = "taste" if agrees else "details"
            events = self._forget(verdict)
            slot = self._add(reading, taste, above)
            return {"events": events + [self._event("split", slot, verdict, layer)]}
        events = self._forget(None)
        slot = self._add(reading, taste, above)
        return {"events": events + [self._event("new", slot)]}

    def dump(self):
        out = []
        for slot, c in sorted(self.slots.items()):
            ranges = [[float(lo), float(hi)] for lo, hi in zip(c.lo, c.hi)]
            weights = list(c.weights)
            if c.taste_lo is None:
                ranges += [None] * TASTE_TRAITS
                weights += [None] * TASTE_TRAITS
            else:
                ranges += [[float(lo), float(hi)] for lo, hi in zip(c.taste_lo, c.taste_hi)]
                weights += [WEIGHT_TENTHS] * TASTE_TRAITS
            out.append({"slot": slot, "ranges": ranges, "weights_tenths": weights, "reliability": RELIABILITY,
                        "eats": len(c.eats)})
        return {"candidates": out}

    def info(self):
        own = "KT-93, the stub's own"
        return {"version": [dict(OS07)], "chooser": "satisficing", "neuron": "spiking",
                "constants": {"detector_width_nw": [DETECTOR_WIDTH_NW, own], "name_min": [NAME_MIN, own],
                              "max_slots": [self.max_slots, own], "spike_nano": [SPIKE_NANO, own],
                              "weight_tenths": [WEIGHT_TENTHS, "M20, KT-94"],
                              "agree_share": [AGREE_SHARE, own],
                              "bar_top": [BAR_TOP, "PLACEHOLDER-27"], "bar_slope": [BAR_SLOPE, "PLACEHOLDER-27"],
                              "wrong_factor_top": [WRONG_FACTOR_TOP, "PLACEHOLDER-05"],
                              "reliability": [RELIABILITY, own]}}


def make(config):
    return StubMind(config)
