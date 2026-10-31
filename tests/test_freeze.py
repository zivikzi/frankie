"""The freeze tool (section 7, I04). Manifests are written to temporary folders only."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import freeze  # noqa: E402


def test_a_bench_manifest_lists_every_bench_file_and_verifies(tmp_path):
    text = freeze.manifest("test", freeze.BENCH)
    paths = [line.split("  ", 1)[1] for line in text.splitlines() if not line.startswith("#")]
    assert "src/baselines/bots.py" in paths and "src/harness/judge.py" in paths
    assert "tests/data/drive_grid.json" in paths and "src/test_fixtures/mk10.py" in paths
    assert not any("__pycache__" in p for p in paths) and paths == sorted(paths)
    out = freeze.write(tmp_path / "bench.sha256", text)
    assert freeze.verify(out) == []


def test_verify_finds_a_changed_file(tmp_path):
    (tmp_path / "a.py").write_text("x = 1\n")
    m = freeze.write(tmp_path / "m.sha256", freeze.manifest("t", ["a.py"], root=tmp_path))
    (tmp_path / "a.py").write_text("x = 2\n")
    assert freeze.verify(m, root=tmp_path) == ["changed: a.py"]
    (tmp_path / "a.py").unlink()
    assert freeze.verify(m, root=tmp_path) == ["missing: a.py"]


def test_a_manifest_is_never_overwritten(tmp_path):
    p = freeze.write(tmp_path / "m.sha256", "x\n")
    with pytest.raises(FileExistsError):
        freeze.write(p, "y\n")


def test_verify_finds_a_file_added_under_a_frozen_folder(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "a.py").write_text("x = 1\n")
    m = freeze.write(tmp_path / "m.sha256", freeze.manifest("t", ["pkg"], root=tmp_path))
    assert freeze.verify(m, root=tmp_path) == []
    (tmp_path / "pkg" / "b.py").write_text("y = 1\n")
    assert freeze.verify(m, root=tmp_path) == ["added: pkg/b.py"]
