#!/usr/bin/env python3
"""ADOP validation helpers."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

try:
    from .adop_artifacts import load_all_artifacts
    from .adop_types import (
        ARCHIVE_NOTE,
        ARTIFACT_ID_PREFIX,
        ARTIFACT_TYPES,
        AUTHORITY_SAFE,
        BLOCKED_NOTE,
        CANDIDATE_INTAKE_NOTE,
        CANDIDATE_SHAPES,
        COMPARISON_NOTE,
        CONTROLABILITY,
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
        LANES,
        MIGRATION_NOTE,
        NON_PROMOTE_VERDICTS,
        OBSERVED_EFFECT,
        RECURRING_CONTROL_DECISIONS,
        ROOT_CAUSE_HYPOTHESIS,
        SANDBOX_TYPES,
        SCHEMA_VERSION,
        STRUCTURAL_GAP,
        TRIAL_PACKET,
        TRIAL_TYPES,
        VERDICTS,
        WATCH_NOTE,
        WRITE_TRIAL_TYPES,
    )
except ImportError:  # pragma: no cover - script import path
    from adop_artifacts import load_all_artifacts
    from adop_types import (
        ARCHIVE_NOTE,
        ARTIFACT_ID_PREFIX,
        ARTIFACT_TYPES,
        AUTHORITY_SAFE,
        BLOCKED_NOTE,
        CANDIDATE_INTAKE_NOTE,
        CANDIDATE_SHAPES,
        COMPARISON_NOTE,
        CONTROLABILITY,
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
        LANES,
        MIGRATION_NOTE,
        NON_PROMOTE_VERDICTS,
        OBSERVED_EFFECT,
        RECURRING_CONTROL_DECISIONS,
        ROOT_CAUSE_HYPOTHESIS,
        SANDBOX_TYPES,
        SCHEMA_VERSION,
        STRUCTURAL_GAP,
        TRIAL_PACKET,
        TRIAL_TYPES,
        VERDICTS,
        WATCH_NOTE,
        WRITE_TRIAL_TYPES,
    )


class AdopValidationError(ValueError):
    """Validation error carrying an exit code."""

    def __init__(self, message: str, exit_code: int = 6):
        super().__init__(message)
        self.exit_code = exit_code


def require_non_empty(value: str | None, field_name: str) -> None:
    if not value or not str(value).strip():
        raise AdopValidationError(f"{field_name} is required", 2)


def validate_choice(value: str, field_name: str, allowed: tuple[str, ...], *, exit_code: int = 3) -> None:
    if value not in allowed:
        raise AdopValidationError(f"{field_name} must be one of {allowed}", exit_code)


def today_iso() -> str:
    return date.today().isoformat()


def validate_filter_assessment(filter_assessment: dict[str, Any]) -> None:
    for key in FILTER_NAMES:
        if key not in filter_assessment:
            raise AdopValidationError(f"filter_assessment.{key} missing")
        section = filter_assessment[key]
        if not isinstance(section, dict):
            raise AdopValidationError(f"filter_assessment.{key} must be object")
        validate_choice(str(section.get("status", "")), f"filter_assessment.{key}.status", FILTER_STATUSES)
        require_non_empty(section.get("reason"), f"filter_assessment.{key}.reason")


def _require_string_list(value: Any, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(str(item).strip() for item in value):
        raise AdopValidationError(f"{field_name} must contain at least one non-empty item", 2)
    return [str(item) for item in value]


def validate_target_project_profile(profile: dict[str, Any]) -> None:
    if not isinstance(profile, dict):
        raise AdopValidationError("target_project_profile must be object", 2)
    require_non_empty(profile.get("main_language"), "target_project_profile.main_language")
    _require_string_list(profile.get("runtime"), "target_project_profile.runtime")
    _require_string_list(profile.get("artifact_surfaces"), "target_project_profile.artifact_surfaces")
    require_non_empty(profile.get("authority_boundary"), "target_project_profile.authority_boundary")
    require_non_empty(profile.get("operator_phase"), "target_project_profile.operator_phase")
    _require_string_list(profile.get("allowed_input_surfaces"), "target_project_profile.allowed_input_surfaces")
    require_non_empty(profile.get("allowed_mutation_boundary"), "target_project_profile.allowed_mutation_boundary")
    _require_string_list(profile.get("verification_methods"), "target_project_profile.verification_methods")


def validate_compatibility_diagnosis(items: Any, *, require_adoption_unit: str | None = None) -> list[dict[str, Any]]:
    if not isinstance(items, list) or not items:
        raise AdopValidationError("compatibility_diagnosis must contain at least one item", 2)
    validated: list[dict[str, Any]] = []
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            raise AdopValidationError(f"compatibility_diagnosis[{idx}] must be object", 2)
        for field in (
            "adoption_unit",
            "scene_fit_to_project",
            "input_fit",
            "output_fit",
            AUTHORITY_SAFE,
            CONTROLABILITY,
            "no_impact_feasibility",
        ):
            require_non_empty(item.get(field), f"compatibility_diagnosis[{idx}].{field}")
        validate_choice(
            str(item.get("recommended_fit_lane", "")),
            f"compatibility_diagnosis[{idx}].recommended_fit_lane",
            FIT_LANES,
        )
        validated.append(item)
    if require_adoption_unit and not any(str(item.get("adoption_unit")) == require_adoption_unit for item in validated):
        raise AdopValidationError("compatibility_diagnosis must include adoption_unit entry", 2)
    return validated


def validate_no_impact_envelope(envelope: dict[str, Any]) -> None:
    if not isinstance(envelope, dict):
        raise AdopValidationError("no_impact_envelope must be object", 2)
    _require_string_list(envelope.get("allowed"), "no_impact_envelope.allowed")
    _require_string_list(envelope.get("forbidden"), "no_impact_envelope.forbidden")


def validate_intake_payload(payload: dict[str, Any]) -> None:
    for field in (
        "candidate_or_tool",
        "source",
        "related_scene",
        "intended_lane",
        "intake_reason",
        ROOT_CAUSE_HYPOTHESIS,
    ):
        require_non_empty(payload.get(field), field)
    validate_choice(payload["intended_lane"], "intended_lane", LANES)
    validate_choice(payload["current_disposition"], "current_disposition", DISPOSITIONS)
    validate_choice(payload.get("candidate_shape", ""), "candidate_shape", CANDIDATE_SHAPES)


def validate_comparison_payload(payload: dict[str, Any]) -> None:
    compared = payload.get("compared_candidates", [])
    if not isinstance(compared, list) or len(compared) < 2 or len(compared) > 3:
        raise AdopValidationError("compared_candidates must contain 2-3 candidates")
    if payload.get("selected_candidate") not in compared:
        raise AdopValidationError("selected_candidate must be in compared_candidates")
    validate_filter_assessment(payload.get("filter_assessment", {}))
    validate_choice(payload.get("candidate_shape", ""), "candidate_shape", CANDIDATE_SHAPES)
    validate_choice(
        payload.get(DECOMPOSITION_DECISION, ""),
        DECOMPOSITION_DECISION,
        DECOMPOSITION_DECISIONS,
    )
    for field in (ROOT_CAUSE_HYPOTHESIS, STRUCTURAL_GAP, "non_tool_alternative", "selection_reason"):
        require_non_empty(payload.get(field), field)
    require_non_empty(payload.get("adoption_unit"), "adoption_unit")
    validate_target_project_profile(payload.get("target_project_profile", {}))
    diagnoses = validate_compatibility_diagnosis(
        payload.get("compatibility_diagnosis", []),
        require_adoption_unit=str(payload.get("adoption_unit", "")),
    )
    recommended_fit_lane = str(payload.get("recommended_fit_lane", "")).strip()
    if recommended_fit_lane:
        validate_choice(recommended_fit_lane, "recommended_fit_lane", FIT_LANES)
        matched = next(
            (item for item in diagnoses if str(item.get("adoption_unit")) == str(payload.get("adoption_unit", ""))),
            None,
        )
        if matched and str(matched.get("recommended_fit_lane")) != recommended_fit_lane:
            raise AdopValidationError("recommended_fit_lane must match adoption_unit diagnosis", 2)
    validate_no_impact_envelope(payload.get("no_impact_envelope", {}))
    if payload.get("candidate_shape") == "composite":
        subtargets = payload.get("discovered_subtargets", [])
        _require_string_list(subtargets, "discovered_subtargets")
    if payload.get(DECOMPOSITION_DECISION) == "split-required":
        require_non_empty(payload.get("recommended_next_candidate"), "recommended_next_candidate")


def validate_no_impact_trial_mode(payload: dict[str, Any], *, no_impact_default: bool) -> None:
    if not no_impact_default:
        return
    if payload.get("trial_type") in WRITE_TRIAL_TYPES:
        raise AdopValidationError("no-impact default allows only non-write trial types", 13)
    if str(payload.get("mutation_boundary", "")).strip().lower() != "no write":
        raise AdopValidationError("no-impact default requires mutation_boundary=no write", 13)


def validate_trial_packet_payload(payload: dict[str, Any]) -> None:
    validate_choice(payload["trial_type"], "trial_type", TRIAL_TYPES)
    validate_choice(payload["sandbox_type"], "sandbox_type", SANDBOX_TYPES)
    validate_choice(payload["lane"], "lane", LANES)
    validate_choice(payload["fallback"], "fallback", FALLBACKS)
    for field in ("input_surface", "output_contract", "mutation_boundary", "verification_method", EXECUTOR, "trigger", EVALUATION_GATE, "writeback_target"):
        require_non_empty(payload.get(field), field)
    if "write" in payload["trial_type"] and "isolated write sandbox" not in payload["sandbox_type"]:
        raise AdopValidationError("write trial requires isolated write sandbox", 13)
    for field in (
        "candidate_shape",
        DECOMPOSITION_DECISION,
        "adoption_unit",
        "recommended_fit_lane",
    ):
        require_non_empty(payload.get(field), field)
    validate_choice(payload.get("candidate_shape", ""), "candidate_shape", CANDIDATE_SHAPES)
    validate_choice(
        payload.get(DECOMPOSITION_DECISION, ""),
        DECOMPOSITION_DECISION,
        DECOMPOSITION_DECISIONS,
    )
    validate_choice(payload.get("recommended_fit_lane", ""), "recommended_fit_lane", FIT_LANES)
    validate_target_project_profile(payload.get("target_project_profile", {}))
    validate_compatibility_diagnosis(
        payload.get("compatibility_diagnosis", []),
        require_adoption_unit=str(payload.get("adoption_unit", "")),
    )
    validate_no_impact_envelope(payload.get("no_impact_envelope", {}))


def validate_close_payload(payload: dict[str, Any]) -> None:
    validate_choice(payload["verdict"], "verdict", VERDICTS)
    observed_effect = payload.get(OBSERVED_EFFECT, payload.get("observed_effect_summary"))
    require_non_empty(observed_effect, OBSERVED_EFFECT)
    require_non_empty(payload.get("judgment_reason"), "judgment_reason")
    require_non_empty(payload.get("next_action"), "next_action")
    require_non_empty(payload.get(ROOT_CAUSE_HYPOTHESIS), ROOT_CAUSE_HYPOTHESIS)
    why = payload.get("why_this_problem_recurred", "")
    require_non_empty(why, "why_this_problem_recurred")
    preventive = payload.get("preventive_action", [])
    if not isinstance(preventive, list) or not preventive or not all(str(item).strip() for item in preventive):
        raise AdopValidationError("preventive_action must contain at least one non-empty item", 2)
    validate_choice(payload.get("recurring_control_decision", ""), "recurring_control_decision", RECURRING_CONTROL_DECISIONS)
    validate_choice(payload.get("candidate_shape", ""), "candidate_shape", CANDIDATE_SHAPES)
    validate_choice(
        payload.get(DECOMPOSITION_DECISION, ""),
        DECOMPOSITION_DECISION,
        DECOMPOSITION_DECISIONS,
    )
    require_non_empty(payload.get("adoption_unit"), "adoption_unit")
    validate_target_project_profile(payload.get("target_project_profile", {}))
    validate_compatibility_diagnosis(
        payload.get("compatibility_diagnosis", []),
        require_adoption_unit=str(payload.get("adoption_unit", "")),
    )
    validate_choice(payload.get("recommended_fit_lane", ""), "recommended_fit_lane", FIT_LANES)
    validate_no_impact_envelope(payload.get("no_impact_envelope", {}))
    if payload["verdict"] in NON_PROMOTE_VERDICTS:
        require_non_empty(payload.get("reopen_condition"), "reopen_condition")


def validate_watch_note_payload(payload: dict[str, Any]) -> None:
    require_non_empty(payload.get("candidate_or_tool"), "candidate_or_tool")
    require_non_empty(payload.get("interest_reason"), "interest_reason")
    # related_scene is intentionally optional for watch-note (tool noticed before use-case is decided)


def validate_blocked_note_payload(payload: dict[str, Any]) -> None:
    require_non_empty(payload.get("related_scene"), "related_scene")
    require_non_empty(payload.get("candidate_or_tool"), "candidate_or_tool")
    require_non_empty(payload.get("block_reason"), "block_reason")
    require_non_empty(payload.get("unblock_condition"), "unblock_condition")
    require_non_empty(payload.get("owner"), "owner")


def validate_deprecation_note_payload(payload: dict[str, Any]) -> None:
    require_non_empty(payload.get("related_scene"), "related_scene")
    require_non_empty(payload.get("candidate_or_tool"), "candidate_or_tool")
    require_non_empty(payload.get("retirement_reason"), "retirement_reason")
    _require_string_list(payload.get("replacement_candidates", []), "replacement_candidates")
    require_non_empty(payload.get("timeline"), "timeline")


def validate_migration_note_payload(payload: dict[str, Any]) -> None:
    require_non_empty(payload.get("related_scene"), "related_scene")
    require_non_empty(payload.get("candidate_or_tool"), "candidate_or_tool")
    require_non_empty(payload.get("migration_target"), "migration_target")
    require_non_empty(payload.get("migration_plan"), "migration_plan")


def validate_archive_note_payload(payload: dict[str, Any]) -> None:
    require_non_empty(payload.get("related_scene"), "related_scene")
    require_non_empty(payload.get("candidate_or_tool"), "candidate_or_tool")
    require_non_empty(payload.get("end_date"), "end_date")
    # successor_tool is optional


def validate_artifact_schema(item: dict[str, Any]) -> None:
    if item.get("schema_version") != SCHEMA_VERSION:
        raise AdopValidationError("schema_version invalid", 11)
    artifact_type = item.get("artifact_type")
    if artifact_type not in ARTIFACT_TYPES:
        raise AdopValidationError(f"artifact_type invalid: {artifact_type}", 11)
    artifact_id = str(item.get("artifact_id", ""))
    prefix = ARTIFACT_ID_PREFIX[artifact_type]
    if not artifact_id.startswith(f"{prefix}-"):
        raise AdopValidationError(f"artifact_id invalid for {artifact_type}: {artifact_id}", 11)
    require_non_empty(item.get("created_at"), "created_at")


def lint_artifact_root(root: Path) -> list[str]:
    issues: list[str] = []
    items = load_all_artifacts(root)
    seen_trial_judgments: set[str] = set()
    by_id = {f"{item.get('artifact_type')}::{item.get('artifact_id')}": item for item in items}

    for item in items:
        try:
            validate_artifact_schema(item)
        except AdopValidationError as exc:
            issues.append(str(exc))
            continue

        artifact_type = item["artifact_type"]
        if artifact_type == COMPARISON_NOTE:
            try:
                validate_comparison_payload(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
        if artifact_type == CANDIDATE_INTAKE_NOTE:
            try:
                validate_intake_payload(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
        if artifact_type == TRIAL_PACKET:
            try:
                validate_trial_packet_payload(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
        if artifact_type == WATCH_NOTE:
            try:
                validate_watch_note_payload(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
        if artifact_type == BLOCKED_NOTE:
            try:
                validate_blocked_note_payload(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
        if artifact_type == DEPRECATION_NOTE:
            try:
                validate_deprecation_note_payload(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
        if artifact_type == MIGRATION_NOTE:
            try:
                validate_migration_note_payload(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
        if artifact_type == ARCHIVE_NOTE:
            try:
                validate_archive_note_payload(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
        if artifact_type == JUDGMENT_REPORT:
            trial_id = str(item["artifact_id"])
            if trial_id in seen_trial_judgments:
                issues.append(f"duplicate judgment-report for {trial_id}")
            seen_trial_judgments.add(trial_id)
            if not item.get("closed_at"):
                issues.append("judgment-report missing closed_at")
            try:
                validate_close_payload(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
            for field in (
                ROOT_CAUSE_HYPOTHESIS,
                "why_this_problem_recurred",
                "next_action",
                "judgment_reason",
                "candidate_shape",
                DECOMPOSITION_DECISION,
                "adoption_unit",
                "recommended_fit_lane",
            ):
                if not item.get(field):
                    issues.append(f"judgment-report missing {field}")
            preventive = item.get("preventive_action", [])
            if not isinstance(preventive, list) or not preventive:
                issues.append("judgment-report missing preventive_action")
            if not isinstance(item.get("target_project_profile"), dict):
                issues.append("judgment-report missing target_project_profile")
            if not isinstance(item.get("compatibility_diagnosis"), list):
                issues.append("judgment-report missing compatibility_diagnosis")
            if not isinstance(item.get("no_impact_envelope"), dict):
                issues.append("judgment-report missing no_impact_envelope")

        for parent_id in item.get("derived_from", []):
            expected_ok = any(
                f"{parent_type}::{parent_id}" in by_id
                for parent_type in ARTIFACT_TYPES
            )
            if not expected_ok:
                issues.append(f"derived_from missing target: {parent_id}")

    for item in items:
        if item.get("artifact_type") == TRIAL_PACKET:
            trial_id = str(item["artifact_id"])
            if trial_id not in seen_trial_judgments:
                issues.append(f"judgment-report missing for trial {trial_id}")

    return issues
