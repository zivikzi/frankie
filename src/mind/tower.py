"""K-F's tower: one settle on one reading, outside in (D13, M01 to M08, section 6, KT-51 to KT-66).

Each remembered kind is a candidate group, and "unknown" is one more group,
always in the race (KT-58). The groups' neurons are not in this file: the
tower drives a set of units, one per group, through `substep`, and reads
their `activation` at the end of each settling step (KT-62). K-F's spiking
units arrive in Week 4; TW7's rate units live in the twins package (M43,
KT-68). Everything else here is the same for both.

One settle, as rows KT-51 to KT-66 fix it:

- Layers switch on one step apart: context at step 1, object at 2, parts at
  3, details at 4, and stay on (KT-51). Context and object read all their
  traits. Parts and details each read the 3 traits with the highest pooled
  weight over the surviving candidates, each candidate weighing in
  proportion to its activation at the end of the step before (equally if all
  are 0); ties go by the run's trait order. The set is chosen once, when the
  layer opens (PLACEHOLDER-14, KT-54). Before an eat only visible traits are
  eligible. After an eat, details also read all 4 tastes (section 6, KT-66).
- A reading lights the detectors within one detector width of it. A trait
  fits a candidate when a lit detector's centre lies inside the candidate's
  stored range, and each fitting checked trait adds its weight to the
  candidate's steady input (PLACEHOLDER-01, KT-53). "Unknown"'s input is the
  new-kind threshold from step 1 (PLACEHOLDER-10, KT-58).
- At each step's end, in this order (KT-63):
  1. Objections. The leader is the live group, "unknown" included, with the
     highest activation; a tie means no leader. A layer's mismatch is the sum
     of the leader's weights on that layer's checked traits that do not fit
     it. When the same candidate leads with parts' or details' mismatch at or
     above the objection threshold at the ends of 2 steps in a row, that
     layer objects (M07, M08, KT-56). The 1st and 2nd objection put the
     leader at rest and bring every eliminated candidate back at rest, which
     reopens the race (a reset). A later one removes the leader for the rest
     of the settle and brings no one back (PLACEHOLDER-13, KT-57). "Unknown"
     is never objected to.
  2. Elimination, at the ends of steps 1 to 3 only: a candidate trailing the
     leading candidate by at least the commit margin is held at rest, with
     no input and no push-down (KT-52). "Unknown" is never eliminated and
     never leads here. A candidate a reset brought back is not eliminated
     again.
  3. Wins, holds and the step-30 rule. A group leads by the margin when its
     activation, less the highest other activation (or rest, 0), is at least
     the commit margin. A group wins at step s when it leads by the margin at
     steps s - 1 and s (PLACEHOLDER-12). The win settles at step s + 4 if
     the winner has stayed strictly the highest, with no reset, through it
     (KT-10, KT-63). With no hold running at step 30, the verdict is
     "unknown" (settled) if no candidate leads "unknown" by the margin, and
     "unsettled" otherwise. A hold still running at step 30 runs on to s + 4
     and the settle is "unsettled" if it breaks (KT-64).
- The verdict after eating runs the same rules for exactly 30 steps: a win
  settled by step 30, otherwise the step-30 rule (KT-66).

Stability is logged at every step's end (KT-127): the leader, whether the
two highest live groups are within the commit margin (a near-tie), every
hold that broke, and why a settle ended unsettled. Nothing reads it but the
reports.

Thinking is measured in checks (KT-45): one candidate's fit on one trait,
taken once when that test first switches on in the settle, and again for a
candidate a reset brings back. Spiking units also report their spikes
(KT-46).

Every sum is taken in a fixed order, one term at a time, so a settle gives
the same doubles on every machine (I05).
"""

import numpy as np

from mind import constants as K

UNKNOWN = "unknown"
UNSETTLED = "unsettled"
CONTEXT = "context"
OBJECT = "object"
PARTS = "parts"
DETAILS = "details"
OBJECTING = (PARTS, DETAILS)                    # only parts and details object (KT-56)
RESET = "reset"
REMOVED = "removed"
LEADS_UNKNOWN = "a candidate leads unknown at step 30 with no hold"     # why a settle ended unsettled (KT-127)
HOLD_BROKE = "a hold begun by step 30 broke after it"                    # (KT-64, KT-127)

