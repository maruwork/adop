#!/usr/bin/env python3
"""ADOP text summary builder."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    from .adop_artifacts import find_by_type, find_judgment_report, load_all_artifacts
    from .adop_ids import parse_numeric_id
    from .adop_state_machine import infer_effective_trial_state
    from .adop_types import (
        CANDIDATE_INTAKE_NOTE,
        COMPARISON_NOTE,
        DECOMPOSITION_DECISION,
        JUDGMENT_REPORT,
        PROPOSED,
        ROOT_CAUSE_HYPOTHESIS,
        STRUCTURAL_GAP,
        SUMMARY_STATES,
        TRIAL_PACKET,
    )
except ImportError:  # pragma: no cover - script import path
    from adop_artifacts import find_by_type, find_judgment_report, load_all_artifacts
    from adop_ids import parse_numeric_id
    from adop_state_machine import infer_effective_trial_state
    from adop_types import (
        CANDIDATE_INTAKE_NOTE,
        COMPARISON_NOTE,
        DECOMPOSITION_DECISION,
        JUDGMENT_REPORT,
        PROPOSED,
        ROOT_CAUSE_HYPOTHESIS,
        STRUCTURAL_GAP,
        SUMMARY_STATES,
        TRIAL_PACKET,
    )


def _id_sort_key(item: dict[str, Any]) -> tuple[int, int, str]:
    """Numeric-aware id sort so "latest" survives ids widening past 3 digits (B31)."""
    raw = str(item.get("artifact_id", ""))
    prefix = raw.split("-", 1)[0] if "-" in raw else ""
    number = parse_numeric_id(raw, prefix) if prefix else None
    if number is None:
        return (1, 0, raw)
    return (0, number, raw)


def _latest_by_scene(items: list[dict[str, Any]], artifact_type: str) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    filtered = [item for item in items if item.get("artifact_type") == artifact_type]
    filtered.sort(key=_id_sort_key)
    for item in filtered:
        scene = str(item.get("related_scene", ""))
        if scene:
            latest[scene] = item
    return latest


def build_summary(root: Path, *, scene: str | None = None, status: str | None = None) -> str:
    items = load_all_artifacts(root)
    # Intake dispositions and trial states are tracked in SEPARATE buckets so a
    # `- hold: N [...]` line never silently mixes intake candidates with trial
    # verdicts (residual B41). Both still render with the same `- {state}: N [..]`
    # line shape used by existing consumers/tests.
    intake_counts: dict[str, list[str]] = defaultdict(list)
    trial_counts: dict[str, list[str]] = defaultdict(list)
    other_trial_states: dict[str, list[str]] = defaultdict(list)

    intake_dispositions = {PROPOSED, "trial-ready", "hold", "reject"}
    for intake in find_by_type(root, CANDIDATE_INTAKE_NOTE):
        if scene and intake.get("related_scene") != scene:
            continue
        intake_state = str(intake.get("current_disposition", PROPOSED))
        if intake_state in intake_dispositions:
            intake_counts[intake_state].append(str(intake.get("candidate_or_tool", "-")))

    for packet in find_by_type(root, TRIAL_PACKET):
        if scene and packet.get("related_scene") != scene:
            continue
        trial_id = packet.get("artifact_id")
        if not trial_id:
            # A packet with no artifact_id cannot be paired to a judgment; skip it
            # rather than emit a phantom "None" row (residual B44).
            continue
        trial_id = str(trial_id)
        judgment = find_judgment_report(root, trial_id)
        effective = infer_effective_trial_state(packet, judgment)
        label = str(packet.get("related_scene", trial_id))
        if effective in SUMMARY_STATES:
            trial_counts[effective].append(label)
        else:
            # An out-of-enum verdict would otherwise vanish (the render loop only
            # iterates SUMMARY_STATES); surface it explicitly (residual B43).
            other_trial_states[effective].append(label)

    lines = ["ADOP Summary"]
    lines.append("Intake Dispositions")
    for state in SUMMARY_STATES:
        if status and state != status:
            continue
        labels = sorted(intake_counts.get(state, []))
        if labels:
            lines.append(f"- {state}: {len(labels)} [{', '.join(labels)}]")
        else:
            lines.append(f"- {state}: 0 [-]")
    lines.append("Trial States")
    for state in SUMMARY_STATES:
        if status and state != status:
            continue
        labels = sorted(trial_counts.get(state, []))
        if labels:
            lines.append(f"- {state}: {len(labels)} [{', '.join(labels)}]")
        else:
            lines.append(f"- {state}: 0 [-]")
    if other_trial_states and not status:
        lines.append("Unrecognized Trial States")
        for state in sorted(other_trial_states):
            labels = sorted(other_trial_states[state])
            lines.append(f"- {state}: {len(labels)} [{', '.join(labels)}]")

    latest_comparisons = _latest_by_scene(items, COMPARISON_NOTE)
    latest_judgments = _latest_by_scene(items, JUDGMENT_REPORT)

    root_cause_lines: list[str] = []
    structural_gap_lines: list[str] = []
    decomposition_lines: list[str] = []
    fit_lane_lines: list[str] = []
    preventive_action_lines: list[str] = []

    for scene_name in sorted(set(latest_comparisons) | set(latest_judgments)):
        if scene and scene_name != scene:
            continue
        comparison = latest_comparisons.get(scene_name, {})
        judgment = latest_judgments.get(scene_name, {})

        hypothesis = str(
            judgment.get(ROOT_CAUSE_HYPOTHESIS)
            or comparison.get(ROOT_CAUSE_HYPOTHESIS)
            or ""
        ).strip()
        if hypothesis:
            root_cause_lines.append(f"- {scene_name}: {hypothesis}")

        structural_gap = str(comparison.get(STRUCTURAL_GAP, "")).strip()
        if structural_gap:
            structural_gap_lines.append(f"- {scene_name}: {structural_gap}")

        decomposition_decision = str(
            judgment.get(DECOMPOSITION_DECISION)
            or comparison.get(DECOMPOSITION_DECISION)
            or ""
        ).strip()
        adoption_unit = str(
            judgment.get("adoption_unit")
            or comparison.get("adoption_unit")
            or ""
        ).strip()
        if decomposition_decision or adoption_unit:
            decomposition_lines.append(
                f"- {scene_name}: {decomposition_decision or '-'} -> {adoption_unit or '-'}"
            )

        recommended_fit_lane = str(
            judgment.get("recommended_fit_lane")
            or comparison.get("recommended_fit_lane")
            or ""
        ).strip()
        if recommended_fit_lane:
            fit_lane_lines.append(f"- {scene_name}: {recommended_fit_lane}")

        preventive_actions = judgment.get("preventive_action", [])
        if isinstance(preventive_actions, list) and preventive_actions:
            preventive_action_lines.append(f"- {scene_name}: {'; '.join(str(item) for item in preventive_actions)}")

    if root_cause_lines:
        lines.append("Root-Cause Signals")
        lines.extend(root_cause_lines)
    if structural_gap_lines:
        lines.append("Structural Gaps")
        lines.extend(structural_gap_lines)
    if decomposition_lines:
        lines.append("Decomposition Decisions")
        lines.extend(decomposition_lines)
    if fit_lane_lines:
        lines.append("Recommended Fit Lanes")
        lines.extend(fit_lane_lines)
    if preventive_action_lines:
        lines.append("Preventive Actions")
        lines.extend(preventive_action_lines)
    return "\n".join(lines)
