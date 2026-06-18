"""
Local reference service — a stand-in for the institution's real systems of record.

The live path proves the Assessment, Grading & Feedback agent talks to systems of
record over real HTTP without requiring a live Canvas / Banner / assessment engine
during a demo. This stdlib HTTP server implements the endpoints the agent's
connectors call (LMS + assessment engine), returning the SAME shapes the fixtures
use, so agent code is identical whether it points here or at a customer gateway.

The MCP gateway has ALREADY authorized the call and minted a short-lived scoped
token before the connector reaches this service. In production you point each
connector's <KIND>_BASE_URL at the customer's API gateway instead of this service;
nothing in the agent changes. Optionally require a bearer token via
REFERENCE_API_TOKEN to mirror an authenticated endpoint.

Bright line: the educator owns the grade. The agent EVALUATES against the rubric
and drafts feedback; releasing a final grade is a consequential action the gateway
human-gates BEFORE any HTTP call. This service never decides a grade — it only
returns the same shapes a real LMS/assessment system would.

Routing: POST /<method> with a JSON body of the tool args. The LiveHTTPConnector
posts to "<KIND>_BASE_URL>/<method>"; method names are unique across kinds, so a
single service can stand in for LMS + assessment at once.

Run standalone:
    python demo/reference_service.py            # listens on :8901
    REFERENCE_PORT=9001 python demo/reference_service.py
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict

PORT = int(os.getenv("REFERENCE_PORT", "8901"))
TOKEN = os.getenv("REFERENCE_API_TOKEN", "")  # if set, require Authorization: Bearer <token>

# Synthetic responses keyed by method name (mirror connectors/fixtures.py shapes),
# but with distinct "live" ids so a test can PROVE the call went over HTTP rather
# than to a fixture.
RESPONSES: Dict[str, Dict[str, Any]] = {
    # LMS
    "get_assignments": {
        "course": "ENG-101",
        "assignments": [{"id": "A5", "title": "Persuasive Essay", "due": "2026-10-02", "points": 20}],
    },
    # Assessment engine
    # Confidence high (~0.86) so the normal path is APPROVE_DRAFT, not ESCALATE.
    "evaluate_rubric": {
        "rubric_id": "RUB-live-101", "criteria_scores": [3, 4, 3, 2], "max_per_criterion": 4,
        "raw_total": 12, "max_total": 16, "confidence": 0.86,
    },
    "draft_feedback": {
        "feedback_id": "FB-live-DRAFT-0001", "status": "DRAFT",
        "summary": "Strong thesis; support the third claim with evidence from the text.",
    },
    "summarize_class_patterns": {
        "course": "ENG-101", "common_misconception": "thesis stated but not defended",
        "suggested_reteach_group": 5,
    },
    # Consequential: releasing a final grade — the educator owns this decision; the
    # agent never releases autonomously. Reached only after the gateway human gate.
    "release_grade": {"grade_id": "GR-live-0001", "status": "RELEASED", "released": True},
}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: dict) -> None:
        payload = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.rstrip("/") == "/health":
            self._send(200, {"status": "healthy"})
        else:
            self._send(404, {"error": "use POST /<method>"})

    def do_POST(self) -> None:  # noqa: N802
        if TOKEN and self.headers.get("Authorization", "") != f"Bearer {TOKEN}":
            self._send(401, {"error": "unauthorized"})
            return
        method = self.path.strip("/").split("/")[-1]
        length = int(self.headers.get("Content-Length", "0"))
        try:
            args = json.loads(self.rfile.read(length) or b"{}") if length else {}
        except json.JSONDecodeError:
            args = {}
        if method not in RESPONSES:
            self._send(404, {"error": f"unknown method {method!r}"})
            return
        result = dict(RESPONSES[method])
        result["echo"] = args
        result["served_by"] = "reference_service"
        self._send(200, result)

    def log_message(self, *args) -> None:  # quiet
        return


def main() -> None:
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"reference_service listening on :{PORT} (auth={'on' if TOKEN else 'off'})")
    server.serve_forever()


if __name__ == "__main__":
    main()
