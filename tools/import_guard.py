"""The import guard (LEDGER I02, KT-89).

The build fails if any module of the mind package imports anything but NumPy
and Numba, or imports from baselines, test fixtures, the world or the
harness. Read strictly: the standard library is not allowed either, except
`from __future__ import ...`, which changes no behaviour at run time. Inside
the package, a mind module imports another by its full name (`mind.x`).
Relative imports are refused, since mind code could point them elsewhere by
setting `__package__`.

It also refuses these disguises:

- any use of `__import__` or `importlib`, and any use of the built-ins
  `exec`, `eval`, `compile`, `globals`, `vars`, `locals`, `getattr`,
  `setattr`, `delattr`, `help` and `breakpoint`;
- any dunder name (`__builtins__`, `__package__`, `__spec__` and so on, all
  but `__all__`, `__doc__`, `__version__`, `__slots__` and `__debug__`), and
  the names and attributes in FORBIDDEN_NAMES and FORBIDDEN_ATTRIBUTES, which
  reach the import machinery, loaded modules, a module's globals or a frame
  (`.modules`, `.meta_path`, `.__globals__`, `.f_globals` and the like),
  whether used, bound, imported, imported under another name or written as
  a string;
- a name imported from NumPy or Numba that is itself a module from outside
  them (NumPy modules hold `sys` and `os`, for example), and any import or
  attribute of their private, test, build or `__main__` modules (`f2py`,
  `ctypeslib`, `testing` and the like), which run code at import, load
  libraries or hold the standard library;
- a source file whose encoding is not UTF-8, since an encoding cookie can
  turn a comment into code;
- any symlink in the package, and any file Python could import but this
  check cannot read (.so, .pyd, .pyw, upper-case suffixes, a .pyc that is
  not the plain timestamp cache of a source file beside it, and so on).

It never runs mind code, and it looks NumPy's and Numba's modules up in a
separate interpreter, so nothing a module does at import can change its
result.

This is a static check against the forms listed above. It cannot see every
way Python can reach an object by reflection, such as a module found
through a chain of attributes or a string built at run time. Keeping the
minds away from the world's objects at run time is the harness's job
(Week 2).

Usage: python tools/import_guard.py [package_dir ...]   (default: src/mind)
Exits 1 and lists every violation if there is any.
"""

import ast
import json
import os
import pathlib
import re
import subprocess
import sys
import tokenize

ALLOWED_TOP_LEVEL = {"numpy", "numba", "mind"}
ALLOWED_FROM_ONLY = {"__future__"}
FORBIDDEN_NAMES = {"__import__", "importlib", "__builtins__", "builtins", "__path__", "__spec__",
                   "__loader__", "__package__", "__name__", "__file__", "__dict__", "__globals__"}
FORBIDDEN_CALLS = {"exec", "eval", "compile", "globals", "vars", "locals", "getattr", "setattr",
                   "delattr", "help", "breakpoint"}
FORBIDDEN_ATTRIBUTES = FORBIDDEN_NAMES | {
    "modules", "import_module", "meta_path", "path_hooks", "path_importer_cache",
    "__getattribute__", "__class__", "__base__", "__bases__", "__mro__", "__subclasses__", "__code__",
    "__closure__", "__self__", "__func__", "__module__", "__getattr__", "__reduce__", "__reduce_ex__",
    "__traceback__", "f_globals", "f_locals", "f_builtins", "f_back", "gi_frame", "cr_frame", "ag_frame",
    "tb_frame",
}
NUMPY_PARTS_REFUSED = {"tests", "testing", "conftest", "f2py", "ctypeslib", "distutils"}
HARMLESS_DUNDERS = {"__all__", "__doc__", "__version__", "__slots__", "__debug__"}
SOURCE_SUFFIXES = {".py"}
CACHE_FILE = re.compile(r"^(?P<stem>[^.]+)\.(?P<tag>[a-z0-9_-]+)(\.opt-[12])?\.pyc$")


def _numpy_module_refused(module: str) -> bool:
    """Private, test, build and __main__ modules of NumPy and Numba run code, load libraries or hold the standard library."""
    return any(p.startswith("_") or p in NUMPY_PARTS_REFUSED for p in module.split(".")[1:])


def _foreign_names(pairs) -> set:
    """Which (module, name) pairs hand over a module from outside NumPy, Numba and mind.

    Worked out in a separate interpreter with a timeout, so nothing a module
    does when imported can change this guard's own result. A pair that
    cannot be worked out counts as foreign.
    """
    if not pairs:
        return set()
    code = (
        "import importlib, json, sys, types\n"
        "out = []\n"
        "for module, name in json.loads(sys.stdin.read()):\n"
        "    try:\n"
        "        obj = getattr(importlib.import_module(module), name)\n"
        "        bad = isinstance(obj, types.ModuleType) and obj.__name__.split('.')[0] not in ('numpy', 'numba')\n"
        "    except (ImportError, AttributeError):\n"
        "        bad = False\n"
        "    except BaseException:\n"
        "        bad = True\n"
        "    out.append(bad)\n"
        "sys.stdout.write('GUARD-RESULT ' + json.dumps(out))\n"
    )
    pairs = sorted(pairs)
    try:
        r = subprocess.run([sys.executable, "-I", "-c", code], input=json.dumps(pairs),
                           capture_output=True, text=True, timeout=120)
        line = r.stdout.rsplit("GUARD-RESULT ", 1)[1]
        flags = json.loads(line)
        if r.returncode != 0 or len(flags) != len(pairs):
            raise ValueError
    except (subprocess.TimeoutExpired, IndexError, ValueError):
        return set(pairs)
    return {p for p, bad in zip(pairs, flags) if bad}


