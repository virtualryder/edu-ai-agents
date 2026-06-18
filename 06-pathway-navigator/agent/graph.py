# agent/graph.py
# ============================================================
# LangGraph DAG for the Pathway Navigator.
#
#   intake -> retrieve -> run_rules -> draft_plan -> checks -> [routing] ->
#       { draft_plan (revise, bounded) | human_review_gate } -> finalize -> END
#
# HITL is framework-enforced: the graph compiles with
# interrupt_before=["human_review_gate"], so a counselor must review the assembled
# options/recommendations and make any placement decision before finalize runs the
# low-risk scheduling action. No application code bypasses it.
# ============================================================
from __future__ import annotations

import logging

from langgraph.graph import END, StateGraph

from agent.nodes import (
    checks,
    draft_plan,
    finalize,
    human_review_gate,
    intake,
    retrieve,
    routing_decision,
    run_rules,
)
from agent.persistence import get_checkpointer
from agent.state import PathwayState

logger = logging.getLogger(__name__)

HUMAN_GATE_NODE = "human_review_gate"


def build_graph(use_memory: bool = True):
    workflow = StateGraph(PathwayState)

    workflow.add_node("intake", intake)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("run_rules", run_rules)
    workflow.add_node("draft_plan", draft_plan)
    workflow.add_node("checks", checks)
    workflow.add_node("human_review_gate", human_review_gate)
    workflow.add_node("finalize", finalize)

    workflow.set_entry_point("intake")
    workflow.add_edge("intake", "retrieve")
    workflow.add_edge("retrieve", "run_rules")
    workflow.add_edge("run_rules", "draft_plan")
    workflow.add_edge("draft_plan", "checks")
    workflow.add_conditional_edges(
        source="checks",
        path=routing_decision,
        path_map={
            "draft_plan": "draft_plan",                 # bounded revision loop
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
    A[Student/Counselor Planning Request] --> B[intake]
    B --> C[retrieve<br/>Profile · Grad reqs · Transfer · Content]
    C --> R[run_rules<br/>Degree audit · Prerequisites]
    R --> D[draft_plan<br/>Option · Recommendation]
    D --> E[checks<br/>Grounding · Placement guard]
    E --> F{routing_decision}
    F -->|issues, revise| D
    F -->|clean / escalate| G[human_review_gate<br/>Counselor review · Placement]
    G --> H[finalize<br/>Schedule counselor · Audit]
    H --> I[END]
    style G fill:#4CAF50,color:#fff
    style I fill:#2196F3,color:#fff
"""
