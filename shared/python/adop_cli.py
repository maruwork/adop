#!/usr/bin/env python3
"""ADOP JSON-native CLI."""

from __future__ import annotations

import argparse
import fnmatch
import io
import json
import os
import re
import shutil
import sys
import tomllib
from argparse import RawTextHelpFormatter
from pathlib import Path
from typing import Any

from common import fix_stdout_encoding

import adop_artifacts as artifacts
from adop_html import render_dashboard_html
from adop_ids import next_sequential_id, parse_numeric_id
from adop_state_machine import comparison_ready_for_trial, promote_gate_errors
from adop_summary import build_summary, get_scene_states
from adop_types import (
    ARCHIVE_NOTE,
    BLOCKED_NOTE,
    CANDIDATE_INTAKE_NOTE,
    CANDIDATE_SHAPES,
    COMPARISON_NOTE,
    COUPLING_NOTE,
    COUPLING_TYPES,
    DECOMPOSITION_DECISION,
    DECOMPOSITION_DECISIONS,
    DEPRECATION_NOTE,
    DISPOSITIONS,
    EVALUATION_GATE,
    EXECUTOR,
    FALLBACKS,
    FILTER_NAMES,
    FILTER_STATUSES,
    FIT_LANES,
    HOLD_NOTE,
    JUDGMENT_REPORT,
    LANDING_TARGET,
    LANES,
    MIGRATION_NOTE,
    OBSERVED_EFFECT,
    PLATFORMS,
    PROMOTION_NOTE,
    PROPOSED,
    RECURRING_CONTROL_DECISIONS,
    REJECT_NOTE,
    REMOVAL_COSTS,
    ROOT_CAUSE_HYPOTHESIS,
    SANDBOX_TYPES,
    SCHEMA_VERSION,
    STRUCTURAL_GAP,
    TRIAL_PACKET,
    TRIAL_RESULT,
    TRIAL_TYPES,
    VERDICTS,
    WATCH_NOTE,
)
from adop_validation import (
    AdopValidationError,
    lint_artifact_root,
    today_iso,
    unknown_tool_attribute_fields,
    validate_archive_note_payload,
    validate_blocked_note_payload,
    validate_close_payload,
    validate_comparison_payload,
    validate_coupling_note_payload,
    validate_deprecation_note_payload,
    validate_filter_assessment,
    validate_intake_payload,
    validate_migration_note_payload,
    validate_no_impact_trial_mode,
    validate_trial_packet_payload,
    validate_watch_note_payload,
)

fix_stdout_encoding()

__version__ = "0.1.1"

_DEFAULT_ARTIFACT_ROOT = ".adop"

# Overlay stub written by `adop init` when the template file cannot be located.
_OVERLAY_INIT_STUB = """\
# Project-Local ADOP Overlay

**Status**: Active
**Common authority**: https://github.com/maruwork/adop
**ADOP version synced**: [fill in from adop.json at sync time]

Copy this file into the project. Fill in each section.
Do not copy schema, lifecycle definitions, or CLI descriptions from ADOP - reference them.

---

## Artifact Root

Adoption artifacts for this project live at:

```
[path/to/artifact-root/]
```

Validate: `python shared/python/adop_cli.py lint --artifact-root [path]`

---

## Runtime Copy

ADOP runtime files (`adop_*.py`, `common.py`) are at:

```
[path/to/adop-runtime-copy/]
```

Last verified against canonical: [date]
Check drift: `python shared/python/adop_sync.py check --target [path/to/project-root/]`

---

## Active Scene Lanes

| Scene Lane | Tool | Current State | Last Activity |
|---|---|---|---|
| [scene] | [tool] | [state] | [date] |

Live view: `python shared/python/adop_cli.py summary --artifact-root [path]`

---

## Operator Flow

| Stage | Who | How |
|---|---|---|
| Raise a candidate | [who] | [how: issue, doc, meeting] |
| Run comparison | [who] | [time box, decision method] |
| Open trial | [who] | [executor, mode, scope] |
| Close trial | [who] | [judgment criteria, sign-off] |
| Define landing target | [who] | [authority, location] |

---

## Current Judgment Memo

State the current project-side judgment in the same language the shared checklist expects.
Fill these fields even when the answer is "none yet" or "not approved".

| Item | Current project answer |
|---|---|
| Adoption class | [operations integration / creation assistance / mixed] |
| Layer to strengthen | [interface / mechanism / scaling] |
| Phase | [core build / future extension / implementation / self-improvement loop] |
| What serves as authority | [repo files, human review gate, workflow, etc.] |
| What does not serve as authority | [tool output, preview HTML rows, ad-hoc chat notes, etc.] |
| Fail-close / escalation / verification | [how the project stops, who decides, and how to verify] |

---

## Approved Use Scenes

List the scenes that are currently approved for recurring use in this project.
If nothing is approved yet, say so explicitly.

| Scene | Tool | Allowed use | Landing target | Notes |
|---|---|---|---|---|
| [scene or "none yet"] | [tool] | [what is currently approved] | [target] | [scope or approval note] |

---

## Prohibited Use Scenes

List the scenes that are currently blocked or forbidden in this project.
Include both "not approved yet" and "explicitly prohibited" when relevant.

| Scene | Tool | Prohibited or blocked use | Reason | Reopen condition |
|---|---|---|---|---|
| [scene or "none recorded"] | [tool] | [what must not happen] | [why] | [what would change this] |

---

## Landing Target Authority

Promoted tools land at:

| Target | Owner | Notes |
|---|---|---|
| [target location] | [owner] | [scope] |

---

## Pending Project Decisions

| Item | Status |
|---|---|
| [pending project decision or gap] | [pending / in-progress] |

---

## Return Path

Common authority: https://github.com/maruwork/adop
Lifecycle and schema spec: `docs/design/adop-lifecycle-schema-design.md`
Adoption checklist: `docs/checklists/external-tool-adoption-checklist.md`
"""

# Next-command templates keyed by lifecycle state.
_NEXT_FOR_STATE: dict[str, str] = {
    "watch":       'adop quick-intake --scene {scene} --candidate <tool> --source doc --why-now "<reason>"',
    "proposed":    'adop quick-compare --scene {scene} --candidate <tool> --candidate <other> --selected <tool>',
    "trial-ready": 'adop quick-trial --scene {scene} --mode review-assist --executor <who> --decision-owner <owner> --landing-target <target>',
    "blocked":     'adop unblock --scene {scene} --why-unblocked "<what changed>"',
    "hold":        'adop quick-compare --scene {scene} --candidate <tool> --candidate <other> --selected <tool>  # resume trial; or: adop deprecate if no longer needed',
    "reject":      'adop deprecate --scene {scene} --deprecation-reason "rejected at trial" # or: adop archive if fully closed',
    "deprecated":  'adop migrate --scene {scene} --migration-target <target> --migration-plan "<plan>"',
    "migrating":   'adop archive --scene {scene} --end-date <YYYY-MM-DD>',
}

_CONFIG_FILE_NAMES: frozenset[str] = frozenset({
    "pyproject.toml", "setup.cfg", "setup.py", "tox.ini",
    ".pre-commit-config.yaml", ".flake8",
    "requirements.txt", "requirements-dev.txt", "requirements-test.txt",
})

# Node ecosystem: package.json declares deps + scripts; lock files are generated artifacts.
_NODE_DEP_FILES: frozenset[str] = frozenset({
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
})

_TOOL_SURFACE_RULES: dict[str, tuple[dict[str, Any], ...]] = {
    "actionlint": (
        {
            "patterns": (".actionlint.yaml", ".actionlint.yml", ".github/actionlint.yaml", ".github/actionlint.yml"),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "tool-owned config surface",
        },
    ),
    "dependabot": (
        {
            "patterns": (".github/dependabot.yml", ".github/dependabot.yaml"),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "dependency bot config surface",
        },
    ),
    "eslint": (
        {
            "patterns": (
                "eslint.config.js", "eslint.config.cjs", "eslint.config.mjs",
                ".eslintrc", ".eslintrc.json", ".eslintrc.yaml", ".eslintrc.yml", ".eslintrc.js",
                ".eslintignore",
            ),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "tool-owned config surface",
        },
        {
            "patterns": (".vscode/extensions.json",),
            "contains_any": ("dbaeumer.vscode-eslint",),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "workspace extension recommendation",
        },
        {
            "patterns": (".vscode/settings.json",),
            "contains_any": ("\"eslint.validate\"", "\"source.fixall.eslint\"", "\"eslint."),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "workspace editor settings",
        },
    ),
    "hadolint": (
        {
            "patterns": (".hadolint.yaml", ".hadolint.yml"),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "tool-owned config surface",
        },
        {
            "path_prefixes": ("dockerfile",),
            "contains_any": ("hadolint",),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "inline hadolint directives",
        },
    ),
    "markdownlint-cli2": (
        {
            "patterns": (".markdownlint-cli2.jsonc", ".markdownlint-cli2.json", ".markdownlint-cli2.yaml", ".markdownlint-cli2.yml"),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "tool-owned config surface",
        },
    ),
    "pre-commit": (
        {
            "patterns": (".pre-commit-config.yaml", ".pre-commit-config.yml"),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "tool-owned config surface",
        },
    ),
    "prettier": (
        {
            "patterns": (
                ".prettierrc", ".prettierrc.json", ".prettierrc.yaml", ".prettierrc.yml",
                ".prettierignore", "prettier.config.js", "prettier.config.cjs", "prettier.config.mjs",
            ),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "tool-owned config surface",
        },
    ),
    "renovate": (
        {
            "patterns": ("renovate.json", "renovate.json5", ".github/renovate.json", ".github/renovate.json5"),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "dependency bot config surface",
        },
    ),
    "shellcheck": (
        {
            "patterns": (".shellcheckrc", "shellcheckrc"),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "tool-owned config surface",
        },
    ),
    "trivy": (
        {
            "patterns": (".trivyignore", "trivy.yaml", "trivy.yml", ".trivy/config.yaml", ".trivy/config.yml"),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "scanner config surface",
        },
    ),
    "vscode-eslint": (
        {
            "patterns": (".vscode/extensions.json",),
            "contains_any": ("dbaeumer.vscode-eslint",),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "workspace extension recommendation",
        },
        {
            "patterns": (".vscode/settings.json",),
            "contains_any": ("\"eslint.validate\"", "\"source.fixall.eslint\"", "\"eslint."),
            "coupling_type": "config",
            "removal_cost": "edit",
            "note": "workspace editor settings",
        },
    ),
}

_SCAN_SKIP_DIRS: frozenset[str] = frozenset({
    ".git", ".hg", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".venv", "venv", "env", "node_modules", ".adop", "build", "dist",
})

_PLATFORM_ALIASES: dict[str, str] = {
    "win": "windows",
    "win32": "windows",
    "windows": "windows",
    "mac": "mac",
    "macos": "mac",
    "osx": "mac",
    "darwin": "mac",
    "linux": "linux",
    "ubuntu": "linux",
    "debian": "linux",
    "alpine": "linux",
    "all": "any",
    "any": "any",
    "cross-platform": "any",
    "crossplatform": "any",
    "cross_platform": "any",
    "platform-agnostic": "any",
    "platformagnostic": "any",
    "agnostic": "any",
    "python": "any",
    "node": "any",
    "javascript": "any",
    "js": "any",
    "typescript": "any",
    "ts": "any",
    "java": "any",
    "go": "any",
    "rust": "any",
    "dotnet": "any",
    "cli": "any",
    "web": "any",
    "unknown": "unknown",
}

_EVALUATION_ONLY_MARKERS: tuple[str, ...] = (
    "quick-intake",
    "quick-compare",
    "quick-trial",
    "quick-close-trial",
    "--candidate",
    "--selected",
    "--scene",
    "--use-case",
    "candidate_or_tool",
)


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _parse_json_arg(raw: str, field_name: str) -> Any:
    text = raw
    if raw.startswith("@"):
        file_path = Path(raw[1:])
        try:
            text = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise AdopValidationError(f"{field_name} file not readable: {file_path}", 2) from exc
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise AdopValidationError(f"{field_name} must be valid JSON: {exc.msg}", 2) from exc


def _root_path(args: argparse.Namespace) -> Path:
    """Resolve artifact root for read-only commands; raise with helpful hint if missing."""
    root = Path(getattr(args, "artifact_root", _DEFAULT_ARTIFACT_ROOT))
    if not root.exists():
        hint = " — run 'adop init' to create it" if str(root) == _DEFAULT_ARTIFACT_ROOT else ""
        raise AdopValidationError(f"artifact root not found: '{root}'{hint}", 2)
    return root


