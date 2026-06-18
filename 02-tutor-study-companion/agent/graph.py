# agent/graph.py
# ============================================================
# LangGraph DAG for the Tutor & Study Companion.
#
#   intake -> retrieve -> tutor_respond -> checks -> [routing] ->
#       { tutor_respond (revise, bounded) | human_review_gate } -> finalize -> END
#
# HITL is framework-enforced: the graph compiles with
# interrupt_before=["human_review_gate"], so a teacher can review the tutoring (and
# any escalated prohibited-assessment request) before finalize closes the session.
# No application code bypasses it.
# ============================================================
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from agent.nodes import (
    checks,
    finalize,
    human_review_gate,
    intake,
    retrieve,
    routing_decision,
    tutor_respond,
)
from agent.persistence import get_checkpointer
from agent.state import TutorState

logger = logging.getLogger(__name__)

HUMAN_GATE_NODE = "human_review_gate"


def build_graph(use_memory: bool = True):
    workflow = StateGraph(TutorState)

    workflow.add_node("intake", intake)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("tutor_respond", tutor_respond)
    workflow.add_node("checks", checks)
    workflow.add_node("human_review_gate", human_review_gate)
    workflow.add_node("finalize", finalize)

    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "retrieve")
    workflow.add_edge("retrieve", "tutor_respond")
    workflow.add_edge("tutor_respond", "checks")
    workflow.add_conditional_edges(
        source="checks",
        path=routing_decision,
        path_map={
            "tutor_respond": "tutor_respond",          # bounded revision loop
            "human_review_gate": "human_review_gate",   # clean / escalate -> human
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
    A[Student Question] --> B[intake]
    B --> C[retrieve<br/>Approved course material · Assignments]
    C --> D[tutor_respond<br/>Socratic hint / explanation]
    D --> E[checks<br/>Grounding · Prohibited-behavior]
    E --> F{routing_decision}
    F -->|issues, revise| D
    F -->|clean / escalate| G[human_review_gate<br/>Teacher oversight]
    G --> H[finalize<br/>Log session · Misconceptions]
    H --> I[END]
    style G fill:#4CAF50,color:#fff
    style I fill:#2196F3,color:#fff
"""
