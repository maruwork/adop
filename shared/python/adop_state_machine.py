#!/usr/bin/env python3
"""ADOP lifecycle state helpers."""

from __future__ import annotations

from typing import Any

try:
    from .adop_types import FILTER_NAMES, IN_TRIAL, TRIAL_READY
except ImportError:  # pragma: no cover - script import path
    from adop_types import FILTER_NAMES, IN_TRIAL, TRIAL_READY


def comparison_ready_for_trial(comparison: dict[str, Any]) -> bool:
    if comparison.get("recommended_fit_lane") != TRIAL_READY:
        return False
    assessment = comparison.get("filter_assessment", {})
    for key in FILTER_NAMES:
        section = assessment.get(key, {})
        if section.get("status") == "fail":
            return False
    return True


def infer_effective_trial_state(packet: dict[str, Any], judgment_report: dict[str, Any] | None) -> str:
    if judgment_report:
        return str(judgment_report.get("verdict", IN_TRIAL))
    return IN_TRIAL


def promote_gate_errors(packet: dict[str, Any], close_payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if close_payload["verdict"] != "promote":
        return errors
    if not close_payload.get("next_action"):
        errors.append("promote requires next_action")
    if not close_payload.get("decision_owner"):
        errors.append("promote requires decision_owner")
    if not close_payload.get("landing_target"):
        errors.append("promote requires landing_target")
    if not packet.get("writeback_target"):
        errors.append("promote requires writeback_target")
    if not packet.get("verification_method"):
        errors.append("promote requires verification_method")
    if not close_payload.get("recurring_control_decision"):
        errors.append("promote requires recurring_control_decision")
    return errors
