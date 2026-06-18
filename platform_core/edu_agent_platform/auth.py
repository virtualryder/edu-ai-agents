"""
Authentication & reviewer identity — federated IdP claims for EDU roles.

The suite never manages its own user accounts. Identity federates from the
institution's IdP (Okta / Microsoft Entra / Google Workspace / Active Directory)
via Amazon Cognito or IAM Identity Center (or Amazon Bedrock AgentCore Identity),
and roles derive from IdP group membership:

    GRP-STUDENTS         -> STUDENT
    GRP-GUARDIANS        -> GUARDIAN          (scoped; dropped when rights transfer)
    GRP-EDUCATORS        -> EDUCATOR          (owns grade release)
    GRP-COUNSELORS       -> COUNSELOR         (owns interventions / outreach)
    GRP-REGISTRAR        -> REGISTRAR         (owns enrollment-record writes)
    GRP-FINANCIAL-AID    -> FINANCIAL_AID
    GRP-ENROLLMENT       -> ENROLLMENT_STAFF
    GRP-ADMIN            -> ADMINISTRATOR
    GRP-IT-STAFF         -> IT_STAFF
    GRP-IT-ADMIN         -> IT_ADMIN          (owns privileged remediation)
    GRP-STAFF            -> STAFF
    GRP-STAFF-APPROVERS  -> STAFF_APPROVER    (owns financial/procurement approval)

Two EDU-specific claims govern access beyond role:
    rights_transferred  true at age 18 / postsecondary enrollment — FERPA rights
                        move to the student; the GUARDIAN role is then dropped.
    under_13            true for COPPA-covered learners — drives heightened
                        Guardrails, data minimization, and prohibited non-
                        educational use (enforced in the model/Guardrail layer).

verify_jwt validates the token when PyJWT + a JWKS URL are configured; in dev it
accepts a pre-decoded claims dict so the demo runs without an IdP. require_role
enforces role membership at HITL approval steps, and record_reviewer_identity
binds a verified human identity into an approval record (the consequential-action
sign-off the gateway requires).
"""
from __future__ import annotations

import datetime as _dt
import logging
import os
from typing import Any, Dict, Iterable, List

logger = logging.getLogger(__name__)

ROLE_CLAIM = os.getenv("AUTH_ROLE_CLAIM", "custom:edu_role")


class AuthError(Exception):
    """Raised on authentication / authorization failure (fail-closed)."""


def _truthy(v: Any) -> bool:
    return str(v).strip().lower() in ("1", "true", "yes")


def roles_from_claims(claims: Dict[str, Any]) -> List[str]:
    raw = claims.get(ROLE_CLAIM) or claims.get("roles") or claims.get("cognito:groups") or []
    if isinstance(raw, str):
        roles = [r.strip() for r in raw.split(",") if r.strip()]
    elif isinstance(raw, (list, tuple)):
        roles = [str(r) for r in raw]
    else:
        roles = []
    # FERPA: at age of majority / postsecondary enrollment, rights transfer to the
    # student and the guardian no longer has access to the education record.
    if _truthy(claims.get("rights_transferred", "")):
        roles = [r for r in roles if r != "GUARDIAN"]
    return roles


def is_under_13(claims: Dict[str, Any]) -> bool:
    """COPPA flag — drives heightened content/data controls in the model layer."""
    return _truthy(claims.get("under_13", ""))


def verify_jwt(token_or_claims: Any) -> Dict[str, Any]:
    """
    Verify a bearer token and return its claims.

    Production: validates RS256 signature against AUTH_JWKS_URL with audience
    AUTH_AUDIENCE. Dev: if given a dict, treats it as already-verified claims so
    the local demo runs without an IdP. Fails closed (raises AuthError).
    """
    if isinstance(token_or_claims, dict):
        if not token_or_claims.get("sub"):
            raise AuthError("claims missing 'sub' (fail-closed)")
        return token_or_claims

    jwks_url = os.getenv("AUTH_JWKS_URL")
    if not jwks_url:
        raise AuthError("AUTH_JWKS_URL not configured; cannot verify token")
    try:  # pragma: no cover - requires network/IdP
        import jwt
        from jwt import PyJWKClient

        signing_key = PyJWKClient(jwks_url).get_signing_key_from_jwt(token_or_claims)
        claims = jwt.decode(
            token_or_claims,
            signing_key.key,
            algorithms=["RS256"],
            audience=os.getenv("AUTH_AUDIENCE"),
        )
        if not claims.get("sub"):
            raise AuthError("verified token missing 'sub'")
        return claims
    except AuthError:
        raise
    except Exception as exc:  # pragma: no cover
        raise AuthError(f"token verification failed: {exc}") from exc


def require_role(claims: Dict[str, Any], allowed: Iterable[str]) -> str:
    """Return the first matching role, or raise AuthError. Used at HITL gates."""
    user_roles = set(roles_from_claims(claims))
    allowed_set = set(allowed)
    match = user_roles & allowed_set
    if not match:
        raise AuthError(
            f"user roles {sorted(user_roles)} lack any required role {sorted(allowed_set)}"
        )
    return sorted(match)[0]


def record_reviewer_identity(claims: Dict[str, Any], decision: str, meaning: str) -> Dict[str, Any]:
    """
    Build a signed approval record bound to a verified human, for a consequential
    action (e.g., "Released final grade", "Authorized enrollment-record update",
    "Approved family outreach"). The record is attached to the audit trail and is
    what the gateway checks before executing a consequential tool.
    """
    sub = claims.get("sub")
    if not sub:
        raise AuthError("cannot record reviewer identity without verified subject")
    return {
        "reviewer": {
            "sub": sub,
            "name": claims.get("name") or claims.get("email") or sub,
            "roles": roles_from_claims(claims),
        },
        "decision": decision,
        "signature_meaning": meaning,
        "signed_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "approved": decision.lower() in ("approve", "approved", "sign", "signed", "authorize"),
    }
