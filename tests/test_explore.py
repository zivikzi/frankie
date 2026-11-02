"""Frankie Lab (explore/): E1 on hand-made cases, E1 through the frozen harness, and the Lab's page.

E1 is an exploration, not part of the kill test; these tests keep it honest:
its elimination, stretch, split and merge do what explore/e1.py says, it
passes every check the frozen harness makes on a tower mind, and the Lab
starts and serves its page.
"""

import json
import pathlib
import sys
import threading
import urllib.request

import numpy as np
import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "explore"))

import e1  # noqa: E402
import minds  # noqa: E402

from harness import scoring  # noqa: E402

BIRTH = {"reserve_milli": 40000, "boldness": 0.3, "trait_order": list(range(22))}


def item(**changes):
    v = np.full(22, 0.5)
    v[18:] = 0.2
    for k, x in changes.items():
        v[int(k[1:])] = x
    return v


def memory_with(p, *kinds):
    m = e1.Memory(p)
    for values, cls in kinds:
        m.new_kind(values, np.full(22, 5), cls, True)
    return m


# ------------------------------------------------------------------ looking: elimination, outside in

def test_a_kind_that_misses_on_the_object_layer_is_ruled_out_there():
    p = e1.Params()
    m = memory_with(p, (item(), 1), (item(t3=0.9, t4=0.9, t5=0.9), 1))     # kind 1 differs on 3 object traits
    verdict, checks, log = e1.look(m, item(), 18, p)
    assert verdict == 0 and log["eliminated"] == {"1": "object"}
    assert [L["layer"] for L in log["layers"]] == ["context", "object", "parts", "details"]
    out = log["layers"][1]["out"]
    assert out[0][0] == 1 and out[0][2] == [3, 4, 5] and out[0][1] == pytest.approx(1.5)
    assert checks == 2 * 2 + 2 * 4 + 1 * 5 + 1 * 7                   # kind 1 stops being checked after the object layer


def test_nothing_survives_means_unknown_and_an_empty_memory_too():
    p = e1.Params()
    assert e1.look(e1.Memory(p), item(), 18, p)[0] == "unknown"
    m = memory_with(p, (item(t0=0.9, t1=0.9, t2=0.9), 1))
    verdict, _, log = e1.look(m, item(), 18, p)
    assert verdict == "unknown" and log["eliminated"] == {"0": "object"}


def test_several_survivors_name_the_fewest_weighted_misses():
    p = e1.Params(threshold=3)
    m = memory_with(p, (item(t6=0.9, t7=0.9), 1), (item(t6=0.9), 1))
    assert e1.look(m, item(), 18, p)[0] == 1


def test_with_an_absolute_threshold_outside_in_changes_where_but_not_what():
    a, b = e1.Params(), e1.Params(outside_in=False)
    m = memory_with(a, (item(), 1), (item(t3=0.9, t4=0.9, t5=0.9), 1), (item(t15=0.9), -1))
    va, ca, la = e1.look(m, item(t15=0.7), 18, a)
    vb, cb, lb = e1.look(m, item(t15=0.7), 18, b)
    assert va == vb and set(la["eliminated"]) == set(lb["eliminated"])
    assert [L["layer"] for L in lb["layers"]] == ["all"] and cb >= ca


def test_taste_joins_the_details_layer_after_eating():
    p = e1.Params()
    m = memory_with(p, (item(), 1))
    assert e1.look(m, item(t19=0.9), 18, p)[0] == 0                   # before eating, taste is not read
    v, _, log = e1.look(m, item(t19=0.9, t20=0.9, t21=0.9), 22, p)
    assert v == "unknown" and log["eliminated"] == {"0": "details"}


# ------------------------------------------------------------------ after eating

def mind(**params):
    return e1.make(dict(BIRTH, params=params))


def eat(m, values, delta):
    d = m.decide(list(values[:18]), 50_000)
    m.land(delta, 50_000 + delta, list(values[18:]))
    return d, m.write()


def test_an_unknown_eat_starts_a_kind_at_the_items_values():
    m = mind()
    d, w = eat(m, item(), 15_000)
    assert d["verdict"] == "unknown" and [e["type"] for e in w["events"]] == ["new"]
    k = m.memory.kinds[0]
    assert np.array_equal(k.lo, item()) and np.array_equal(k.hi, item()) and list(k.tenths) == [5] * 22


def test_a_right_guess_stretches_and_a_trait_that_widened_a_lot_loses_relevance():
    m = mind(threshold=3)
    eat(m, item(), 15_000)
    d, w = eat(m, item(t6=0.62, t7=0.53), 15_000)                     # 12 and 3 noise widths away
    assert d["verdict"] == 0 and w["events"][0]["type"] == "stretch"
    k = m.memory.kinds[0]
    assert k.hi[6] == pytest.approx(0.62) and k.tenths[6] == 4 and k.tenths[7] == 5
    assert w["events"][0]["weight_deltas"] == [[0, 6, -1]]


