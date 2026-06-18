"""Gateway behavior: authn, deny-by-default intersection, human gate, tokens, audit."""
import os
import sys
from pathlib import Path

PLATFORM = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLATFORM))
os.environ.setdefault("CONNECTOR_MODE", "fixture")

from edu_agent_platform.mcp_gateway import MCPGateway, decide
from edu_agent_platform.mcp_gateway.policy import user_entitlements


def _claims(sub, role, **extra):
    return {"sub": sub, "custom:edu_role": role, **extra}


def test_fail_closed_without_subject():
    gw = MCPGateway()
    res = gw.invoke(user_claims={}, agent_id="01-student-family-concierge",
                    tool="sis.get_student_profile")
    assert res.decision == "DENY"
    assert not res.allowed


def test_read_allowed_for_entitled_student():
    gw = MCPGateway()
    res = gw.invoke(
        user_claims=_claims("u-stu", "STUDENT"),
        agent_id="01-student-family-concierge",
        tool="sis.check_application_status",
        args={},
    )
    assert res.decision == "ALLOW"
    assert res.allowed
    assert res.result  # fixture returns data
    assert res.token_jti  # a scoped token was minted


def test_agent_overreach_denied():
    # Concierge is not granted assessment.release_grade even for an admin user.
    gw = MCPGateway()
    res = gw.invoke(
        user_claims=_claims("u-admin", "ADMINISTRATOR"),
        agent_id="01-student-family-concierge",
        tool="assessment.release_grade",
    )
    assert res.decision == "DENY"


def test_user_underreach_denied():
    # The assessment agent IS granted release_grade, but a STUDENT is not entitled.
    gw = MCPGateway()
    res = gw.invoke(
        user_claims=_claims("u-stu", "STUDENT"),
        agent_id="04-assessment-grading-feedback",
        tool="assessment.release_grade",
    )
    assert res.decision == "DENY"
    assert "not entitled" in res.reason


def test_consequential_tool_requires_approval():
    gw = MCPGateway()
    # Educator IS entitled to release a grade and the agent is granted it,
    # but it is consequential -> pending approval until a reviewer is bound.
    res = gw.invoke(
        user_claims=_claims("u-teacher", "EDUCATOR"),
        agent_id="04-assessment-grading-feedback",
        tool="assessment.release_grade",
        args={"grade": "B"},
    )
    assert res.decision == "PENDING_APPROVAL"
    assert res.requires_approval

    approval = {"approved": True, "reviewer": {"sub": "u-teacher", "roles": ["EDUCATOR"]}}
    res2 = gw.invoke(
        user_claims=_claims("u-teacher", "EDUCATOR"),
        agent_id="04-assessment-grading-feedback",
        tool="assessment.release_grade",
        args={"grade": "B"},
        approval=approval,
    )
    assert res2.decision == "ALLOW"
    assert res2.allowed


def test_ferpa_rights_transfer_drops_guardian():
    # A guardian whose rights have transferred loses the GUARDIAN role.
    gw = MCPGateway()
    res = gw.invoke(
        user_claims=_claims("u-parent", "GUARDIAN", rights_transferred=True),
        agent_id="01-student-family-concierge",
        tool="sis.get_student_profile",
    )
    assert res.decision == "DENY"


def test_audit_trail_records_every_attempt():
    gw = MCPGateway()
    gw.invoke(user_claims=_claims("u-stu", "STUDENT"),
              agent_id="01-student-family-concierge", tool="sis.get_schedule")
    gw.invoke(user_claims={}, agent_id="01-student-family-concierge", tool="sis.get_schedule")
    assert len(gw.audit.records) == 2
    decisions = {r["decision"] for r in gw.audit.records}
    assert "ALLOW" in decisions and "DENY" in decisions


def test_intersection_is_symmetric():
    # decide() permits only when in BOTH agent grant and user entitlement.
    d = decide("04-assessment-grading-feedback", ["EDUCATOR"], "assessment.draft_feedback")
    assert d.allowed
    ent = user_entitlements(["STUDENT"])
    assert "assessment.release_grade" not in ent