def _next_step(scene: str, state: str, root: Path, items: list[dict[str, Any]]) -> str:
    """Return the recommended next CLI command for the given scene/state."""
    if state == "in-trial":
        pkts = [
            i for i in items
            if i.get("artifact_type") == TRIAL_PACKET
            and str(i.get("related_scene", "")) == scene
        ]
        trial_id = str(pkts[-1]["artifact_id"]) if pkts else "tr-001"
        return (
            f"adop quick-close-trial --trial-id {trial_id} "
            f'--verdict <promote|hold|reject> --observed-effect "<what you saw>" '
            f"# promote also requires explicit judgment fields"
        )
    template = _NEXT_FOR_STATE.get(state, "")
    return template.format(scene=scene) if template else ""


def _prepare_artifact_root(args: argparse.Namespace) -> Path:
    root_arg = getattr(args, "artifact_root", _DEFAULT_ARTIFACT_ROOT)
    if not Path(root_arg).exists() and root_arg == _DEFAULT_ARTIFACT_ROOT:
        raise AdopValidationError(
            "artifact root '.adop' not found — run 'adop init' to create it", 2
        )
    try:
        return artifacts.ensure_artifact_root(
            Path(root_arg),
            target_project_root=Path(args.target_project_root) if getattr(args, "target_project_root", None) else None,
            allow_project_impact=bool(getattr(args, "allow_project_impact", False)),
        )
    except artifacts.AdopBoundaryError as exc:
        # Boundary violation only -> exit 14. Plain AdopArtifactError (e.g. mkdir
        # permission/IO failure) flows to main()'s handler, which returns 11.
        raise AdopValidationError(str(exc), 14) from exc


def _ensure_scene_not_rejected(root: Path, scene: str, *, command: str) -> None:
    state = get_scene_states(root).get(scene)
    if state == "reject":
        raise AdopValidationError(
            f"scene '{scene}' is terminal reject; {command} cannot reopen it. "
            "Use a new scene name for a materially new evaluation.",
            7,
        )


def _no_impact_envelope_default() -> dict[str, list[str]]:
    return {
        "allowed": [
            "file read",
            "metadata read",
            "git read",
            "artifact write outside target project",
            "temp clone outside target project",
        ],
        "forbidden": [
            "dependency install inside target project",
            "branch mutation inside target project",
            "tracked file write inside target project",
            "generated artifact write inside target project",
        ],
    }


def _default_tool_attributes() -> dict[str, Any]:
    return {
        "platform": "unknown",
        "license": "unknown",
        "cost": "unknown",
        "version": "unknown",
        "category": "unknown",
        "ai_compatibility": "unknown",
        "data_flow": {
            "destination": "unknown",
            "data_types": ["unknown"],
            "opt_in": True,
        },
    }


def _normalize_platform_value(raw: str) -> str:
    text = str(raw or "").strip()
    if not text:
        return text
    key = re.sub(r"[\s_]+", "-", text.lower())
    if key in PLATFORMS:
        return key
    return _PLATFORM_ALIASES.get(key, text)


def _normalize_scan_pattern(raw: str) -> str:
    return str(raw or "").replace("\\", "/").strip().lstrip("./").strip("/")


def _matches_scan_exclusion(rel_path: str, patterns: list[str]) -> bool:
    rel_norm = _normalize_scan_pattern(rel_path)
    if not rel_norm:
        return False
    basename = Path(rel_norm).name
    for pattern in patterns:
        pat = _normalize_scan_pattern(pattern)
        if not pat:
            continue
        if rel_norm == pat or rel_norm.startswith(f"{pat}/"):
            return True
        if fnmatch.fnmatch(rel_norm, pat) or fnmatch.fnmatch(basename, pat):
            return True
    return False


def _iter_scan_files(target: Path, excludes: list[str]) -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []
    for current_root, dirnames, filenames in os.walk(target):
        current = Path(current_root)
        rel_dir = current.relative_to(target).as_posix()
        rel_dir = "" if rel_dir == "." else rel_dir
        kept_dirs: list[str] = []
        for dirname in sorted(dirnames):
            rel = f"{rel_dir}/{dirname}" if rel_dir else dirname
            if (
                dirname in _SCAN_SKIP_DIRS
                or dirname.endswith((".egg-info", ".dist-info"))
                or _matches_scan_exclusion(rel, excludes)
            ):
                continue
            kept_dirs.append(dirname)
        dirnames[:] = kept_dirs
        for filename in sorted(filenames):
            rel = f"{rel_dir}/{filename}" if rel_dir else filename
            if _matches_scan_exclusion(rel, excludes):
                continue
            files.append((current / filename, rel))
    return files


def _tool_search_aliases(tool: str) -> list[str]:
    base = tool.lower().strip()
    aliases = {
        base,
        base.replace("-", "_"),
        base.replace("_", "-"),
        base.replace(".", "-"),
        base.replace(".", "_"),
    }
    if base == "pytest-xdist":
        aliases.add("xdist")
    return sorted((alias for alias in aliases if alias), key=len, reverse=True)


def _text_mentions_tool(text_lower: str, aliases: list[str]) -> bool:
    return any(
        re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?![a-z0-9])", text_lower)
        for alias in aliases
    )


def _operational_tool_mention_exists(text_lower: str, aliases: list[str]) -> bool:
    for raw_line in text_lower.splitlines():
        line = raw_line.strip()
        if not line or not _text_mentions_tool(line, aliases):
            continue
        if any(marker in line for marker in _EVALUATION_ONLY_MARKERS):
            continue
        return True
    return False


def _build_detected_coupling(
    rel: str,
    coupling_type: str,
    removal_cost: str,
    *,
    note: str | None = None,
    detection_source: str,
    confidence: str,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "path": rel,
        "coupling_type": coupling_type,
        "removal_cost": removal_cost,
        "detection_source": detection_source,
        "confidence": confidence,
    }
    if note:
        entry["note"] = note
    return entry


def _surface_rule_match(tool: str, rel: str, text_lower: str) -> dict[str, Any] | None:
    rules = _TOOL_SURFACE_RULES.get(tool.lower().strip(), ())
    rel_lower = rel.lower()
    for rule in rules:
        patterns = tuple(str(pattern).lower() for pattern in rule.get("patterns", ()))
        prefixes = tuple(str(prefix).lower() for prefix in rule.get("path_prefixes", ()))
        matches_path = rel_lower in patterns or any(Path(rel_lower).name.startswith(prefix) for prefix in prefixes)
        if not matches_path:
            continue
        contains_any = tuple(str(token).lower() for token in rule.get("contains_any", ()))
        if contains_any and not any(token in text_lower for token in contains_any):
            continue
        return _build_detected_coupling(
            rel,
            str(rule["coupling_type"]),
            str(rule["removal_cost"]),
            note=str(rule.get("note", "")) or None,
            detection_source="surface-rule",
            confidence="high",
        )
    return None


def _text_mentions_tool_in_context(tool: str, rel: str, text_lower: str, aliases: list[str]) -> bool:
    tool_key = tool.lower().strip()
    rel_lower = rel.lower()
    if tool_key == "renovate":
        return bool(
            re.search(r"(?<!check-)\brenovate\b", text_lower)
            or "renovatebot" in text_lower
        )
    if tool_key == "hadolint" and Path(rel_lower).name.startswith("dockerfile"):
        return "hadolint" in text_lower
    return _operational_tool_mention_exists(text_lower, aliases)


def _dependency_string_mentions_tool(raw: Any, aliases: list[str]) -> bool:
    if not isinstance(raw, str):
        return False
    value = raw.lower()
    return any(
        re.search(rf"(?<![a-z0-9]){re.escape(alias)}(?=[<>=!~\s\[\],;]|$)", value)
        for alias in aliases
    )


def _structured_pyproject_match(rel: str, text: str, aliases: list[str]) -> dict[str, Any] | None:
    if rel.lower() != "pyproject.toml":
        return None
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return None

    tool_table = data.get("tool")
    normalized_aliases = {alias.replace("-", "_").replace(".", "_") for alias in aliases}
    if isinstance(tool_table, dict) and any(alias in tool_table for alias in normalized_aliases):
        return _build_detected_coupling(
            rel, "config", "edit",
            note="tool configuration section",
            detection_source="config-mention",
            confidence="high",
        )

    dependency_lists: list[list[Any]] = []
    project = data.get("project")
    if isinstance(project, dict):
        direct = project.get("dependencies")
        if isinstance(direct, list):
            dependency_lists.append(direct)
        optional = project.get("optional-dependencies")
        if isinstance(optional, dict):
            dependency_lists.extend(value for value in optional.values() if isinstance(value, list))
    build_system = data.get("build-system")
    if isinstance(build_system, dict):
        requires = build_system.get("requires")
        if isinstance(requires, list):
            dependency_lists.append(requires)

    if any(_dependency_string_mentions_tool(item, aliases) for group in dependency_lists for item in group):
        return _build_detected_coupling(
            rel, "config", "edit",
            note="dependency declaration",
            detection_source="config-mention",
            confidence="high",
        )
    return None


def _structured_package_json_match(rel: str, text: str, aliases: list[str], tool: str) -> dict[str, Any] | None:
    if rel.lower() != "package.json":
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    dependency_maps = [
        data.get("dependencies"),
        data.get("devDependencies"),
        data.get("optionalDependencies"),
        data.get("peerDependencies"),
    ]
    alias_set = {alias.lower() for alias in aliases}
    for mapping in dependency_maps:
        if isinstance(mapping, dict) and any(str(key).lower() in alias_set for key in mapping):
            return _build_detected_coupling(
                rel, "config", "edit",
                note="dependency declaration",
                detection_source="config-mention",
                confidence="high",
            )

    scripts = data.get("scripts")
    if isinstance(scripts, dict):
        for value in scripts.values():
            if not isinstance(value, str):
                continue
            value_lower = value.lower()
            if _looks_like_pytest_xdist_invocation(tool, value_lower) or _text_mentions_tool_in_context(tool, rel, value_lower, aliases):
                return _build_detected_coupling(
                    rel, "invocation", "edit",
                    note="package script invocation",
                    detection_source="invocation-pattern",
                    confidence="high",
                )
    return None


def _structured_precommit_match(rel: str, text_lower: str, aliases: list[str]) -> dict[str, Any] | None:
    if rel.lower() not in (".pre-commit-config.yaml", ".pre-commit-config.yml"):
        return None

    if "github.com/pre-commit/pre-commit-hooks" in text_lower and any(alias == "pre-commit-hooks" for alias in aliases):
        return _build_detected_coupling(
            rel, "config", "edit",
            note="hook repository declaration",
            detection_source="config-mention",
            confidence="high",
        )
    if "github.com/python-jsonschema/check-jsonschema" in text_lower and any(alias == "check-jsonschema" for alias in aliases):
        return _build_detected_coupling(
            rel, "config", "edit",
            note="hook repository declaration",
            detection_source="config-mention",
            confidence="high",
        )

    for raw_line in text_lower.splitlines():
        line = raw_line.strip()
        if not line.startswith(("id:", "entry:", "name:")):
            continue
        if _text_mentions_tool(line, aliases):
            return _build_detected_coupling(
                rel, "invocation", "edit",
                note="hook entry declaration",
                detection_source="config-mention",
                confidence="high",
            )
    return None


