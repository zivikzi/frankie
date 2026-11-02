"""E1 in the mind package (src/mind/e1.py, kill-test/E1_ADDENDUM.md, KT-132 to KT-138).

- Hand-made cases: elimination outside in, stretch, split, merging and how a
  merge is reported to the frozen harness, the sour fix (taste keeps its
  relevance) and E1-OS10.
- E1 and E1-OS10 give the same record in their own sandboxed process as in
  this one, and pass the charter's automatic mind checks.
- The kill-run driver (kill-test/e1_kill_run.py) runs in the frozen order on a
  tiny slice of the tuning set, and refuses a kill-run set without set A's
  manifest.
"""

import dataclasses
import json
import pathlib
import sys

import numpy as np
import pytest

from harness import agents
from harness.readings_cache import ReadingCache
from harness.run import run_one
from mind import e1
from mind import entry
from world import keys
from world.run_plan import generate_run

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "kill-test"))
import mind_checks  # noqa: E402

BIRTH = {"reserve_milli": 40000, "boldness": 0.3, "trait_order": list(range(22))}
FROZEN = {"tol_nw": 10, "threshold": 1.0, "widen_nw": 10, "split_up": 2, "stretch_down": 5, "merge_cutoff": 5,
          "merge": True, "outside_in": True, "merge_context": True, "merge_widen": True, "taste_keeps": True}


def item(**changes):
    v = np.full(22, 0.5)
    v[18:] = 0.2
    for k, x in changes.items():
        v[int(k[1:])] = x
    return v


def kinds_of(*specs):
    out = {}
    for i, (values, cls) in enumerate(specs):
        out[i] = e1.Kind(values, np.full(22, 5), cls, True, i + 1)
    return out


def mind(**settings):
    return entry.make(dict(BIRTH, params=dict(settings, mind="E1")))


def eat(m, values, delta):
    d = m.decide(list(values[:18]), 50_000)
    m.land(delta, 50_000 + delta, list(values[18:]))
    return d, m.write()


# ------------------------------------------------------------------ settings

def test_e1s_defaults_are_the_frozen_settings():
    s = e1.Settings()
    assert {k: s._get(k) for k in FROZEN} == FROZEN
    table = mind().info()["constants"]
    assert table["detector_width_nw"][0] == 10 and table["taste_keeps"] == [1, "KT-132"]


def test_the_entry_makes_e1_only_when_asked_and_k_f_otherwise():
    assert isinstance(mind(), e1.E1Mind)
    assert not isinstance(entry.make(dict(BIRTH, params={"spike_nano": 0})), e1.E1Mind)


@pytest.mark.parametrize("settings,why", [({"gain": 1}, "no setting"), ({"merge": 1}, "switch"),
                                          ({"tol_nw": -1}, "finite number"), ({"threshold": float("nan")},
                                                                               "finite number")])
def test_e1_refuses_settings_it_does_not_have(settings, why):
    with pytest.raises(ValueError, match=why):
        mind(**settings)


# ------------------------------------------------------------------ looking: elimination, outside in

def test_a_kind_missing_on_the_object_layer_is_ruled_out_there():
    s = e1.Settings(tol_nw=3)
    k = kinds_of((item(), 1), (item(t3=0.9, t4=0.9, t5=0.9), 1))
    verdict, checks, log = e1.look(k, item(), 18, s)
    assert verdict == 0 and log["eliminated"] == {"1": "object"}
    assert log["layers"][1]["out"][0][2] == [3, 4, 5]
    assert checks == 2 * 2 + 2 * 4 + 1 * 5 + 1 * 7


def test_nothing_left_is_unknown_and_an_empty_memory_too():
    s = e1.Settings()
    assert e1.look({}, item(), 18, s)[0] == "unknown"
    v, _, log = e1.look(kinds_of((item(t0=0.9, t1=0.9, t2=0.9), 1)), item(), 18, s)
    assert v == "unknown" and log["eliminated"] == {"0": "object"}


def test_outside_in_changes_where_a_kind_is_ruled_out_but_not_the_verdict():
    k = kinds_of((item(), 1), (item(t3=0.9, t4=0.9, t5=0.9), 1))
    a = e1.look(k, item(t15=0.7), 18, e1.Settings())
    b = e1.look(k, item(t15=0.7), 18, e1.Settings(outside_in=False))
    assert a[0] == b[0] and set(a[2]["eliminated"]) == set(b[2]["eliminated"])
    assert [L["layer"] for L in b[2]["layers"]] == ["all"]