# (name, first trait, end, the step it switches on at), outside in (KT-51)
LAYERS = ((CONTEXT, 0, K.OBJECT_FROM, K.CONTEXT_STEP), (OBJECT, K.OBJECT_FROM, K.PARTS_FROM, K.OBJECT_STEP),
          (PARTS, K.PARTS_FROM, K.DETAILS_FROM, K.PARTS_STEP), (DETAILS, K.DETAILS_FROM, K.TASTE_FROM, K.DETAILS_STEP))

CENTRES = (np.arange(K.DETECTORS) + K.DETECTOR_OFFSET) / K.DETECTORS      # (KT-53)
CENTRES.flags.writeable = False


def ordered_sum(xs) -> float:
    """x[0] + x[1] + ..., left to right."""
    total = 0.0
    for x in xs:
        total = total + float(x)
    return total


def fits(values, known_end, lo, hi, width):
    """fit[i, t]: a detector lit by trait t's reading has its centre inside candidate i's range (KT-53).

    Only traits before known_end have a reading; the rest never fit.
    """
    fit = np.zeros(lo.shape, dtype=bool)
    for t in range(known_end):
        lit = CENTRES[np.abs(values[t] - CENTRES) <= width]
        for c in lit:
            fit[:, t] |= (lo[:, t] <= c) & (c <= hi[:, t])
    return fit


class Settle:
    """The result of one settle."""

    def __init__(self, verdict, settle_step, checks, spikes, log):
        self.verdict = verdict              # a slot, "unknown" or "unsettled"
        self.settle_step = settle_step      # None when unsettled
        self.checks = checks
        self.spikes = spikes
        self.log = log


