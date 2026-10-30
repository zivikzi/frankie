"""B1n-mind: Frankie's drive with the tower and memory replaced by a nearest-item memory (X36, section 4).

Its "named candidate" is the nearest stored item over the 18 observable
traits, in noise widths, ties to the most recent item (KT-44, KT-05). It judges
an object "unknown" when memory is empty or the nearest item is farther than
its own radius, which is chosen like B1n-bot-r's (section 4, KT-101). That
item's own eat is its whole record, and its reliability is always 1.

It pays the sharp look and 0.001 per check, one check being one stored item on
one trait, counted once per decision (KT-45, KT-46). It chooses through the
drive (drive.py), with habits off (OS07, lifetime).
"""

import numpy as np

from . import rules as K
from .drive import BAR_SLOPE, BAR_TOP, WRONG_FACTOR_TOP, drive

RELIABILITY = 1.0            # B1n-mind's reliability is always 1 (section 4)
CHECK_MILLI = 1              # 0.001 per check (B14, KT-46), in milli-units
OS07 = {"switch": "OS07", "setting": "habits off", "scope": "lifetime"}    # (section 5, KT-49)


class B1nMind:
    agent_type = "B1n-mind"

    def __init__(self, config):
        self.reserve_milli = int(config["reserve_milli"])
        self.boldness = float(config["boldness"])
        self.radius = config["params"]["radius"]
        self.items = K.StoredItems()
        self.above_r = []          # per stored item: energy at or above R right after its eat (KT-70)
        self.untried = []          # outcomes of the eats judged "unknown" (PLACEHOLDER-34)
        self._pending = None
        self._landed = None

    def _tally(self):
        return None if not self.untried else sum(self.untried) / len(self.untried) / 1000

    def decide(self, visible, energy_milli):
        o = np.array(visible, dtype=np.float64)
        n = len(self.items)
        checks = n * len(K.OBSERVABLE)              # one stored item on one trait (KT-45)
        thinking = checks * CHECK_MILLI
        log = {}
        verdict, state, share = "unknown", "unknown", None
        if n:
            d = K.mean_nw(self.items.readings, o, K.OBSERVABLE)
            i = K.nearest(d)
            log = {"nearest": i, "distance_nw": float(d[i]), "outcome_milli": int(self.items.outcomes[i])}
            if self.radius is None or d[i] <= self.radius:
                verdict, state = i, "named"
                share = 1.0 if self.above_r[i] else 0.0   # its own eat is its whole record (section 4)
        tr = drive(state, share, RELIABILITY, int(energy_milli), thinking, self.reserve_milli, self.boldness)
        provenance = tr.pop("provenance")
        tr["untried_tally"] = self._tally()
        self._pending, self._landed = (o, verdict), None
        return {"action": tr["pick"], "verdict": verdict, "settle_step": None,
                "thinking": {"unit": "check", "count": checks, "cost_milli": thinking},
                "drive": tr, "provenance": provenance, "log": log}

    def land(self, delta_milli, energy_after_milli, taste):
        self._landed = (int(delta_milli), int(energy_after_milli) >= self.reserve_milli)
        return {"verdict": None, "settle_step": None}

    def write(self):
        (o, verdict), (delta, above) = self._pending, self._landed
        self.items.add(o, delta)
        self.above_r.append(above)
        if verdict == "unknown":
            self.untried.append(delta)
        self._pending, self._landed = None, None
        return {"events": []}

    def dump(self):
        return dict(self.items.dump(), above_r=list(self.above_r))

    def info(self):
        return {"version": [dict(OS07)], "chooser": "satisficing", "neuron": None,
                "constants": {"radius_nw": [self.radius, "KT-05, KT-101"],
                              "bar_top": [BAR_TOP, "PLACEHOLDER-27"], "bar_slope": [BAR_SLOPE, "PLACEHOLDER-27"],
                              "wrong_factor_top": [WRONG_FACTOR_TOP, "PLACEHOLDER-05"],
                              "reliability": [RELIABILITY, "section 4"],
                              "check_milli": [CHECK_MILLI, "B14, KT-46"]}}
