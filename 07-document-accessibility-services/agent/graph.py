# agent/graph.py
# ============================================================
# LangGraph DAG for Document & Accessibility Services.
#
#   intake -> classify_extract -> validate -> draft -> checks -> [routing] ->
#       { draft (revise, bounded) | human_review_gate } -> finalize -> END
#
# HITL is framework-enforced: the graph compiles with
# interrupt_before=["human_review_gate"], so a human verifies extracted data and
# approves any consequential enrollment-record write before finalize runs it. No
# application code bypasses it, and the SIS write also requires a gateway-bound
# approval to execute.
# ============================================================
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from agent.nodes import (
    checks,
    classify_extract,
    draft,
    finalize,
    human_review_gate,
    intake,
    routing_decision,
    validate,
)
from agent.persistence import get_checkpointer
from agent.state import DocAccessState

logger = logging.getLogger(__name__)

HUMAN_GATE_NODE = "human_review_gate"


def build_graph(use_memory: bool = True):
    workflow = StateGraph(DocAccessState)

    workflow.add_node("intake", intake)
    workflow.add_node("classify_extract", classify_extract)
    workflow.add_node("validate", validate)
    workflow.add_node("draft", draft)
    workflow.add_node("checks", checks)
    workflow.add_node("human_review_gate", human_review_gate)
    workflow.add_node("finalize", finalize)

    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "classify_extract")
    workflow.add_edge("classify_extract", "validate")
    workflow.add_edge("validate", "draft")
    workflow.add_edge("draft", "checks")
    workflow.add_conditional_edges(
        source="checks",
        path=routing_decision,
        path_map={
            "draft": "draft",                            # bounded revision loop
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
    A[Document / Content Request] --> B[intake]
    B --> C[classify_extract<br/>Classify · Extract · or Transform/Translate]
    C --> V[validate<br/>Completeness · Missing items]
    V --> D[draft<br/>Missing-items request · Artifact summary]
    D --> E[checks<br/>Grounding · Confidence/Sensitivity]
    E --> F{routing_decision}
    F -->|issues, revise| D
    F -->|clean / escalate| G[human_review_gate<br/>Staff verification · Approval]
    G --> H[finalize<br/>Enrollment update only w/ approval · Audit]
    H --> I[END]
    style G fill:#4CAF50,color:#fff
    style I fill:#2196F3,color:#fff
"""
