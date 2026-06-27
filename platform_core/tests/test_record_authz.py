"""Record-level authorization: a self-scoped principal reaches only their own record."""
import os
import sys
from pathlib import Path

PLATFORM = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLATFORM))
os.environ.setdefault("CONNECTOR_MODE", "fixture")

from edu_agent_platform.mcp_gateway import MCPGateway
from edu_agent_platform.mcp_gateway.policy import record_scope_ok

TOOL = "sis.get_student_profile"


# ── unit: the decision function ───────────────────────────────────────────────
def test_student_own_record_ok():
    ok, _ = record_scope_ok(["STUDENT"], {"sub": "u1", "student_id": "S-1"}, TOOL, {"student_id": "S-1"})
    assert ok


def test_student_other_record_denied():
    ok, reason = record_scope_ok(["STUDENT"], {"sub": "u1", "student_id": "S-1"}, TOOL, {"student_id": "S-2"})
    assert not ok and "record-scope" in reason


def test_guardian_linked_ok_unlinked_denied():
    claims = {"sub": "p1", "students": ["S-1", "S-3"]}
    assert record_scope_ok(["GUARDIAN"], claims, TOOL, {"student_id": "S-3"})[0]
    assert not record_scope_ok(["GUARDIAN"], claims, TOOL, {"student_id": "S-9"})[0]


def test_staff_institutional_scope_ok():
    ok, _ = record_scope_ok(["REGISTRAR"], {"sub": "r1"}, TOOL, {"student_id": "S-anything"})
    assert ok


def test_no_target_or_non_record_tool_is_open():
    assert record_scope_ok(["STUDENT"], {"sub": "u1"}, TOOL, {})[0]               # no record named
    assert record_scope_ok(["STUDENT"], {"sub": "u1"}, "kb.search_policies", {"student_id": "S-2"})[0]


# ── integration: the gateway denies cross-record access (before connector) ─────
def test_gateway_denies_student_cross_record():
    gw = MCPGateway()
    res = gw.invoke(
        user_claims={"sub": "u-stu", "custom:edu_role": "STUDENT", "student_id": "S-1"},
        agent_id="01-student-family-concierge",
        tool=TOOL,
        args={"student_id": "S-999"},  # another student's record
    )
    assert res.decision == "DENY"
    assert "record-scope" in res.reason
