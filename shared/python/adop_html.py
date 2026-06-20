#!/usr/bin/env python3
"""ADOP HTML dashboard renderer."""

from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path
from typing import Any

from adop_artifacts import AdopArtifactError, load_all_artifacts
from adop_ids import parse_numeric_id
from adop_summary import get_scene_states

_TEMPLATE_NAME = "adop-governance-dashboard-template.html"

_STATE_LABELS: dict[str, str] = {
    "watch": "Watching",
    "proposed": "Proposed",
    "trial-ready": "Ready to trial",
    "in-trial": "Trial running",
    "promote": "Approved",
    "hold": "On hold",
    "reject": "Rejected",
    "blocked": "Blocked",
    "deprecated": "Retiring",
    "migrating": "Replacing",
    "archived": "Archived",
}

_STATE_MEANINGS: dict[str, str] = {
    "watch": "The tool is only being watched. No formal review has started yet.",
    "proposed": "The candidate and reason are recorded, but comparison and trial are still unfinished.",
    "trial-ready": "Comparison is done and the decision is ready for a bounded trial.",
    "in-trial": "A bounded trial is underway or waiting to be closed with evidence.",
    "promote": "This decision is approved for use within the recorded allowed area and rules.",
    "hold": "The trial paused without approval. The review may resume later.",
    "reject": "This decision ended in rejection for this use case.",
    "blocked": "This decision cannot move until an explicit blocker is cleared.",
    "deprecated": "Retirement was decided, and the removal phase is now recorded.",
    "migrating": "Replacement work has started and is still in progress.",
    "archived": "This decision is closed and kept only as history.",
}

_STATE_TONES: dict[str, str] = {
    "watch": "neutral",
    "proposed": "neutral",
    "trial-ready": "trialing",
    "in-trial": "trialing",
    "promote": "promoted",
    "hold": "blocked",
    "reject": "blocked",
    "blocked": "blocked",
    "deprecated": "neutral",
    "migrating": "trialing",
    "archived": "neutral",
}

_STATE_SORT: dict[str, int] = {
    "blocked": 0,
    "in-trial": 1,
    "trial-ready": 2,
    "proposed": 3,
    "watch": 4,
    "promote": 5,
    "hold": 6,
    "reject": 7,
    "deprecated": 8,
    "migrating": 9,
    "archived": 10,
}

_HISTORICAL_STATES: frozenset[str] = frozenset({"reject", "deprecated", "migrating", "archived"})

_EMPTY_STATE_COMMANDS: tuple[dict[str, str], ...] = (
    {
        "label": "Initialize ADOP",
        "command": "adop init",
        "note": "Create the .adop record folder and the project-local overlay.",
    },
    {
        "label": "Record the first candidate",
        "command": 'adop quick-intake --candidate <tool> --source doc --scene <scene> --why-now "<reason>"',
        "note": "Record why this tool is being considered and tie it to one use case.",
    },
    {
        "label": "Compare candidates",
        "command": "adop quick-compare --scene <scene> --candidate <tool> --candidate <other> --selected <tool>",
        "note": "Narrow the review to one selected candidate before trialing it.",
    },
    {
        "label": "Start a bounded trial",
        "command": "adop quick-trial --scene <scene> --mode review-assist --executor <who> --decision-owner <owner> --landing-target <target>",
        "note": "Record who runs the trial, where approved use may happen, and the trial boundary before recurring use.",
    },
    {
        "label": "Check current state",
        "command": "adop status",
        "note": "Review which decisions are active, blocked, or approved right now.",
    },
    {
        "label": "Render this dashboard",
        "command": "adop render-html --artifact-root .adop --output workspace/html-preview/adop_dashboard.html",
        "note": "Generate one HTML status page from the canonical template.",
    },
)

_READER_STEPS: tuple[str, ...] = (
    "Check the summary counts",
    "Scan the current decisions table",
    "Open the row you care about",
    "Stop here unless you are responsible for changing status",
)

_OPERATOR_STEPS: tuple[str, ...] = (
    "Open the decision you need to change",
    "Confirm the current state, reason, and usage limits",
    "Use the command box only when the status should change",
    "Re-render the page after you record the new decision",
)

