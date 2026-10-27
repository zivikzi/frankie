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


BYPASSES = {
    # found by the independent review; each must be refused
    "utf7.py": b"# coding: utf-7\nx = 1 # +AAo-import world.run_plan as rp\n",
    "alias_import.py": b"f = __import__\nrp = f('world.run_plan', fromlist=['*'])\n",
    "builtins_lookup.py": b"b = __builtins__['__import__']('baselines')\n",
    "exec_alias.py": b"e = exec\ne('import world')\n",
    "map_import.py": b"mods = list(map(__import__, ['harness']))\n",
    "future_plain.py": b"import __future__\n",
    "numpy_sys.py": b"from numpy.f2py.crackfortran import sys\n",
    "sys_modules.py": b"import numpy as np\nw = np.f2py.crackfortran.sys.modules['world.kinds']\n",
    "path_trick.py": b"__path__.append('../world')\n",
    "star.py": b"from numpy import *\n",
}


def test_known_bypasses_are_refused(tmp_path):
    mind = tmp_path / "mind"
    mind.mkdir()
    (mind / "__init__.py").write_text("")
    for name, src in BYPASSES.items():
        (mind / name).write_bytes(src)
    flagged = {pathlib_name(p) for p, _, _ in import_guard.check([mind])}
    assert flagged == set(BYPASSES)


def pathlib_name(p):
    return Path(p).name


def test_files_the_guard_cannot_read_are_refused(tmp_path):
    mind = tmp_path / "mind"
    (mind / "__pycache__").mkdir(parents=True)
    (mind / "__init__.py").write_text("import numpy\n")
    (mind / "__pycache__" / "x.cpython-312.pyc").write_bytes(b"\0")    # normal cache: allowed
    (mind / "hidden.pyc").write_bytes(b"\0")
    (mind / "fast.so").write_bytes(b"\0")
    found = import_guard.check([mind])
    assert sorted(Path(p).name for p, _, _ in found) == ["fast.so", "hidden.pyc"]


def test_the_mind_package_loads_nothing_forbidden():
    """Run-time check: importing the mind package pulls in no world, harness, bot or fixture module."""
    code = ("import sys, mind\n"
            "bad = [m for m in sys.modules if m.split('.')[0] in "
            "{'world', 'harness', 'baselines', 'twins', 'test_fixtures'}]\n"
            "print(bad)\nsys.exit(1 if bad else 0)\n")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