def test_taste_joins_details_after_eating_and_e1_os10_never_reads_it():
    k = kinds_of((item(),  1))
    assert e1.look(k, item(t19=0.9, t20=0.9), 18, e1.Settings())[0] == 0
    assert e1.look(k, item(t19=0.9, t20=0.9, t21=0.9), 22, e1.Settings())[0] == "unknown"
    m = mind(OS10=True)
    eat(m, item(), 15_000)
    m.decide(list(item()[:18]), 50_000)
    after = m.land(15_000, 65_000, [0.9, 0.9, 0.9, 0.9])
    assert after["verdict"] == 0


# ------------------------------------------------------------------ after eating

def test_an_unknown_eat_starts_a_kind_at_the_items_values():
    m = mind()
    d, w = eat(m, item(), 15_000)
    assert d["verdict"] == "unknown" and [e["type"] for e in w["events"]] == ["new"]
    assert w["events"][0]["placeholder_93"] is True       # "unknown" is always a skip, so this eat was forced
    c = m.dump()["candidates"][0]
    assert c["weights_tenths"] == [5] * 22 and c["ranges"][3] == [0.5, 0.5]


def test_a_right_guess_stretches_and_a_trait_that_widened_a_lot_stops_counting():
    m = mind(threshold=3, merge=False)
    eat(m, item(), 15_000)
    d, w = eat(m, item(t6=0.62, t7=0.53, t19=0.9), 15_000)              # 12, 3 and 70 noise widths away
    assert d["verdict"] == 0 and w["events"][0]["type"] == "stretch"
    k = m.kinds[0]
    assert k.tenths[6] == 0 and k.tenths[7] == 5
    assert k.tenths[19] == 5                                            # the sour fix: taste keeps its relevance


def test_without_the_sour_fix_a_widened_taste_stops_counting_too():
    m = mind(threshold=3, merge=False, taste_keeps=False)
    eat(m, item(), 15_000)
    eat(m, item(t19=0.9), 15_000)
    assert m.kinds[0].tenths[19] == 0


def test_a_wrong_guess_splits_and_the_traits_that_differed_gain_relevance():
    m = mind(threshold=3, merge=False)
    eat(m, item(), 15_000)
    d, w = eat(m, item(t8=0.62, t9=0.62), -20_000)                     # 12 noise widths off on two parts traits
    split = w["events"][0]
    assert d["verdict"] == 0 and split["type"] == "split" and split["parent_slot"] == 0 and split["slot"] == 1
    assert m.kinds[0].tenths[8] == 7 and list(m.kinds[1].tenths) == list(m.kinds[0].tenths)


def test_a_new_kind_merged_at_once_into_an_older_one_is_reported_as_a_stretch_of_it():
    m = mind()
    eat(m, item(), 15_000)
    d, w = eat(m, item(t2=0.9, t3=0.9, t4=0.9), 15_000)                # 3 misses: "unknown", then a merge
    assert d["verdict"] == "unknown"
    assert [(e["type"], e["slot"]) for e in w["events"]] == [("stretch", 0)]
    assert w["log"]["merges"] == [[1, 0]] and list(m.kinds) == [0]       # the older kind survives
    k = m.kinds[0]
    assert k.hi[2] == pytest.approx(0.9) and k.tenths[2] == 0 and len(k.eats) == 2


def test_kinds_merge_only_with_the_same_outcome_and_in_the_same_place():
    m = mind()
    eat(m, item(), 15_000)
    eat(m, item(t2=0.9, t3=0.9, t4=0.9), -20_000)                       # a new poison kind: never merged
    assert len(m.kinds) == 2
    c = mind()
    eat(c, item(), 15_000)
    eat(c, item(t0=0.9, t1=0.9, t2=0.9), 15_000)                        # met in another scene
    assert len(c.kinds) == 2
    off = mind(merge=False)
    eat(off, item(), 15_000)
    eat(off, item(t2=0.9, t3=0.9, t4=0.9), 15_000)
    assert len(off.kinds) == 2