class Race:
    """One settle of the tower on one reading (section 6)."""

    def __init__(self, memory, values, taste_known, positions, settings, units):
        self.slots = memory.slots()
        n = self.n = len(self.slots)
        self.unknown = n                                    # "unknown" is the last group
        self.s = settings
        shape = (n, K.N_TRAITS)
        lo, hi = np.zeros(shape), np.zeros(shape)
        tenths = np.zeros(shape, dtype=np.int64)
        for i, slot in enumerate(self.slots):
            kind = memory.kinds[slot]
            lo[i], hi[i], tenths[i] = kind.lo, kind.hi, kind.tenths
        self.tenths = tenths
        self.weights = tenths / K.TENTHS
        self.taste_known = taste_known
        known_end = K.N_TRAITS if taste_known else K.TASTE_FROM
        self.fit = fits(np.asarray(values, dtype=np.float64), known_end, lo, hi, settings.detector_width)
        self.positions = positions                          # trait -> its place in the run's trait order (KT-41)
        self.units = units
        self.live = np.ones(n + 1, dtype=bool)              # groups in the race: not eliminated, not removed
        self.eliminated = np.zeros(n, dtype=bool)
        self.returned = np.zeros(n, dtype=bool)             # brought back by a reset: never eliminated again
        self.checked = {}                                   # layer -> the traits it checks
        self.checks = 0
        self.inputs = np.zeros(n + 1)
        self.log = {"checked": {}, "eliminated": [], "objections": [], "leaders": [], "near_ties": 0,
                    "holds_broken": [], "unsettled_why": None}

    # ------------------------------------------------------------ inputs and layers

    def _set_inputs(self):
        inputs = np.zeros(self.n + 1)
        for t in sorted(t for traits in self.checked.values() for t in traits):
            inputs[:self.n] = inputs[:self.n] + self.fit[:, t] * self.weights[:, t]
        inputs[self.unknown] = self.s.new_kind_threshold
        inputs[~self.live] = 0.0
        self.inputs = inputs

    def _attention(self, first, end, a):
        """The 3 traits of [first, end) with the highest pooled weight (PLACEHOLDER-14, KT-54)."""
        survivors = [i for i in range(self.n) if self.live[i]]
        if not survivors:
            return []
        shares = [float(a[i]) for i in survivors]
        if ordered_sum(shares) == 0.0:
            shares = [1.0] * len(survivors)
        total = ordered_sum(shares)
        pooled = {t: ordered_sum(sh * float(self.tenths[i, t]) for sh, i in zip(shares, survivors)) / total
                  for t in range(first, end)}
        ranked = sorted(range(first, end), key=lambda t: (-pooled[t], self.positions[t]))
        return sorted(ranked[:K.ATTENTION_TRAITS])

    def _open(self, step, a):
        for name, first, end, opens in LAYERS:
            if step != opens:
                continue
            if name in (CONTEXT, OBJECT):
                traits = list(range(first, end))
            else:
                traits = self._attention(first, end, a)
                if name == DETAILS and self.taste_known:
                    traits = traits + list(range(K.TASTE_FROM, K.N_TRAITS))      # (section 6, KT-66)
            self.checked[name] = traits
            self.log["checked"][name] = list(traits)
            self.checks += len(traits) * int(self.live[:self.n].sum())          # (KT-45)
            self._set_inputs()

    def _checked_now(self) -> int:
        return sum(len(traits) for traits in self.checked.values())

    # ------------------------------------------------------------ reading the race

    def _name(self, g):
        return UNKNOWN if g == self.unknown else self.slots[g]

    def _leader(self, a):
        """The live group with the highest activation, or None on a tie (KT-56)."""
        groups = [g for g in range(self.n + 1) if self.live[g]]
        if not groups:
            return None
        top = max(float(a[g]) for g in groups)
        at_top = [g for g in groups if float(a[g]) == top]
        return at_top[0] if len(at_top) == 1 else None

    def _others_top(self, g, a) -> float:
        """The highest activation of every other group, or rest (0) if that is higher."""
        others = np.delete(a, g)
        return max(0.0, float(others.max())) if others.size else 0.0

    def _lead(self, a):
        """The group leading every other group, and rest, by the commit margin, if one does (KT-63)."""
        g = int(np.argmax(a))
        if self.live[g] and float(a[g]) - self._others_top(g, a) >= self.s.commit_margin:
            return g
        return None

    def _strictly_highest(self, g, a) -> bool:
        return float(a[g]) > self._others_top(g, a)

    def _mismatch(self, g, layer) -> float:
        traits = self.checked.get(layer, [])
        return ordered_sum(self.weights[g, t] for t in traits if not self.fit[g, t])

    # ------------------------------------------------------------ changing the race

    def _rest(self, g):
        self.units.rest(g)

    def _knock_down(self, g, step, layers):
        """The 1st and 2nd objection: a reset (KT-57)."""
        self._rest(g)
        back = [i for i in range(self.n) if self.eliminated[i]]
        for i in back:
            self.eliminated[i] = False
            self.returned[i] = True
            self.live[i] = True
            self._rest(i)
        self.checks += len(back) * self._checked_now()                  # their tests switch on again (KT-45)
        self._set_inputs()
        self.log["objections"].append([step, self.slots[g], list(layers), RESET, [self.slots[i] for i in back]])

    def _remove(self, g, step, layers):
        """A 3rd or later objection removes the leader and brings no one back (KT-57)."""
        self.live[g] = False
        self._rest(g)
        self._set_inputs()
        self.log["objections"].append([step, self.slots[g], list(layers), REMOVED, []])

    def _eliminate(self, step, a):
        """At a handover, drop each candidate trailing the leading candidate by the margin (KT-52)."""
        active = [i for i in range(self.n) if self.live[i]]
        if not active:
            return
        top = max(float(a[i]) for i in active)
        out = [i for i in active if not self.returned[i] and top - float(a[i]) >= self.s.commit_margin]
        for i in out:
            self.live[i] = False
            self.eliminated[i] = True
            self._rest(i)
            self.log["eliminated"].append([step, self.slots[i]])
        if out:
            self._set_inputs()

    # ------------------------------------------------------------ the settle

    def run(self, after_eating=False) -> Settle:
        last = K.LAST_WIN_STEP if after_eating else K.LAST_WIN_STEP + K.HOLD_STEPS
        a = self.units.activation()
        lead_group, lead_steps = None, 0
        hold = None                                   # (winner, the step it won at)
        streak_leader, streak = None, {layer: 0 for layer in OBJECTING}
        objections = 0
        for step in range(1, last + 1):
            self._open(step, a)
            for _ in range(K.SUBSTEPS):
                self.units.substep(self.inputs, self.live)
            a = self.units.activation()
            reset = False
            # 1. objections (KT-56, KT-57)
            leader = self._leader(a)
            self._log_stability(leader, a)
            if leader is None or leader == self.unknown or leader != streak_leader:
                streak = {layer: 0 for layer in OBJECTING}
            streak_leader = leader
            if leader is not None and leader != self.unknown:
                for layer in OBJECTING:
                    over = self._mismatch(leader, layer) >= self.s.objection_threshold
                    streak[layer] = streak[layer] + 1 if over else 0
                firing = [layer for layer in OBJECTING if streak[layer] >= K.OBJECTION_STEPS]
                if firing:
                    objections += 1
                    if objections <= K.RESETS:
                        self._knock_down(leader, step, firing)
                        reset = True
                    else:
                        self._remove(leader, step, firing)
                    streak_leader, streak = None, {layer: 0 for layer in OBJECTING}
                    a = self.units.activation()
            # 2. elimination at the handovers (KT-52)
            if step < K.DETAILS_STEP:
                self._eliminate(step, a)
                a = self.units.activation()
            # 3. wins, holds and the step-30 rule (KT-63, KT-64, KT-66)
            if hold is not None:
                winner, won_at = hold
                if reset or not self._strictly_highest(winner, a):
                    self.log["holds_broken"].append([step, self._name(winner)])
                    hold = None
                elif step == won_at + K.HOLD_STEPS:
                    return self._result(self._name(winner), step, a)
            lead = self._lead(a)
            if lead is not None and lead == lead_group:
                lead_steps += 1
            elif lead is not None:
                lead_group, lead_steps = lead, 1
            else:
                lead_group, lead_steps = None, 0
            if hold is None and step <= K.LAST_WIN_STEP and lead_steps >= K.WIN_STEPS:
                hold = (lead_group, step)
            if step == K.LAST_WIN_STEP and (after_eating or hold is None):
                verdict = self._step_30(a)
                if verdict == UNSETTLED:
                    self.log["unsettled_why"] = LEADS_UNKNOWN
                return self._result(verdict, step, a)
            if step > K.LAST_WIN_STEP and hold is None:
                self.log["unsettled_why"] = HOLD_BROKE
                return self._result(UNSETTLED, step, a)
        raise RuntimeError("a hold begun by step 30 always ends by step 34")

    def _log_stability(self, leader, a):
        """Stability on near-ties (section 11, KT-127): logged only, read by nothing in the mind.

        Each step's end adds its leader (a slot, "unknown", or None on a tie) and
        adds 1 to near_ties when the two highest live groups are less than the
        commit margin apart.
        """
        self.log["leaders"].append(None if leader is None else self._name(leader))
        tops = sorted((float(a[g]) for g in range(self.n + 1) if self.live[g]), reverse=True)
        if len(tops) > 1 and tops[0] - tops[1] < self.s.commit_margin:
            self.log["near_ties"] += 1

    def _step_30(self, a):
        """No hold running at step 30: "unknown" unless some candidate leads it by the margin (KT-10, KT-64)."""
        u = float(a[self.unknown])
        if any(float(a[i]) - u >= self.s.commit_margin for i in range(self.n)):
            return UNSETTLED
        return UNKNOWN

    def _result(self, verdict, step, a) -> Settle:
        top = int(np.argmax(a))                                       # ties: the lowest slot, "unknown" last
        near = [self._name(h) for h in range(self.n + 1)
                if h != top and float(a[top]) - float(a[h]) < self.s.commit_margin]
        self.log.update({"last_step": step, "last_leader": self._name(top), "within_margin": near})
        return Settle(verdict, None if verdict == UNSETTLED else step, self.checks, self.units.spikes, self.log)
