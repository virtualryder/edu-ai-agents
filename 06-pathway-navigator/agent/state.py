# agent/state.py
# ============================================================
# PathwayState — state for a course/degree planning interaction.
#
# Bounded agent: it ASSEMBLES grounded planning options from deterministic degree
# rules (degree audit, prerequisite checks), maps transfer credits, surfaces
# career pathways, and initiates a LOW-RISK workflow (schedule a counselor
# appointment). It distinguishes an OPTION from a RECOMMENDATION from an APPROVED
# PLAN, and it NEVER makes an irreversible placement decision — placement is a
# human counselor's call, framework-enforced at the human-review gate. Every field
# maps to a planning input, a rules result, an action, or an audit requirement.
# ============================================================
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class RecommendedAction(str, Enum):
    ANSWER = "ANSWER"        # clean, grounded plan -> route to counselor gate / finalize
    REVISE = "REVISE"        # grounding/labeling issue -> redraft (bounded)
    ESCALATE = "ESCALATE"    # placement / out-of-scope -> human counselor


class PathwayState(TypedDict, total=False):
    # ── Request / context ─────────────────────────────────────────────────────
    request_id: str
    channel: str                 # web | mobile | voice | sms | chat
    goal: str                    # plan | graduation | transfer | career
    question: str
    preferred_language: str

    # Verified IdP claims for the acting user (student/counselor). Gateway-backed
    # tools require these; absent them the gateway denies (fail-closed).
    acting_user_claims: Dict[str, Any]

    # ── Retrieval ─────────────────────────────────────────────────────────────
    profile: Dict[str, Any]                # sis.get_student_profile
    grad_requirements: Dict[str, Any]      # sis.get_graduation_requirements
    transfer_credits: Dict[str, Any]       # sis.get_transfer_credits
    policy_hits: List[Dict[str, Any]]      # kb.search_policies
    career_pathways: Dict[str, Any]        # labor.get_career_pathways

    # ── Deterministic rules ───────────────────────────────────────────────────
    degree_audit: Dict[str, Any]           # rules.run_degree_audit
    prereq_check: Dict[str, Any]           # rules.check_prerequisites

    # ── Draft + checks ────────────────────────────────────────────────────────
    draft_plan: str
    generated_by: str                      # bedrock | anthropic | demo-stub
    grounding_report: Dict[str, Any]
    compliance_findings: List[str]
    recommended_action: RecommendedAction
    revision_count: int

    # ── Optional low-risk action (schedule with a counselor) ──────────────────
    action_request: Optional[Dict[str, Any]]  # e.g. {"type":"schedule_appointment", ...}
    approval: Optional[Dict[str, Any]]        # reviewer sign-off (not required for low-risk)
    appointment_id: str

    # ── Disposition ───────────────────────────────────────────────────────────
    case_status: str             # PLANNING | PENDING_REVIEW | RESOLVED | ESCALATED

    # ── LangGraph / UI infra + audit ──────────────────────────────────────────
    messages: List[Any]
    current_step: str
    completed_steps: List[str]
    errors: List[Dict[str, Any]]
    audit_trail: List[Dict[str, Any]]
