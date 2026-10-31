"""Write a freeze manifest: the SHA-256 of every file that decides a result (section 7, I04).

    python tools/freeze.py bench OUT       the bench: world, harness, bots, fixtures, tools, the drive grid
    python tools/freeze.py set A OUT       a kill-run set's code freeze (Week 5; names the set)
    python tools/freeze.py verify MANIFEST lists every file that differs from a manifest

A manifest is plain text: a header naming what it freezes and the folders and
files it covers, then one line per file, "sha256  path", in path order.
Verifying reports a file that changed, one that is missing and one added under
a covered folder. This tool never pushes anything and
refuses to overwrite a file. A manifest that lands in freeze/ on main is
stamped by the timestamp Action and that cannot be undone, so it goes there
only by a commit Aitzaz has approved; tests write to temporary folders.
"""

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
BENCH = ("pyproject.toml", "uv.lock", "src/world", "src/harness", "src/baselines", "src/test_fixtures", "tools",
         "tests/data/drive_grid.json", ".github/workflows/power-check.yml")
SET_CODE = BENCH + ("src/mind", "src/twins")
SKIP_PARTS = ("__pycache__", ".pytest_cache", ".hypothesis")
ROOTS_LINE = "# covers: "


def files(roots, root=ROOT) -> list:
    out = []
    for r in roots:
        p = root / r
        if p.is_file():
            out.append(p)
        elif p.is_dir():
            out += [q for q in p.rglob("*") if q.is_file() and not any(s in q.parts for s in SKIP_PARTS)]
        else:
            raise FileNotFoundError(f"{r} is missing")
    return sorted(set(out), key=lambda q: q.relative_to(root).as_posix())


def manifest(name, roots, root=ROOT) -> str:
    import numpy
    lines = [f"# FRANKIE freeze manifest: {name}", f"# Python {sys.version.split()[0]}, NumPy {numpy.__version__}",
             f"{ROOTS_LINE}{' '.join(roots)}", "# sha256  path"]
    for p in files(roots, root):
        lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(root).as_posix()}")
    return "\n".join(lines) + "\n"


def verify(path, root=ROOT) -> list:
    """Every file whose hash differs from the manifest's, that is missing, or that was added under its roots."""
    out = []
    roots = []
    listed = set()
    for line in pathlib.Path(path).read_text().splitlines():
        if line.startswith(ROOTS_LINE):
            roots = line[len(ROOTS_LINE):].split()
        if line.startswith("#") or not line.strip():
            continue
        digest, rel = line.split("  ", 1)
        listed.add(rel)
        p = root / rel
        if not p.is_file():
            out.append(f"missing: {rel}")
        elif hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            out.append(f"changed: {rel}")
    present = files([r for r in roots if (root / r).exists()], root)
    out += [f"added: {rel}" for rel in (p.relative_to(root).as_posix() for p in present) if rel not in listed]
    return out


def write(path, text):
    path = pathlib.Path(path)
    if path.exists():
        raise FileExistsError(f"{path} exists; a manifest is never overwritten")
    path.write_text(text)
    return path


def main(argv) -> int:
    if len(argv) == 3 and argv[1] == "bench":
        write(argv[2], manifest("kill-test bench (bots, B1n-mind, harness, analysis script)", BENCH))
    elif len(argv) == 4 and argv[1] == "set" and argv[2] in ("A", "B", "C"):
        write(argv[3], manifest(f"kill-run set {argv[2]} code (section 3)", SET_CODE))
    elif len(argv) == 3 and argv[1] == "verify":
        diffs = verify(argv[2])
        print("\n".join(diffs) if diffs else "every file matches the manifest")
        return 1 if diffs else 0
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
