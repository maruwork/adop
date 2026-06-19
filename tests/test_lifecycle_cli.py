"""End-to-end CLI tests for the 5 extended lifecycle states.

Each test drives the real argv -> parser -> handler -> validation -> write path
through main(), then inspects the written artifacts on disk. Exit codes follow
the CLI contract: 0 ok, 5 missing artifact / gate not met.
"""

from __future__ import annotations

import json
from pathlib import Path

from conftest import promote_scene
from adop_validation import lint_artifact_root

WATCH_NOTE = "watch-note"
BLOCKED_NOTE = "blocked-note"
CANDIDATE_INTAKE_NOTE = "candidate-intake-note"
DEPRECATION_NOTE = "deprecation-note"
MIGRATION_NOTE = "migration-note"
ARCHIVE_NOTE = "archive-note"
HOLD_NOTE = "hold-note"
REJECT_NOTE = "reject-note"
TRIAL_PACKET = "trial-packet"


# --- watch -----------------------------------------------------------------

def test_watch_without_scene_succeeds(run, root, latest):
    """watch-note is the only type where related_scene is optional."""
    assert run(
        "watch", "--artifact-root", root,
        "--candidate", "ruff", "--interest-reason", "fast linter candidate",
    ) == 0
    note = latest(root, WATCH_NOTE)
    assert note is not None
    assert note["artifact_id"].startswith("wt-")
    assert note["candidate_or_tool"] == "ruff"
    assert "related_scene" not in note


def test_watch_with_scene_records_related_scene(run, root, latest):
    assert run(
        "watch", "--artifact-root", root,
        "--candidate", "ruff", "--interest-reason", "speed",
        "--use-case", "lint-pipeline",
    ) == 0
    note = latest(root, WATCH_NOTE, scene="lint-pipeline")
    assert note is not None
    assert note["related_scene"] == "lint-pipeline"


# --- block / unblock -------------------------------------------------------

def test_block_requires_intake(run, root):
    """Blocking a scene with no candidate-intake-note is a missing-artifact gate."""
    assert run(
        "block", "--artifact-root", root, "--use-case", "type-check",
        "--block-reason", "no budget", "--unblock-condition", "Q3 budget",
        "--owner", "lead",
    ) == 5


def test_block_then_unblock_chain(run, root, latest):
    assert run(
        "quick-intake", "--artifact-root", root, "--candidate", "mypy",
        "--source", "doc", "--use-case", "type-check", "--why-now", "strict typing",
    ) == 0
    assert run(
        "block", "--artifact-root", root, "--use-case", "type-check",
        "--block-reason", "no budget", "--unblock-condition", "Q3 budget",
        "--owner", "lead",
    ) == 0
    blocked = latest(root, BLOCKED_NOTE, scene="type-check")
    assert blocked["artifact_id"].startswith("bl-")
    assert blocked["candidate_or_tool"] == "mypy"

    # unblock re-enters the proposed lane via a fresh candidate-intake-note
    assert run(
        "unblock", "--artifact-root", root, "--use-case", "type-check",
        "--why-unblocked", "budget approved",
    ) == 0
    reentry = latest(root, CANDIDATE_INTAKE_NOTE, scene="type-check")
    assert reentry["candidate_or_tool"] == "mypy"
    assert reentry["source"] == "unblock"


# --- deprecate / migrate / archive gates -----------------------------------

def test_deprecate_requires_promotion(run, root):
    assert run(
        "deprecate", "--artifact-root", root, "--use-case", "lint",
        "--retirement-reason", "x", "--replacement-candidate", "ruff",
        "--timeline", "Q3",
    ) == 5


def test_migrate_requires_deprecation(run, root):
    promote_scene(run, root)
    assert run(
        "migrate", "--artifact-root", root, "--use-case", "lint",
        "--migration-target", "ruff", "--migration-plan", "switch config",
    ) == 5


def test_archive_requires_deprecation_or_migration(run, root):
    promote_scene(run, root)
    assert run(
        "archive", "--artifact-root", root, "--use-case", "lint",
        "--end-date", "2026-09-30",
    ) == 5


# --- full retirement chain -------------------------------------------------

