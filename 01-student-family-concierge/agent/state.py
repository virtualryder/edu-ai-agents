# agent/state.py
# ============================================================
# ConciergeState — state for a student/family services interaction.
#
# Bounded agent: it ANSWERS questions grounded in approved institutional content,
# checks authenticated status, and initiates LOW-RISK workflows (open an advising
# case, schedule an appointment). It does NOT decide admissions, financial aid,
# discipline, or placement, and consequential outbound messages require a human
# approval bound at the gateway. Every field maps to an answer, action, or audit
# requirement (FERPA disclosure recordkeeping).
# ============================================================
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class RecommendedAction(str, Enum):
    ANSWER = "ANSWER"        # clean, grounded -> route to human gate / finalize
    REVISE = "REVISE"        # grounding/compliance issue -> redraft (bounded)
    ESCALATE = "ESCALATE"    # sensitive / out-of-scope -> human staff


class ConciergeState(TypedDict, total=False):
    # ── Request / context ─────────────────────────────────────────────────────
    request_id: str
    channel: str                 # web | mobile | voice | sms | chat
    question: str
    intent: str                  # INFO | STATUS | ACTION
    authenticated: bool
    preferred_language: str

    # Verified IdP claims for the acting user (student/guardian/staff). Gateway-
    # backed tools require these; absent them the gateway denies (fail-closed).
    acting_user_claims: Dict[str, Any]

    # ── Retrieval ─────────────────────────────────────────────────────────────
    policy_hits: List[Dict[str, Any]]      # kb.search_policies
    status_result: Dict[str, Any]          # sis.check_application_status
    schedule: Dict[str, Any]               # sis.get_schedule

    # ── Draft + checks ────────────────────────────────────────────────────────
    draft_response: str
    generated_by: str                      # bedrock | anthropic | demo-stub
    grounding_report: Dict[str, Any]
    compliance_findings: List[str]
    recommended_action: RecommendedAction
    revision_count: int

    # ── Optional low-risk action / consequential send ─────────────────────────
    action_request: Optional[Dict[str, Any]]  # e.g. {"type":"create_advising_case", ...}
    approval: Optional[Dict[str, Any]]        # reviewer sign-off for consequential sends
    case_id: str
    appointment_id: str
    message_id: str

    # ── Disposition ───────────────────────────────────────────────────────────
    case_status: str             # ANSWERING | PENDING_REVIEW | RESOLVED | ESCALATED

    # ── LangGraph / UI infra + audit ──────────────────────────────────────────
    messages: List[Any]
    current_step: str
    completed_steps: List[str]
    errors: List[Dict[str, Any]]
    audit_trail: List[Dict[str, Any]]
