"""
Local reference service — a stand-in for the institution's real systems of record.

The live path proves the agent talks to systems of record over real HTTP without
requiring a live PowerSchool / Banner / Slate / Amazon Connect during a demo.
This stdlib HTTP server implements the endpoints the Concierge's connectors call,
returning the SAME shapes the fixtures use, so agent code is identical whether it
points here or at a customer gateway.

The MCP gateway has ALREADY authorized the call and minted a short-lived scoped
token before the connector reaches this service. In production you point each
connector's <KIND>_BASE_URL at the customer's API gateway instead of this service;
nothing in the agent changes. Optionally require a bearer token via
REFERENCE_API_TOKEN to mirror an authenticated endpoint.

Routing: POST /<method> with a JSON body of the tool args. The LiveHTTPConnector
posts to "<KIND>_BASE_URL>/<method>"; method names are unique across kinds, so a
single service can stand in for SIS + CRM + KB + comms at once.

Run standalone:
    python demo/reference_service.py            # listens on :8900
    REFERENCE_PORT=9000 python demo/reference_service.py
"""
from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict

PORT = int(os.getenv("REFERENCE_PORT", "8900"))
TOKEN = os.getenv("REFERENCE_API_TOKEN", "")  # if set, require Authorization: Bearer <token>

# Synthetic responses keyed by method name (mirror connectors/fixtures.py shapes).
RESPONSES: Dict[str, Dict[str, Any]] = {
    # SIS
    "get_student_profile": {"student_pseudonym": "STU-live0001", "level": "undergraduate",
                            "program": "AA Liberal Arts", "standing": "good", "credits_earned": 42},
    "get_schedule": {"term": "Fall 2026", "courses": [
        {"course": "ENG-101", "title": "Composition I", "days": "MWF", "time": "09:00"},
        {"course": "MAT-120", "title": "College Algebra", "days": "TR", "time": "11:00"}]},
    "check_application_status": {"application_pseudonym": "APP-live0001", "status": "documents_incomplete",
                                "missing": ["official transcript", "residency verification"],
                                "explanation": "Two items are still needed before a decision can be made."},
    # CRM
    "get_case": {"case_id": "CASE-live-0001", "type": "advising", "status": "open"},
    "create_advising_case": {"case_id": "CASE-live-0007", "status": "OPEN", "created": True},
    "schedule_appointment": {"appointment_id": "APPT-live-0003", "status": "BOOKED",
                             "with": "advising", "slot": "Tue 2:30pm"},
    # Knowledge base
    "search_policies": {"results": [
        {"title": "Registration & Add/Drop Policy", "ref": "POL-REG-002", "relevance": 0.93},
        {"title": "Financial Aid Satisfactory Academic Progress", "ref": "POL-FA-007", "relevance": 0.89}]},
    # Communications
    "draft_message": {"draft_id": "MSG-live-DRAFT-0001", "status": "DRAFT", "channel": "email"},
    "send_message": {"message_id": "MSG-live-0001", "status": "SENT", "channel": "email"},
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