def test_full_retirement_chain(run, root, latest):
    promote_scene(run, root, scene="lint", tool="pylint")

    assert run(
        "deprecate", "--artifact-root", root, "--use-case", "lint",
        "--retirement-reason", "ruff is faster",
        "--replacement-candidate", "ruff", "--timeline", "end of Q3",
    ) == 0
    assert run(
        "migrate", "--artifact-root", root, "--use-case", "lint",
        "--migration-target", "ruff", "--migration-plan", "switch config and CI",
    ) == 0
    assert run(
        "archive", "--artifact-root", root, "--use-case", "lint",
        "--end-date", "2026-09-30", "--successor-tool", "ruff",
    ) == 0

    dp = latest(root, DEPRECATION_NOTE, scene="lint")
    mg = latest(root, MIGRATION_NOTE, scene="lint")
    ar = latest(root, ARCHIVE_NOTE, scene="lint")

    # candidate_or_tool must resolve to the selected tool, not the observed_effect
    assert dp["candidate_or_tool"] == "pylint"
    assert mg["candidate_or_tool"] == "pylint"
    assert ar["candidate_or_tool"] == "pylint"

    # provenance: each note derives from the previous stage
    assert dp["derived_from"] == ["pm-001"]
    assert mg["derived_from"] == [dp["artifact_id"]]
    assert ar["derived_from"] == [mg["artifact_id"]]
    assert ar["successor_tool"] == "ruff"


def test_lint_passes_on_full_chain(run, root):
    promote_scene(run, root)
    run("deprecate", "--artifact-root", root, "--use-case", "lint",
        "--retirement-reason", "x", "--replacement-candidate", "ruff", "--timeline", "Q3")
    run("migrate", "--artifact-root", root, "--use-case", "lint",
        "--migration-target", "ruff", "--migration-plan", "p")
    run("archive", "--artifact-root", root, "--use-case", "lint", "--end-date", "2026-09-30")
    assert run("lint", "--artifact-root", root) == 0


# --- close-trial: hold / reject --------------------------------------------

def _run_to_open_trial(run, root, *, scene: str = "ci-format", tool: str = "ruff", known_attrs: bool = False) -> str:
    """Drive a scene through intake → compare → trial; return the trial id."""
    intake_args = [
        "quick-intake", "--artifact-root", root,
        "--candidate", tool, "--source", "doc",
        "--use-case", scene, "--why-now", "evaluate",
    ]
    if known_attrs:
        intake_args += [
            "--platform", "any",
            "--license", "MIT",
            "--cost", "free",
            "--version", "1.0.0",
            "--category", "cli",
            "--ai-compatibility", "any",
            "--data-flow-json", '{"destination":"local","data_types":["code"],"opt_in":true}',
        ]
    assert run(*intake_args) == 0
    assert run(
        "quick-compare", "--artifact-root", root, "--use-case", scene,
        "--candidate", tool, "--candidate", "pylint", "--selected", tool,
    ) == 0
    assert run(
        "quick-trial", "--artifact-root", root, "--use-case", scene,
        "--mode", "read-only-comparison", "--executor", "ci",
        "--decision-owner", "lead", "--landing-target", f"tooling/{scene}",
    ) == 0
    return "tr-001"


def test_close_trial_hold_generates_hold_note(run, root, latest):
    trial_id = _run_to_open_trial(run, root)
    assert run(
        "quick-close-trial", "--artifact-root", root,
        "--trial-id", trial_id,
        "--verdict", "hold",
        "--observed-effect", "inconclusive — needs more data",
    ) == 0
    note = latest(root, HOLD_NOTE)
    assert note is not None
    assert note["artifact_id"].startswith("hl-")
    assert note["artifact_type"] == HOLD_NOTE
    assert note["derived_from"] == [trial_id]
    assert note.get("hold_reason")


def test_close_trial_reject_generates_reject_note(run, root, latest):
    trial_id = _run_to_open_trial(run, root, scene="ci-lint", tool="pylint")
    assert run(
        "quick-close-trial", "--artifact-root", root,
        "--trial-id", trial_id,
        "--verdict", "reject",
        "--observed-effect", "too slow for our use case",
    ) == 0
    note = latest(root, REJECT_NOTE)
    assert note is not None
    assert note["artifact_id"].startswith("rj-")
    assert note["artifact_type"] == REJECT_NOTE
    assert note["derived_from"] == [trial_id]
    assert note.get("reject_reason")


def test_close_trial_double_close_is_rejected(run, root):
    trial_id = _run_to_open_trial(run, root, scene="ci-double", tool="black", known_attrs=True)
    assert run(
        "quick-close-trial", "--artifact-root", root,
        "--trial-id", trial_id, "--verdict", "promote",
        "--observed-effect", "great",
        "--judgment-reason", "trial succeeded for the bounded scene",
        "--next-action", "promote the formatter into CI",
        "--recurring-control-decision", "yes",
        "--root-cause-hypothesis", "the project needed a stable formatter path",
        "--preventive-action", "document the approved formatter usage scene",
        "--why-this-problem-recurred", "the team had no prior explicit formatter adoption record",
    ) == 0
    # Second close of the same trial must fail with exit 5.
    assert run(
        "quick-close-trial", "--artifact-root", root,
        "--trial-id", trial_id, "--verdict", "reject",
        "--observed-effect", "retroactive",
    ) == 5


