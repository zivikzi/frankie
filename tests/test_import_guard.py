"""The import guard (I02), with a positive control that shows it bites."""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import import_guard  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def test_the_mind_package_is_clean():
    assert import_guard.check([ROOT / "src" / "mind"]) == []


def test_the_guard_runs_as_a_script():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "import_guard.py"), str(ROOT / "src" / "mind")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_positive_control(tmp_path):
    mind = tmp_path / "mind"
    (mind / "sub").mkdir(parents=True)
    (mind / "__init__.py").write_text("from __future__ import annotations\nimport numpy as np\nfrom . import sub\n")
    (mind / "ok.py").write_text("import numba\nfrom numpy import zeros\nfrom mind.sub import x\n")
    (mind / "sub" / "__init__.py").write_text("from .. import ok\n")
    (mind / "bad.py").write_text(
        "import os\n"
        "from world import run_plan\n"
        "import baselines.b1n\n"
        "from test_fixtures import f\n"
        "from .. import world\n"
        "x = __import__('harness')\n"
        "import importlib\n"
        "eval('1')\n"
    )
    found = import_guard.check([mind])
    assert {p for p, _, _ in found} == {str(mind / "bad.py")}
    assert len(found) == 8
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "import_guard.py"), str(mind)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "I02 forbids import os" in r.stdout


def test_the_world_package_would_fail_the_guard():
    """The guard is strict: even the standard library is refused in the mind."""
    assert import_guard.check([ROOT / "src" / "world"]) != []
