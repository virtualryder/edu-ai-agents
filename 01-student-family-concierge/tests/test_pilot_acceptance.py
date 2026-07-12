"""Pilot acceptance — the four governance scenarios proven live on AWS (docs/evidence/pilot-deploy.md),
asserted in-repo against the real MCP gateway so CI guards them too."""
import os
import sys
from pathlib import Path

PLATFORM = Path(__file__).resolve().parent.parent.parent / "platform_core"
sys.path.insert(0, str(PLATFORM))
os.environ.setdefault("CONNECTOR_MODE", "fixture")

from edu_agent_platform.mcp_gateway import MCPGateway

AGENT = "01-student-family-concierge"


def _student(sid="S-100"):
    return {"sub": "u-1", "custom:edu_role": "STUDENT", "student_id": sid}


def test_scenario1_public_info_allow():
    gw = MCPGateway()
    r = gw.invoke(user_claims=_student(), agent_id=AGENT, tool="kb.search_policies",
                  args={"query": "enrollment deadlines"})
    assert r.decision == "ALLOW" and r.allowed


def test_scenario2_own_record_allow():
    gw = MCPGateway()
    r = gw.invoke(user_claims=_student("S-100"), agent_id=AGENT,
                  tool="sis.get_student_profile", args={"student_id": "S-100"})
    assert r.decision == "ALLOW"


def test_scenario3_cross_record_denied():
    gw = MCPGateway()
    r = gw.invoke(user_claims=_student("S-100"), agent_id=AGENT,
                  tool="sis.get_student_profile", args={"student_id": "S-999"})
    assert r.decision == "DENY" and "record-scope" in r.reason


def test_scenario4_consequential_pending_without_approval():
    gw = MCPGateway()
    r = gw.invoke(user_claims={"sub": "u-c1", "custom:edu_role": "COUNSELOR"},
                  agent_id=AGENT, tool="comms.send_message",
                  args={"student_id": "S-100", "body": "Please submit your documents."})
    assert r.decision == "PENDING_APPROVAL" and r.requires_approval