def test_compare_after_hold_links_hold_note(run, root, latest):
    """comparison-note created after a hold must derive from the hold-note."""
    trial_id = _run_to_open_trial(run, root, scene="hold-resume", tool="ruff")
    assert run(
        "quick-close-trial", "--artifact-root", root,
        "--trial-id", trial_id, "--verdict", "hold",
        "--observed-effect", "inconclusive",
    ) == 0
    hold = latest(root, HOLD_NOTE, scene="hold-resume")
    assert hold is not None

    assert run(
        "quick-compare", "--artifact-root", root, "--use-case", "hold-resume",
        "--candidate", "ruff", "--candidate", "pylint", "--selected", "ruff",
    ) == 0
    cmp = latest(root, "comparison-note", scene="hold-resume")
    assert cmp is not None
    assert hold["artifact_id"] in cmp["derived_from"]


def test_lint_passes_on_open_trial(run, root):
    """lint must not report judgment-report missing while a trial is still in progress."""
    assert run(
        "quick-intake", "--artifact-root", root,
        "--candidate", "ruff", "--source", "doc",
        "--use-case", "in-flight", "--why-now", "evaluate",
    ) == 0
    assert run(
        "quick-compare", "--artifact-root", root, "--use-case", "in-flight",
        "--candidate", "ruff", "--candidate", "pylint", "--selected", "ruff",
    ) == 0
    assert run(
        "quick-trial", "--artifact-root", root, "--use-case", "in-flight",
        "--mode", "read-only-comparison", "--executor", "ci",
        "--decision-owner", "lead", "--landing-target", "ci/in-flight",
    ) == 0
    # Trial is open — lint must pass with no issues.
    assert run("lint", "--artifact-root", root) == 0


def test_quick_trial_persists_owner_and_landing_target(run, root, latest):
    trial_id = _run_to_open_trial(run, root, scene="landing-proof", tool="ruff")
    packet = latest(root, TRIAL_PACKET, scene="landing-proof")
    assert packet is not None
    assert packet["artifact_id"] == trial_id
    assert packet["decision_owner"] == "lead"
    assert packet["landing_target"] == "tooling/landing-proof"


def test_unblock_generates_lint_clean_intake(run, root):
    """unblock re-enters proposed via a new intake that passes lint."""
    assert run(
        "quick-intake", "--artifact-root", root,
        "--candidate", "mypy", "--source", "doc",
        "--use-case", "typing", "--why-now", "strict mode",
    ) == 0
    assert run(
        "block", "--artifact-root", root, "--use-case", "typing",
        "--block-reason", "no budget", "--unblock-condition", "Q3",
        "--owner", "lead",
    ) == 0
    assert run(
        "unblock", "--artifact-root", root, "--use-case", "typing",
        "--why-unblocked", "budget approved",
    ) == 0
    # The re-entry intake written by unblock must satisfy lint.
    assert run("lint", "--artifact-root", root) == 0


def test_quick_promote_requires_explicit_judgment_fields(run, root):
    trial_id = _run_to_open_trial(run, root, scene="ci-promote-check", tool="ruff")
    assert run(
        "quick-close-trial", "--artifact-root", root,
        "--trial-id", trial_id, "--verdict", "promote",
        "--observed-effect", "works",
    ) == 2


def test_promote_requires_known_tool_attributes(run, root):
    trial_id = _run_to_open_trial(run, root, scene="ci-promote-known-fields", tool="ruff")
    assert run(
        "quick-close-trial", "--artifact-root", root,
        "--trial-id", trial_id, "--verdict", "promote",
        "--observed-effect", "works",
        "--judgment-reason", "trial succeeded for the bounded scene",
        "--next-action", "promote the formatter into CI",
        "--recurring-control-decision", "yes",
        "--root-cause-hypothesis", "the project needed a stable formatter path",
        "--preventive-action", "document the approved formatter usage scene",
        "--why-this-problem-recurred", "the team had no prior explicit formatter adoption record",
    ) == 7


