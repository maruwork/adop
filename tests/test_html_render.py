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
        "--artifact-root",
        root,
        "--output",
        str(output),
        "--scene",
        "lint-ci",
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    payload = _extract_payload(text)
    lane = payload["lanes"][0]

    assert 'data-adop-template="governance-dashboard-v2"' in text
    assert (
        "ADOP shows which external tools are under review, approved, blocked, retired, or kept only as history."
        in text
    )
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
        "--artifact-root",
        root,
        "--output",
        str(output),
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    payload = _extract_payload(text)

    assert "Start recording when no decisions exist yet" in text
    assert payload["metrics"]["recorded_lanes"] == 0
    assert payload["metrics"]["preview_sample_lanes"] == 0
    assert payload["empty_state_commands"][0]["command"] == "adop init"
    assert payload["empty_state_commands"][1]["command"].startswith(
        "adop quick-intake --candidate <tool> --source doc --scene <scene>"
    )
    assert payload["empty_state_commands"][2]["command"].startswith(
        "adop quick-compare --scene <scene>"
    )
    assert payload["empty_state_commands"][3]["command"].startswith(
        "adop quick-trial --scene <scene>"
    )
    assert payload["empty_state_commands"][4]["command"] == "adop status"
    assert payload["empty_state_commands"][5]["command"].startswith(
        "adop render-html --artifact-root .adop"
    )


