"""One run of one mind on one run plan: the cafeteria (section 5).

The schedule is fixed. 40 forced warm-up tastes (K-F-NOWARM skips them), then
t1 to t8, each forced. Snapshots S1, S2, S4, S6 and S8 are taken right after
tastes 1, 2, 4, 6 and 8, once the write is complete, and check set P runs on
20 fresh copies of each, one probe per copy. From S8, the SOUR and
SWEET-CONTROL branches each make the h2 decision and eat (forced if skipped),
and check set Q runs on 20 copies of S8 and of each branch after its write.
That is 210 decisions (170 for K-F-NOWARM), each preceded by a logged reset of
energy to R + 10 (W45 kill-test entry): the only energy change the harness
makes besides the look, thinking and the eat's outcome (FORBIDDEN 31).

Every decision has a fixed number in that schedule, whatever order the checks
are run in. The check copies may be run in any order; nothing a copy does
reaches the main line, the snapshots or another copy (section 11's check-order
test, tests/test_check_order.py).

The harness, never the mind, keeps the H set, from the memory write events and
their lineage (KT-12, KT-76, FORBIDDEN 18). World-side facts (labels, roles,
natures, places, replica keys) go into the run record and never to the mind.
"""

import copy
import dataclasses
from dataclasses import dataclass, field

from world import traits
from world.kinds import NOTHING, NOURISH, POISON
from world.objects import COPY, FAR_APPLE, LOOKALIKE, NEUTRAL
from world.run_plan import CHECKPOINTS, REPLICA_MAIN, REPLICA_SOUR_BRANCHES, replica_p, replica_q

from . import constants as C
from . import protocol
from .host import InProcessHost, MindError, SubprocessHost, factory_from

OUTCOME_MILLI = {NOURISH: C.NOURISH_MILLI, NOTHING: C.NOTHING_MILLI, POISON: C.POISON_MILLI}   # (section 5)
SOUR, SWEET = "SOUR", "SWEET-CONTROL"
Q_STATES = ("S8", SOUR, SWEET)


class RunError(RuntimeError):
    """A run could not finish as the schedule says. Nothing is dropped or retried (KT-95)."""


def schedule(warmup: bool = True) -> list:
    """The 210 (or 170) decisions of a run, in their fixed order, as (step, detail) pairs."""
    out = []
    if warmup:
        out += [("warmup", i) for i in range(1, C.N_WARMUP + 1)]
    for k in range(1, C.N_TEACHING + 1):
        out.append(("teach", k))
        if k in CHECKPOINTS:
            out += [("P", (k, i)) for i in range(1, C.N_PROBES + 1)]
    out += [("branch", SOUR), ("branch", SWEET)]
    for state in Q_STATES:
        out += [("Q", (state, i)) for i in range(1, C.N_PROBES + 1)]
    return out


def probe_role(obj) -> str:
    """The world-side role of a probe, by its plan label (KT-87). Never sent to a mind."""
    label = obj.label
    if label.startswith("P-far-"):
        return "far"
    if label.startswith("P-look-h1-"):
        return "look-h1"
    if label.startswith("P-look-far-"):
        return "look-far"
    if label.startswith("Q-near-"):
        return "apple"
    if label.startswith("Q-look-"):
        return "look-h1" if label.startswith("Q-look-h1-") else "look-h2"
    if obj.role == NEUTRAL:
        return "neutral"
    if obj.role == COPY:
        return "copy"
    raise RunError(f"no probe role for {label}")


