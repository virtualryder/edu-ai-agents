# agent/graph.py
# ============================================================
# LangGraph DAG for the Student & Family Services Concierge.
#
#   intake -> retrieve -> draft_response -> checks -> [routing] ->
#       { draft_response (revise, bounded) | human_review_gate } -> finalize -> END
#
# HITL is framework-enforced: the graph compiles with
# interrupt_before=["human_review_gate"], so a staff member must review and resume
# before finalize runs any consequential action. No application code bypasses it.
# ============================================================
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from agent.nodes import (
    checks,
    draft_response,
    finalize,
    human_review_gate,
    intake,
    retrieve,
    routing_decision,
)
from agent.persistence import get_checkpointer
from agent.state import ConciergeState

logger = logging.getLogger(__name__)

HUMAN_GATE_NODE = "human_review_gate"


def build_graph(use_memory: bool = True):
    workflow = StateGraph(ConciergeState)

    workflow.add_node("intake", intake)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("draft_response", draft_response)
    workflow.add_node("checks", checks)
    workflow.add_node("human_review_gate", human_review_gate)
    workflow.add_node("finalize", finalize)

    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "retrieve")
    workflow.add_edge("retrieve", "draft_response")
    workflow.add_edge("draft_response", "checks")
    workflow.add_conditional_edges(
        source="checks",
        path=routing_decision,
        path_map={
            "draft_response": "draft_response",          # bounded revision loop
            "human_review_gate": "human_review_gate",     # escalate / consequential send -> human
            "finalize": "finalize",                       # clean read-only / low-risk -> no gate
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
    A[Student/Family Question] --> B[intake]
    B --> C[retrieve<br/>Approved content · Status]
    C --> D[draft_response<br/>Grounded answer]
    D --> E[checks<br/>Grounding · Compliance]
    E --> F{routing_decision}
    F -->|issues, revise| D
    F -->|clean / escalate| G[human_review_gate<br/>Staff review/approval]
    G --> H[finalize<br/>Open case · Schedule · Audit]
    H --> I[END]
    style G fill:#4CAF50,color:#fff
    style I fill:#2196F3,color:#fff
"""
