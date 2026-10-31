"""Write the frozen grid of drive inputs and B1n-mind's drive outputs (KT-44).

The grid is frozen with the bots in Week 2. In Week 3 the mind package writes
its own copy of the drive from section 5, and a test outside both packages
requires it to give the same chances, picks and no-safe-option flags on every
row of tests/data/drive_grid.json. Rerunning this script must leave the file
unchanged; tests/test_drive.py checks that.

Usage: python tools/make_drive_grid.py [output path]
"""

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from baselines.drive import drive  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "tests" / "data" / "drive_grid.json"

SHARES = [0.0, 0.1, 0.25, 1 / 3, 0.5, 2 / 3, 0.7, 0.75, 0.8, 0.9, 0.95, 1.0]
RELIABILITIES = [0.0, 0.5, 0.75, 0.9, 1.0]
BOLDNESS = [0.1, 1 / 3, 0.6]
RESERVE = 40000
# energy minus thinking: well above, just at, and just below R
ENERGIES = [(50000, 0), (40030, 30), (40030, 31), (60000, 21000)]


def rows():
    out = []
    for state in ("named", "unknown", "unsettled"):
        for share in (SHARES if state == "named" else [None]):
            for rel in (RELIABILITIES if state == "named" else [None]):
                for b in BOLDNESS:
                    for energy, thinking in ENERGIES:
                        tr = drive(state, share, rel, energy, thinking, RESERVE, b)
                        out.append({"in": {"verdict_state": state, "share": share, "reliability": rel,
                                           "energy_milli": energy, "thinking_milli": thinking,
                                           "reserve_milli": RESERVE, "boldness": b},
                                    "out": {"eat_chance": tr["eat_chance"], "skip_chance": tr["skip_chance"],
                                            "bar": tr["bar"], "pick": tr["pick"],
                                            "no_safe_option": tr["no_safe_option"],
                                            "provenance": tr["provenance"],
                                            "cleared": [o["cleared_bar"] for o in tr["options_considered"]]}})
    return out


def grid_text():
    """One row per line, so a difference shows up row by row."""
    lines = [json.dumps(r, sort_keys=True, separators=(",", ":")) for r in rows()]
    return ('{"what":"drive grid (KT-44): inputs and B1n-mind\'s drive outputs, frozen in Week 2",\n"rows":[\n'
            + ",\n".join(lines) + "\n]}\n")


if __name__ == "__main__":
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else OUT
    path.write_text(grid_text())
    print(f"wrote {len(rows())} rows to {path}")
