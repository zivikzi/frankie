"""B1n-mind's copy of the drive (section 5, KT-08, KT-44 to KT-50), and its frozen grid."""

import json
import pathlib
import sys

import pytest

from baselines.drive import drive

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import make_drive_grid  # noqa: E402


def test_the_frozen_grid_is_what_the_drive_gives():
    assert (ROOT / "tests" / "data" / "drive_grid.json").read_text() == make_drive_grid.grid_text()


def test_the_grid_covers_every_kind_of_outcome():
    rows = json.loads((ROOT / "tests" / "data" / "drive_grid.json").read_text())["rows"]
    kinds = {(r["in"]["verdict_state"], r["out"]["pick"], r["out"]["provenance"]) for r in rows}
    assert kinds == {("named", "eat", "bench"), ("named", "skip", "bench"),
                     ("named", "eat", "no-safe-option-fallback"), ("named", "skip", "no-safe-option-fallback"),
                     ("unknown", "skip", "bench"), ("unsettled", "skip", "bench")}


def test_unknown_and_unsettled_always_skip_without_the_chooser():
    for state in ("unknown", "unsettled"):
        tr = drive(state, None, None, 10**6, 0, 40000, 0.6)
        assert tr["pick"] == "skip" and tr["options_considered"] == [] and tr["eat_chance"] is None
        assert not tr["no_safe_option"] and tr["provenance"] == "bench"


def test_eats_chance_and_the_bar():
    tr = drive("named", 0.75, 0.5, 50000, 0, 40000, 0.5)
    assert tr["eat_chance"] == 1.0 - (1.0 - 0.75) * (2.0 - 0.5)      # 0.625
    assert tr["bar"] == 0.9 - 0.3 * 0.5
    assert tr["pick"] == "skip" and [o["cleared_bar"] for o in tr["options_considered"]] == [False, True]
    assert drive("named", 0.2, 0.0, 50000, 0, 40000, 0.5)["eat_chance"] == 0.0     # never below 0


def test_eat_is_taken_first_when_it_clears():
    tr = drive("named", 1.0, 1.0, 50000, 0, 40000, 0.1)
    assert tr["pick"] == "eat" and len(tr["options_considered"]) == 1 and tr["options_considered"][0]["cleared_bar"]


def test_a_chance_equal_to_the_bar_clears_it():
    tr = drive("named", 0.5, 1.0, 50000, 0, 40000, 4 / 3)        # bar 0.5
    assert tr["bar"] == tr["eat_chance"] == 0.5 and tr["pick"] == "eat"


@pytest.mark.parametrize("energy,thinking,want", [(40030, 30, 1.0), (40030, 31, 0.0), (39999, 0, 0.0)])
def test_skips_chance_is_whether_energy_after_thinking_stays_at_or_above_r(energy, thinking, want):
    assert drive("named", 0.0, 1.0, energy, thinking, 40000, 0.3)["skip_chance"] == want


def test_the_fallback_takes_the_higher_chance_and_ties_skip():
    tr = drive("named", 0.5, 1.0, 39000, 0, 40000, 0.1)          # eat 0.5, skip 0: neither clears 0.87
    assert tr["no_safe_option"] and tr["pick"] == "eat" and tr["provenance"] == "no-safe-option-fallback"
    assert [o["cleared_bar"] for o in tr["options_considered"]] == [False, False]
    tie = drive("named", 0.0, 1.0, 39000, 0, 40000, 0.1)          # both 0
    assert tie["no_safe_option"] and tie["pick"] == "skip"
