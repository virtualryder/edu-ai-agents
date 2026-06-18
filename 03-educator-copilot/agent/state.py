# agent/state.py
# ============================================================
# CopilotState — state for an educator instructional-design interaction.
#
# Bounded agent: it drafts instructional artifacts (lessons, rubrics, quizzes,
# announcements, differentiation) grounded in approved curriculum and PLACES THEM
# AS DRAFTS in the LMS via low-risk tools. It never auto-publishes: making content
# live to students (publish_content) or moving a learner's deadline
# (update_assignment_due_date) is consequential and requires a verified educator
# approval bound at the gateway. Every field maps to an artifact, an action, or an
# audit requirement.
# ============================================================
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class RecommendedAction(str, Enum):
    APPROVE_DRAFT = "APPROVE_DRAFT"  # clean, grounded -> route to human gate / finalize
    REVISE = "REVISE"                # grounding/accessibility issue -> redraft (bounded)
    ESCALATE = "ESCALATE"            # out-of-scope / needs a human decision


class CopilotState(TypedDict, total=False):
    # ── Request / context ─────────────────────────────────────────────────────
    request_id: str
    channel: str                 # web | mobile | voice | sms | chat
    artifact_type: str           # lesson | rubric | quiz | announcement | differentiation
    course: str
    instructions: str

    # Verified IdP claims for the acting user (educator). Gateway-backed tools
    # require these; absent them the gateway denies (fail-closed).
    acting_user_claims: Dict[str, Any]

    # ── Retrieval ─────────────────────────────────────────────────────────────
    roster: Dict[str, Any]                 # lms.get_roster
    curriculum_hits: List[Dict[str, Any]]  # kb.search_course_material + lms.get_course_content
    class_results: Dict[str, Any]          # lms.get_engagement / identify_missing_submissions

    # ── Draft + checks ────────────────────────────────────────────────────────
    draft_artifact: str
    generated_by: str                      # bedrock | anthropic | demo-stub
    grounding_report: Dict[str, Any]
    compliance_findings: List[str]
    recommended_action: RecommendedAction
    revision_count: int

    # ── Low-risk draft write + optional consequential action ──────────────────
    action_request: Optional[Dict[str, Any]]  # e.g. {"type":"update_assignment_due_date", ...}
    approval: Optional[Dict[str, Any]]         # reviewer sign-off for consequential actions
    draft_id: str
    published: bool

    # ── Disposition ───────────────────────────────────────────────────────────
    case_status: str             # DRAFTING | PENDING_REVIEW | RESOLVED | ESCALATED

    # ── LangGraph / UI infra + audit ──────────────────────────────────────────
    messages: List[Any]
    current_step: str
    completed_steps: List[str]
    errors: List[Dict[str, Any]]
    audit_trail: List[Dict[str, Any]]
