"""Reviewer service: authentication, entitlement, separation of duties, single-use issuance."""
import os
import sys
from pathlib import Path

PLATFORM = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLATFORM))
os.environ.setdefault("CONNECTOR_MODE", "fixture")

from edu_agent_platform.mcp_gateway import MCPGateway
from edu_agent_platform.reviewer import ReviewService

CONCIERGE = "01-student-family-concierge"
ENROLL_AGENT = "07-document-accessibility-services"


def _claims(sub, role):
    return {"sub": sub, "custom:edu_role": role}


def test_unentitled_reviewer_is_refused():
    svc = ReviewService()
    item = svc.enqueue(agent_id=CONCIERGE, requester_sub="u-staff",
                       tool="comms.send_message", args={"body": "hi"}, summary="Outreach")
    # A STUDENT is not entitled to send messages, so cannot approve one.
    dec = svc.decide(_claims("u-stu", "STUDENT"), item.id)
    assert not dec.approved and "not entitled" in dec.reason


def test_list_pending_is_entitlement_filtered():
    svc = ReviewService()
    svc.enqueue(agent_id=CONCIERGE, requester_sub="u-staff",
                tool="comms.send_message", args={}, summary="Outreach")
    assert svc.list_pending(_claims("a", "ADMINISTRATOR"))      # entitled -> visible
    assert svc.list_pending(_claims("s", "STUDENT")) == []      # not entitled -> hidden


def test_separation_of_duties_blocks_self_approval():
    svc = ReviewService()
    item = svc.enqueue(agent_id=ENROLL_AGENT, requester_sub="u-reg",
                       tool="sis.update_enrollment_record",
                       args={"student_id": "S-1", "status": "enrolled"}, summary="Enroll")
    same = svc.decide(_claims("u-reg", "REGISTRAR"), item.id)        # requester == approver
    assert not same.approved and "separation of duties" in same.reason
    # a different registrar may approve
    item2 = svc.enqueue(agent_id=ENROLL_AGENT, requester_sub="u-reg",
                        tool="sis.update_enrollment_record",
                        args={"student_id": "S-1", "status": "enrolled"}, summary="Enroll")
    other = svc.decide(_claims("u-reg-2", "REGISTRAR"), item2.id)
    assert other.approved and other.approval


def test_issued_approval_passes_gateway_exactly_once():
    svc = ReviewService()
    args = {"student_id": "S-1", "channel": "email", "body": "Welcome"}
    item = svc.enqueue(agent_id=CONCIERGE, requester_sub="u-staff",
                       tool="comms.send_message", args=args, summary="Outreach")
    dec = svc.decide(_claims("u-super", "ADMINISTRATOR"), item.id)
    assert dec.approved

    gw = MCPGateway()
    requester = _claims("u-staff", "ADMINISTRATOR")
    first = gw.invoke(user_claims=requester, agent_id=CONCIERGE,
                      tool="comms.send_message", args=args, approval=dec.approval)
    second = gw.invoke(user_claims=requester, agent_id=CONCIERGE,
                       tool="comms.send_message", args=args, approval=dec.approval)
    assert first.decision == "ALLOW"
    assert second.decision == "PENDING_APPROVAL"  # single-use: replay rejected


def test_decision_is_audited():
    svc = ReviewService()
    item = svc.enqueue(agent_id=CONCIERGE, requester_sub="u-staff",
                       tool="comms.send_message", args={}, summary="Outreach")
    svc.decide(_claims("u-super", "ADMINISTRATOR"), item.id)
    events = {e["event"] for e in svc.audit}
    assert "enqueued" in events and "approved" in events
