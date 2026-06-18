# agent/state.py
# ============================================================
# EngagementState — state for a student-success / proactive-outreach interaction.
#
# Bounded agent: it ASSEMBLES authorized signals into an intervention plan, drafts
# proactive outreach, and can open a low-risk advising case. It SEPARATES
# prediction, explanation, and human decision: it never sends outreach
# autonomously (a send is consequential and requires a human approval bound at the
# gateway), and it must not infer or condition on protected categories. Every
# field maps to evidence, a draft, an action, or an audit requirement
# (FERPA/PPRA recordkeeping and equity monitoring).
# ============================================================
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class RecommendedAction(str, Enum):
    PROCEED = "PROCEED"      # clean, grounded -> route to human gate / finalize
    REVISE = "REVISE"        # grounding issue -> redraft plan/outreach (bounded)
    ESCALATE = "ESCALATE"    # equity flag / sensitive -> human counselor review


class EngagementState(TypedDict, total=False):
    # ── Request / context ─────────────────────────────────────────────────────
    request_id: str
    channel: str                 # web | sis | lms | batch
    student_ref: str
    trigger_event: str           # absences | missing_work | disengagement | deadline

    # Verified IdP claims for the acting user (the counselor). Gateway-backed tools
    # require these; absent them the gateway denies (fail-closed).
    acting_user_claims: Dict[str, Any]

    # Optional aggregate group rates for equity monitoring (institution-supplied;
    # no protected attributes are inferred or stored by the agent).
    base_rates: Dict[str, float]
    selected_rates: Dict[str, float]

    # ── Assembled evidence ────────────────────────────────────────────────────
    evidence: Dict[str, Any]               # risk signals + attendance + grades + engagement + history

    # ── Draft + checks ────────────────────────────────────────────────────────
    draft_plan: str
    draft_message: str
    generated_by: str                      # bedrock | anthropic | demo-stub
    grounding_report: Dict[str, Any]
    fairness_report: Dict[str, Any]
    compliance_findings: List[str]
    recommended_action: RecommendedAction
    revision_count: int

    # ── Optional low-risk case / consequential outreach send ──────────────────
    action_request: Optional[Dict[str, Any]]  # e.g. {"type":"send_message", ...}
    approval: Optional[Dict[str, Any]]        # counselor sign-off for an outreach send
    case_id: str
    message_id: str

    # ── Disposition ───────────────────────────────────────────────────────────
    case_status: str             # ASSEMBLING | PENDING_REVIEW | RESOLVED | ESCALATED

    # ── LangGraph / UI infra + audit ──────────────────────────────────────────
    messages: List[Any]
    current_step: str
    completed_steps: List[str]
    errors: List[Dict[str, Any]]
    audit_trail: List[Dict[str, Any]]
