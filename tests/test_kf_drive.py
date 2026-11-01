"""K-F's own copy of the drive (mind/drive.py) against B1n-mind's frozen grid, and hand-made cases (KT-44 to KT-50).

KT-44: a test outside both packages feeds both copies the same grid of
inputs and requires identical chances, choices and no-safe-option flags.
The grid (tests/data/drive_grid.json) was frozen with B1n-mind in Week 2.
"""

import json
import pathlib

import pytest

from harness import protocol
from mind import drive

GRID = pathlib.Path(__file__).resolve().parent / "data" / "drive_grid.json"


def _rows():
    return json.loads(GRID.read_text())["rows"]


def test_the_grid_is_the_frozen_one():
    rows = _rows()
    assert len(rows) == 744          # (KT-102)


@pytest.mark.parametrize("row", _rows(), ids=lambda r: "{verdict_state}-{share}-{reliability}-{boldness}-"
                                                     "{energy_milli}-{thinking_milli}".format(**r["in"]))
def test_k_fs_drive_matches_b1n_minds_copy_on_every_row(row):
    i, want = row["in"], row["out"]
    trace, provenance = drive.choose(i["verdict_state"] == "named", i["share"], i["reliability"],
                                     i["energy_milli"], i["thinking_milli"], i["reserve_milli"], i["boldness"])
    assert trace["eat_chance"] == want["eat_chance"]
    assert trace["skip_chance"] == want["skip_chance"]
    assert trace["bar"] == want["bar"]
    assert trace["pick"] == want["pick"]
    assert trace["no_safe_option"] == want["no_safe_option"]
    assert [o["cleared_bar"] for o in trace["options_considered"]] == want["cleared"]
    assert provenance == want["provenance"]


def test_unknown_and_unsettled_skip_without_the_chooser():
    trace, provenance = drive.choose(False, None, None, 60000, 0, 40000, 0.6)
    assert trace["pick"] == "skip" and trace["options_considered"] == [] and trace["eat_chance"] is None
    assert not trace["no_safe_option"] and provenance == "bench"


def test_the_untried_tally_is_logged_and_changes_nothing():
    a, _ = drive.choose(True, 0.5, 1.0, 50000, 0, 40000, 0.3, untried_tally=-20.0)
    b, _ = drive.choose(True, 0.5, 1.0, 50000, 0, 40000, 0.3)
    assert a["untried_tally"] == -20.0 and b["untried_tally"] is None
    assert {k: v for k, v in a.items() if k != "untried_tally"} == {k: v for k, v in b.items() if k != "untried_tally"}


def test_a_kind_with_no_eats_on_record_stops_with_an_error():
    with pytest.raises(ValueError, match="KT-50"):
        drive.share_above([])
    assert drive.share_above([True, False, True, True]) == 0.75


@pytest.mark.parametrize("units", [0, 1, 499, 500, 501, 1499, 1500, 123456])
@pytest.mark.parametrize("unit_nano", [1_000_000, 500, 1, 2_500, 333_333])
def test_thinking_is_priced_as_the_harness_prices_it(units, unit_nano):
    assert drive.thinking_milli(units, unit_nano) == protocol.thinking_cost_milli(units, unit_nano)


def test_the_traces_pass_the_harness_checks():
    from harness.agents import tower_minds
    spec = tower_minds(None)[-1]                      # TW7
    for named, share, rel, energy in ((True, 1.0, 1.0, 50000), (True, 0.0, 1.0, 39000), (True, 0.5, 1.0, 39000),
                                      (False, None, None, 50000)):
        trace, provenance = drive.choose(named, share, rel, energy, 12, 40000, 0.4)
        d = {"action": trace["pick"], "verdict": 0 if named else "unknown", "settle_step": 6,
             "thinking": {"unit": "check", "count": 12, "cost_milli": 12}, "drive": trace, "provenance": provenance}
        protocol.check_decision(d, spec)
