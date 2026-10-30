"""The automatic mind checks pass on the stub, and each one bites (section 7, step 5)."""

import dataclasses
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import mind_checks as mc  # noqa: E402

from harness import run as harness_run  # noqa: E402
from harness.readings_cache import ReadingCache  # noqa: E402
from test_fixtures.stub import STUB_DIR, stub_spec  # noqa: E402
from world import keys  # noqa: E402
from world.run_plan import generate_run  # noqa: E402

PLAN = generate_run("tuning", keys.tuning_set_key(), 3, 2)


@pytest.fixture
def stub_copy(tmp_path):
    d = tmp_path / "mind"
    shutil.copytree(STUB_DIR, d, ignore=shutil.ignore_patterns("__pycache__"))
    return d


def _append(d, text):
    with (d / "entry.py").open("a", encoding="utf-8") as f:
        f.write("\n" + text + "\n")


# ---------------------------------------------------------------- the stub passes

def test_the_stub_passes_every_static_check():
    assert mc.static_checks(STUB_DIR) == []


def test_the_stub_passes_every_run_time_check():
    res = mc.run_checks(STUB_DIR, stub_spec(), plans=[PLAN],
                        taste_blind_plans=[generate_run("tuning", keys.tuning_set_key(), f, 5) for f in (7, 8)])
    assert res["findings"] == []
    assert res["chooser"]["chooser"] == ["satisficing"]


# ---------------------------------------------------------------- static checks bite

def test_the_guard_refuses_the_standard_library(stub_copy):
    _append(stub_copy, "import json")
    assert any(f.check == "import guard" for f in mc.static_checks(stub_copy))


def test_the_file_scan_finds_weights(stub_copy):
    (stub_copy / "weights.npz").write_bytes(b"PK")
    assert [f.check for f in mc.file_scan(stub_copy)] == ["FORBIDDEN 1 file scan"]


@pytest.mark.parametrize("text,entry", [
    ("# a softmax over options", 12), ("def gradient_step():\n    return None", 2), ("NOVELTY_W = None", 4),
    ("def plan_route():\n    return None", 22), ("x_td = None", 11), ("def best_gini():\n    return None", 21),
    ("label = 'essence'", 18), ("c3 = None", 18), ("seedBank = None", 10), ("# competence", 6),
])
def test_the_word_scans_find_their_words(stub_copy, text, entry):
    _append(stub_copy, text)
    hits = mc.word_scan(stub_copy)
    assert hits and all(h.review for h in hits)
    assert any(h.check.startswith(f"FORBIDDEN {entry} ") for h in hits)


def test_the_word_scans_split_names_and_skip_the_interfaces_own_fields():
    assert mc._split_name("gradStep_size2x") == ["grad", "step", "size", "x"]
    assert mc._matches("gradient", "grad") and not mc._matches("std", "td") and mc._matches("td", "td")
    assert "count" in mc.INTERFACE_FIELDS


@pytest.mark.parametrize("text", [
    "LEAK = 0.37", "def f(x):\n    return x * 0.37", "TRAIT_WIDTHS = (2, 3, 4)  # (KT-20)",
    "WIDTH = 3  # tuned by hand",
])
def test_the_constants_check_finds_unlisted_numbers(stub_copy, text):
    _append(stub_copy, text)
    assert any(f.check == "FORBIDDEN 28 constants" for f in mc.constants_scan(stub_copy))


def test_a_cited_constant_passes(stub_copy):
    _append(stub_copy, "LEAK = 0.37  # (KT-19)\nSIGNED = -2  # (PLACEHOLDER-14)")
    assert mc.constants_scan(stub_copy) == []


# ---------------------------------------------------------------- run-time checks bite

def test_the_counter_check_catches_a_mind_that_keeps_its_looks():
    assert mc.counter_check(stub_spec(restless=True), STUB_DIR, PLAN)
    assert mc.counter_check(stub_spec(), STUB_DIR, PLAN) == []


def test_the_birth_check_catches_a_preloaded_memory_and_uneven_weights():
    found = mc.birth_check(stub_spec(preloaded=True), STUB_DIR, PLAN)
    assert [f.check for f in found][:1] == ["FORBIDDEN 20 empty at birth"]
    found = mc.birth_check(stub_spec(uneven=True), STUB_DIR, PLAN)
    assert found and all(f.check == "M20 equal weights" for f in found)


def test_the_interface_check_catches_a_world_field_at_birth(monkeypatch):
    real = harness_run.birth_config

    def leaky(plan, spec, extra=None):
        cfg = real(plan, spec, extra)
        cfg["params"]["role"] = "apple"
        return cfg
    monkeypatch.setattr(harness_run, "birth_config", leaky)
    found = mc.interface_check(stub_spec(), STUB_DIR, [PLAN])
    assert found and all(f.check == "FORBIDDEN 18 interface" for f in found)


def test_the_leak_check_catches_a_reading_that_depends_on_nature(monkeypatch):
    real = ReadingCache.visible

    def leaky(self, obj, replica):
        v = real(self, obj, replica)
        return v[:-1] + ((0.0 if obj.nature == "poison" else 1.0),)
    monkeypatch.setattr(ReadingCache, "visible", leaky)
    assert any(f.check == "FORBIDDEN 18 leak" for f in mc.leak_check(stub_spec(), STUB_DIR, PLAN))


def test_the_taste_blind_check_catches_a_mind_that_notices():
    assert mc.taste_blind_check(stub_spec("taste-aware"), STUB_DIR, [PLAN])


def test_the_constants_table_must_cite_rows():
    rec = harness_run.run_one(PLAN, stub_spec(host="in-process"), ReadingCache(PLAN.noise_key), checks=False)
    assert mc.constants_check([rec]) == []
    rec = dataclasses.replace(rec, info=dict(rec.info, constants={"leak": [0.3, "tuned by hand"]}))
    assert mc.constants_check([rec])
