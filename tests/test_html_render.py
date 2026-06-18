"""Tests for HTML dashboard rendering."""

from __future__ import annotations

import json
import re
from pathlib import Path

from conftest import promote_scene


def _extract_payload(html_text: str) -> dict:
    match = re.search(
        r'<script id="adop-dashboard-payload" type="application/json">(.*?)</script>',
        html_text,
        re.DOTALL,
    )
    assert match, "embedded dashboard payload not found"
    return json.loads(match.group(1))


def test_render_html_writes_first_time_guidance_and_promote_command_guard(run, root):
    promote_scene(run, root, scene="lint-ci", tool="ruff")
    output = Path(root) / "dashboard.html"

    rc = run(
        "render-html",
        "--artifact-root", root,
        "--output", str(output),
        "--scene", "lint-ci",
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    payload = _extract_payload(text)
    lane = payload["lanes"][0]

    assert 'data-adop-template="governance-dashboard-v2"' in text
    assert "ADOP shows which external tools are under review, approved, blocked, retired, or kept only as history." in text
    assert "Use this page to understand status" in text
    assert "Run commands only when you are changing a decision" in text
    assert "You are a reader if you only need to understand status" in text
    assert "Source data (.adop)" in text
    assert "Copy primary command" in text
    assert "Copy retirement command" in text
    assert payload["selected_scene"] == "lint-ci"
    assert payload["metrics"]["managed_lanes"] == 1
    assert payload["metrics"]["recorded_lanes"] == 1
    assert payload["metrics"]["preview_sample_lanes"] == 0
    assert payload["metrics"]["promoted"] == 1
    assert lane["tool"] == "ruff"
    assert lane["state"] == "promote"
    assert lane["decision"].startswith("Approved for use")
    assert lane["next_step"] == "Use the tool only within the approved area and rules."
    assert lane["next_command_label"] == "No required next command"
    assert lane["next_command"] == ""
    assert lane["next_command_details"][0]["label"] == "Why there is no command"
    assert lane["retirement_command_label"] == "Retirement command"
    assert lane["retirement_command_details"][0]["label"] == "Why this command"
    assert lane["retirement_command"].startswith("adop deprecate --scene lint-ci")
    assert lane["state_meaning"].startswith("This decision is approved")
    assert lane["scene_label"] == "Lint CI"


def test_render_html_empty_state_includes_start_commands(run, root):
    output = Path(root) / "dashboard-empty.html"

    rc = run(
        "render-html",
        "--artifact-root", root,
        "--output", str(output),
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    payload = _extract_payload(text)

    assert "Start recording when no decisions exist yet" in text
    assert payload["metrics"]["recorded_lanes"] == 0
    assert payload["metrics"]["preview_sample_lanes"] == 0
    assert payload["empty_state_commands"][0]["command"] == "adop init"
    assert payload["empty_state_commands"][1]["command"].startswith("adop quick-intake --candidate <tool> --source doc --scene <scene>")
    assert payload["empty_state_commands"][2]["command"].startswith("adop quick-compare --scene <scene>")
    assert payload["empty_state_commands"][3]["command"].startswith("adop quick-trial --scene <scene>")
    assert payload["empty_state_commands"][4]["command"] == "adop status"
    assert payload["empty_state_commands"][5]["command"].startswith("adop render-html --artifact-root .adop")


def test_render_html_can_warn_when_sample_lanes_are_mixed_in(run, root):
    promote_scene(run, root, scene="lint-ci", tool="ruff")
    output = Path(root) / "dashboard-sample.html"

    rc = run(
        "render-html",
        "--artifact-root", root,
        "--output", str(output),
        "--sample-board-count", "10",
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    payload = _extract_payload(text)

    assert "Preview only: 9 sample decisions are shown for layout checking. Do not treat them as project records." in text
    assert "Preview sample" in text
    assert payload["metrics"]["managed_lanes"] == 10
    assert payload["metrics"]["recorded_lanes"] == 1
    assert payload["metrics"]["preview_sample_lanes"] == 9
    assert payload["sample_rows_included"] == 9
    assert payload["selected_scene"] == "lint-ci"
    assert len(payload["lanes"]) == 10
    assert len(payload["active_lanes"]) == 1
    assert all(not lane["is_sample"] for lane in payload["active_lanes"])
    assert len(payload["sample_lanes"]) == 9
    assert any(lane["is_sample"] for lane in payload["lanes"])
    assert any(lane["state"] == "archived" for lane in payload["sample_lanes"])


def test_render_html_explains_why_a_blocked_command_should_be_used(run, root):
    promote_scene(run, root, scene="lint-ci", tool="ruff")
    output = Path(root) / "dashboard-blocked-sample.html"

    rc = run(
        "render-html",
        "--artifact-root", root,
        "--output", str(output),
        "--scene", "dep-alerts",
        "--sample-board-count", "10",
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    payload = _extract_payload(text)
    lane = next(item for item in payload["lanes"] if item["scene"] == "dep-alerts")

    assert lane["state"] == "blocked"
    assert lane["next_command"].startswith("adop unblock --scene dep-alerts")
    assert lane["next_command_details"][0]["value"].startswith("This decision is blocked.")
    assert "The blocker has been cleared and you need to record what changed." in text
    assert "ADOP removes the blocked state and reopens the decision for the next review step." in text


def test_render_html_includes_large_board_controls_and_limits(run, root):
    promote_scene(run, root, scene="lint-ci", tool="ruff")
    output = Path(root) / "dashboard-large.html"

    rc = run(
        "render-html",
        "--artifact-root", root,
        "--output", str(output),
        "--sample-board-count", "100",
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    payload = _extract_payload(text)

    assert "Current external tool decisions" in text
    assert "Search decisions" in text
    assert "State filter" in text
    assert "Sort by" in text
    assert "Blocked" in text
    assert "Trial Running" in text
    assert "Ready To Trial" in text
    assert "Historical" in text
    assert "Show more current decisions" in text
    assert "Show more past decisions" in text
    assert "Read the table first. The detail view explains the decision. The command box is separate and only matters for the person changing status." in text
    assert "Layout-check examples, not project decisions" in text
    assert "Needed next from owner" in text
    assert "Latest update" in text
    assert 'data-filter-target="blocked"' in text
    assert 'data-filter-target="historical"' in text
    assert 'setBoardFilter(card.dataset.filterTarget || "all", true);' in text
    assert payload["metrics"]["managed_lanes"] == 100
    assert payload["initial_active_limit"] == 12
    assert payload["initial_historical_limit"] == 12
    assert payload["metrics"]["preview_sample_lanes"] == 99


def test_render_html_keeps_accessibility_hooks_for_modal_and_copy(run, root):
    promote_scene(run, root, scene="lint-ci", tool="ruff")
    output = Path(root) / "dashboard-a11y.html"

    rc = run(
        "render-html",
        "--artifact-root", root,
        "--output", str(output),
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")

    assert 'aria-label="Close decision detail"' in text
    assert 'aria-label="Copy primary command"' in text
    assert 'aria-label="Copy retirement command"' in text
    assert 'event.key === "Escape"' in text
    assert 'uiState.lastFocusedRow.focus()' in text
    assert 'document.execCommand("copy")' in text


def test_render_html_separates_reader_and_operator_guidance(run, root):
    promote_scene(run, root, scene="lint-ci", tool="ruff")
    output = Path(root) / "dashboard-guidance.html"

    rc = run(
        "render-html",
        "--artifact-root", root,
        "--output", str(output),
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    payload = _extract_payload(text)

    assert "For readers" in text
    assert "For operators" in text
    assert "Operator only" in text
    assert "You are the operator only if you are the person who records approve, hold, reject, unblock, retire, or trial changes in ADOP." in text
    assert "Open operator action" in text
    assert payload["reader_steps"][0] == "Check the summary counts"
    assert payload["operator_steps"][0] == "Open the decision you need to change"
