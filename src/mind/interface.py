"""A tower mind behind the one mind interface (B21, KT-93, KT-97): K-F, and the twins built from its code.

make(config) gives a mind that answers decide, land, write, dump and info,
with plain data only. What the mind is told is fixed by KT-97: at birth R, b,
its own settings and the run's trait order; before each decision the 18
visible readings and its energy after the reset and the look; after an eat
the outcome, the energy after it and the 4 tastes. Nothing else reaches it.

- decide() settles the tower on the reading, prices the thinking and lets
  the drive choose (section 5). It changes nothing the mind keeps: it only
  holds the decision for land() and write() (FORBIDDEN 9).
- land() makes the verdict after eating, which costs nothing and changes no
  choice or record (section 6, KT-66).
- write() applies the memory rule to the verdict committed before the eat
  (section 6). Its trigger is the mind's own reading of its pick: a skipped
  decision that was then eaten was forced (KT-97).

The units each group runs on come from a maker with start(n_groups,
settings): K-F's spiking units (Week 4) or TW7's rate units (twins package).
"""

import numpy as np

from mind import constants as K
from mind.drive import EAT, choose, share_above, thinking_milli
from mind.memory import Memory
from mind.tower import Race

CHOSEN = "chosen-eat"
DESIGNED = "designed-exposure"


class TowerMind:
    def __init__(self, config, units_maker, unit, unit_nano, neuron, version, settings=None):
        self.reserve_milli = int(config["reserve_milli"])
        self.boldness = float(config["boldness"])
        order = [int(t) for t in config["trait_order"]]
        if sorted(order) != list(range(K.N_TRAITS)):
            raise ValueError("the trait order must list each of the 22 traits once (KT-41)")
        self.positions = [0] * K.N_TRAITS
        for place, t in enumerate(order):
            self.positions[t] = place
        self.settings = settings or K.Settings()
        self.units_maker = units_maker
        self.unit = unit                        # "check" or "spike" (KT-46)
        self.unit_nano = unit_nano
        self.neuron = neuron                    # "rate" or "spiking" (FORBIDDEN 27)
        self.version = [dict(v) for v in version]
        self.memory = Memory(self.settings)     # empty at birth (M09)
        self.untried_milli = 0                  # PLACEHOLDER-34's tally, logged only (KT-49)
        self.untried_eats = 0
        self.pending = None
        self.landed = None

    def _race(self, values, taste_known):
        units = self.units_maker.start(len(self.memory.kinds) + 1, self.settings)
        return Race(self.memory, values, taste_known, self.positions, self.settings, units)

    def _tally(self):
        if self.untried_eats == 0:
            return None
        return self.untried_milli / self.untried_eats / K.MILLI_PER_UNIT

    # ------------------------------------------------------------ the interface

    def decide(self, visible, energy_milli):
        values = np.zeros(K.N_TRAITS)
        values[:K.N_VISIBLE] = np.asarray(visible, dtype=np.float64)
        settle = self._race(values, False).run()
        used = settle.checks if self.unit == "check" else settle.spikes
        cost = thinking_milli(used, self.unit_nano)
        named = isinstance(settle.verdict, int)
        share = reliability = None
        if named:
            kind = self.memory.kinds[settle.verdict]
            share, reliability = share_above(kind.above_flags()), kind.reliability_share()
        trace, provenance = choose(named, share, reliability, int(energy_milli), cost, self.reserve_milli,
                                   self.boldness, self._tally())
        self.pending = {"values": values, "verdict": settle.verdict, "pick": trace["pick"]}
        self.landed = None
        log = dict(settle.log, checks=settle.checks, spikes=settle.spikes)
        return {"action": trace["pick"], "verdict": settle.verdict, "settle_step": settle.settle_step,
                "thinking": {"unit": self.unit, "count": used, "cost_milli": cost}, "drive": trace,
                "provenance": provenance, "log": log}

    def land(self, delta_milli, energy_after_milli, taste):
        if self.pending is None:
            raise ValueError("an eat landed with no decision before it")
        values = self.pending["values"].copy()
        values[K.TASTE_FROM:] = np.asarray(taste, dtype=np.float64)
        settle = self._race(values, True).run(after_eating=True)
        self.landed = {"values": values, "delta_milli": int(delta_milli),
                       "above": int(energy_after_milli) >= self.reserve_milli}
        return {"verdict": settle.verdict, "settle_step": settle.settle_step, "log": settle.log}

    def write(self):
        if self.pending is None or self.landed is None:
            raise ValueError("a memory write needs a decision and its eat")
        verdict = self.pending["verdict"]
        trigger = CHOSEN if self.pending["pick"] == EAT else DESIGNED
        events = self.memory.write(verdict, self.landed["values"], self.landed["delta_milli"],
                                   self.landed["above"], trigger)
        if not isinstance(verdict, int):         # an eat judged "unknown", or with nothing settled (PLACEHOLDER-34, -93)
            self.untried_milli += self.landed["delta_milli"]
            self.untried_eats += 1
        self.pending = self.landed = None
        return {"events": events}

    def dump(self):
        return self.memory.dump()

    def info(self):
        table = self.settings.table()
        table.update(self.units_maker.table())
        table.update({"slots": [K.SLOTS, "PLACEHOLDER-08"], "attention_traits": [K.ATTENTION_TRAITS, "PLACEHOLDER-14"],
                      "weight_start_tenths": [K.WEIGHT_START, "M20, KT-94"],
                      "substeps": [K.SUBSTEPS, "KT-09"], "trace_ms": [K.TRACE_MS, "KT-09, KT-62"],
                      "unit_nano": [self.unit_nano, "B14, KT-27, KT-46, KT-92"]})
        return {"version": [dict(v) for v in self.version], "constants": table, "chooser": "satisficing",
                "neuron": self.neuron}