class Lineage:
    """Candidates by harness-given lineage id, and the H set (KT-12, KT-75, KT-76, KT-98).

    The mind names candidates by its own slot numbers, which it reuses after
    forgetting (KT-75), so every slot is translated to a lineage id that is
    never reused. The H set is built as the run goes (KT-98): it starts as the
    candidate t1's eat is filed under. A candidate created at a2, a3 or a4
    (t3, t5, t7) joins; one created at t2, t4, t6, t8, h2 or SWEET-CONTROL
    never joins; any other new candidate joins if its parent is in the set.
    Candidates created before t1 are not in it.
    """

    def __init__(self):
        self.slot_lid = {}
        self.parent = {}
        self.created_at = {}
        self.h = set()
        self.h1 = None
        self.h1_new = None
        self.next = 1
        self.log = []

    def lid(self, verdict):
        if isinstance(verdict, int):
            if verdict not in self.slot_lid:
                raise RunError(f"a verdict names slot {verdict}, which holds no candidate")
            return self.slot_lid[verdict]
        return verdict

    def _new_lid(self, slot, item, parent):
        if slot in self.slot_lid:
            raise RunError(f"slot {slot} still holds {self.slot_lid[slot]}; it must be forgotten first (KT-75)")
        lid = f"c{self.next}"
        self.next += 1
        self.slot_lid[slot] = lid
        self.parent[lid] = parent
        self.created_at[lid] = item
        if self.h1 is not None and item != "t1":
            taste = int(item[1:]) if item.startswith("t") else None
            if taste in C.H_JOINING_TASTES:
                self.h.add(lid)
            elif taste is not None or item in ("h2", "sweet"):
                pass
            elif parent in self.h:
                self.h.add(lid)
        return lid

    def apply(self, events, item) -> str:
        """Apply one write's events; returns the lineage id the eat is filed under."""
        filed = None
        for e in events:
            t, slot = e["type"], e["slot"]
            if t == "forget":
                if slot not in self.slot_lid:
                    raise RunError(f"forget of empty slot {slot}")
                lid = self.slot_lid.pop(slot)
                self.log.append({"item": item, "type": t, "lid": lid, "slot": slot})
                continue
            if t == "new":
                lid = self._new_lid(slot, item, None)
            elif t == "split":
                parent = self.lid(e["parent_slot"])
                lid = self._new_lid(slot, item, parent)
            else:
                lid = self.lid(slot)
            filed = lid
            self.log.append({"item": item, "type": t, "lid": lid, "slot": slot,
                             "parent": self.parent.get(lid) if t == "split" else None,
                             "trigger": e["trigger"], "layer": e["layer"]})
        if item == "t1":
            self.h1 = filed
            self.h1_new = any(e["type"] in ("new", "split") for e in events)
            self.h = {filed}
        return filed


@dataclass
class RunRecord:
    set_name: str
    family_number: int
    run_number: int
    label: str
    agent_type: str
    mind_class: str
    info: dict = None
    decisions: dict = field(default_factory=dict)       # schedule number -> record
    probes: list = field(default_factory=list)          # one per check copy, in schedule order
    injections: list = field(default_factory=list)
    exposures: list = field(default_factory=list)
    lineage_log: list = field(default_factory=list)
    h_sets: dict = field(default_factory=dict)          # state -> sorted lineage ids
    h1_lid: str = None
    h1_new: bool = None
    taste_noticed: dict = None
    birth_dump: dict = None
    partial: bool = False


