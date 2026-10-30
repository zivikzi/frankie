"""Running minds over a set of families, and choosing the radii (sections 3, 4 and 7).

Every mind sees the same run plans in the same order (X38 matching): for each
family and run key the plan and its readings are made once and every mind runs
on them. Runs are independent, so they may be spread over worker processes;
the results don't depend on how.
"""

from concurrent.futures import ProcessPoolExecutor

from world import sets, traits
from world.certificates import verify_run_plan
from world.run_plan import generate_run, tuning_family

from . import agents, scoring
from .readings_cache import ReadingCache
from .run import run_one

RUNS_PER_FAMILY = 10      # each family gets 10 runs per mind (section 5)


def core_placement(family) -> str:
    """Where H's core traits sit: "object" if any is in the object layer, else "none" (section 9)."""
    return "object" if any(traits.LAYER_OF[traits.TRAITS[t]] == "object" for t in family.H.core) else "none"


class CertificateError(RuntimeError):
    """A kill-run plan failed a certificate. The script stops (KT-88, KT-95)."""


def certify(plan, set_key):
    """Every rule of the plan re-checked from scratch, and the separation certificate (KT-38, KT-88)."""
    failures = verify_run_plan(plan, tuning_family)
    failures += sets.separation_failures(plan.set_name, set_key, [plan.family], [plan])
    if failures:
        raise CertificateError(f"{plan.set_name} family {plan.family_number} run {plan.run_number}: {failures}")


def _one_run(job):
    set_name, set_key, family, run, specs, keep_records = job
    plan = generate_run(set_name, set_key, family, run)
    if set_name not in ("tuning", "practice"):
        certify(plan, set_key)
    cache = ReadingCache(plan.noise_key)
    out, records = {}, {}
    for spec in specs:
        rec = run_one(plan, spec, cache)
        out[spec.label] = scoring.measures(rec)
        if keep_records:
            records[spec.label] = rec
    return family, run, core_placement(plan.family), out, records, plan if keep_records else None


def run_set(set_name, set_key, families, specs, runs=RUNS_PER_FAMILY, workers=1, keep_records=False,
            progress=None):
    """Every spec on every run of every family. Returns (measures, core_of, records).

    measures[label][(family, run)] is that run's measure record (scoring.measures).
    """
    if any(s.test_only for s in specs):
        raise ValueError("the stub and its variants never run on a set (section 7)")
    jobs = [(set_name, set_key, f, r, tuple(specs), keep_records) for f in families for r in range(1, runs + 1)]
    measures = {s.label: {} for s in specs}
    records = {s.label: {} for s in specs}
    core_of, plans = {}, {}
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for k, done in enumerate(pool.map(_one_run, jobs, chunksize=1), 1):
                _collect(measures, records, core_of, plans, *done)
                if progress:
                    progress(k, len(jobs))
    else:
        for k, job in enumerate(jobs, 1):
            _collect(measures, records, core_of, plans, *_one_run(job))
            if progress:
                progress(k, len(jobs))
    if keep_records:
        records["plans"] = plans
    return measures, core_of, records


def _collect(measures, records, core_of, plans, f, r, core, out, recs, plan):
    core_of[f] = core
    for label, m in out.items():
        measures[label][(f, r)] = m
    for label, rec in recs.items():
        records[label][(f, r)] = rec
    if plan is not None:
        plans[(f, r)] = plan


def radius_grid_specs():
    """B1n-bot-r, B1n-mind, G16 and G18 at every radius on the grid (section 4)."""
    return [make(r) for make in (agents.b1n_bot_r, agents.b1n_mind, agents.g16, agents.g18)
            for r in agents.RADIUS_GRID]


def choose_radius(measures, make) -> tuple:
    """The grid radius that maximises the mind's mean D_learn (D_beh) on the tuning set (section 4).

    Equal means go to the smaller radius, the earlier one on the grid (KT-101).
    Returns (radius, {radius: mean}).
    """
    from .judge import set_mean
    table = {r: set_mean(measures[make(r).label], "d_learn_beh") for r in agents.RADIUS_GRID}
    best = agents.RADIUS_GRID[0]
    for r in agents.RADIUS_GRID[1:]:
        if table[r] > table[best]:
            best = r
    return best, table
