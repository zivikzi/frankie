"""One kill-run set, in the frozen order (sections 3 and 9).

1. The set is generated from its key, and every plan passes its certificates.
2. Every non-tower mind runs, and rule 6 is judged before any tower mind runs.
   If it fails, the set is retired with no verdict.
3. The tower minds run. On each run key K-F runs first, since OS01-cap's
   limit is K-F's median thinking spend in that run (KT-67).
4. The judge applies rules 1 to 5 and 7 and the verdict order, and the
   verdict table is printed before any per-family result.

The tuning set and practice families never come through here (section 3).
"""

from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction

from world import keys, sets
from world.run_plan import generate_run

from . import agents, bench, judge, scoring
from .readings_cache import ReadingCache
from .run import run_one

KILL_RUN_SETS = ("A", "B", "C")


def median_thinking_nano(rec, unit_nano) -> Fraction:
    """K-F's median per-decision thinking spend in one run, counting thinking only (KT-67)."""
    spends = sorted(d["mind"]["thinking"]["count"] * unit_nano for d in rec.decisions.values())
    n = len(spends)
    return Fraction(spends[n // 2]) if n % 2 else Fraction(spends[n // 2 - 1] + spends[n // 2], 2)


def _tower_run(job):
    set_name, set_key, family, run, specs, dirs = job
    plan = generate_run(set_name, set_key, family, run)
    bench.certify(plan, set_key)
    cache = ReadingCache(plan.noise_key)
    out, kf = {}, None
    for spec in specs:
        extra = None
        if spec.after:
            cap = median_thinking_nano(kf, spec_unit(specs, spec.after))
            extra = {"cap_nano": [cap.numerator, cap.denominator]}
        rec = run_one(plan, spec, cache, package_dir=dirs[spec.entry], extra=extra)
        if spec.label == "K-F":
            kf = rec
        out[spec.label] = scoring.measures(rec)
    return family, run, out


def spec_unit(specs, label):
    return next(s.unit_nano for s in specs if s.label == label)


def run_kill_set(set_name, block_hash_hex, n_families, tower_specs, package_dirs, workers=1, runs=None,
                 progress=None) -> dict:
    """The whole set in the frozen order. Returns the record the report is written from."""
    if set_name not in KILL_RUN_SETS:
        raise ValueError(f"the kill-run sets are {KILL_RUN_SETS}")
    runs = runs or bench.RUNS_PER_FAMILY
    set_key = keys.kill_run_set_key(block_hash_hex)
    families = sets.kill_run_families(set_name, block_hash_hex, n_families)
    sets.require_separation(set_name, set_key, families)
    numbers = [f.number for f in families]
    non_tower = agents.bench_minds()
    measures, core_of, _ = bench.run_set(set_name, set_key, numbers, non_tower, runs=runs, workers=workers,
                                         progress=progress)
    by_type = {s.agent_type: measures[s.label] for s in non_tower}
    r6 = judge.rule6(set_name, by_type, core_of, list(agents.MUST_FAIL))
    out = {"set": set_name, "families": n_families, "runs_per_family": runs, "rule6": r6,
           "floor_mind": r6["floor_mind"], "floor": r6["floor"]}
    if not r6["holds"]:
        out["retired"] = True
        out["verdict"] = None
        return out
    if [s.label for s in tower_specs][:1] != ["K-F"]:
        raise ValueError("K-F runs first on each run key (KT-67)")
    jobs = [(set_name, set_key, f, r, tuple(tower_specs), dict(package_dirs)) for f in numbers
            for r in range(1, runs + 1)]
    tower = {s.label: {} for s in tower_specs}
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            done = list(pool.map(_tower_run, jobs, chunksize=1))
    else:
        done = [_tower_run(j) for j in jobs]
    for f, r, res in done:
        for label, m in res.items():
            tower[label][(f, r)] = m
    verdict = judge.judge(set_name, tower["K-F"], by_type[r6["floor_mind"]], r6["floor"], tower["OS10"], core_of)
    out.update(retired=False, verdict=verdict["verdict"], label=verdict["label"], judged=verdict,
               reported={label: {"d_learn_strict": judge.set_mean(m, "d_learn_strict"),
                                 "settle_rate": judge.set_mean(m, "settle_rate")}
                         for label, m in tower.items() if label != "K-F"})
    return out


def verdict_table(result) -> str:
    """The verdict table, printed before anyone sees a per-family result (section 3)."""
    if result.get("retired"):
        bots = [b for b, row in result["rule6"]["bots"].items() if not row["fails_one"]]
        return f"Set {result['set']}: rule 6 failed ({', '.join(bots)} passed all five). Retired, no verdict."
    v = result["judged"]
    lines = [f"Set {result['set']}: {result['verdict']}" + (f" ({result['label']})" if result["label"] else ""),
             f"  floor: {result['floor_mind']} {float(result['floor']):.4f}",
             f"  rule 1 settle rate {float(v['1']['value']):.4f} {'pass' if v['1']['pass'] else 'FAIL'}",
             f"  rule 2 CopyAccept {float(v['2']['value']):.4f} {'pass' if v['2']['pass'] else 'FAIL'}",
             f"  rule 3 D_learn {float(v['3']['value']):.4f}; margin {'pass' if v['3']['margin_pass'] else 'FAIL'};"
             f" bootstrap {v['3']['bootstrap_at_or_below_0']} of 10,000 at or below 0"
             f" {'pass' if v['3']['bootstrap_pass'] else 'FAIL'}"]
    for rule in ("4", "4b", "4c"):
        vals = ", ".join(f"{k} {float(x):.4f}" for k, x in v["disc"][rule]["values"].items())
        lines.append(f"  rule {rule} {vals} {'pass' if v['disc'][rule]['pass'] else 'FAIL'}")
    lines.append(f"  rule 5 sour drop {float(v['5']['sour_drop']):.4f}, Q {float(v['5']['q']):.4f}, noticed "
                 f"{float(v['5']['noticed']):.4f}, OS10 quiet {float(v['5']['os10_not_noticing']):.4f} "
                 f"{'pass' if v['5']['pass'] else ('uninformative' if not v['5']['applicable'] else 'FAIL')}")
    lines.append(f"  rule 7 D_strict at check 1 {float(v['7']['value']):.4f} {'pass' if v['7']['pass'] else 'FAIL'}")
    return "\n".join(lines)
