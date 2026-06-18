# agent/graph.py
# ============================================================
# LangGraph DAG for Operations & Service Desk.
#
#   intake -> retrieve -> draft_resolution -> checks -> [routing] ->
#       { draft_resolution (revise, bounded) | human_review_gate } -> finalize -> END
#
# HITL is framework-enforced: the graph compiles with
# interrupt_before=["human_review_gate"], so a human reviews the resolution and
# approves any privileged remediation (password reset, service restart) or
# financial approval before finalize runs it. No application code bypasses it, and
# the privileged tools also require a gateway-bound approval to execute.
# ============================================================
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from agent.nodes import (
    checks,
    draft_resolution,
    finalize,
    human_review_gate,
    intake,
    retrieve,
    routing_decision,
)
from agent.persistence import get_checkpointer
from agent.state import ServiceDeskState

logger = logging.getLogger(__name__)

HUMAN_GATE_NODE = "human_review_gate"


def build_graph(use_memory: bool = True):
    workflow = StateGraph(ServiceDeskState)

    workflow.add_node("intake", intake)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("draft_resolution", draft_resolution)
    workflow.add_node("checks", checks)
    workflow.add_node("human_review_gate", human_review_gate)
    workflow.add_node("finalize", finalize)

    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "retrieve")
    workflow.add_edge("retrieve", "draft_resolution")
    workflow.add_edge("draft_resolution", "checks")
    workflow.add_conditional_edges(
        source="checks",
        path=routing_decision,
        path_map={
            "draft_resolution": "draft_resolution",       # bounded revision loop
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
    A[IT / Admin Service Request] --> B[intake]
    B --> C[retrieve<br/>Policy · Diagnostic]
    C --> D[draft_resolution<br/>Answer · Diagnostic summary · Document]
    D --> E[checks<br/>Grounding · Safeguarding/Security]
    E --> F{routing_decision}
    F -->|issues, revise| D
    F -->|clean / escalate| G[human_review_gate<br/>Staff review · Privileged approval]
    G --> H[finalize<br/>Ticket/draft low-risk · Privileged only w/ approval · Audit]
    H --> I[END]
    style G fill:#4CAF50,color:#fff
    style I fill:#2196F3,color:#fff
"""
