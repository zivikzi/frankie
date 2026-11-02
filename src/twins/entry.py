"""The tower twins, behind the same interface as K-F (section 4, section 6, M16, M43).

Week 3 builds TW7, and TW2 comes in Week 5 (OS01, OS10 and K-F-NOWARM are
switch settings of K-F's own code, section 7). The twins
import K-F's code (the mind package) and K-F's code never imports them
(FORBIDDEN 26). The import guard lets this package import only NumPy, Numba
and the mind package, so each twin's own part lives in this one file.

TW7 is K-F with ordinary rate units in place of spiking neurons (M43, KT-68).
Each group, "unknown" included, is one rate unit, updated every 1 ms substep:

- Its activation stands for the group's expected spike trace (KT-62), so
  K-F's commit margin and thresholds apply to it unchanged. A trace of a
  stands for a x (1 - e^(-1/10)) expected spikes per ms.
- Each step it moves toward its target by 1/tau of the gap, tau being the
  time constant (KT-29): tau da/dt = target - a, one 1 ms step at a time.
- Target = gain (KT-28) x 8 / (threshold x (1 - e^(-1/10))) x (input -
  push-down - firing level), and never below 0 (KT-108). The firing level is
  the threshold times the leak (KT-19, KT-20), the input at which a leaky
  neuron's charge levels off exactly at its threshold. The middle factor
  turns charge above it into the trace 8 neurons would leave if each fired
  once per threshold's worth of charge, so a gain of 1 is about K-F's own
  pace. The push-down is what K-F's spikes would take off one neuron at
  these rates: the inhibition strength (KT-22) times the expected spikes of
  every other live group in the substep before (KT-59).
- A group at rest (eliminated, removed or knocked down) is held at 0, and
  pushes nothing down.

Everything else, from the layer timetable to the memory rule and the drive,
is K-F's own code. TW7 pays 0.001 per check (B14, KT-45, KT-46).

The logged search of section 7 hands TW7 K-F's picked values as "tuned"
and each gain and time constant it tries as "rate" (KT-126). Without them
TW7 runs on the values in mind.constants and in this file.
"""

import numpy as np

from mind import constants as K
from mind.interface import TowerMind

GAIN = 1                     # TW7's rate-unit gain (KT-28, start value)
TAU_MS = 10                  # TW7's rate-unit time constant, in ms (KT-29, start value)
TW7 = "TW7"
RATE = "rate"
CHECK = "check"


class RateUnits:
    """One rate unit per group (KT-68)."""

    def __init__(self, n_groups, settings, gain, tau_ms):
        self.a = np.zeros(n_groups)
        # trace per unit of charge above the firing level: 8 neurons, each firing about once per threshold's
        # worth of charge, behind a trace that decays by e^(-1/10) per ms (KT-61, KT-62, KT-68)
        self.gain = gain * K.GROUP_NEURONS / (settings.threshold * (1.0 - K.TRACE_DECAY))
        self.step_share = 1.0 / tau_ms
        self.firing_level = settings.threshold * settings.leak
        self.inhibition = settings.inhibition
        self.spikes = 0                      # rate units make no spikes

    def activation(self):
        return self.a.copy()

    def rest(self, g):
        self.a[g] = 0.0

    def substep(self, inputs, live):
        rates = self.a * (1.0 - K.TRACE_DECAY)                  # expected spikes per ms (KT-62)
        total = float(np.add.accumulate(rates)[-1])             # summed left to right (I05)
        push = self.inhibition * (total - rates)                # from every other group (KT-59)
        target = self.gain * np.maximum(inputs - push - self.firing_level, 0.0)
        a = self.a + (target - self.a) * self.step_share
        a[~live] = 0.0
        self.a = a


class RateMaker:
    def __init__(self, gain=GAIN, tau_ms=TAU_MS):
        self.gain = gain
        self.tau_ms = tau_ms

    def start(self, n_groups, settings):
        return RateUnits(n_groups, settings, self.gain, self.tau_ms)

    def table(self):
        return {"rate_gain": [self.gain, "KT-28"], "rate_tau_ms": [self.tau_ms, "KT-29"]}


def make_tw7(config, settings=None, maker=None):
    return TowerMind(config, maker or RateMaker(), CHECK, K.CHECK_NANO, RATE, [K.OS07], settings)


def _rate_maker(given):
    """TW7's own two numbers from the birth parameters, for the logged search (KT-28, KT-29, KT-126)."""
    if not isinstance(given, dict) or not set(given) <= {"gain", "tau_ms"}:
        raise ValueError("TW7's own setting names only its gain and time constant (section 7)")
    for name, value in given.items():
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not np.isfinite(value) or value <= 0:
            raise ValueError(f"{name} must be one finite number above 0 (section 7)")
    return RateMaker(**given)


def make(config):
    params = config["params"]
    twin = params.get("twin")
    if twin != TW7:
        raise ValueError(f"no twin {twin!r} is built yet: TW2 comes in Week 5")
    unknown = sorted(set(params) - {"twin", "tuned", "rate"})
    if unknown:
        raise ValueError(f"TW7 takes no birth parameter {unknown}")
    settings = K.Settings.from_params(params["tuned"]) if "tuned" in params else None     # K-F's values (KT-126)
    maker = _rate_maker(params["rate"]) if "rate" in params else None
    return make_tw7(config, settings, maker)
