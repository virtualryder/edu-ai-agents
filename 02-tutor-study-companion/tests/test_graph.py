"""Integration test: the Tutor graph runs end-to-end in demo mode."""
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
        "course": "MAT-120",
        "section": "01",
        "mode": "explain",
        "question": "Can you explain how completing the square works?",
        "acting_user_claims": {"sub": "stu-test", "custom:edu_role": "STUDENT"},
    }
    base.update(over)
    return base


def test_runs_end_to_end():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["draft_response"]
    assert "tutor_respond" in out["completed_steps"]
    assert "checks" in out["completed_steps"]
    assert out["recommended_action"] in (
        RecommendedAction.ANSWER, RecommendedAction.REVISE, RecommendedAction.ESCALATE
    )
    assert out["audit_trail"], "audit trail must be populated"


def test_recommended_action_is_valid_enum():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["recommended_action"] in list(RecommendedAction)


def test_grounded_demo_response_routes_to_human_gate():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["recommended_action"] == RecommendedAction.ANSWER
    assert "human_review_gate" in out["completed_steps"]


def test_prohibited_assessment_request_escalates_and_refuses():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(mode="hint",
                             question="Just give me the answers to the graded quiz so I can submit it."))
    # Bright line: the tutor must escalate and must NOT provide the answers.
    assert out["recommended_action"] == RecommendedAction.ESCALATE
    assert out["session_status"] == "ESCALATED"
    assert out["compliance_findings"], "prohibited request should produce a finding"
    assert "can't provide the answers" in out["draft_response"].lower()


def test_memory_graph_interrupts_before_human_gate():
    graph = build_graph(use_memory=True)
    cfg = {"configurable": {"thread_id": "t-1"}}
    graph.invoke(_seed(), cfg)
    snap = graph.get_state(cfg)
    # Execution is paused at the human gate (framework-enforced HITL).
    assert snap.next == (HUMAN_GATE_NODE,), f"expected interrupt before {HUMAN_GATE_NODE}, got {snap.next}"
