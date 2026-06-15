"""Regression guards for the index-bound constants in adop_types.

Several named constants are bound by tuple index (e.g. IN_TRIAL =
SUMMARY_STATES[4]). Inserting a state earlier in the tuple silently shifts
every later index. These tests fail loudly if that binding drifts.
"""

from __future__ import annotations

import adop_types as t


def test_artifact_types_count_and_new_members():
    assert len(t.ARTIFACT_TYPES) == 13
    for name in (
        "watch-note", "blocked-note", "deprecation-note", "migration-note",
        "archive-note", "coupling-note",
    ):
        assert name in t.ARTIFACT_TYPES


def test_coupling_note_is_not_a_lifecycle_state():
    """coupling-note is orthogonal metadata; it must not appear in SUMMARY_STATES."""
    assert t.COUPLING_NOTE == "coupling-note"
    assert t.COUPLING_NOTE not in t.SUMMARY_STATES
    assert t.ARTIFACT_ID_PREFIX["coupling-note"] == "cp"


def test_artifact_id_prefixes():
    expected = {
        "watch-note": "wt",
        "blocked-note": "bl",
        "deprecation-note": "dp",
        "migration-note": "mg",
        "archive-note": "ar",
    }
    for artifact_type, prefix in expected.items():
        assert t.ARTIFACT_ID_PREFIX[artifact_type] == prefix


def test_named_artifact_constants_match_tuple():
    assert t.WATCH_NOTE == "watch-note"
    assert t.BLOCKED_NOTE == "blocked-note"
    assert t.DEPRECATION_NOTE == "deprecation-note"
    assert t.MIGRATION_NOTE == "migration-note"
    assert t.ARCHIVE_NOTE == "archive-note"


def test_summary_states_order():
    assert t.SUMMARY_STATES == (
        "watch", "proposed", "blocked", "trial-ready", "in-trial",
        "promote", "hold", "reject", "deprecated", "migrating", "archived",
    )


def test_in_trial_index_binding():
    """The fragile binding: IN_TRIAL must stay pinned to the 'in-trial' value."""
    assert t.IN_TRIAL == "in-trial"
    assert t.IN_TRIAL == t.SUMMARY_STATES[4]


def test_extended_state_constants():
    assert t.WATCH == "watch"
    assert t.BLOCKED_STATE == "blocked"
    assert t.DEPRECATED == "deprecated"
    assert t.MIGRATING == "migrating"
    assert t.ARCHIVED == "archived"
