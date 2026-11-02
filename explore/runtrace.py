"""One run of one mind, recorded step by step for the Lab's "watch a run" view.

The run is the frozen harness's own run (harness.run.run_one). A thin wrapper
around the in-process host records what the mind was shown (its 18 readings)
and its memory after each write. It changes nothing the mind sees or does:
dump() is read-only, and the harness's own checks still run on every answer.
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import minds  # noqa: E402

from harness import scoring  # noqa: E402
from harness.host import InProcessHost, factory_from  # noqa: E402
from harness.readings_cache import ReadingCache  # noqa: E402
from harness.run import run_one  # noqa: E402
from world import traits  # noqa: E402

TRACES = minds.ROOT / "explore" / "results" / "traces"
LAYER_SPANS = [["context", 0, 2], ["object", 2, 6], ["parts", 6, 11], ["details", 11, 18], ["taste", 18, 22]]


class Recorder:
    """Passes every call through; keeps the readings each decision saw and the memory after each write."""

    def __init__(self, inner):
        self.inner = inner
        self.shown = []
        self.after_write = []

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def decide(self, name, visible, energy_milli):
        self.shown.append((name, [float(x) for x in visible], int(energy_milli)))
        return self.inner.decide(name, visible, energy_milli)

    def write(self, name):
        out = self.inner.write(name)
        self.after_write.append((name, self.inner.dump(name)))
        return out


def _role(d):
    label, item = d.get("label", ""), d.get("item", "")
    if item.startswith("warmup"):
        return "warm-up item"
    names = {"h1": "h1: the first apple (super-sweet)", "a2": "teaching apple a2", "a3": "teaching apple a3",
             "a4": "teaching apple a4", "t2": "teaching look-alike of h1 (poison)",
             "t4": "teaching look-alike of a2 (poison)", "t6": "teaching look-alike of a3 (poison)",
             "t8": "teaching look-alike of a4 (poison)"}
    if label in names:
        return names[label]
    if item == "h2-SOUR":
        return "h2: a new far apple, super-SOUR (the sour test)"
    if item == "h2-SWEET-CONTROL":
        return "h2 with sweet taste (SWEET-CONTROL)"
    role = d.get("role", "")
    return {"far": "far apple (looks different from h1)", "look-h1": "look-alike of h1 (poison)",
            "look-far": "look-alike of a far apple (poison)", "neutral": "neutral (a never-seen 'nothing' kind)",
            "copy": "exact copy of h1", "apple": "apple near h1 or h2",
            "look-h2": "look-alike of h2 (poison)"}.get(role, role or label)


def _phase(d):
    item = d.get("item", "")
    if item.startswith("warmup"):
        return "warm-up"
    if item.startswith("t") and item[1:].isdigit():
        return "teaching"
    if item.startswith("h2"):
        return "sour test"
    return f"check {d.get('state', '')}".strip()


def _r(x):
    return None if x is None else round(float(x), 4)


def _kinds(dump, slot_lid, h):
    out = []
    for c in dump.get("candidates", []):
        lid = slot_lid.get(c["slot"])
        out.append({"slot": c["slot"], "lid": lid, "in_h": lid in h if lid else False,
                    "ranges": [None if r is None else [_r(r[0]), _r(r[1])] for r in c["ranges"]],
                    "weights": c["weights_tenths"], "eats": c["eats"],
                    "record": (c.get("log") or {}).get("record")})
    return out


def record(name, family, run, params=None):
    plan = minds.plan_of(family, run)
    spec = minds.spec(name, params)
    inner = InProcessHost(factory_from(spec.entry)) if spec.host == "in-process" else None
    if inner is None:
        raise ValueError("the Lab records in-process minds only")
    host = Recorder(inner)
    rec = run_one(plan, spec, ReadingCache(plan.noise_key), host=host)
    numbers = sorted(rec.decisions)
    state_of = {pr["decision"]: pr["state"] for pr in rec.probes}
    lineage = list(rec.lineage_log)
    ptr = 0
    lines = {"main": {}}
    in_h = set().union(*[set(v) for v in rec.h_sets.values()]) if rec.h_sets else set()
    memories, writes = [], iter(host.after_write)
    last_mem = {"main": None}
    steps = []
    for i, n in enumerate(numbers):
        d = rec.decisions[n]
        visible = d["visible"]                             # what the mind was shown (the harness keeps it)
        mind = d["mind"]
        item = d.get("item", "")
        line = "main" if d.get("role") == "main" else (item.replace("h2-", "") if d.get("role") == "h2" else None)
        step = {"n": n, "phase": _phase(d), "item": item, "role": _role(d), "visible": [_r(x) for x in visible],
                "taste": [_r(x) for x in d["taste"]] if d.get("taste") else None,
                "verdict": mind["verdict"], "verdict_lid": d.get("verdict_lid"), "action": mind["action"],
                "ate": d.get("ate"), "forced": d.get("forced", False), "outcome": d.get("outcome_milli"),
                "energy_set": d.get("energy_set_milli"), "energy_choice": d.get("energy_at_choice_milli"),
                "energy_after": d.get("energy_after_eat_milli"), "log": mind.get("log") or {},
                "landing": (d.get("landing") or {}).get("verdict"), "events": [], "merges": [], "names_h": None}
        step["memory_before"] = (last_mem.get(line, last_mem["main"]) if line else None)
        if "write" in d:
            w = d["write"]
            events = w.get("events", [])
            step["events"] = [{k: e[k] for k in ("type", "slot", "parent_slot")} for e in events]
            step["merges"] = (w.get("log") or {}).get("merges", [])
            if line not in lines:
                lines[line] = dict(lines["main"])              # a sour-test branch starts from S8's memory
            sl = lines[line]
            for e in lineage[ptr:ptr + len(events)]:
                if e["type"] == "forget":
                    sl.pop(e["slot"], None)
                else:
                    sl[e["slot"]] = e["lid"]
            ptr += len(events)
            _, dump = next(writes)
            memories.append(_kinds(dump, sl, in_h))
            last_mem[line] = len(memories) - 1
        state = state_of.get(n, "")
        if step["memory_before"] is None:
            step["memory_before"] = last_mem.get(state[2:]) if state.startswith("Q-") and state[2:] in last_mem \
                else last_mem["main"]
        if state.startswith("Q-") and state[2:] in last_mem:
            step["memory"] = last_mem[state[2:]]
        else:
            step["memory"] = last_mem.get(line, last_mem["main"]) if line else last_mem["main"]
        steps.append(step)
    for p in rec.probes:                                    # the check copies' own facts, joined by decision number
        for s in steps:
            if s["n"] == p["decision"]:
                s["names_h"] = p.get("names_h")
                s["phase"] = f"check {p['state']}"
    m = scoring.measures(rec)
    keep = {k: (float(v) if not isinstance(v, (str, bool, type(None))) else v) for k, v in m.items()
            if not isinstance(v, (list, dict))}
    return {"mind": name, "family": family, "run": run, "half": "odd" if family % 2 else "even",
            "mind_class": rec.mind_class, "reserve": plan.reserve_milli, "boldness": plan.boldness,
            "traits": list(traits.TRAITS), "layers": LAYER_SPANS, "core": sorted(plan.family.H.core),
            "h1_lid": rec.h1_lid, "h_set": sorted(rec.h_sets.get("S8", [])), "steps": steps, "memories": memories,
            "measures": keep}


def path_for(name, family, run):
    return TRACES / f"{name.replace(' ', '_')}__{family}__{run}.json"


def get(name, family, run, params=None, cache=True):
    p = path_for(name, family, run)
    if cache and p.exists():
        return json.loads(p.read_text())
    t = record(name, family, run, params)
    if cache:
        TRACES.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(t, separators=(",", ":")))
    return t
