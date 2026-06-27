"""
Reviewer service — the production human-in-the-loop approval path.

When the gateway returns PENDING_APPROVAL for a consequential action, the proposed
action is enqueued for a named human. This service implements the review sequence a
CISO expects, end-to-end and testable without a UI framework:

  1. Reviewer authenticates (verified claims; production = a signed JWT).
  2. Reviewer entitlement is verified — you may only approve an action you are
     yourself entitled to perform (role ∩ tool entitlement).
  3. The reviewer is shown the EXACT proposed action and canonical arguments.
  4. Separation of duties is enforced — for the highest-risk commits the approver
     must not be the requester.
  5. On approval, a transaction-bound, single-use, expiring approval is SIGNED and
     issued (approvals.sign_approval) — bound to the exact agent/user/tool/args.
  6. The bound approval is submitted to the gateway (or a Step Functions callback)
     and is rejected on replay (single-use nonce).
  7. The decision is written to the audit trail.

`ReviewQueue` is in-memory here; production backs it with DynamoDB (and the
Step Functions task token for `SendTaskSuccess`). A thin Streamlit UI lives in
`reviewer/app.py`; this module is the logic it calls and what the tests assert.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..auth import AuthError, roles_from_claims, verify_jwt
from ..mcp_gateway import approvals as _approvals
from ..mcp_gateway import policy as _policy


@dataclass
class PendingAction:
    id: str
    agent_id: str
    requester_sub: str
    tool: str
    args: Dict[str, Any]
    summary: str
    created_at: float = field(default_factory=lambda: time.time())
    consequential: bool = True

    def detail(self) -> Dict[str, Any]:
        """Exactly what the reviewer is shown before deciding."""
        return {
            "id": self.id, "agent_id": self.agent_id, "requested_by": self.requester_sub,
            "tool": self.tool, "arguments": self.args, "summary": self.summary,
            "args_sha256": _approvals.canonical_args_hash(self.args),
            "separation_of_duties_required": self.tool in _policy.SEPARATION_REQUIRED_TOOLS,
        }


@dataclass
class ReviewDecision:
    approved: bool
    reason: str
    approval: Optional[Dict[str, Any]] = None  # the signed, bound approval (if approved)
    reviewer_sub: str = ""


class ReviewService:
    def __init__(self, audit_sink=None) -> None:
        self._queue: Dict[str, PendingAction] = {}
        self._audit: List[Dict[str, Any]] = []
        self._audit_sink = audit_sink  # production: append-only DynamoDB writer

    # ── queue ──────────────────────────────────────────────────────────────────
    def enqueue(self, *, agent_id: str, requester_sub: str, tool: str,
                args: Dict[str, Any], summary: str) -> PendingAction:
        item = PendingAction(id=f"REV-{uuid.uuid4().hex[:10]}", agent_id=agent_id,
                             requester_sub=requester_sub, tool=tool, args=args, summary=summary)
        self._queue[item.id] = item
        self._record({"event": "enqueued", "item": item.id, "tool": tool,
                      "requested_by": requester_sub})
        return item

    def list_pending(self, reviewer_claims: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Only items this reviewer is entitled to approve are visible to them."""
        ent = _policy.user_entitlements(roles_from_claims(reviewer_claims))
        return [it.detail() for it in self._queue.values() if it.tool in ent]

    def action_detail(self, item_id: str) -> Dict[str, Any]:
        if item_id not in self._queue:
            raise KeyError(item_id)
        return self._queue[item_id].detail()

    # ── decision ───────────────────────────────────────────────────────────────
    def decide(self, reviewer_token_or_claims: Any, item_id: str, *,
               approve: bool = True, meaning: str = "Approved consequential action",
               ttl_seconds: Optional[int] = None) -> ReviewDecision:
        item = self._queue.get(item_id)
        if item is None:
            return ReviewDecision(False, f"unknown item {item_id!r}")

        # 1. authenticate the reviewer (fail closed)
        try:
            claims = verify_jwt(reviewer_token_or_claims)
        except AuthError as exc:
            return self._reject(item, "", f"reviewer not authenticated: {exc}")
        reviewer_sub = claims.get("sub", "")

        if not approve:
            return self._reject(item, reviewer_sub, "reviewer declined", pop=True)

        # 2. entitlement: you may only approve what you could perform
        ent = _policy.user_entitlements(roles_from_claims(claims))
        if item.tool not in ent:
            return self._reject(item, reviewer_sub,
                                f"reviewer not entitled to approve {item.tool!r}")

        # 3. separation of duties for the highest-risk commits
        if item.tool in _policy.SEPARATION_REQUIRED_TOOLS and reviewer_sub == item.requester_sub:
            return self._reject(item, reviewer_sub,
                                "separation of duties: requester may not approve their own commit")

        # 4. sign a transaction-bound, single-use, expiring approval
        reviewer = {"sub": reviewer_sub,
                    "name": claims.get("name") or claims.get("email") or reviewer_sub,
                    "roles": roles_from_claims(claims)}
        approval = _approvals.sign_approval(
            reviewer=reviewer, agent_id=item.agent_id, subject=item.requester_sub,
            tool=item.tool, args=item.args, decision="approved", meaning=meaning,
            ttl_seconds=ttl_seconds,
        )
        self._queue.pop(item_id, None)  # one decision per item
        self._record({"event": "approved", "item": item.id, "tool": item.tool,
                      "reviewer": reviewer_sub, "requested_by": item.requester_sub,
                      "nonce": approval["binding"]["nonce"]})
        return ReviewDecision(True, "approved", approval=approval, reviewer_sub=reviewer_sub)

    # ── helpers ─────────────────────────────────────────────────────────────────
    def _reject(self, item: PendingAction, reviewer_sub: str, reason: str,
                pop: bool = False) -> ReviewDecision:
        if pop:
            self._queue.pop(item.id, None)
        self._record({"event": "rejected", "item": item.id, "tool": item.tool,
                      "reviewer": reviewer_sub, "reason": reason})
        return ReviewDecision(False, reason, reviewer_sub=reviewer_sub)

    def _record(self, entry: Dict[str, Any]) -> None:
        entry = {"ts": time.time(), **entry}
        self._audit.append(entry)
        if self._audit_sink is not None:  # pragma: no cover - production sink
            try:
                self._audit_sink(entry)
            except Exception:
                pass

    @property
    def audit(self) -> List[Dict[str, Any]]:
        return list(self._audit)