class _Run:
    def __init__(self, plan, spec, host, cache, birth):
        self.plan, self.spec, self.host, self.cache = plan, spec, host, cache
        self.rec = RunRecord(plan.set_name, plan.family_number, plan.run_number, spec.label,
                             spec.agent_type, spec.mind_class)
        self.numbers = {key: n for n, key in enumerate(schedule(spec.warmup), 1)}
        self.reset_to = plan.reserve_milli + C.RESET_ABOVE_R_MILLI     # (W45 kill-test entry)
        self.lineage = {"main": Lineage()} if spec.mind_class == "tower" else None
        self.birth = birth
        self.slot_maps = {}

    # ------------------------------------------------------------ one decision

    def _decide(self, name, number, item, obj, replica, role):
        """Reset, look and choose. Returns (decision record, energy left after thinking)."""
        spec = self.spec
        self.rec.injections.append({"decision": number, "item": item, "type": "energy-set",
                                    "set_to_milli": self.reset_to})
        e = self.reset_to - (C.LOOK_MILLI if spec.pays_look else 0)       # (KT-48)
        visible = self.cache.visible(obj, replica)
        d = self.host.decide(name, visible, e)
        protocol.check_decision(d, spec)
        th = d["thinking"]
        cost = 0 if spec.thinking_unit == "none" else protocol.thinking_cost_milli(th["count"], spec.unit_nano)
        if th["cost_milli"] != cost:
            raise protocol.InterfaceError(f"{spec.label} says its thinking cost {th['cost_milli']} milli, "
                                          f"the registry charges {cost} (KT-48)")
        left = e - cost
        r = {"decision": number, "item": item, "label": obj.label, "place": obj.place, "replica": replica,
             "role": role, "energy_set_milli": self.reset_to,
             "look_milli": C.LOOK_MILLI if spec.pays_look else 0, "thinking_milli": cost,
             "energy_at_choice_milli": left, "visible": list(visible), "mind": d}
        self.rec.decisions[number] = r
        return r, left

    def _eat(self, name, r, obj, left, forced, item, designed=True):
        """The outcome lands at once, then the taste and the verdict after eating (section 5)."""
        delta = OUTCOME_MILLI[obj.nature]
        after = left + delta
        taste = self.cache.taste(obj.place, REPLICA_MAIN, obj.values)
        landing = self.host.land(name, delta, after, taste)
        protocol.check_landing(landing, self.spec)
        r.update({"ate": True, "forced": forced, "outcome_milli": delta, "energy_after_eat_milli": after,
                  "taste": list(taste), "landing": landing,
                  "action_provenance": "designed-exposure" if forced else r["mind"]["provenance"]})
        if designed:
            self.rec.exposures.append({"decision": r["decision"], "item": item, "test": "KILL_TEST",
                                       "item_role": obj.role,
                                       "choice_window_outcome": "forced" if forced else "chosen"})
        return landing

    def _write(self, name, r, item, line):
        w = self.host.write(name)
        protocol.check_write(w, self.spec)
        r["write"] = w
        if self.lineage is not None:
            r["filed_under"] = self.lineage[line].apply(w["events"], item)
        return w

    def _verdict_lid(self, line, verdict):
        if self.lineage is None or not isinstance(verdict, int):
            return verdict
        return self.lineage[line].lid(verdict)

    def _main_taste(self, number, item, obj):
        r, left = self._decide("main", number, item, obj, REPLICA_MAIN, "main")
        self._verdict_check("main", r)
        self._eat("main", r, obj, left, forced=True, item=item)       # every warm-up and teaching taste is forced
        self._write("main", r, item, "main")

    def _verdict_check(self, line, r):
        d = r["mind"]
        r["verdict_lid"] = self._verdict_lid(line, d["verdict"])
        if self.lineage is not None:
            lin = self.lineage[line]
            log = d.get("log", {})
            if "last_leader" in log and "within_margin" in log:
                ids = [lin.lid(s) if isinstance(s, int) else s for s in [log["last_leader"]] + log["within_margin"]]
                r["leader_and_runner_up_in_h"] = (len(ids) > 1 and ids[0] in lin.h
                                                  and any(i in lin.h for i in ids[1:]))     # (KT-69)

    # ------------------------------------------------------------ the checks

    def _probe(self, state, number, item, obj, replica):
        self.host.copy(state, "probe")
        try:
            r, _ = self._decide("probe", number, item, obj, replica, probe_role(obj))
        finally:
            self.host.drop("probe")
        self._verdict_check(state, r)
        r["ate"] = r["mind"]["action"] == "eat"         # a copy's eat ends the probe (KT-96)
        return r

    # ------------------------------------------------------------ the run

    def run(self, order=None, checks=True, checkpoints=CHECKPOINTS, branches=True):
        plan, spec, host = self.plan, self.spec, self.host
        host.new("main", self.birth)
        info = host.info("main")
        protocol.check_info(info, spec)
        self.rec.info = info
        self.rec.birth_dump = host.dump("main")
        protocol.check_dump(self.rec.birth_dump, spec)
        jobs = []
        if spec.warmup:
            for i, obj in enumerate(plan.warmup_sequence(), 1):
                self._main_taste(self.numbers[("warmup", i)], f"warmup-{i}", obj)
        for k, obj in enumerate(plan.teaching, 1):
            self._main_taste(self.numbers[("teach", k)], f"t{k}", obj)
            if k in CHECKPOINTS:
                host.copy("main", f"S{k}")
                self._remember_line(f"S{k}", "main")
                if checks and k in checkpoints:
                    for i, probe in enumerate(plan.P, 1):
                        jobs.append((("P", (k, i)), f"S{k}", probe, replica_p(k, i)))
        if branches:
            self._branches()
            if checks:
                for state in Q_STATES:
                    for i, probe in enumerate(plan.Q, 1):
                        jobs.append((("Q", (state, i)), state, probe, replica_q(i)))
        if order is not None:
            jobs = order(jobs)
        for key, state, probe, replica in jobs:
            kind, (where, i) = key
            item = f"P@S{where}#{i}" if kind == "P" else f"Q@{where}#{i}"
            r = self._probe(state, self.numbers[key], item, probe, replica)
            self.rec.probes.append({"decision": r["decision"], "state": state if kind == "P" else f"Q-{state}",
                                    "probe": i, "label": probe.label, "role": r["role"], "ate": r["ate"],
                                    "verdict": r["verdict_lid"], "names_h": self._names_h(state, r),
                                    "settled": r["mind"]["verdict"] != "unsettled"})
        self.rec.probes.sort(key=lambda p: p["decision"])
        full = checks and branches and tuple(checkpoints) == CHECKPOINTS
        expected = C.DECISIONS_PER_RUN if spec.warmup else C.DECISIONS_PER_RUN_NOWARM
        if full and len(self.rec.decisions) != expected:
            raise RunError(f"{len(self.rec.decisions)} decisions, not {expected} (section 5)")
        if len(self.rec.injections) != len(self.rec.decisions):
            raise RunError("every decision follows exactly one energy reset (W45)")
        self.rec.partial = not full
        if self.lineage is not None:
            main = self.lineage["main"]
            self.rec.h1_lid, self.rec.h1_new = main.h1, main.h1_new
            self.rec.lineage_log = [dict(e, line="main") for e in main.log]
            if branches:
                n = len(self.lineage["S8"].log)
                self.rec.lineage_log += [dict(e, line=b) for b in (SOUR, SWEET) for e in self.lineage[b].log[n:]]
        return self.rec

    # snapshots carry the lineage of the line they were taken from
    def _remember_line(self, state, line):
        if self.lineage is not None:
            self.lineage[state] = copy.deepcopy(self.lineage[line])
            self.rec.h_sets[state] = sorted(self.lineage[state].h)

    def _names_h(self, state, r):
        if self.lineage is None:
            return None
        return r["mind"]["action"] == "eat" and r["verdict_lid"] in self.lineage[state].h

    def _branches(self):
        """SOUR and SWEET-CONTROL from S8, sharing one replica key (KT-16, KT-87, KT-99)."""
        plan, spec, host = self.plan, self.spec, self.host
        h2 = plan.h2
        decisions = {}
        for branch, step in ((SOUR, ("branch", SOUR)), (SWEET, ("branch", SWEET))):
            host.copy("S8", branch)
            if self.lineage is not None:
                self.lineage[branch] = copy.deepcopy(self.lineage["S8"])
            r, left = self._decide(branch, self.numbers[step], f"h2-{branch}", h2, REPLICA_SOUR_BRANCHES, "h2")
            self._verdict_check(branch, r)
            decisions[branch] = (r, left)
        a, b = decisions[SOUR][0]["mind"], decisions[SWEET][0]["mind"]
        if a != b:
            raise RunError("the h2 decision differs between SOUR and SWEET-CONTROL (KT-16)")
        verdict = decisions[SOUR][0]["verdict_lid"]
        sc_values, candidate, ranges = self._sweet_control_values(verdict)
        sweet_obj = dataclasses.replace(h2, values=sc_values)
        noticed = {"candidate": candidate, "h2_verdict": verdict}
        for branch, obj, item in ((SOUR, h2, "h2"), (SWEET, sweet_obj, "sweet")):
            r, left = decisions[branch]
            forced = r["mind"]["action"] == "skip"           # forced if skipped, and flagged (section 5)
            self._eat(branch, r, obj, left, forced=forced, item=f"h2-{branch}")
            dump = host.dump(branch)
            protocol.check_dump(dump, spec)
            noticed[branch] = {"taste": r["taste"], "candidate_record": _candidate_record(dump, self, branch,
                                                                                         candidate)}
            self._write(branch, r, item, branch)
            if self.lineage is not None:
                noticed[branch]["write_types"] = [e["type"] for e in r["write"]["events"]]
                self.rec.h_sets[branch] = sorted(self.lineage[branch].h)
            else:
                noticed[branch]["write_types"] = []
        if self.lineage is not None and noticed[SOUR]["candidate_record"] != noticed[SWEET]["candidate_record"]:
            raise RunError("the SWEET-CONTROL candidate's record differs between branches before their writes")
        noticed["sweet_control_taste_values"] = [sc_values[t] for t in traits.TASTE_INDICES]
        noticed["taste_ranges_stored"] = ranges
        self.rec.taste_noticed = noticed

    def _sweet_control_values(self, verdict):
        """h2 with its 4 taste values replaced (section 5, KT-65, KT-99)."""
        plan, h2 = self.plan, self.plan.h2
        candidate = None
        ranges = None
        if self.lineage is not None:
            lin = self.lineage["S8"]
            candidate = verdict if verdict in lin.h else lin.h1
            dump = self.host.dump("S8")
            protocol.check_dump(dump, self.spec)
            ranges = _taste_ranges(dump, lin, candidate)
        if ranges is None:
            taste = [plan.h1.values[t] for t in traits.TASTE_INDICES]        # h1's taste values (section 5)
        else:
            taste = [(lo + hi) / 2 for lo, hi in ranges]
            if not all(0.0 <= x <= 1.0 for x in taste):
                raise RunError(f"a SWEET-CONTROL taste centre lies outside 0 to 1: {taste} (KT-99)")
        values = list(h2.values)
        for t, x in zip(traits.TASTE_INDICES, taste):
            values[t] = x
        return tuple(values), candidate, ranges


