"""
Canvas / LMS LTI 1.3 launch reference — map an LTI launch to gateway identity.

This is the Layer-1 (Experience) bridge for the LMS-surfaced agents (02 Tutor,
03 Educator Copilot, and any panel embedded in Canvas / Blackboard / Schoology /
Moodle / D2L). It shows how an institution-approved **LTI 1.3 / LTI Advantage**
launch becomes the verified identity the MCP gateway authorizes against — so the
agent inherits exactly the launching user's role, and never more.

Flow (LTI 1.3, OIDC third-party-initiated login):
  1. OIDC login init: the LMS hits your /login with iss, login_hint, target_link_uri.
     You redirect to the platform auth endpoint with state + nonce.
  2. Launch: the LMS POSTs an id_token (a signed JWT) to your /launch. You MUST
     validate it: signature against the platform JWKS, iss/aud, exp/iat, and that
     the nonce matches the one you issued (replay protection).
  3. Map claims -> gateway identity: roles, sub, context, and (for K-12) age
     signals become `acting_user_claims` with `custom:edu_role`.
  4. Invoke the agent through the SAME governed path as every other surface; the
     gateway enforces deny-by-default authorization + the human-approval gate.

This module ships the deterministic, testable part (role mapping + claim
construction) plus a reference HTTP handler. JWT validation is wired but, for a
local dev launch with no platform keys, set LTI_DEV=1 to decode the id_token
WITHOUT signature verification — NEVER do that in production.

Dependencies for production validation: PyJWT[crypto]. Dev mode needs nothing.
"""
from __future__ import annotations

import base64
import json
import os
from typing import Any, Dict, List

# ── LTI 1.3 role URIs -> EDU gateway roles ────────────────────────────────────
# https://www.imsglobal.org/spec/lti/v1p3 — context + institution role vocab.
_ROLE_URI_MAP = {
    # Context roles (within a course)
    "http://purl.imsglobal.org/vocab/lis/v2/membership#Instructor": "EDUCATOR",
    "http://purl.imsglobal.org/vocab/lis/v2/membership#TeachingAssistant": "EDUCATOR",
    "http://purl.imsglobal.org/vocab/lis/v2/membership#ContentDeveloper": "EDUCATOR",
    "http://purl.imsglobal.org/vocab/lis/v2/membership#Learner": "STUDENT",
    "http://purl.imsglobal.org/vocab/lis/v2/membership#Mentor": "GUARDIAN",
    # Institution roles
    "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Student": "STUDENT",
    "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Faculty": "EDUCATOR",
    "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Staff": "STAFF",
    "http://purl.imsglobal.org/vocab/lis/v2/institution/person#Administrator": "ADMINISTRATOR",
    "http://purl.imsglobal.org/vocab/lis/v2/system/person#Administrator": "ADMINISTRATOR",
    # Short forms some platforms still send
    "Instructor": "EDUCATOR",
    "Learner": "STUDENT",
    "Student": "STUDENT",
    "Mentor": "GUARDIAN",
    "Administrator": "ADMINISTRATOR",
}

# Most-privileged-wins ordering when a launch carries multiple roles.
_ROLE_PRECEDENCE = ["ADMINISTRATOR", "EDUCATOR", "STAFF", "COUNSELOR", "GUARDIAN", "STUDENT"]

_ROLES_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/roles"
_CONTEXT_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/context"
_CUSTOM_CLAIM = "https://purl.imsglobal.org/spec/lti/claim/custom"


def map_lti_roles(role_uris: List[str]) -> List[str]:
    """Map LTI role URIs to EDU gateway roles, de-duplicated, precedence-ordered."""
    mapped = {_ROLE_URI_MAP[u] for u in role_uris if u in _ROLE_URI_MAP}
    return [r for r in _ROLE_PRECEDENCE if r in mapped]


