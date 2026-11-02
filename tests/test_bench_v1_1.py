"""The bench fixes of v1.1 (rows KT-117 to KT-124): each gap Week 3 found in the frozen bench, and its fix."""

import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import import_guard  # noqa: E402
import mind_checks as mc  # noqa: E402

from harness.agents import tower_minds  # noqa: E402
from harness.host import PACKAGE_USES, InProcessHost, MindError, SubprocessHost  # noqa: E402
from harness.readings_cache import ReadingCache  # noqa: E402
from harness.run import Lineage, RunError, run_one  # noqa: E402
from world import keys  # noqa: E402
from world.run_plan import generate_run  # noqa: E402

TEMPLATE = textwrap.dedent('''
    {imports}


    class Probe:
        def __init__(self, config):
            self.config = config

        def info(self):
            {body}

        def dump(self):
            {dump}


    def make(config):
        return Probe(config)
''')


def package(root, name, imports="import numpy as np", body="return {}", dump="return {}", extra=None):
    d = root / name
    d.mkdir(parents=True)
    (d / "__init__.py").write_text("")
    (d / "entry.py").write_text(TEMPLATE.format(imports=imports, body=body, dump=dump))
    for file, text in (extra or {}).items():
        (d / file).write_text(textwrap.dedent(text))
    return d


# ---------------------------------------------------------------- gap 1: the twins use K-F's code (section 6)

def test_only_the_twins_use_another_package():
    assert PACKAGE_USES == {"twins": ("mind",)}


def test_the_twins_run_k_fs_code_in_their_own_process(tmp_path):
    package(tmp_path, "mind", extra={"shared.py": "def triple(x):\n    return 3 * x\n"})
    twins = package(tmp_path, "twins", imports="import mind.shared", body='return {"v": mind.shared.triple(2)}')
    with SubprocessHost(twins) as host:
        host.new("m", {})
        assert host.info("m") == {"v": 6}
        mods = host.loaded_modules()
    assert "mind.shared" in mods and "twins.entry" in mods
    assert not [m for m in mods if m.split(".")[0] in ("world", "harness", "baselines", "test_fixtures")]


def test_k_fs_code_never_imports_the_twins(tmp_path):
    """FORBIDDEN 26: the mind package may import only itself, even when it runs beside the twins."""
    package(tmp_path, "mind", extra={"shared.py": "import twins.entry\n"})
    twins = package(tmp_path, "twins", imports="import mind.shared")
    with pytest.raises(MindError, match="the mind package may not import twins"):
        SubprocessHost(twins)


def test_the_twins_may_import_nothing_else(tmp_path):
    package(tmp_path, "mind")
    twins = package(tmp_path, "twins", body="import harness\n        return {}")
    with SubprocessHost(twins) as host:
        host.new("m", {})
        with pytest.raises(MindError, match="may not import harness"):
            host.info("m")


def test_the_twins_need_the_mind_package_beside_them(tmp_path):
    with pytest.raises(MindError, match="needs the mind package"):
        SubprocessHost(package(tmp_path, "twins"))


def test_tw7_in_its_own_process_gives_the_in_process_record():
    import twins.entry as tw
    spec = tower_minds(None)[-1]
    assert spec.label == "TW7" and spec.host == "subprocess"
    plan = generate_run("tuning", keys.tuning_set_key(), 3, 2)
    a = run_one(plan, spec, ReadingCache(plan.noise_key), package_dir=ROOT / "src" / "twins")
    b = run_one(plan, spec, ReadingCache(plan.noise_key), host=InProcessHost(tw.make))
    assert a.decisions == b.decisions and a.lineage_log == b.lineage_log and a.info == b.info


# ---------------------------------------------------------------- gap 2: a split copies its parent (KT-72)

class Scripted:
    """A host whose dumps and writes are given in advance, for _DumpAfterWrite."""

    def __init__(self, dumps, events):
        self.dumps = list(dumps)
        self.events = events

    def dump(self, name):
        return {"candidates": [{"slot": s, "weights_tenths": w} for s, w in self.dumps.pop(0).items()]}

    def write(self, name):
        return {"events": self.events}


