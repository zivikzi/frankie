"""The import guard (I02), with a positive control that shows it bites."""

import importlib.util
import marshal
import os
import py_compile
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import import_guard  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TAG = sys.implementation.cache_tag


def names(found):
    return sorted(Path(p).name for p, _, _ in found)


def test_the_mind_package_is_clean():
    assert import_guard.check([ROOT / "src" / "mind"]) == []


def test_the_guard_runs_as_a_script():
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "import_guard.py"), str(ROOT / "src" / "mind")],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_positive_control(tmp_path):
    mind = tmp_path / "mind"
    (mind / "sub").mkdir(parents=True)
    (mind / "__init__.py").write_text("from __future__ import annotations\nimport numpy as np\nimport mind.sub\n")
    (mind / "ok.py").write_text(
        "import numba\nfrom numpy import zeros\nfrom numpy.random import Philox\nfrom mind.sub import x\n"
        "import numpy.linalg\nfrom numpy import __version__\n__all__ = ['zeros']\n"
        "w = np.lib.stride_tricks.sliding_window_view\n\n\nclass A:\n    def __init__(self):\n"
        "        super().__init__()\n        self.mode = 'eval'\n        self._state = np.zeros(3)\n")
    (mind / "sub" / "__init__.py").write_text("from mind import ok\nx = 1\n")
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
    assert len(found) == 9          # import importlib counts twice: the module and the name
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "import_guard.py"), str(mind)],
                       capture_output=True, text=True)
    assert r.returncode == 1 and "I02 forbids import os" in r.stdout


def test_the_world_package_would_fail_the_guard():
    """The guard is strict: even the standard library is refused in the mind."""
    assert import_guard.check([ROOT / "src" / "world"]) != []


BYPASSES = {
    # found by the two independent reviews; each must be refused
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
    "package_trick.py": b"__package__ = 'world'\nfrom . import kinds\n",
    "relative.py": b"from . import sibling\n",
    "package_alias.py": b"from numpy import random as __package__\n",
    "globals_lookup.py": b"def act(obs):\n    return globals()['__builtins__']['__import__']('world.run_plan')\n",
    "globals_update.py": b"globals().update(x=1)\n",
    "vars_lookup.py": b"import numpy as np\nm = vars(np.random)\n",
    "func_globals.py": b"import numpy as np\nb = np.load.__globals__\n",
    "numpy_builtins.py": b"from numpy import __builtins__ as B\n",
    "mind_spec.py": b"from mind import __spec__ as S\n",
    "numpy_loader.py": b"from numpy import __loader__\n",
    "f2py_main.py": b"if False:\n    from numpy.f2py.__main__ import main\n",
    "f2py_import.py": b"import numpy.f2py.__main__\n",
    "numpy_private.py": b"from numpy._core import _internal\n",
    "ctypeslib.py": b"from numpy.ctypeslib import load_library\n",
    "ctypeslib_attr.py": b"import numpy as n\nlib = n.ctypeslib.load_library('x', '.')\n",
    "getattr_trick.py": b"import numpy as np\nm = getattr(np, 'mod' + 'ules')\n",
    "subclasses.py": b"s = ().__class__.__base__.__subclasses__()\n",
    "frame_globals.py": b"try:\n    1 / 0\nexcept ZeroDivisionError as e:\n    g = e.__traceback__.tb_frame.f_globals\n",
    "self_module.py": b"b = len.__self__\n",
    "meta_path.py": b"import numpy as np\nf = np.random.x.meta_path\n",
    "string_key.py": b"import numpy as np\nm = np.random.x['modules']\n",
    "breakpoint.py": b"breakpoint()\n",
    "dunder_name.py": b"s = __loader__\n",
    # found by the third check
    "from_numpy_part.py": b"from numpy import f2py\n",
    "from_numpy_testing.py": b"from numpy import testing as t\n",
    "from_numpy_private.py": b"from numpy import _core\n",
    "from_random_private.py": b"from numpy.random import _pcg64\n",
    "numpy_private_attr.py": b"import numpy as np\nm = np._core\n",
    "imported_private_attr.py": b"from numpy import random\nx = random._pcg64.np\n",
    "deep_chain.py": b"x = a" + b".b" * 10_000 + b"\n",
}


def test_known_bypasses_are_refused(tmp_path):
    mind = tmp_path / "mind"
    mind.mkdir()
    (mind / "__init__.py").write_text("")
    for name, src in BYPASSES.items():
        (mind / name).write_bytes(src)
    assert set(names(import_guard.check([mind]))) == set(BYPASSES)


def test_one_bad_line_never_hides_another(tmp_path):
    """A name the guard has to look up in NumPy cannot stop the guard or hide the other violations."""
    mind = tmp_path / "mind"
    mind.mkdir()
    (mind / "__init__.py").write_text("")
    (mind / "a_first.py").write_text("from numpy.f2py.__main__ import main\nfrom numpy.lib import format\n")
    (mind / "z_bad.py").write_text("import os\nfrom world import run_plan\n")
    found = import_guard.check([mind])
    assert names(found) == ["a_first.py", "z_bad.py", "z_bad.py"]
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "import_guard.py"), str(mind)],
                       capture_output=True, text=True, timeout=300)
    assert r.returncode == 1 and r.stdout.count("I02 forbids") == 3, r.stdout + r.stderr


def test_a_module_from_outside_numpy_is_refused():
    pairs = {("numpy.matlib", "warnings"), ("numpy.lib.format", "read_array"), ("numpy.random", "Philox"),
             ("numpy.no_such_module", "x")}
    assert import_guard._foreign_names(pairs) == {("numpy.matlib", "warnings")}


