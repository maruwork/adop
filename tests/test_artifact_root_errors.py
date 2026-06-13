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
