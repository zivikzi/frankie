"""Where a mind lives while it runs: in the harness's own process, or in a process of its own.

Both hosts hold a mind's states under names ("main", "S1", "probe", ...) and
answer the same requests: new, copy, drop, decide, land, write, dump, info and
fingerprint. Everything that crosses goes through the plain-data codec in
child.py, both ways, so a bot run in-process and a mind run in its own process
hand the harness the same kind of answer (KT-93).

- InProcessHost runs frozen bench code: the bots and B1n-mind (src/baselines).
- SubprocessHost runs a mind package (src/mind, src/twins, or the stub in
  src/test_fixtures) in a fresh interpreter that can reach nothing but NumPy,
  Numba and its own package (child.py). This is the run-time half of keeping
  minds away from the world's objects, which the static import guard cannot
  give on its own (KT-89).
"""

import copy
import importlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
import sysconfig
import tempfile

import numpy as np

from . import child

CHILD_SCRIPT = pathlib.Path(child.__file__).resolve()


class MindError(RuntimeError):
    """A mind failed, or broke the interface. The run stops; nothing is retried."""


def _roundtrip(obj):
    """obj as the plain data the other side of a pipe would receive."""
    return child.decode(child.encode(obj))


def _guarded(method):
    """Any failure of the mind or of the codec becomes a MindError, as it does across a pipe (KT-95)."""
    def call(self, *args):
        try:
            return method(self, *args)
        except MindError:
            raise
        except Exception as e:
            raise MindError(f"{type(e).__name__}: {e}") from e
    return call


class InProcessHost:
    def __init__(self, factory):
        self._factory = factory
        self._minds = {}

    @_guarded
    def new(self, name, config):
        self._minds[name] = self._factory(_roundtrip(config))

    @_guarded
    def copy(self, src, dst):
        self._minds[dst] = copy.deepcopy(self._minds[src])

    def drop(self, name):
        del self._minds[name]

    @_guarded
    def decide(self, name, visible, energy_milli):
        return _roundtrip(self._minds[name].decide(child.packet(visible), int(energy_milli)))

    @_guarded
    def land(self, name, delta_milli, energy_after_milli, taste):
        return _roundtrip(self._minds[name].land(int(delta_milli), int(energy_after_milli),
                                                 child.packet(taste)))

    @_guarded
    def write(self, name):
        return _roundtrip(self._minds[name].write())

    @_guarded
    def dump(self, name):
        return _roundtrip(self._minds[name].dump())

    @_guarded
    def info(self, name):
        return _roundtrip(self._minds[name].info())

    def fingerprint(self, name):
        mind = self._minds[name]
        mod = sys.modules[type(mind).__module__]
        return child.state_fingerprint(mind, [mod])

    def close(self):
        self._minds.clear()


def factory_from(entry: str):
    """'package.module:Name' -> the callable it names."""
    module, _, name = entry.partition(":")
    return getattr(importlib.import_module(module), name)


def _library_dirs():
    dirs = [str(pathlib.Path(np.__file__).resolve().parent.parent)]
    try:
        import numba   # noqa: F401  (Week 3 adds it; the host only needs its directory)
        d = str(pathlib.Path(numba.__file__).resolve().parent.parent)
        if d not in dirs:
            dirs.append(d)
    except ImportError:
        pass
    return dirs


def _stdlib_dirs():
    paths = sysconfig.get_paths()
    return sorted({str(pathlib.Path(paths[k]).resolve()) for k in ("stdlib", "platstdlib")})


