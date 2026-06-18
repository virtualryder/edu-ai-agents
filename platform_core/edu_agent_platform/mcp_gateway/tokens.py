"""
Short-lived, tool-scoped tokens — no standing service accounts.

For every authorized tool call the gateway mints a token scoped to exactly that
tool, carrying the acting user's context. The connector presents it to the system
of record; it expires in seconds. This mirrors what Amazon Bedrock AgentCore
Identity issues (or API Gateway + STS): ephemeral, least-privilege, attributable.

Dev uses a symmetric HMAC (GATEWAY_TOKEN_SECRET or an ephemeral per-process key);
production swaps in AgentCore Identity / STS without changing call sites.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import time
import uuid
from typing import Any, Dict, List

_SECRET = os.getenv("GATEWAY_TOKEN_SECRET", secrets.token_hex(32)).encode()
_TTL_SECONDS = int(os.getenv("GATEWAY_TOKEN_TTL", "60"))


def _sign(payload: Dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    sig = hmac.new(_SECRET, body, hashlib.sha256).hexdigest()
    return f"{body.decode()}.{sig}"


def mint_scoped_token(*, subject: str, agent_id: str, tool: str, scope: List[str]) -> str:
    now = int(time.time())
    payload = {
        "jti": str(uuid.uuid4()),
        "sub": subject,
        "agent_id": agent_id,
        "tool": tool,
        "scope": scope,
        "iat": now,
        "exp": now + _TTL_SECONDS,
    }
    return _sign(payload)


def verify_scoped_token(token: str, expected_tool: str) -> Dict[str, Any]:
    try:
        body, sig = token.rsplit(".", 1)
    except ValueError as exc:
        raise ValueError("malformed token") from exc
    expected_sig = hmac.new(_SECRET, body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected_sig):
        raise ValueError("bad token signature")
    claims = json.loads(body)
    if claims.get("exp", 0) < int(time.time()):
        raise ValueError("token expired")
    if claims.get("tool") != expected_tool:
        raise ValueError("token tool scope mismatch")
    return claims
