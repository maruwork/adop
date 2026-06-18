"""Tests for usability commands: init, status, scan, next, and default artifact root."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PYTHON_DIR = Path(__file__).resolve().parent.parent / "shared" / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import adop_cli
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


def test_init_overlay_matches_scene_lane_contract(tmp_path):
    root = str(tmp_path / ".adop")
    overlay = str(tmp_path / "adop-overlay.md")
    run("init", "--artifact-root", root, "--overlay", overlay)
    text = Path(overlay).read_text(encoding="utf-8")
    assert "## Active Scene Lanes" in text
    assert "| Scene Lane | Tool | Current State | Last Activity |" in text
    assert "## Current Judgment Memo" in text
    assert "## Approved Use Scenes" in text
    assert "## Prohibited Use Scenes" in text
    assert "## Landing Target Authority" in text
    assert "## Pending Project Decisions" in text
    assert "## Open Items" not in text


def test_init_fallback_overlay_still_matches_contract(tmp_path, monkeypatch):
    root = str(tmp_path / ".adop")
    overlay = str(tmp_path / "adop-overlay.md")
    missing_layout = tmp_path / "missing-layout" / "shared" / "python" / "adop_cli.py"
    missing_layout.parent.mkdir(parents=True, exist_ok=True)
    missing_layout.write_text("# placeholder\n", encoding="utf-8")
    monkeypatch.setattr(adop_cli, "__file__", str(missing_layout))
    run("init", "--artifact-root", root, "--overlay", overlay)
    text = Path(overlay).read_text(encoding="utf-8")
    assert "## Active Scene Lanes" in text
    assert "## Current Judgment Memo" in text
    assert "## Approved Use Scenes" in text
    assert "## Prohibited Use Scenes" in text
    assert "## Landing Target Authority" in text
    assert "## Pending Project Decisions" in text


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


def test_scene_alias_is_accepted_on_guided_commands(tmp_path, capsys):
    root = str(tmp_path / ".adop")
    assert run(
        "quick-intake", "--artifact-root", root,
        "--candidate", "ruff", "--source", "doc",
        "--scene", "lint", "--why-now", "evaluate",
    ) == 0
    rc = run("next", "--artifact-root", root)
    assert rc == 0
    out = capsys.readouterr().out
    assert "--scene lint" in out
    assert run(
        "quick-compare", "--artifact-root", root,
        "--scene", "lint", "--candidate", "ruff", "--candidate", "flake8", "--selected", "ruff",
    ) == 0
    assert run(
        "quick-trial", "--artifact-root", root,
        "--scene", "lint", "--mode", "read-only-comparison", "--executor", "ci",
        "--decision-owner", "lead", "--landing-target", "ci/lint",
    ) == 0


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


def test_scan_detects_hidden_config_and_workflow_paths(tmp_path, capsys):
    (tmp_path / ".pre-commit-config.yaml").write_text("repos:\n  - repo: local\n", encoding="utf-8")
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("name: CI\nsteps:\n  - run: python -m ruff check .\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert ".github/workflows/ci.yml" in out


def test_scan_detects_precommit_hook_entry_as_high_confidence(tmp_path, capsys):
    config = tmp_path / ".pre-commit-config.yaml"
    config.write_text(
        "repos:\n  - repo: local\n    hooks:\n      - id: ruff-check\n        entry: python -m ruff check\n",
        encoding="utf-8",
    )
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".pre-commit-config.yaml"
    assert data[0]["coupling_type"] == "invocation"
    assert data[0]["detection_source"] == "config-mention"
    assert data[0]["confidence"] == "high"


def test_scan_detects_prettier_surface_filename_without_tool_name(tmp_path, capsys):
    (tmp_path / ".prettierrc.json").write_text('{"semi": false}\n', encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "prettier")
    assert rc == 0
    out = capsys.readouterr().out
    assert ".prettierrc.json" in out
    assert "high confidence via surface-rule" in out


def test_scan_matches_pre_commit_underscore_invocation(tmp_path, capsys):
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - run: python -m pre_commit run --all-files\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "pre-commit")
    assert rc == 0
    out = capsys.readouterr().out
    assert ".github/workflows/ci.yml" in out


def test_scan_detects_workflow_action_usage_as_high_confidence(tmp_path, capsys):
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - uses: rhysd/actionlint@v1\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "actionlint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".github/workflows/ci.yml"
    assert data[0]["coupling_type"] == "invocation"
    assert data[0]["detection_source"] == "invocation-pattern"
    assert data[0]["confidence"] == "high"


def test_scan_detects_workflow_npm_script_indirection_as_high_confidence(tmp_path, capsys):
    package = tmp_path / "package.json"
    package.write_text(
        '{\n  "scripts": {\n    "lint:js": "eslint eslint.config.js"\n  }\n}\n',
        encoding="utf-8",
    )
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - run: npm run lint:js\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "eslint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert any(entry["path"] == ".github/workflows/ci.yml" for entry in data)
    workflow_entry = next(entry for entry in data if entry["path"] == ".github/workflows/ci.yml")
    assert workflow_entry["coupling_type"] == "invocation"
    assert workflow_entry["detection_source"] == "invocation-pattern"
    assert workflow_entry["confidence"] == "high"


def test_scan_ignores_check_renovate_hook_name(tmp_path, capsys):
    config = tmp_path / ".pre-commit-config.yaml"
    config.write_text(
        "repos:\n  - repo: https://github.com/python-jsonschema/check-jsonschema\n    hooks:\n      - id: check-renovate\n",
        encoding="utf-8",
    )
    rc = run("scan", "--target", str(tmp_path), "--tool", "renovate")
    assert rc == 0
    out = capsys.readouterr().out
    assert "No references" in out


def test_scan_ignores_evaluation_only_candidate_mentions(tmp_path, capsys):
    manifest = tmp_path / "audit.manifest.yml"
    manifest.write_text(
        'commands:\n'
        '  - id: quick-intake\n'
        '    run: python shared/python/adop_cli.py quick-intake --candidate ruff --source doc --use-case lint-pipeline --why-now "audit manifest smoke"\n',
        encoding="utf-8",
    )
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert "No references" in out


def test_scan_detects_vscode_eslint_settings_without_tool_id(tmp_path, capsys):
    settings = tmp_path / ".vscode" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(
        '{\n  "eslint.validate": ["javascript"],\n  "editor.codeActionsOnSave": {"source.fixAll.eslint": "explicit"}\n}\n',
        encoding="utf-8",
    )
    rc = run("scan", "--target", str(tmp_path), "--tool", "vscode-eslint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".vscode/settings.json"
    assert data[0]["coupling_type"] == "config"
    assert data[0]["detection_source"] == "surface-rule"
    assert data[0]["confidence"] == "high"


def test_scan_detects_eslint_editor_surface_as_config(tmp_path, capsys):
    settings = tmp_path / ".vscode" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text('{\n  "eslint.validate": ["javascript"]\n}\n', encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "eslint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".vscode/settings.json"
    assert data[0]["coupling_type"] == "config"
    assert data[0]["detection_source"] == "surface-rule"
    assert data[0]["confidence"] == "high"


def test_scan_detects_package_json_dependency_as_high_confidence(tmp_path, capsys):
    package = tmp_path / "package.json"
    package.write_text(
        '{\n  "devDependencies": {\n    "eslint": "^9.0.0"\n  }\n}\n',
        encoding="utf-8",
    )
    rc = run("scan", "--target", str(tmp_path), "--tool", "eslint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == "package.json"
    assert data[0]["detection_source"] == "config-mention"
    assert data[0]["confidence"] == "high"


def test_scan_detects_package_json_script_as_invocation(tmp_path, capsys):
    package = tmp_path / "package.json"
    package.write_text(
        '{\n  "scripts": {\n    "lint:js": "eslint eslint.config.js"\n  }\n}\n',
        encoding="utf-8",
    )
    rc = run("scan", "--target", str(tmp_path), "--tool", "eslint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == "package.json"
    assert data[0]["coupling_type"] == "invocation"
    assert data[0]["detection_source"] == "invocation-pattern"
    assert data[0]["confidence"] == "high"


def test_scan_detects_makefile_command_as_invocation(tmp_path, capsys):
    makefile = tmp_path / "Makefile"
    makefile.write_text(
        "lint:\n\truff check .\n",
        encoding="utf-8",
    )
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == "Makefile"
    assert data[0]["coupling_type"] == "invocation"
    assert data[0]["detection_source"] == "invocation-pattern"
    assert data[0]["confidence"] == "high"


def test_scan_keeps_operational_tool_mentions_even_with_eval_lines(tmp_path, capsys):
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text(
        "steps:\n"
        "  - run: adop quick-intake --candidate ruff --source doc --use-case lint\n"
        "  - run: python -m ruff check .\n",
        encoding="utf-8",
    )
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert ".github/workflows/ci.yml" in out


def test_scan_detects_pytest_xdist_invocation_pattern(tmp_path, capsys):
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - run: python -m pytest tests -q -n auto\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "pytest-xdist", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".github/workflows/ci.yml"
    assert data[0]["coupling_type"] == "invocation"
    assert data[0]["detection_source"] == "invocation-pattern"


def test_scan_exclude_skips_selected_paths(tmp_path, capsys):
    kept = tmp_path / "src" / "pyproject.toml"
    kept.parent.mkdir(parents=True, exist_ok=True)
    kept.write_text("[tool.ruff]\n", encoding="utf-8")
    skipped = tmp_path / "workspace" / "pyproject.toml"
    skipped.parent.mkdir(parents=True, exist_ok=True)
    skipped.write_text("[tool.ruff]\n", encoding="utf-8")
    rc = run(
        "scan", "--target", str(tmp_path), "--tool", "ruff",
        "--exclude", "workspace",
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "src/pyproject.toml" in out
    assert "workspace/pyproject.toml" not in out
    assert "Excluded paths: workspace" in out


def test_scan_skips_build_directory_by_default(tmp_path, capsys):
    kept = tmp_path / "src" / "pyproject.toml"
    kept.parent.mkdir(parents=True, exist_ok=True)
    kept.write_text("[tool.ruff]\n", encoding="utf-8")
    skipped = tmp_path / "build" / "pyproject.toml"
    skipped.parent.mkdir(parents=True, exist_ok=True)
    skipped.write_text("[tool.ruff]\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert "src/pyproject.toml" in out
    assert "build/pyproject.toml" not in out


def test_scan_skips_egg_info_directory_by_default(tmp_path, capsys):
    kept = tmp_path / "src" / "pyproject.toml"
    kept.parent.mkdir(parents=True, exist_ok=True)
    kept.write_text("[tool.ruff]\n", encoding="utf-8")
    skipped = tmp_path / "pkg.egg-info" / "PKG-INFO"
    skipped.parent.mkdir(parents=True, exist_ok=True)
    skipped.write_text("ruff mentioned in package metadata\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert "src/pyproject.toml" in out
    assert "pkg.egg-info/PKG-INFO" not in out


def test_scan_no_results(tmp_path, capsys):
    (tmp_path / "app.py").write_text("print('hello')\n", encoding="utf-8")
    (tmp_path / "notes.md").write_text("ruff is mentioned in docs only\n", encoding="utf-8")
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
    assert data[0]["detection_source"] == "config-mention"
    assert data[0]["confidence"] == "high"


def test_scan_detects_hadolint_inline_directive_in_dockerfile(tmp_path, capsys):
    dockerfile = tmp_path / "Dockerfile"
    dockerfile.write_text("# hadolint global ignore=DL3008\nFROM alpine:3.20\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "hadolint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == "Dockerfile"
    assert data[0]["coupling_type"] == "config"
    assert data[0]["detection_source"] == "surface-rule"
    assert data[0]["confidence"] == "high"


def test_scan_detects_shellcheck_inline_directive_in_script(tmp_path, capsys):
    script = tmp_path / "repo-smoke.sh"
    script.write_text("#!/usr/bin/env bash\n# shellcheck shell=bash\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "shellcheck", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == "repo-smoke.sh"
    assert data[0]["coupling_type"] == "config"
    assert data[0]["detection_source"] == "config-mention"
    assert data[0]["confidence"] == "high"


def test_scan_record_writes_canonical_coupling_note(tmp_path, capsys):
    root = str(tmp_path / ".adop")
    Path(root).mkdir()
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
    rc = run(
        "scan", "--artifact-root", root,
        "--target", str(tmp_path), "--tool", "ruff",
        "--scene", "lint", "--record",
    )
    assert rc == 0
    out = capsys.readouterr().out
    assert "Recorded coupling snapshot: adop_coupling-note_cp-001.json" in out
    assert run("couplings", "--artifact-root", root) == 0
    report = capsys.readouterr().out
    assert "ruff @ lint" in report
    assert "pyproject.toml" in report


def test_scan_record_requires_scene(tmp_path):
    root = str(tmp_path / ".adop")
    Path(root).mkdir()
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
    rc = run("scan", "--artifact-root", root, "--target", str(tmp_path), "--tool", "ruff", "--record")
    assert rc == 2


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
        "--decision-owner", "lead", "--landing-target", "ci/lint",
    )
    rc = run("next", "--artifact-root", root)
    assert rc == 0
    out = capsys.readouterr().out
    assert "quick-close-trial" in out


def test_next_after_hold_resume_returns_quick_trial(tmp_path, capsys):
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
        "--decision-owner", "lead", "--landing-target", "ci/lint",
    )
    run(
        "quick-close-trial", "--artifact-root", root,
        "--trial-id", "tr-001", "--verdict", "hold",
        "--observed-effect", "needs narrowing",
    )
    run(
        "quick-compare", "--artifact-root", root, "--use-case", "lint",
        "--candidate", "ruff", "--candidate", "flake8", "--selected", "ruff",
    )
    rc = run("next", "--artifact-root", root)
    assert rc == 0
    out = capsys.readouterr().out
    assert "quick-trial" in out
