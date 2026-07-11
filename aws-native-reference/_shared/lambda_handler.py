"""
Native-path Lambda handler shim — `handler.lambda_handler`.

The native CloudFormation path (`infra/cloudformation/agent-service.yaml`) wires a
Step Functions state machine over four Lambda functions per agent
(core / policy_gate / hitl_enqueue / finalize), each `Handler: handler.lambda_handler`.
`scripts/package_lambdas.sh` packages THIS file as `handler.py` alongside the
agent's `agent/`, `tools/`, `data/` packages plus `edu_agent_platform/` and
`governance/`, so the import paths below resolve inside the Lambda zip.

This reference shim runs the agent's LangGraph workflow for a single stateless
invocation. In a fully-specialized native split, each of the four functions would
run only its segment of the graph; here the same entrypoint runs the governed
workflow end-to-end (authorization, grounding, and the HITL classification still
happen through the platform), which is correct and testable as a reference. The
Step Functions `waitForTaskToken` gate (in the state machine) is what suspends a
consequential action for human approval before `finalize` runs.

Event contract: the state-machine step passes the task state as the event; we
accept either the raw seed dict or `{"input": {...}}`. The acting user's verified
IdP claims must be present as `acting_user_claims` (the gateway fails closed
without a subject).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# The zip root holds handler.py + agent/ + tools/ + edu_agent_platform/ + governance/
sys.path.insert(0, str(Path(__file__).resolve().parent))

os.environ.setdefault("CONNECTOR_MODE", os.getenv("CONNECTOR_MODE", "fixture"))

_GRAPH = None


def _graph():
    global _GRAPH
    if _GRAPH is None:
        from agent.graph import build_graph  # packaged alongside this file

        _GRAPH = build_graph(use_memory=False)
    return _GRAPH


def lambda_handler(event, context=None):
    """Run the agent on the event payload; return a JSON-safe result."""
    payload = {}
    if isinstance(event, dict):
        payload = event.get("input", event)
    if not isinstance(payload, dict):
        payload = {}
    # Identity is taken from the VERIFIED API Gateway JWT authorizer context when present
    # (requestContext.authorizer.jwt.claims), never from the body. Without an authorizer
    # context we fall back to verify_jwt, which accepts a claims dict ONLY in demo mode and
    # otherwise fails closed — so a seeded/forged acting_user_claims cannot be trusted in prod.
    from edu_agent_platform.auth import AuthError, verify_jwt  # noqa: E402

    try:
        authz = {}
        if isinstance(event, dict):
            authz = (event.get("requestContext") or {}).get("authorizer") or {}
        verified = authz["jwt"].get("claims") if isinstance(authz.get("jwt"), dict) else None
        if verified is not None:
            payload = {**payload, "acting_user_claims": verified}  # already verified by API GW
        else:
            payload = {**payload, "acting_user_claims": verify_jwt(payload.get("acting_user_claims") or {})}
    except AuthError as exc:
        return {"ok": False, "error": "unauthorized", "detail": str(exc)}
    try:
        result = _graph().invoke(payload)
        return json.loads(json.dumps(result, default=str))
    except Exception as exc:  # fail closed with a clear, loggable error
        return {"ok": False, "error": type(exc).__name__, "detail": str(exc)}