def _package_scripts_matching_tool(target: Path, aliases: list[str], tool: str) -> set[str]:
    package_path = target / "package.json"
    if not package_path.exists():
        return set()
    try:
        data = json.loads(package_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    scripts = data.get("scripts")
    if not isinstance(scripts, dict):
        return set()
    matched: set[str] = set()
    for name, value in scripts.items():
        if not isinstance(name, str) or not isinstance(value, str):
            continue
        value_lower = value.lower()
        if _looks_like_pytest_xdist_invocation(tool, value_lower) or _text_mentions_tool_in_context(tool, "package.json", value_lower, aliases):
            matched.add(name.lower())
    return matched


def _workflow_command_lines(text_lower: str) -> list[str]:
    commands: list[str] = []
    in_run_block = False
    run_block_indent = -1
    for raw_line in text_lower.splitlines():
        stripped = raw_line.strip()
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if re.match(r"^-?\s*run:\s*[|>]\s*$", stripped):
            in_run_block = True
            run_block_indent = indent
            continue
        if stripped.startswith(("run:", "- run:")):
            commands.append(stripped.split(":", 1)[1].strip())
            in_run_block = False
            continue
        if in_run_block:
            if not stripped:
                continue
            if indent > run_block_indent:
                commands.append(stripped)
                continue
            in_run_block = False
        run_block_indent = run_block_indent if in_run_block else -1
    return commands


def _structured_workflow_match(target: Path, rel: str, text_lower: str, aliases: list[str], tool: str) -> dict[str, Any] | None:
    if not rel.lower().startswith(".github/workflows/"):
        return None

    action_patterns: dict[str, tuple[str, ...]] = {
        "actionlint": ("rhysd/actionlint@",),
        "hadolint": ("hadolint/hadolint-action@",),
        "shellcheck": ("action-shellcheck@",),
        "trivy": ("trivy-action@",),
    }
    matching_scripts = _package_scripts_matching_tool(target, aliases, tool)
    for raw_line in text_lower.splitlines():
        line = raw_line.strip()
        if line.startswith(("- uses:", "uses:")):
            if any(pattern in line for pattern in action_patterns.get(tool.lower().strip(), ())):
                return _build_detected_coupling(
                    rel, "invocation", "edit",
                    note="workflow action usage",
                    detection_source="invocation-pattern",
                    confidence="high",
                )
    for line in _workflow_command_lines(text_lower):
        if any(re.search(rf"\bnpm\s+run\s+{re.escape(script)}\b", line) for script in matching_scripts):
            return _build_detected_coupling(
                rel, "invocation", "edit",
                note="workflow run command",
                detection_source="invocation-pattern",
                confidence="high",
            )
        if _looks_like_pytest_xdist_invocation(tool, line) or _text_mentions_tool_in_context(tool, rel, line, aliases):
            return _build_detected_coupling(
                rel, "invocation", "edit",
                note="workflow run command",
                detection_source="invocation-pattern",
                confidence="high",
            )
    return None


def _structured_shell_script_match(path: Path, rel: str, text_lower: str, tool: str) -> dict[str, Any] | None:
    if tool.lower().strip() == "shellcheck" and path.suffix in (".sh", ".bash"):
        if any(raw_line.strip().startswith("# shellcheck ") for raw_line in text_lower.splitlines()):
            return _build_detected_coupling(
                rel, "config", "edit",
                note="inline shellcheck directive",
                detection_source="config-mention",
                confidence="high",
            )
    return None


def _structured_config_match(target: Path, path: Path, rel: str, text: str, text_lower: str, aliases: list[str], tool: str) -> dict[str, Any] | None:
    return (
        _structured_pyproject_match(rel, text, aliases)
        or _structured_package_json_match(rel, text, aliases, tool)
        or _structured_precommit_match(rel, text_lower, aliases)
        or _structured_workflow_match(target, rel, text_lower, aliases, tool)
        or _structured_shell_script_match(path, rel, text_lower, tool)
    )


def _looks_like_pytest_xdist_invocation(tool: str, text_lower: str) -> bool:
    if tool.lower() != "pytest-xdist":
        return False
    return bool(
        re.search(r"python\s+-m\s+pytest\b[^\n\r]*\s-n(?:\s|=)", text_lower)
        or re.search(r"\bpytest\b[^\n\r]*\s-n(?:\s|=)", text_lower)
    )


def _format_detection_suffix(entry: dict[str, Any]) -> str:
    note_text = f"  # {entry['note']}" if entry.get("note") else ""
    source = str(entry.get("detection_source", "")).strip()
    confidence = str(entry.get("confidence", "")).strip()
    if source and confidence:
        return f"  ({confidence} confidence via {source}){note_text}"
    if source:
        return f"  (via {source}){note_text}"
    if confidence:
        return f"  ({confidence} confidence){note_text}"
    return note_text


def _scan_target_for_tool(target: Path, tool: str, excludes: list[str]) -> list[dict[str, Any]]:
    tool_mod = re.sub(r"[-.]", "_", tool).lower()
    aliases = _tool_search_aliases(tool)
    couplings: list[dict[str, Any]] = []

    for path, rel in _iter_scan_files(target, excludes):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        text_lower = text.lower()

        surface_match = _surface_rule_match(tool, rel, text_lower)
        if surface_match:
            couplings.append(surface_match)
            continue

        structured_match = _structured_config_match(target, path, rel, text, text_lower, aliases, tool)
        if structured_match:
            couplings.append(structured_match)
            continue

        if path.suffix == ".py":
            if re.search(rf"(?m)^\s*(?:import|from)\s+{re.escape(tool_mod)}\b", text):
                couplings.append(
                    _build_detected_coupling(
                        rel, "import", "edit",
                        detection_source="python-import",
                        confidence="high",
                    )
                )
        elif path.name in _NODE_DEP_FILES:
            if _text_mentions_tool_in_context(tool, rel, text_lower, aliases):
                if path.name in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock"):
                    couplings.append(
                        _build_detected_coupling(
                            rel, "config", "clean",
                            note="generated lock file",
                            detection_source="config-mention",
                            confidence="medium",
                        )
                    )
                else:
                    couplings.append(
                        _build_detected_coupling(
                            rel, "config", "edit",
                            detection_source="config-mention",
                            confidence="medium",
                        )
                    )
        elif path.name in _CONFIG_FILE_NAMES or path.suffix in (".yml", ".yaml", ".toml", ".cfg", ".ini"):
            if _text_mentions_tool_in_context(tool, rel, text_lower, aliases) or _looks_like_pytest_xdist_invocation(tool, text_lower):
                if path.name in ("requirements.txt", "requirements-dev.txt", "requirements-test.txt"):
                    couplings.append(
                        _build_detected_coupling(
                            rel, "config", "clean",
                            note="dependency declaration",
                            detection_source="config-mention",
                            confidence="medium",
                        )
                    )
                else:
                    detection_source = "invocation-pattern" if _looks_like_pytest_xdist_invocation(tool, text_lower) else "config-mention"
                    confidence = "high" if detection_source == "invocation-pattern" else "medium"
                    couplings.append(
                        _build_detected_coupling(
                            rel, "config", "edit",
                            detection_source=detection_source,
                            confidence=confidence,
                        )
                    )
        elif path.suffix in (".sh", ".bash", ".ps1", ".bat", ".cmd") or path.name in ("Makefile", "makefile"):
            if _text_mentions_tool_in_context(tool, rel, text_lower, aliases) or _looks_like_pytest_xdist_invocation(tool, text_lower):
                detection_source = "invocation-pattern"
                confidence = "high"
                couplings.append(
                    _build_detected_coupling(
                        rel, "invocation", "edit",
                        detection_source=detection_source,
                        confidence=confidence,
                    )
                )
        elif _text_mentions_tool_in_context(tool, rel, text_lower, aliases) and path.suffix not in (".pyc", ".pyo", ".lock", ".md", ".rst", ".txt"):
            couplings.append(
                _build_detected_coupling(
                    rel, "reference", "clean",
                    detection_source="text-reference",
                    confidence="low",
                )
            )
    return couplings


def _write_coupling_note(root: Path, *, scene: str, tool: str, couplings: list[dict[str, Any]]) -> Path:
    artifact_id = next_sequential_id(root, "cp")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": COUPLING_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "related_scene": scene,
        "candidate_or_tool": tool,
        "couplings": couplings,
    }
    validate_coupling_note_payload(payload)
    return artifacts.write_artifact(root, COUPLING_NOTE, artifact_id, payload)


def _simple_project_profile_default() -> dict[str, Any]:
    return {
        "main_language": "unknown",
        "runtime": ["manual"],
        "artifact_surfaces": ["review-note", "trial-artifact"],
        "authority_boundary": "human approved writeback only",
        "operator_phase": "evaluation",
        "allowed_input_surfaces": ["tool output", "manual notes"],
        "allowed_mutation_boundary": "no write",
        "verification_methods": ["human review"],
    }


def _simple_compatibility_diagnosis_default(adoption_unit: str) -> list[dict[str, str]]:
    return [
        {
            "adoption_unit": adoption_unit,
            "scene_fit_to_project": "fits one bounded scene lane",
            "input_fit": "simple operator input is sufficient",
            "output_fit": "result can be reviewed before writeback",
            "authority_safe": "safe when reviewed before writeback",
            "controlability": "bounded trial is possible",
            "no_impact_feasibility": "artifact root can stay outside target project",
            "recommended_fit_lane": FIT_LANES[2],
        }
    ]


def _simple_trial_preset(mode: str) -> dict[str, str]:
    if mode == "review-assist":
        return {
            "trial_type": TRIAL_TYPES[2],
            "sandbox_type": SANDBOX_TYPES[0],
            "lane": LANES[1],
            "input_surface": "bounded review input",
            "output_contract": "structured review notes",
            "mutation_boundary": "no write",
            "verification_method": "human review",
            "trigger": "manual review request",
            "evaluation_gate": "at least one useful finding",
            "writeback_target": "trial-result and judgment-report",
            "fallback": FALLBACKS[2],
        }
    if mode == "read-only-comparison":
        return {
            "trial_type": TRIAL_TYPES[0],
            "sandbox_type": SANDBOX_TYPES[0],
            "lane": LANES[1],
            "input_surface": "bounded comparison input",
            "output_contract": "comparison summary",
            "mutation_boundary": "no write",
            "verification_method": "human review",
            "trigger": "manual comparison request",
            "evaluation_gate": "clear compare outcome",
            "writeback_target": "trial-result and judgment-report",
            "fallback": FALLBACKS[2],
        }
    raise AdopValidationError(f"unsupported quick trial mode: {mode}", 2)


def _simple_close_preset(verdict: str) -> dict[str, Any]:
    if verdict == VERDICTS[0]:
        return {
            "judgment_reason": "bounded trial produced reusable value",
            "next_action": "promote with explicit writeback review",
            "recurring_control_decision": RECURRING_CONTROL_DECISIONS[2],
            "reopen_condition": "",
            "preventive_actions": ["capture the reusable writeback pattern in project-local guidance"],
            "why_this_problem_recurred": "the use case had no stable helper path before the bounded trial",
        }
    if verdict == VERDICTS[1]:
        return {
            "judgment_reason": "bounded trial was useful but still needs narrowing",
            "next_action": "narrow the use case and rerun",
            "recurring_control_decision": RECURRING_CONTROL_DECISIONS[2],
            "reopen_condition": "retry after narrowing the use case or threshold",
            "preventive_actions": ["clarify the bounded scene before the next trial"],
            "why_this_problem_recurred": "the use case still depends on ad hoc operator judgment",
        }
    if verdict == VERDICTS[2]:
        return {
            "judgment_reason": "bounded trial did not justify continued use",
            "next_action": "keep the use case on manual handling",
            "recurring_control_decision": RECURRING_CONTROL_DECISIONS[1],
            "reopen_condition": "retry only if a different bounded scene appears",
            "preventive_actions": ["record the rejected pattern so the same trial is not repeated blindly"],
            "why_this_problem_recurred": "the candidate did not fit the bounded scene well enough",
        }
    raise AdopValidationError(f"unsupported quick close verdict: {verdict}", 2)


def _comparison_filter_args(parser: argparse.ArgumentParser) -> None:
    for cli_name in ("scene-fit", "authority-safe", "controlability"):
        key = cli_name.replace("-", "_")
        parser.add_argument(f"--{cli_name}-status", required=True, choices=FILTER_STATUSES)
        parser.add_argument(f"--{cli_name}-reason", required=True)
        parser.add_argument(f"--{cli_name}-constraint", default=None)


def _scene_arg(
    parser: argparse.ArgumentParser,
    *,
    required: bool,
    default: str | None = None,
    help_text: str | None = None,
    metavar: str | None = None,
) -> None:
    kwargs: dict[str, Any] = {"dest": "scene", "required": required}
    if default is not None:
        kwargs["default"] = default
    if help_text is not None:
        kwargs["help"] = help_text
    if metavar is not None:
        kwargs["metavar"] = metavar
    parser.add_argument("--scene", "--use-case", **kwargs)


def _project_boundary_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target-project-root")
    parser.add_argument("--allow-project-impact", action="store_true")


