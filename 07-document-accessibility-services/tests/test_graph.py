"""Integration test: the Document & Accessibility graph runs end-to-end in demo mode."""
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
        "mode": "accessibility",
        "document_ref": "CONTENT-test-0001",
        "target_language": "es",
        "question": "Make this approved content accessible and translate it.",
        "acting_user_claims": {"sub": "staff-test", "custom:edu_role": "ENROLLMENT_STAFF"},
    }
    base.update(over)
    return base


def test_runs_end_to_end():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["draft_message"]
    assert "classify_extract" in out["completed_steps"]
    assert "validate" in out["completed_steps"]
    assert "checks" in out["completed_steps"]
    assert out["recommended_action"] in (
        RecommendedAction.ANSWER, RecommendedAction.REVISE, RecommendedAction.ESCALATE
    )
    assert out["audit_trail"], "audit trail must be populated"


def test_clean_accessibility_routes_to_human_gate():
    # Accessibility mode with no low-confidence/incomplete inputs -> ANSWER.
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed())
    assert out["recommended_action"] == RecommendedAction.ANSWER
    assert "human_review_gate" in out["completed_steps"]


def test_consequential_enrollment_update_without_approval_stays_pending():
    graph = build_graph(use_memory=False)
    out = graph.invoke(_seed(mode="enrollment", document_ref="DOC-transcript-0001",
                             action_request={"type": "update_enrollment_record",
                                             "payload": {"student": "STU-demo0001", "field": "transfer_credits"}}))
    # No approval bound -> the gateway does not execute the write; no record id.
    assert not out.get("enrollment_record_id"), "consequential SIS write must not execute without approval"


def test_memory_graph_interrupts_before_human_gate():
    graph = build_graph(use_memory=True)
    cfg = {"configurable": {"thread_id": "t-1"}}
    graph.invoke(_seed(), cfg)
    snap = graph.get_state(cfg)
    # Execution is paused at the human gate (framework-enforced HITL).
    assert snap.next == (HUMAN_GATE_NODE,), f"expected interrupt before {HUMAN_GATE_NODE}, got {snap.next}"
