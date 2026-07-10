"""
MCP authorization negative-test matrix — EDU hero (01-student-family-concierge).

The identical 12-case "hard proof" that every hero in the portfolio ships, proven
here against EDU's shipping gateway. Maps to the deployed edge (401 / 403 / deny);
offline the gateway returns a DENY decision or the underlying primitive raises.

EDU nuance, stated honestly:
  * Cases 1-6, 11, 12 run against the CONCIERGE hero directly.
  * Case 6 is EDU's data-class boundary expressed as FERPA record scope: a student
    may not reach ANOTHER student's record even via an entitled read.
  * Cases 7-10 exercise the gateway's shared human-approval binding. EDU reserves
    strict separation-of-duties (requestor != approver) for enrollment / procurement
    COMMITS (sis.update_enrollment_record, erp.initiate_approval), so the SoD case
    (#7) is driven through an entitled REGISTRAR on that gated commit; replay /
    tamper / expiry (#8-10) are shown on the concierge's own consequential act
    (comms.send_message, family outreach) via an entitled COUNSELOR. Same machinery.

Run:
    PYTHONPATH=platform_core:. pytest governance/tests/test_mcp_authz_matrix.py -q
"""
from __future__ import annotations

import os

# Deterministic secrets must be set BEFORE importing modules that read them at import.
os.environ.setdefault("GATEWAY_TOKEN_SECRET", "edu-authz-matrix-test-secret")
os.environ.setdefault("APPROVAL_SIGNING_SECRET", "edu-authz-matrix-approval-secret")
os.environ.pop("AUTH_ALLOW_UNVERIFIED_CLAIMS", None)   # keep JWT verification fail-closed
os.environ.pop("AUTH_JWKS_URL", None)

import pytest

from edu_agent_platform import auth
from edu_agent_platform.mcp_gateway import approvals, tokens
from edu_agent_platform.mcp_gateway.gateway import MCPGateway

CONCIERGE = "01-student-family-concierge"
DOCSVC = "07-document-accessibility-services"   # grants the SoD enrollment commit

STUDENT = {"sub": "stu-1", "custom:edu_role": "STUDENT", "student_id": "stu-1"}
COUNSELOR = {"sub": "cou-9", "custom:edu_role": "COUNSELOR"}
REGISTRAR = {"sub": "reg-7", "custom:edu_role": "REGISTRAR"}


def _gw() -> MCPGateway:
    # fixture connectors; the deny paths below never reach a system of record.
    return MCPGateway(connector_mode="fixture")


# 1 ── No token / unauthenticated -> 401 (gateway fail-closed on missing subject)
def test_01_no_token_denies():
    r = _gw().invoke(user_claims={}, agent_id=CONCIERGE, tool="kb.search_policies")
    assert r.decision == "DENY" and "authenticated subject" in r.reason


# 2 ── Bad / unverifiable token -> 401 (JWT verification fails closed)
def test_02_bad_token_denies():
    with pytest.raises(auth.AuthError):
        auth.verify_jwt("not-a-real-jwt")  # no JWKS configured, demo off -> raises


# 3 ── Valid token, MISSING scope -> 403 (token minted for tool A rejected at tool B)
def test_03_missing_scope_denies():
    tok = tokens.mint_scoped_token(
        subject="cou-9", agent_id=CONCIERGE, tool="kb.search_policies",
        scope=["kb.search_policies"],
    )
    with pytest.raises(ValueError, match="tool scope mismatch"):
        tokens.verify_scoped_token(tok, expected_tool="comms.send_message")


# 4 ── Unregistered tool -> deny (allow-list; unknown tool)
def test_04_unregistered_tool_denies():
    r = _gw().invoke(user_claims=COUNSELOR, agent_id=CONCIERGE, tool="sis.delete_universe")
    assert r.decision == "DENY" and "unknown tool" in r.reason


