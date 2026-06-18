# agent/graph.py
# ============================================================
# LangGraph DAG for the Educator Copilot.
#
#   intake -> retrieve -> draft_artifact -> checks -> [routing] ->
#       { draft_artifact (revise, bounded) | human_review_gate } -> finalize -> END
#
# HITL is framework-enforced: the graph compiles with
# interrupt_before=["human_review_gate"], so an educator must review and approve
# before finalize runs any consequential action (publish_content /
# update_assignment_due_date). No application code bypasses it.
# ============================================================
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from agent.nodes import (
    checks,
    draft_artifact,
    finalize,
    human_review_gate,
    intake,
    retrieve,
    routing_decision,
)
from agent.persistence import get_checkpointer
from agent.state import CopilotState

logger = logging.getLogger(__name__)

HUMAN_GATE_NODE = "human_review_gate"


def build_graph(use_memory: bool = True):
    workflow = StateGraph(CopilotState)

    workflow.add_node("intake", intake)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("draft_artifact", draft_artifact)
    workflow.add_node("checks", checks)
    workflow.add_node("human_review_gate", human_review_gate)
    workflow.add_node("finalize", finalize)

    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "retrieve")
    workflow.add_edge("retrieve", "draft_artifact")
    workflow.add_edge("draft_artifact", "checks")
    workflow.add_conditional_edges(
        source="checks",
        path=routing_decision,
        path_map={
            "draft_artifact": "draft_artifact",         # bounded revision loop
            "human_review_gate": "human_review_gate",    # clean / escalate -> human
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
    A[Educator Request] --> B[intake]
    B --> C[retrieve<br/>Curriculum · Roster · Results]
    C --> D[draft_artifact<br/>Grounded DRAFT]
    D --> E[checks<br/>Grounding · Accessibility]
    E --> F{routing_decision}
    F -->|issues, revise| D
    F -->|clean / escalate| G[human_review_gate<br/>Educator approval]
    G --> H[finalize<br/>Create LMS draft · Approved actions]
    H --> I[END]
    style G fill:#4CAF50,color:#fff
    style I fill:#2196F3,color:#fff
"""
