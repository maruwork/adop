from __future__ import annotations

from adop_state_machine import promote_gate_errors


def test_promote_gate_requires_decision_owner_and_landing_target():
    packet = {
        "writeback_target": "trial-result and judgment-report",
        "verification_method": "lint",
    }
    close_payload = {
        "verdict": "promote",
        "next_action": "promote into CI",
        "recurring_control_decision": "yes",
        "decision_owner": "",
        "landing_target": "",
    }
    errors = promote_gate_errors(packet, close_payload)
    assert "promote requires decision_owner" in errors
    assert "promote requires landing_target" in errors


def test_promote_gate_accepts_complete_payload():
    packet = {
        "writeback_target": "trial-result and judgment-report",
        "verification_method": "lint",
    }
    close_payload = {
        "verdict": "promote",
        "next_action": "promote into CI",
        "recurring_control_decision": "yes",
        "decision_owner": "lead",
        "landing_target": "ci/lint",
    }
    assert promote_gate_errors(packet, close_payload) == []
