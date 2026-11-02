"""Write set A's code manifest for E1 (kill-test/E1_ADDENDUM.md section 8, KILL_TEST.md section 3).

    python kill-test/write_set_a_manifest.py

It calls the frozen tools/freeze.py's own manifest() with the set's code paths
(SET_CODE: the bench, src/mind and src/twins) plus E1's driver, the reader of
N and the addendum, which lie outside SET_CODE. The manifest names set A, so pushing it
to main fixes set A's key: it is written to freeze/ only by a commit Aitzaz
has approved. It never overwrites a file.
"""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import freeze  # noqa: E402

OUT = ROOT / "freeze" / "killtest-code-v1-set-A.sha256"
EXTRA = ("kill-test/e1_kill_run.py", "kill-test/read_set_a_key.py", "kill-test/E1_ADDENDUM.md")
NAME = "kill-run set A code (section 3): E1 under kill-test/E1_ADDENDUM.md"


def main() -> int:
    text = freeze.manifest(NAME, freeze.SET_CODE + EXTRA)
    freeze.write(OUT, text)
    print(f"wrote {OUT.relative_to(ROOT)}: {sum(1 for line in text.splitlines() if not line.startswith('#'))} files")
    diffs = freeze.verify(OUT)
    print("verify:", "every file matches" if not diffs else diffs)
    return 0 if not diffs else 1


if __name__ == "__main__":
    sys.exit(main())
