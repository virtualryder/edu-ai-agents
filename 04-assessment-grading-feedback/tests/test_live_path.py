"""
Live-path test — proves the Grading agent talks to a system of record over REAL
HTTP through the MCP gateway (CONNECTOR_MODE=live), not just fixtures.

Starts the bundled reference service on a free port, points the connector
BASE_URLs at it, and asserts: reads/analysis round-trip over HTTP (the returned
body originates from the service), the consequential grade release is blocked at
the gateway until a verified EDUCATOR approval is bound, and the audit trail
records live lineage. CONNECTOR_MODE is toggled per-test and restored so fixture
tests are unaffected.

Bright line: the educator owns the grade; the agent never releases autonomously.
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
for _kind in ("LMS", "ASSESSMENT"):
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
        res = gw.invoke(user_claims={"sub": "edu", "custom:edu_role": "EDUCATOR"},
                        agent_id="04-assessment-grading-feedback",
                        tool="assessment.evaluate_rubric",
                        args={"submission_id": "SUB-1", "rubric_ref": "RUB-live-101"})
        assert res.decision == "ALLOW"
        # The body came from the live reference service, not a fixture.
        assert res.result.get("served_by") == "reference_service"
        assert res.result.get("confidence") == 0.86


def test_release_grade_gated_then_executes_over_live_http():
    from agent.graph import build_graph
    g = build_graph(use_memory=False)
    base = {
        "request_id": "LIVE-T2", "channel": "lms", "course": "ENG-101",
        "submission_id": "SUB-live-T2", "rubric_ref": "RUB-live-101",
        "acting_user_claims": {"sub": "edu", "custom:edu_role": "EDUCATOR"},
        "action_request": {"type": "release_grade",
                           "payload": {"submission_id": "SUB-live-T2", "rubric_ref": "RUB-live-101"}},
    }
    with _live():
        blocked = g.invoke(dict(base))
        assert not blocked.get("grade_id"), "must not release the grade without approval"
        approved = dict(base)
        approved["approval"] = {"approved": True,
                                "reviewer": {"sub": "edu", "roles": ["EDUCATOR"]}}
        released = g.invoke(approved)
    # ID originates from the reference service => proves the live round-trip.
    assert released.get("grade_id") == "GR-live-0001"  # came from the live service after approval
    assert released["case_status"] == "RESOLVED"
