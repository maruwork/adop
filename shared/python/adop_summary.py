#!/usr/bin/env python3
"""ADOP text summary builder."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from adop_artifacts import find_by_type, find_judgment_report, load_all_artifacts
from adop_ids import parse_numeric_id
from adop_state_machine import infer_effective_trial_state
from adop_types import (
    ARCHIVE_NOTE,
    ARCHIVED,
    BLOCKED_NOTE,
    BLOCKED_STATE,
    CANDIDATE_INTAKE_NOTE,
    COMPARISON_NOTE,
    COUPLING_NOTE,
    DECOMPOSITION_DECISION,
    DEPRECATED,
    DEPRECATION_NOTE,
    HOLD_NOTE,
    IN_TRIAL,
    JUDGMENT_REPORT,
    MIGRATING,
    MIGRATION_NOTE,
    PROMOTION_NOTE,
    PROPOSED,
    REMOVAL_COSTS,
    ROOT_CAUSE_HYPOTHESIS,
    STRUCTURAL_GAP,
    SUMMARY_STATES,
    TRIAL_PACKET,
    TRIAL_READY,
    WATCH,
    WATCH_NOTE,
)

# Hold / reject are reused by both intake and trial buckets, so they are spelled
# as literals here rather than imported, matching the existing intake_dispositions set.
HOLD = "hold"
REJECT = "reject"
PROMOTE = "promote"

# Each summary section iterates ONLY the states it can legitimately hold, so a
# state that a section can never reach (e.g. a trial is never "watch") no longer
# renders a misleading always-zero line.
INTAKE_STATES: tuple[str, ...] = (PROPOSED, TRIAL_READY, HOLD, REJECT)
TRIAL_STATES: tuple[str, ...] = (IN_TRIAL, PROMOTE, HOLD, REJECT)

# Extended lifecycle states are tracked by dedicated note types, not by intake
# disposition or trial verdict. State = the latest note of this type per scene.
EXTENDED_STATE_NOTES: tuple[tuple[str, str], ...] = (
    (WATCH, WATCH_NOTE),
    (BLOCKED_STATE, BLOCKED_NOTE),
    (DEPRECATED, DEPRECATION_NOTE),
    (MIGRATING, MIGRATION_NOTE),
    (ARCHIVED, ARCHIVE_NOTE),
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


def _resolve_scene_states(root: Path, items: list[dict[str, Any]]) -> dict[str, str]:
    """Resolve each scene to its single current lifecycle state (Case B).

    Resolution uses lifecycle precedence, not timestamps. created_at is
    day-granular and per-type ids are not globally ordered, so "latest artifact
    wins" cannot be read from dates. Instead:
      - the retirement tail (archived > migrating > deprecated > promote) is
        monotonic-forward, so the most-advanced note present wins;
      - block vs. unblock recency is read from derived_from provenance: a scene
        is `blocked` only if no later candidate-intake-note derives from the
        blocked-note.
    A scene-less watch-note is keyed by its tool with a "(watch)" prefix.
    """

    def of_type(scene: str, artifact_type: str) -> list[dict[str, Any]]:
        matched = [
            item for item in items
            if item.get("artifact_type") == artifact_type
            and str(item.get("related_scene", "")).strip() == scene
        ]
        matched.sort(key=_id_sort_key)
        return matched

    scenes = sorted({
        str(item.get("related_scene", "")).strip()
        for item in items
        if str(item.get("related_scene", "")).strip()
    })

    resolved: dict[str, str] = {}
    for scene in scenes:
        if of_type(scene, ARCHIVE_NOTE):
            resolved[scene] = ARCHIVED
        elif of_type(scene, MIGRATION_NOTE):
            resolved[scene] = MIGRATING
        elif of_type(scene, DEPRECATION_NOTE):
            resolved[scene] = DEPRECATED
        elif of_type(scene, PROMOTION_NOTE):
            resolved[scene] = "promote"
        elif _scene_resumed_after_hold(scene, of_type):
            resolved[scene] = TRIAL_READY
        elif of_type(scene, TRIAL_PACKET):
            packet = of_type(scene, TRIAL_PACKET)[-1]
            judgment = find_judgment_report(root, str(packet.get("artifact_id", "")))
            resolved[scene] = str(judgment.get("verdict", IN_TRIAL)) if judgment else IN_TRIAL
        elif _scene_is_blocked(scene, items, of_type):
            resolved[scene] = BLOCKED_STATE
        elif of_type(scene, COMPARISON_NOTE):
            resolved[scene] = TRIAL_READY
        elif of_type(scene, CANDIDATE_INTAKE_NOTE):
            intake = of_type(scene, CANDIDATE_INTAKE_NOTE)[-1]
            resolved[scene] = str(intake.get("current_disposition", PROPOSED))
        elif of_type(scene, WATCH_NOTE):
            resolved[scene] = WATCH

    for note in items:
        if note.get("artifact_type") == WATCH_NOTE and not str(note.get("related_scene", "")).strip():
            resolved.setdefault(f"(watch) {note.get('candidate_or_tool', '-')}", WATCH)

    return resolved


def _scene_is_blocked(scene: str, items: list[dict[str, Any]], of_type) -> bool:
    blocked_notes = of_type(scene, BLOCKED_NOTE)
    if not blocked_notes:
        return False
    blocked_id = blocked_notes[-1].get("artifact_id")
    reopened = any(
        item.get("artifact_type") == CANDIDATE_INTAKE_NOTE
        and blocked_id in (item.get("derived_from") or [])
        for item in items
    )
    return not reopened


def _scene_resumed_after_hold(scene: str, of_type) -> bool:
    hold_notes = of_type(scene, HOLD_NOTE)
    comparisons = of_type(scene, COMPARISON_NOTE)
    if not hold_notes or not comparisons:
        return False

    latest_hold = hold_notes[-1]
    latest_comparison = comparisons[-1]
    derived_from = latest_comparison.get("derived_from") or []
    if latest_hold.get("artifact_id") not in derived_from:
        return False

    latest_packet = of_type(scene, TRIAL_PACKET)
    if not latest_packet:
        return True

    packet_derived_from = latest_packet[-1].get("derived_from") or []
    return latest_comparison.get("artifact_id") not in packet_derived_from


def get_scene_states(root: Path) -> dict[str, str]:
    """Return current lifecycle state per scene. Public entry for CLI status/next commands."""
    items = load_all_artifacts(root)
    return _resolve_scene_states(root, items)


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
    # Scenes with a comparison-note have advanced past the intake stage; their
    # lifecycle state is captured by "Current State by Scene" instead. Showing
    # them in "Intake Dispositions" would create a misleading mismatch (the
    # intake artifact's current_disposition is still "proposed" because artifacts
    # are append-only and compare does not rewrite the intake).
    scenes_past_intake = {
        str(item.get("related_scene", ""))
        for item in items
        if item.get("artifact_type") == COMPARISON_NOTE and str(item.get("related_scene", ""))
    }
    # Count latest intake per (scene, tool) pair to avoid double-counting when
    # quick-intake is run multiple times for the same candidate.
    latest_intake: dict[tuple[str, str], dict] = {}
    for intake in find_by_type(root, CANDIDATE_INTAKE_NOTE):
        if scene and intake.get("related_scene") != scene:
            continue
        intake_scene = str(intake.get("related_scene", ""))
        if intake_scene in scenes_past_intake:
            continue
        key = (intake_scene, str(intake.get("candidate_or_tool", "")))
        # find_by_type returns items in id order; later id wins (append-only).
        latest_intake[key] = intake
    for intake in latest_intake.values():
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

    # Extended lifecycle states (watch / blocked / deprecated / migrating /
    # archived) are not intake dispositions or trial verdicts; each is the latest
    # note of its dedicated type per scene (per tool for a scene-less watch-note).
    lifecycle_counts: dict[str, list[str]] = defaultdict(list)
    for state_name, artifact_type in EXTENDED_STATE_NOTES:
        latest_notes: dict[str, dict[str, Any]] = {}
        notes = [item for item in items if item.get("artifact_type") == artifact_type]
        notes.sort(key=_id_sort_key)
        for note in notes:
            note_scene = str(note.get("related_scene", "")).strip()
            tool = str(note.get("candidate_or_tool", "-"))
            note_key = note_scene or f"tool:{tool}"
            latest_notes[note_key] = note  # later id wins (append-only history)
        for note in latest_notes.values():
            note_scene = str(note.get("related_scene", "")).strip()
            if scene and note_scene != scene:
                continue
            lifecycle_counts[state_name].append(note_scene or str(note.get("candidate_or_tool", "-")))

    def _render_section(title: str, states: tuple[str, ...], counts: dict[str, list[str]]) -> None:
        lines.append(title)
        for state in states:
            if status and state != status:
                continue
            labels = sorted(counts.get(state, []))
            if labels:
                lines.append(f"- {state}: {len(labels)} [{', '.join(labels)}]")
            else:
                lines.append(f"- {state}: 0 [-]")

    lines = ["ADOP Summary"]

    # Headline view: each scene resolved to its single current lifecycle state.
    scene_states = _resolve_scene_states(root, items)
    scene_rows = [
        f"- {label}: {state}"
        for label, state in sorted(scene_states.items())
        if not (scene and label != scene) and not (status and state != status)
    ]
    if scene_rows:
        lines.append("Current State by Scene")
        lines.extend(scene_rows)

    _render_section("Intake Dispositions", INTAKE_STATES, intake_counts)
    _render_section("Trial States", TRIAL_STATES, trial_counts)
    _render_section("Lifecycle Notes", tuple(state for state, _ in EXTENDED_STATE_NOTES), lifecycle_counts)

    # Tool entanglement: latest coupling-note per scene/tool snapshot, headline =
    # worst detachment cost. status filter does not apply (coupling is not a state).
    cost_rank = {cost: rank for rank, cost in enumerate(REMOVAL_COSTS)}
    coupling_notes = [item for item in items if item.get("artifact_type") == COUPLING_NOTE]
    coupling_notes.sort(key=_id_sort_key)
    latest_couplings: dict[tuple[str, str], dict[str, Any]] = {}
    for note in coupling_notes:
        note_scene = str(note.get("related_scene", ""))
        if scene and note_scene != scene:
            continue
        latest_couplings[(note_scene, str(note.get("candidate_or_tool", "")))] = note
    if latest_couplings:
        lines.append("Tool Entanglement")
        for (note_scene, tool) in sorted(latest_couplings):
            entries = latest_couplings[(note_scene, tool)].get("couplings", [])
            worst = max(
                (str(e.get("removal_cost", REMOVAL_COSTS[0])) for e in entries),
                key=lambda c: cost_rank.get(c, 0),
                default=REMOVAL_COSTS[0],
            )
            lines.append(f"- {tool} @ {note_scene}: {len(entries)} file(s), detachment: {worst}")

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