def _build_filter_assessment(args: argparse.Namespace) -> dict[str, dict[str, str | None]]:
    data: dict[str, dict[str, str | None]] = {}
    for key in FILTER_NAMES:
        cli_name = key.replace("_", "-")
        data[key] = {
            "status": getattr(args, f"{key}_status"),
            "reason": getattr(args, f"{key}_reason"),
            "constraint": getattr(args, f"{key}_constraint"),
        }
    validate_filter_assessment(data)
    return data


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="ADOP JSON-native CLI",
        epilog=(
            "First time in a project:\n"
            "  adop init                       # creates .adop/ and adop-overlay.md\n\n"
            "Simple path (guided path; some fields may be preset or defaulted):\n"
            "  quick-intake -> quick-compare -> quick-trial -> quick-close-trial\n\n"
            "Advanced path (explicit, full control over every field):\n"
            "  intake / compare / start-trial / close-trial\n\n"
            "Inspect anytime:\n"
            "  status / next / summary / list / show / lint\n"
            "  scan --target . --tool <name>   # detect couplings\n"
            "  scan --target . --tool <name> --scene <scene> --record\n\n"
            "Scene naming:\n"
            "  prefer --scene; legacy --use-case remains accepted for compatibility\n\n"
            "JSON-blob flags also accept a file via @path\n"
            "  e.g. --compatibility-diagnosis-json @diagnosis.json\n\n"
            "Exit codes:\n"
            "  0 ok\n"
            "  2 invalid CLI usage / validation\n"
            "  5 missing artifact or readiness gate not met\n"
            "  7 trial-ready or promotion gate not met\n"
            "  10 lint found invalid artifacts\n"
            "  11 artifact read/write/schema error\n"
            "  13 no-impact envelope violated (write trial requires isolated sandbox)\n"
            "  14 artifact-root boundary violation"
        ),
        formatter_class=RawTextHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"adop {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True, metavar="command")

    quick_intake = subparsers.add_parser(
        "quick-intake",
        help="simple path: create a candidate intake with minimal inputs",
        description="Create a candidate intake artifact from the minimum required inputs.",
    )
    quick_intake.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(quick_intake)
    quick_intake.add_argument("--candidate", required=True)
    quick_intake.add_argument("--source", required=True)
    _scene_arg(quick_intake, required=True, help_text="scene lane to record")
    quick_intake.add_argument("--why-now", required=True)
    quick_intake.add_argument("--candidate-shape", default=CANDIDATE_SHAPES[0], choices=CANDIDATE_SHAPES)
    quick_intake.add_argument("--lane", default=LANES[1], choices=LANES)
    quick_intake.add_argument("--root-cause-hypothesis", default="")
    quick_intake.add_argument("--platform", default="")
    quick_intake.add_argument("--license", default="")
    quick_intake.add_argument("--cost", default="")
    quick_intake.add_argument("--version", default="")
    quick_intake.add_argument("--category", default="")
    quick_intake.add_argument("--ai-compatibility", default="")
    quick_intake.add_argument("--data-flow-json", default="")

    quick_compare = subparsers.add_parser(
        "quick-compare",
        help="simple path: compare 2-3 candidates for one bounded scene lane",
        description="Create a comparison artifact with default project profile and filter reasoning.",
    )
    quick_compare.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(quick_compare)
    _scene_arg(quick_compare, required=True, help_text="scene lane to compare within")
    quick_compare.add_argument("--candidate", dest="candidates", action="append", required=True)
    quick_compare.add_argument("--selected", required=True)
    quick_compare.add_argument("--candidate-shape", default=CANDIDATE_SHAPES[0], choices=CANDIDATE_SHAPES)
    quick_compare.add_argument("--adoption-unit")
    quick_compare.add_argument("--root-cause-hypothesis", default="")
    quick_compare.add_argument("--structural-gap", default="current workflow lacks a bounded evaluation lane for this scene")
    quick_compare.add_argument("--non-tool-alternative", default="tighten the manual checklist before adding a tool")
    quick_compare.add_argument("--target-project-profile-json", default="")
    quick_compare.add_argument("--compatibility-diagnosis-json", default="")
    quick_compare.add_argument("--no-impact-envelope-json", default="")

    quick_trial = subparsers.add_parser(
        "quick-trial",
        help="simple path: open a bounded trial from the latest comparison",
        description="Start a trial with a small preset such as review-assist.",
    )
    quick_trial.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(quick_trial)
    _scene_arg(quick_trial, required=True, help_text="scene lane to open a trial for")
    quick_trial.add_argument("--mode", required=True, choices=("review-assist", "read-only-comparison"))
    quick_trial.add_argument("--executor", required=True)
    quick_trial.add_argument("--decision-owner", required=True)
    quick_trial.add_argument("--landing-target", required=True)
    quick_trial.add_argument("--trigger", default="")
    quick_trial.add_argument("--evaluation-gate", default="")
    quick_trial.add_argument("--writeback-target", default="")
    quick_trial.add_argument("--fallback", default="")

    quick_close = subparsers.add_parser(
        "quick-close-trial",
        help="simple path: close a trial; hold/reject can use presets, promote stays explicit",
        description=(
            "Close a trial with a verdict and observed effect. "
            "Hold/reject can use default judgment wording; promote requires explicit judgment fields."
        ),
    )
    quick_close.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(quick_close)
    quick_close.add_argument("--trial-id", required=True)
    quick_close.add_argument("--verdict", required=True, choices=VERDICTS)
    quick_close.add_argument("--observed-effect", required=True)
    quick_close.add_argument("--root-cause-hypothesis", default="")
    quick_close.add_argument("--judgment-reason", default="")
    quick_close.add_argument("--next-action", default="")
    quick_close.add_argument("--reopen-condition", default="")
    quick_close.add_argument("--recurring-control-decision", default="")
    quick_close.add_argument("--preventive-action", dest="preventive_actions", action="append", default=[])
    quick_close.add_argument("--why-this-problem-recurred", default="")

    intake = subparsers.add_parser(
        "intake",
        help="advanced: explicit candidate intake",
        description="Low-level intake command with explicit intake fields.",
    )
    intake.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(intake)
    intake.add_argument("--candidate", required=True)
    intake.add_argument("--candidate-shape", required=True, choices=CANDIDATE_SHAPES)
    intake.add_argument("--source", required=True)
    intake.add_argument("--scene", required=True)
    intake.add_argument("--lane", required=True, choices=LANES)
    intake.add_argument("--reason", required=True)
    intake.add_argument("--root-cause-hypothesis", required=True)
    intake.add_argument("--platform", required=True)
    intake.add_argument("--license", required=True)
    intake.add_argument("--cost", required=True)
    intake.add_argument("--version", required=True)
    intake.add_argument("--category", required=True)
    intake.add_argument("--ai-compatibility", required=True)
    intake.add_argument("--data-flow-json", required=True)

    compare = subparsers.add_parser(
        "compare",
        help="advanced: explicit comparison with full filter and compatibility fields",
        description="Low-level comparison command with explicit filters, project profile, and compatibility diagnosis.",
    )
    compare.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(compare)
    compare.add_argument("--scene", required=True)
    compare.add_argument("--candidate", dest="candidates", action="append", required=True)
    compare.add_argument("--selected", required=True)
    compare.add_argument("--candidate-shape", required=True, choices=CANDIDATE_SHAPES)
    compare.add_argument("--decomposition-decision", required=True, choices=DECOMPOSITION_DECISIONS)
    compare.add_argument("--adoption-unit", required=True)
    compare.add_argument("--discovered-subtarget", dest="discovered_subtargets", action="append", default=[])
    compare.add_argument("--recommended-next-candidate", default="")
    compare.add_argument("--target-project-profile-json", required=True)
    compare.add_argument("--compatibility-diagnosis-json", required=True)
    compare.add_argument("--no-impact-envelope-json", default="")
    compare.add_argument("--owner", default=None)
    compare.add_argument("--root-cause-hypothesis", required=True)
    compare.add_argument("--structural-gap", required=True)
    compare.add_argument("--non-tool-alternative", required=True)
    _comparison_filter_args(compare)

    start = subparsers.add_parser(
        "start-trial",
        help="advanced: explicit trial packet creation",
        description="Low-level trial command with explicit trial type, sandbox, gate, and writeback fields.",
    )
    start.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(start)
    start.add_argument("--scene", required=True)
    start.add_argument("--derived-from", default=None)
    start.add_argument("--trial-type", required=True, choices=TRIAL_TYPES)
    start.add_argument("--sandbox-type", required=True, choices=SANDBOX_TYPES)
    start.add_argument("--lane", required=True, choices=LANES)
    start.add_argument("--input-surface", required=True)
    start.add_argument("--output-contract", required=True)
    start.add_argument("--mutation-boundary", required=True)
    start.add_argument("--verification-method", required=True)
    start.add_argument("--executor", required=True)
    start.add_argument("--trigger", required=True)
    start.add_argument("--evaluation-gate", required=True)
    start.add_argument("--landing-target", required=True)
    start.add_argument("--writeback-target", required=True)
    start.add_argument("--decision-owner", required=True)
    start.add_argument("--fallback", required=True, choices=FALLBACKS)

    close = subparsers.add_parser(
        "close-trial",
        help="advanced: explicit trial close with full judgment fields",
        description="Low-level close command with explicit verdict, preventive actions, and recurring control fields.",
    )
    close.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(close)
    close.add_argument("--trial-id", required=True)
    close.add_argument("--verdict", required=True, choices=VERDICTS)
    close.add_argument("--observed-effect", required=True)
    close.add_argument("--judgment-reason", required=True)
    close.add_argument("--evidence-ref", dest="evidence_refs", action="append", default=[])
    close.add_argument("--reopen-condition", default="")
    close.add_argument("--next-action", required=True)
    close.add_argument("--recurring-control-decision", required=True, choices=RECURRING_CONTROL_DECISIONS)
    close.add_argument("--decision-owner", default=None)
    close.add_argument("--root-cause-hypothesis", required=True)
    close.add_argument("--preventive-action", dest="preventive_actions", action="append", required=True)
    close.add_argument("--why-this-problem-recurred", required=True)

    summary = subparsers.add_parser(
        "summary",
        help="show artifact summary",
        description="Render a text summary from the current artifact root.",
    )
    summary.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    summary.add_argument("--scene")
    summary.add_argument("--status")
    summary.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable JSON envelope instead of plain text",
    )

    render_html = subparsers.add_parser(
        "render-html",
        help="render one HTML dashboard from the current artifact root",
        description="Render the canonical ADOP HTML dashboard template with the current artifact data.",
    )
    render_html.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    render_html.add_argument("--output", required=True, metavar="FILE")
    render_html.add_argument("--title", default="ADOP Governance Dashboard")
    render_html.add_argument("--scene", help="preselect one scene lane in the rendered dashboard")
    render_html.add_argument(
        "--sample-board-count",
        type=int,
        default=0,
        help="fill the board to this row count with deterministic sample lanes for layout testing",
    )

    list_cmd = subparsers.add_parser(
        "list",
        help="list artifacts under the current artifact root",
        description="List artifacts with optional type/scene/status filters.",
    )
    list_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    list_cmd.add_argument("--type", dest="artifact_type")
    list_cmd.add_argument("--scene")
    list_cmd.add_argument("--status")
    list_cmd.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable JSON envelope instead of plain text",
    )

    show = subparsers.add_parser(
        "show",
        help="show artifacts for one artifact id",
        description="Show one artifact id, optionally narrowed by artifact type.",
    )
    show.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    show.add_argument("--id", dest="artifact_id", required=True)
    show.add_argument("--type", dest="artifact_type")
    show.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable JSON envelope instead of plain text",
    )

    lint = subparsers.add_parser(
        "lint",
        help="lint the artifact root",
        description="Validate artifact files under the current artifact root.",
    )
    lint.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")

    watch_cmd = subparsers.add_parser(
        "watch",
        help="record a tool on the radar before formal evaluation",
        description="Create a watch-note. Scene lane is optional at this stage.",
    )
    watch_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(watch_cmd)
    watch_cmd.add_argument("--candidate", required=True)
    watch_cmd.add_argument("--interest-reason", required=True)
    _scene_arg(watch_cmd, required=False, default="", help_text="optional scene lane if already known")

    block_cmd = subparsers.add_parser(
        "block",
        help="block a proposed adoption on an external constraint",
        description="Create a blocked-note. Requires an existing candidate-intake-note for the scene.",
    )
    block_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(block_cmd)
    _scene_arg(block_cmd, required=True, help_text="scene lane to block")
    block_cmd.add_argument("--block-reason", required=True)
    block_cmd.add_argument("--unblock-condition", required=True)
    block_cmd.add_argument("--owner", required=True)

    unblock_cmd = subparsers.add_parser(
        "unblock",
        help="lift a block and re-enter proposed state",
        description="Create a new candidate-intake-note from blocked state.",
    )
    unblock_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(unblock_cmd)
    _scene_arg(unblock_cmd, required=True, help_text="scene lane to unblock")
    unblock_cmd.add_argument("--why-unblocked", required=True)

    deprecate_cmd = subparsers.add_parser(
        "deprecate",
        help="begin retirement of a promoted tool",
        description="Create a deprecation-note. Requires an existing promotion-note for the scene.",
    )
    deprecate_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(deprecate_cmd)
    _scene_arg(deprecate_cmd, required=True, help_text="scene lane to retire")
    deprecate_cmd.add_argument("--retirement-reason", required=True)
    deprecate_cmd.add_argument("--replacement-candidate", dest="replacement_candidates", action="append", required=True)
    deprecate_cmd.add_argument("--timeline", required=True)

    migrate_cmd = subparsers.add_parser(
        "migrate",
        help="start active migration away from a deprecated tool",
        description="Create a migration-note. Requires an existing deprecation-note for the scene.",
    )
    migrate_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(migrate_cmd)
    _scene_arg(migrate_cmd, required=True, help_text="scene lane to migrate")
    migrate_cmd.add_argument("--migration-target", required=True)
    migrate_cmd.add_argument("--migration-plan", required=True)

    archive_cmd = subparsers.add_parser(
        "archive",
        help="mark a tool as fully archived for this scene lane",
        description="Create an archive-note. Requires an existing deprecation-note or migration-note.",
    )
    archive_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(archive_cmd)
    _scene_arg(archive_cmd, required=True, help_text="scene lane to archive")
    archive_cmd.add_argument("--end-date", required=True)
    archive_cmd.add_argument("--successor-tool", default="")

    couple_cmd = subparsers.add_parser(
        "couple",
        help="record how an external tool is entangled with project files",
        description=(
            "Create a coupling-note: a complete snapshot of which files the tool is\n"
            "entangled with, how (coupling_type), and how hard each is to detach\n"
            "(removal_cost). Each call records the CURRENT full coupling set; the report\n"
            "uses the latest coupling-note per scene/tool snapshot.\n\n"
            "Provide couplings either as repeated --couple 'PATH|TYPE|COST[|NOTE]'\n"
            "or as --couplings-json (a JSON list; @path reads a file).\n"
            f"  TYPE one of: {', '.join(COUPLING_TYPES)}\n"
            f"  COST one of: {', '.join(REMOVAL_COSTS)}"
        ),
        formatter_class=RawTextHelpFormatter,
    )
    couple_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(couple_cmd)
    _scene_arg(couple_cmd, required=True, help_text="scene lane this coupling snapshot belongs to")
    couple_cmd.add_argument("--tool", required=True)
    couple_cmd.add_argument(
        "--couple", dest="couples", action="append", default=[],
        metavar="PATH|TYPE|COST[|NOTE]",
        help="one coupling entry, pipe-delimited; repeatable",
    )
    couple_cmd.add_argument("--couplings-json", default="")

    couplings_cmd = subparsers.add_parser(
        "couplings",
        help="report tool-to-file entanglement (latest coupling-note per scene/tool snapshot)",
        description="Report declared tool-to-file couplings and their detachment cost.",
    )
    couplings_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    _project_boundary_args(couplings_cmd)
    _scene_arg(couplings_cmd, required=False, default=None, help_text="filter to one scene lane")
    couplings_cmd.add_argument("--json", action="store_true")

    # ── Usability commands (no --artifact-root required on first run) ──────────
    init_cmd = subparsers.add_parser(
        "init",
        help="scaffold artifact root and overlay file (run once per project)",
        description="Create .adop/ artifact root and a project-local overlay stub.",
    )
    init_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    init_cmd.add_argument(
        "--overlay",
        default="adop-overlay.md",
        metavar="FILE",
        help="path for overlay file (default: adop-overlay.md)",
    )

    status_cmd = subparsers.add_parser(
        "status",
        help="show current lifecycle state per scene and next steps",
        description="Print the current lifecycle state for each tracked scene lane.",
    )
    status_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")

    scan_cmd = subparsers.add_parser(
        "scan",
        help="static-analyse project files to detect tool couplings",
        description="Scan a directory for references to a tool, optionally excluding paths or recording a coupling snapshot.",
    )
    scan_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")
    scan_cmd.add_argument("--target", required=True, metavar="DIR", help="directory to scan")
    scan_cmd.add_argument("--tool", required=True, help="tool name to detect (case-insensitive)")
    _scene_arg(scan_cmd, required=False, default=None, metavar="SCENE", help_text="optional scene lane label for the resulting coupling note")
    scan_cmd.add_argument(
        "--exclude",
        dest="excludes",
        action="append",
        default=[],
        metavar="PATH",
        help="path prefix or glob to skip; repeatable",
    )
    scan_cmd.add_argument("--record", action="store_true", help="write the detected coupling set as a coupling-note")
    scan_cmd.add_argument("--json", action="store_true", help="emit raw JSON coupling list")

    next_cmd = subparsers.add_parser(
        "next",
        help="show recommended next action for the most active scene lane",
        description="Print the single next recommended CLI command for each pending scene lane.",
    )
    next_cmd.add_argument("--artifact-root", default=_DEFAULT_ARTIFACT_ROOT, metavar="DIR")

    return parser


