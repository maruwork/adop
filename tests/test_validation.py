"""Unit tests for the 5 extended-state payload validators.

These pin the required-field contract for each new artifact type, and the
single deliberate exception: watch-note allows an absent related_scene.
"""

from __future__ import annotations

import pytest

from adop_validation import (
    AdopValidationError,
    validate_archive_note_payload,
    validate_blocked_note_payload,
    validate_deprecation_note_payload,
    validate_migration_note_payload,
    validate_watch_note_payload,
)


# --- watch-note: related_scene is intentionally optional -------------------

def test_watch_note_passes_without_scene():
    validate_watch_note_payload({
        "candidate_or_tool": "ruff",
        "interest_reason": "fast",
    })  # must not raise


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


@pytest.mark.parametrize("missing", ["related_scene", "candidate_or_tool", "retirement_reason", "timeline"])
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
