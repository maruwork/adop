#!/usr/bin/env python3
"""ADOP shared constants and lightweight schema helpers."""

from __future__ import annotations

from typing import Final

SCHEMA_VERSION: Final[int] = 1

ARTIFACT_TYPES: Final[tuple[str, ...]] = (
    "candidate-intake-note",  # [0]
    "comparison-note",        # [1]
    "trial-packet",           # [2]
    "trial-result",           # [3]
    "reject-note",            # [4]
    "promotion-note",         # [5]
    "judgment-report",        # [6]
    "watch-note",             # [7]
    "blocked-note",           # [8]
    "deprecation-note",       # [9]
    "migration-note",         # [10]
    "archive-note",           # [11]
    "coupling-note",          # [12] — orthogonal metadata, NOT a lifecycle state
    "hold-note",              # [13] — trial closed with hold verdict (distinct from reject-note)
)

ARTIFACT_ID_PREFIX: Final[dict[str, str]] = {
    "candidate-intake-note": "ci",
    "comparison-note": "cmp",
    "trial-packet": "tr",
    "trial-result": "tr",
    "reject-note": "rj",
    "promotion-note": "pm",
    "judgment-report": "tr",
    "watch-note": "wt",
    "blocked-note": "bl",
    "deprecation-note": "dp",
    "migration-note": "mg",
    "archive-note": "ar",
    "coupling-note": "cp",
    "hold-note": "hl",
}

# Tool-to-file coupling vocabulary (declared entanglement; see coupling-note).
# COUPLING_TYPES = HOW the tool is entangled with a file.
COUPLING_TYPES: Final[tuple[str, ...]] = (
    "config",        # tool configuration lives in the file
    "import",        # source imports the tool as a dependency
    "invocation",    # file calls/runs the tool (CI step, script, hook)
    "generated",     # file is generated/owned by the tool
    "data-write",    # tool writes runtime data into the file
    "reference",     # file hardcodes a path/name reference to the tool
)
# REMOVAL_COSTS = the "癒着度": how hard it is to detach the tool from the file.
REMOVAL_COSTS: Final[tuple[str, ...]] = (
    "clean",         # remove/disable with no edits to other content
    "edit",          # requires targeted edits to the file
    "entangled",     # pervasive; removal is risky or large
)
PLATFORMS: Final[tuple[str, ...]] = (
    "windows",
    "mac",
    "linux",
    "any",
    "unknown",
)
COSTS: Final[tuple[str, ...]] = (
    "free",
    "paid",
    "freemium",
    "unknown",
)
DATA_FLOW_DESTINATIONS: Final[tuple[str, ...]] = (
    "local",
    "vendor-api",
    "third-party",
    "unknown",
)
RECORDING_MODES: Final[tuple[str, ...]] = (
    "guided",
    "explicit",
)
RECORDING_SOURCES: Final[tuple[str, ...]] = (
    "manual-cli",
    "quick-intake",
    "quick-compare",
    "quick-trial",
    "quick-close-trial",
    "unblock",
)

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
SUMMARY_STATES: Final[tuple[str, ...]] = (
    "watch",       # [0]
    "proposed",    # [1]
    "blocked",     # [2]
    "trial-ready", # [3]
    "in-trial",    # [4]
    "promote",     # [5]
    "hold",        # [6]
    "reject",      # [7]
    "deprecated",  # [8]
    "migrating",   # [9]
    "archived",    # [10]
)

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
WATCH_NOTE: Final[str] = ARTIFACT_TYPES[7]
BLOCKED_NOTE: Final[str] = ARTIFACT_TYPES[8]
DEPRECATION_NOTE: Final[str] = ARTIFACT_TYPES[9]
MIGRATION_NOTE: Final[str] = ARTIFACT_TYPES[10]
ARCHIVE_NOTE: Final[str] = ARTIFACT_TYPES[11]
COUPLING_NOTE: Final[str] = ARTIFACT_TYPES[12]
HOLD_NOTE: Final[str] = ARTIFACT_TYPES[13]

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
IN_TRIAL: Final[str] = SUMMARY_STATES[4]  # "in-trial" — tuple is SSOT

# Named state constants for extended lifecycle states
WATCH: Final[str] = SUMMARY_STATES[0]      # "watch"
BLOCKED_STATE: Final[str] = SUMMARY_STATES[2]  # "blocked"
DEPRECATED: Final[str] = SUMMARY_STATES[8]  # "deprecated"
MIGRATING: Final[str] = SUMMARY_STATES[9]   # "migrating"
ARCHIVED: Final[str] = SUMMARY_STATES[10]   # "archived"


def empty_filter_assessment() -> dict[str, dict[str, str | None]]:
    return {
        name: {
            "status": "pass",
            "reason": "",
            "constraint": None,
        }
        for name in FILTER_NAMES
    }
