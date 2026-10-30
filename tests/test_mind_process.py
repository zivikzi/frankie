"""The mind's own process: plain data only, and nothing reachable but NumPy and its package (KT-93)."""

import textwrap
from pathlib import Path

import numpy as np
import pytest

from harness import child
from harness.host import MindError, SubprocessHost
from test_fixtures.stub import STUB_DIR

PROBE = textwrap.dedent('''
    import numpy as np


    class Probe:
        def __init__(self, config):
            self.config = config

        def decide(self, visible, energy_milli):
            return {"writeable": bool(visible.flags.writeable), "n": int(visible.shape[0])}

        def land(self, delta, after, taste):
            return {"taste": [float(x) for x in taste]}

        def write(self):
            return {"events": []}

        def dump(self):
            return {}

        def info(self):
            return self.config


    def make(config):
        return Probe(config)
''')

ATTEMPTS = {
    "read a file": 'open("/etc/hostname").read()',
    "write a file": 'open("x.txt", "w").write("x")',
    "import socket": "import socket",
    "import the world": "import world",
    "import the harness": "import harness",
    "run a program": "import os; os.system('true')",
    "open a file descriptor": "import os; os.fdopen(0)",
}


def package(tmp_path, body):
    d = tmp_path / "mind"
    d.mkdir()
    (d / "__init__.py").write_text("")
    (d / "entry.py").write_text(body)
    return d


def attempt(tmp_path, code):
    body = PROBE.replace("        return self.config", "        " + code + "\n        return {}")
    return package(tmp_path, body)


def test_the_codec_refuses_what_is_not_plain_data():
    with pytest.raises(ValueError):
        child.encode({"x": float("nan")})
    with pytest.raises(ValueError):
        child.decode('{"x": NaN}')
    assert child.decode(child.encode({"a": np.float64(0.5), "b": np.arange(3), "c": (1, 2)})) == \
        {"a": 0.5, "b": [0, 1, 2], "c": [1, 2]}
    p = child.packet([0.1, 0.2])
    assert p.dtype == np.float64 and not p.flags.writeable


def test_a_packet_arrives_read_only(tmp_path):
    with SubprocessHost(package(tmp_path, PROBE)) as host:
        host.new("m", {"x": 1})
        assert host.decide("m", [0.5] * 18, 1000) == {"writeable": False, "n": 18}
        assert host.land("m", 1, 2, [0.1, 0.2, 0.3, 0.4]) == {"taste": [0.1, 0.2, 0.3, 0.4]}
        assert host.info("m") == {"x": 1}


@pytest.mark.parametrize("what", sorted(ATTEMPTS))
def test_the_mind_cannot_reach_outside_its_package(tmp_path, what):
    with SubprocessHost(attempt(tmp_path, ATTEMPTS[what])) as host:
        host.new("m", {})
        with pytest.raises(MindError):
            host.info("m")


def test_nothing_of_the_world_or_the_harness_is_loaded_in_the_minds_process():
    with SubprocessHost(STUB_DIR) as host:
        mods = host.loaded_modules()
    assert not [m for m in mods if m.split(".")[0] in ("world", "harness", "baselines", "test_fixtures", "twins")]
    assert "mind.entry" in mods


def test_the_minds_process_has_a_scrubbed_environment(monkeypatch):
    import subprocess
    seen = {}
    real = subprocess.Popen

    def spy(*args, **kwargs):
        seen.update(kwargs)
        return real(*args, **kwargs)
    monkeypatch.setattr(subprocess, "Popen", spy)
    with SubprocessHost(STUB_DIR, hash_seed="7"):
        assert Path(seen["cwd"]).name == "work" and not any(Path(seen["cwd"]).iterdir())
    assert set(seen["env"]) <= {"PYTHONHASHSEED", "PYTHONDONTWRITEBYTECODE", "PYTHONIOENCODING", "SYSTEMROOT"}
    assert seen["env"]["PYTHONHASHSEED"] == "7"


def test_numpys_own_parts_work_inside_the_sandbox(tmp_path):
    code = "import numpy as np\n        np.random.default_rng(1).random()"
    with SubprocessHost(attempt(tmp_path, code)) as host:
        host.new("m", {})
        assert host.info("m") == {}


def test_a_crashed_mind_stops_with_an_error(tmp_path):
    with SubprocessHost(attempt(tmp_path, "raise RuntimeError('boom')")) as host:
        host.new("m", {})
        with pytest.raises(MindError, match="boom"):
            host.info("m")


def test_already_loaded_modules_are_refused_too(tmp_path):
    for code in ("import os", "import sys", "import json", "from os import path", "import numpy.random"):
        d = tmp_path / code.replace(" ", "_").replace(".", "_")
        d.mkdir()
        pkg = attempt(d, code)
        with SubprocessHost(pkg) as host:
            host.new("m", {})
            if code == "import numpy.random":
                assert host.info("m") == {}
            else:
                with pytest.raises(MindError, match="may not import"):
                    host.info("m")


def test_writing_through_os_open_is_refused(tmp_path):
    code = "import numpy as np\n        np.save('x.npy', np.zeros(2))"
    with SubprocessHost(attempt(tmp_path, code)) as host:
        host.new("m", {})
        with pytest.raises(MindError):
            host.info("m")


def test_the_entry_module_runs_inside_the_sandbox(tmp_path):
    body = "import socket\n" + PROBE
    with pytest.raises(MindError):
        SubprocessHost(package(tmp_path, body))