def ev(t, slot, parent=None):
    return {"type": t, "slot": slot, "parent_slot": parent}


def birth_findings(before, after, events):
    out = []
    mc._DumpAfterWrite(Scripted([before, after], events), out).write("main")
    return [f.check for f in out]


W5, W6 = [5] * 22, [5] * 21 + [7]


@pytest.mark.parametrize("before,after,events,found", [
    ({}, {0: W5}, [ev("new", 0)], []),
    ({}, {0: W6}, [ev("new", 0)], ["M20 equal weights"]),
    ({0: W5}, {0: W6, 1: W6}, [ev("split", 1, 0)], []),                       # the child copies the raised parent
    ({0: W5}, {0: W6, 1: W5}, [ev("split", 1, 0)], ["KT-72 split copies its parent"]),
    ({0: W5}, {0: W6}, [ev("forget", 0), ev("split", 0, 0)], []),             # the parent forgotten (KT-75)
    ({0: W5}, {0: [5] * 21 + [8]}, [ev("forget", 0), ev("split", 0, 0)], ["KT-72 split copies its parent"]),
    ({0: W6}, {0: [4] + [5] * 20 + [7]}, [ev("forget", 0), ev("split", 0, 0)], ["KT-72 split copies its parent"]),
])
def test_the_birth_check_holds_new_kinds_at_5_tenths_and_splits_to_their_parent(before, after, events, found):
    assert birth_findings(before, after, events) == found


def test_the_birth_check_passes_tw7_where_v1_flagged_it():
    """Tuning family 4 holds a split; the v1 check wanted the child at 5 tenths."""
    spec = tower_minds(None)[-1]
    plan = generate_run("tuning", keys.tuning_set_key(), 4, 1)
    assert mc.birth_check(spec, ROOT / "src" / "twins", plan) == []


# ---------------------------------------------------------------- gap 3: forgetting a split's own parent (KT-75)

def test_a_split_may_name_a_parent_forgotten_in_the_same_write():
    lin = Lineage()
    assert lin.apply([ev("new", 0) | {"trigger": "chosen-eat", "layer": None}], "t1") == "c1"
    filed = lin.apply([ev("forget", 0), ev("split", 0, 0) | {"trigger": "chosen-eat", "layer": "details"}], "q2")
    assert filed == "c2" and lin.parent["c2"] == "c1" and lin.slot_lid == {0: "c2"}
    assert lin.h == {"c1", "c2"}                      # its parent was in the H set, so it joins (KT-98)
    assert [e["type"] for e in lin.log] == ["new", "forget", "split"] and lin.log[-1]["parent"] == "c1"


def test_a_split_naming_an_empty_slot_still_stops_the_run():
    lin = Lineage()
    with pytest.raises(RunError, match="holds no candidate"):
        lin.apply([ev("split", 0, 3) | {"trigger": "chosen-eat", "layer": "details"}], "q2")


# ---------------------------------------------------------------- gap 4: the mind checks' command line

def test_the_command_line_finds_each_registered_configuration():
    assert mc.registered_spec(ROOT / "src" / "twins", "TW7").label == "TW7"
    assert mc.registered_spec(ROOT / "src" / "mind", "K-F", spike_nano=5).unit_nano == 5
    for args, why in (((ROOT / "src" / "mind", "K-F"), "--spike-nano"),
                      ((ROOT / "src" / "mind", "OS01-cap"), "checked as K-F"),
                      ((ROOT / "src" / "mind", "TW7"), "lives in the twins package"),
                      ((ROOT / "src" / "twins", "TW9"), "not a registered")):
        with pytest.raises(ValueError, match=why):
            mc.registered_spec(*args)


def test_the_command_line_checks_tw7():
    assert mc.main(["mind_checks.py", str(ROOT / "src" / "twins"), "TW7"]) == 0


# ---------------------------------------------------------------- gaps 5 and 6: Numba, locked and in the sandbox

