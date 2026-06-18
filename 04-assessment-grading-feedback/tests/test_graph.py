"""Integration test: the Grading graph runs end-to-end in demo mode."""
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
        "channel": "lms",
        "course": "ENG-101",
        "submission_id": "SUB-TEST",
        "rubric_ref": "RUB-101",
        "acting_user_claims": {"sub": "edu-test", "custom:edu_role": "EDUCATOR"},
    }
    base.update(over)
    return base


def test_runs_end_to_end():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["draft_feedback"]
    assert "draft_feedback" in out["completed_steps"]
    assert "checks" in out["completed_steps"]
    assert out["recommended_action"] in (
        RecommendedAction.APPROVE_DRAFT, RecommendedAction.REVISE, RecommendedAction.ESCALATE
    )
    assert out["audit_trail"], "audit trail must be populated"


def test_confident_eval_routes_to_human_gate():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["recommended_action"] == RecommendedAction.APPROVE_DRAFT
    assert "human_review_gate" in out["completed_steps"]


def test_low_confidence_escalates():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(confidence=0.42))
    assert out["recommended_action"] == RecommendedAction.ESCALATE
    assert out["case_status"] == "ESCALATED"


def test_release_grade_without_approval_stays_pending():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(action_request={"type": "release_grade",
                                             "payload": {"submission_id": "SUB-TEST",
                                                         "rubric_ref": "RUB-101"}}))
    # No approval bound -> the gateway does not release the grade; no grade_id.
    assert not out.get("grade_id"), "consequential grade release must not execute without approval"


def test_memory_graph_interrupts_before_human_gate():
    graph = build_graph(use_memory=True)
    cfg = {"configurable": {"thread_id": "t-1"}}
    graph.invoke(_seed(), cfg)
    snap = graph.get_state(cfg)
    # Execution is paused at the human gate (framework-enforced HITL).
    assert snap.next == (HUMAN_GATE_NODE,), f"expected interrupt before {HUMAN_GATE_NODE}, got {snap.next}"
