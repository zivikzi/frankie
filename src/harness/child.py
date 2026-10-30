"""The mind's own process: the far end of the harness's subprocess host (KT-89, KT-93).

The harness starts this file as a script, in a fresh interpreter with no site
packages, an empty working directory and a scrubbed environment. It then:

1. reads one line of setup from the harness (the mind's package root and the
   directories NumPy and Numba live in);
2. imports NumPy (and Numba, if present), then the mind's entry module
   `<package>.entry`;
3. installs an audit hook (PEP 578) that from then on refuses any import of a
   new module outside NumPy, Numba and the mind's package, any file opened
   outside the directories it was given, and any socket, subprocess, process,
   signal, ctypes or file-system change;
4. answers the harness's requests, one JSON line each, until told to quit.

Only plain data crosses the pipe: JSON numbers, strings, booleans, null,
lists and objects, with arrays sent as lists of floats. Nothing is pickled in
either direction, so the mind can hand the harness no object and the harness
hands the mind no world object, plan, key or label. The mind's own printing
goes to the error stream, never into the protocol.

This file imports only the standard library and NumPy. The harness imports its
codec and state fingerprint from here, so both sides use one implementation.
"""

import hashlib
import json
import math
import os
import struct
import sys

try:
    import numpy as np
except ImportError:       # in the mind's own process, main() adds NumPy's directory first
    np = None

MAX_LINE = 64 * 1024 * 1024      # refuse a message longer than this (64 MiB)


# ---------------------------------------------------------------- codec

def _refuse_constant(name):
    raise ValueError(f"{name} is not a number the bench accepts")


def decode(line: str):
    if len(line) > MAX_LINE:
        raise ValueError("message too long")
    return json.loads(line, parse_constant=_refuse_constant)


def encode(obj) -> str:
    return json.dumps(plain(obj), allow_nan=False, separators=(",", ":"))


def plain(obj):
    """obj as JSON-ready plain data: arrays become lists, tuples lists, NumPy scalars Python ones."""
    if obj is None or isinstance(obj, (bool, str)):
        return obj
    if isinstance(obj, (int, np.integer)) and not isinstance(obj, np.bool_):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, (float, np.floating)):
        x = float(obj)
        if not math.isfinite(x):
            raise ValueError("non-finite number")
        return x
    if isinstance(obj, np.ndarray):
        return [plain(x) for x in obj.tolist()]
    if isinstance(obj, (list, tuple)):
        return [plain(x) for x in obj]
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if not isinstance(k, str):
                raise ValueError("object keys must be strings")
            out[k] = plain(v)
        return out
    raise ValueError(f"{type(obj).__name__} cannot cross the interface")


def packet(values):
    """A fresh, read-only float64 array that owns its data (FORBIDDEN 18)."""
    a = np.array([float(x) for x in values], dtype=np.float64)
    a.flags.writeable = False
    return a


# ---------------------------------------------------------------- state fingerprint

def _walk(obj, out, seen):
    if obj is None:
        out.append(b"N")
    elif isinstance(obj, (bool, np.bool_)):
        out.append(b"T" if obj else b"F")
    elif isinstance(obj, (int, np.integer)):
        out.append(b"I" + str(int(obj)).encode() + b";")
    elif isinstance(obj, (float, np.floating)):
        out.append(b"D" + struct.pack("<d", float(obj)))
    elif isinstance(obj, str):
        b = obj.encode("utf-8")
        out.append(b"S" + str(len(b)).encode() + b":" + b)
    elif isinstance(obj, bytes):
        out.append(b"B" + str(len(obj)).encode() + b":" + obj)
    elif isinstance(obj, np.ndarray):
        a = np.ascontiguousarray(obj)
        out.append(b"A" + a.dtype.str.encode() + repr(a.shape).encode() + a.tobytes())
    else:
        if id(obj) in seen:
            raise ValueError("mind state may not hold a cycle")
        seen = seen | {id(obj)}
        if isinstance(obj, (list, tuple)):
            out.append(b"L" if isinstance(obj, list) else b"U")
            out.append(str(len(obj)).encode() + b"[")
            for x in obj:
                _walk(x, out, seen)
            out.append(b"]")
        elif isinstance(obj, dict):
            parts = []
            for k, v in obj.items():
                kb, vb = [], []
                _walk(k, kb, seen)
                _walk(v, vb, seen)
                parts.append((b"".join(kb), b"".join(vb)))
            parts.sort()
            out.append(b"M" + str(len(parts)).encode() + b"{")
            for kb, vb in parts:
                out.append(kb)
                out.append(vb)
            out.append(b"}")
        elif isinstance(obj, (set, frozenset)):
            parts = []
            for x in obj:
                xb = []
                _walk(x, xb, seen)
                parts.append(b"".join(xb))
            parts.sort()
            out.append(b"Z" + str(len(parts)).encode() + b"{" + b"".join(parts) + b"}")
        elif hasattr(obj, "__dict__") or hasattr(type(obj), "__slots__"):
            cls = type(obj)
            out.append(b"O" + (cls.__module__ + "." + cls.__qualname__).encode() + b"(")
            fields = dict(getattr(obj, "__dict__", {}))
            for name in getattr(cls, "__slots__", ()):
                if hasattr(obj, name):
                    fields[name] = getattr(obj, name)
            _walk(fields, out, seen)
            out.append(b")")
        else:
            raise ValueError(f"mind state may not hold a {type(obj).__name__}")