def test_numba_is_locked():
    lock = (ROOT / "uv.lock").read_text()
    assert 'name = "numba"\nversion = "0.68.0"' in lock and 'name = "llvmlite"\nversion = "0.50.0"' in lock
    assert '"numba",' in (ROOT / "pyproject.toml").read_text()


NUMBA_BODY = '''
    import numba
    import numpy as np


    @numba.njit
    def trace(a, s):
        out = np.zeros(a.shape[0])
        for i in range(a.shape[0]):
            out[i] = out[i - 1] * s + a[i]
        return out, out.sum()


    @numba.njit
    def check(k):
        if k > 2:
            raise ValueError("too many")
        return k
'''


def test_numba_compiles_and_runs_inside_the_sandbox(tmp_path):
    d = package(tmp_path, "mind", imports="import numpy as np\nimport mind.loops",
                body="out, total = mind.loops.trace(np.arange(3.0), 0.5)\n"
                     "        return {'out': out, 'total': float(total), 'k': mind.loops.check(1)}",
                dump="return {'k': mind.loops.check(5)}",
                extra={"loops.py": NUMBA_BODY})
    with SubprocessHost(d) as host:
        host.new("m", {})
        assert host.info("m") == {"out": [0.0, 1.0, 2.5], "total": 3.5, "k": 1}
        with pytest.raises(MindError, match="too many"):
            host.dump("m")


# Routes to ctypes and pickle through Numba's own modules. The import guard refuses them (KT-119); these
# check that the sandbox refuses them too, so Numba's allowances (KT-118) stay as narrow as written.
ROUTES = {
    "load a library": "numba.core.typing.ctypes_utils.ctypes.CDLL('frankie-no-such-library')",
    "look up a C function": "numba.core.typing.ctypes_utils.ctypes.pythonapi.Py_GetVersion",
    "unpickle a function": "numba.core.serialize.pickle.loads(b'cos\\nsystem\\n.')",
    "unpickle a builtin": "numba.core.serialize.pickle.loads(b'cbuiltins\\nopen\\n.')",
}


@pytest.mark.parametrize("what", sorted(ROUTES))
def test_numbas_allowances_open_nothing_else(tmp_path, what):
    d = package(tmp_path, "mind", imports="import numba\nimport numba.core.typing.ctypes_utils\n"
                                          "import numba.core.serialize",
                body=ROUTES[what] + "\n        return {}")
    with SubprocessHost(d) as host:
        host.new("m", {})
        with pytest.raises(MindError, match="may not use (ctypes.dlopen|ctypes.dlsym|pickle.find_class)"):
            host.info("m")


GUARDED = textwrap.dedent('''
    import numba
    import numba as nb
    from numba import njit
    from numba import njit as jit


    @numba.njit
    def a(x):
        return x


    @njit
    def b(x):
        return x


    @jit("float64(float64)")
    def c(x):
        return x
''')

REFUSED = {
    "from numba import prange": "from numba import prange",
    "from numba.extending import intrinsic": "from numba.extending import intrinsic",
    "import numba.core": "import numba.core",
    "x = numba.objmode": "numba.objmode",
    "x = nb.cfunc": "numba.cfunc",
    "@numba.njit(fastmath=True)\ndef d(x):\n    return x": "fastmath",
    "@njit(parallel=True)\ndef d(x):\n    return x": "parallel",
    "@jit(cache=True)\ndef d(x):\n    return x": "cache",
    "@nb.njit(**{})\ndef d(x):\n    return x": "**",
}


def test_the_guard_lets_the_mind_use_njit(tmp_path):
    d = tmp_path / "mind"
    d.mkdir()
    (d / "a.py").write_text(GUARDED)
    assert import_guard.check([d]) == []


@pytest.mark.parametrize("line", sorted(REFUSED))
def test_the_guard_refuses_the_rest_of_numba(tmp_path, line):
    d = tmp_path / "mind"
    d.mkdir()
    (d / "a.py").write_text(GUARDED + "\n\n" + line + "\n")
    found = import_guard.check([d])
    assert len(found) == 1 and REFUSED[line] in found[0][2] and "KT-119" in found[0][2]