def _slot_of(lin, lid):
    for slot, l in lin.slot_lid.items():
        if l == lid:
            return slot
    return None


def _taste_ranges(dump, lin, lid):
    slot = _slot_of(lin, lid)
    for c in dump["candidates"]:
        if c["slot"] == slot:
            ranges = [c["ranges"][t] for t in traits.TASTE_INDICES]
            return None if ranges[0] is None else [tuple(r) for r in ranges]
    return None


def _candidate_record(dump, run, branch, lid):
    """The SWEET-CONTROL candidate's taste ranges and weights at the verdict after eating (section 8)."""
    if run.lineage is None or lid is None:
        return None
    slot = _slot_of(run.lineage[branch], lid)
    for c in dump["candidates"]:
        if c["slot"] == slot:
            return {"slot": slot,
                    "ranges": [c["ranges"][t] for t in traits.TASTE_INDICES],
                    "weights_tenths": [c["weights_tenths"][t] for t in traits.TASTE_INDICES]}
    return {"slot": slot, "ranges": None, "weights_tenths": None}


def make_host(spec, package_dir=None, hash_seed="0"):
    if spec.host == "in-process":
        return InProcessHost(factory_from(spec.entry))
    if package_dir is None:
        raise RunError(f"{spec.label} runs in its own process and needs its package's directory")
    return SubprocessHost(package_dir, hash_seed=hash_seed)


