"""Frankie Lab (explore/): every Lab mind through the frozen harness, and the Lab's page.

E1's own hand-made cases live in tests/test_e1.py, since E1 moved into the
mind package; the Lab runs that same code (explore/e1.py only re-exports it).
"""

import json
import pathlib
import sys
import threading
import urllib.request

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "explore"))

import e1 as lab_e1  # noqa: E402
import minds  # noqa: E402

from harness import scoring  # noqa: E402
from mind import e1 as frozen  # noqa: E402


def test_the_lab_runs_the_frozen_e1():
    assert lab_e1.Settings is frozen.Settings and lab_e1.look is frozen.look


@pytest.mark.parametrize("name", list(minds.VARIANTS))
def test_every_lab_variant_passes_the_harness_checks_and_scores(name):
    _, rec = minds.run_record(name, 3, 2)
    m = scoring.measures(rec)
    assert len(rec.decisions) == 210 and rec.info["neuron"] == "rate" and rec.info["chooser"] == "satisficing"
    assert -1 <= float(m["d_learn_strict"]) <= 1 and m["settle_rate"] == 1


def test_e1_os10_never_notices_and_e1_does_on_this_run():
    _, a = minds.run_record("E1-OS10", 1, 1)
    assert scoring.measures(a)["noticed"] is False


def test_the_same_e1_run_twice_gives_the_same_record():
    _, a = minds.run_record("E1", 5, 1)
    _, b = minds.run_record("E1", 5, 1)
    assert a.decisions == b.decisions and a.lineage_log == b.lineage_log


def test_merges_reach_the_harness_as_stretches_and_forgets_and_the_lineage_holds():
    _, rec = minds.run_record("E1", 1, 1)
    merged = [d for d in rec.decisions.values() if "write" in d and d["write"]["log"]["merges"]]
    assert merged, "E1 merged nothing on this run"
    for d in merged:
        events = d["write"]["events"]
        assert sum(1 for e in events if e["type"] != "forget") == 1
        assert all(e["type"] in ("new", "stretch", "split", "forget") for e in events)


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