def module_state(module) -> dict:
    """The data a module holds at its top level: everything but modules, functions and classes."""
    out = {}
    for name, value in sorted(vars(module).items()):
        if name.startswith("__") or callable(value) or type(value).__name__ == "module":
            continue
        out[name] = value
    return out


def state_fingerprint(mind, modules=()) -> str:
    """A canonical SHA-256 of everything a mind holds, and of its modules' top-level data.

    Arrays count by dtype, shape and bytes; a dict counts its items whatever
    their order. Used by the counter check (FORBIDDEN 9) and the check-order
    test, which compare states bit for bit.
    """
    out = []
    _walk(mind, out, frozenset())
    for m in modules:
        out.append(b"#" + m.__name__.encode())
        _walk(module_state(m), out, frozenset())
    return hashlib.sha256(b"".join(out)).hexdigest()


# ---------------------------------------------------------------- the child's loop

_BANNED_EVENT_PREFIXES = (
    "socket.", "subprocess.", "os.system", "os.exec", "os.spawn", "os.posix_spawn", "os.fork",
    "os.kill", "os.killpg", "os.remove", "os.unlink", "os.rename", "os.rmdir", "os.mkdir",
    "os.chdir", "os.chmod", "os.chown", "os.truncate", "os.symlink", "os.link", "os.putenv",
    "os.unsetenv", "glob.", "shutil.", "ctypes.", "signal.", "sys.settrace", "sys.setprofile",
    "sys._getframe", "sys.addaudithook", "code.__new__", "function.__new__", "pickle.",
    "urllib.", "http.", "ftplib.", "smtplib.", "webbrowser.", "winreg.", "_winapi.", "msvcrt.",
    "sqlite3.", "mmap.",
)


def _install_hook(allowed_roots, allowed_top):
    roots = tuple(os.path.normcase(os.path.abspath(r)) + os.sep for r in allowed_roots)

    def hook(event, args):
        if event == "import":
            name = args[0]
            if name.split(".")[0] in allowed_top:
                return
            raise ImportError(f"the mind's process may not import {name}")
        if event == "open":
            path = args[0]
            if isinstance(path, int):
                raise PermissionError("the mind's process may not open file descriptors")
            mode = args[1] if len(args) > 1 and isinstance(args[1], str) else "r"
            if any(c in mode for c in "wax+"):
                raise PermissionError("the mind's process may not write files")
            p = os.path.normcase(os.path.abspath(os.fsdecode(path)))
            if not p.startswith(roots):
                raise PermissionError(f"the mind's process may not open {path!r}")
            return
        if event.startswith(_BANNED_EVENT_PREFIXES):
            raise PermissionError(f"the mind's process may not use {event}")

    sys.addaudithook(hook)


def _serve(entry, proto_in, proto_out, mind_modules):
    minds = {}

    def reply(obj):
        proto_out.write(encode(obj) + "\n")
        proto_out.flush()

    while True:
        line = proto_in.readline()
        if not line:
            return
        try:
            msg = decode(line)
            op = msg["op"]
            if op == "quit":
                reply({"ok": True})
                return
            if op == "new":
                minds[msg["name"]] = entry.make(msg["config"])
                out = None
            elif op == "copy":
                minds[msg["dst"]] = _deepcopy(minds[msg["src"]])
                out = None
            elif op == "drop":
                del minds[msg["name"]]
                out = None
            elif op == "decide":
                out = minds[msg["name"]].decide(packet(msg["visible"]), int(msg["energy_milli"]))
            elif op == "land":
                out = minds[msg["name"]].land(int(msg["delta_milli"]), int(msg["energy_after_milli"]),
                                              packet(msg["taste"]))
            elif op == "write":
                out = minds[msg["name"]].write()
            elif op == "dump":
                out = minds[msg["name"]].dump()
            elif op == "info":
                out = minds[msg["name"]].info()
            elif op == "fingerprint":
                out = state_fingerprint(minds[msg["name"]], mind_modules())
            elif op == "modules":
                out = sorted(sys.modules)
            else:
                raise ValueError(f"unknown request {op!r}")
            reply({"ok": True, "out": out})
        except Exception as e:      # the harness turns this into an error and stops the run
            reply({"ok": False, "error": f"{type(e).__name__}: {e}"})


def _deepcopy(obj):
    import copy                    # loaded before the hook goes in (see main)
    return copy.deepcopy(obj)


def main():
    import copy  # noqa: F401  (loaded now, so _deepcopy needs no import after the hook)
    proto_in = sys.stdin
    proto_out = os.fdopen(os.dup(sys.stdout.fileno()), "w", encoding="utf-8", newline="\n")
    sys.stdout = sys.stderr       # the mind's own printing goes to the error stream
    setup = decode(proto_in.readline())
    package_root, package = setup["package_root"], setup["package"]
    for d in reversed(setup["library_dirs"]):
        sys.path.insert(0, d)
    sys.path.insert(0, package_root)
    global np
    import numpy as np
    try:
        import numba  # noqa: F401
    except ImportError:
        pass
    entry = __import__(package + ".entry", fromlist=["make"])
    allowed_top = {"numpy", "numba", "llvmlite", package}
    roots = [package_root] + setup["library_dirs"] + setup["stdlib_dirs"]
    _install_hook(roots, allowed_top)

    def mind_modules():
        return [m for name, m in sorted(sys.modules.items())
                if m is not None and (name == package or name.startswith(package + "."))]

    proto_out.write(encode({"ok": True, "ready": True}) + "\n")
    proto_out.flush()
    _serve(entry, proto_in, proto_out, mind_modules)


if __name__ == "__main__":
    main()
