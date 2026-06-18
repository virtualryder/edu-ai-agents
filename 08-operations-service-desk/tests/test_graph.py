"""Integration test: the Operations & Service Desk graph runs end-to-end in demo mode."""
import os
import sys
from pathlib import Path

AGENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AGENT))
sys.path.insert(0, str(AGENT.parent / "platform_core"))
sys.path.insert(0, str(AGENT.parent))
os.environ["EXTRACT_MODE"] = "demo"
os.environ["CONNECTOR_MODE"] = "fixture"

from agent.graph import HUMAN_GATE_NODE, build_graph
from agent.state import RecommendedAction


def _seed(**over):
    base = {
        "request_id": "REQ-TEST",
        "channel": "portal",
        "track": "it",
        "request": "A lab laptop keeps dropping the wifi and is slow.",
        "acting_user_claims": {"sub": "it-test", "custom:edu_role": "IT_ADMIN"},
    }
    base.update(over)
    return base


def test_runs_end_to_end():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["draft_resolution"]
    assert "retrieve" in out["completed_steps"]
    assert "draft_resolution" in out["completed_steps"]
    assert "checks" in out["completed_steps"]
    assert out["recommended_action"] in (
        RecommendedAction.ANSWER, RecommendedAction.REVISE, RecommendedAction.ESCALATE
    )
    assert out["audit_trail"], "audit trail must be populated"


def test_grounded_demo_resolution_routes_to_human_gate():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["recommended_action"] == RecommendedAction.ANSWER
    assert "human_review_gate" in out["completed_steps"]


def test_security_concern_escalates():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(request="We think an account was compromised in a phishing attack."))
    assert out["recommended_action"] == RecommendedAction.ESCALATE
    assert out["case_status"] == "ESCALATED"


def test_low_risk_ticket_executes_after_gate():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(action_request={"type": "create_ticket",
                                             "payload": {"category": "wifi"}}))
    assert out.get("ticket_id"), "low-risk ticket should be created"
    assert out["case_status"] == "RESOLVED"


def test_privileged_remediation_without_approval_stays_pending():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(request="A staff member is locked out and needs a reset.",
                             action_request={"type": "reset_password",
                                             "payload": {"account": "staff-7788"}}))
    # No approval bound -> the gateway does not execute the privileged remediation.
    assert not out.get("remediation_id"), "privileged remediation must not execute without approval"


def test_memory_graph_interrupts_before_human_gate():
    graph = build_graph(use_memory=True)
    cfg = {"configurable": {"thread_id": "t-1"}}
    graph.invoke(_seed(), cfg)
    snap = graph.get_state(cfg)
    # Execution is paused at the human gate (framework-enforced HITL).
    assert snap.next == (HUMAN_GATE_NODE,), f"expected interrupt before {HUMAN_GATE_NODE}, got {snap.next}"