def _handle_intake(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    _ensure_scene_not_rejected(root, args.scene, command="intake")
    artifact_id = next_sequential_id(root, "ci")
    data_flow = _parse_json_arg(args.data_flow_json, "data_flow_json")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": CANDIDATE_INTAKE_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "recording_mode": getattr(args, "recording_mode", "explicit"),
        "recording_source": getattr(args, "recording_source", "manual-cli"),
        "candidate_or_tool": args.candidate,
        "candidate_shape": args.candidate_shape,
        "source": args.source,
        "related_scene": args.scene,
        "intended_lane": args.lane,
        "intake_reason": args.reason,
        "current_disposition": PROPOSED,
        "next_action": "compare candidate set",
        ROOT_CAUSE_HYPOTHESIS: args.root_cause_hypothesis,
        "platform": args.platform,
        "license": args.license,
        "cost": args.cost,
        "version": args.version,
        "category": args.category,
        "ai_compatibility": args.ai_compatibility,
        "data_flow": data_flow,
    }
    validate_intake_payload(payload)
    path = artifacts.write_artifact(root, CANDIDATE_INTAKE_NOTE, artifact_id, payload)
    return artifacts.json_response("intake", "ok", [path.name], [])


def _handle_compare(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    _ensure_scene_not_rejected(root, args.scene, command="compare")
    if len(args.candidates) < 2 or len(args.candidates) > 3:
        raise AdopValidationError("candidate must appear 2-3 times")
    if args.selected not in args.candidates:
        raise AdopValidationError("selected candidate must be in candidate list")
    parent = artifacts.latest_by_type(root, CANDIDATE_INTAKE_NOTE, scene=args.scene)
    if not parent:
        raise AdopValidationError("candidate-intake-note for scene not found", 5)
    target_project_profile = _parse_json_arg(args.target_project_profile_json, "target_project_profile_json")
    compatibility_diagnosis = _parse_json_arg(args.compatibility_diagnosis_json, "compatibility_diagnosis_json")
    no_impact_envelope = (
        _parse_json_arg(args.no_impact_envelope_json, "no_impact_envelope_json")
        if args.no_impact_envelope_json
        else _no_impact_envelope_default()
    )
    recommended_fit_lane = ""
    for item in compatibility_diagnosis:
        if isinstance(item, dict) and str(item.get("adoption_unit")) == args.adoption_unit:
            recommended_fit_lane = str(item.get("recommended_fit_lane", ""))
            break
    if not recommended_fit_lane and compatibility_diagnosis and isinstance(compatibility_diagnosis[0], dict):
        recommended_fit_lane = str(compatibility_diagnosis[0].get("recommended_fit_lane", ""))
    artifact_id = next_sequential_id(root, "cmp")
    derived_from = [parent["artifact_id"]]
    hold_note = artifacts.latest_by_type(root, HOLD_NOTE, scene=args.scene)
    if hold_note:
        derived_from.append(hold_note["artifact_id"])
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": COMPARISON_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "recording_mode": getattr(args, "recording_mode", "explicit"),
        "recording_source": getattr(args, "recording_source", "manual-cli"),
        "related_scene": args.scene,
        "candidate_shape": args.candidate_shape,
        "derived_from": derived_from,
        "compared_candidates": args.candidates,
        "filter_assessment": _build_filter_assessment(args),
        "selected_candidate": args.selected,
        "decision_owner": args.owner,
        "discriminator": ["scene-fit", "authority-safe", "controlability"],
        "drawbacks": [],
        ROOT_CAUSE_HYPOTHESIS: args.root_cause_hypothesis,
        STRUCTURAL_GAP: args.structural_gap,
        "non_tool_alternative": args.non_tool_alternative,
        DECOMPOSITION_DECISION: args.decomposition_decision,
        "adoption_unit": args.adoption_unit,
        "discovered_subtargets": args.discovered_subtargets,
        "recommended_next_candidate": args.recommended_next_candidate,
        "target_project_profile": target_project_profile,
        "compatibility_diagnosis": compatibility_diagnosis,
        "recommended_fit_lane": recommended_fit_lane,
        "no_impact_envelope": no_impact_envelope,
        "selection_reason": f"selected {args.selected} for bounded trial",
        "rejected_reasons": [],
    }
    validate_comparison_payload(payload)
    path = artifacts.write_artifact(root, COMPARISON_NOTE, artifact_id, payload)
    return artifacts.json_response("compare", "ok", [path.name], [])


def _handle_start_trial(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    _ensure_scene_not_rejected(root, args.scene, command="start-trial")
    comparison = None
    if args.derived_from:
        for item in artifacts.find_by_type(root, COMPARISON_NOTE):
            if item["artifact_id"] == args.derived_from:
                comparison = item
                break
    else:
        comparison = artifacts.latest_by_type(root, COMPARISON_NOTE, scene=args.scene)
    if not comparison:
        raise AdopValidationError("comparison-note for scene not found", 5)
    if not comparison_ready_for_trial(comparison):
        raise AdopValidationError("comparison is not trial-ready; cannot start trial", 7)
    base_payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": TRIAL_PACKET,
        "artifact_id": "",
        "status": "active",
        "created_at": today_iso(),
        "recording_mode": getattr(args, "recording_mode", "explicit"),
        "recording_source": getattr(args, "recording_source", "manual-cli"),
        "related_scene": args.scene,
        "candidate_shape": comparison["candidate_shape"],
        DECOMPOSITION_DECISION: comparison[DECOMPOSITION_DECISION],
        "adoption_unit": comparison["adoption_unit"],
        "derived_from": [comparison["artifact_id"]],
        "trial_type": args.trial_type,
        "sandbox_type": args.sandbox_type,
        "lane": args.lane,
        "input_surface": args.input_surface,
        "output_contract": args.output_contract,
        "mutation_boundary": args.mutation_boundary,
        "verification_method": args.verification_method,
        EXECUTOR: args.executor,
        "trigger": args.trigger,
        EVALUATION_GATE: args.evaluation_gate,
        "landing_target": args.landing_target,
        "writeback_target": args.writeback_target,
        "decision_owner": args.decision_owner,
        "fallback": args.fallback,
        "target_project_profile": comparison["target_project_profile"],
        "compatibility_diagnosis": comparison["compatibility_diagnosis"],
        "recommended_fit_lane": comparison["recommended_fit_lane"],
        "no_impact_envelope": comparison["no_impact_envelope"],
        "trigger_canonical_record": {
            "scene": args.scene,
            "friction_class": "",
            "observable_signal": args.trigger,
            "start_threshold": "",
            "stop_condition": args.evaluation_gate,
            "reopen_condition": "",
        },
        "code_level_compatibility": {
            "input_surface_fit": "provided",
            "output_contract_fit": "provided",
            "mutation_boundary_fit": "provided",
            "dependency_fit": "",
            "workflow_fit": "",
            "verification_fit": "provided",
            "failure_mode_fit": "",
        },
        "dependency_note": "",
        "failure_mode_hypothesis": [],
    }
    def _build_packet_payload(artifact_id: str) -> dict[str, Any]:
        payload = dict(base_payload)
        payload["artifact_id"] = artifact_id
        validate_trial_packet_payload(payload)
        validate_no_impact_trial_mode(payload, no_impact_default=not args.allow_project_impact)
        return payload

    # Reserve the id and write under exclusive lock so two concurrent start-trial
    # callers cannot mint the same tr- id (residual B13).
    _artifact_id, path = artifacts.write_next_sequential_artifact(
        root, TRIAL_PACKET, "tr", _build_packet_payload
    )
    return artifacts.json_response("start-trial", "ok", [path.name], [])