_SAMPLE_LANES: tuple[dict[str, Any], ...] = (
    {
        "scene": "typed-app",
        "tool": "mypy",
        "state": "promote",
        "decision": "Promoted after staged verification",
        "landing_target": "ci/typecheck",
        "control_model": "Human-reviewed config update only",
        "last_evidence": "Decision record tr-002 + approval note pm-002",
        "kind_meta": "cli / MIT / local data flow",
        "why_it_matters": "Static typing moved from opinion to an approved tool decision.",
        "why_this_state": "The trial proved the tool can run with bounded operator review.",
        "what_happens_next": "Roll out the approved config only in the typed-app use case.",
        "change_condition": "A migration or retirement note would change this decision state.",
        "allowed": ["file read", "metadata read", "config diff review"],
        "forbidden": ["tracked file write without review", "repo-wide mutation"],
        "rationale": [
            {"label": "Judgment reason", "value": "trial produced reusable value"},
            {"label": "Observed effect", "value": "reduced manual type drift checks"},
        ],
        "artifacts": [
            {"type": "trial-result", "id": "tr-002", "purpose": "records observed typing outcomes"},
            {"type": "promotion-note", "id": "pm-002", "purpose": "marks the decision as approved"},
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
    {
        "scene": "infra-docs",
        "tool": "terraform-docs",
        "state": "promote",
        "decision": "Promoted for bounded documentation generation",
        "landing_target": "docs/infra",
        "control_model": "Writeback only after diff review",
        "last_evidence": "Decision record tr-003 + approval note pm-003",
        "kind_meta": "cli / MPL-2.0 / local repo metadata",
        "why_it_matters": "Infrastructure docs are governed as a distinct tool decision.",
        "why_this_state": "The decision proved doc output can be reviewed before acceptance.",
        "what_happens_next": "Use the tool only in the infra-docs approved area.",
        "change_condition": "Future doc ownership changes would reopen this decision.",
        "allowed": ["repo metadata read", "write output outside the target project"],
        "forbidden": ["direct README overwrite", "unreviewed generated commit"],
        "rationale": [
            {"label": "Judgment reason", "value": "bounded doc generation proved stable"},
            {"label": "Observed effect", "value": "consistent terraform module docs"},
        ],
        "artifacts": [
            {"type": "trial-result", "id": "tr-003", "purpose": "captures doc generation outcome"},
            {
                "type": "promotion-note",
                "id": "pm-003",
                "purpose": "marks the doc decision as promoted",
            },
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
    {
        "scene": "deploy-observability",
        "tool": "datadog-ci",
        "state": "promote",
        "decision": "Promoted with explicit token handling guardrails",
        "landing_target": "ops/deploy",
        "control_model": "Secrets kept outside the recorded trial files",
        "last_evidence": "Approval note pm-004 + control review",
        "kind_meta": "cli / SaaS bridge / deploy metadata only",
        "why_it_matters": "Operational tooling is managed with its own evidence boundary.",
        "why_this_state": "The decision was approved only after secret-handling controls were fixed.",
        "what_happens_next": "Use the tool only through the approved deploy path.",
        "change_condition": "Any token model change would trigger re-evaluation.",
        "allowed": ["deploy metadata read", "write external output"],
        "forbidden": ["token commit", "unreviewed pipeline mutation"],
        "rationale": [
            {"label": "Judgment reason", "value": "control model became explicit and reviewable"},
            {"label": "Observed effect", "value": "deployment annotations remained bounded"},
        ],
        "artifacts": [
            {
                "type": "promotion-note",
                "id": "pm-004",
                "purpose": "records the approved observability decision",
            },
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
    {
        "scene": "e2e-smoke",
        "tool": "playwright",
        "state": "trial-ready",
        "decision": "Trial packet approved; bounded smoke run not started yet",
        "landing_target": "ci/e2e-smoke",
        "control_model": "Read + isolated output write only",
        "last_evidence": "Trial plan tr-004",
        "kind_meta": "framework / Apache-2.0 / browser automation",
        "why_it_matters": "This decision has a narrow objective and a declared executor.",
        "why_this_state": "Scope is ready, but execution evidence has not been written yet.",
        "what_happens_next": "Run the bounded smoke trial and close it with evidence.",
        "change_condition": "A trial result and decision record will advance this decision.",
        "allowed": ["browser run", "write output outside the target project"],
        "forbidden": ["branch mutation", "tracked file write inside target project"],
        "rationale": [
            {"label": "Trial readiness", "value": "executor, gate, and boundary are defined"},
        ],
        "artifacts": [
            {
                "type": "trial-packet",
                "id": "tr-004",
                "purpose": "declares trial scope and controls",
            },
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
    {
        "scene": "secrets-scan",
        "tool": "semgrep",
        "state": "in-trial",
        "decision": "Trial active with false-positive review in progress",
        "landing_target": "security/pre-merge",
        "control_model": "No branch mutation during evaluation",
        "last_evidence": "Trial result tr-005 pending close",
        "kind_meta": "cli / LGPL-2.1 / rule-driven source scan",
        "why_it_matters": "Security scanning needs explicit evidence, not only enthusiasm.",
        "why_this_state": "Observed output exists, but the review has not reached a final decision yet.",
        "what_happens_next": "Review findings, close the trial, then decide promote/hold/reject.",
        "change_condition": "A decision record will change this state.",
        "allowed": ["source read", "write output outside the target project"],
        "forbidden": ["auto-fix writeback", "branch mutation"],
        "rationale": [
            {"label": "Observed effect", "value": "mixed findings require human review"},
        ],
        "artifacts": [
            {"type": "trial-packet", "id": "tr-005", "purpose": "defines trial scope"},
            {"type": "trial-result", "id": "tr-005", "purpose": "captures scan outcome"},
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
    {
        "scene": "image-scan",
        "tool": "trivy",
        "state": "in-trial",
        "decision": "Trial active on release images only",
        "landing_target": "ci/container-scan",
        "control_model": "Registry read only, no build mutation",
        "last_evidence": "Trial result tr-006 pending close",
        "kind_meta": "cli / Apache-2.0 / image and fs scan",
        "why_it_matters": "Container policy should be visible as its own recorded decision.",
        "why_this_state": "Evidence exists, but promotion criteria have not been closed yet.",
        "what_happens_next": "Complete the trial review and decide whether to approve the tool.",
        "change_condition": "Closing the trial will change this state.",
        "allowed": ["image read", "write output outside the target project"],
        "forbidden": ["image rebuild", "deployment mutation"],
        "rationale": [
            {"label": "Observed effect", "value": "release image findings need owner review"},
        ],
        "artifacts": [
            {"type": "trial-packet", "id": "tr-006", "purpose": "defines image-scan trial"},
            {"type": "trial-result", "id": "tr-006", "purpose": "records scan output"},
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
    {
        "scene": "dep-alerts",
        "tool": "snyk",
        "state": "blocked",
        "decision": "Blocked until license and data-boundary decision",
        "landing_target": "security/dependency",
        "control_model": "No token issue until owner approval",
        "last_evidence": "Blocked note bl-001",
        "kind_meta": "service / SaaS bridge / dependency advisory",
        "why_it_matters": "This decision is visible precisely because approval is not automatic.",
        "why_this_state": "Control questions exist that must be answered before a trial is allowed.",
        "what_happens_next": "Resolve the blocker, then reopen the review through intake.",
        "change_condition": "An unblock path or renewed intake would change this state.",
        "allowed": ["comparison prep", "non-secret documentation"],
        "forbidden": ["token creation", "service connection to target project"],
        "rationale": [
            {"label": "Block reason", "value": "license and outbound data boundary undecided"},
        ],
        "artifacts": [
            {"type": "comparison-note", "id": "cmp-002", "purpose": "captures candidate narrowing"},
            {"type": "blocked-note", "id": "bl-001", "purpose": "records why the review stopped"},
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
    {
        "scene": "dep-update",
        "tool": "renovate",
        "state": "proposed",
        "decision": "Scope proposal prepared; trial not opened yet",
        "landing_target": "repo/dependencies",
        "control_model": "Mutation model not approved yet",
        "last_evidence": "Intake note ci-004",
        "kind_meta": "service / AGPL-3.0 / PR automation",
        "why_it_matters": "The tool is visible before anyone mistakes it for an approved automation.",
        "why_this_state": "Need and candidate were captured, but comparison and trial gates remain open.",
        "what_happens_next": "Compare candidates or narrow this proposed use case further.",
        "change_condition": "A comparison note would move this decision to trial ready.",
        "allowed": ["note capture", "bounded comparison"],
        "forbidden": ["repo mutation", "bot installation"],
        "rationale": [
            {"label": "Why now", "value": "dependency update burden keeps recurring"},
        ],
        "artifacts": [
            {
                "type": "candidate-intake-note",
                "id": "ci-004",
                "purpose": "records the proposed decision",
            },
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
    {
        "scene": "docs-style",
        "tool": "vale",
        "state": "watch",
        "decision": "Observed need; not yet narrowed to a trial decision",
        "landing_target": "docs/editorial",
        "control_model": "No execution authority granted",
        "last_evidence": "Watch note wt-001",
        "kind_meta": "cli / MIT / prose lint",
        "why_it_matters": "ADOP can show interest without pretending a decision exists.",
        "why_this_state": "Only watch-level evidence exists, so the review remains before intake.",
        "what_happens_next": "Convert interest into a bounded intake if the team wants to evaluate it.",
        "change_condition": "A candidate-intake-note would move this into the active funnel.",
        "allowed": ["watch entry"],
        "forbidden": ["trial start", "writeback authority"],
        "rationale": [
            {
                "label": "Interest reason",
                "value": "editorial consistency is becoming a recurring problem",
            },
        ],
        "artifacts": [
            {"type": "watch-note", "id": "wt-001", "purpose": "records early interest only"},
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
    {
        "scene": "legacy-lint",
        "tool": "tslint",
        "state": "archived",
        "decision": "Archived after migration completed",
        "landing_target": "historical/frontend-lint",
        "control_model": "Historical record only",
        "last_evidence": "Archive note ar-001",
        "kind_meta": "cli / MIT / local",
        "why_it_matters": "Past decisions stay visible so teams do not re-open the same retired path blindly.",
        "why_this_state": "Migration completed and the decision was intentionally closed.",
        "what_happens_next": "No further action is required unless a materially new evaluation begins.",
        "change_condition": "A new evaluation should use a new scene name instead of reviving this archived decision.",
        "allowed": ["historical lookup"],
        "forbidden": ["silent reuse without new evaluation"],
        "rationale": [
            {"label": "Archive reason", "value": "migration away from tslint is complete"},
        ],
        "artifacts": [
            {
                "type": "archive-note",
                "id": "ar-001",
                "purpose": "records final closure of the decision",
            },
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
    {
        "scene": "repo-linter-old",
        "tool": "eslint",
        "state": "deprecated",
        "decision": "Retirement decision recorded; successor decision is active",
        "landing_target": "historical/js-lint",
        "control_model": "Frozen pending migration completion",
        "last_evidence": "Retirement note dp-001",
        "kind_meta": "cli / MIT / local",
        "why_it_matters": "Retirement decisions are part of governance, not noise to delete.",
        "why_this_state": "The team decided to retire this decision but has not fully closed it yet.",
        "what_happens_next": "Move active work to the successor decision, then archive this one.",
        "change_condition": "A migration or archive note will advance this decision.",
        "allowed": ["historical reference", "planned migration work"],
        "forbidden": ["treating this decision as the current approved standard"],
        "rationale": [
            {
                "label": "Retirement reason",
                "value": "the successor decision is replacing the old lint path",
            },
        ],
        "artifacts": [
            {
                "type": "deprecation-note",
                "id": "dp-001",
                "purpose": "records the retirement decision",
            },
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
    {
        "scene": "buildkite-trial",
        "tool": "buildkite",
        "state": "reject",
        "decision": "Rejected after evaluation for this use case",
        "landing_target": "historical/ci-eval",
        "control_model": "Historical record only",
        "last_evidence": "Reject note rj-001",
        "kind_meta": "service / commercial / cloud",
        "why_it_matters": "Rejected decisions are retained so future teams can see why this path stopped.",
        "why_this_state": "The trial did not justify adoption for this scene.",
        "what_happens_next": "Use a new use case key if a materially different review is needed later.",
        "change_condition": "This scene itself is terminal; only a new scene can restart evaluation.",
        "allowed": ["historical lookup"],
        "forbidden": ["reopening the same rejected scene"],
        "rationale": [
            {
                "label": "Reject reason",
                "value": "cost and fit did not justify adoption for this scene",
            },
        ],
        "artifacts": [
            {
                "type": "reject-note",
                "id": "rj-001",
                "purpose": "records terminal rejection for this use case",
            },
        ],
        "raw_artifacts": [],
        "timeline": [],
    },
)


def _id_sort_key(item: dict[str, Any]) -> tuple[int, int, str]:
    raw = str(item.get("artifact_id", ""))
    prefix = raw.split("-", 1)[0] if "-" in raw else ""
    number = parse_numeric_id(raw, prefix) if prefix else None
    if number is None:
        return (1, 0, raw)
    return (0, number, raw)


def _load_template() -> str:
    candidates = (
        Path(__file__).parent.parent / "templates" / _TEMPLATE_NAME,
        Path(sys.prefix) / "share" / "adop" / "templates" / _TEMPLATE_NAME,
    )
    for template_path in candidates:
        try:
            return template_path.read_text(encoding="utf-8")
        except OSError:
            continue
    raise AdopArtifactError(f"dashboard template not readable: {candidates[0]}")


def _strip_runtime_metadata(item: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in item.items() if key not in {"_path", "_adop_path"}}


def _latest(items: list[dict[str, Any]], artifact_type: str) -> dict[str, Any] | None:
    matched = [item for item in items if item.get("artifact_type") == artifact_type]
    if not matched:
        return None
    matched.sort(key=_id_sort_key)
    return matched[-1]


def _pick_first(*values: Any) -> str:
    for value in values:
        text = str(value or "").strip()
        if text:
            return text
    return "-"


def _lane_tool(scene_items: list[dict[str, Any]]) -> str:
    for item in sorted(scene_items, key=_id_sort_key, reverse=True):
        text = _pick_first(item.get("candidate_or_tool"), item.get("adoption_unit"))
        if text != "-":
            return text
    return "-"


def _lane_meta(scene_items: list[dict[str, Any]]) -> str:
    intake = _latest(scene_items, "candidate-intake-note")
    if not intake:
        return "decision record"
    flow = intake.get("data_flow") or {}
    destination = _pick_first(flow.get("destination"), "unspecified flow")
    return " / ".join(
        [
            _pick_first(intake.get("category"), "category ?"),
            _pick_first(intake.get("license"), "license ?"),
            destination,
        ]
    )


def _scene_label(scene: str) -> str:
    words = [part for part in scene.replace("_", "-").split("-") if part]
    if not words:
        return scene
    return " ".join(
        word.upper() if len(word) <= 3 else word[:1].upper() + word[1:] for word in words
    )


def _landing_target(scene_items: list[dict[str, Any]]) -> str:
    for artifact_type in ("promotion-note", "judgment-report", "trial-packet"):
        item = _latest(scene_items, artifact_type)
        if item:
            target = _pick_first(item.get("landing_target"))
            if target != "-":
                return target
    return "-"


# Lifecycle stage rank for "latest update": later stage = more recent action.
# Used as a same-day tiebreak so the headline never picks an earlier-stage note
# just because its id number happens to be larger (e.g. ci-002 over tr-001).
_EVIDENCE_STAGE: dict[str, int] = {
    "watch-note": 0,
    "candidate-intake-note": 1,
    "coupling-note": 1,
    "blocked-note": 2,
    "comparison-note": 3,
    "trial-packet": 4,
    "trial-result": 5,
    "judgment-report": 6,
    "hold-note": 6,
    "reject-note": 6,
    "promotion-note": 6,
    "deprecation-note": 7,
    "migration-note": 8,
    "archive-note": 9,
}


def _decision_owner(scene_items: list[dict[str, Any]]) -> str:
    """Who owns this decision — from the most-advanced artifact that records one."""
    best: str | None = None
    best_key: tuple[str, int] | None = None
    for item in scene_items:
        owner = _pick_first(item.get("decision_owner"))
        if owner == "-":
            continue
        key = (
            str(item.get("created_at", "")),
            _EVIDENCE_STAGE.get(str(item.get("artifact_type", "")), 0),
        )
        if best_key is None or key >= best_key:
            best_key = key
            best = owner
    return best or "-"


def _last_evidence(scene_items: list[dict[str, Any]]) -> str:
    if not scene_items:
        return "-"

    def recency_key(item: dict[str, Any]) -> tuple[str, int, int]:
        created = str(item.get("created_at", ""))
        stage = _EVIDENCE_STAGE.get(str(item.get("artifact_type", "")), 0)
        raw = str(item.get("artifact_id", ""))
        prefix = raw.split("-", 1)[0] if "-" in raw else ""
        number = parse_numeric_id(raw, prefix) if prefix else None
        return (created, stage, number or 0)

    item = max(scene_items, key=recency_key)
    label = _artifact_label(str(item.get("artifact_type", "-")))
    created = str(item.get("created_at", "")).strip()
    # Date first so the "Latest update" column reads as a date and sorts chronologically.
    return f"{created} · {label}" if created else label


def _artifact_label(artifact_type: str) -> str:
    labels = {
        "candidate-intake-note": "Intake note",
        "comparison-note": "Comparison note",
        "trial-packet": "Trial plan",
        "trial-result": "Trial result",
        "judgment-report": "Decision record",
        "promotion-note": "Approval note",
        "blocked-note": "Blocked note",
        "watch-note": "Watch note",
        "deprecation-note": "Retirement note",
        "migration-note": "Migration note",
        "archive-note": "Archive note",
        "reject-note": "Reject note",
    }
    return labels.get(artifact_type, artifact_type)


def _state_label(state: str) -> str:
    return _STATE_LABELS.get(state, state.title())


def _state_tone(state: str) -> str:
    return _STATE_TONES.get(state, "neutral")


def _state_meaning(state: str) -> str:
    return _STATE_MEANINGS.get(state, "A lifecycle state is recorded for this decision.")


def _decision_text(state: str, scene_items: list[dict[str, Any]], landing_target: str) -> str:
    if state == "promote":
        if landing_target != "-":
            return f"Approved for use at {landing_target} under recorded controls."
        return "Approved for use within the recorded controls."
    if state == "trial-ready":
        return "Trial is defined and ready to start."
    if state == "in-trial":
        return "Trial is running and waiting for a decision."
    if state == "blocked":
        return _pick_first(
            (_latest(scene_items, "blocked-note") or {}).get("block_reason"),
            "Blocked until someone makes an explicit unblock decision.",
        )
    if state == "proposed":
        return "Candidate is recorded, but comparison and trial are not complete yet."
    if state == "watch":
        return "On the radar, but no active decision exists yet."
    if state == "deprecated":
        return _pick_first(
            (_latest(scene_items, "deprecation-note") or {}).get("retirement_reason"),
            "A retirement path is recorded for this decision.",
        )
    if state == "migrating":
        target = _pick_first((_latest(scene_items, "migration-note") or {}).get("migration_target"))
        return (
            f"Replacement in progress; migrating to {target}."
            if target != "-"
            else "Replacement work is actively in progress."
        )
    if state == "archived":
        archive = _latest(scene_items, "archive-note") or {}
        end = _pick_first(archive.get("end_date"))
        successor = _pick_first(archive.get("successor_tool"))
        if end != "-" and successor != "-":
            return f"Closed on {end}; succeeded by {successor}."
        if end != "-":
            return f"Closed and archived on {end}."
        return "This decision is closed and archived."
    if state == "hold":
        return _pick_first(
            (_latest(scene_items, "hold-note") or {}).get("hold_reason"),
            "The trial closed on hold, and the decision is paused.",
        )
    if state == "reject":
        return _pick_first(
            (_latest(scene_items, "reject-note") or {}).get("reject_reason"),
            "This decision ended in rejection for this use case.",
        )
    return "A lifecycle state is recorded."


def _control_model(scene_items: list[dict[str, Any]]) -> str:
    judgment = _latest(scene_items, "judgment-report")
    if judgment:
        envelope = judgment.get("no_impact_envelope") or {}
        target_profile = judgment.get("target_project_profile") or {}
        mutation = _pick_first(target_profile.get("allowed_mutation_boundary"))
        authority = _pick_first(target_profile.get("authority_boundary"))
        if mutation != "-" or authority != "-":
            return ", ".join([part for part in (mutation, authority) if part != "-"])
        allowed = envelope.get("allowed") or []
        forbidden = envelope.get("forbidden") or []
        if allowed or forbidden:
            return f"allowed {len(allowed)} / forbidden {len(forbidden)} controls recorded"
    packet = _latest(scene_items, "trial-packet")
    if packet:
        return (
            ", ".join(
                [
                    part
                    for part in (
                        _pick_first(packet.get("mutation_boundary")),
                        _pick_first(packet.get("verification_method")),
                    )
                    if part != "-"
                ]
            )
            or "trial boundary recorded"
        )
    return "No usage limits are recorded yet."


def _allowed_forbidden(scene_items: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    # Prefer the closed-trial judgment envelope; fall back to the open trial
    # packet's envelope so in-trial / trial-ready lanes still show real limits.
    for artifact_type in ("judgment-report", "trial-packet"):
        source = _latest(scene_items, artifact_type)
        if not source:
            continue
        envelope = source.get("no_impact_envelope") or {}
        allowed = [str(item) for item in envelope.get("allowed") or []]
        forbidden = [str(item) for item in envelope.get("forbidden") or []]
        if allowed or forbidden:
            return allowed, forbidden
    return (
        ["No explicit allow-list recorded yet"],
        ["No explicit deny-list recorded yet"],
    )


def _rationale(scene_items: list[dict[str, Any]]) -> list[dict[str, str]]:
    # Retirement-tail notes win over the (older) promote judgment-report: once a
    # lane is deprecated/migrating/archived, the relevant reasoning is the
    # retirement note, not the promotion that preceded it.
    archive = _latest(scene_items, "archive-note")
    if archive:
        rows = [
            ("End date", archive.get("end_date")),
            ("Successor tool", archive.get("successor_tool")),
        ]
        surfaced = [
            {"label": label, "value": _pick_first(value)}
            for label, value in rows
            if _pick_first(value) != "-"
        ]
        return surfaced or [
            {"label": "Archived", "value": "This decision is closed and kept as history."}
        ]
    migration = _latest(scene_items, "migration-note")
    if migration:
        return [
            {"label": "Migration target", "value": _pick_first(migration.get("migration_target"))},
            {"label": "Migration plan", "value": _pick_first(migration.get("migration_plan"))},
        ]
    deprecation = _latest(scene_items, "deprecation-note")
    if deprecation:
        rows = [
            ("Retirement reason", deprecation.get("retirement_reason")),
            (
                "Replacement candidates",
                ", ".join(str(x) for x in deprecation.get("replacement_candidates") or []),
            ),
            ("Timeline", deprecation.get("timeline")),
        ]
        return [
            {"label": label, "value": _pick_first(value)}
            for label, value in rows
            if _pick_first(value) != "-"
        ]
    judgment = _latest(scene_items, "judgment-report")
    if judgment:
        rows = [
            ("Judgment reason", judgment.get("judgment_reason")),
            ("Observed effect", judgment.get("observed_effect_summary")),
            ("Root-cause hypothesis", judgment.get("root_cause_hypothesis")),
            ("Why this problem recurred", judgment.get("why_this_problem_recurred")),
            (
                "Preventive action",
                ", ".join(str(x) for x in judgment.get("preventive_action") or []),
            ),
            ("Recurring control decision", judgment.get("recurring_control_decision")),
        ]
        return [
            {"label": label, "value": _pick_first(value)}
            for label, value in rows
            if _pick_first(value) != "-"
        ]
    reject_note = _latest(scene_items, "reject-note")
    if reject_note:
        return [{"label": "Reject reason", "value": _pick_first(reject_note.get("reject_reason"))}]
    blocked = _latest(scene_items, "blocked-note")
    if blocked:
        return [{"label": "Block reason", "value": _pick_first(blocked.get("block_reason"))}]
    intake = _latest(scene_items, "candidate-intake-note")
    if intake:
        return [
            {"label": "Why now", "value": _pick_first(intake.get("intake_reason"))},
            {
                "label": "Root-cause hypothesis",
                "value": _pick_first(intake.get("root_cause_hypothesis")),
            },
        ]
    watch = _latest(scene_items, "watch-note")
    if watch:
        return [{"label": "Interest reason", "value": _pick_first(watch.get("interest_reason"))}]
    return [{"label": "Status", "value": "No reason fields are available yet for this decision."}]


def _artifacts(scene_items: list[dict[str, Any]]) -> list[dict[str, str]]:
    rows = []
    for item in sorted(scene_items, key=_id_sort_key):
        rows.append(
            {
                "type": str(item.get("artifact_type", "-")),
                "id": str(item.get("artifact_id", "-")),
                "purpose": _artifact_purpose(item),
            }
        )
    return rows


def _artifact_purpose(item: dict[str, Any]) -> str:
    artifact_type = str(item.get("artifact_type", ""))
    if artifact_type == "candidate-intake-note":
        return "records why this decision entered review"
    if artifact_type == "comparison-note":
        return "records the narrowed candidate choice"
    if artifact_type == "trial-packet":
        return "records who runs the trial, where approved use may happen, and the trial boundary"
    if artifact_type == "trial-result":
        return "records what happened during the trial"
    if artifact_type == "judgment-report":
        return "records why the decision was reached"
    if artifact_type == "promotion-note":
        return "marks this decision as approved for operational use"
    if artifact_type == "blocked-note":
        return "records why this decision cannot move forward yet"
    if artifact_type == "watch-note":
        return "records early interest only"
    if artifact_type == "deprecation-note":
        return "records the retirement decision"
    if artifact_type == "migration-note":
        return "records the migration plan"
    if artifact_type == "archive-note":
        return "records final closure of this decision"
    return "records evidence for this decision"


def _timeline(scene_items: list[dict[str, Any]], state: str) -> list[dict[str, Any]]:
    def has(artifact_type: str) -> bool:
        return _latest(scene_items, artifact_type) is not None

    return [
        {
            "step": "Intake",
            "body": "This decision has an explicit entry reason, instead of living in chat history.",
            "done": has("candidate-intake-note") or has("watch-note"),
        },
        {
            "step": "Comparison",
            "body": "Candidate choice was narrowed to one tool in one use case.",
            "done": has("comparison-note"),
        },
        {
            "step": "Trial",
            "body": "The trial boundary, allowed use area, and verification method were written down.",
            "done": has("trial-packet"),
        },
        {
            "step": "Judgment",
            "body": "Observed effect and decision reasoning were recorded.",
            "done": has("judgment-report"),
        },
        {
            "step": "Operational state",
            "body": f"This decision is currently in the {_state_label(state)} lifecycle state.",
            "done": True,
        },
    ]


def _lane_summary(
    scene_items: list[dict[str, Any]], state: str, lane: dict[str, Any]
) -> dict[str, str]:
    judgment = _latest(scene_items, "judgment-report")
    next_text = _default_next_text(state, lane["landing_target"])
    summary = {
        "headline": f"{lane['tool']} is in the {_state_label(state)} state for the {lane['scene']} use case.",
        "why_it_matters": "This keeps tool decisions reviewable instead of rediscovering them later.",
        "why_this_state": _decision_text(state, scene_items, str(lane["landing_target"])),
        "what_happens_next": next_text
        if state == "promote"
        else _pick_first(judgment.get("next_action") if judgment else "", next_text),
        "change_condition": _default_change_condition(state),
    }
    if judgment and judgment.get("judgment_reason"):
        summary["why_this_state"] = str(judgment["judgment_reason"])
    return summary


def _default_next_text(state: str, landing_target: str) -> str:
    if state == "promote":
        return "Use the tool only within the approved area and rules."
    if state == "trial-ready":
        return "Run the bounded trial and record what happened."
    if state == "in-trial":
        return "Close the trial and record the decision."
    if state == "blocked":
        return "Resolve the blocker, then reopen this decision through intake or compare."
    if state == "proposed":
        return "Narrow this decision through comparison and trial planning."
    if state == "watch":
        return "Decide whether to convert this watch item into a real intake."
    if state == "deprecated":
        return "Complete migration or archive planning."
    if state == "migrating":
        return "Finish the replacement work and archive the retired decision."
    if state == "archived":
        return "No further action is required unless a materially new review starts."
    return "Continue this decision using the next lifecycle command."


def _next_command(scene: str, state: str, scene_items: list[dict[str, Any]]) -> str:
    if state == "watch":
        return f'adop quick-intake --scene {scene} --candidate <tool> --source doc --why-now "<reason>"'
    if state == "proposed":
        return f"adop quick-compare --scene {scene} --candidate <tool> --candidate <other> --selected <tool>"
    if state == "trial-ready":
        return f"adop quick-trial --scene {scene} --mode review-assist --executor <who> --decision-owner <owner> --landing-target <target>"
    if state == "in-trial":
        packet = _latest(scene_items, "trial-packet")
        trial_id = _pick_first((packet or {}).get("artifact_id"), "tr-001")
        return (
            f"adop quick-close-trial --trial-id {trial_id} "
            f'--verdict <promote|hold|reject> --observed-effect "<what you saw>"'
        )
    if state == "blocked":
        return f'adop unblock --scene {scene} --why-unblocked "<what changed>"'
    if state == "hold":
        return f"adop quick-compare --scene {scene} --candidate <tool> --candidate <other> --selected <tool>"
    if state == "deprecated":
        return f'adop migrate --scene {scene} --migration-target <target> --migration-plan "<plan>"'
    if state == "migrating":
        return f"adop archive --scene {scene} --end-date <YYYY-MM-DD>"
    if state == "reject":
        return "Use a new scene name for any materially new evaluation."
    if state == "archived":
        return "No next command. This decision is closed but retained as history."
    return "No recommended next command."


def _command_details(state: str, scene: str) -> list[dict[str, str]]:
    if state == "watch":
        return [
            {
                "label": "Why this command",
                "value": "The tool is only being watched. Intake is the first command that turns interest into a recorded review.",
            },
            {
                "label": "Use it when",
                "value": "You have decided the tool should enter formal review for this use case.",
            },
            {
                "label": "Do not use it when",
                "value": "The team is still only collecting ideas and is not ready to open a real review.",
            },
            {
                "label": "Result",
                "value": "ADOP records why the review is starting and moves this decision out of watch-only status.",
            },
        ]
    if state == "proposed":
        return [
            {
                "label": "Why this command",
                "value": "The candidate exists, but ADOP still needs one selected option before trial planning can be trusted.",
            },
            {
                "label": "Use it when",
                "value": "You are ready to narrow the review to one chosen candidate for this use case.",
            },
            {
                "label": "Do not use it when",
                "value": "You still need to gather candidates or the selected tool is not decided yet.",
            },
            {
                "label": "Result",
                "value": "ADOP records the chosen candidate and prepares the decision for bounded trial setup.",
            },
        ]
    if state == "trial-ready":
        return [
            {
                "label": "Why this command",
                "value": "Comparison is complete, but ADOP still needs the trial boundary, owner, and target before execution begins.",
            },
            {
                "label": "Use it when",
                "value": "The team is ready to start the bounded trial under explicit ownership and scope.",
            },
            {
                "label": "Do not use it when",
                "value": "The trial owner, execution mode, or allowed use area is still undecided.",
            },
            {
                "label": "Result",
                "value": "ADOP records the trial plan and moves the review into an executable trial phase.",
            },
        ]
    if state == "in-trial":
        return [
            {
                "label": "Why this command",
                "value": "Trial output exists, but ADOP still needs the final decision to close the review properly.",
            },
            {
                "label": "Use it when",
                "value": "The bounded trial has finished and you are ready to record promote, hold, or reject.",
            },
            {
                "label": "Do not use it when",
                "value": "Evidence is still incomplete or the team has not decided the verdict yet.",
            },
            {
                "label": "Result",
                "value": "ADOP records the outcome and moves the decision into its next explicit lifecycle state.",
            },
        ]
    if state == "blocked":
        return [
            {
                "label": "Why this command",
                "value": "This decision is blocked. Unblock exists to record that the blocking condition is actually resolved.",
            },
            {
                "label": "Use it when",
                "value": "The blocker has been cleared and you need to record what changed.",
            },
            {
                "label": "Do not use it when",
                "value": "The blocker still exists, or you are only reviewing the situation without resolving it.",
            },
            {
                "label": "Result",
                "value": "ADOP removes the blocked state and reopens the decision for the next review step.",
            },
        ]
    if state == "hold":
        return [
            {
                "label": "Why this command",
                "value": "The earlier trial paused. Comparison is the clean way to restart the review with a fresh narrowed choice.",
            },
            {
                "label": "Use it when",
                "value": "You want to resume the paused review and choose the next candidate path.",
            },
            {
                "label": "Do not use it when",
                "value": "The review should remain paused or a blocker must be resolved first.",
            },
            {
                "label": "Result",
                "value": "ADOP records the resumed comparison and moves the decision back toward a bounded trial.",
            },
        ]
    if state == "deprecated":
        return [
            {
                "label": "Why this command",
                "value": "Retirement has been decided, but ADOP still needs the actual migration target and plan.",
            },
            {
                "label": "Use it when",
                "value": "A replacement path is agreed and the team is ready to record migration work.",
            },
            {
                "label": "Do not use it when",
                "value": "The replacement target or migration plan is still unclear.",
            },
            {
                "label": "Result",
                "value": "ADOP records the replacement plan and marks the decision as actively being replaced.",
            },
        ]
    if state == "migrating":
        return [
            {
                "label": "Why this command",
                "value": "Replacement work is already underway. Archive is the final step that closes the old decision.",
            },
            {
                "label": "Use it when",
                "value": "Migration is complete and the retired decision should be kept only as history.",
            },
            {
                "label": "Do not use it when",
                "value": "The old tool is still in use or migration work is not actually finished.",
            },
            {
                "label": "Result",
                "value": "ADOP closes the decision and retains it only as historical record.",
            },
        ]
    if state == "reject":
        return [
            {
                "label": "Why there is no command",
                "value": "A reject decision is terminal for this use case.",
            },
            {
                "label": "Use a new review when",
                "value": "A materially different evaluation must begin later under a new use case key.",
            },
        ]
    if state == "archived":
        return [
            {
                "label": "Why there is no command",
                "value": "This decision is already closed and kept only for historical reference.",
            },
            {
                "label": "Use a new review when",
                "value": "A materially new evaluation needs to start instead of reviving old history.",
            },
        ]
    if state == "promote":
        return [
            {
                "label": "Why there is no command",
                "value": "The decision is already approved, so no normal lifecycle command is required now.",
            },
            {
                "label": "What to do instead",
                "value": "Keep use inside the approved area and recorded rules until retirement is needed.",
            },
        ]
    return [
        {
            "label": "Why this command",
            "value": "This is the next recorded lifecycle move for the decision.",
        },
        {"label": "Result", "value": "ADOP records the next explicit state change."},
    ]


def _retirement_command_details() -> list[dict[str, str]]:
    return [
        {
            "label": "Why this command",
            "value": "The tool is still approved. This command exists only to record that retirement has formally started.",
        },
        {
            "label": "Use it when",
            "value": "The team has decided the approved tool should stop being the active path.",
        },
        {
            "label": "Do not use it when",
            "value": "You only want to pause usage temporarily or there is not yet a real retirement decision.",
        },
        {
            "label": "Result",
            "value": "ADOP records the retirement start and moves the decision into the removal phase.",
        },
    ]


def _command_surface(scene: str, state: str, scene_items: list[dict[str, Any]]) -> dict[str, Any]:
    next_command = _next_command(scene, state, scene_items)
    surface: dict[str, Any] = {
        "next_command_label": "Recommended next CLI command",
        "next_command_note": "This is a state-change command, not a read-only lookup command.",
        "next_command_details": _command_details(state, scene),
        "next_command": next_command,
        "next_command_copyable": next_command.startswith("adop "),
        "retirement_command_label": "",
        "retirement_command_note": "",
        "retirement_command_details": [],
        "retirement_command": "",
        "retirement_command_copyable": False,
    }
    if state == "promote":
        surface.update(
            {
                "next_command_label": "No required next command",
                "next_command_note": "No state change is required right now.",
                "next_command": "",
                "next_command_copyable": False,
                "retirement_command_label": "Retirement command",
                "retirement_command_note": "This command changes the decision from approved into retirement tracking.",
                "retirement_command_details": _retirement_command_details(),
                "retirement_command": f'adop deprecate --scene {scene} --retirement-reason "<reason>" --replacement-candidate "<tool>" --timeline "<when>"',
                "retirement_command_copyable": True,
            }
        )
    elif state == "archived":
        surface.update(
            {
                "next_command_label": "No required next command",
                "next_command_note": "Archived decisions stay in the record. They are not removed from history.",
                "next_command": "",
                "next_command_copyable": False,
            }
        )
    elif state == "reject":
        surface.update(
            {
                "next_command_label": "Next guidance",
                "next_command_note": "Rejected decisions are terminal for this scene. Start a materially new evaluation with a new scene name.",
                "next_command_copyable": False,
            }
        )
    return surface


def _default_change_condition(state: str) -> str:
    if state == "promote":
        return "A retirement, migration, or archive note would move this decision beyond promoted."
    if state in {"trial-ready", "in-trial"}:
        return (
            "A decision record will decide whether this review becomes promoted, hold, or reject."
        )
    if state == "blocked":
        return "An unblock path plus renewed intake would change this decision."
    if state == "watch":
        return "A candidate-intake-note would move this from watch into active evaluation."
    if state == "proposed":
        return "A comparison record would move this decision into trial-ready."
    return "A later lifecycle record would change this decision state."


def _is_historical(state: str) -> bool:
    return state in _HISTORICAL_STATES


def _build_lane(scene: str, scene_items: list[dict[str, Any]], state: str) -> dict[str, Any]:
    tool = _lane_tool(scene_items)
    landing_target = _landing_target(scene_items)
    command_surface = _command_surface(scene, state, scene_items)
    summary = _lane_summary(
        scene_items,
        state,
        {
            "tool": tool,
            "scene": scene,
            "landing_target": landing_target,
        },
    )
    allowed, forbidden = _allowed_forbidden(scene_items)
    return {
        "scene": scene,
        "scene_label": _scene_label(scene),
        "tool": tool,
        "state": state,
        "is_historical": _is_historical(state),
        "state_label": _state_label(state),
        "state_meaning": _state_meaning(state),
        "tone": _state_tone(state),
        "decision": _decision_text(state, scene_items, landing_target),
        "next_step": _default_next_text(state, landing_target)
        if not summary["what_happens_next"]
        else summary["what_happens_next"],
        "landing_target": landing_target,
        "control_model": _control_model(scene_items),
        "decision_owner": _decision_owner(scene_items),
        "last_evidence": _last_evidence(scene_items),
        "kind_meta": _lane_meta(scene_items),
        "headline": summary["headline"],
        "why_it_matters": summary["why_it_matters"],
        "why_this_state": summary["why_this_state"],
        "what_happens_next": summary["what_happens_next"],
        "change_condition": summary["change_condition"],
        "allowed": allowed,
        "forbidden": forbidden,
        "rationale": _rationale(scene_items),
        "artifacts": _artifacts(scene_items),
        "raw_artifacts": [
            _strip_runtime_metadata(item) for item in sorted(scene_items, key=_id_sort_key)
        ],
        "timeline": _timeline(scene_items, state),
        "is_sample": False,
        **command_surface,
    }


def _sample_lane(base: dict[str, Any]) -> dict[str, Any]:
    lane = dict(base)
    lane["scene_label"] = _scene_label(str(lane["scene"]))
    lane["is_historical"] = _is_historical(str(lane["state"]))
    lane["state_label"] = _state_label(str(lane["state"]))
    lane["state_meaning"] = _state_meaning(str(lane["state"]))
    lane["tone"] = _state_tone(str(lane["state"]))
    lane["headline"] = (
        f"{lane['tool']} is in the {lane['state_label']} state for the {lane['scene']} use case."
    )
    lane["next_step"] = _default_next_text(str(lane["state"]), str(lane.get("landing_target", "-")))
    lane.update(_command_surface(str(lane["scene"]), str(lane["state"]), []))
    lane["timeline"] = lane.get("timeline") or [
        {"step": "Intake", "body": "Sample decision for layout stress testing.", "done": True},
        {"step": "Comparison", "body": "Sample decision for layout stress testing.", "done": True},
        {
            "step": "Trial",
            "body": "Sample decision for layout stress testing.",
            "done": lane["state"] in {"trial-ready", "in-trial", "promote"},
        },
        {
            "step": "Judgment",
            "body": "Sample decision for layout stress testing.",
            "done": lane["state"] == "promote",
        },
        {
            "step": "Operational state",
            "body": f"Sample decision is in the {lane['state_label']} state.",
            "done": True,
        },
    ]
    lane["is_sample"] = True
    return lane


def _clone_sample_seed(base: dict[str, Any], ordinal: int) -> dict[str, Any]:
    clone = json.loads(json.dumps(base))
    clone["scene"] = f"{base['scene']}-sample-{ordinal:03d}"
    clone["decision"] = str(base.get("decision", "Preview sample decision"))
    clone["last_evidence"] = f"preview-sample ps-{ordinal:03d}"
    clone["artifacts"] = [
        {
            "type": str(item.get("type", "sample-artifact")),
            "id": f"{item.get('id', 'sample')}-s{ordinal:03d}",
            "purpose": str(item.get("purpose", "sample decision evidence")),
        }
        for item in clone.get("artifacts", [])
    ]
    return clone


def build_dashboard_payload(
    root: Path,
    *,
    title: str = "ADOP Governance Dashboard",
    selected_scene: str | None = None,
    sample_board_count: int = 0,
) -> dict[str, Any]:
    items = load_all_artifacts(root)
    scene_states = get_scene_states(root)
    lanes = [
        _build_lane(
            scene,
            [item for item in items if str(item.get("related_scene", "")).strip() == scene],
            state,
        )
        for scene, state in scene_states.items()
    ]
    lanes.sort(key=lambda lane: (_STATE_SORT.get(str(lane["state"]), 99), str(lane["scene"])))

    if sample_board_count > len(lanes):
        existing_scenes = {str(lane["scene"]) for lane in lanes}
        available = [
            candidate
            for candidate in _SAMPLE_LANES
            if str(candidate["scene"]) not in existing_scenes
        ]
        historical_candidates = [
            candidate for candidate in available if _is_historical(str(candidate["state"]))
        ]
        active_candidates = [
            candidate for candidate in available if not _is_historical(str(candidate["state"]))
        ]

        chosen: list[dict[str, Any]] = []
        has_historical_real = any(_is_historical(str(lane["state"])) for lane in lanes)
        if not has_historical_real and historical_candidates:
            chosen.append(historical_candidates.pop(0))
        for pool in (active_candidates, historical_candidates):
            for candidate in pool:
                if len(lanes) + len(chosen) >= sample_board_count:
                    break
                chosen.append(candidate)
            if len(lanes) + len(chosen) >= sample_board_count:
                break
        if len(lanes) + len(chosen) < sample_board_count:
            seed_pool = available or list(_SAMPLE_LANES)
            ordinal = 1
            while len(lanes) + len(chosen) < sample_board_count and seed_pool:
                seed = seed_pool[(ordinal - 1) % len(seed_pool)]
                clone = _clone_sample_seed(seed, ordinal)
                if str(clone["scene"]) not in existing_scenes:
                    chosen.append(clone)
                    existing_scenes.add(str(clone["scene"]))
                ordinal += 1
        for candidate in chosen:
            lanes.append(_sample_lane(candidate))
        lanes.sort(key=lambda lane: (_STATE_SORT.get(str(lane["state"]), 99), str(lane["scene"])))

    recorded_lanes = [lane for lane in lanes if not lane["is_sample"]]
    sample_lanes = [lane for lane in lanes if lane["is_sample"]]

    selected_lane = None
    if selected_scene:
        selected_lane = next((lane for lane in lanes if str(lane["scene"]) == selected_scene), None)
    if selected_lane is None and recorded_lanes:
        selected_lane = recorded_lanes[0]
    if selected_lane is None and lanes:
        selected_lane = lanes[0]

    sample_rows_included = len(sample_lanes)
    recorded_rows = len(recorded_lanes)

    metrics = {
        "managed_lanes": len(lanes),
        "recorded_lanes": recorded_rows,
        "preview_sample_lanes": sample_rows_included,
        "promoted": sum(1 for lane in lanes if lane["state"] == "promote"),
        "proposed": sum(1 for lane in lanes if lane["state"] == "proposed"),
        "trial_ready": sum(1 for lane in lanes if lane["state"] == "trial-ready"),
        "in_trial": sum(1 for lane in lanes if lane["state"] == "in-trial"),
        "open_trials": sum(1 for lane in lanes if lane["state"] in {"trial-ready", "in-trial"}),
        "blocked": sum(1 for lane in lanes if lane["state"] == "blocked"),
        "historical": sum(1 for lane in lanes if _is_historical(str(lane["state"]))),
    }
    active_lanes = [lane for lane in recorded_lanes if not _is_historical(str(lane["state"]))]
    historical_lanes = [lane for lane in recorded_lanes if _is_historical(str(lane["state"]))]
    return {
        "title": title,
        "artifact_root": str(root),
        "metrics": metrics,
        "lanes": lanes,
        "active_lanes": active_lanes,
        "historical_lanes": historical_lanes,
        "sample_lanes": sample_lanes,
        "selected_scene": selected_lane["scene"] if selected_lane else None,
        "generated_from_records": bool(recorded_lanes),
        "sample_rows_included": sample_rows_included,
        "preview_warning": (
            f"Preview only: {sample_rows_included} sample decision{'s' if sample_rows_included != 1 else ''} are shown for layout checking. "
            "Do not treat them as project records."
            if sample_rows_included
            else ""
        ),
        "empty_state_commands": list(_EMPTY_STATE_COMMANDS),
        "reader_steps": list(_READER_STEPS),
        "operator_steps": list(_OPERATOR_STEPS),
        "empty_state": "No decision records exist yet in this record folder.",
        "state_sort": dict(_STATE_SORT),
        "initial_active_limit": 12,
        "initial_historical_limit": 12,
        "initial_sample_limit": 12,
    }


def render_dashboard_html(
    root: Path,
    *,
    title: str = "ADOP Governance Dashboard",
    selected_scene: str | None = None,
    sample_board_count: int = 0,
) -> str:
    template = _load_template()
    payload = build_dashboard_payload(
        root,
        title=title,
        selected_scene=selected_scene,
        sample_board_count=sample_board_count,
    )
    payload_json = json.dumps(payload, ensure_ascii=False)
    payload_json = (
        payload_json.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    )
    return template.replace("__ADOP_DASHBOARD_TITLE__", escape(title)).replace(
        "__ADOP_DASHBOARD_PAYLOAD__", payload_json
    )
