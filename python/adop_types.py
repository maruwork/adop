#!/usr/bin/env python3
"""ADOP shared constants and lightweight schema helpers."""

from __future__ import annotations

from typing import Final

SCHEMA_VERSION: Final[int] = 1

ARTIFACT_TYPES: Final[tuple[str, ...]] = (
    "candidate-intake-note",
    "comparison-note",
    "trial-packet",
    "trial-result",
    "reject-note",
    "promotion-note",
    "judgment-report",
)

ARTIFACT_ID_PREFIX: Final[dict[str, str]] = {
    "candidate-intake-note": "ci",
    "comparison-note": "cmp",
    "trial-packet": "tr",
    "trial-result": "tr",
    "reject-note": "rj",
    "promotion-note": "pm",
    "judgment-report": "tr",
}

FILTER_NAMES: Final[tuple[str, ...]] = ("scene_fit", "authority_safe", "controlability")
FILTER_STATUSES: Final[tuple[str, ...]] = ("pass", "conditional", "fail")
CANDIDATE_SHAPES: Final[tuple[str, ...]] = ("atomic", "composite", "unknown")
DECOMPOSITION_DECISIONS: Final[tuple[str, ...]] = ("as-is", "split-required", "reference-only", "reject")
FIT_LANES: Final[tuple[str, ...]] = ("reference-only", "compare", "trial-ready", "reject")
TRIAL_TYPES: Final[tuple[str, ...]] = (
    "read-only",
    "retrospective-comparison",
    "review-assist",
    "isolated-write",
    "task-scoped",
    "phase-scoped",
    "shadow",
    "human-gated",
)
SANDBOX_TYPES: Final[tuple[str, ...]] = (
    "read-only sandbox",
    "review sandbox",
    "isolated write sandbox",
    "task-local sandbox",
    "phase sandbox",
    "shadow sandbox",
)
LANES: Final[tuple[str, ...]] = ("operations", "assistance")
DISPOSITIONS: Final[tuple[str, ...]] = ("proposed", "hold", "reject", "trial-ready")
VERDICTS: Final[tuple[str, ...]] = ("promote", "hold", "reject")
FALLBACKS: Final[tuple[str, ...]] = ("fail-close", "warn", "hold", "reject")
RECURRING_CONTROL_DECISIONS: Final[tuple[str, ...]] = ("yes", "no", "later")
SUMMARY_STATES: Final[tuple[str, ...]] = ("proposed", "trial-ready", "in-trial", "promote", "hold", "reject")

WRITE_TRIAL_TYPES: Final[frozenset[str]] = frozenset({"isolated-write", "task-scoped", "phase-scoped"})
NON_PROMOTE_VERDICTS: Final[frozenset[str]] = frozenset({"hold", "reject"})

# Named artifact type constants — index-bound to ARTIFACT_TYPES (keep in sync with tuple order)
CANDIDATE_INTAKE_NOTE: Final[str] = ARTIFACT_TYPES[0]
COMPARISON_NOTE: Final[str] = ARTIFACT_TYPES[1]
TRIAL_PACKET: Final[str] = ARTIFACT_TYPES[2]
TRIAL_RESULT: Final[str] = ARTIFACT_TYPES[3]
REJECT_NOTE: Final[str] = ARTIFACT_TYPES[4]
PROMOTION_NOTE: Final[str] = ARTIFACT_TYPES[5]
JUDGMENT_REPORT: Final[str] = ARTIFACT_TYPES[6]

# Named filter name constants — index-bound to FILTER_NAMES (keep in sync with tuple order)
SCENE_FIT: Final[str] = FILTER_NAMES[0]
AUTHORITY_SAFE: Final[str] = FILTER_NAMES[1]
CONTROLABILITY: Final[str] = FILTER_NAMES[2]

# Named JSON field name constants — ADOP document field keys (Wave A: ADOP-internal fields)
DECOMPOSITION_DECISION: Final[str] = "decomposition_decision"
ROOT_CAUSE_HYPOTHESIS: Final[str] = "root_cause_hypothesis"
STRUCTURAL_GAP: Final[str] = "structural_gap"
PROPOSED: Final[str] = DISPOSITIONS[0]  # tuple is SSOT

# Named JSON field name constants — Wave B (cross external_tool_adoption_lint boundary)
EVALUATION_GATE: Final[str] = "evaluation_gate"
EXECUTOR: Final[str] = "executor"
LANDING_TARGET: Final[str] = "landing_target"
OBSERVED_EFFECT: Final[str] = "observed_effect"

# Named state constants — Wave C (in-trial / trial-ready SSOT unification)
TRIAL_READY: Final[str] = FIT_LANES[2]    # "trial-ready" — tuple is SSOT
IN_TRIAL: Final[str] = SUMMARY_STATES[2]  # "in-trial" — tuple is SSOT


def empty_filter_assessment() -> dict[str, dict[str, str | None]]:
    return {
        name: {
            "status": "pass",
            "reason": "",
            "constraint": None,
        }
        for name in FILTER_NAMES
    }
