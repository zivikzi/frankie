"""The import guard (LEDGER I02, KT-89).

The build fails if any module of the mind package imports anything but NumPy
and Numba, or imports from baselines, test fixtures, the world or the
harness. Read strictly: the standard library is not allowed either, except
`from __future__ import ...`, which changes no behaviour at run time. Imports
inside the mind package itself (`mind.x`, or relative imports that stay
inside it) are allowed.

It also refuses what would let an import hide from this check:

- dynamic imports: any use of `__import__`, `importlib`, `exec`, `eval` or
  `compile`, called or not;
- names that reach the import machinery or loaded modules: `__builtins__`,
  `builtins`, `__path__`, `__spec__`, `__loader__`, and the attribute
  `modules` (as in `sys.modules`);
- a name imported from NumPy or Numba that is itself a module from outside
  them (NumPy modules hold `sys` and `os`, for example);
- a source file whose encoding is not UTF-8, since an encoding cookie can
  turn a comment into code;
- any file in the package that Python could import but this check cannot
  read (.so, .pyd, .pyc outside __pycache__, .pth, .zip, .egg).

This is a static check of the source. Keeping the minds away from the world's
objects at run time is the harness's job (Week 2).

Usage: python tools/import_guard.py [package_dir ...]   (default: src/mind)
Exits 1 and lists every violation if there is any.
"""

import ast
import importlib
import pathlib
import sys
import tokenize
import types

ALLOWED_TOP_LEVEL = {"numpy", "numba", "mind"}
ALLOWED_FROM_ONLY = {"__future__"}
FORBIDDEN_NAMES = {"__import__", "importlib", "exec", "eval", "compile", "__builtins__", "builtins",
                   "__path__", "__spec__", "__loader__"}
FORBIDDEN_ATTRIBUTES = FORBIDDEN_NAMES | {"modules", "import_module"}
UNREADABLE_SUFFIXES = {".so", ".pyd", ".pyc", ".pyo", ".pth", ".zip", ".egg", ".whl"}


def _foreign_module(module: str, name: str) -> bool:
    """True if `from module import name` would hand over a module from outside NumPy, Numba and mind."""
    try:
        obj = getattr(importlib.import_module(module), name)
    except (ImportError, AttributeError):
        return False                 # nothing to hand over; a broken import fails on its own
    return isinstance(obj, types.ModuleType) and obj.__name__.split(".")[0] not in ALLOWED_TOP_LEVEL


def violations(path: pathlib.Path, depth: int = 1) -> list:
    """depth: how many package levels the file sits below src (1 for mind/x.py).

    A relative import may climb at most that many levels, so it stays inside
    the mind package.
    """
    raw = path.read_bytes()
    with path.open("rb") as f:
        encoding = tokenize.detect_encoding(f.readline)[0]
    out = []
    if encoding not in ("utf-8", "utf-8-sig"):
        out.append((1, f"a source encoding other than UTF-8 ({encoding})"))
    tree = ast.parse(raw, filename=str(path))     # bytes, so Python's own encoding rules apply
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] not in ALLOWED_TOP_LEVEL:
                    out.append((node.lineno, f"import {alias.name}"))
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                if node.level > depth:
                    out.append((node.lineno, "a relative import that leaves the package"))
                continue
            top = (node.module or "").split(".")[0]
            if top not in ALLOWED_TOP_LEVEL | ALLOWED_FROM_ONLY:
                out.append((node.lineno, f"from {node.module} import ..."))
            elif top in ("numpy", "numba"):
                for alias in node.names:
                    if alias.name == "*" or _foreign_module(node.module, alias.name):
                        out.append((node.lineno, f"from {node.module} import {alias.name}"))
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
            out.append((node.lineno, f"use of {node.id}"))
        elif isinstance(node, ast.Attribute) and node.attr in FORBIDDEN_ATTRIBUTES:
            out.append((node.lineno, f"use of .{node.attr}"))
    return out


def check(dirs) -> list:
    found = []
    for d in dirs:
        root = pathlib.Path(d)
        if root.is_dir():
            files = sorted(root.rglob("*.py"))
            for p in sorted(root.rglob("*")):
                if p.is_file() and p.suffix in UNREADABLE_SUFFIXES and "__pycache__" not in p.parts:
                    found.append((str(p), 0, f"a {p.suffix} file the guard cannot read"))
        else:
            files = [root]
        if not files:
            found.append((str(root), 0, "no Python files found: wrong path?"))
        for path in files:
            depth = len(path.relative_to(root).parts) if root.is_dir() else 1
            for lineno, what in violations(path, depth):
                found.append((str(path), lineno, what))
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
