"""
AgentCore Runtime container contract — generic HTTP server for any EDU agent.

Amazon Bedrock AgentCore Runtime invokes a container over HTTP with a fixed
contract:

    POST /invocations   -> run the agent on a JSON payload, return JSON
    GET  /ping          -> liveness/health (200 "healthy")
    port 8080, ARM64 image, non-root

This wrapper makes any agent in the suite satisfy that contract with no agent
code changes. It selects the agent by the AGENT_DIR env var (the agent folder),
imports its `agent.graph.build_graph`, and runs the graph WITHOUT memory for a
single stateless invocation (the HITL interrupt is exercised via the stateful
Step Functions / `waitForTaskToken` path in production; a stateless invoke runs
the read/draft path and returns the proposed action for a human to approve).

Dependency-light on purpose (stdlib http.server) so the image stays small and the
contract is obvious. Swap in FastAPI/uvicorn if you prefer; the contract is the
same. Demo mode (EXTRACT_MODE=demo, CONNECTOR_MODE=fixture) runs with no API key.
"""
from __future__ import annotations

import json
import logging
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("agentcore_server")

AGENT_DIR = os.getenv("AGENT_DIR", "/app")
PORT = int(os.getenv("PORT", "8080"))


def _load_graph():
    agent_path = Path(AGENT_DIR).resolve()
    sys.path.insert(0, str(agent_path))
    sys.path.insert(0, str(agent_path.parent / "platform_core"))
    sys.path.insert(0, str(agent_path.parent))
    from agent.graph import build_graph  # type: ignore

    return build_graph(use_memory=False)


_GRAPH = None


def _graph():
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = _load_graph()
    return _GRAPH


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") == "/ping":
            self._send(200, {"status": "healthy"})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path.rstrip("/") != "/invocations":
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length else b"{}"
            payload = json.loads(raw or b"{}")
            if not isinstance(payload, dict):
                payload = {}
            # Identity is derived SERVER-SIDE from a verified bearer token — never
            # trusted from the request body. verify_jwt validates an RS256/JWKS token in
            # production; in demo mode (no IdP) it accepts a claims dict. It fails closed
            # (AuthError) otherwise, so a caller cannot self-assert privileged claims.
            from edu_agent_platform.auth import AuthError, verify_jwt  # noqa: E402

            auth_header = self.headers.get("Authorization", "") or ""
            bearer = auth_header[7:].strip() if auth_header[:7].lower() == "bearer " else None
            try:
                claims = verify_jwt(bearer if bearer else (payload.get("acting_user_claims") or {}))
            except AuthError as exc:
                self._send(401, {"ok": False, "error": "unauthorized", "detail": str(exc)})
                return
            payload["acting_user_claims"] = claims  # authoritative; overrides any body value
            result = _graph().invoke(payload)
            # Return a JSON-safe projection (drop non-serializable objects).
            safe = json.loads(json.dumps(result, default=str))
            self._send(200, {"ok": True, "result": safe})
        except Exception as exc:  # fail closed with a clear error
            logger.exception("invocation failed")
            self._send(500, {"ok": False, "error": type(exc).__name__, "detail": str(exc)})

    def log_message(self, *args) -> None:  # quiet default logging
        return


def main() -> None:
    _graph()  # eager-load so /ping reflects readiness
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    logger.info("AgentCore server listening on :%d for AGENT_DIR=%s", PORT, AGENT_DIR)
    server.serve_forever()


if __name__ == "__main__":
    main()
