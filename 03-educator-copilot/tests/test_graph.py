"""Integration test: the Educator Copilot graph runs end-to-end in demo mode."""
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
        "artifact_type": "differentiation",
        "course": "MAT-120",
        "instructions": "Draft a differentiated lesson on quadratic functions for Unit 3.",
        "acting_user_claims": {"sub": "edu-test", "custom:edu_role": "EDUCATOR"},
    }
    base.update(over)
    return base


def test_runs_end_to_end():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["draft_artifact"]
    assert "draft_artifact" in out["completed_steps"]
    assert "checks" in out["completed_steps"]
    assert out["recommended_action"] in (
        RecommendedAction.APPROVE_DRAFT, RecommendedAction.REVISE, RecommendedAction.ESCALATE
    )
    assert out["audit_trail"], "audit trail must be populated"


def test_recommended_action_is_valid_enum():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["recommended_action"] in list(RecommendedAction)


def test_low_risk_draft_is_created_after_gate():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(artifact_type="rubric"))
    assert out.get("draft_id"), "low-risk LMS draft should be created"
    assert out["case_status"] == "RESOLVED"


def test_consequential_action_without_approval_does_not_publish():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(
        artifact_type="announcement",
        action_request={"type": "update_assignment_due_date",
                        "payload": {"assignment": "A5", "new_due": "2026-10-09"}},
    ))
    # No approval bound -> the gateway does not execute the due-date change.
    assert not out.get("published"), "consequential due-date change must not execute without approval"


def test_memory_graph_interrupts_before_human_gate():
    graph = build_graph(use_memory=True)
    cfg = {"configurable": {"thread_id": "t-1"}}
    graph.invoke(_seed(), cfg)
    snap = graph.get_state(cfg)
    # Execution is paused at the human gate (framework-enforced HITL).
    assert snap.next == (HUMAN_GATE_NODE,), f"expected interrupt before {HUMAN_GATE_NODE}, got {snap.next}"