def _handle_close_trial(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    packet = artifacts.find_trial_packet(root, args.trial_id)
    if not packet:
        raise AdopValidationError("trial-packet not found", 5)
    # Detect double-close before building any payloads (exit 5 = readiness gate).
    if any(str(r.get("artifact_id")) == args.trial_id for r in artifacts.find_by_type(root, TRIAL_RESULT)):
        raise AdopValidationError(f"trial {args.trial_id} already closed", 5)
    close_payload = {
        "verdict": args.verdict,
        OBSERVED_EFFECT: args.observed_effect,
        "judgment_reason": args.judgment_reason,
        "reopen_condition": args.reopen_condition,
        "next_action": args.next_action,
        "recurring_control_decision": args.recurring_control_decision,
        ROOT_CAUSE_HYPOTHESIS: args.root_cause_hypothesis,
        "preventive_action": args.preventive_actions,
        "why_this_problem_recurred": args.why_this_problem_recurred,
        "decision_owner": args.decision_owner or packet.get("decision_owner"),
        "landing_target": packet["landing_target"],
        "candidate_shape": packet["candidate_shape"],
        DECOMPOSITION_DECISION: packet[DECOMPOSITION_DECISION],
        "adoption_unit": packet["adoption_unit"],
        "target_project_profile": packet["target_project_profile"],
        "compatibility_diagnosis": packet["compatibility_diagnosis"],
        "recommended_fit_lane": packet["recommended_fit_lane"],
        "no_impact_envelope": packet["no_impact_envelope"],
    }
    validate_close_payload(close_payload)
    if args.verdict == "promote":
        latest_intake = artifacts.latest_by_type(root, CANDIDATE_INTAKE_NOTE, scene=str(packet.get("related_scene", "")))
        if not latest_intake:
            raise AdopValidationError("promote requires candidate-intake-note history", 7)
        unknowns = unknown_tool_attribute_fields(latest_intake)
        if unknowns:
            raise AdopValidationError(
                "promote requires known tool attributes in the latest intake: " + ", ".join(unknowns),
                7,
            )
    promote_errors = promote_gate_errors(packet, close_payload)
    if promote_errors:
        raise AdopValidationError("; ".join(promote_errors), 7)

    comparison = None
    derived_from = packet.get("derived_from", [])
    if derived_from:
        cmp_id = str(derived_from[0])
        for item in artifacts.find_by_type(root, COMPARISON_NOTE):
            if item.get("artifact_id") == cmp_id:
                comparison = item
                break

    created_at = today_iso()
    result_payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": TRIAL_RESULT,
        "artifact_id": args.trial_id,
        "status": "closed",
        "created_at": packet["created_at"],
        "closed_at": created_at,
        "recording_mode": getattr(args, "recording_mode", "explicit"),
        "recording_source": getattr(args, "recording_source", "manual-cli"),
        "related_scene": packet["related_scene"],
        "derived_from": [packet["artifact_id"]],
        "trial_type": packet["trial_type"],
        "sandbox_type": packet["sandbox_type"],
        "input_surface": packet["input_surface"],
        "output_contract": packet["output_contract"],
        "mutation_boundary": packet["mutation_boundary"],
        "verification_method": packet["verification_method"],
        "decision_owner": args.decision_owner or packet.get("decision_owner"),
        "landing_target": packet["landing_target"],
        OBSERVED_EFFECT: args.observed_effect,
        "evidence_refs": args.evidence_refs,
        "code_level_compatibility_summary": (
            f"input={packet['input_surface']}; output={packet['output_contract']}; "
            f"mutation={packet['mutation_boundary']}; verification={packet['verification_method']}"
        ),
        "failure_observed": [],
        "writeback_performed": [packet["writeback_target"]],
    }
    judgment_payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": JUDGMENT_REPORT,
        "artifact_id": args.trial_id,
        "status": "closed",
        "created_at": packet["created_at"],
        "closed_at": created_at,
        "recording_mode": getattr(args, "recording_mode", "explicit"),
        "recording_source": getattr(args, "recording_source", "manual-cli"),
        "related_scene": packet["related_scene"],
        "derived_from": [packet["artifact_id"]],
        "related_artifacts": [packet["artifact_id"], args.trial_id],
        "candidate_or_tool": (comparison or {}).get("selected_candidate", packet["related_scene"]),
        "candidate_shape": packet["candidate_shape"],
        DECOMPOSITION_DECISION: packet[DECOMPOSITION_DECISION],
        "adoption_unit": packet["adoption_unit"],
        "target_project_profile": packet["target_project_profile"],
        "compatibility_diagnosis": packet["compatibility_diagnosis"],
        "recommended_fit_lane": packet["recommended_fit_lane"],
        "no_impact_envelope": packet["no_impact_envelope"],
        "verdict": args.verdict,
        "decision_owner": args.decision_owner or packet.get("decision_owner"),
        "landing_target": packet["landing_target"],
        "recurring_control_decision": args.recurring_control_decision,
        "judgment_reason": args.judgment_reason,
        "observed_effect_summary": args.observed_effect,
        "code_level_compatibility_summary": result_payload["code_level_compatibility_summary"],
        ROOT_CAUSE_HYPOTHESIS: args.root_cause_hypothesis,
        "preventive_action": args.preventive_actions,
        "why_this_problem_recurred": args.why_this_problem_recurred,
        "writeback_artifact": [packet["writeback_target"]],
        "reopen_condition": args.reopen_condition,
        "next_action": args.next_action,
    }
    # Build the full 2-3 artifact set first, then commit it as one bounded group
    # so a failure does not leave a half-written close set (residual B14).
    group_specs: list[tuple[str, str, dict[str, Any]]] = [
        (TRIAL_RESULT, args.trial_id, result_payload),
        (JUDGMENT_REPORT, args.trial_id, judgment_payload),
    ]

    if args.verdict == "hold":
        hold_id = next_sequential_id(root, "hl")
        hold_payload = {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": HOLD_NOTE,
            "artifact_id": hold_id,
            "status": "closed",
            "created_at": created_at,
            "recording_mode": getattr(args, "recording_mode", "explicit"),
            "recording_source": getattr(args, "recording_source", "manual-cli"),
            "related_scene": packet["related_scene"],
            "derived_from": [args.trial_id],
            "decision_owner": args.decision_owner or packet.get("decision_owner"),
            "hold_reason": args.judgment_reason,
            "reopen_condition": args.reopen_condition,
            "evidence_refs": args.evidence_refs,
        }
        group_specs.append((HOLD_NOTE, hold_id, hold_payload))
    elif args.verdict == "reject":
        reject_id = next_sequential_id(root, "rj")
        reject_payload = {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": REJECT_NOTE,
            "artifact_id": reject_id,
            "status": "closed",
            "created_at": created_at,
            "recording_mode": getattr(args, "recording_mode", "explicit"),
            "recording_source": getattr(args, "recording_source", "manual-cli"),
            "related_scene": packet["related_scene"],
            "derived_from": [args.trial_id],
            "decision_owner": args.decision_owner or packet.get("decision_owner"),
            "reject_reason": args.judgment_reason,
            "evidence_refs": args.evidence_refs,
            "drawbacks": [],
        }
        group_specs.append((REJECT_NOTE, reject_id, reject_payload))
    elif args.verdict == "promote":
        promotion_id = next_sequential_id(root, "pm")
        promotion_payload = {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": PROMOTION_NOTE,
            "artifact_id": promotion_id,
            "status": "closed",
            "created_at": created_at,
            "recording_mode": getattr(args, "recording_mode", "explicit"),
            "recording_source": getattr(args, "recording_source", "manual-cli"),
            "related_scene": packet["related_scene"],
            "derived_from": [args.trial_id],
            "decision_owner": args.decision_owner or packet.get("decision_owner"),
            "repeated_effect": args.observed_effect,
            "trigger_canonical_record": packet.get("trigger_canonical_record", {}),
            LANDING_TARGET: packet["landing_target"],
            "minimum_bake_duration": "n/a",
            "reversal_test": "not run",
        }
        group_specs.append((PROMOTION_NOTE, promotion_id, promotion_payload))

    committed = artifacts.write_artifact_group(root, group_specs)
    artifact_refs = [path.name for path in committed]
    return artifacts.json_response("close-trial", "ok", artifact_refs, [])


def _handle_watch(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    if args.scene:
        _ensure_scene_not_rejected(root, args.scene, command="watch")
    artifact_id = next_sequential_id(root, "wt")
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": WATCH_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "candidate_or_tool": args.candidate,
        "interest_reason": args.interest_reason,
    }
    if args.scene:
        payload["related_scene"] = args.scene
    validate_watch_note_payload(payload)
    path = artifacts.write_artifact(root, WATCH_NOTE, artifact_id, payload)
    return artifacts.json_response("watch", "ok", [path.name], [])


def _handle_block(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    _ensure_scene_not_rejected(root, args.scene, command="block")
    parent = artifacts.latest_by_type(root, CANDIDATE_INTAKE_NOTE, scene=args.scene)
    if not parent:
        raise AdopValidationError("candidate-intake-note for scene not found", 5)
    artifact_id = next_sequential_id(root, "bl")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": BLOCKED_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "related_scene": args.scene,
        "candidate_or_tool": str(parent.get("candidate_or_tool", "")),
        "derived_from": [parent["artifact_id"]],
        "block_reason": args.block_reason,
        "unblock_condition": args.unblock_condition,
        "owner": args.owner,
    }
    validate_blocked_note_payload(payload)
    path = artifacts.write_artifact(root, BLOCKED_NOTE, artifact_id, payload)
    return artifacts.json_response("block", "ok", [path.name], [])


def _handle_unblock(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    _ensure_scene_not_rejected(root, args.scene, command="unblock")
    blocked = artifacts.latest_by_type(root, BLOCKED_NOTE, scene=args.scene)
    if not blocked:
        raise AdopValidationError("blocked-note for scene not found", 5)
    artifact_id = next_sequential_id(root, "ci")
    prior_intake = artifacts.latest_by_type(root, CANDIDATE_INTAKE_NOTE, scene=args.scene)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": CANDIDATE_INTAKE_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "recording_mode": "explicit",
        "recording_source": "unblock",
        "related_scene": args.scene,
        "candidate_or_tool": str(blocked.get("candidate_or_tool", "")),
        "source": "unblock",
        "intended_lane": LANES[1],
        "intake_reason": args.why_unblocked,
        "current_disposition": PROPOSED,
        "candidate_shape": str(prior_intake.get("candidate_shape", "unknown")) if prior_intake else "unknown",
        "next_action": "compare candidate set",
        ROOT_CAUSE_HYPOTHESIS: args.why_unblocked,
        "derived_from": [blocked["artifact_id"]],
        "platform": str((prior_intake or {}).get("platform", _default_tool_attributes()["platform"])),
        "license": str((prior_intake or {}).get("license", _default_tool_attributes()["license"])),
        "cost": str((prior_intake or {}).get("cost", _default_tool_attributes()["cost"])),
        "version": str((prior_intake or {}).get("version", _default_tool_attributes()["version"])),
        "category": str((prior_intake or {}).get("category", _default_tool_attributes()["category"])),
        "ai_compatibility": str((prior_intake or {}).get("ai_compatibility", _default_tool_attributes()["ai_compatibility"])),
        "data_flow": (prior_intake or {}).get("data_flow", _default_tool_attributes()["data_flow"]),
    }
    validate_intake_payload(payload)
    path = artifacts.write_artifact(root, CANDIDATE_INTAKE_NOTE, artifact_id, payload)
    return artifacts.json_response("unblock", "ok", [path.name], [])


def _handle_deprecate(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    parent = artifacts.latest_by_type(root, PROMOTION_NOTE, scene=args.scene)
    if not parent:
        raise AdopValidationError("promotion-note for scene not found; tool must be promoted before deprecation", 5)
    cmp = artifacts.latest_by_type(root, COMPARISON_NOTE, scene=args.scene)
    intake = artifacts.latest_by_type(root, CANDIDATE_INTAKE_NOTE, scene=args.scene)
    tool_name = (cmp or {}).get("selected_candidate") or str((intake or {}).get("candidate_or_tool", ""))
    artifact_id = next_sequential_id(root, "dp")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": DEPRECATION_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "related_scene": args.scene,
        "candidate_or_tool": tool_name,
        "derived_from": [parent["artifact_id"]],
        "retirement_reason": args.retirement_reason,
        "replacement_candidates": args.replacement_candidates,
        "timeline": args.timeline,
    }
    validate_deprecation_note_payload(payload)
    path = artifacts.write_artifact(root, DEPRECATION_NOTE, artifact_id, payload)
    return artifacts.json_response("deprecate", "ok", [path.name], [])


def _handle_migrate(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    parent = artifacts.latest_by_type(root, DEPRECATION_NOTE, scene=args.scene)
    if not parent:
        raise AdopValidationError("deprecation-note for scene not found; tool must be deprecated before migration", 5)
    artifact_id = next_sequential_id(root, "mg")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": MIGRATION_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "related_scene": args.scene,
        "candidate_or_tool": str(parent.get("candidate_or_tool", "")),
        "derived_from": [parent["artifact_id"]],
        "migration_target": args.migration_target,
        "migration_plan": args.migration_plan,
    }
    validate_migration_note_payload(payload)
    path = artifacts.write_artifact(root, MIGRATION_NOTE, artifact_id, payload)
    return artifacts.json_response("migrate", "ok", [path.name], [])


