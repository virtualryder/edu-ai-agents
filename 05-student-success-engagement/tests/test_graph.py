"""Integration test: the Student Success graph runs end-to-end in demo mode."""
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
        "channel": "sis",
        "student_ref": "STU-test",
        "trigger_event": "absences",
        "acting_user_claims": {"sub": "cnsl-test", "custom:edu_role": "COUNSELOR"},
    }
    base.update(over)
    return base


def test_runs_end_to_end():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["draft_plan"]
    assert "draft_intervention" in out["completed_steps"]
    assert "checks" in out["completed_steps"]
    assert out["recommended_action"] in (
        RecommendedAction.PROCEED, RecommendedAction.REVISE, RecommendedAction.ESCALATE
    )
    assert out["audit_trail"], "audit trail must be populated"


def test_clean_case_routes_to_human_gate():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["recommended_action"] == RecommendedAction.PROCEED
    assert "human_review_gate" in out["completed_steps"]


def test_low_risk_advising_case_executes_after_gate():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(action_request={"type": "create_advising_case",
                                             "payload": {"topic": "attendance check-in"}}))
    assert out.get("case_id"), "low-risk advising case should be created"
    assert out["case_status"] == "RESOLVED"


def test_consequential_send_without_approval_stays_pending():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(trigger_event="disengagement",
                             action_request={"type": "send_message",
                                             "payload": {"to": "student", "topic": "check-in"}}))
    # No approval bound -> the gateway does not execute the send; no message_id.
    assert not out.get("message_id"), "consequential send must not execute without approval"


def test_memory_graph_interrupts_before_human_gate():
    graph = build_graph(use_memory=True)
    cfg = {"configurable": {"thread_id": "t-1"}}
    graph.invoke(_seed(), cfg)
    snap = graph.get_state(cfg)
    # Execution is paused at the human gate (framework-enforced HITL).
    assert snap.next == (HUMAN_GATE_NODE,), f"expected interrupt before {HUMAN_GATE_NODE}, got {snap.next}"