def test_lint_flags_promoted_unknown_tool_attributes(run, root, latest):
    promote_scene(run, root, scene="lint", tool="pylint")
    intake = latest(root, CANDIDATE_INTAKE_NOTE, scene="lint")
    assert intake is not None
    path = Path(str(intake["_adop_path"]))
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["license"] = "unknown"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    issues = lint_artifact_root(Path(root))
    assert any("unknown tool attributes" in issue and "license" in issue for issue in issues)


def test_reject_terminal_blocks_same_scene_reentry(run, root):
    trial_id = _run_to_open_trial(run, root, scene="ci-reject-terminal", tool="ruff")
    assert run(
        "quick-close-trial", "--artifact-root", root,
        "--trial-id", trial_id, "--verdict", "reject",
        "--observed-effect", "too slow for our use case",
    ) == 0
    assert run(
        "quick-intake", "--artifact-root", root,
        "--candidate", "ruff", "--source", "doc",
        "--use-case", "ci-reject-terminal", "--why-now", "retrying anyway",
    ) == 7


def test_quick_intake_defaults_tool_attributes_and_guided_mode(run, root, latest):
    assert run(
        "quick-intake", "--artifact-root", root,
        "--candidate", "tool-a", "--source", "doc",
        "--use-case", "guided-intake", "--why-now", "evaluate",
    ) == 0
    intake = latest(root, CANDIDATE_INTAKE_NOTE, scene="guided-intake")
    assert intake is not None
    assert intake["recording_mode"] == "guided"
    assert intake["recording_source"] == "quick-intake"
    assert intake["platform"] == "unknown"
    assert intake["license"] == "unknown"
    assert intake["cost"] == "unknown"
    assert intake["version"] == "unknown"
    assert intake["category"] == "unknown"
    assert intake["ai_compatibility"] == "unknown"
    assert intake["data_flow"] == {
        "destination": "unknown",
        "data_types": ["unknown"],
        "opt_in": True,
    }


def test_quick_intake_normalizes_casual_platform_aliases(run, root, latest):
    assert run(
        "quick-intake", "--artifact-root", root,
        "--candidate", "tool-b", "--source", "doc",
        "--use-case", "guided-platform", "--why-now", "evaluate",
        "--platform", "python",
    ) == 0
    intake = latest(root, CANDIDATE_INTAKE_NOTE, scene="guided-platform")
    assert intake is not None
    assert intake["platform"] == "any"


def test_reject_from_proposed_resolves_reject(run, root):
    from adop_summary import get_scene_states
    from pathlib import Path
    assert run("quick-intake", "--artifact-root", root, "--candidate", "R", "--source", "doc",
               "--use-case", "r", "--why-now", "x") == 0
    assert run("reject", "--artifact-root", root, "--use-case", "r", "--reject-reason", "not worth it") == 0
    assert get_scene_states(Path(root)).get("r") == "reject"


def test_reject_from_blocked_resolves_reject(run, root):
    from adop_summary import get_scene_states
    from pathlib import Path
    assert run("quick-intake", "--artifact-root", root, "--candidate", "R", "--source", "doc",
               "--use-case", "r", "--why-now", "x") == 0
    assert run("block", "--artifact-root", root, "--use-case", "r", "--block-reason", "lic",
               "--unblock-condition", "u", "--owner", "o") == 0
    assert run("reject", "--artifact-root", root, "--use-case", "r", "--reject-reason", "permanent block") == 0
    assert get_scene_states(Path(root)).get("r") == "reject"


def test_reject_is_terminal_blocks_reintake(run, root):
    assert run("quick-intake", "--artifact-root", root, "--candidate", "R", "--source", "doc",
               "--use-case", "r", "--why-now", "x") == 0
    assert run("reject", "--artifact-root", root, "--use-case", "r", "--reject-reason", "no") == 0
    assert run("quick-intake", "--artifact-root", root, "--candidate", "R", "--source", "doc",
               "--use-case", "r", "--why-now", "again") == 7


def test_reject_requires_history(run, root):
    assert run("reject", "--artifact-root", root, "--use-case", "empty", "--reject-reason", "no") == 5


def test_reject_open_trial_directs_to_close(run, root):
    assert run("quick-intake", "--artifact-root", root, "--candidate", "R", "--source", "doc",
               "--use-case", "r", "--why-now", "x") == 0
    assert run("quick-compare", "--artifact-root", root, "--use-case", "r",
               "--candidate", "R", "--candidate", "S", "--selected", "R") == 0
    assert run("quick-trial", "--artifact-root", root, "--use-case", "r", "--mode", "review-assist",
               "--executor", "ci", "--decision-owner", "o", "--landing-target", "x") == 0
    assert run("reject", "--artifact-root", root, "--use-case", "r", "--reject-reason", "no") == 7
