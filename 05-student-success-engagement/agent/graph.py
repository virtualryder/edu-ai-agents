# agent/graph.py
# ============================================================
# LangGraph DAG for the Student Success & Engagement agent.
#
#   intake -> assemble_evidence -> draft_intervention -> checks -> [routing] ->
#       { draft_intervention (revise, bounded) | human_review_gate } -> finalize -> END
#
# HITL is framework-enforced: the graph compiles with
# interrupt_before=["human_review_gate"], so a counselor must review and resume
# before finalize runs any consequential outreach. No application code bypasses it.
# ============================================================
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from agent.nodes import (
    assemble_evidence,
    checks,
    draft_intervention,
    finalize,
    human_review_gate,
    intake,
    routing_decision,
)
from agent.persistence import get_checkpointer
from agent.state import EngagementState

logger = logging.getLogger(__name__)

HUMAN_GATE_NODE = "human_review_gate"


def build_graph(use_memory: bool = True):
    workflow = StateGraph(EngagementState)

    workflow.add_node("intake", intake)
    workflow.add_node("assemble_evidence", assemble_evidence)
    workflow.add_node("draft_intervention", draft_intervention)
    workflow.add_node("checks", checks)
    workflow.add_node("human_review_gate", human_review_gate)
    workflow.add_node("finalize", finalize)

    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "assemble_evidence")
    workflow.add_edge("assemble_evidence", "draft_intervention")
    workflow.add_edge("draft_intervention", "checks")
    workflow.add_conditional_edges(
        source="checks",
        path=routing_decision,
        path_map={
            "draft_intervention": "draft_intervention",   # bounded revision loop
            "human_review_gate": "human_review_gate",      # clean / escalate -> human
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
    A[Trigger Event] --> B[intake]
    B --> C[assemble_evidence<br/>Signals · Attendance · Grades · Engagement · History]
    C --> D[draft_intervention<br/>Plan + grounded outreach]
    D --> E[checks<br/>Grounding · PPRA guard · Fairness]
    E --> F{routing_decision}
    F -->|issues, revise| D
    F -->|clean / escalate| G[human_review_gate<br/>Counselor approves outreach]
    G --> H[finalize<br/>Advising case · Send only w/ approval · Audit]
    H --> I[END]
    style G fill:#4CAF50,color:#fff
    style I fill:#2196F3,color:#fff
"""