def _handle_archive(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    migration = artifacts.latest_by_type(root, MIGRATION_NOTE, scene=args.scene)
    deprecation = artifacts.latest_by_type(root, DEPRECATION_NOTE, scene=args.scene)
    parent = migration or deprecation
    if not parent:
        raise AdopValidationError(
            "deprecation-note or migration-note for scene not found; tool must be deprecated before archiving", 5
        )
    artifact_id = next_sequential_id(root, "ar")
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": ARCHIVE_NOTE,
        "artifact_id": artifact_id,
        "status": "closed",
        "created_at": today_iso(),
        "related_scene": args.scene,
        "candidate_or_tool": str(parent.get("candidate_or_tool", "")),
        "derived_from": [parent["artifact_id"]],
        "end_date": args.end_date,
    }
    if args.successor_tool:
        payload["successor_tool"] = args.successor_tool
    validate_archive_note_payload(payload)
    path = artifacts.write_artifact(root, ARCHIVE_NOTE, artifact_id, payload)
    return artifacts.json_response("archive", "ok", [path.name], [])


def _parse_couple_entry(raw: str) -> dict[str, Any]:
    parts = raw.split("|", 3)  # PATH|TYPE|COST[|NOTE]
    if len(parts) < 3:
        raise AdopValidationError(f"--couple must be 'PATH|TYPE|COST[|NOTE]': {raw}", 2)
    entry: dict[str, Any] = {
        "path": parts[0].strip(),
        "coupling_type": parts[1].strip(),
        "removal_cost": parts[2].strip(),
    }
    if len(parts) == 4 and parts[3].strip():
        entry["note"] = parts[3].strip()
    return entry


def _handle_couple(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    couplings: list[dict[str, Any]] = []
    if args.couplings_json:
        parsed = _parse_json_arg(args.couplings_json, "couplings-json")
        if not isinstance(parsed, list):
            raise AdopValidationError("couplings-json must be a JSON list", 2)
        couplings.extend(parsed)
    couplings.extend(_parse_couple_entry(raw) for raw in args.couples)
    path = _write_coupling_note(root, scene=args.scene, tool=args.tool, couplings=couplings)
    return artifacts.json_response("couple", "ok", [path.name], [])


# Detachment severity: clean < edit < entangled (index in REMOVAL_COSTS is the rank).
_COST_SEVERITY = {cost: rank for rank, cost in enumerate(REMOVAL_COSTS)}


def _worst_removal_cost(couplings: list[dict[str, Any]]) -> str:
    return max(
        (str(c.get("removal_cost", REMOVAL_COSTS[0])) for c in couplings),
        key=lambda cost: _COST_SEVERITY.get(cost, 0),
        default=REMOVAL_COSTS[0],
    )


def _latest_coupling_notes(root: Path, scene: str | None) -> list[dict[str, Any]]:
    """Latest coupling-note per (tool, scene) — each note is a full snapshot."""
    notes = [
        item for item in artifacts.load_all_artifacts(root)
        if item.get("artifact_type") == COUPLING_NOTE
        and (scene is None or str(item.get("related_scene", "")) == scene)
    ]
    notes.sort(key=lambda n: parse_numeric_id(str(n.get("artifact_id", "")), "cp") or 0)
    latest: dict[tuple[str, str], dict[str, Any]] = {}
    for note in notes:
        key = (str(note.get("related_scene", "")), str(note.get("candidate_or_tool", "")))
        latest[key] = note  # higher id wins
    return [latest[key] for key in sorted(latest)]


def _handle_couplings(args: argparse.Namespace) -> tuple[int, dict[str, Any] | str]:
    notes = _latest_coupling_notes(Path(args.artifact_root), args.scene)

    if getattr(args, "json", False):
        report = [
            {
                "tool": note.get("candidate_or_tool"),
                "scene": note.get("related_scene"),
                "file_count": len(note.get("couplings", [])),
                "max_removal_cost": _worst_removal_cost(note.get("couplings", [])),
                "couplings": note.get("couplings", []),
            }
            for note in notes
        ]
        return 0, {
            "schema_version": SCHEMA_VERSION,
            "command": "couplings",
            "status": "ok",
            "count": len(report),
            "report": report,
        }

    if not notes:
        return 0, "ADOP Coupling Report\n(no couplings recorded)"
    lines = ["ADOP Coupling Report"]
    for note in notes:
        couplings = note.get("couplings", [])
        lines.append(
            f"{note.get('candidate_or_tool', '-')} @ {note.get('related_scene', '-')} "
            f"— {len(couplings)} file(s), detachment: {_worst_removal_cost(couplings)}"
        )
        for entry in couplings:
            lines.append(
                f"- {entry.get('path', '-')} "
                f"[{entry.get('coupling_type', '-')}, {entry.get('removal_cost', '-')}]{_format_detection_suffix(entry)}"
            )
    return 0, "\n".join(lines)


def _handle_summary(args: argparse.Namespace) -> str:
    return build_summary(Path(args.artifact_root), scene=args.scene, status=args.status)


def _handle_render_html(args: argparse.Namespace) -> str:
    html = render_dashboard_html(
        Path(args.artifact_root),
        title=args.title,
        selected_scene=args.scene,
        sample_board_count=max(0, int(args.sample_board_count)),
    )
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    return f"Rendered HTML dashboard to {output_path}"


def _handle_quick_intake(args: argparse.Namespace) -> dict[str, Any]:
    defaults = _default_tool_attributes()
    if not args.root_cause_hypothesis:
        args.root_cause_hypothesis = args.why_now
    args.platform = _normalize_platform_value(args.platform or defaults["platform"])
    args.license = args.license or defaults["license"]
    args.cost = args.cost or defaults["cost"]
    args.version = args.version or defaults["version"]
    args.category = args.category or defaults["category"]
    args.ai_compatibility = args.ai_compatibility or defaults["ai_compatibility"]
    if not args.data_flow_json:
        args.data_flow_json = json.dumps(defaults["data_flow"], ensure_ascii=False)
    args.recording_mode = "guided"
    args.recording_source = "quick-intake"
    args.reason = args.why_now
    return _handle_intake(args)


def _handle_quick_compare(args: argparse.Namespace) -> dict[str, Any]:
    if len(args.candidates) < 2 or len(args.candidates) > 3:
        raise AdopValidationError("candidate must appear 2-3 times", 2)
    args.decomposition_decision = DECOMPOSITION_DECISIONS[0]
    args.discovered_subtargets = []
    args.recommended_next_candidate = ""
    args.owner = None
    args.adoption_unit = args.adoption_unit or args.selected
    args.root_cause_hypothesis = args.root_cause_hypothesis or f"the use case '{args.scene}' still depends on ad hoc operator judgment"
    if not args.target_project_profile_json:
        args.target_project_profile_json = json.dumps(_simple_project_profile_default(), ensure_ascii=False)
    if not args.compatibility_diagnosis_json:
        args.compatibility_diagnosis_json = json.dumps(
            _simple_compatibility_diagnosis_default(args.adoption_unit),
            ensure_ascii=False,
        )
    if not args.no_impact_envelope_json:
        args.no_impact_envelope_json = json.dumps(_no_impact_envelope_default(), ensure_ascii=False)
    args.scene_fit_status = FILTER_STATUSES[0]
    args.scene_fit_reason = "one bounded scene lane"
    args.scene_fit_constraint = None
    args.authority_safe_status = FILTER_STATUSES[1]
    args.authority_safe_reason = "safe when reviewed before writeback"
    args.authority_safe_constraint = "review before writeback"
    args.controlability_status = FILTER_STATUSES[0]
    args.controlability_reason = "bounded trial possible"
    args.controlability_constraint = None
    args.recording_mode = "guided"
    args.recording_source = "quick-compare"
    return _handle_compare(args)


def _handle_quick_trial(args: argparse.Namespace) -> dict[str, Any]:
    preset = _simple_trial_preset(args.mode)
    args.derived_from = None
    args.trial_type = preset["trial_type"]
    args.sandbox_type = preset["sandbox_type"]
    args.lane = preset["lane"]
    args.input_surface = preset["input_surface"]
    args.output_contract = preset["output_contract"]
    args.mutation_boundary = preset["mutation_boundary"]
    args.verification_method = preset["verification_method"]
    args.trigger = args.trigger or preset["trigger"]
    args.evaluation_gate = args.evaluation_gate or preset["evaluation_gate"]
    args.writeback_target = args.writeback_target or preset["writeback_target"]
    args.decision_owner = args.decision_owner
    args.fallback = args.fallback or preset["fallback"]
    args.recording_mode = "guided"
    args.recording_source = "quick-trial"
    return _handle_start_trial(args)


def _handle_quick_close_trial(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    packet = artifacts.find_trial_packet(root, args.trial_id)
    if not packet:
        raise AdopValidationError("trial-packet not found", 5)
    if args.verdict == VERDICTS[0]:
        missing: list[str] = []
        if not args.judgment_reason.strip():
            missing.append("--judgment-reason")
        if not args.next_action.strip():
            missing.append("--next-action")
        if not args.recurring_control_decision.strip():
            missing.append("--recurring-control-decision")
        if not args.root_cause_hypothesis.strip():
            missing.append("--root-cause-hypothesis")
        if not args.preventive_actions:
            missing.append("--preventive-action")
        if not args.why_this_problem_recurred.strip():
            missing.append("--why-this-problem-recurred")
        if missing:
            raise AdopValidationError(
                "quick-close-trial promote requires explicit fields: " + ", ".join(missing),
                2,
            )
    else:
        preset = _simple_close_preset(args.verdict)
        args.judgment_reason = args.judgment_reason or preset["judgment_reason"]
        args.next_action = args.next_action or preset["next_action"]
        args.recurring_control_decision = (
            args.recurring_control_decision or preset["recurring_control_decision"]
        )
        args.reopen_condition = args.reopen_condition or preset["reopen_condition"]
        args.preventive_actions = args.preventive_actions or list(preset["preventive_actions"])
        args.why_this_problem_recurred = (
            args.why_this_problem_recurred or preset["why_this_problem_recurred"]
        )
    args.decision_owner = None
    args.evidence_refs = []
    args.root_cause_hypothesis = (
        args.root_cause_hypothesis
        or f"the bounded scene '{packet['related_scene']}' needed a more explicit helper path"
    )
    args.recording_mode = "guided"
    args.recording_source = "quick-close-trial"
    return _handle_close_trial(args)


def _handle_init(args: argparse.Namespace) -> str:
    root = Path(args.artifact_root)
    created_root = not root.exists()
    root.mkdir(parents=True, exist_ok=True)

    overlay_path = Path(args.overlay)
    created_overlay = not overlay_path.exists()
    if created_overlay:
        candidates = (
            Path(__file__).parent.parent / "templates" / "project-local-adop-overlay-template.md",
            Path(sys.prefix) / "share" / "adop" / "templates" / "project-local-adop-overlay-template.md",
        )
        for candidate in candidates:
            if candidate.exists():
                shutil.copy(candidate, overlay_path)
                break
        else:
            overlay_path.write_text(_OVERLAY_INIT_STUB, encoding="utf-8")

    lines = ["ADOP initialized.", ""]
    lines.append(f"  Artifact root : {root}/{'  (created)' if created_root else '  (already exists)'}")
    lines.append(f"  Overlay file  : {overlay_path}{'  (created)' if created_overlay else '  (already exists)'}")
    lines += [
        "",
        "Next steps:",
        '  adop watch --candidate <tool> --interest-reason "watching to evaluate"',
        '  adop quick-intake --candidate <tool> --source doc --scene <scene> --why-now "<reason>"',
        '  adop status',
    ]
    return "\n".join(lines)


def _handle_status(args: argparse.Namespace) -> str:
    root = _root_path(args)
    scene_states = get_scene_states(root)
    items = artifacts.load_all_artifacts(root)

    lines = [f"ADOP  ({root}/)", ""]

    if not scene_states:
        lines += [
            "No adoption records yet.",
            "",
            "Start with:",
            '  adop quick-intake --candidate <tool> --source doc --scene <scene> --why-now "<reason>"',
        ]
        return "\n".join(lines)

    col = max(len(k) for k in scene_states) + 2
    action_needed: list[tuple[str, str, str]] = []
    for label, state in sorted(scene_states.items()):
        lines.append(f"  {label:<{col}} {state}")
        cmd = _next_step(label, state, root, items)
        if cmd and state not in ("promote", "archived", "reject"):
            action_needed.append((label, state, cmd))

    coupling_notes = [i for i in items if i.get("artifact_type") == COUPLING_NOTE]
    if coupling_notes:
        lines += ["", "Couplings:"]
        latest_cp: dict[tuple[str, str], dict[str, Any]] = {}
        for note in coupling_notes:
            key = (str(note.get("related_scene", "")), str(note.get("candidate_or_tool", "")))
            latest_cp[key] = note
        for (sc, tool), note in sorted(latest_cp.items()):
            entries = note.get("couplings", [])
            worst = _worst_removal_cost(entries)
            lines.append(f"  {tool} @ {sc}: {len(entries)} file(s), max detachment: {worst}")
    else:
        tool_hint = next(
            (str(i.get("candidate_or_tool", "<tool>")) for i in items if i.get("candidate_or_tool")),
            "<tool>",
        )
        scene_hint = next(iter(sorted(scene_states)), "<scene>")
        lines += [
            "",
            "No couplings recorded.",
            f"  -> adop scan --target . --tool {tool_hint} --scene {scene_hint} --record",
        ]

    if action_needed:
        lines += ["", "Next steps:"]
        for label, _, cmd in action_needed[:3]:
            lines.append(f"  [{label}]")
            lines.append(f"    {cmd}")

    return "\n".join(lines)


def _handle_scan(args: argparse.Namespace) -> tuple[int, str]:
    target = Path(args.target)
    if not target.is_dir():
        raise AdopValidationError(f"scan target is not a directory: {target}", 2)
    excludes = [_normalize_scan_pattern(raw) for raw in getattr(args, "excludes", []) if str(raw).strip()]
    scene = getattr(args, "scene", None) or "<scene>"
    couplings = _scan_target_for_tool(target, args.tool, excludes)
    artifact_ref = ""

    if not couplings:
        if getattr(args, "record", False):
            return 0, f"No references to '{args.tool}' found in {target}/\nNo coupling note was written."
        return 0, f"No references to '{args.tool}' found in {target}/"

    if getattr(args, "record", False):
        if getattr(args, "scene", None) is None:
            raise AdopValidationError("scan --record requires --scene", 2)
        root = _prepare_artifact_root(args)
        artifact_ref = _write_coupling_note(root, scene=args.scene, tool=args.tool, couplings=couplings).name

    if getattr(args, "json", False):
        if artifact_ref:
            return 0, json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "command": "scan",
                    "status": "ok",
                    "count": len(couplings),
                    "artifact_refs": [artifact_ref],
                    "couplings": couplings,
                },
                ensure_ascii=False,
                indent=2,
            )
        return 0, json.dumps(couplings, ensure_ascii=False, indent=2)

    lines = [f"Detected {len(couplings)} coupling(s) for '{args.tool}' in {target}/", ""]
    if excludes:
        lines += [f"Excluded paths: {', '.join(excludes)}", ""]
    for entry in couplings:
        lines.append(
            f"  {entry['path']} [{entry['coupling_type']}, {entry['removal_cost']}]"
            f"{_format_detection_suffix(entry)}"
        )
    if artifact_ref:
        lines += ["", f"Recorded coupling snapshot: {artifact_ref}"]
        return 0, "\n".join(lines)

    lines += ["", "Scan output is advisory only. No canonical artifact is written until `adop couple` or `adop scan --record` runs.", ""]
    direct = [f"adop scan --target {args.target} --tool {args.tool}"]
    if getattr(args, "scene", None):
        direct.append(f"--scene {scene}")
    for excluded in excludes:
        direct.append(f"--exclude {excluded}")
    direct.append("--record")
    lines += ["Record directly next time:", f"  {' '.join(direct)}", "", "Or create a manual snapshot:", f"  adop couple --scene {scene} --tool {args.tool} \\"]
    for entry in couplings:
        np = f"|{entry['note']}" if entry.get("note") else ""
        lines.append(f"    --couple '{entry['path']}|{entry['coupling_type']}|{entry['removal_cost']}{np}' \\")
    lines += ["", "Or as JSON:", f"  adop scan --target {args.target} --tool {args.tool} --json > couplings.json"]
    lines.append(f"  adop couple --scene {scene} --tool {args.tool} --couplings-json @couplings.json")
    return 0, "\n".join(lines)


