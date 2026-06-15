"""Tests for usability commands: init, status, scan, next, and default artifact root."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parent.parent / "shared" / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

from adop_cli import main


def run(*argv: str) -> int:
    return main(list(argv))


# ── init ─────────────────────────────────────────────────────────────────────

def test_init_creates_artifact_root(tmp_path):
    root = str(tmp_path / ".adop")
    overlay = str(tmp_path / "adop-overlay.md")
    rc = run("init", "--artifact-root", root, "--overlay", overlay)
    assert rc == 0
    assert Path(root).is_dir()


def test_init_creates_overlay_file(tmp_path):
    root = str(tmp_path / ".adop")
    overlay = str(tmp_path / "adop-overlay.md")
    run("init", "--artifact-root", root, "--overlay", overlay)
    assert Path(overlay).exists()
    text = Path(overlay).read_text(encoding="utf-8")
    assert "ADOP" in text


def test_init_idempotent(tmp_path):
    root = str(tmp_path / ".adop")
    overlay = str(tmp_path / "adop-overlay.md")
    assert run("init", "--artifact-root", root, "--overlay", overlay) == 0
    # second run must not overwrite an existing overlay
    Path(overlay).write_text("custom content", encoding="utf-8")
    assert run("init", "--artifact-root", root, "--overlay", overlay) == 0
    assert Path(overlay).read_text(encoding="utf-8") == "custom content"


def test_init_output_mentions_next_steps(tmp_path, capsys):
    root = str(tmp_path / ".adop")
    overlay = str(tmp_path / "adop-overlay.md")
    run("init", "--artifact-root", root, "--overlay", overlay)
    out = capsys.readouterr().out
    assert "Next steps" in out
    assert "adop status" in out


# ── default artifact root ────────────────────────────────────────────────────

def test_default_artifact_root_missing_shows_hint(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    rc = run("status")
    assert rc == 2
    out = capsys.readouterr().out
    assert "adop init" in out


def test_default_artifact_root_used_when_exists(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    adop_dir = tmp_path / ".adop"
    adop_dir.mkdir()
    rc = run("status")
    assert rc == 0


# ── status ────────────────────────────────────────────────────────────────────

def test_status_empty(tmp_path, capsys):
    root = str(tmp_path / ".adop")
    Path(root).mkdir()
    rc = run("status", "--artifact-root", root)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No adoption records" in out


def test_status_with_records(tmp_path, capsys):
    root = str(tmp_path / ".adop")
    assert run(
        "quick-intake", "--artifact-root", root,
        "--candidate", "ruff", "--source", "doc",
        "--use-case", "lint", "--why-now", "evaluate",
    ) == 0
    rc = run("status", "--artifact-root", root)
    assert rc == 0
    out = capsys.readouterr().out
    assert "lint" in out
    assert "proposed" in out


def test_status_shows_next_steps(tmp_path, capsys):
    root = str(tmp_path / ".adop")
    run(
        "quick-intake", "--artifact-root", root,
        "--candidate", "ruff", "--source", "doc",
        "--use-case", "lint", "--why-now", "evaluate",
    )
    run("status", "--artifact-root", root)
    out = capsys.readouterr().out
    assert "Next steps" in out


# ── scan ──────────────────────────────────────────────────────────────────────

def test_scan_detects_python_import(tmp_path, capsys):
    src = tmp_path / "app.py"
    src.write_text("import ruff\nfrom ruff import check\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert "app.py" in out
    assert "import" in out


def test_scan_detects_config_reference(tmp_path, capsys):
    cfg = tmp_path / "pyproject.toml"
    cfg.write_text("[tool.ruff]\nline-length = 88\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert "pyproject.toml" in out
    assert "config" in out


def test_scan_detects_requirements(tmp_path, capsys):
    req = tmp_path / "requirements.txt"
    req.write_text("ruff>=0.1\npytest\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert "requirements.txt" in out


def test_scan_no_results(tmp_path, capsys):
    (tmp_path / "app.py").write_text("print('hello')\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert "No references" in out


def test_scan_json_output(tmp_path, capsys):
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff", "--json")
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, list)
    assert data[0]["coupling_type"] == "config"


def test_scan_invalid_target(tmp_path):
    rc = run("scan", "--target", str(tmp_path / "nonexistent"), "--tool", "ruff")
    assert rc == 2


# ── next ──────────────────────────────────────────────────────────────────────

def test_next_no_records(tmp_path, capsys):
    root = str(tmp_path / ".adop")
    Path(root).mkdir()
    rc = run("next", "--artifact-root", root)
    assert rc == 0
    out = capsys.readouterr().out
    assert "No records" in out


def test_next_proposed(tmp_path, capsys):
    root = str(tmp_path / ".adop")
    run(
        "quick-intake", "--artifact-root", root,
        "--candidate", "ruff", "--source", "doc",
        "--use-case", "lint", "--why-now", "evaluate",
    )
    rc = run("next", "--artifact-root", root)
    assert rc == 0
    out = capsys.readouterr().out
    assert "quick-compare" in out


def test_next_in_trial(tmp_path, capsys):
    root = str(tmp_path / ".adop")
    run(
        "quick-intake", "--artifact-root", root,
        "--candidate", "ruff", "--source", "doc",
        "--use-case", "lint", "--why-now", "evaluate",
    )
    run(
        "quick-compare", "--artifact-root", root, "--use-case", "lint",
        "--candidate", "ruff", "--candidate", "flake8", "--selected", "ruff",
    )
    run(
        "quick-trial", "--artifact-root", root, "--use-case", "lint",
        "--mode", "read-only-comparison", "--executor", "ci",
    )
    rc = run("next", "--artifact-root", root)
    assert rc == 0
    out = capsys.readouterr().out
    assert "quick-close-trial" in out
