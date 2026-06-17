"""End-to-end CLI tests for the 5 extended lifecycle states.

Each test drives the real argv -> parser -> handler -> validation -> write path
through main(), then inspects the written artifacts on disk. Exit codes follow
the CLI contract: 0 ok, 5 missing artifact / gate not met.
"""

from __future__ import annotations

from conftest import promote_scene

WATCH_NOTE = "watch-note"
BLOCKED_NOTE = "blocked-note"
CANDIDATE_INTAKE_NOTE = "candidate-intake-note"
DEPRECATION_NOTE = "deprecation-note"
MIGRATION_NOTE = "migration-note"
ARCHIVE_NOTE = "archive-note"
HOLD_NOTE = "hold-note"
REJECT_NOTE = "reject-note"


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

def _run_to_open_trial(run, root, *, scene: str = "ci-format", tool: str = "ruff") -> str:
    """Drive a scene through intake → compare → trial; return the trial id."""
    assert run(
        "quick-intake", "--artifact-root", root,
        "--candidate", tool, "--source", "doc",
        "--use-case", scene, "--why-now", "evaluate",
    ) == 0
    assert run(
        "quick-compare", "--artifact-root", root, "--use-case", scene,
        "--candidate", tool, "--candidate", "pylint", "--selected", tool,
    ) == 0
    assert run(
        "quick-trial", "--artifact-root", root, "--use-case", scene,
        "--mode", "read-only-comparison", "--executor", "ci",
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
    trial_id = _run_to_open_trial(run, root, scene="ci-double", tool="black")
    assert run(
        "quick-close-trial", "--artifact-root", root,
        "--trial-id", trial_id, "--verdict", "promote",
        "--observed-effect", "great",
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
    ) == 0
    # Trial is open — lint must pass with no issues.
    assert run("lint", "--artifact-root", root) == 0


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
