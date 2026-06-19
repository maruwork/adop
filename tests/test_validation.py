"""Unit tests for the 5 extended-state payload validators.

These pin the required-field contract for each new artifact type, and the
single deliberate exception: watch-note allows an absent related_scene.
"""

from __future__ import annotations

import pytest
from adop_validation import (
    AdopValidationError,
    unknown_tool_attribute_fields,
    validate_archive_note_payload,
    validate_blocked_note_payload,
    validate_deprecation_note_payload,
    validate_intake_payload,
    validate_migration_note_payload,
    validate_watch_note_payload,
)

# --- watch-note: related_scene is intentionally optional -------------------


def test_watch_note_passes_without_scene():
    validate_watch_note_payload(
        {
            "candidate_or_tool": "ruff",
            "interest_reason": "fast",
        }
    )  # must not raise


def test_watch_note_requires_candidate():
    with pytest.raises(AdopValidationError):
        validate_watch_note_payload({"interest_reason": "fast"})


def test_watch_note_requires_interest_reason():
    with pytest.raises(AdopValidationError):
        validate_watch_note_payload({"candidate_or_tool": "ruff"})


# --- blocked-note: all five fields required --------------------------------

BLOCKED_FULL = {
    "related_scene": "type-check",
    "candidate_or_tool": "mypy",
    "block_reason": "no budget",
    "unblock_condition": "Q3 budget",
    "owner": "lead",
}


@pytest.mark.parametrize("missing", sorted(BLOCKED_FULL))
def test_blocked_note_requires_each_field(missing):
    payload = {k: v for k, v in BLOCKED_FULL.items() if k != missing}
    with pytest.raises(AdopValidationError):
        validate_blocked_note_payload(payload)


def test_blocked_note_full_passes():
    validate_blocked_note_payload(dict(BLOCKED_FULL))


# --- deprecation-note ------------------------------------------------------

DEPRECATION_FULL = {
    "related_scene": "lint",
    "candidate_or_tool": "pylint",
    "retirement_reason": "ruff is faster",
    "replacement_candidates": ["ruff"],
    "timeline": "Q3",
}


@pytest.mark.parametrize(
    "missing", ["related_scene", "candidate_or_tool", "retirement_reason", "timeline"]
)
def test_deprecation_note_requires_scalar_fields(missing):
    payload = {k: v for k, v in DEPRECATION_FULL.items() if k != missing}
    with pytest.raises(AdopValidationError):
        validate_deprecation_note_payload(payload)


def test_deprecation_note_full_passes():
    validate_deprecation_note_payload(dict(DEPRECATION_FULL))


def test_deprecation_note_rejects_empty_replacement_list():
    """Retirement must name at least one replacement candidate — empty is rejected."""
    payload = dict(DEPRECATION_FULL, replacement_candidates=[])
    with pytest.raises(AdopValidationError):
        validate_deprecation_note_payload(payload)


# --- migration-note --------------------------------------------------------

MIGRATION_FULL = {
    "related_scene": "lint",
    "candidate_or_tool": "pylint",
    "migration_target": "ruff",
    "migration_plan": "switch config",
}


@pytest.mark.parametrize("missing", sorted(MIGRATION_FULL))
def test_migration_note_requires_each_field(missing):
    payload = {k: v for k, v in MIGRATION_FULL.items() if k != missing}
    with pytest.raises(AdopValidationError):
        validate_migration_note_payload(payload)


def test_migration_note_full_passes():
    validate_migration_note_payload(dict(MIGRATION_FULL))


# --- archive-note: successor_tool optional ---------------------------------

ARCHIVE_FULL = {
    "related_scene": "lint",
    "candidate_or_tool": "pylint",
    "end_date": "2026-09-30",
}


@pytest.mark.parametrize("missing", sorted(ARCHIVE_FULL))
def test_archive_note_requires_each_field(missing):
    payload = {k: v for k, v in ARCHIVE_FULL.items() if k != missing}
    with pytest.raises(AdopValidationError):
        validate_archive_note_payload(payload)