def claims_from_launch(id_token_claims: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the gateway `acting_user_claims` from a validated LTI 1.3 id_token.

    Produces: sub, custom:edu_role (comma-joined, precedence-ordered), name,
    email, lti_context (course), and EDU age signals (under_13, rights_transferred)
    when the platform sends them as LTI custom claims — so FERPA rights-transfer
    and COPPA handling carry through from the LMS launch.
    """
    roles = map_lti_roles(id_token_claims.get(_ROLES_CLAIM, []) or [])
    if not roles:
        roles = ["STUDENT"]  # safest default; least privilege
    custom = id_token_claims.get(_CUSTOM_CLAIM, {}) or {}
    ctx = id_token_claims.get(_CONTEXT_CLAIM, {}) or {}
    claims: Dict[str, Any] = {
        "sub": id_token_claims.get("sub"),
        "custom:edu_role": ",".join(roles),
        "name": id_token_claims.get("name") or id_token_claims.get("email") or id_token_claims.get("sub"),
        "email": id_token_claims.get("email"),
        "lti_context": {"id": ctx.get("id"), "label": ctx.get("label"), "title": ctx.get("title")},
    }
    # EDU age signals (institution-provided LTI custom variables).
    if str(custom.get("under_13", "")).strip().lower() in ("1", "true", "yes"):
        claims["under_13"] = True
    if str(custom.get("rights_transferred", "")).strip().lower() in ("1", "true", "yes"):
        claims["rights_transferred"] = True
    return claims


# ── id_token handling ─────────────────────────────────────────────────────────
def _b64url_decode(seg: str) -> bytes:
    seg += "=" * (-len(seg) % 4)
    return base64.urlsafe_b64decode(seg.encode())


def decode_id_token(id_token: str, *, jwks_url: str = "", audience: str = "") -> Dict[str, Any]:
    """
    Return the validated claims of an LTI id_token.

    Production: validates RS256 signature against the platform JWKS, plus aud/exp.
    Dev (LTI_DEV=1): decodes the payload WITHOUT verification so a local launch
    works with no platform keys. Never enable LTI_DEV in production.
    """
    if os.getenv("LTI_DEV", "").strip().lower() in ("1", "true", "yes"):
        payload = id_token.split(".")[1]
        return json.loads(_b64url_decode(payload))

    if not jwks_url:
        raise RuntimeError("LTI id_token validation requires a platform JWKS URL (or set LTI_DEV=1 for dev)")
    import jwt  # PyJWT[crypto]
    from jwt import PyJWKClient

    signing_key = PyJWKClient(jwks_url).get_signing_key_from_jwt(id_token)
    return jwt.decode(id_token, signing_key.key, algorithms=["RS256"], audience=audience)


def launch_to_agent(id_token: str, agent_id: str, payload: Dict[str, Any], *,
                    jwks_url: str = "", audience: str = "") -> Dict[str, Any]:
    """
    Reference end-to-end: validate an LTI launch and run the named agent with the
    launching user's identity, through the governed graph path. Returns the agent
    output. The agent's tools still pass through the MCP gateway, so authorization
    and the human gate apply exactly as for any other surface.
    """
    claims = claims_from_launch(decode_id_token(id_token, jwks_url=jwks_url, audience=audience))
    seed = dict(payload)
    seed["acting_user_claims"] = claims
    # Lazy import so this module is usable for role-mapping without the agent stack.
    import importlib
    import sys
    from pathlib import Path

    repo = Path(__file__).resolve().parents[3]
    agent_dir = repo / agent_id
    sys.path.insert(0, str(agent_dir))
    sys.path.insert(0, str(repo / "platform_core"))
    sys.path.insert(0, str(repo))
    for m in [m for m in list(sys.modules) if m == "agent" or m.startswith("agent.")]:
        del sys.modules[m]
    graph_mod = importlib.import_module("agent.graph")
    return graph_mod.build_graph(use_memory=False).invoke(seed)


# ── Reference HTTP handler (OIDC login init + launch) ─────────────────────────
def build_wsgi_app(agent_id: str = "03-educator-copilot"):
    """
    Minimal WSGI reference: GET /login (OIDC init) and POST /launch (id_token).
    Returned for illustration; production deployments front this with the
    institution's gateway and a real session/nonce store. Kept dependency-free.
    """
    import secrets as _secrets
    from urllib.parse import parse_qs

    _nonces: set = set()

    def app(environ, start_response):
        path = environ.get("PATH_INFO", "")
        method = environ.get("REQUEST_METHOD", "GET")
        if path == "/login" and method == "GET":
            nonce = _secrets.token_urlsafe(16)
            _nonces.add(nonce)
            body = json.dumps({"action": "redirect_to_platform_auth", "nonce": nonce,
                               "note": "set state, store nonce, redirect to the platform OIDC auth endpoint"}).encode()
            start_response("200 OK", [("Content-Type", "application/json")])
            return [body]
        if path == "/launch" and method == "POST":
            size = int(environ.get("CONTENT_LENGTH", "0") or 0)
            form = parse_qs(environ["wsgi.input"].read(size).decode())
            id_token = (form.get("id_token") or [""])[0]
            try:
                claims = claims_from_launch(decode_id_token(id_token))
                body = json.dumps({"ok": True, "acting_user_claims": claims, "agent_id": agent_id}).encode()
                start_response("200 OK", [("Content-Type", "application/json")])
                return [body]
            except Exception as exc:
                start_response("400 Bad Request", [("Content-Type", "application/json")])
                return [json.dumps({"ok": False, "error": str(exc)}).encode()]
        start_response("404 Not Found", [("Content-Type", "application/json")])
        return [b'{"error":"use GET /login or POST /launch"}']

    return app