def _cache(mind, stem, source, invalidation=py_compile.PycInvalidationMode.TIMESTAMP):
    src = mind / f"{stem}.py"
    src.write_text(source)
    target = Path(importlib.util.cache_from_source(str(src)))
    py_compile.compile(str(src), cfile=str(target), invalidation_mode=invalidation, doraise=True)
    return target


def test_files_the_guard_cannot_read_are_refused(tmp_path):
    mind = tmp_path / "mind"
    (mind / "__pycache__").mkdir(parents=True)
    (mind / "__init__.py").write_text("import numpy\n")
    _cache(mind, "plain", "x = 1\n")                                       # Python's own cache: allowed
    _cache(mind, "tower", "x = 1\n", py_compile.PycInvalidationMode.UNCHECKED_HASH)
    _cache(mind, "checked", "x = 1\n", py_compile.PycInvalidationMode.CHECKED_HASH)
    sourceless = _cache(mind, "gone", "x = 1\n")
    (mind / "gone.py").unlink()
    (mind / "__pycache__" / "plain.cpython-0.pyc").write_bytes(b"\0" * 16)
    (mind / "__pycache__" / "_json.so").write_bytes(b"\0")
    (mind / "__pycache__" / "helper.py").write_text("x = 1\n")
    (mind / "hidden.pyc").write_bytes(b"\0")
    (mind / "fast.so").write_bytes(b"\0")
    (mind / "SHOUT.SO").write_bytes(b"\0")      # a distinct stem: Mac and Windows ignore case
    (mind / "tower2.pyw").write_text("import os\n")
    (mind / "upper.PY").write_text("x = 1\n")
    (mind / "lib.dll").write_bytes(b"\0")
    (mind / "notes.txt").write_text("not importable\n")
    found = import_guard.check([mind])
    assert names(found) == sorted([f"tower.{TAG}.pyc", f"checked.{TAG}.pyc", sourceless.name,
                                   "plain.cpython-0.pyc", "_json.so", "helper.py", "hidden.pyc", "fast.so",
                                   "SHOUT.SO", "tower2.pyw", "upper.PY", "lib.dll"])


def test_a_forged_cache_is_refused(tmp_path):
    """A timestamp .pyc that matches its source's mtime and size runs instead of it, so it must hold the same code."""
    mind = tmp_path / "mind"
    (mind / "__pycache__").mkdir(parents=True)
    (mind / "__init__.py").write_text("")
    src = mind / "foo.py"
    src.write_text("VALUE = 'benign'\n")
    st = src.stat()
    header = importlib.util.MAGIC_NUMBER + (0).to_bytes(4, "little") + \
        (int(st.st_mtime) & 0xFFFFFFFF).to_bytes(4, "little") + (st.st_size & 0xFFFFFFFF).to_bytes(4, "little")
    forged = Path(importlib.util.cache_from_source(str(src)))
    forged.write_bytes(header + marshal.dumps(compile("import world.run_plan\n", str(src), "exec")))
    assert names(import_guard.check([mind])) == [forged.name]
    # the same header with the source's own code is Python's cache: allowed
    forged.write_bytes(header + marshal.dumps(compile(src.read_bytes(), str(src), "exec", dont_inherit=True)))
    assert import_guard.check([mind]) == []
    # a stale cache, which Python recompiles, is harmless
    stale = header[:8] + (12345).to_bytes(4, "little") + header[12:]
    forged.write_bytes(stale + marshal.dumps(compile("import world.run_plan\n", str(src), "exec")))
    assert import_guard.check([mind]) == []


def _can_symlink(tmp_path):
    try:
        (tmp_path / "probe").symlink_to(tmp_path)
    except (OSError, NotImplementedError):
        return False
    (tmp_path / "probe").unlink()
    return True


def test_symlinks_are_refused(tmp_path):
    if not _can_symlink(tmp_path):
        pytest.skip("this machine cannot make symlinks")
    other = tmp_path / "other"
    other.mkdir()
    (other / "bad.py").write_text("import os\n")
    mind = tmp_path / "mind"
    mind.mkdir()
    (mind / "__init__.py").write_text("")
    (mind / "w").symlink_to(other, target_is_directory=True)
    (mind / "link.py").symlink_to(other / "bad.py")
    (mind / "dangling.py").symlink_to(tmp_path / "nowhere.py")
    found = import_guard.check([mind])
    assert names(found) == ["dangling.py", "link.py", "w"]
    assert all(what == "a symlink" for _, _, what in found)
    shutil.rmtree(other)


def test_no_cache_or_compiled_file_is_committed():
    """Git must never carry a file the guard would refuse, such as a .pyc that Python could run instead of its source."""
    if shutil.which("git") is None or not (ROOT / ".git").exists():
        pytest.skip("not a git checkout")
    r = subprocess.run(["git", "ls-files", "src/mind"], cwd=ROOT, capture_output=True, text=True, check=True)
    tracked = [line for line in r.stdout.splitlines() if line]
    assert tracked and all(line.endswith(".py") and "__pycache__" not in line for line in tracked), tracked


def test_the_mind_package_loads_nothing_forbidden():
    """Run-time check: importing every mind module pulls in no world, harness, bot or fixture module."""
    code = ("import pkgutil, sys, mind, importlib\n"
            "for m in pkgutil.walk_packages(mind.__path__, 'mind.'):\n"
            "    importlib.import_module(m.name)\n"
            "bad = [m for m in sys.modules if m.split('.')[0] in "
            "{'world', 'harness', 'baselines', 'twins', 'test_fixtures'}]\n"
            "print(bad)\nsys.exit(1 if bad else 0)\n")
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    assert r.returncode == 0, r.stdout + r.stderr
