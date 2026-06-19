"""Tests for usability commands: init, status, scan, next, and default artifact root."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PYTHON_DIR = Path(__file__).resolve().parent.parent / "shared" / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))

import adop_cli
from adop_cli import main
from adop_validation import validate_coupling_note_payload


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


def test_init_accepts_custom_artifact_root_and_overlay_paths(tmp_path):
    root = str(tmp_path / "records" / "adop-store")
    overlay_dir = tmp_path / "notes"
    overlay_dir.mkdir()
    overlay = str(overlay_dir / "adop-local.md")
    rc = run("init", "--artifact-root", root, "--overlay", overlay)
    assert rc == 0
    assert Path(root).is_dir()
    assert Path(overlay).exists()


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


def test_repo_overlay_does_not_reference_removed_example_surfaces():
    overlay = Path(__file__).resolve().parent.parent / "adop-overlay.md"
    text = overlay.read_text(encoding="utf-8")
    forbidden = (
        "tool-surfaces/package.json",
        ".github/workflows/tool-surface-examples.yml",
        "tool-surfaces/scripts/repo-smoke.sh",
        "tool-surfaces/.trivyignore",
        "tool-surfaces/renovate.json",
        "tool-surfaces/Dockerfile.tooling-example",
        "tool-surfaces/.markdownlint-cli2.jsonc",
        "tool-surfaces/.vscode/extensions.json",
        "tool-surfaces/.vscode/settings.json",
    )
    for needle in forbidden:
        assert needle not in text


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

def test_supported_scan_tool_catalog_matches_documented_tool_universe():
    assert adop_cli._CANONICAL_TOOL_IDS == frozenset({
        "actionlint",
        "dependabot",
        "eslint",
        "hadolint",
        "markdownlint-cli2",
        "pre-commit",
        "prettier",
        "pytest-xdist",
        "renovate",
        "ruff",
        "shellcheck",
        "trivy",
        "vscode-eslint",
    })
    assert adop_cli._SCAN_TOOL_SUPPORT["ruff"]["support_level"] == "structured-parser-only"
    assert adop_cli._SCAN_TOOL_SUPPORT["pytest-xdist"]["support_level"] == "structured-parser-only"


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


def test_scan_detects_markdownlint_surface_filename_without_tool_name(tmp_path, capsys):
    (tmp_path / ".markdownlint-cli2.jsonc").write_text('{"globs":["README.md"]}\n', encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "markdownlint-cli2", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".markdownlint-cli2.jsonc"
    assert data[0]["coupling_type"] == "config"
    assert data[0]["detection_source"] == "surface-rule"
    assert data[0]["confidence"] == "high"


def test_scan_matches_pre_commit_underscore_invocation(tmp_path, capsys):
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - run: python -m pre_commit run --all-files\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "pre-commit")
    assert rc == 0
    out = capsys.readouterr().out
    assert ".github/workflows/ci.yml" in out


def test_scan_matches_pre_commit_alias_on_surface_rule(tmp_path, capsys):
    config = tmp_path / ".pre-commit-config.yaml"
    config.write_text("repos:\n  - repo: local\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "pre_commit", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".pre-commit-config.yaml"
    assert data[0]["coupling_type"] == "config"
    assert data[0]["detection_source"] == "surface-rule"
    assert data[0]["confidence"] == "high"


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


def test_scan_detects_prefixed_workflow_npm_script_indirection(tmp_path, capsys):
    package = tmp_path / "tool-surfaces" / "package.json"
    package.parent.mkdir(parents=True, exist_ok=True)
    package.write_text(
        '{\n  "scripts": {\n    "lint:js": "eslint eslint.config.js"\n  }\n}\n',
        encoding="utf-8",
    )
    workflow = tmp_path / "tool-surfaces" / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - run: npm run lint:js\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "eslint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    workflow_entry = next(entry for entry in data if entry["path"] == "tool-surfaces/.github/workflows/ci.yml")
    assert workflow_entry["coupling_type"] == "invocation"
    assert workflow_entry["detection_source"] == "invocation-pattern"
    assert workflow_entry["confidence"] == "high"


def test_scan_detects_workflow_npm_prefix_script_indirection(tmp_path, capsys):
    package = tmp_path / "tool-surfaces" / "package.json"
    package.parent.mkdir(parents=True, exist_ok=True)
    package.write_text(
        '{\n  "scripts": {\n    "lint:js": "eslint eslint.config.js"\n  }\n}\n',
        encoding="utf-8",
    )
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - run: npm --prefix tool-surfaces run lint:js\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "eslint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
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


def test_scan_detects_renovate_config_as_high_confidence(tmp_path, capsys):
    config = tmp_path / "renovate.json"
    config.write_text('{"extends":["config:best-practices"]}\n', encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "renovate", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == "renovate.json"
    assert data[0]["coupling_type"] == "config"
    assert data[0]["detection_source"] == "surface-rule"
    assert data[0]["confidence"] == "high"


def test_scan_detects_dependabot_config_as_high_confidence(tmp_path, capsys):
    config = tmp_path / ".github" / "dependabot.yml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(
        "version: 2\nupdates:\n  - package-ecosystem: pip\n    directory: /\n    schedule:\n      interval: weekly\n",
        encoding="utf-8",
    )
    rc = run("scan", "--target", str(tmp_path), "--tool", "dependabot", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".github/dependabot.yml"
    assert data[0]["coupling_type"] == "config"
    assert data[0]["detection_source"] == "surface-rule"
    assert data[0]["confidence"] == "high"


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


def test_scan_detects_prefixed_vscode_settings(tmp_path, capsys):
    settings = tmp_path / "tool-surfaces" / ".vscode" / "settings.json"
    settings.parent.mkdir(parents=True, exist_ok=True)
    settings.write_text(
        '{\n  "eslint.validate": ["javascript"]\n}\n',
        encoding="utf-8",
    )
    rc = run("scan", "--target", str(tmp_path), "--tool", "vscode-eslint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == "tool-surfaces/.vscode/settings.json"
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


def test_scan_detects_prefixed_package_json_script_as_invocation(tmp_path, capsys):
    package = tmp_path / "tool-surfaces" / "package.json"
    package.parent.mkdir(parents=True, exist_ok=True)
    package.write_text(
        '{\n  "scripts": {\n    "lint:js": "eslint eslint.config.js"\n  }\n}\n',
        encoding="utf-8",
    )
    rc = run("scan", "--target", str(tmp_path), "--tool", "eslint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == "tool-surfaces/package.json"
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


def test_scan_detects_pytest_xdist_alias_with_underscore(tmp_path, capsys):
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - run: python -m pytest tests -q -n auto\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "pytest_xdist", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".github/workflows/ci.yml"
    assert data[0]["coupling_type"] == "invocation"
    assert data[0]["detection_source"] == "invocation-pattern"
    assert data[0]["confidence"] == "high"


def test_scan_detects_pytest_xdist_short_alias(tmp_path, capsys):
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - run: pytest tests -q -n auto\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "xdist", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".github/workflows/ci.yml"
    assert data[0]["coupling_type"] == "invocation"
    assert data[0]["detection_source"] == "invocation-pattern"
    assert data[0]["confidence"] == "high"


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


def test_scan_ignores_token_collision_in_non_docs_file(tmp_path, capsys):
    manifest = tmp_path / "ops.yaml"
    manifest.write_text("tool: ruffle\nowner: team\n", encoding="utf-8")
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


def test_scan_detects_hadolint_workflow_action_usage_as_high_confidence(tmp_path, capsys):
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - uses: hadolint/hadolint-action@v3.1.0\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "hadolint", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".github/workflows/ci.yml"
    assert data[0]["coupling_type"] == "invocation"
    assert data[0]["detection_source"] == "invocation-pattern"
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


def test_scan_detects_shellcheck_workflow_action_usage_as_high_confidence(tmp_path, capsys):
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - uses: reviewdog/action-shellcheck@v1\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "shellcheck", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".github/workflows/ci.yml"
    assert data[0]["coupling_type"] == "invocation"
    assert data[0]["detection_source"] == "invocation-pattern"
    assert data[0]["confidence"] == "high"


def test_scan_detects_trivy_surface_filename_without_tool_name(tmp_path, capsys):
    config = tmp_path / ".trivyignore"
    config.write_text("# advisory accepted during bounded test\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "trivy", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".trivyignore"
    assert data[0]["coupling_type"] == "config"
    assert data[0]["detection_source"] == "surface-rule"
    assert data[0]["confidence"] == "high"


def test_scan_detects_trivy_workflow_action_usage_as_high_confidence(tmp_path, capsys):
    workflow = tmp_path / ".github" / "workflows" / "ci.yml"
    workflow.parent.mkdir(parents=True, exist_ok=True)
    workflow.write_text("steps:\n  - uses: aquasecurity/trivy-action@0.31.0\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "trivy", "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data[0]["path"] == ".github/workflows/ci.yml"
    assert data[0]["coupling_type"] == "invocation"
    assert data[0]["detection_source"] == "invocation-pattern"
    assert data[0]["confidence"] == "high"


@pytest.mark.parametrize(
    ("tool", "rel_path", "contents", "expected"),
    [
        (
            "ruff",
            "app.py",
            "import ruff\nfrom ruff import check\n",
            {"coupling_type": "import", "removal_cost": "edit", "detection_source": "python-import", "confidence": "high"},
        ),
        (
            "ruff",
            "pyproject.toml",
            "[tool.ruff]\nline-length = 88\n",
            {"coupling_type": "config", "removal_cost": "edit", "detection_source": "config-mention", "confidence": "high"},
        ),
        (
            "ruff",
            "requirements.txt",
            "ruff>=0.1\npytest\n",
            {"coupling_type": "config", "removal_cost": "clean", "detection_source": "config-mention", "confidence": "medium"},
        ),
        (
            "prettier",
            ".prettierrc.json",
            "{ \"semi\": true }\n",
            {"coupling_type": "config", "removal_cost": "edit", "detection_source": "surface-rule", "confidence": "high"},
        ),
        (
            "pre-commit",
            ".pre-commit-config.yaml",
            "repos:\n  - repo: local\n    hooks:\n      - id: ruff-check\n        entry: python -m ruff check\n",
            {"coupling_type": "config", "removal_cost": "edit", "detection_source": "surface-rule", "confidence": "high"},
        ),
        (
            "ruff",
            ".pre-commit-config.yaml",
            "repos:\n  - repo: local\n    hooks:\n      - id: ruff-check\n        entry: python -m ruff check\n",
            {"coupling_type": "invocation", "removal_cost": "edit", "detection_source": "config-mention", "confidence": "high"},
        ),
        (
            "pytest-xdist",
            ".github/workflows/ci.yml",
            "steps:\n  - run: python -m pytest tests -q -n auto\n",
            {"coupling_type": "invocation", "removal_cost": "edit", "detection_source": "invocation-pattern", "confidence": "high"},
        ),
        (
            "actionlint",
            ".github/workflows/ci.yml",
            "steps:\n  - uses: rhysd/actionlint@v1\n",
            {"coupling_type": "invocation", "removal_cost": "edit", "detection_source": "invocation-pattern", "confidence": "high"},
        ),
        (
            "dependabot",
            ".github/dependabot.yml",
            "version: 2\nupdates:\n  - package-ecosystem: pip\n    directory: /\n    schedule:\n      interval: weekly\n",
            {"coupling_type": "config", "removal_cost": "edit", "detection_source": "surface-rule", "confidence": "high"},
        ),
        (
            "vscode-eslint",
            ".vscode/settings.json",
            "{\n  \"eslint.validate\": [\"javascript\"]\n}\n",
            {"coupling_type": "config", "removal_cost": "edit", "detection_source": "surface-rule", "confidence": "high"},
        ),
        (
            "eslint",
            "package.json",
            '{\n  "devDependencies": {\n    "eslint": "^9.0.0"\n  }\n}\n',
            {"coupling_type": "config", "removal_cost": "edit", "detection_source": "config-mention", "confidence": "high"},
        ),
        (
            "eslint",
            "package.json",
            '{\n  "scripts": {\n    "lint": "eslint ."\n  }\n}\n',
            {"coupling_type": "invocation", "removal_cost": "edit", "detection_source": "invocation-pattern", "confidence": "high"},
        ),
        (
            "eslint",
            ".github/workflows/ci.yml",
            "steps:\n  - run: npm run lint:js\n",
            {"coupling_type": "invocation", "removal_cost": "edit", "detection_source": "invocation-pattern", "confidence": "high"},
        ),
        (
            "hadolint",
            "Dockerfile",
            "# hadolint global ignore=DL3008\nFROM alpine:3.20\n",
            {"coupling_type": "config", "removal_cost": "edit", "detection_source": "surface-rule", "confidence": "high"},
        ),
        (
            "shellcheck",
            "repo-smoke.sh",
            "#!/usr/bin/env bash\n# shellcheck shell=bash\n",
            {"coupling_type": "config", "removal_cost": "edit", "detection_source": "config-mention", "confidence": "high"},
        ),
        (
            "trivy",
            ".github/workflows/ci.yml",
            "steps:\n  - uses: aquasecurity/trivy-action@0.31.0\n",
            {"coupling_type": "invocation", "removal_cost": "edit", "detection_source": "invocation-pattern", "confidence": "high"},
        ),
        (
            "ruff",
            "Makefile",
            "lint:\n\truff check .\n",
            {"coupling_type": "invocation", "removal_cost": "edit", "detection_source": "invocation-pattern", "confidence": "high"},
        ),
    ],
)
def test_scan_exact_output_tuple_contracts(tmp_path, capsys, tool, rel_path, contents, expected):
    path = tmp_path / Path(rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if tool == "eslint" and rel_path == ".github/workflows/ci.yml":
        package = tmp_path / "package.json"
        package.write_text(
            '{\n  "scripts": {\n    "lint:js": "eslint eslint.config.js"\n  }\n}\n',
            encoding="utf-8",
        )
    path.write_text(contents, encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", tool, "--json")
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    entry = next(item for item in data if item["path"] == rel_path.replace("\\", "/"))
    assert entry["coupling_type"] == expected["coupling_type"]
    assert entry["removal_cost"] == expected["removal_cost"]
    assert entry["detection_source"] == expected["detection_source"]
    assert entry["confidence"] == expected["confidence"]


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


def test_scan_record_written_note_conforms_to_coupling_schema(tmp_path, capsys):
    root = tmp_path / ".adop"
    root.mkdir()
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
    rc = run(
        "scan", "--artifact-root", str(root),
        "--target", str(tmp_path), "--tool", "ruff",
        "--scene", "lint", "--record",
    )
    assert rc == 0
    capsys.readouterr()
    note_path = next(root.rglob("adop_coupling-note_*.json"))
    payload = json.loads(note_path.read_text(encoding="utf-8"))
    assert payload["related_scene"] == "lint"
    assert payload["candidate_or_tool"] == "ruff"
    coupling = payload["couplings"][0]
    assert coupling["path"] == "pyproject.toml"
    assert coupling["coupling_type"] == "config"
    assert coupling["removal_cost"] == "edit"
    assert coupling["detection_source"] == "config-mention"
    assert coupling["confidence"] == "high"
    validate_coupling_note_payload(payload)


def test_scan_without_record_stays_advisory_and_writes_no_coupling_note(tmp_path, capsys):
    root = tmp_path / ".adop"
    root.mkdir()
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
    rc = run("scan", "--artifact-root", str(root), "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert "Scan output is advisory only." in out
    assert not list(root.rglob("adop_coupling-note_*.json"))


def test_scan_record_requires_scene(tmp_path):
    root = str(tmp_path / ".adop")
    Path(root).mkdir()
    (tmp_path / "pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
    rc = run("scan", "--artifact-root", root, "--target", str(tmp_path), "--tool", "ruff", "--record")
    assert rc == 2


def test_scan_invalid_target(tmp_path):
    rc = run("scan", "--target", str(tmp_path / "nonexistent"), "--tool", "ruff")
    assert rc == 2


@pytest.mark.parametrize(
    "skip_dir",
    [".adop", ".git", ".hg", "node_modules", ".venv", "venv", "env", ".pytest_cache", ".mypy_cache", "__pycache__", "dist"],
)
def test_scan_skips_internal_default_skip_dirs(tmp_path, capsys, skip_dir):
    kept = tmp_path / "src" / "pyproject.toml"
    kept.parent.mkdir(parents=True, exist_ok=True)
    kept.write_text("[tool.ruff]\n", encoding="utf-8")
    skipped = tmp_path / skip_dir / "pyproject.toml"
    skipped.parent.mkdir(parents=True, exist_ok=True)
    skipped.write_text("[tool.ruff]\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert "src/pyproject.toml" in out
    assert f"{skip_dir}/pyproject.toml" not in out


@pytest.mark.parametrize(
    ("rel_dir", "filename"),
    [("pkg.egg-info", "PKG-INFO"), ("pkg.dist-info", "METADATA")],
)
def test_scan_skips_generated_package_metadata_dirs(tmp_path, capsys, rel_dir, filename):
    kept = tmp_path / "src" / "pyproject.toml"
    kept.parent.mkdir(parents=True, exist_ok=True)
    kept.write_text("[tool.ruff]\n", encoding="utf-8")
    skipped = tmp_path / rel_dir / filename
    skipped.parent.mkdir(parents=True, exist_ok=True)
    skipped.write_text("ruff mentioned in package metadata\n", encoding="utf-8")
    rc = run("scan", "--target", str(tmp_path), "--tool", "ruff")
    assert rc == 0
    out = capsys.readouterr().out
    assert "src/pyproject.toml" in out
    assert f"{rel_dir}/{filename}" not in out


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
