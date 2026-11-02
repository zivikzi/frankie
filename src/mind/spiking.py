"""K-F's spiking units: 8 leaky integrate-and-fire neurons per group (D12, section 6, KT-59 to KT-62, KT-125).

The tower (tower.py) drives one set of units per settle, one group per
candidate and one for "unknown", through `substep(inputs, live)` once per
1 ms substep, and reads `activation()` at the end of each settling step.
Every group starts each settle from rest (KT-09): charge 0, no neuron
resting after a spike, trace 0 and no spikes pending.

Each 1 ms substep, for every neuron k (0 to 7) of every live group, in this
order (KT-60, KT-59, KT-61, KT-125):

1. Its charge decays toward rest: charge x (1 - leak) (KT-19).
2. It is pushed down: the inhibition strength (KT-22) times the spikes every
   other group that is live now made in the substep before (KT-59). Charge
   may fall below rest and leaks back.
3. If it is still resting after a spike, it ignores its input and one more
   millisecond of its rest passes. Otherwise it adds its share of the
   group's steady input, (2k + 1)/8 of it (KT-61), and if its charge has
   reached the threshold (KT-20) it spikes: its charge goes to rest and it
   ignores its input for the refractory period (KT-21), that many
   substeps.

A group's trace then decays by e^(-1/10) and adds 1 for each spike of its
neurons in this substep (KT-62); the trace is the group's activation. A group
that is not live (eliminated or removed, KT-52, KT-57) is held at rest: no
charge, no trace, no spikes, no push-down. `rest(g)` puts a group back at
rest at once, its pending spikes included (a knock-down, KT-57).

The neurons add no noise (section 6). Every spike of every group, "unknown"
included, adds 1 to `spikes`, which K-F pays for (KT-46).

The inner loop is plain loops compiled by Numba (section 6, I05), with no
fastmath and no other option (KT-119). `substep_reference` is the same step
written with NumPy's whole-array operations, kept for the tests (section 6),
which require both to give the same doubles, bit for bit.
"""

import numba
import numpy as np

from mind import constants as K

# Neuron k of a group gets (2k + 1)/8 of the group's input: 1/8 to 15/8, averaging 1 (KT-61)
SHARES = (K.SHARE_STEP * np.arange(K.GROUP_NEURONS) + 1) / K.GROUP_NEURONS
SHARES.flags.writeable = False
SPIKING = "spiking"


@numba.njit
def _substep(charge, resting, trace, pending, inputs, live, keep, threshold, refractory, inhibition, shares,
             decay):
    """One 1 ms substep of every group, in place. Returns the spikes made in it (KT-59 to KT-62)."""
    groups, neurons = charge.shape
    total = 0
    for g in range(groups):
        if live[g]:
            total += pending[g]
    made = 0
    for g in range(groups):
        if not live[g]:
            for k in range(neurons):
                charge[g, k] = 0.0
                resting[g, k] = 0
            trace[g] = 0.0
            pending[g] = 0
            continue
        push = inhibition * (total - pending[g])
        fired = 0
        for k in range(neurons):
            x = charge[g, k] * keep
            x = x - push
            if resting[g, k] > 0:
                resting[g, k] -= 1
            else:
                x = x + shares[k] * inputs[g]
                if x >= threshold:
                    fired += 1
                    x = 0.0
                    resting[g, k] = refractory
            charge[g, k] = x
        trace[g] = trace[g] * decay + fired
        pending[g] = fired
        made += fired
    return made


def substep_reference(charge, resting, trace, pending, inputs, live, keep, threshold, refractory, inhibition):
    """The same substep with NumPy's whole-array operations (section 6). Returns new arrays and the spikes made."""
    on = np.asarray(live, dtype=bool)
    total = int(np.sum(pending[on]))
    push = inhibition * (total - pending)
    x = charge * keep - push[:, None]
    still = resting > 0
    added = x + SHARES[None, :] * np.asarray(inputs, dtype=np.float64)[:, None]
    fire = ~still & (added >= threshold)
    x = np.where(still, x, added)
    x = np.where(fire, 0.0, x)
    resting = np.where(still, resting - 1, np.where(fire, refractory, 0)).astype(np.int64)
    fired = fire.sum(axis=1).astype(np.int64)
    trace = trace * K.TRACE_DECAY + fired
    off = ~on
    x[off] = 0.0
    resting[off] = 0
    trace[off] = 0.0
    fired[off] = 0
    return x, resting, trace, fired, int(fired.sum())


class SpikingUnits:
    """8 spiking neurons per group, every group at rest (KT-09, KT-61)."""

    def __init__(self, n_groups, settings):
        self.charge = np.zeros((n_groups, K.GROUP_NEURONS))
        self.resting = np.zeros((n_groups, K.GROUP_NEURONS), dtype=np.int64)
        self.trace = np.zeros(n_groups)
        self.pending = np.zeros(n_groups, dtype=np.int64)      # each group's spikes in the substep before (KT-59)
        self.keep = 1.0 - settings.leak                         # (KT-19, KT-60)
        self.threshold = float(settings.threshold)              # (KT-20)
        self.refractory = int(settings.refractory_ms)           # (KT-21)
        self.inhibition = float(settings.inhibition)            # (KT-22)
        self.spikes = 0

    def activation(self):
        return self.trace.copy()

    def rest(self, g):
        self.charge[g] = 0.0
        self.resting[g] = 0
        self.trace[g] = 0.0
        self.pending[g] = 0

    def substep(self, inputs, live):
        self.spikes += int(_substep(self.charge, self.resting, self.trace, self.pending,
                                    np.asarray(inputs, dtype=np.float64), np.asarray(live, dtype=np.bool_),
                                    self.keep, self.threshold, self.refractory, self.inhibition, SHARES,
                                    K.TRACE_DECAY))


class SpikingMaker:
    def start(self, n_groups, settings):
        return SpikingUnits(n_groups, settings)

    def table(self):
        return {"group_neurons": [K.GROUP_NEURONS, "D12, KT-61"]}
