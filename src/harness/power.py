"""The power check (section 7, step 4): MK10 through the frozen judge on simulated sets.

Simulated set s takes, at place i, practice family 1,000 + (s - 1) x 120 + i,
with the core-trait placement of tuning family ((i - 1) mod 30) + 1 (KT-42).
A set of size N uses places 1 to N, so sizes nest. Each set's floor comes from
the frozen B1n-bot-r and B1n-mind run on that set's own families, 10 runs
each. Only their D_learn is needed, so those runs stop after S8's checks and
skip checks 1, SOUR, SWEET-CONTROL and Q (KT-104).

The mock's records then go through judge.judge(), the code that will judge
K-F, with rule 6 off. 1,000 sets are simulated at each size. The mock must
reach GO in at least 80% of them. The size starts at 40 and rises by 20 until
it does (X39); if 120 isn't enough, the bench is redesigned.

This is a go/no-go check on the design of the bench, not evidence about K-F.
"""

import json
import pathlib
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction

import numpy as np

from test_fixtures import mk10
from world import keys, sets
from world.run_plan import generate_run

from . import agents, judge, scoring
from .bench import RUNS_PER_FAMILY, core_placement
from .readings_cache import ReadingCache
from .run import run_one

SIZES = (40, 60, 80, 100, 120)       # set sizes tried, in order (section 7, X39)
SIMULATED_SETS = 1_000               # 1,000 sets at each size (section 7)
PASS_SHARE = Fraction(80, 100)       # GO in at least 80% of simulated sets (section 7)
FLOOR_CHECKS = (2, 4, 6, 8)          # a floor run's checks: D_learn's alone (KT-104)
TUNING_CORES = None


def _tuning_cores():
    global TUNING_CORES
    if TUNING_CORES is None:
        TUNING_CORES = [f.H.core for f in sets.tuning_families()]
    return TUNING_CORES


def place_family(simulated_set: int, place: int):
    """(family number, family) at a place of a simulated set (KT-42)."""
    number = sets.power_check_family_number(simulated_set, place)
    core = _tuning_cores()[(place - 1) % len(_tuning_cores())]
    return number, sets.practice_family(number, core_override=core)


def floor_family(job) -> dict:
    """The floor minds' D_learn on every run of one simulated family (KT-104)."""
    simulated_set, place, specs = job
    number, family = place_family(simulated_set, place)
    out = {"set": simulated_set, "place": place, "family": number, "core": core_placement(family)}
    key = keys.tuning_set_key()
    for spec in specs:
        out[spec.agent_type] = []
    for r in range(1, RUNS_PER_FAMILY + 1):
        plan = generate_run("practice", key, number, r, family=family)
        if tuple(plan.family.H.core) != tuple(_tuning_cores()[(place - 1) % 30]):
            raise RuntimeError("a practice family lost its core placement")
        cache = ReadingCache(plan.noise_key)
        for spec in specs:
            rec = run_one(plan, spec, cache, checkpoints=FLOOR_CHECKS, branches=False)
            out[spec.agent_type].append(str(scoring.measures(rec)["d_learn_beh"]))
    return out


class FloorStore:
    """The floor runs, one line per simulated family, kept so a long check can resume."""

    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.rows = {}
        if self.path.exists():
            for line in self.path.read_text().splitlines():
                if line.strip():
                    row = json.loads(line)
                    self.rows[(row["set"], row["place"])] = row

    def missing(self, n_sets, size):
        return [(s, i) for s in range(1, n_sets + 1) for i in range(1, size + 1) if (s, i) not in self.rows]

    def add(self, row):
        self.rows[(row["set"], row["place"])] = row
        with self.path.open("a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")


def run_floors(store, n_sets, size, specs, workers=1, progress=None):
    todo = store.missing(n_sets, size)
    jobs = [(s, i, tuple(specs)) for s, i in todo]
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for k, row in enumerate(pool.map(floor_family, jobs, chunksize=1), 1):
                store.add(row)
                if progress:
                    progress(k, len(jobs))
    else:
        for k, job in enumerate(jobs, 1):
            store.add(floor_family(job))
            if progress:
                progress(k, len(jobs))


def judge_simulated_set(store, simulated_set, size, spreads) -> dict:
    """One simulated set of the given size, judged by the frozen judge with rule 6 off."""
    floor_minds = {name: {} for name in judge.FLOOR_MINDS}
    core_of = {}
    rows = [store.rows[(simulated_set, i)] for i in range(1, size + 1)]
    for row in rows:
        core_of[row["family"]] = row["core"]
        for name in judge.FLOOR_MINDS:
            for r, v in enumerate(row[name], 1):
                floor_minds[name][(row["family"], r)] = {"d_learn_beh": Fraction(v)}
    fmind, fval = judge.floor(floor_minds)
    kf, os10 = {}, {}
    for i, row in enumerate(rows, 1):
        k, o = mk10.family_runs(simulated_set, i, row["family"], float(fval), spreads)
        kf.update(k)
        os10.update(o)
    res = judge.judge(f"power-check/{simulated_set}", kf, floor_minds[fmind], fval, os10, core_of)
    return {"set": simulated_set, "size": size, "floor_mind": fmind, "floor": fval,
            "verdict": res["verdict"], "label": res["label"], "causes": res["causes"],
            "rule1": res["1"]["pass"], "rule2": res["2"]["pass"], "rule3_bootstrap": res["3"]["bootstrap_pass"]}


def power_at(store, size, spreads, n_sets=SIMULATED_SETS) -> dict:
    results = [judge_simulated_set(store, s, size, spreads) for s in range(1, n_sets + 1)]
    go = sum(1 for r in results if r["verdict"] == "GO")
    fails = {}
    for r in results:
        if not r["rule1"]:
            fails["rule 1"] = fails.get("rule 1", 0) + 1
        if not r["rule2"]:
            fails["rule 2"] = fails.get("rule 2", 0) + 1
        if not r["rule3_bootstrap"]:
            fails["rule 3 bootstrap"] = fails.get("rule 3 bootstrap", 0) + 1
        for c in r["causes"]:
            fails[c] = fails.get(c, 0) + 1
    return {"size": size, "sets": n_sets, "go": go, "go_share": Fraction(go, n_sets),
            "passes": Fraction(go, n_sets) >= PASS_SHARE, "fails": fails, "sets_detail": results}


def report_header(spreads) -> dict:
    return {"what": "power check (section 7, step 4): a go/no-go check on the bench's design, not evidence",
            "mk10_seed_text": mk10.SEED_TEXT, "bootstrap_seed_text": judge.BOOTSTRAP_SEED_TEXT,
            "numpy": np.__version__, "spreads": spreads}


def floor_specs(r_bot, r_mind):
    return [agents.b1n_bot_r(r_bot), agents.b1n_mind(r_mind)]