def test_two_older_kinds_a_stretch_brings_together_merge_and_the_younger_is_forgotten():
    m = mind()
    m.kinds = kinds_of((item(), 1), (item(t0=0.68), 1))                 # 18 noise widths apart in scene
    m.born = 2
    d, w = eat(m, item(t0=0.59), 15_000)                                # fits both; the older is named
    assert d["verdict"] == 0
    assert [(e["type"], e["slot"]) for e in w["events"]] == [("stretch", 0), ("forget", 1)]
    assert list(m.kinds) == [0] and m.kinds[0].hi[0] == pytest.approx(0.68)


# ------------------------------------------------------------------ E1-OS10

def test_e1_os10_stores_no_taste_and_never_blames_it():
    m = mind(OS10=True, merge=False, threshold=3)
    eat(m, item(), 15_000)
    eat(m, item(t19=0.9, t8=0.62), -20_000)
    c = m.dump()["candidates"]
    assert all(r is None for r in c[0]["ranges"][18:]) and all(w is None for w in c[0]["weights_tenths"][18:])
    assert m.kinds[0].tenths[8] == 7 and all(m.kinds[0].tenths[18:] == 5)
    assert m.info()["version"][-1] == e1.OS10_RECORD


# ------------------------------------------------------------------ in its own process, and the mind checks

def spec(label="E1", settings=None):
    settings = settings or {}
    return agents.AgentSpec(agent_type="E1", label=label, mind_class="tower", entry="mind", host="subprocess",
                            pays_look=True, thinking_unit="check", unit_nano=1_000_000, unit_row="B14, KT-46",
                            version=tuple(e1.version_of(label, bool(settings.get("OS10")))),
                            params=dict(settings, mind="E1", name=label))


@pytest.mark.parametrize("label,settings", [("E1", {}), ("E1-OS10", {"OS10": True})])
def test_e1_in_its_own_process_gives_the_in_process_record(label, settings):
    plan = generate_run("tuning", keys.tuning_set_key(), 3, 2)
    a = run_one(plan, spec(label, settings), ReadingCache(plan.noise_key), package_dir=ROOT / "src" / "mind")
    inproc = dataclasses.replace(spec(label, settings), host="in-process", entry="mind.entry:make")
    b = run_one(plan, inproc, ReadingCache(plan.noise_key))
    assert a.decisions == b.decisions and a.lineage_log == b.lineage_log and a.info == b.info


@pytest.mark.parametrize("label,settings", [("E1", {}), ("E1-OS10", {"OS10": True})])
def test_the_mind_checks_pass_e1_and_e1_os10(label, settings):
    plans = [generate_run("tuning", keys.tuning_set_key(), f, 1) for f in (1, 4)]
    res = mind_checks.run_checks(ROOT / "src" / "mind", spec(label, settings), plans=plans)
    assert res["failed"] == [] and res["review"] == [], [str(f) for f in res["failed"] + res["review"]]


# ------------------------------------------------------------------ the kill-run driver

def test_the_driver_runs_in_the_frozen_order_and_judges_e1(tmp_path):
    import e1_kill_run as d
    res = d.run_set("tuning", keys.tuning_set_key(), [1, 2], workers=1, runs=1, progress=lambda m: None)
    assert res["rule6"]["holds"] and res["verdict"] in ("GO", "NO-GO", "INCONCLUSIVE")
    assert set(res["reported"]) == {"E1", "E1-OS10", "E1 no merging", "E1 all at once"}
    assert res["reported"]["E1-OS10"]["noticed"] == 0
    d.write(res, tmp_path / "out.json")
    out = json.loads((tmp_path / "out.json").read_text())
    assert out["verdict_table"].startswith("Set tuning: ") and "rule 5" in out["verdict_table"]


def test_the_driver_refuses_a_kill_run_set_without_set_as_manifest(tmp_path, monkeypatch):
    import e1_kill_run as d
    monkeypatch.setattr(d, "MANIFEST", tmp_path / "missing.sha256")
    assert d.kill("A", "0" * 64, str(tmp_path / "out.json"), 1) == 1
    assert d.kill("B", "0" * 64, str(tmp_path / "out.json"), 1) == 1
    assert not (tmp_path / "out.json").exists()
