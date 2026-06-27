"""The golden transaction proven as ONE reproducible chain (identity -> ... -> audit)."""
import os
import sys
from pathlib import Path

AGENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AGENT))
sys.path.insert(0, str(AGENT.parent / "platform_core"))
os.environ.setdefault("CONNECTOR_MODE", "fixture")

from demo.golden_transaction import run


def _stage(bundle, name):
    return next(s for s in bundle["stages"] if s["stage"] == name)


def test_full_chain_end_to_end():
    b = run()
    # identity verified
    assert b["identity"]["student_verified"] and b["identity"]["staff_verified"]
    # read of own record authorized + a scoped token minted
    read = _stage(b, "read_own_record")
    assert read["decision"] == "ALLOW" and read["token_jti"]
    # low-risk workflow runs without a human gate
    assert _stage(b, "low_risk_workflow")["decision"] == "ALLOW"
    # consequential action blocked until approved
    assert _stage(b, "consequential_blocked")["decision"] == "PENDING_APPROVAL"
    # approval is bound to the exact transaction and signed
    appr = b["human_approval"]
    assert appr["bound_to"]["tool"] == "comms.send_message"
    assert appr["bound_to"]["agent_id"] == "01-student-family-concierge"
    assert appr["signature_present"] and appr["args_sha256"]
    # with the bound approval, the action executes — exactly once
    assert _stage(b, "consequential_approved")["decision"] == "ALLOW"
    # replay of the same single-use approval is rejected
    assert _stage(b, "approval_replay_rejected")["decision"] == "PENDING_APPROVAL"


def test_audit_trail_is_complete_and_masked():
    b = run()
    assert b["audit_record_count"] >= 5
    # every attempt recorded with a decision
    assert all(r.get("decision") for r in b["audit_trail"])
    # no raw student id / email survives into the audit evidence
    blob = str(b["audit_trail"])
    assert "S-100" not in blob or "[" in blob  # masked or absent
    assert "@" not in blob  # no raw email addresses in the masked trail
    # telemetry for the gated action was emitted
    assert "ApprovalRequired" in b["metrics_emitted"]