def test_a_wrong_guess_splits_and_the_traits_that_differed_gain_relevance():
    m = mind(threshold=3, merge=False)
    eat(m, item(), 15_000)
    d, w = eat(m, item(t8=0.6, t9=0.6), -20_000)                        # 10 noise widths off on two parts traits
    assert d["verdict"] == 0
    split = w["events"][0]
    assert split["type"] == "split" and split["parent_slot"] == 0 and split["slot"] == 1
    assert m.memory.kinds[0].tenths[8] == 7 and m.memory.kinds[0].tenths[9] == 7
    assert list(m.memory.kinds[1].tenths) == list(m.memory.kinds[0].tenths)
    assert m.memory.kinds[1].founding() == -1


def test_two_kinds_with_the_same_outcome_and_overlapping_ranges_merge():
    m = mind(merge_cutoff=5)                                             # no trait is above 5 tenths yet
    eat(m, item(), 15_000)
    _, w = eat(m, item(t2=0.9, t3=0.9, t4=0.9, t5=0.9), 15_000)         # "unknown": a new kind, then a merge
    types = [e["type"] for e in w["events"]]
    assert types == ["new", "forget"] and w["log"]["merges"] == [[0, 1]]
    assert list(m.memory.kinds) == [1]                                   # the kind the eat was filed under survives
    k = m.memory.kinds[1]
    assert k.lo[2] == pytest.approx(0.5) and k.hi[2] == pytest.approx(0.9) and len(k.eats) == 2


def test_merging_needs_the_same_outcome_and_with_merge_context_the_same_place():
    m = mind(merge_cutoff=5)
    eat(m, item(), 15_000)
    eat(m, item(t2=0.9, t3=0.9, t4=0.9, t5=0.9), -20_000)
    assert len(m.memory.kinds) == 2                                      # different outcomes never merge
    c = mind(merge_cutoff=5, merge_context=True)
    eat(c, item(), 15_000)
    eat(c, item(t0=0.9, t2=0.9, t3=0.9, t4=0.9, t5=0.9), 15_000)
    assert len(c.memory.kinds) == 2                                      # met in another scene: kept apart


def test_a_merge_that_widens_a_trait_lowers_its_relevance_when_asked():
    m = mind(merge_cutoff=5, merge_widen=True, stretch_down=5)
    eat(m, item(), 15_000)
    eat(m, item(t3=0.9), 15_000)
    k = next(iter(m.memory.kinds.values()))
    assert k.tenths[3] == 0 and k.tenths[2] == 5


def test_merging_off_keeps_every_kind():
    m = mind(merge_cutoff=5, merge=False)
    eat(m, item(), 15_000)
    eat(m, item(t2=0.9, t3=0.9, t4=0.9, t5=0.9), 15_000)
    assert len(m.memory.kinds) == 2


def test_e1_refuses_settings_it_does_not_have():
    with pytest.raises(ValueError, match="no setting"):
        mind(gain=1)
    with pytest.raises(ValueError, match="elimination"):
        mind(elimination="sideways")


# ------------------------------------------------------------------ through the frozen harness

@pytest.mark.parametrize("name", ["E1", "E1 no merging", "E1 all at once", "E1 as first written"])
def test_every_e1_variant_passes_the_harness_checks_and_scores(name):
    _, rec = minds.run_record(name, 3, 2)
    m = scoring.measures(rec)
    assert len(rec.decisions) == 210 and rec.info["neuron"] == "rate" and rec.info["chooser"] == "satisficing"
    assert -1 <= float(m["d_learn_strict"]) <= 1 and m["settle_rate"] == 1


def test_the_same_e1_run_twice_gives_the_same_record():
    _, a = minds.run_record("E1", 5, 1)
    _, b = minds.run_record("E1", 5, 1)
    assert a.decisions == b.decisions and a.lineage_log == b.lineage_log


def test_a_merge_reaches_the_harness_as_a_forget_and_the_lineage_holds():
    _, rec = minds.run_record("E1", 1, 1)
    merges = [d for d in rec.decisions.values() if "write" in d and d["write"]["log"]["merges"]]
    assert merges, "E1 merged nothing on this run"
    for d in merges:
        forgets = [e["slot"] for e in d["write"]["events"] if e["type"] == "forget"]
        assert sorted(forgets) == sorted(g for g, _ in d["write"]["log"]["merges"])


# ------------------------------------------------------------------ the Lab

@pytest.fixture()
def lab(tmp_path, monkeypatch):
    import lab as labmod
    import runtrace
    monkeypatch.setattr(runtrace, "TRACES", tmp_path / "traces")
    server, url = labmod.serve(port=8870, open_browser=False)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    yield url
    server.shutdown()
    server.server_close()


def get(url):
    with urllib.request.urlopen(url, timeout=120) as r:
        return r.status, r.read()


def test_the_lab_starts_and_serves_its_page_and_a_run(lab):
    status, body = get(lab)
    assert status == 200 and b"Frankie Lab" in body
    status, body = get(lab + "app.js")
    assert status == 200 and b"drawObject" in body
    meta = json.loads(get(lab + "api/meta")[1])
    assert "E1" in meta["minds"] and "K-F" in meta["minds"] and len(meta["families"]) == 30
    trace = json.loads(get(lab + "api/trace?mind=E1&family=1&run=1")[1])
    assert len(trace["steps"]) == 210 and trace["mind"] == "E1"
    s = next(s for s in trace["steps"] if s["item"] == "t2")
    assert len(s["visible"]) == 18 and s["taste"] is not None and s["events"]
    assert json.loads(get(lab + "api/scoreboard")[1]) is not None
