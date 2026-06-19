"""Error-path tests for artifact-root preparation.

A JSON-native CLI must never leak a raw traceback. These pin the two distinct
failure modes to their documented exit codes:
  - unwritable / uncreatable root -> 11 (artifact IO error)
  - root overlapping the target project -> 14 (boundary violation)
"""

from __future__ import annotations

from pathlib import Path


def test_uncreatable_root_returns_io_error_not_traceback(run, root, capsys):
    """A root whose parent is a file cannot be created; expect a clean exit 11."""
    parent_file = Path(root) / "afile"
    parent_file.write_text("x", encoding="utf-8")
    bad_root = str(parent_file / "sub")  # mkdir under a file -> OSError

    code = run("watch", "--artifact-root", bad_root,
               "--candidate", "ruff", "--interest-reason", "speed")

    assert code == 11
    out = capsys.readouterr().out
    assert '"status": "error"' in out
    assert "Traceback" not in out


def test_boundary_violation_returns_14(run, root, capsys):
    """An artifact root inside the target project is rejected with exit 14."""
    project = Path(root) / "proj"
    project.mkdir()
    inside = str(project / "artifacts")

    code = run(
        "quick-intake", "--artifact-root", inside,
        "--target-project-root", str(project),
        "--candidate", "x", "--source", "doc", "--use-case", "u", "--why-now", "w",
    )

    assert code == 14
    assert "Traceback" not in capsys.readouterr().out


def test_lint_on_missing_root_exits_10(run, tmp_path, capsys):
    """lint on a non-existent artifact root must fail, not silently pass."""
    missing = str(tmp_path / "does_not_exist")
    code = run("lint", "--artifact-root", missing)
    assert code == 10
    out = capsys.readouterr().out
    assert "does not exist" in out


def test_lint_on_empty_root_exits_10(run, tmp_path, capsys):
    """lint on an empty artifact root (no artifacts) must fail."""
    empty = tmp_path / "empty_root"
    empty.mkdir()
    code = run("lint", "--artifact-root", str(empty))
    assert code == 10
    out = capsys.readouterr().out
    assert "empty" in out


def _watch_payload(artifact_id: str) -> dict:
    return {
        "schema_version": 1, "artifact_type": "watch-note", "artifact_id": artifact_id,
        "status": "active", "created_at": "2026-01-01", "candidate_or_tool": "x",
        "interest_reason": "y",
    }


def test_stale_lock_is_reclaimed(tmp_path):
    import os
    import time as _t

    import adop_artifacts as A
    A.ensure_artifact_root(tmp_path)
    name = A.artifact_filename("watch-note", "wt-001")
    lock = tmp_path / f".{name}.lock"
    lock.write_text("")
    old = _t.time() - 120  # far older than the stale threshold
    os.utime(lock, (old, old))
    path = A.write_artifact(tmp_path, "watch-note", "wt-001", _watch_payload("wt-001"))
    assert path.exists()
    assert not lock.exists()  # reclaimed and cleaned up


def test_fresh_lock_blocks(tmp_path):
    import adop_artifacts as A
    import pytest
    A.ensure_artifact_root(tmp_path)
    name = A.artifact_filename("watch-note", "wt-002")
    lock = tmp_path / f".{name}.lock"
    lock.write_text("")  # fresh lock (current mtime)
    with pytest.raises(A.AdopArtifactError):
        A.write_artifact(tmp_path, "watch-note", "wt-002", _watch_payload("wt-002"))


def test_concurrent_id_minting_no_duplicates(tmp_path):
    """Many writers minting sequential ids under contention must not collide."""
    from concurrent.futures import ThreadPoolExecutor

    import adop_artifacts as A
    A.ensure_artifact_root(tmp_path)

    def mint(_n):
        def factory(artifact_id):
            return {
                "schema_version": 1, "artifact_type": "watch-note", "artifact_id": artifact_id,
                "status": "active", "created_at": "2026-01-01", "candidate_or_tool": "x",
                "interest_reason": "y",
            }
        artifact_id, _path = A.write_next_sequential_artifact(tmp_path, "watch-note", "wt", factory)
        return artifact_id

    workers = 12
    with ThreadPoolExecutor(max_workers=workers) as ex:
        ids = list(ex.map(mint, range(workers)))

    assert len(ids) == workers
    assert len(set(ids)) == workers, f"duplicate ids minted: {sorted(ids)}"
    written = sorted(p.name for p in tmp_path.glob("adop_watch-note_*.json"))
    assert len(written) == workers