def birth_config(plan, spec, extra=None) -> dict:
    """What a mind is told at birth: R, b, the run's trait order for tower minds, its own settings (KT-97)."""
    cfg = {"reserve_milli": plan.reserve_milli, "boldness": plan.boldness, "params": dict(spec.params)}
    if spec.mind_class == "tower":
        cfg["trait_order"] = list(plan.trait_order)
    if spec.oracle_core:
        cfg["params"]["core"] = list(plan.family.H.core)        # B2e alone (X03)
    if extra:
        cfg["params"].update(extra)
    return cfg


def run_one(plan, spec, cache, *, host=None, package_dir=None, extra=None, order=None, checks=True,
            checkpoints=CHECKPOINTS, branches=True, hash_seed="0") -> RunRecord:
    """Run one mind's life on one run plan. Stops with an error on any departure (KT-95).

    Every error names the mind, the set, the family and the run.
    """
    where = f"{spec.label} on {plan.set_name} family {plan.family_number} run {plan.run_number}"
    own = host is None
    try:
        if own:
            host = make_host(spec, package_dir, hash_seed)
        return _Run(plan, spec, host, cache, birth_config(plan, spec, extra)).run(
            order=order, checks=checks, checkpoints=checkpoints, branches=branches)
    except (MindError, protocol.InterfaceError, RunError) as e:
        raise RunError(f"{where}: {e}") from e
    finally:
        if own and host is not None:
            host.close()
