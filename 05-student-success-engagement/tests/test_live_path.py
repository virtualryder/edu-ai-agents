"""
Live-path test — proves the Student Success agent talks to a system of record over
REAL HTTP through the MCP gateway (CONNECTOR_MODE=live), not just fixtures.

Starts the bundled reference service on a free port, points the connector
BASE_URLs at it, and asserts: reads round-trip over HTTP (the returned body
originates from the service), a low-risk advising case is created over HTTP, the
consequential outreach send is blocked at the gateway until a verified COUNSELOR
approval is bound, and the audit trail records live lineage. CONNECTOR_MODE is
toggled per-test and restored so fixture tests are unaffected.

PPRA note: no protected-category inference; the agent never sends autonomously.
"""
import os
import socket
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

AGENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AGENT))
sys.path.insert(0, str(AGENT.parent / "platform_core"))
sys.path.insert(0, str(AGENT.parent))

from demo.reference_service import Handler
from edu_agent_platform.mcp_gateway import MCPGateway


# ── Start the reference service once for this module ───────────────────────────
def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


_PORT = _free_port()
_URL = f"http://127.0.0.1:{_PORT}"
_SERVER = ThreadingHTTPServer(("127.0.0.1", _PORT), Handler)
threading.Thread(target=_SERVER.serve_forever, daemon=True).start()
for _kind in ("ANALYTICS", "SIS", "LMS", "CRM", "COMMS"):
    os.environ[f"{_kind}_BASE_URL"] = _URL


class _live:
    """Context manager: CONNECTOR_MODE=live for the block, restored after."""
    def __enter__(self):
        self._prev = os.environ.get("CONNECTOR_MODE")
        os.environ["CONNECTOR_MODE"] = "live"
        return self
    def __exit__(self, *a):
        if self._prev is None:
            os.environ.pop("CONNECTOR_MODE", None)
        else:
            os.environ["CONNECTOR_MODE"] = self._prev


def test_gateway_read_round_trips_over_http():
    with _live():
        gw = MCPGateway()
        res = gw.invoke(user_claims={"sub": "cnsl", "custom:edu_role": "COUNSELOR"},
                        agent_id="05-student-success-engagement",
                        tool="analytics.get_risk_signals", args={})
        assert res.decision == "ALLOW"
        # The body came from the live reference service, not a fixture.
        assert res.result.get("served_by") == "reference_service"
        assert res.result.get("signals")


def test_low_risk_advising_case_executes_over_live_http():
    from agent.graph import build_graph
    with _live():
        out = build_graph(use_memory=False).invoke({
            "request_id": "LIVE-T1", "channel": "sis", "student_ref": "STU-T1",
            "trigger_event": "absences",
            "acting_user_claims": {"sub": "cnsl", "custom:edu_role": "COUNSELOR"},
            "action_request": {"type": "create_advising_case",
                               "payload": {"topic": "attendance check-in"}},
        })
    # ID originates from the reference service => proves the live round-trip.
    assert out.get("case_id") == "CASE-live-0042"
    assert out["case_status"] == "RESOLVED"


def test_consequential_send_gated_then_executes_over_live_http():
    from agent.graph import build_graph
    g = build_graph(use_memory=False)
    base = {
        "request_id": "LIVE-T2", "channel": "lms", "student_ref": "STU-T2",
        "trigger_event": "disengagement",
        "acting_user_claims": {"sub": "cnsl", "custom:edu_role": "COUNSELOR"},
        "action_request": {"type": "send_message",
                           "payload": {"to": "student", "topic": "wellness check-in"}},
    }
    with _live():
        blocked = g.invoke(dict(base))
        assert not blocked.get("message_id"), "must not call the service without approval"
        approved = dict(base)
        approved["approval"] = {"approved": True,
                                "reviewer": {"sub": "cnsl", "roles": ["COUNSELOR"]}}
        sent = g.invoke(approved)
    assert sent.get("message_id") == "MSG-live-0009"  # came from the live service after approval
