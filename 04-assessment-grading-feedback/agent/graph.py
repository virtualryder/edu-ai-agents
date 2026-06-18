# agent/graph.py
# ============================================================
# LangGraph DAG for the Assessment, Grading & Feedback agent.
#
#   intake -> retrieve -> evaluate -> draft_feedback -> checks -> [routing] ->
#       { draft_feedback (revise, bounded) | human_review_gate } -> finalize -> END
#
# HITL is framework-enforced: the graph compiles with
# interrupt_before=["human_review_gate"], so the educator must review and resume
# before finalize releases any grade. No application code bypasses it.
# ============================================================
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from agent.nodes import (
    checks,
    draft_feedback,
    evaluate,
    finalize,
    human_review_gate,
    intake,
    retrieve,
    routing_decision,
)
from agent.persistence import get_checkpointer
from agent.state import GradingState

logger = logging.getLogger(__name__)

HUMAN_GATE_NODE = "human_review_gate"


def build_graph(use_memory: bool = True):
    workflow = StateGraph(GradingState)

    workflow.add_node("intake", intake)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("evaluate", evaluate)
    workflow.add_node("draft_feedback", draft_feedback)
    workflow.add_node("checks", checks)
    workflow.add_node("human_review_gate", human_review_gate)
    workflow.add_node("finalize", finalize)

    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "retrieve")
    workflow.add_edge("retrieve", "evaluate")
    workflow.add_edge("evaluate", "draft_feedback")
    workflow.add_edge("draft_feedback", "checks")
    workflow.add_conditional_edges(
        source="checks",
        path=routing_decision,
        path_map={
            "draft_feedback": "draft_feedback",          # bounded revision loop
            "human_review_gate": "human_review_gate",     # clean / escalate -> human
        },
    )
    workflow.add_edge("human_review_gate", "finalize")
    workflow.add_edge("finalize", END)

    if use_memory:
        return workflow.compile(
            checkpointer=get_checkpointer(),
            interrupt_before=[HUMAN_GATE_NODE],  # framework-enforced HITL
        )
    return workflow.compile()


def get_graph_visualization() -> str:
    return """
graph TD
    A[Student Submission + Rubric] --> B[intake]
    B --> C[retrieve<br/>Assignment · Rubric ref]
    C --> D[evaluate<br/>Rubric scores · Confidence]
    D --> E[draft_feedback<br/>Grounded feedback]
    E --> F[checks<br/>Grounding · Confidence threshold]
    F --> G{routing_decision}
    G -->|issues, revise| E
    G -->|clean / escalate| H[human_review_gate<br/>Educator owns the grade]
    H --> I[finalize<br/>Release grade only w/ approval · Audit]
    I --> J[END]
    style H fill:#4CAF50,color:#fff
    style J fill:#2196F3,color:#fff
"""
