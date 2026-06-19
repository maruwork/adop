"""Tests for summary rendering of the extended lifecycle states.

Pins two things the previous summary got wrong:
  1. The 5 new states are actually counted (watch-note etc. are no longer 0).
  2. Each section iterates only its legitimate states, so a trial never renders
     a misleading "watch: 0" line and intake never renders "archived: 0".
"""

from __future__ import annotations

from pathlib import Path

import adop_summary
from conftest import promote_scene


def _summary(root: str, **kwargs) -> str:
    return adop_summary.build_summary(Path(root), **kwargs)


def _section(text: str, title: str) -> list[str]:
    """Return the '- ...' lines under a section header."""
    out: list[str] = []
    in_section = False
    headers = {
        "ADOP Summary", "Current State by Scene", "Intake Dispositions", "Trial States",
        "Lifecycle Notes", "Unrecognized Trial States", "Root-Cause Signals",
        "Structural Gaps", "Decomposition Decisions", "Recommended Fit Lanes",
        "Preventive Actions",
    }
    for line in text.splitlines():
        if line == title:
            in_section = True
            continue
        if line in headers:
            in_section = False
        if in_section and line.startswith("- "):
            out.append(line)
    return out


def test_watch_note_is_counted(run, root):
    run("watch", "--artifact-root", root, "--candidate", "ruff", "--interest-reason", "speed")
    lifecycle = _section(_summary(root), "Lifecycle Notes")
    assert "- watch: 1 [ruff]" in lifecycle


def test_new_states_absent_from_intake_and_trial_sections(run, root):
    run("watch", "--artifact-root", root, "--candidate", "ruff", "--interest-reason", "x")
    text = _summary(root)
    intake = _section(text, "Intake Dispositions")
    trial = _section(text, "Trial States")
    # the extended states must not pollute these two sections at all
    for state in ("watch", "blocked", "deprecated", "migrating", "archived"):
        assert not any(line.startswith(f"- {state}:") for line in intake)
        assert not any(line.startswith(f"- {state}:") for line in trial)


def test_retirement_chain_shows_each_note(run, root):
    promote_scene(run, root, scene="lint", tool="pylint")
    run("deprecate", "--artifact-root", root, "--use-case", "lint",
        "--retirement-reason", "faster", "--replacement-candidate", "ruff", "--timeline", "Q3")
    run("migrate", "--artifact-root", root, "--use-case", "lint",
        "--migration-target", "ruff", "--migration-plan", "p")
    lifecycle = _section(_summary(root), "Lifecycle Notes")
    assert "- deprecated: 1 [lint]" in lifecycle
    assert "- migrating: 1 [lint]" in lifecycle
    assert "- archived: 0 [-]" in lifecycle


def test_latest_note_per_scene_not_double_counted(run, root):
    """Two deprecation-notes for one scene count once (latest wins, append-only)."""
    promote_scene(run, root, scene="lint", tool="pylint")
    run("deprecate", "--artifact-root", root, "--use-case", "lint",
        "--retirement-reason", "r1", "--replacement-candidate", "ruff", "--timeline", "Q3")
    run("deprecate", "--artifact-root", root, "--use-case", "lint",
        "--retirement-reason", "r2", "--replacement-candidate", "ruff", "--timeline", "Q4")
    lifecycle = _section(_summary(root), "Lifecycle Notes")
    assert "- deprecated: 1 [lint]" in lifecycle


def test_scene_filter_excludes_sceneless_watch(run, root):
    run("watch", "--artifact-root", root, "--candidate", "ruff", "--interest-reason", "x")
    lifecycle = _section(_summary(root, scene="lint"), "Lifecycle Notes")
    assert "- watch: 0 [-]" in lifecycle


# --- Current State by Scene (single resolved state per scene) ---------------

def test_current_state_resolves_to_latest_in_retirement_chain(run, root):
    """A scene promoted then migrated shows ONLY migrating, not three states."""
    promote_scene(run, root, scene="lint", tool="pylint")
    run("deprecate", "--artifact-root", root, "--use-case", "lint",
        "--retirement-reason", "faster", "--replacement-candidate", "ruff", "--timeline", "Q3")
    run("migrate", "--artifact-root", root, "--use-case", "lint",
        "--migration-target", "ruff", "--migration-plan", "p")
    current = _section(_summary(root), "Current State by Scene")
    assert "- lint: migrating" in current
    assert not any("promote" in line or "deprecated" in line for line in current)


def test_current_state_archived_wins(run, root):
    promote_scene(run, root, scene="lint", tool="pylint")
    run("deprecate", "--artifact-root", root, "--use-case", "lint",
        "--retirement-reason", "x", "--replacement-candidate", "ruff", "--timeline", "Q3")
    run("archive", "--artifact-root", root, "--use-case", "lint", "--end-date", "2026-09-30")
    current = _section(_summary(root), "Current State by Scene")
    assert "- lint: archived" in current


