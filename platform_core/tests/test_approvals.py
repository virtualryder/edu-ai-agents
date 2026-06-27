"""Transaction-bound, single-use approvals: binding, replay, retarget, prod gating."""
import os
import sys
from pathlib import Path

PLATFORM = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLATFORM))
os.environ.setdefault("CONNECTOR_MODE", "fixture")

from edu_agent_platform.mcp_gateway import MCPGateway
from edu_agent_platform.mcp_gateway import approvals as _approvals

AGENT = "04-assessment-grading-feedback"
TOOL = "assessment.release_grade"


def _teacher():
    return {"sub": "u-teacher", "custom:edu_role": "EDUCATOR"}


def _reviewer():
    return {"sub": "lead-1", "roles": ["EDUCATOR"], "name": "Dept Lead"}


def test_signed_approval_bound_to_exact_transaction_allows():
    gw = MCPGateway(connector_mode="fixture")
    args = {"grade": "B"}
    appr = _approvals.sign_approval(reviewer=_reviewer(), agent_id=AGENT,
                                    subject="u-teacher", tool=TOOL, args=args)
    res = gw.invoke(user_claims=_teacher(), agent_id=AGENT, tool=TOOL, args=args, approval=appr)
    assert res.decision == "ALLOW" and res.allowed


def test_signed_approval_for_different_args_is_rejected():
    gw = MCPGateway(connector_mode="fixture")
    appr = _approvals.sign_approval(reviewer=_reviewer(), agent_id=AGENT,
                                    subject="u-teacher", tool=TOOL, args={"grade": "B"})
    # Same approval, but the agent now tries to release a DIFFERENT grade.
    res = gw.invoke(user_claims=_teacher(), agent_id=AGENT, tool=TOOL,
                    args={"grade": "A"}, approval=appr)
    assert res.decision == "PENDING_APPROVAL"


def test_signed_approval_is_single_use_replay_rejected():
    gw = MCPGateway(connector_mode="fixture")
    args = {"grade": "B"}
    appr = _approvals.sign_approval(reviewer=_reviewer(), agent_id=AGENT,
                                    subject="u-teacher", tool=TOOL, args=args)
    first = gw.invoke(user_claims=_teacher(), agent_id=AGENT, tool=TOOL, args=args, approval=appr)
    second = gw.invoke(user_claims=_teacher(), agent_id=AGENT, tool=TOOL, args=args, approval=appr)
    assert first.decision == "ALLOW"
    assert second.decision == "PENDING_APPROVAL"  # nonce already used


def test_tampered_signature_is_rejected():
    args = {"grade": "B"}
    appr = _approvals.sign_approval(reviewer=_reviewer(), agent_id=AGENT,
                                    subject="u-teacher", tool=TOOL, args=args)
    appr["binding"]["tool"] = "assessment.draft_feedback"  # retarget without re-signing
    ok, reason = _approvals.verify_approval(appr, agent_id=AGENT, subject="u-teacher",
                                            tool="assessment.draft_feedback", args=args)
    assert not ok and "signature" in reason


def test_production_mode_rejects_unsigned_approval(monkeypatch):
    # Remove every demo flag -> production gating.
    monkeypatch.delenv("CONNECTOR_MODE", raising=False)
    monkeypatch.delenv("EXTRACT_MODE", raising=False)
    monkeypatch.delenv("AUTH_ALLOW_UNVERIFIED_CLAIMS", raising=False)
    gw = MCPGateway(connector_mode="fixture")  # connector still works; gating reads env
    unsigned = {"approved": True, "reviewer": {"sub": "lead-1"}}
    res = gw.invoke(user_claims=_teacher(), agent_id=AGENT, tool=TOOL,
                    args={"grade": "B"}, approval=unsigned)
    assert res.decision == "PENDING_APPROVAL"  # hand-built dict cannot pass the prod gate

    # A properly signed, bound approval still works in production.
    appr = _approvals.sign_approval(reviewer=_reviewer(), agent_id=AGENT,
                                    subject="u-teacher", tool=TOOL, args={"grade": "B"})
    ok = gw.invoke(user_claims=_teacher(), agent_id=AGENT, tool=TOOL,
                   args={"grade": "B"}, approval=appr)
    assert ok.decision == "ALLOW"