def _is_dunder(name: str) -> bool:
    """A dunder name other than the harmless few a module may define."""
    return len(name) > 4 and name.startswith("__") and name.endswith("__") and name not in HARMLESS_DUNDERS


def violations(path: pathlib.Path) -> tuple:
    """(violations, the (module, name) pairs imported from NumPy or Numba, with line numbers)."""
    raw = path.read_bytes()
    with path.open("rb") as f:
        encoding = tokenize.detect_encoding(f.readline)[0]
    out, from_numpy = [], []
    if encoding not in ("utf-8", "utf-8-sig"):
        out.append((1, f"a source encoding other than UTF-8 ({encoding})"))
    try:
        tree = ast.parse(raw, filename=str(path))     # bytes, so Python's own encoding rules apply
    except (SyntaxError, ValueError) as e:
        return [(getattr(e, "lineno", 0) or 0, "a file the guard cannot parse")], []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                for n in (alias.name.split(".")[-1], alias.asname or ""):
                    if n in FORBIDDEN_ATTRIBUTES or n in FORBIDDEN_CALLS or _is_dunder(n):
                        out.append((node.lineno, f"importing the name {n}"))
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in ALLOWED_TOP_LEVEL or (top != "mind" and _numpy_module_refused(alias.name)):
                    out.append((node.lineno, f"import {alias.name}"))
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                out.append((node.lineno, "a relative import (use the full name, mind.x)"))
                continue
            top = (node.module or "").split(".")[0]
            if top not in ALLOWED_TOP_LEVEL | ALLOWED_FROM_ONLY:
                out.append((node.lineno, f"from {node.module} import ..."))
            elif top in ("numpy", "numba"):
                if _numpy_module_refused(node.module):
                    out.append((node.lineno, f"from {node.module} import ..."))
                    continue
                for alias in node.names:
                    if alias.name == "*":
                        out.append((node.lineno, f"from {node.module} import *"))
                    else:
                        from_numpy.append((node.lineno, node.module, alias.name))
        elif isinstance(node, ast.Name) and (node.id in FORBIDDEN_NAMES | FORBIDDEN_CALLS or _is_dunder(node.id)):
            out.append((node.lineno, f"use of {node.id}"))
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRIBUTES | NUMPY_PARTS_REFUSED:
            out.append((node.lineno, f"use of .{node.attr}"))
        elif isinstance(node, (ast.arg, ast.keyword)) and node.arg and \
                (node.arg in FORBIDDEN_NAMES | FORBIDDEN_CALLS or _is_dunder(node.arg)):
            out.append((node.lineno, f"binding the name {node.arg}"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and \
                (node.value in FORBIDDEN_ATTRIBUTES or _is_dunder(node.value)):
            out.append((node.lineno, f"the string {node.value!r}, which names a forbidden object"))
    return out, from_numpy


def _walk(root: pathlib.Path):
    """Every file and symlink under root, never following a link."""
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for name in dirnames + filenames:
            yield pathlib.Path(dirpath) / name


def _unreadable(p: pathlib.Path) -> str:
    """Why an importable file is refused, or '' if the guard can read it (or Python cannot import it)."""
    suffix = p.suffix.lower()
    if p.parent.name == "__pycache__":
        m = CACHE_FILE.match(p.name)
        if not m or m.group("tag") != sys.implementation.cache_tag or \
                not (p.parent.parent / (m.group("stem") + ".py")).is_file():
            return "a file in __pycache__ that is not the cache of a source file beside it"
        with p.open("rb") as f:
            header = f.read(8)
        if len(header) < 8 or int.from_bytes(header[4:8], "little") != 0:
            return "a hash-based .pyc, which Python may run instead of its source"
        return ""
    if suffix in SOURCE_SUFFIXES and p.suffix == suffix:
        return ""
    if suffix in {".py", ".pyw", ".pyc", ".pyo", ".so", ".pyd", ".dll", ".dylib", ".pth", ".zip", ".egg", ".whl"}:
        return f"a {p.suffix} file the guard cannot read"
    return ""


def check(dirs) -> list:
    found = []
    for d in dirs:
        root = pathlib.Path(d)
        if root.is_symlink():
            found.append((str(root), 0, "a symlink"))
            continue
        if root.is_dir():
            files = []
            for p in _walk(root):
                if p.is_symlink():
                    found.append((str(p), 0, "a symlink"))
                elif p.is_file():
                    why = _unreadable(p)
                    if why:
                        found.append((str(p), 0, why))
                    elif p.suffix == ".py":
                        files.append(p)
            files.sort()
        else:
            files = [root]
        if not files:
            found.append((str(root), 0, "no Python files found: wrong path?"))
        pending = []
        for path in files:
            out, from_numpy = violations(path)
            found += [(str(path), lineno, what) for lineno, what in out]
            pending += [(str(path), lineno, module, name) for lineno, module, name in from_numpy]
        foreign = _foreign_names({(module, name) for _, _, module, name in pending})
        for path, lineno, module, name in pending:
            if (module, name) in foreign:
                found.append((path, lineno, f"from {module} import {name}, a module from outside NumPy"))
    return found


def main(argv) -> int:
    dirs = argv[1:] or ["src/mind"]
    found = check(dirs)
    for path, lineno, what in found:
        print(f"{path}:{lineno}: I02 forbids {what}")
    if found:
        return 1
    print(f"import guard: {', '.join(dirs)} clean")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
