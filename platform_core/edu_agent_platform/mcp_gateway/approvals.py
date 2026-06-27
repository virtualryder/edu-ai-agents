"""
Transaction-bound, single-use human approvals for consequential tool calls.

The simple "approved + reviewer.sub" record is enough for a local demo, but a
PRODUCTION human gate must guarantee that an approval authorizes EXACTLY ONE
specific transaction and cannot be replayed or retargeted. An approval to send
one family message must not be reusable to send a different message, to another
student, by another agent.

`sign_approval()` binds a verified reviewer's decision to the precise
(agent, acting user, tool, canonical args) tuple with a one-time nonce and a
short expiry, signed with an approval secret. `verify_approval()` re-derives the
binding from the ACTUAL call and rejects anything whose agent/user/tool/args
don't match, that has expired, that isn't signed, or whose nonce was already
used. This is the reference for what AWS issues as a signed AgentCore Identity
approval or a signed Step Functions task token.

The nonce store here is in-process. Production binds single-use to a durable
store (a DynamoDB conditional `PutItem` with `attribute_not_exists`) so an
approval cannot be replayed across workers — see
docs/PRODUCTION-READINESS-ACTION-PLAN.md.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any, Dict, Optional, Set, Tuple

# Reuse the gateway token secret if a dedicated approval secret isn't set. In
# production this is an asymmetric KMS/AgentCore-issued key; here it is a single
# HMAC secret so the binding is testable without AWS.
_SECRET = os.getenv(
    "APPROVAL_SIGNING_SECRET", os.getenv("GATEWAY_TOKEN_SECRET", secrets.token_hex(32))
).encode()
_TTL_SECONDS = int(os.getenv("APPROVAL_TTL_SECONDS", "900"))


def _demo_mode() -> bool:
    """True in local/dev/test; production is the secure default (no demo flag set)."""
    if str(os.getenv("AUTH_ALLOW_UNVERIFIED_CLAIMS", "")).strip().lower() in ("1", "true", "yes"):
        return True
    if str(os.getenv("EXTRACT_MODE", "")).strip().lower() == "demo":
        return True
    if str(os.getenv("CONNECTOR_MODE", "")).strip().lower() in ("fixture", "demo"):
        return True
    return False


def canonical_args_hash(args: Optional[Dict[str, Any]]) -> str:
    body = json.dumps(args or {}, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(body).hexdigest()


def _binding_bytes(agent_id: str, subject: str, tool: str, args_hash: str, nonce: str, exp: int) -> bytes:
    return json.dumps(
        {"agent_id": agent_id, "sub": subject, "tool": tool,
         "args_sha256": args_hash, "nonce": nonce, "exp": exp},
        sort_keys=True, separators=(",", ":"),
    ).encode()


def _sign(agent_id: str, subject: str, tool: str, args_hash: str, nonce: str, exp: int) -> str:
    return hmac.new(_SECRET, _binding_bytes(agent_id, subject, tool, args_hash, nonce, exp),
                    hashlib.sha256).hexdigest()


def sign_approval(
    *, reviewer: Dict[str, Any], agent_id: str, subject: str, tool: str,
    args: Optional[Dict[str, Any]] = None, decision: str = "approved",
    meaning: str = "", ttl_seconds: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Produce a signed, transaction-bound, single-use approval record. Called by the
    reviewer experience after a named human approves THIS specific action.
    `reviewer` must carry a verified `sub` (see auth.record_reviewer_identity).
    """
    if not (reviewer or {}).get("sub"):
        raise ValueError("reviewer must carry a verified 'sub'")
    exp = int(time.time()) + int(ttl_seconds or _TTL_SECONDS)
    nonce = secrets.token_hex(16)
    args_hash = canonical_args_hash(args)
    approved = str(decision).strip().lower() in (
        "approve", "approved", "sign", "signed", "authorize", "authorized"
    )
    return {
        "approved": approved,
        "reviewer": reviewer,
        "decision": decision,
        "signature_meaning": meaning,
        "binding": {"agent_id": agent_id, "sub": subject, "tool": tool,
                    "args_sha256": args_hash, "nonce": nonce, "exp": exp},
        "signature": _sign(agent_id, subject, tool, args_hash, nonce, exp),
    }


def verify_approval(
    approval: Optional[Dict[str, Any]], *, agent_id: str, subject: str, tool: str,
    args: Optional[Dict[str, Any]] = None, seen_nonces: Optional[Set[str]] = None,
) -> Tuple[bool, str]:
    """
    Verify a signed approval against the ACTUAL transaction. Returns (ok, reason).
    Rejects: not approved, missing reviewer, unsigned, bad signature, mismatched
    agent/user/tool/args, expired, or replayed nonce.
    """
    if not approval:
        return False, "no approval"
    if not approval.get("approved"):
        return False, "approval not granted"
    if not (approval.get("reviewer") or {}).get("sub"):
        return False, "approval missing verified reviewer"
    binding = approval.get("binding")
    signature = approval.get("signature")
    if not binding or not signature:
        return False, "approval is not transaction-bound (unsigned)"

    expected = _sign(
        binding.get("agent_id"), binding.get("sub"), binding.get("tool"),
        binding.get("args_sha256"), binding.get("nonce"), int(binding.get("exp", 0)),
    )
    if not hmac.compare_digest(str(signature), expected):
        return False, "approval signature invalid"
    if binding.get("agent_id") != agent_id:
        return False, "approval bound to a different agent"
    if binding.get("sub") != subject:
        return False, "approval bound to a different user"
    if binding.get("tool") != tool:
        return False, "approval bound to a different tool"
    if binding.get("args_sha256") != canonical_args_hash(args):
        return False, "approval bound to different arguments"
    if int(binding.get("exp", 0)) < int(time.time()):
        return False, "approval expired"

    nonce = binding.get("nonce")
    if seen_nonces is not None:
        if nonce in seen_nonces:
            return False, "approval already used (replay rejected)"
        seen_nonces.add(nonce)
    return True, "ok"