def test_render_html_can_warn_when_sample_lanes_are_mixed_in(run, root):
    promote_scene(run, root, scene="lint-ci", tool="ruff")
    output = Path(root) / "dashboard-sample.html"

    rc = run(
        "render-html",
        "--artifact-root",
        root,
        "--output",
        str(output),
        "--sample-board-count",
        "10",
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    payload = _extract_payload(text)

    assert (
        "Preview only: 9 sample decisions are shown for layout checking. Do not treat them as project records."
        in text
    )
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
        "--artifact-root",
        root,
        "--output",
        str(output),
        "--scene",
        "dep-alerts",
        "--sample-board-count",
        "10",
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    payload = _extract_payload(text)
    lane = next(item for item in payload["lanes"] if item["scene"] == "dep-alerts")

    assert lane["state"] == "blocked"
    assert lane["next_command"].startswith("adop unblock --scene dep-alerts")
    assert lane["next_command_details"][0]["value"].startswith("This decision is blocked.")
    assert "The blocker has been cleared and you need to record what changed." in text
    assert (
        "ADOP removes the blocked state and reopens the decision for the next review step." in text
    )


def test_render_html_includes_large_board_controls_and_limits(run, root):
    promote_scene(run, root, scene="lint-ci", tool="ruff")
    output = Path(root) / "dashboard-large.html"

    rc = run(
        "render-html",
        "--artifact-root",
        root,
        "--output",
        str(output),
        "--sample-board-count",
        "100",
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
    assert (
        "Read the table first. The detail view explains the decision. The command box is separate and only matters for the person changing status."
        in text
    )
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
        "--artifact-root",
        root,
        "--output",
        str(output),
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")

    assert 'aria-label="Close decision detail"' in text
    assert 'aria-label="Copy primary command"' in text
    assert 'aria-label="Copy retirement command"' in text
    assert 'event.key === "Escape"' in text
    assert "uiState.lastFocusedRow.focus()" in text
    assert 'document.execCommand("copy")' in text


def test_render_html_separates_reader_and_operator_guidance(run, root):
    promote_scene(run, root, scene="lint-ci", tool="ruff")
    output = Path(root) / "dashboard-guidance.html"

    rc = run(
        "render-html",
        "--artifact-root",
        root,
        "--output",
        str(output),
    )

    assert rc == 0
    text = output.read_text(encoding="utf-8")
    payload = _extract_payload(text)

    assert "For readers" in text
    assert "For operators" in text
    assert "Operator only" in text
    assert (
        "You are the operator only if you are the person who records approve, hold, reject, unblock, retire, or trial changes in ADOP."
        in text
    )
    assert "Open operator action" in text
    assert payload["reader_steps"][0] == "Check the summary counts"
    assert payload["operator_steps"][0] == "Open the decision you need to change"


def test_in_trial_lane_shows_packet_envelope(run, root):
    from adop_html import build_dashboard_payload

    assert (
        run(
            "quick-intake",
            "--artifact-root",
            root,
            "--candidate",
            "T",
            "--source",
            "doc",
            "--use-case",
            "t",
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
            "t",
            "--candidate",
            "T",
            "--candidate",
            "U",
            "--selected",
            "T",
        )
        == 0
    )
    assert (
        run(
            "quick-trial",
            "--artifact-root",
            root,
            "--use-case",
            "t",
            "--mode",
            "review-assist",
            "--executor",
            "ci",
            "--decision-owner",
            "o",
            "--landing-target",
            "x",
        )
        == 0
    )
    lane = next(
        lane for lane in build_dashboard_payload(Path(root))["lanes"] if lane["scene"] == "t"
    )
    assert lane["allowed"] != ["No explicit allow-list recorded yet"]
    assert "file read" in lane["allowed"]
    assert any("inside target project" in f for f in lane["forbidden"])


def test_blocked_lane_shows_block_reason(run, root):
    from adop_html import build_dashboard_payload

    assert (
        run(
            "quick-intake",
            "--artifact-root",
            root,
            "--candidate",
            "B",
            "--source",
            "doc",
            "--use-case",
            "b",
            "--why-now",
            "x",
        )
        == 0
    )
    assert (
        run(
            "block",
            "--artifact-root",
            root,
            "--use-case",
            "b",
            "--block-reason",
            "LICENSE_UNDECIDED",
            "--unblock-condition",
            "legal ok",
            "--owner",
            "o",
        )
        == 0
    )
    lane = next(
        lane for lane in build_dashboard_payload(Path(root))["lanes"] if lane["scene"] == "b"
    )
    assert "LICENSE_UNDECIDED" in lane["decision"]
    assert any("LICENSE_UNDECIDED" in str(r["value"]) for r in lane["rationale"])


def test_proposed_lane_shows_why_now(run, root):
    from adop_html import build_dashboard_payload

    assert (
        run(
            "intake",
            "--artifact-root",
            root,
            "--candidate",
            "P",
            "--candidate-shape",
            "atomic",
            "--source",
            "doc",
            "--scene",
            "p",
            "--lane",
            "assistance",
            "--reason",
            "WHYNOW_TEXT",
            "--root-cause-hypothesis",
            "DIFFERENT_RCH",
            "--platform",
            "any",
            "--license",
            "MIT",
            "--cost",
            "free",
            "--version",
            "1.0",
            "--category",
            "cli",
            "--ai-compatibility",
            "any",
            "--data-flow-json",
            '{"destination":"local","data_types":["code"],"opt_in":true}',
        )
        == 0
    )
    lane = next(
        lane for lane in build_dashboard_payload(Path(root))["lanes"] if lane["scene"] == "p"
    )
    why_now = next(r["value"] for r in lane["rationale"] if r["label"] == "Why now")
    assert why_now == "WHYNOW_TEXT"


def test_no_wrong_deprecation_flag_anywhere():
    py = Path("shared/python")
    cli = (py / "adop_cli.py").read_text(encoding="utf-8")
    html = (py / "adop_html.py").read_text(encoding="utf-8")
    assert "--deprecation-reason" not in cli
    assert "--deprecation-reason" not in html
    assert "--retirement-reason" in html
    assert "wa-001" not in html


def test_modal_open_moves_focus_and_traps(run, root):
    from adop_html import render_dashboard_html

    assert (
        run(
            "quick-intake",
            "--artifact-root",
            root,
            "--candidate",
            "A",
            "--source",
            "doc",
            "--use-case",
            "a",
            "--why-now",
            "x",
        )
        == 0
    )
    html = render_dashboard_html(Path(root))
    open_fn = html.split("function openLaneDetail")[1].split("function closeLaneDetail")[0]
    assert 'document.getElementById("detail-close").focus()' in open_fn
    assert "trapModalTab" in html


def test_watch_lane_shows_interest_reason(run, root):
    from adop_html import build_dashboard_payload

    assert (
        run(
            "watch",
            "--artifact-root",
            root,
            "--candidate",
            "vale",
            "--interest-reason",
            "EDITORIAL_MARK",
            "--use-case",
            "docs-style",
        )
        == 0
    )
    lane = next(
        lane
        for lane in build_dashboard_payload(Path(root))["lanes"]
        if lane["scene"] == "docs-style"
    )
    assert any("EDITORIAL_MARK" in str(r["value"]) for r in lane["rationale"])


def test_pre_trial_reject_shows_reason_not_trial(run, root):
    from adop_html import build_dashboard_payload

    assert (
        run(
            "quick-intake",
            "--artifact-root",
            root,
            "--candidate",
            "snyk",
            "--source",
            "doc",
            "--use-case",
            "dep-x",
            "--why-now",
            "risk",
        )
        == 0
    )
    assert (
        run(
            "reject",
            "--artifact-root",
            root,
            "--use-case",
            "dep-x",
            "--reject-reason",
            "COST_FIT_MARK",
        )
        == 0
    )
    lane = next(
        lane for lane in build_dashboard_payload(Path(root))["lanes"] if lane["scene"] == "dep-x"
    )
    assert "trial closed" not in lane["decision"].lower()
    assert "COST_FIT_MARK" in lane["decision"] or any(
        "COST_FIT_MARK" in str(r["value"]) for r in lane["rationale"]
    )


def test_scan_skips_oversized_file(run, root, tmp_path):
    target = tmp_path / "big"
    target.mkdir()
    (target / "huge.cfg").write_bytes(b"eslint\n" + b"x" * (6 * 1024 * 1024))
    (target / "small.cfg").write_text("eslint config here\n")
    from adop_cli import _scan_target_for_tool

    couplings = _scan_target_for_tool(target, "eslint", [])
    paths = {c["path"] for c in couplings}
    assert "huge.cfg" not in paths  # oversized file skipped


def _visible_blob(root_str, scene):
    import json as _j

    from adop_html import build_dashboard_payload

    lane = next(
        lane for lane in build_dashboard_payload(Path(root_str))["lanes"] if lane["scene"] == scene
    )
    return _j.dumps({"decision": lane["decision"], "rationale": lane["rationale"]}), lane


def test_deprecated_lane_surfaces_retirement_reason(run, root):
    promote_scene(run, root, scene="lint", tool="pylint")
    assert (
        run(
            "deprecate",
            "--artifact-root",
            root,
            "--use-case",
            "lint",
            "--retirement-reason",
            "RETIRE_MARK",
            "--replacement-candidate",
            "ruff",
            "--timeline",
            "Q3",
        )
        == 0
    )
    blob, _ = _visible_blob(root, "lint")
    assert "RETIRE_MARK" in blob


def test_migrating_lane_surfaces_migration(run, root):
    promote_scene(run, root, scene="lint", tool="pylint")
    run(
        "deprecate",
        "--artifact-root",
        root,
        "--use-case",
        "lint",
        "--retirement-reason",
        "r",
        "--replacement-candidate",
        "ruff",
        "--timeline",
        "Q3",
    )
    assert (
        run(
            "migrate",
            "--artifact-root",
            root,
            "--use-case",
            "lint",
            "--migration-target",
            "MIGTGT_MARK",
            "--migration-plan",
            "MIGPLAN_MARK",
        )
        == 0
    )
    blob, _ = _visible_blob(root, "lint")
    assert "MIGTGT_MARK" in blob or "MIGPLAN_MARK" in blob


def test_archived_lane_surfaces_end_date(run, root):
    promote_scene(run, root, scene="lint", tool="pylint")
    run(
        "deprecate",
        "--artifact-root",
        root,
        "--use-case",
        "lint",
        "--retirement-reason",
        "r",
        "--replacement-candidate",
        "ruff",
        "--timeline",
        "Q3",
    )
    assert (
        run(
            "archive",
            "--artifact-root",
            root,
            "--use-case",
            "lint",
            "--end-date",
            "2026-07-01",
            "--successor-tool",
            "SUCC_MARK",
        )
        == 0
    )
    blob, _ = _visible_blob(root, "lint")
    assert "2026-07-01" in blob or "SUCC_MARK" in blob


def test_hold_lane_decision_mentions_hold(run, root):
    assert (
        run(
            "quick-intake",
            "--artifact-root",
            root,
            "--candidate",
            "mypy",
            "--source",
            "doc",
            "--use-case",
            "h",
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
            "h",
            "--candidate",
            "mypy",
            "--candidate",
            "y",
            "--selected",
            "mypy",
        )
        == 0
    )
    assert (
        run(
            "quick-trial",
            "--artifact-root",
            root,
            "--use-case",
            "h",
            "--mode",
            "review-assist",
            "--executor",
            "ci",
            "--decision-owner",
            "l",
            "--landing-target",
            "ci",
        )
        == 0
    )
    assert (
        run(
            "quick-close-trial",
            "--artifact-root",
            root,
            "--trial-id",
            "tr-001",
            "--verdict",
            "hold",
            "--observed-effect",
            "HOLDREASON_MARK",
        )
        == 0
    )
    _, lane = _visible_blob(root, "h")
    assert "HOLDREASON_MARK" in lane["decision"] or any(
        "HOLDREASON_MARK" in str(r["value"]) for r in lane["rationale"]
    )


def test_sample_board_renders_preview_lanes(run, root):
    from adop_html import build_dashboard_payload

    payload = build_dashboard_payload(Path(root), sample_board_count=6)
    assert payload["sample_rows_included"] > 0
    assert payload["preview_warning"]
    assert all(lane["decision"] for lane in payload["lanes"])
    assert all(lane["rationale"] for lane in payload["lanes"])


def test_render_html_multistate_embeds_all_lanes(run, root):
    from adop_html import render_dashboard_html

    assert (
        run(
            "watch",
            "--artifact-root",
            root,
            "--candidate",
            "vale",
            "--interest-reason",
            "r",
            "--use-case",
            "w-scene",
        )
        == 0
    )
    assert (
        run(
            "quick-intake",
            "--artifact-root",
            root,
            "--candidate",
            "ruff",
            "--source",
            "doc",
            "--use-case",
            "p-scene",
            "--why-now",
            "x",
        )
        == 0
    )
    html = render_dashboard_html(Path(root))
    payload = _extract_payload(html)
    scenes = {lane["scene"] for lane in payload["lanes"]}
    assert {"w-scene", "p-scene"} <= scenes
    for lane in payload["lanes"]:
        assert lane["decision"]
        assert lane["rationale"]


def test_large_sample_board_clones_seed_lanes(run, root):
    from adop_html import build_dashboard_payload

    payload = build_dashboard_payload(Path(root), sample_board_count=40)
    assert payload["metrics"]["managed_lanes"] == 40
    assert payload["sample_rows_included"] == 40
    # cloned sample lanes still carry renderable fields
    assert all(lane["decision"] and lane["rationale"] for lane in payload["sample_lanes"])


def test_historical_filter_opens_history_details(run, root):
    from adop_html import render_dashboard_html

    assert (
        run(
            "watch",
            "--artifact-root",
            root,
            "--candidate",
            "x",
            "--interest-reason",
            "r",
            "--use-case",
            "s",
        )
        == 0
    )
    html = render_dashboard_html(Path(root))
    assert 'uiState.filter === "historical"' in html
    assert "historyShell.open = true" in html


def test_dashboard_has_back_to_top(run, root):
    from adop_html import render_dashboard_html

    assert (
        run(
            "quick-intake",
            "--artifact-root",
            root,
            "--candidate",
            "ruff",
            "--source",
            "doc",
            "--use-case",
            "lint",
            "--why-now",
            "x",
        )
        == 0
    )
    html = render_dashboard_html(Path(root))
    assert '<button class="to-top"' in html
    assert 'aria-label="Back to top"' in html
    assert "window.scrollTo({ top: 0" in html


def test_latest_update_is_most_advanced_artifact_with_date(run, root):
    from adop_html import build_dashboard_payload

    assert (
        run(
            "quick-intake",
            "--artifact-root",
            root,
            "--candidate",
            "mypy",
            "--source",
            "doc",
            "--use-case",
            "types",
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
            "types",
            "--candidate",
            "mypy",
            "--candidate",
            "pyright",
            "--selected",
            "mypy",
        )
        == 0
    )
    assert (
        run(
            "quick-trial",
            "--artifact-root",
            root,
            "--use-case",
            "types",
            "--mode",
            "review-assist",
            "--executor",
            "ci",
            "--decision-owner",
            "lead",
            "--landing-target",
            "ci/types",
        )
        == 0
    )
    lane = next(ln for ln in build_dashboard_payload(Path(root))["lanes"] if ln["scene"] == "types")
    ev = lane["last_evidence"]
    assert "Trial plan" in ev  # the most-advanced artifact, not the intake
    assert "Intake" not in ev
    assert ev[:4].isdigit() and ev[4] == "-"  # leads with a date (YYYY-...)
