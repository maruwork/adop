#!/usr/bin/env python3
"""ADOP JSON-native CLI."""

from __future__ import annotations

import argparse
import io
import json
import sys
from argparse import RawTextHelpFormatter
from pathlib import Path
from typing import Any

try:
    from .common import fix_stdout_encoding
    from . import adop_artifacts as artifacts
    from .adop_ids import next_sequential_id, parse_numeric_id
    from .adop_state_machine import comparison_ready_for_trial, promote_gate_errors
    from .adop_summary import build_summary
    from .adop_types import (
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
        JUDGMENT_REPORT,
        LANDING_TARGET,
        LANES,
        MIGRATION_NOTE,
        NON_PROMOTE_VERDICTS,
        OBSERVED_EFFECT,
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
    from .adop_validation import (
        AdopValidationError,
        lint_artifact_root,
        today_iso,
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
except ImportError:  # pragma: no cover - script import path
    from common import fix_stdout_encoding

    import adop_artifacts as artifacts
    from adop_ids import next_sequential_id, parse_numeric_id
    from adop_state_machine import comparison_ready_for_trial, promote_gate_errors
    from adop_summary import build_summary
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
        JUDGMENT_REPORT,
        LANDING_TARGET,
        LANES,
        MIGRATION_NOTE,
        NON_PROMOTE_VERDICTS,
        OBSERVED_EFFECT,
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

__version__ = "0.1.0"


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


def _prepare_artifact_root(args: argparse.Namespace) -> Path:
    try:
        return artifacts.ensure_artifact_root(
            Path(args.artifact_root),
            target_project_root=Path(args.target_project_root) if getattr(args, "target_project_root", None) else None,
            allow_project_impact=bool(getattr(args, "allow_project_impact", False)),
        )
    except artifacts.AdopBoundaryError as exc:
        # Boundary violation only -> exit 14. Plain AdopArtifactError (e.g. mkdir
        # permission/IO failure) flows to main()'s handler, which returns 11.
        raise AdopValidationError(str(exc), 14) from exc


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
            "scene_fit_to_project": "fits one bounded use case",
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
            "preventive_actions": ["clarify the bounded use case before the next trial"],
            "why_this_problem_recurred": "the use case still depends on ad hoc operator judgment",
        }
    if verdict == VERDICTS[2]:
        return {
            "judgment_reason": "bounded trial did not justify continued use",
            "next_action": "keep the use case on manual handling",
            "recurring_control_decision": RECURRING_CONTROL_DECISIONS[1],
            "reopen_condition": "retry only if a different bounded use case appears",
            "preventive_actions": ["record the rejected pattern so the same trial is not repeated blindly"],
            "why_this_problem_recurred": "the candidate did not fit the bounded use case well enough",
        }
    raise AdopValidationError(f"unsupported quick close verdict: {verdict}", 2)


def _comparison_filter_args(parser: argparse.ArgumentParser) -> None:
    for cli_name in ("scene-fit", "authority-safe", "controlability"):
        key = cli_name.replace("-", "_")
        parser.add_argument(f"--{cli_name}-status", required=True, choices=FILTER_STATUSES)
        parser.add_argument(f"--{cli_name}-reason", required=True)
        parser.add_argument(f"--{cli_name}-constraint", default=None)


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
            "Simple path (guided, preset-filled — start here):\n"
            "  quick-intake -> quick-compare -> quick-trial -> quick-close-trial\n\n"
            "Advanced path (explicit, full control over every field):\n"
            "  intake / compare / start-trial / close-trial\n\n"
            "Inspect anytime:\n"
            "  summary (text or --json) / list / show / lint\n\n"
            "JSON-blob flags also accept a file via @path\n"
            "  e.g. --compatibility-diagnosis-json @diagnosis.json\n\n"
            "Exit codes:\n"
            "  0 ok\n"
            "  2 invalid CLI usage / validation\n"
            "  5 missing artifact or readiness gate not met\n"
            "  10 lint found invalid artifacts\n"
            "  11 artifact read/write/schema error\n"
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
    quick_intake.add_argument("--artifact-root", required=True)
    _project_boundary_args(quick_intake)
    quick_intake.add_argument("--candidate", required=True)
    quick_intake.add_argument("--source", required=True)
    quick_intake.add_argument("--use-case", dest="scene", required=True)
    quick_intake.add_argument("--why-now", required=True)
    quick_intake.add_argument("--candidate-shape", default=CANDIDATE_SHAPES[0], choices=CANDIDATE_SHAPES)
    quick_intake.add_argument("--lane", default=LANES[1], choices=LANES)
    quick_intake.add_argument("--root-cause-hypothesis", default="")

    quick_compare = subparsers.add_parser(
        "quick-compare",
        help="simple path: compare 2-3 candidates for one bounded use case",
        description="Create a comparison artifact with default project profile and filter reasoning.",
    )
    quick_compare.add_argument("--artifact-root", required=True)
    _project_boundary_args(quick_compare)
    quick_compare.add_argument("--use-case", dest="scene", required=True)
    quick_compare.add_argument("--candidate", dest="candidates", action="append", required=True)
    quick_compare.add_argument("--selected", required=True)
    quick_compare.add_argument("--candidate-shape", default=CANDIDATE_SHAPES[0], choices=CANDIDATE_SHAPES)
    quick_compare.add_argument("--adoption-unit")
    quick_compare.add_argument("--root-cause-hypothesis", default="")
    quick_compare.add_argument("--structural-gap", default="current workflow lacks a bounded evaluation lane for this use case")
    quick_compare.add_argument("--non-tool-alternative", default="tighten the manual checklist before adding a tool")
    quick_compare.add_argument("--target-project-profile-json", default="")
    quick_compare.add_argument("--compatibility-diagnosis-json", default="")
    quick_compare.add_argument("--no-impact-envelope-json", default="")

    quick_trial = subparsers.add_parser(
        "quick-trial",
        help="simple path: open a bounded trial from the latest comparison",
        description="Start a trial with a small preset such as review-assist.",
    )
    quick_trial.add_argument("--artifact-root", required=True)
    _project_boundary_args(quick_trial)
    quick_trial.add_argument("--use-case", dest="scene", required=True)
    quick_trial.add_argument("--mode", required=True, choices=("review-assist", "read-only-comparison"))
    quick_trial.add_argument("--executor", required=True)
    quick_trial.add_argument("--trigger", default="")
    quick_trial.add_argument("--evaluation-gate", default="")
    quick_trial.add_argument("--writeback-target", default="")
    quick_trial.add_argument("--fallback", default="")

    quick_close = subparsers.add_parser(
        "quick-close-trial",
        help="simple path: close a trial with preset judgment fields",
        description="Close a trial with a verdict and observed effect, using default judgment wording when omitted.",
    )
    quick_close.add_argument("--artifact-root", required=True)
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
    intake.add_argument("--artifact-root", required=True)
    _project_boundary_args(intake)
    intake.add_argument("--candidate", required=True)
    intake.add_argument("--candidate-shape", required=True, choices=CANDIDATE_SHAPES)
    intake.add_argument("--source", required=True)
    intake.add_argument("--scene", required=True)
    intake.add_argument("--lane", required=True, choices=LANES)
    intake.add_argument("--reason", required=True)
    intake.add_argument("--root-cause-hypothesis", required=True)

    compare = subparsers.add_parser(
        "compare",
        help="advanced: explicit comparison with full filter and compatibility fields",
        description="Low-level comparison command with explicit filters, project profile, and compatibility diagnosis.",
    )
    compare.add_argument("--artifact-root", required=True)
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
    start.add_argument("--artifact-root", required=True)
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
    start.add_argument("--writeback-target", required=True)
    start.add_argument("--decision-owner", default=None)
    start.add_argument("--fallback", required=True, choices=FALLBACKS)

    close = subparsers.add_parser(
        "close-trial",
        help="advanced: explicit trial close with full judgment fields",
        description="Low-level close command with explicit verdict, preventive actions, and recurring control fields.",
    )
    close.add_argument("--artifact-root", required=True)
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
    summary.add_argument("--artifact-root", required=True)
    summary.add_argument("--scene")
    summary.add_argument("--status")
    summary.add_argument(
        "--json",
        action="store_true",
        help="emit a machine-readable JSON envelope instead of plain text",
    )

    list_cmd = subparsers.add_parser(
        "list",
        help="list artifacts under the current artifact root",
        description="List artifacts with optional type/scene/status filters.",
    )
    list_cmd.add_argument("--artifact-root", required=True)
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
    show.add_argument("--artifact-root", required=True)
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
    lint.add_argument("--artifact-root", required=True)

    watch_cmd = subparsers.add_parser(
        "watch",
        help="record a tool on the radar before formal evaluation",
        description="Create a watch-note. Use-case is optional at this stage.",
    )
    watch_cmd.add_argument("--artifact-root", required=True)
    _project_boundary_args(watch_cmd)
    watch_cmd.add_argument("--candidate", required=True)
    watch_cmd.add_argument("--interest-reason", required=True)
    watch_cmd.add_argument("--use-case", dest="scene", default="")

    block_cmd = subparsers.add_parser(
        "block",
        help="block a proposed adoption on an external constraint",
        description="Create a blocked-note. Requires an existing candidate-intake-note for the scene.",
    )
    block_cmd.add_argument("--artifact-root", required=True)
    _project_boundary_args(block_cmd)
    block_cmd.add_argument("--use-case", dest="scene", required=True)
    block_cmd.add_argument("--block-reason", required=True)
    block_cmd.add_argument("--unblock-condition", required=True)
    block_cmd.add_argument("--owner", required=True)

    unblock_cmd = subparsers.add_parser(
        "unblock",
        help="lift a block and re-enter proposed state",
        description="Create a new candidate-intake-note from blocked state.",
    )
    unblock_cmd.add_argument("--artifact-root", required=True)
    _project_boundary_args(unblock_cmd)
    unblock_cmd.add_argument("--use-case", dest="scene", required=True)
    unblock_cmd.add_argument("--why-unblocked", required=True)

    deprecate_cmd = subparsers.add_parser(
        "deprecate",
        help="begin retirement of a promoted tool",
        description="Create a deprecation-note. Requires an existing promotion-note for the scene.",
    )
    deprecate_cmd.add_argument("--artifact-root", required=True)
    _project_boundary_args(deprecate_cmd)
    deprecate_cmd.add_argument("--use-case", dest="scene", required=True)
    deprecate_cmd.add_argument("--retirement-reason", required=True)
    deprecate_cmd.add_argument("--replacement-candidate", dest="replacement_candidates", action="append", required=True)
    deprecate_cmd.add_argument("--timeline", required=True)

    migrate_cmd = subparsers.add_parser(
        "migrate",
        help="start active migration away from a deprecated tool",
        description="Create a migration-note. Requires an existing deprecation-note for the scene.",
    )
    migrate_cmd.add_argument("--artifact-root", required=True)
    _project_boundary_args(migrate_cmd)
    migrate_cmd.add_argument("--use-case", dest="scene", required=True)
    migrate_cmd.add_argument("--migration-target", required=True)
    migrate_cmd.add_argument("--migration-plan", required=True)

    archive_cmd = subparsers.add_parser(
        "archive",
        help="mark a tool as fully archived for this use-case",
        description="Create an archive-note. Requires an existing deprecation-note or migration-note.",
    )
    archive_cmd.add_argument("--artifact-root", required=True)
    _project_boundary_args(archive_cmd)
    archive_cmd.add_argument("--use-case", dest="scene", required=True)
    archive_cmd.add_argument("--end-date", required=True)
    archive_cmd.add_argument("--successor-tool", default="")

    couple_cmd = subparsers.add_parser(
        "couple",
        help="record how an external tool is entangled with project files",
        description=(
            "Create a coupling-note: a complete snapshot of which files the tool is\n"
            "entangled with, how (coupling_type), and how hard each is to detach\n"
            "(removal_cost). Each call records the CURRENT full coupling set; the report\n"
            "uses the latest coupling-note per (tool, use-case).\n\n"
            "Provide couplings either as repeated --couple 'PATH|TYPE|COST[|NOTE]'\n"
            "or as --couplings-json (a JSON list; @path reads a file).\n"
            f"  TYPE one of: {', '.join(COUPLING_TYPES)}\n"
            f"  COST one of: {', '.join(REMOVAL_COSTS)}"
        ),
        formatter_class=RawTextHelpFormatter,
    )
    couple_cmd.add_argument("--artifact-root", required=True)
    _project_boundary_args(couple_cmd)
    couple_cmd.add_argument("--use-case", dest="scene", required=True)
    couple_cmd.add_argument("--tool", required=True)
    couple_cmd.add_argument(
        "--couple", dest="couples", action="append", default=[],
        metavar="PATH|TYPE|COST[|NOTE]",
        help="one coupling entry, pipe-delimited; repeatable",
    )
    couple_cmd.add_argument("--couplings-json", default="")

    couplings_cmd = subparsers.add_parser(
        "couplings",
        help="report tool-to-file entanglement (latest coupling-note per tool/use-case)",
        description="Report declared tool-to-file couplings and their detachment cost.",
    )
    couplings_cmd.add_argument("--artifact-root", required=True)
    _project_boundary_args(couplings_cmd)
    couplings_cmd.add_argument("--use-case", dest="scene", default=None, help="filter to one use-case")
    couplings_cmd.add_argument("--json", action="store_true")

    return parser


def _handle_intake(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    artifact_id = next_sequential_id(root, "ci")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": CANDIDATE_INTAKE_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "candidate_or_tool": args.candidate,
        "candidate_shape": args.candidate_shape,
        "source": args.source,
        "related_scene": args.scene,
        "intended_lane": args.lane,
        "intake_reason": args.reason,
        "current_disposition": PROPOSED,
        "next_action": "compare candidate set",
        ROOT_CAUSE_HYPOTHESIS: args.root_cause_hypothesis,
    }
    validate_intake_payload(payload)
    path = artifacts.write_artifact(root, CANDIDATE_INTAKE_NOTE, artifact_id, payload)
    return artifacts.json_response("intake", "ok", [path.name], [])


def _handle_compare(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
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
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": COMPARISON_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "related_scene": args.scene,
        "candidate_shape": args.candidate_shape,
        "derived_from": [parent["artifact_id"]],
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
        "candidate_shape": packet["candidate_shape"],
        DECOMPOSITION_DECISION: packet[DECOMPOSITION_DECISION],
        "adoption_unit": packet["adoption_unit"],
        "target_project_profile": packet["target_project_profile"],
        "compatibility_diagnosis": packet["compatibility_diagnosis"],
        "recommended_fit_lane": packet["recommended_fit_lane"],
        "no_impact_envelope": packet["no_impact_envelope"],
    }
    validate_close_payload(close_payload)
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
        "related_scene": packet["related_scene"],
        "derived_from": [packet["artifact_id"]],
        "trial_type": packet["trial_type"],
        "sandbox_type": packet["sandbox_type"],
        "input_surface": packet["input_surface"],
        "output_contract": packet["output_contract"],
        "mutation_boundary": packet["mutation_boundary"],
        "verification_method": packet["verification_method"],
        "decision_owner": args.decision_owner or packet.get("decision_owner"),
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

    if args.verdict in NON_PROMOTE_VERDICTS:
        reject_id = next_sequential_id(root, "rj")
        reject_payload = {
            "schema_version": SCHEMA_VERSION,
            "artifact_type": REJECT_NOTE,
            "artifact_id": reject_id,
            "status": "closed",
            "created_at": created_at,
            "related_scene": packet["related_scene"],
            "derived_from": [args.trial_id],
            "decision_owner": args.decision_owner or packet.get("decision_owner"),
            "reject_or_hold_reason": args.judgment_reason,
            "reopen_condition": args.reopen_condition,
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
            "related_scene": packet["related_scene"],
            "derived_from": [args.trial_id],
            "decision_owner": args.decision_owner or packet.get("decision_owner"),
            "repeated_effect": args.observed_effect,
            "trigger_canonical_record": packet.get("trigger_canonical_record", {}),
            LANDING_TARGET: packet["writeback_target"],
            "minimum_bake_duration": "n/a",
            "reversal_test": "not run",
        }
        group_specs.append((PROMOTION_NOTE, promotion_id, promotion_payload))

    committed = artifacts.write_artifact_group(root, group_specs)
    artifact_refs = [path.name for path in committed]
    return artifacts.json_response("close-trial", "ok", artifact_refs, [])


def _handle_watch(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
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
    blocked = artifacts.latest_by_type(root, BLOCKED_NOTE, scene=args.scene)
    if not blocked:
        raise AdopValidationError("blocked-note for scene not found", 5)
    artifact_id = next_sequential_id(root, "ci")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": CANDIDATE_INTAKE_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "related_scene": args.scene,
        "candidate_or_tool": str(blocked.get("candidate_or_tool", "")),
        "source": "unblock",
        "intended_lane": LANES[1],
        "intake_reason": args.why_unblocked,
        "current_disposition": PROPOSED,
        "next_action": "compare candidate set",
        ROOT_CAUSE_HYPOTHESIS: args.why_unblocked,
        "derived_from": [blocked["artifact_id"]],
    }
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
    artifact_id = next_sequential_id(root, "cp")
    payload = {
        "schema_version": SCHEMA_VERSION,
        "artifact_type": COUPLING_NOTE,
        "artifact_id": artifact_id,
        "status": "active",
        "created_at": today_iso(),
        "related_scene": args.scene,
        "candidate_or_tool": args.tool,
        "couplings": couplings,
    }
    validate_coupling_note_payload(payload)
    path = artifacts.write_artifact(root, COUPLING_NOTE, artifact_id, payload)
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
            note_text = f" {entry['note']}" if entry.get("note") else ""
            lines.append(
                f"- {entry.get('path', '-')} "
                f"[{entry.get('coupling_type', '-')}, {entry.get('removal_cost', '-')}]{note_text}"
            )
    return 0, "\n".join(lines)


def _handle_summary(args: argparse.Namespace) -> str:
    return build_summary(Path(args.artifact_root), scene=args.scene, status=args.status)


def _handle_quick_intake(args: argparse.Namespace) -> dict[str, Any]:
    if not args.root_cause_hypothesis:
        args.root_cause_hypothesis = args.why_now
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
    args.scene_fit_reason = "one bounded use case"
    args.scene_fit_constraint = None
    args.authority_safe_status = FILTER_STATUSES[1]
    args.authority_safe_reason = "safe when reviewed before writeback"
    args.authority_safe_constraint = "review before writeback"
    args.controlability_status = FILTER_STATUSES[0]
    args.controlability_reason = "bounded trial possible"
    args.controlability_constraint = None
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
    args.decision_owner = None
    args.fallback = args.fallback or preset["fallback"]
    return _handle_start_trial(args)


def _handle_quick_close_trial(args: argparse.Namespace) -> dict[str, Any]:
    root = _prepare_artifact_root(args)
    packet = artifacts.find_trial_packet(root, args.trial_id)
    if not packet:
        raise AdopValidationError("trial-packet not found", 5)
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
        or f"the bounded use case '{packet['related_scene']}' needed a more explicit helper path"
    )
    return _handle_close_trial(args)


def _handle_lint(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    issues = lint_artifact_root(Path(args.artifact_root))
    if issues:
        return 10, artifacts.json_response("lint", "error", [], issues)
    return 0, artifacts.json_response("lint", "ok", [], [])


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
            exit_code, payload = _handle_lint(args)
            _emit(payload)
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
        raise AdopValidationError(f"unsupported command: {args.command}", 2)
    except AdopValidationError as exc:
        _emit(artifacts.json_response(args.command, "error", [], [str(exc)]))
        return exc.exit_code
    except artifacts.AdopArtifactError as exc:
        _emit(artifacts.json_response(args.command, "error", [], [str(exc)]))
        return 11


if __name__ == "__main__":
    raise SystemExit(main())
