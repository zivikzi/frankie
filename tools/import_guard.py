"""The import guard (LEDGER I02, KT-89).

The build fails if any module of the mind package imports anything but NumPy
and Numba, or imports from baselines, test fixtures, the world or the
harness. Read strictly: the standard library is not allowed either, except
`from __future__ import ...`, which changes no behaviour at run time. Imports
inside the mind package itself (`mind.x`, or relative imports) are allowed.

Dynamic imports (`__import__`, `importlib`, `exec`, `eval`, `compile`) are
refused outright, so no import can hide from this check.

Usage: python tools/import_guard.py [package_dir ...]   (default: src/mind)
Exits 1 and lists every violation if there is any.
"""

import ast
import pathlib
import sys

ALLOWED_TOP_LEVEL = {"numpy", "numba", "mind", "__future__"}
FORBIDDEN_CALLS = {"__import__", "exec", "eval", "compile"}


def violations(path: pathlib.Path, depth: int = 1) -> list:
    """depth: how many package levels the file sits below src (1 for mind/x.py).

    A relative import may climb at most that many levels, so it stays inside
    the mind package.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in ALLOWED_TOP_LEVEL:
                    out.append((node.lineno, f"import {alias.name}"))
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                if node.level > depth:
                    out.append((node.lineno, "a relative import that leaves the package"))
                continue
            top = (node.module or "").split(".")[0]
            if top not in ALLOWED_TOP_LEVEL:
                out.append((node.lineno, f"from {node.module} import ..."))
        elif isinstance(node, ast.Call):
            f = node.func
            name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if name in FORBIDDEN_CALLS:
                out.append((node.lineno, f"call to {name}()"))
        elif isinstance(node, ast.Name) and node.id == "importlib":
            out.append((node.lineno, "use of importlib"))
    return out


def check(dirs) -> list:
    found = []
    for d in dirs:
        root = pathlib.Path(d)
        files = sorted(root.rglob("*.py")) if root.is_dir() else [root]
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