class SubprocessHost:
    """A mind package run in its own interpreter (child.py).

    package_dir is the directory of the package to run (its name is the
    package's import name, `mind` for the mind package and the stub). Only its
    .py files are copied, into a fresh temporary directory, and only that copy
    is put on the child's path. The child gets an empty working directory and
    an environment holding nothing but a fixed hash seed (and, on Windows, the
    system root it needs to start).
    """

    def __init__(self, package_dir, hash_seed: str = "0"):
        package_dir = pathlib.Path(package_dir).resolve()
        self.package = package_dir.name
        self._proc = self._stderr = None
        self._tmp = tempfile.mkdtemp(prefix="frankie-mind-")
        try:
            self._start(package_dir, hash_seed)
        except BaseException:
            self.close()                # a mind that fails to start leaves no process or folder behind
            raise

    def _start(self, package_dir, hash_seed):
        root = pathlib.Path(self._tmp, "root")
        for src in sorted(package_dir.rglob("*.py")):
            rel = src.relative_to(package_dir)
            if "__pycache__" in rel.parts:
                continue
            dst = root / self.package / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
        work = pathlib.Path(self._tmp, "work")
        work.mkdir()
        env = {"PYTHONHASHSEED": str(hash_seed), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
        if "SYSTEMROOT" in os.environ:
            env["SYSTEMROOT"] = os.environ["SYSTEMROOT"]
        self._stderr = open(pathlib.Path(self._tmp, "stderr.txt"), "w+", encoding="utf-8")
        self._proc = subprocess.Popen(
            [sys.executable, "-S", "-P", str(CHILD_SCRIPT)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self._stderr,
            cwd=work, env=env, text=True, encoding="utf-8", bufsize=1)
        self._send({"package_root": str(root), "package": self.package,
                    "library_dirs": _library_dirs(), "stdlib_dirs": _stdlib_dirs()})
        ready = self._receive()
        if not ready.get("ready"):
            raise MindError(f"the mind's process did not start: {ready}")

    def _send(self, msg):
        try:
            self._proc.stdin.write(child.encode(msg) + "\n")
            self._proc.stdin.flush()
        except (BrokenPipeError, OSError) as e:
            raise MindError(f"the mind's process is gone: {e}{self._stderr_tail()}") from None

    def _receive(self):
        line = self._proc.stdout.readline()
        if not line:
            raise MindError(f"the mind's process closed its pipe{self._stderr_tail()}")
        try:
            msg = child.decode(line)
        except (ValueError, json.JSONDecodeError) as e:
            raise MindError(f"the mind's process sent something that is not plain data: {e}") from None
        if not isinstance(msg, dict) or not msg.get("ok"):
            err = msg.get("error") if isinstance(msg, dict) else msg
            raise MindError(f"{err}{self._stderr_tail()}")
        return msg

    def _stderr_tail(self):
        try:
            self._stderr.flush()
            self._stderr.seek(0)
            text = self._stderr.read()[-2000:]
        except (OSError, ValueError):
            return ""
        return f"\n--- the mind's error stream ---\n{text}" if text.strip() else ""

    def _request(self, msg):
        self._send(msg)
        return self._receive().get("out")

    def new(self, name, config):
        self._request({"op": "new", "name": name, "config": config})

    def copy(self, src, dst):
        self._request({"op": "copy", "src": src, "dst": dst})

    def drop(self, name):
        self._request({"op": "drop", "name": name})

    def decide(self, name, visible, energy_milli):
        return self._request({"op": "decide", "name": name, "visible": list(visible),
                              "energy_milli": int(energy_milli)})

    def land(self, name, delta_milli, energy_after_milli, taste):
        return self._request({"op": "land", "name": name, "delta_milli": int(delta_milli),
                              "energy_after_milli": int(energy_after_milli), "taste": list(taste)})

    def write(self, name):
        return self._request({"op": "write", "name": name})

    def dump(self, name):
        return self._request({"op": "dump", "name": name})

    def info(self, name):
        return self._request({"op": "info", "name": name})

    def fingerprint(self, name):
        return self._request({"op": "fingerprint", "name": name})

    def loaded_modules(self):
        return self._request({"op": "modules"})

    def close(self):
        if self._proc is not None and self._proc.poll() is None:
            try:
                self._request({"op": "quit"})
            except MindError:
                pass
            try:
                self._proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._proc.kill()
                self._proc.wait()
        pipes = (self._proc.stdin, self._proc.stdout) if self._proc is not None else ()
        for f in pipes + (self._stderr,):
            try:
                if f is not None:
                    f.close()
            except OSError:
                pass
        shutil.rmtree(self._tmp, ignore_errors=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