# 5 ── Wrong role (not entitled) -> deny (least-privilege intersection)
#     comms.send_message is granted to the agent but NOT to a STUDENT.
def test_05_wrong_role_denies():
    r = _gw().invoke(user_claims=STUDENT, agent_id=CONCIERGE, tool="comms.send_message")
    assert r.decision == "DENY" and "not entitled" in r.reason


# 6 ── Wrong data class (FERPA record boundary) -> deny
#     A student may not reach ANOTHER student's record, even via an entitled read.
def test_06_cross_record_denies():
    r = _gw().invoke(
        user_claims=STUDENT, agent_id=CONCIERGE, tool="sis.get_student_profile",
        args={"student_id": "stu-2"},   # not this student's own record
    )
    assert r.decision == "DENY" and "record-scope" in r.reason


# 7 ── Self-approval -> deny (separation of duties on the enrollment commit)
def test_07_self_approval_denies():
    args = {"student_id": "stu-2", "status": "withdrawn"}
    self_approval = approvals.sign_approval(
        reviewer={"sub": "reg-7"},                # SAME as the requesting subject
        agent_id=DOCSVC, subject="reg-7",
        tool="sis.update_enrollment_record", args=args,
    )
    r = _gw().invoke(
        user_claims=REGISTRAR, agent_id=DOCSVC,
        tool="sis.update_enrollment_record", args=args, approval=self_approval,
    )
    assert r.decision != "ALLOW"  # requestor may not approve their own commit


# 8 ── Replayed approval -> deny (single-use nonce already consumed)
def test_08_replayed_approval_denies():
    gw = _gw()
    args = {"student_id": "fam-1", "body": "Welcome message"}
    appr = approvals.sign_approval(
        reviewer={"sub": "sup-2"}, agent_id=CONCIERGE, subject="cou-9",
        tool="comms.send_message", args=args,
    )
    nonce = appr["binding"]["nonce"]
    assert gw._approval_store.consume(nonce) is True      # first use
    r = gw.invoke(user_claims=COUNSELOR, agent_id=CONCIERGE,
                  tool="comms.send_message", args=args, approval=appr)
    assert r.decision != "ALLOW"                          # replay refused


# 9 ── Tampered approval args -> deny (args hash mismatch)
def test_09_tampered_args_denies():
    appr = approvals.sign_approval(
        reviewer={"sub": "sup-2"}, agent_id=CONCIERGE, subject="cou-9",
        tool="comms.send_message", args={"student_id": "fam-1", "body": "original"},
    )
    r = _gw().invoke(
        user_claims=COUNSELOR, agent_id=CONCIERGE, tool="comms.send_message",
        args={"student_id": "fam-1", "body": "TAMPERED"}, approval=appr,
    )
    assert r.decision != "ALLOW"


# 10 ── Stale / expired approval -> deny (exp in the past)
def test_10_expired_approval_denies():
    args = {"student_id": "fam-1", "body": "hello"}
    appr = approvals.sign_approval(
        reviewer={"sub": "sup-2"}, agent_id=CONCIERGE, subject="cou-9",
        tool="comms.send_message", args=args, ttl_seconds=-10,  # already expired
    )
    r = _gw().invoke(user_claims=COUNSELOR, agent_id=CONCIERGE,
                     tool="comms.send_message", args=args, approval=appr)
    assert r.decision != "ALLOW"


# 11 ── No outbound credential -> deny (connector unreachable without a scoped token)
def test_11_no_outbound_credential_denies():
    with pytest.raises(ValueError):
        tokens.verify_scoped_token("no.valid.outbound.token", expected_tool="kb.search_policies")


# 12 ── Audit write failure -> fail-closed (no silent path without an audit trail)
def test_12_audit_failure_fails_closed():
    gw = _gw()

    def _boom(*_a, **_k):
        raise RuntimeError("audit sink unavailable")

    gw.audit.record = _boom  # type: ignore[assignment]
    with pytest.raises(RuntimeError):
        gw.invoke(user_claims=COUNSELOR, agent_id=CONCIERGE, tool="sis.delete_universe")
