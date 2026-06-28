"""Integration test: the Concierge graph runs end-to-end in demo mode."""
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
        "channel": "web",
        "intent": "STATUS",
        "authenticated": True,
        "question": "What's my application status and what do I still need?",
        "acting_user_claims": {"sub": "stu-test", "custom:edu_role": "STUDENT"},
    }
    base.update(over)
    return base


def test_runs_end_to_end():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["draft_response"]
    assert "draft_response" in out["completed_steps"]
    assert "checks" in out["completed_steps"]
    assert out["recommended_action"] in (
        RecommendedAction.ANSWER, RecommendedAction.REVISE, RecommendedAction.ESCALATE
    )
    assert out["audit_trail"], "audit trail must be populated"


def test_grounded_demo_answer_skips_gate_for_read_only():
    """Clean read-only answers go straight to finalize — no over-gating."""
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["recommended_action"] == RecommendedAction.ANSWER
    assert "human_review_gate" not in out["completed_steps"]
    assert "finalize" in out["completed_steps"]


def test_consequential_action_routes_to_human_gate():
    """Consequential outbound actions (e.g. send_message) must pass through the gate."""
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(intent="ACTION",
                             action_request={"type": "send_message",
                                             "payload": {"to": "guardian", "topic": "status"}}))
    assert "human_review_gate" in out["completed_steps"]


def test_low_risk_action_executes_after_gate():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(action_request={"type": "create_advising_case",
                                             "payload": {"topic": "documents"}}))
    assert out.get("case_id"), "low-risk advising case should be created"
    assert out["case_status"] == "RESOLVED"


def test_consequential_send_without_approval_stays_pending():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(intent="ACTION",
                             action_request={"type": "send_message",
                                             "payload": {"to": "guardian", "topic": "next steps"}}))
    # No approval bound -> the gateway does not execute the send; no message_id.
    assert not out.get("message_id"), "consequential send must not execute without approval"


def test_memory_graph_interrupts_before_human_gate():
    """When a consequential action triggers the gate, the memory graph pauses there."""
    graph = build_graph(use_memory=True)
    cfg = {"configurable": {"thread_id": "t-1"}}
    graph.invoke(_seed(intent="ACTION",
                       action_request={"type": "send_message",
                                       "payload": {"to": "guardian", "topic": "status"}}), cfg)
    snap = graph.get_state(cfg)
    # Execution is paused at the human gate (framework-enforced HITL).
    assert snap.next == (HUMAN_GATE_NODE,), f"expected interrupt before {HUMAN_GATE_NODE}, got {snap.next}"