def _handle_next(args: argparse.Namespace) -> str:
    root = _root_path(args)
    scene_states = get_scene_states(root)
    items = artifacts.load_all_artifacts(root)

    if not scene_states:
        return 'No records yet — start: adop quick-intake --candidate <tool> --source doc --scene <scene> --why-now "<reason>"'

    terminal = {"promote", "archived", "reject"}
    priority = {"in-trial": 0, "proposed": 1, "trial-ready": 2, "watch": 3, "blocked": 4, "deprecated": 5, "migrating": 6}
    active = sorted(
        [(sc, st) for sc, st in scene_states.items() if st not in terminal],
        key=lambda x: (priority.get(x[1], 99), x[0]),
    )
    if not active:
        return "All scenes are in a terminal state (promote / archived / reject). Nothing pending."

    lines: list[str] = []
    for scene_label, state in active[:3]:
        cmd = _next_step(scene_label, state, root, items)
        if cmd:
            lines.append(f"[{scene_label}] ({state})")
            lines.append(f"  {cmd}")
    return "\n".join(lines) if lines else "No pending actions."


def _handle_lint(args: argparse.Namespace) -> tuple[int, str]:
    root = Path(args.artifact_root)
    if not root.exists():
        return 10, f"lint: error — artifact root does not exist: {root}"
    all_files = list(root.glob("adop_*_*.json"))
    if not all_files:
        return 10, f"lint: error — artifact root is empty: {root}"
    issues = lint_artifact_root(root)
    if issues:
        lines = ["lint: issues found"]
        for issue in issues:
            lines.append(f"  {issue}")
        return 10, "\n".join(lines)
    return 0, f"lint: ok ({len(all_files)} artifact(s) checked)"


def _artifact_numeric_sort_key(item: dict[str, Any]) -> tuple[str, int, int, str]:
    artifact_type = str(item.get("artifact_type", ""))
    raw_id = str(item.get("artifact_id", ""))
    prefix = raw_id.split("-", 1)[0] if "-" in raw_id else ""
    number = parse_numeric_id(raw_id, prefix) if prefix else None
    if number is None:
        return (artifact_type, 1, 0, raw_id)
    return (artifact_type, 0, number, raw_id)


def _filtered_artifacts(
    root: Path,
    *,
    artifact_type: str | None = None,
    scene: str | None = None,
    status: str | None = None,
    artifact_id: str | None = None,
) -> list[dict[str, Any]]:
    items = artifacts.load_all_artifacts(root)
    filtered: list[dict[str, Any]] = []
    for item in items:
        if artifact_type is not None and item.get("artifact_type") != artifact_type:
            continue
        if scene is not None and item.get("related_scene") != scene:
            continue
        if status is not None and item.get("status") != status:
            continue
        if artifact_id is not None and item.get("artifact_id") != artifact_id:
            continue
        filtered.append(item)
    filtered.sort(key=_artifact_numeric_sort_key)
    return filtered


def _artifact_summary_label(item: dict[str, Any]) -> str:
    for key in ("candidate_or_tool", "selected_candidate", "adoption_unit"):
        value = item.get(key)
        if value:
            return str(value)
    return "-"


def _strip_runtime_metadata(item: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in item.items() if key not in {"_path", "_adop_path"}}


def _handle_list(args: argparse.Namespace) -> tuple[int, dict[str, Any] | str]:
    items = _filtered_artifacts(
        Path(args.artifact_root),
        artifact_type=getattr(args, "artifact_type", None),
        scene=getattr(args, "scene", None),
        status=getattr(args, "status", None),
    )
    if getattr(args, "json", False):
        payload = {
            "schema_version": SCHEMA_VERSION,
            "command": "list",
            "status": "ok",
            "count": len(items),
            "artifacts": [
                {
                    "artifact_id": item.get("artifact_id"),
                    "artifact_type": item.get("artifact_type"),
                    "status": item.get("status"),
                    "related_scene": item.get("related_scene"),
                    "label": _artifact_summary_label(item),
                    "path": item.get("_adop_path") or item.get("_path"),
                }
                for item in items
            ],
        }
        return 0, payload

    lines = [
        f"{item.get('artifact_id', '-')}: {item.get('artifact_type', '-')} "
        f"status={item.get('status', '-')} "
        f"scene={item.get('related_scene', '-')} "
        f"label={_artifact_summary_label(item)}"
        for item in items
    ]
    return 0, "\n".join(lines)


def _handle_show(args: argparse.Namespace) -> tuple[int, dict[str, Any] | str]:
    items = _filtered_artifacts(
        Path(args.artifact_root),
        artifact_type=getattr(args, "artifact_type", None),
        artifact_id=args.artifact_id,
    )
    if not items:
        raise AdopValidationError("artifact id not found", 5)

    if getattr(args, "json", False):
        payload = {
            "schema_version": SCHEMA_VERSION,
            "command": "show",
            "status": "ok",
            "count": len(items),
            "artifacts": [
                {
                    **_strip_runtime_metadata(item),
                    "path": item.get("_adop_path") or item.get("_path"),
                }
                for item in items
            ],
        }
        return 0, payload

    blocks = []
    for item in items:
        header = (
            f"--- {item.get('artifact_type', '-')} {item.get('artifact_id', '-')} "
            f"({Path(str(item.get('_adop_path') or item.get('_path'))).name}) ---"
        )
        body = json.dumps(_strip_runtime_metadata(item), ensure_ascii=False, indent=2)
        blocks.append(f"{header}\n{body}")
    return 0, "\n\n".join(blocks)


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "intake":
            _emit(_handle_intake(args))
            return 0
        if args.command == "compare":
            _emit(_handle_compare(args))
            return 0
        if args.command == "start-trial":
            _emit(_handle_start_trial(args))
            return 0
        if args.command == "close-trial":
            _emit(_handle_close_trial(args))
            return 0
        if args.command == "summary":
            text = _handle_summary(args)
            if getattr(args, "json", False):
                _emit(
                    {
                        "schema_version": SCHEMA_VERSION,
                        "command": "summary",
                        "status": "ok",
                        "summary": text,
                    }
                )
            else:
                print(text)
            return 0
        if args.command == "render-html":
            print(_handle_render_html(args))
            return 0
        if args.command == "list":
            exit_code, payload = _handle_list(args)
            if isinstance(payload, str):
                print(payload)
            else:
                _emit(payload)
            return exit_code
        if args.command == "show":
            exit_code, payload = _handle_show(args)
            if isinstance(payload, str):
                print(payload)
            else:
                _emit(payload)
            return exit_code
        if args.command == "quick-intake":
            _emit(_handle_quick_intake(args))
            return 0
        if args.command == "quick-compare":
            _emit(_handle_quick_compare(args))
            return 0
        if args.command == "quick-trial":
            _emit(_handle_quick_trial(args))
            return 0
        if args.command == "quick-close-trial":
            _emit(_handle_quick_close_trial(args))
            return 0
        if args.command == "lint":
            exit_code, message = _handle_lint(args)
            print(message)
            return exit_code
        if args.command == "watch":
            _emit(_handle_watch(args))
            return 0
        if args.command == "block":
            _emit(_handle_block(args))
            return 0
        if args.command == "unblock":
            _emit(_handle_unblock(args))
            return 0
        if args.command == "deprecate":
            _emit(_handle_deprecate(args))
            return 0
        if args.command == "migrate":
            _emit(_handle_migrate(args))
            return 0
        if args.command == "archive":
            _emit(_handle_archive(args))
            return 0
        if args.command == "couple":
            _emit(_handle_couple(args))
            return 0
        if args.command == "couplings":
            exit_code, payload = _handle_couplings(args)
            if isinstance(payload, str):
                print(payload)
            else:
                _emit(payload)
            return exit_code
        if args.command == "init":
            print(_handle_init(args))
            return 0
        if args.command == "status":
            print(_handle_status(args))
            return 0
        if args.command == "scan":
            exit_code, text = _handle_scan(args)
            print(text)
            return exit_code
        if args.command == "next":
            print(_handle_next(args))
            return 0
        raise AdopValidationError(f"unsupported command: {args.command}", 2)
    except AdopValidationError as exc:
        _emit(artifacts.json_response(args.command, "error", [], [str(exc)]))
        return exc.exit_code
    except artifacts.AdopArtifactError as exc:
        _emit(artifacts.json_response(args.command, "error", [], [str(exc)]))
        return 11


if __name__ == "__main__":
    raise SystemExit(main())
