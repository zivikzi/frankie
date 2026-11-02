"""K-F's entry point: make(config) (B21, KT-93).

K-F is the tower, the memory rule and the drive of this package on spiking
units (D12, mind.spiking), paying KT-27's per-spike cost (KT-46). Its birth
parameters may switch on one of its off-switch versions, OS10 (taste out of
memory and the verdict after eating, section 4). OS01 comes in Week 5.

With the birth parameter "mind" set to "E1", it makes E1 instead (mind.e1,
kill-test/E1_ADDENDUM.md, KT-132), and E1 reads the rest of the parameters
itself. Without it, nothing below changes.

The logged search of section 7 hands K-F each setting it tries through
the birth parameters, as "tuned" (the closed list's own names, KT-19 to
KT-26) and "spike_nano" (KT-27). Without them K-F runs on the values in
mind.constants. With no per-spike cost there (KT-27 is set after the
search), K-F refuses to run unless it is handed one (KT-126).
"""

from mind import constants as K
from mind import e1
from mind.interface import TowerMind
from mind.spiking import SPIKING, SpikingMaker

SPIKE = "spike"
TUNED = "tuned"
SPIKE_NANO = "spike_nano"
OS10 = "OS10"
OS01 = "OS01"
OS10_RECORD = {"switch": "OS10", "setting": None, "scope": "lifetime"}     # (section 4, KT-49)
PARAMS = (TUNED, SPIKE_NANO, OS10, OS01)


def _spike_nano(params):
    nano = params.get(SPIKE_NANO, K.SPIKE_NANO)
    if nano is None:
        raise ValueError("K-F needs KT-27's per-spike cost, which is set after the search (KT-47, KT-126)")
    if isinstance(nano, bool) or not isinstance(nano, int) or nano < 0:
        raise ValueError("the per-spike cost is a whole number of nano-units (KT-92)")
    return nano


MIND = "mind"


def make(config):
    params = config["params"]
    if params.get(MIND) == e1.E1:                      # E1, under kill-test/E1_ADDENDUM.md (KT-132)
        return e1.make(config)
    unknown = sorted(set(params) - set(PARAMS))
    if unknown:
        raise ValueError(f"K-F takes no birth parameter {unknown}")
    if params.get(OS01):
        raise ValueError("OS01 is built in Week 5")
    settings = K.Settings.from_params(params[TUNED]) if TUNED in params else K.Settings()
    version = [K.OS07]
    blind = bool(params.get(OS10))
    if blind:
        version.append(OS10_RECORD)
    return TowerMind(config, SpikingMaker(), SPIKE, _spike_nano(params), SPIKING, version, settings,
                     taste_blind=blind)
