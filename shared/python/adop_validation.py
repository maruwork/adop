#!/usr/bin/env python3
"""ADOP validation helpers."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

try:
    from .adop_artifacts import latest_by_type, load_all_artifacts
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
        COUPLING_CONFIDENCE_LEVELS,
        COUPLING_DETECTION_SOURCES,
        COUPLING_NOTE,
        COUPLING_TYPES,
        COSTS,
        DATA_FLOW_DESTINATIONS,
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
        LANES,
        MIGRATION_NOTE,
        NON_PROMOTE_VERDICTS,
        OBSERVED_EFFECT,
        PROMOTION_NOTE,
        PLATFORMS,
        RECORDING_MODES,
        RECORDING_SOURCES,
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
        WRITE_TRIAL_TYPES,
    )
except ImportError:  # pragma: no cover - script import path
    from adop_artifacts import latest_by_type, load_all_artifacts
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
        COUPLING_CONFIDENCE_LEVELS,
        COUPLING_DETECTION_SOURCES,
        COUPLING_NOTE,
        COUPLING_TYPES,
        COSTS,
        DATA_FLOW_DESTINATIONS,
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
        LANES,
        MIGRATION_NOTE,
        NON_PROMOTE_VERDICTS,
        OBSERVED_EFFECT,
        PROMOTION_NOTE,
        PLATFORMS,
        RECORDING_MODES,
        RECORDING_SOURCES,
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


def _is_unknown_scalar(value: Any) -> bool:
    return str(value or "").strip().lower() == "unknown"


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


def validate_recording_metadata(payload: dict[str, Any]) -> None:
    require_non_empty(payload.get("recording_mode"), "recording_mode")
    require_non_empty(payload.get("recording_source"), "recording_source")
    validate_choice(str(payload.get("recording_mode", "")), "recording_mode", RECORDING_MODES)
    validate_choice(str(payload.get("recording_source", "")), "recording_source", RECORDING_SOURCES)


def validate_tool_attributes(payload: dict[str, Any]) -> None:
    validate_choice(str(payload.get("platform", "")), "platform", PLATFORMS)
    require_non_empty(payload.get("license"), "license")
    validate_choice(str(payload.get("cost", "")), "cost", COSTS)
    require_non_empty(payload.get("version"), "version")
    require_non_empty(payload.get("category"), "category")
    require_non_empty(payload.get("ai_compatibility"), "ai_compatibility")
    data_flow = payload.get("data_flow")
    if not isinstance(data_flow, dict):
        raise AdopValidationError("data_flow must be object", 2)
    validate_choice(
        str(data_flow.get("destination", "")),
        "data_flow.destination",
        DATA_FLOW_DESTINATIONS,
    )
    _require_string_list(data_flow.get("data_types"), "data_flow.data_types")
    if not isinstance(data_flow.get("opt_in"), bool):
        raise AdopValidationError("data_flow.opt_in must be boolean", 2)


def unknown_tool_attribute_fields(payload: dict[str, Any]) -> list[str]:
    unknowns: list[str] = []
    for field in ("platform", "license", "cost", "version", "category", "ai_compatibility"):
        if _is_unknown_scalar(payload.get(field)):
            unknowns.append(field)
    data_flow = payload.get("data_flow")
    if isinstance(data_flow, dict):
        if _is_unknown_scalar(data_flow.get("destination")):
            unknowns.append("data_flow.destination")
        data_types = data_flow.get("data_types")
        if isinstance(data_types, list) and any(_is_unknown_scalar(item) for item in data_types):
            unknowns.append("data_flow.data_types")
    return unknowns


def validate_intake_payload(payload: dict[str, Any]) -> None:
    validate_recording_metadata(payload)
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
    validate_tool_attributes(payload)


def validate_comparison_payload(payload: dict[str, Any]) -> None:
    validate_recording_metadata(payload)
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
    validate_recording_metadata(payload)
    validate_choice(payload["trial_type"], "trial_type", TRIAL_TYPES)
    validate_choice(payload["sandbox_type"], "sandbox_type", SANDBOX_TYPES)
    validate_choice(payload["lane"], "lane", LANES)
    validate_choice(payload["fallback"], "fallback", FALLBACKS)
    for field in (
        "input_surface",
        "output_contract",
        "mutation_boundary",
        "verification_method",
        EXECUTOR,
        "trigger",
        EVALUATION_GATE,
        "writeback_target",
        "decision_owner",
        "landing_target",
    ):
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
    require_non_empty(payload.get("decision_owner"), "decision_owner")
    require_non_empty(payload.get("landing_target"), "landing_target")
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


def validate_coupling_entries(value: Any, field_name: str = "couplings") -> None:
    """Validate the declared tool-to-file coupling list.

    Each entry records one file the tool is entangled with, HOW (coupling_type)
    and how hard it is to detach (removal_cost). The list must be non-empty: a
    coupling-note with no couplings carries no information.
    """
    if not isinstance(value, list) or not value:
        raise AdopValidationError(f"{field_name} must contain at least one coupling", 2)
    for index, entry in enumerate(value):
        where = f"{field_name}[{index}]"
        if not isinstance(entry, dict):
            raise AdopValidationError(f"{where} must be an object", 2)
        require_non_empty(entry.get("path"), f"{where}.path")
        validate_choice(str(entry.get("coupling_type", "")), f"{where}.coupling_type", COUPLING_TYPES)
        validate_choice(str(entry.get("removal_cost", "")), f"{where}.removal_cost", REMOVAL_COSTS)
        if "detection_source" in entry:
            validate_choice(
                str(entry.get("detection_source", "")),
                f"{where}.detection_source",
                COUPLING_DETECTION_SOURCES,
            )
        if "confidence" in entry:
            validate_choice(
                str(entry.get("confidence", "")),
                f"{where}.confidence",
                COUPLING_CONFIDENCE_LEVELS,
            )


def validate_coupling_note_payload(payload: dict[str, Any]) -> None:
    require_non_empty(payload.get("related_scene"), "related_scene")
    require_non_empty(payload.get("candidate_or_tool"), "candidate_or_tool")
    validate_coupling_entries(payload.get("couplings"), "couplings")


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
        if artifact_type == COUPLING_NOTE:
            try:
                validate_coupling_note_payload(item)
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
                validate_recording_metadata(item)
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

        if artifact_type == TRIAL_RESULT:
            try:
                validate_recording_metadata(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
            if not item.get("closed_at"):
                issues.append(f"trial-result {item.get('artifact_id')} missing closed_at")
            if not item.get("related_scene"):
                issues.append(f"trial-result {item.get('artifact_id')} missing related_scene")
            if not item.get("derived_from"):
                issues.append(f"trial-result {item.get('artifact_id')} missing derived_from")
            if not item.get(OBSERVED_EFFECT):
                issues.append(f"trial-result {item.get('artifact_id')} missing {OBSERVED_EFFECT}")

        if artifact_type == PROMOTION_NOTE:
            try:
                validate_recording_metadata(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
            if not item.get("related_scene"):
                issues.append(f"promotion-note {item.get('artifact_id')} missing related_scene")
            if not item.get("derived_from"):
                issues.append(f"promotion-note {item.get('artifact_id')} missing derived_from")
            if not item.get("landing_target"):
                issues.append(f"promotion-note {item.get('artifact_id')} missing landing_target")
            intake = latest_by_type(root, CANDIDATE_INTAKE_NOTE, scene=str(item.get("related_scene", "")))
            if not intake:
                issues.append(f"promotion-note {item.get('artifact_id')} missing candidate-intake-note history")
            else:
                unknowns = unknown_tool_attribute_fields(intake)
                if unknowns:
                    issues.append(
                        f"promotion-note {item.get('artifact_id')} cannot rely on unknown tool attributes "
                        f"from {intake.get('artifact_id')}: {', '.join(unknowns)}"
                    )

        if artifact_type == REJECT_NOTE:
            try:
                validate_recording_metadata(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
            if not item.get("related_scene"):
                issues.append(f"reject-note {item.get('artifact_id')} missing related_scene")
            if not item.get("derived_from"):
                issues.append(f"reject-note {item.get('artifact_id')} missing derived_from")
            if not item.get("reject_reason"):
                issues.append(f"reject-note {item.get('artifact_id')} missing reject_reason")

        if artifact_type == HOLD_NOTE:
            try:
                validate_recording_metadata(item)
            except AdopValidationError as exc:
                issues.append(str(exc))
            if not item.get("related_scene"):
                issues.append(f"hold-note {item.get('artifact_id')} missing related_scene")
            if not item.get("derived_from"):
                issues.append(f"hold-note {item.get('artifact_id')} missing derived_from")
            if not item.get("hold_reason"):
                issues.append(f"hold-note {item.get('artifact_id')} missing hold_reason")

        for parent_id in item.get("derived_from", []):
            expected_ok = any(
                f"{parent_type}::{parent_id}" in by_id
                for parent_type in ARTIFACT_TYPES
            )
            if not expected_ok:
                issues.append(f"derived_from missing target: {parent_id}")

    seen_trial_ids = {str(i["artifact_id"]) for i in items if i.get("artifact_type") == TRIAL_PACKET}
    # Trials that have been closed: a trial-result exists that derives from the packet.
    closed_trial_ids: set[str] = set()
    for item in items:
        if item.get("artifact_type") == TRIAL_RESULT:
            for parent_id in (item.get("derived_from") or []):
                closed_trial_ids.add(str(parent_id))

    for item in items:
        if item.get("artifact_type") == TRIAL_PACKET:
            trial_id = str(item["artifact_id"])
            # Only require a judgment-report for closed trials; open trials are in-progress.
            if trial_id in closed_trial_ids and trial_id not in seen_trial_judgments:
                issues.append(f"judgment-report missing for trial {trial_id}")
        if item.get("artifact_type") == TRIAL_RESULT:
            result_id = str(item.get("artifact_id", ""))
            if result_id not in seen_trial_ids:
                issues.append(f"trial-result {result_id} has no matching trial-packet")

    return issues