def test_archive_note_passes_without_successor():
    validate_archive_note_payload(dict(ARCHIVE_FULL))  # successor_tool optional


INTAKE_FULL = {
    "recording_mode": "explicit",
    "recording_source": "manual-cli",
    "candidate_or_tool": "ruff",
    "source": "doc",
    "related_scene": "lint",
    "intended_lane": "assistance",
    "intake_reason": "evaluate",
    "root_cause_hypothesis": "the team needs a bounded lint evaluation lane",
    "current_disposition": "proposed",
    "candidate_shape": "atomic",
    "platform": "any",
    "license": "MIT",
    "cost": "free",
    "version": "0.5.0",
    "category": "cli",
    "ai_compatibility": "any",
    "data_flow": {
        "destination": "local",
        "data_types": ["code"],
        "opt_in": True,
    },
}


def test_intake_requires_tool_attributes():
    payload = dict(INTAKE_FULL)
    del payload["platform"]
    with pytest.raises(AdopValidationError):
        validate_intake_payload(payload)


def test_intake_with_tool_attributes_passes():
    validate_intake_payload(dict(INTAKE_FULL))


def test_intake_requires_recording_metadata():
    payload = dict(INTAKE_FULL)
    del payload["recording_mode"]
    with pytest.raises(AdopValidationError):
        validate_intake_payload(payload)


def test_unknown_tool_attribute_fields_detects_all_unknowns():
    payload = dict(INTAKE_FULL)
    payload.update(
        {
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
    )
    assert unknown_tool_attribute_fields(payload) == [
        "platform",
        "license",
        "cost",
        "version",
        "category",
        "ai_compatibility",
        "data_flow.destination",
        "data_flow.data_types",
    ]


def test_task_scoped_write_trial_requires_isolated_sandbox(run, root):
    assert (
        run(
            "quick-intake",
            "--artifact-root",
            root,
            "--candidate",
            "W",
            "--source",
            "doc",
            "--use-case",
            "w",
            "--why-now",
            "x",
        )
        == 0
    )
    assert (
        run(
            "quick-compare",
            "--artifact-root",
            root,
            "--use-case",
            "w",
            "--candidate",
            "W",
            "--candidate",
            "V",
            "--selected",
            "W",
        )
        == 0
    )
    common = [
        "start-trial",
        "--artifact-root",
        root,
        "--scene",
        "w",
        "--allow-project-impact",
        "--trial-type",
        "task-scoped",
        "--lane",
        "operations",
        "--input-surface",
        "i",
        "--output-contract",
        "o",
        "--mutation-boundary",
        "writes",
        "--verification-method",
        "v",
        "--executor",
        "ci",
        "--trigger",
        "t",
        "--evaluation-gate",
        "g",
        "--landing-target",
        "lt",
        "--writeback-target",
        "wb",
        "--decision-owner",
        "d",
        "--fallback",
        "warn",
    ]
    assert run(*common, "--sandbox-type", "review sandbox") == 13
    assert run(*common, "--sandbox-type", "isolated write sandbox") == 0


# --- schema version tolerance (durability across adop versions) -------------


def _schema_item(version):
    return {
        "schema_version": version,
        "artifact_type": "watch-note",
        "artifact_id": "wt-001",
        "created_at": "2026-01-01",
    }


def test_current_schema_version_is_valid():
    from adop_types import SCHEMA_VERSION
    from adop_validation import validate_artifact_schema

    validate_artifact_schema(_schema_item(SCHEMA_VERSION))  # must not raise


def test_future_schema_version_says_newer_not_invalid():
    import pytest
    from adop_types import SCHEMA_VERSION
    from adop_validation import AdopValidationError, validate_artifact_schema

    with pytest.raises(AdopValidationError) as exc:
        validate_artifact_schema(_schema_item(SCHEMA_VERSION + 1))
    assert "newer adop" in str(exc.value)


def test_bad_schema_version_is_invalid():
    import pytest
    from adop_validation import AdopValidationError, validate_artifact_schema

    for bad in (0, -1, "1", 1.0, True, None):
        with pytest.raises(AdopValidationError):
            validate_artifact_schema(_schema_item(bad))
