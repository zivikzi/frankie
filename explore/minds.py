"""The minds Frankie Lab compares, and running them through the frozen harness.

Every mind runs through harness.run.run_one and is scored by
harness.scoring.measures, so every number means exactly what it means in the
kill test. Nothing here changes the harness, the bots or K-F.

- B1n-bot-r: trial and error at its registered radius (the floor to beat).
- B1n-mind: trial and error inside Frankie's drive (the other floor mind).
- B2e: the answer-key control (reads the hidden core traits; shows the best
  possible score).
- K-F: as registered after Week 4 (kill-test/TUNED.md), hosted in this
  process (KT-93: the same records as its own process).
- E1 and its variants (explore/e1.py), defined in VARIANTS.
"""

import dataclasses
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
for p in (ROOT / "src", ROOT / "explore"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from harness import agents, judge, scoring  # noqa: E402
from harness import constants as C  # noqa: E402
from harness.readings_cache import ReadingCache  # noqa: E402
from harness.run import run_one  # noqa: E402
from mind import constants as K  # noqa: E402
from world import keys  # noqa: E402
from world.run_plan import generate_run  # noqa: E402

import e1  # noqa: E402

ODD = tuple(range(1, 31, 2))            # where E1 is developed (the search half)
EVEN = tuple(range(2, 31, 2))           # reported as a check, never tuned on
RUNS = 10

# E1 variants: name -> E1 settings. "E1" is the variant with the best D_learn on the search half (odd families)
# after the exploration logged in explore/results/variants.jsonl; the others switch one idea off.
E1_BEST = {"tol_nw": 10, "threshold": 1.0, "stretch_down": 5, "merge_cutoff": 5, "merge_context": True,
           "merge_widen": True}
VARIANTS = {
    "E1": dict(E1_BEST),
    "E1 no merging": dict(E1_BEST, merge=False),
    "E1 all at once": dict(E1_BEST, outside_in=False),
    "E1 as first written": {},
}


def e1_spec(name, params=None):
    params = dict(VARIANTS.get(name, {}) if params is None else params)
    return agents.AgentSpec(agent_type="E1", label=name, mind_class="tower", entry="e1:make", host="in-process",
                            pays_look=True, thinking_unit="check", unit_nano=C.CHECK_NANO, unit_row="B14",
                            version=tuple(e1.version_of(name)), params=dict(params, name=name))


def spec(name, params=None):
    if name == "B1n-bot-r":
        return agents.b1n_bot_r(agents.RADIUS_B1N_BOT_R)
    if name == "B1n-mind":
        return agents.b1n_mind(agents.RADIUS_B1N_MIND)
    if name in ("B2e", "B1n-bot", "G08"):
        return agents.plain_bot(name)
    if name == "K-F":
        kf = agents.tower_minds(K.SPIKE_NANO)[0]
        return dataclasses.replace(kf, host="in-process", entry="mind.entry:make")
    if name.startswith("E1"):
        return e1_spec(name, params)
    raise ValueError(f"no mind called {name!r}")


def plan_of(family, run):
    return generate_run("tuning", keys.tuning_set_key(), family, run)


def run_record(name, family, run, params=None, host=None):
    plan = plan_of(family, run)
    return plan, run_one(plan, spec(name, params), ReadingCache(plan.noise_key), host=host)


def one(job):
    name, params, family, run = job
    plan, rec = run_record(name, family, run, params)
    m = scoring.measures(rec)
    core = "object" if any(t in (2, 3, 4, 5) for t in plan.family.H.core) else "none"
    return name, family, run, core, m


FIELDS = ("settle_rate", "copy_accept", "d_learn", "fmn", "lr_h1", "lr_far", "dq_sour", "sour_drop", "noticed",
          "d_1", "d_2", "d_4", "d_6", "d_8")


def summary(runs: dict, tower: bool) -> dict:
    """Set means (mean of family means, as the judge takes them) of the measures the Lab shows."""
    k = "strict" if tower else "beh"
    src = {"settle_rate": "settle_rate", "copy_accept": "copy_accept", "d_learn": f"d_learn_{k}",
           "fmn": f"fmn_{k}", "lr_h1": "lr_h1", "lr_far": "lr_far", "dq_sour": f"dq_sour_{k}",
           "sour_drop": f"sour_drop_{k}", "noticed": "noticed"}
    for c in (1, 2, 4, 6, 8):
        src[f"d_{c}"] = f"d_{k}_{c}"
    out = {}
    for name, field in src.items():
        if any(field not in m for m in runs.values()):
            continue
        out[name] = float(judge.set_mean(runs, field))
    out["runs"] = len(runs)
    return out
