"""
Golden transaction — the ONE complete path, proven end-to-end and reproducible.

The second review's headline ask: prove a single transaction across the whole chain
and publish evidence —

    verified identity -> agent -> policy gateway -> scoped tool token ->
    connector (system of record) -> human approval (signed, bound, single-use) ->
    verified result -> immutable, PII-masked audit

This runs that chain in-process against the fixture systems of record (no AWS, no
network, no API key), through the REAL MCPGateway, and writes a structured evidence
bundle to demo/evidence/golden_transaction_evidence.json. `tests/test_end_to_end.py`
asserts every stage. Point CONNECTOR_MODE=live + <KIND>_BASE_URL at real systems to
run the identical chain over HTTP.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

_HERE = Path(__file__).resolve().parent
_AGENT = _HERE.parent
sys.path.insert(0, str(_AGENT.parent / "platform_core"))

os.environ.setdefault("CONNECTOR_MODE", "fixture")  # demo mode (fixtures)

from edu_agent_platform.auth import verify_jwt, record_reviewer_identity
from edu_agent_platform.mcp_gateway import MCPGateway, metrics as _metrics
from edu_agent_platform.mcp_gateway import approvals as _approvals

AGENT_ID = "01-student-family-concierge"

# A student self-serves reads of their OWN record; staff send consequential outreach;
# a separate supervisor reviews/approves it.
STUDENT = {"sub": "u-stu-100", "custom:edu_role": "STUDENT", "student_id": "S-100"}
STAFF = {"sub": "u-staff-7", "custom:edu_role": "ADMINISTRATOR", "name": "A. Staff"}
SUPERVISOR = {"sub": "u-super-1", "custom:edu_role": "ADMINISTRATOR", "name": "S. Supervisor"}


def _stage(name: str, res: Any, **extra) -> Dict[str, Any]:
    return {
        "stage": name,
        "decision": res.decision,
        "allowed": res.allowed,
        "reason": res.reason,
        "token_jti": getattr(res, "token_jti", None),
        "scope": getattr(res, "scope", []),
        "audit_id": res.audit_id,
        **extra,
    }


def run() -> Dict[str, Any]:
    _metrics.reset()
    gw = MCPGateway()  # one instance -> one shared audit log + single-use nonce store
    stages = []

    # 1. Verified identity (demo: a pre-decoded claims dict is accepted only in demo
    #    mode; production verifies a signed JWT — see auth.verify_jwt).
    student = verify_jwt(STUDENT)
    staff = verify_jwt(STAFF)
    identity = {"stage": "identity", "student_verified": student["sub"],
                "staff_verified": staff["sub"], "mode": "demo (claims dict accepted)"}

    # 2. Read of the student's OWN record (record-scope enforced).
    r_read = gw.invoke(user_claims=student, agent_id=AGENT_ID,
                       tool="sis.check_application_status", args={"student_id": "S-100"})
    stages.append(_stage("read_own_record", r_read))

    # 3. Low-risk workflow — open an advising case (no human gate).
    r_case = gw.invoke(user_claims=staff, agent_id=AGENT_ID,
                       tool="crm.create_advising_case",
                       args={"student_id": "S-100", "topic": "registration"})
    stages.append(_stage("low_risk_workflow", r_case))

    # 4. CONSEQUENTIAL outbound message — BLOCKED until a human approves.
    send_args = {"student_id": "S-100", "channel": "email",
                 "body": "Your registration window opens Monday."}
    r_blocked = gw.invoke(user_claims=staff, agent_id=AGENT_ID,
                          tool="comms.send_message", args=send_args)
    stages.append(_stage("consequential_blocked", r_blocked))

    # 5. A verified human reviewer signs a transaction-bound, single-use approval.
    reviewer = record_reviewer_identity(verify_jwt(SUPERVISOR), "approved",
                                        "Approved family outreach")["reviewer"]
    approval = _approvals.sign_approval(reviewer=reviewer, agent_id=AGENT_ID,
                                        subject=staff["sub"], tool="comms.send_message",
                                        args=send_args)
    approval_evidence = {
        "stage": "human_approval_signed",
        "reviewer": approval["reviewer"]["sub"],
        "bound_to": {k: approval["binding"][k] for k in ("agent_id", "sub", "tool")},
        "args_sha256": approval["binding"]["args_sha256"],
        "single_use_nonce": approval["binding"]["nonce"][:8] + "…",
        "expires_at": approval["binding"]["exp"],
        "signature_present": bool(approval["signature"]),
    }

    # 6. With the bound approval, the consequential action executes — exactly once.
    r_send = gw.invoke(user_claims=staff, agent_id=AGENT_ID, tool="comms.send_message",
                       args=send_args, approval=approval)
    stages.append(_stage("consequential_approved", r_send))

    # 7. Replay of the same approval is rejected (single-use).
    r_replay = gw.invoke(user_claims=staff, agent_id=AGENT_ID, tool="comms.send_message",
                         args=send_args, approval=approval)
    stages.append(_stage("approval_replay_rejected", r_replay))

    bundle = {
        "transaction": "golden-path-01",
        "chain": ["identity", "policy_gateway", "scoped_token", "connector_sor",
                  "human_approval", "verified_result", "immutable_audit"],
        "identity": identity,
        "stages": stages,
        "human_approval": approval_evidence,
        "metrics_emitted": sorted({m["metric"] for m in _metrics.recorded()}),
        "audit_trail": gw.audit.records,  # PII-masked, append-only
        "audit_record_count": len(gw.audit.records),
    }
    return bundle


def main() -> int:
    bundle = run()
    out = _HERE / "evidence" / "golden_transaction_evidence.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bundle, indent=2, default=str))
    print(f"Golden transaction complete. Evidence -> {out}")
    for s in bundle["stages"]:
        print(f"  {s['stage']:28} {s['decision']:18} {s['reason'][:48]}")
    print(f"  metrics emitted: {bundle['metrics_emitted']}")
    print(f"  audit records:   {bundle['audit_record_count']} (PII-masked, append-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
