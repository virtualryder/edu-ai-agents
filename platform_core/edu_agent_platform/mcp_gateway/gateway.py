"""
MCP authorization gateway — the governed front door to systems of record.

Every agent tool call passes through one enforcement point that, in order:

  1. AUTHENTICATES the acting user (verified IdP claims; fail-closed on missing sub).
  2. AUTHORIZES via deny-by-default policy with least-privilege intersection
     (agent grant ∩ user entitlement) — an agent can never exceed the human.
  3. For CONSEQUENTIAL tools (post a grade, change enrollment, send a sensitive
     determination/outreach, privileged IT remediation), requires HUMAN APPROVAL
     before execution; a verified reviewer identity is bound into the record.
  4. MINTS a short-lived token scoped to exactly that tool, carrying user context
     (no standing service account).
  5. INVOKES the tool via the connector framework (fixture or live).
  6. AUDITS the attempt (ALLOW/DENY/PENDING_APPROVAL/ERROR), PII-masked, with
     lineage to the system of record reached (FERPA disclosure recordkeeping).
  7. FAILS CLOSED on any error.

This is the reference logic for what AWS deploys as **Amazon Bedrock AgentCore
Gateway + AgentCore Identity** (or API Gateway + Lambda authorizer + STS +
Cognito + Cedar/OPA, or a self-built FastMCP server). The decision /
least-privilege / token / audit semantics are identical across all three hosting
options; each tool here corresponds to an AgentCore Gateway target.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from . import approvals as _approvals
from . import approval_store as _approval_store
from . import policy as _policy
from . import tokens as _tokens
from .audit import GatewayAuditLog
from .errors import ApprovalRequired, PolicyDenied

logger = logging.getLogger(__name__)

_ROLE_CLAIM = os.getenv("AUTH_ROLE_CLAIM", "custom:edu_role")


def _roles_from_claims(claims: Dict[str, Any]) -> List[str]:
    raw = claims.get(_ROLE_CLAIM) or claims.get("roles") or claims.get("cognito:groups") or []
    if isinstance(raw, str):
        roles = [r.strip() for r in raw.split(",") if r.strip()]
    elif isinstance(raw, (list, tuple)):
        roles = [str(r) for r in raw]
    else:
        roles = []

    # FERPA rights transfer: at 18 / postsecondary enrollment the guardian's
    # access to the student's education record ends. If the claims mark rights as
    # transferred, drop the GUARDIAN role so the intersection cannot surface the
    # student's record to the parent.
    if str(claims.get("rights_transferred", "")).strip().lower() in ("1", "true", "yes"):
        roles = [r for r in roles if r != "GUARDIAN"]
    return roles


@dataclass
class GatewayResult:
    decision: str                       # ALLOW | DENY | PENDING_APPROVAL
    tool: str
    audit_id: str
    allowed: bool = False
    result: Any = None
    reason: str = ""
    token_jti: Optional[str] = None
    requires_approval: bool = False
    scope: List[str] = field(default_factory=list)


class MCPGateway:
    def __init__(self, audit: Optional[GatewayAuditLog] = None, connector_mode: Optional[str] = None,
                 approval_store: Optional[_approval_store.ApprovalNonceStore] = None) -> None:
        self.audit = audit or GatewayAuditLog()
        self._connector_mode = connector_mode  # None -> CONNECTOR_MODE env (default fixture)
        # Single-use approval enforcement. In-memory by default; production wires a
        # DynamoDBApprovalNonceStore so a signed approval executes exactly once cluster-wide.
        self._approval_store = approval_store or _approval_store.default_store()

    def invoke(
        self,
        *,
        user_claims: Dict[str, Any],
        agent_id: str,
        tool: str,
        args: Optional[Dict[str, Any]] = None,
        approval: Optional[Dict[str, Any]] = None,
        raise_on_deny: bool = False,
    ) -> GatewayResult:
        args = args or {}
        subject = (user_claims or {}).get("sub")
        roles = _roles_from_claims(user_claims or {})

        # 1. Authentication (fail-closed: no verified subject -> deny)
        if not subject:
            aid = self.audit.record({
                "decision": "DENY", "tool": tool, "agent_id": agent_id, "user": None,
                "reason": "no authenticated subject (fail-closed)",
            })
            if raise_on_deny:
                raise PolicyDenied("no authenticated subject")
            return GatewayResult("DENY", tool, aid, reason="no authenticated subject")

        # 2. Authorization (deny-by-default, least-privilege intersection)
        decision = _policy.decide(agent_id, roles, tool)
        if not decision.allowed:
            aid = self.audit.record({
                "decision": "DENY", "tool": tool, "agent_id": agent_id, "user": subject,
                "roles": roles, "reason": decision.reason,
            })
            if raise_on_deny:
                raise PolicyDenied(decision.reason)
            return GatewayResult("DENY", tool, aid, reason=decision.reason)

        # 2b. Record-level authorization: a self-scoped principal (student/guardian)
        # may only reach their own / linked student record, even for a tool they are
        # entitled to. Staff roles operate at institutional scope (customer can narrow
        # to assigned students). Prevents a student passing another student's id.
        scope_ok, scope_reason = _policy.record_scope_ok(roles, user_claims or {}, tool, args)
        if not scope_ok:
            aid = self.audit.record({
                "decision": "DENY", "tool": tool, "agent_id": agent_id, "user": subject,
                "roles": roles, "reason": scope_reason,
            })
            if raise_on_deny:
                raise PolicyDenied(scope_reason)
            return GatewayResult("DENY", tool, aid, reason=scope_reason)

        # 3. Human approval gate for consequential tools
        if decision.requires_approval and not self._approval_associated(
            approval, agent_id=agent_id, subject=subject, tool=tool, args=args
        ):
            aid = self.audit.record({
                "decision": "PENDING_APPROVAL", "tool": tool, "agent_id": agent_id,
                "user": subject, "roles": roles,
                "reason": f"{tool} is consequential; human approval required before execution",
            })
            if raise_on_deny:
                raise ApprovalRequired(f"{tool} requires human approval")
            return GatewayResult("PENDING_APPROVAL", tool, aid, reason="human approval required",
                                 requires_approval=True, scope=decision.effective_scope)

        # 4. Mint a short-lived token scoped to exactly this tool (user context inside)
        token = _tokens.mint_scoped_token(
            subject=subject, agent_id=agent_id, tool=tool, scope=decision.effective_scope,
        )
        claims = _tokens.verify_scoped_token(token, expected_tool=tool)  # prove it round-trips

        # 5. Invoke the tool via the connector framework
        try:
            result = self._invoke_connector(decision, args)
        except Exception as exc:  # 7. fail closed on any execution error
            self.audit.record({
                "decision": "ERROR", "tool": tool, "agent_id": agent_id, "user": subject,
                "token_jti": claims["jti"], "error": type(exc).__name__, "detail": str(exc),
            })
            raise

        # 6. Audit the allowed call, with lineage to the system of record
        approver = (approval or {}).get("reviewer") if decision.requires_approval else None
        aid = self.audit.record({
            "decision": "ALLOW", "tool": tool, "agent_id": agent_id, "user": subject,
            "roles": roles, "token_jti": claims["jti"], "scope": decision.effective_scope,
            "lineage": {"connector": decision.connector_kind, "method": decision.method},
            "approved_by": approver, "args": args,
        })
        return GatewayResult("ALLOW", tool, aid, allowed=True, result=result,
                             token_jti=claims["jti"], scope=decision.effective_scope,
                             requires_approval=decision.requires_approval)

    # ── helpers ───────────────────────────────────────────────────────────────
    def _approval_associated(
        self, approval: Optional[Dict[str, Any]], *,
        agent_id: str, subject: str, tool: str, args: Optional[Dict[str, Any]],
    ) -> bool:
        """
        Is this approval valid for THIS exact transaction?

        Production: a signed, transaction-bound, single-use approval (see
        approvals.sign_approval) verified against the actual agent/user/tool/args,
        expiry, and a one-time nonce, so it can't be replayed or retargeted.

        Demo/dev: the legacy "{approved, reviewer.sub}" record is accepted ONLY
        when a demo flag is set (CONNECTOR_MODE=fixture/demo, EXTRACT_MODE=demo, or
        AUTH_ALLOW_UNVERIFIED_CLAIMS=1). In production an unsigned approval is
        rejected -- the gate cannot be passed with a hand-built dict.
        """
        if not approval:
            return False
        if approval.get("binding") or approval.get("signature"):
            # Verify the signature, binding, and expiry...
            ok, _reason = _approvals.verify_approval(
                approval, agent_id=agent_id, subject=subject, tool=tool, args=args,
                seen_nonces=None,
            )
            if not ok:
                return False
            # ...then enforce single-use via the (durable in prod) nonce store.
            nonce = (approval.get("binding") or {}).get("nonce")
            return self._approval_store.consume(nonce)
        if _approvals._demo_mode():
            reviewer = approval.get("reviewer") or {}
            return bool(approval.get("approved")) and bool(reviewer.get("sub"))
        return False

    def _invoke_connector(self, decision: "_policy.PolicyDecision", args: Dict[str, Any]) -> Any:
        from edu_agent_platform.connectors import get_connector

        conn = get_connector(decision.connector_kind, mode=self._connector_mode)
        method = getattr(conn, decision.method)
        return method(**args)
