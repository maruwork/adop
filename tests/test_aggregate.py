"""Cross-project aggregation: a read-only portfolio view across artifact roots."""
from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from adop_cli import main


def _run_capture(*argv: str) -> tuple[int, str]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = main(list(argv))
    return rc, buf.getvalue()


def test_aggregate_spans_multiple_roots(tmp_path):
    a = str(tmp_path / "proj-a")
    b = str(tmp_path / "proj-b")
    assert main(["quick-intake", "--artifact-root", a, "--candidate", "ruff", "--source", "doc",
                 "--use-case", "lint", "--why-now", "x"]) == 0
    assert main(["watch", "--artifact-root", b, "--candidate", "vale",
                 "--interest-reason", "r", "--use-case", "docs"]) == 0
    rc, out = _run_capture("aggregate", "--root", a, "--root", b, "--json")
    assert rc == 0
    payload = json.loads(out)
    rows = payload["portfolio"]
    by_scene = {(Path(r["root"]).name, r["scene"]): r for r in rows}
    assert ("proj-a", "lint") in by_scene
    assert by_scene[("proj-a", "lint")]["state"] == "proposed"
    assert by_scene[("proj-a", "lint")]["tool"] == "ruff"
    assert ("proj-b", "docs") in by_scene
    assert by_scene[("proj-b", "docs")]["state"] == "watch"


def test_aggregate_missing_root_is_flagged(tmp_path):
    rc, out = _run_capture("aggregate", "--root", str(tmp_path / "nope"), "--json")
    assert rc == 0
    assert json.loads(out)["portfolio"][0]["state"] == "MISSING_ROOT"


def test_aggregate_text_output_groups_by_root(tmp_path):
    a = str(tmp_path / "p")
    assert main(["quick-intake", "--artifact-root", a, "--candidate", "ruff", "--source", "doc",
                 "--use-case", "lint", "--why-now", "x"]) == 0
    rc, out = _run_capture("aggregate", "--root", a)
    assert rc == 0
    assert "ADOP Portfolio" in out
    assert "lint: proposed (ruff)" in out