def test_current_state_blocked(run, root):
    run("quick-intake", "--artifact-root", root, "--candidate", "mypy",
        "--source", "doc", "--use-case", "typecheck", "--why-now", "strict")
    run("block", "--artifact-root", root, "--use-case", "typecheck",
        "--block-reason", "budget", "--unblock-condition", "Q3", "--owner", "lead")
    current = _section(_summary(root), "Current State by Scene")
    assert "- typecheck: blocked" in current


def test_current_state_unblock_returns_to_proposed(run, root):
    """Provenance, not timestamps: an intake derived from the blocked-note clears blocked."""
    run("quick-intake", "--artifact-root", root, "--candidate", "mypy",
        "--source", "doc", "--use-case", "typecheck", "--why-now", "strict")
    run("block", "--artifact-root", root, "--use-case", "typecheck",
        "--block-reason", "budget", "--unblock-condition", "Q3", "--owner", "lead")
    run("unblock", "--artifact-root", root, "--use-case", "typecheck", "--why-unblocked", "approved")
    current = _section(_summary(root), "Current State by Scene")
    assert "- typecheck: proposed" in current
    assert not any("blocked" in line for line in current)


def test_current_state_in_trial(run, root):
    run("quick-intake", "--artifact-root", root, "--candidate", "pylint",
        "--source", "doc", "--use-case", "lint", "--why-now", "need")
    run("quick-compare", "--artifact-root", root, "--use-case", "lint",
        "--candidate", "pylint", "--candidate", "other", "--selected", "pylint")
    run("quick-trial", "--artifact-root", root, "--use-case", "lint",
        "--mode", "read-only-comparison", "--executor", "ci",
        "--decision-owner", "lead", "--landing-target", "ci/lint")
    current = _section(_summary(root), "Current State by Scene")
    assert "- lint: in-trial" in current


def test_current_state_hold_resume_returns_trial_ready(run, root):
    run("quick-intake", "--artifact-root", root, "--candidate", "ruff",
        "--source", "doc", "--use-case", "lint", "--why-now", "need")
    run("quick-compare", "--artifact-root", root, "--use-case", "lint",
        "--candidate", "ruff", "--candidate", "other", "--selected", "ruff")
    run("quick-trial", "--artifact-root", root, "--use-case", "lint",
        "--mode", "read-only-comparison", "--executor", "ci",
        "--decision-owner", "lead", "--landing-target", "ci/lint")
    run("quick-close-trial", "--artifact-root", root, "--trial-id", "tr-001",
        "--verdict", "hold", "--observed-effect", "needs narrowing")
    run("quick-compare", "--artifact-root", root, "--use-case", "lint",
        "--candidate", "ruff", "--candidate", "other", "--selected", "ruff")
    current = _section(_summary(root), "Current State by Scene")
    assert "- lint: trial-ready" in current


def test_current_state_sceneless_watch_keyed_by_tool(run, root):
    run("watch", "--artifact-root", root, "--candidate", "ruff", "--interest-reason", "x")
    current = _section(_summary(root), "Current State by Scene")
    assert "- (watch) ruff: watch" in current


def test_reject_note_resolves_scene_to_reject(run, root):
    from pathlib import Path

    from adop_summary import get_scene_states
    assert run("quick-intake", "--artifact-root", root, "--candidate", "R", "--source", "doc",
               "--use-case", "r", "--why-now", "x") == 0
    assert run("reject", "--artifact-root", root, "--use-case", "r", "--reject-reason", "no") == 0
    assert get_scene_states(Path(root))["r"] == "reject"


def test_summary_loads_artifacts_once(run, root, monkeypatch):
    import adop_artifacts
    for i in range(6):
        sc = f"s{i}"
        assert run("quick-intake", "--artifact-root", root, "--candidate", "t", "--source", "doc",
                   "--use-case", sc, "--why-now", "x") == 0
        assert run("quick-compare", "--artifact-root", root, "--use-case", sc,
                   "--candidate", "t", "--candidate", "u", "--selected", "t") == 0
        assert run("quick-trial", "--artifact-root", root, "--use-case", sc, "--mode", "review-assist",
                   "--executor", "ci", "--decision-owner", "l", "--landing-target", "ci") == 0
        tid = f"tr-00{i + 1}"
        assert run("quick-close-trial", "--artifact-root", root, "--trial-id", tid,
                   "--verdict", "hold", "--observed-effect", "x") == 0
    calls = {"n": 0}
    real = adop_artifacts.load_all_artifacts

    def counting(target):
        calls["n"] += 1
        return real(target)

    monkeypatch.setattr(adop_artifacts, "load_all_artifacts", counting)
    monkeypatch.setattr(adop_summary, "load_all_artifacts", counting)
    adop_summary.build_summary(Path(root))
    # The whole summary must come from a single artifact-root load, not one
    # disk reload per trial/scene (was O(scenes x files)).
    assert calls["n"] <= 2, f"artifact root re-loaded {calls['n']} times (per-trial reload)"
