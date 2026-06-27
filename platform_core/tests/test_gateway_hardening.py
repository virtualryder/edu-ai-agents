"""Second-review hardening: connector token boundary, fail-closed record scope, SoD, telemetry."""
import os
import sys
from pathlib import Path

import pytest

PLATFORM = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLATFORM))
os.environ.setdefault("CONNECTOR_MODE", "fixture")

from edu_agent_platform.connectors import get_connector
from edu_agent_platform.mcp_gateway import MCPGateway, tokens
from edu_agent_platform.mcp_gateway import metrics as _metrics
from edu_agent_platform.mcp_gateway.gateway import _separation_ok
from edu_agent_platform.mcp_gateway.policy import record_scope_ok


# ── Gap 2: connector independently validates the gateway-issued scoped token ───
def test_connector_rejects_absent_token():
    conn = get_connector("sis")
    with pytest.raises(PermissionError):
        conn.authorize_call("", "sis.get_student_profile")


def test_connector_rejects_wrong_tool_token():
    conn = get_connector("sis")
    tok = tokens.mint_scoped_token(subject="u", agent_id="a", tool="sis.get_schedule", scope=["sis.get_schedule"])
    with pytest.raises(PermissionError):
        conn.authorize_call(tok, "sis.get_student_profile")  # token scoped to a different tool


def test_connector_accepts_matching_token():
    conn = get_connector("sis")
    tok = tokens.mint_scoped_token(subject="u", agent_id="a", tool="sis.get_schedule", scope=["sis.get_schedule"])
    conn.authorize_call(tok, "sis.get_schedule")  # no raise


# ── Gap 3: record scope fails closed on an absent/ambiguous target ─────────────
def test_guardian_missing_target_is_denied_when_ambiguous():
    ok, reason = record_scope_ok(["GUARDIAN"], {"sub": "p", "students": ["S-1", "S-2"]},
                                 "sis.get_student_profile", {})
    assert not ok and "fail-closed" in reason


def test_guardian_single_linked_resolves_without_target():
    ok, _ = record_scope_ok(["GUARDIAN"], {"sub": "p", "students": ["S-1"]},
                            "sis.get_student_profile", {})
    assert ok


# ── Gap 4: separation of duties for the highest-risk commits ───────────────────
def test_separation_of_duties_blocks_self_approval():
    appr = {"approved": True, "reviewer": {"sub": "u-reg"}}
    assert not _separation_ok("sis.update_enrollment_record", appr, subject="u-reg")
    assert _separation_ok("sis.update_enrollment_record", appr, subject="u-other")
    assert _separation_ok("assessment.release_grade", appr, subject="u-reg")  # not SoD-required


def test_gateway_blocks_self_approved_enrollment_change():
    gw = MCPGateway()
    res = gw.invoke(
        user_claims={"sub": "u-reg", "custom:edu_role": "REGISTRAR"},
        agent_id="07-document-accessibility-services",
        tool="sis.update_enrollment_record",
        args={"student_id": "S-1", "status": "enrolled"},
        approval={"approved": True, "reviewer": {"sub": "u-reg"}},  # requestor == approver
    )
    assert res.decision == "PENDING_APPROVAL"  # separation of duties refused it


# ── Gap 7: the gateway emits the telemetry the observability stack alarms on ───
def test_denied_call_emits_metric():
    _metrics.reset()
    gw = MCPGateway()
    gw.invoke(user_claims={"sub": "u", "custom:edu_role": "ADMINISTRATOR"},
              agent_id="01-student-family-concierge", tool="assessment.release_grade")
    assert any(r["metric"] == _metrics.TOOL_AUTH_DENIED for r in _metrics.recorded())
