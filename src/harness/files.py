"""The bench's plain per-run files (section 11, "Kept lean"): the key record, the verdict trace,
and the list of designed exposures and injections, which stands in for the priors card.

One JSON file per run of each mind, written with sorted keys so it replays
byte for byte. The full log schema and the Parquet chain wait for Stage 1.
"""

import hashlib
import json
import pathlib

TRACE_FIELDS = ("decision", "item", "label", "role", "replica", "energy_set_milli", "look_milli",
                "thinking_milli", "energy_at_choice_milli", "verdict_lid", "forced", "outcome_milli",
                "energy_after_eat_milli", "action_provenance", "filed_under", "leader_and_runner_up_in_h")


def key_record(plan) -> dict:
    return {"set": plan.set_name, "family": plan.family_number, "run": plan.run_number,
            "reserve_milli": plan.reserve_milli, "boldness": plan.boldness, "trait_order": list(plan.trait_order),
            "h_is_tuning_family": plan.h_is_tuning_family,
            "noise_key_sha256": hashlib.sha256(plan.noise_key.to_bytes(32, "little")).hexdigest()}


def verdict_trace(rec) -> list:
    out = []
    for n in sorted(rec.decisions):
        d = rec.decisions[n]
        row = {k: d[k] for k in TRACE_FIELDS if k in d}
        mind = d["mind"]
        row.update({"verdict": mind["verdict"], "settle_step": mind["settle_step"], "action": mind["action"],
                    "thinking": mind["thinking"], "provenance": mind["provenance"]})
        if mind["drive"] is not None:
            row["drive"] = mind["drive"]
        if "landing" in d:
            row["verdict_after_eating"] = d["landing"]["verdict"]
        if "write" in d and d["write"]["events"]:
            row["writes"] = d["write"]["events"]
        out.append(row)
    return out


def run_file(rec, plan) -> dict:
    return {"key_record": key_record(plan), "mind": {"label": rec.label, "agent_type": rec.agent_type,
                                                     "class": rec.mind_class, "info": rec.info},
            "verdict_trace": verdict_trace(rec), "designed_exposures": rec.exposures, "injections": rec.injections,
            "lineage_log": rec.lineage_log, "h_sets": rec.h_sets, "taste_noticed": rec.taste_noticed,
            "partial": rec.partial}


def write_run(rec, plan, out_dir) -> pathlib.Path:
    path = pathlib.Path(out_dir) / plan.set_name / rec.label / f"f{plan.family_number:04d}-r{plan.run_number:02d}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(run_file(rec, plan), sort_keys=True, separators=(",", ":")) + "\n")
    return path
