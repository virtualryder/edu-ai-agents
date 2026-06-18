"""
Local reference service — a stand-in for the institution's real systems of record.

The live path proves the Student Success & Engagement agent talks to systems of
record over real HTTP without requiring a live analytics lake / PowerSchool /
Canvas / Slate / Amazon Connect during a demo. This stdlib HTTP server implements
the endpoints the agent's connectors call (analytics + SIS + LMS + CRM + comms),
returning the SAME shapes the fixtures use, so agent code is identical whether it
points here or at a customer gateway.

The MCP gateway has ALREADY authorized the call and minted a short-lived scoped
token before the connector reaches this service. In production you point each
connector's <KIND>_BASE_URL at the customer's API gateway instead of this service;
nothing in the agent changes. Optionally require a bearer token via
REFERENCE_API_TOKEN to mirror an authenticated endpoint.

PPRA note: this service surfaces only authorized behavioral signals (attendance,
engagement, grades, risk composite). The agent does not infer or condition on
protected categories, and a consequential outreach send is human-gated by the
gateway BEFORE any HTTP call.

Routing: POST /<method> with a JSON body of the tool args. The LiveHTTPConnector
posts to "<KIND>_BASE_URL>/<method>"; method names are unique across kinds, so a
single service can stand in for analytics + SIS + LMS + CRM + comms at once.

Run standalone:
    python demo/reference_service.py            # listens on :8902
    REFERENCE_PORT=9002 python demo/reference_service.py
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict

PORT = int(os.getenv("REFERENCE_PORT", "8902"))
TOKEN = os.getenv("REFERENCE_API_TOKEN", "")  # if set, require Authorization: Bearer <token>

# Synthetic responses keyed by method name (mirror connectors/fixtures.py shapes),
# but with distinct "live" ids so a test can PROVE the call went over HTTP rather
# than to a fixture.
RESPONSES: Dict[str, Dict[str, Any]] = {
    # Analytics (student success) — authorized behavioral signals only.
    "get_risk_signals": {
        "signals": [
            {"type": "attendance", "value": "78%", "severity": "moderate"},
            {"type": "lms_engagement", "value": "6 days since login", "severity": "moderate"},
            {"type": "missing_work", "value": "1 assignment", "severity": "low"},
        ],
        "composite": "watch",
    },
    "get_intervention_history": {
        "prior": [{"date": "2026-09-15", "type": "advisor outreach", "outcome": "no response"}],
    },
    # SIS
    "get_attendance": {"term": "Fall 2026", "present_pct": 78.0, "absences": 9, "tardies": 3},
    "get_grades": {
        "term": "Fall 2026",
        "grades": [{"course": "ENG-101", "grade": "B"}, {"course": "MAT-120", "grade": "C-"}],
        "gpa": 2.6,
    },
    # LMS
    "get_engagement": {"course": "MAT-120", "last_login_days_ago": 6, "submissions_on_time_pct": 64.0},
    # CRM — opening an advising case is low-risk and runs directly (no approval gate).
    "create_advising_case": {"case_id": "CASE-live-0042", "status": "OPEN", "created": True},
    # Communications
    "draft_message": {"draft_id": "MSG-live-DRAFT-0001", "status": "DRAFT", "channel": "email"},
    # Consequential: an outbound student/family outreach — reached only after the
    # gateway human gate; the agent never sends autonomously.
    "send_message": {"message_id": "MSG-live-0009", "status": "SENT", "channel": "email"},
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
