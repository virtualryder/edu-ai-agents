# agent/state.py
# ============================================================
# TutorState — state for a curriculum-grounded Socratic tutoring interaction.
#
# Bounded agent: it gives HINTS, concept explanations, practice, and prerequisite
# review grounded ONLY in instructor-approved course material. It NEVER completes a
# graded or otherwise prohibited assessment — a request to do so is escalated, not
# answered. There are no consequential writes; the human gate gives the teacher
# oversight (surfacing misconceptions, never hidden scores). Every field maps to a
# tutoring response, a check, or an audit requirement.
# ============================================================
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class RecommendedAction(str, Enum):
    ANSWER = "ANSWER"        # clean, grounded hint/explanation -> human gate / finalize
    REVISE = "REVISE"        # grounding issue -> redraft (bounded)
    ESCALATE = "ESCALATE"    # prohibited/graded-assessment request -> human teacher; do NOT answer


class TutorState(TypedDict, total=False):
    # ── Request / context ─────────────────────────────────────────────────────
    request_id: str
    channel: str                 # web | mobile | voice | sms | chat
    question: str
    course: str
    section: str
    mode: str                    # hint | explain | practice

    # Verified IdP claims for the acting user (student). Gateway-backed tools
    # require these; absent them the gateway denies (fail-closed).
    acting_user_claims: Dict[str, Any]

    # ── Retrieval ─────────────────────────────────────────────────────────────
    course_hits: List[Dict[str, Any]]      # kb.search_course_material + lms.get_course_content
    assignments: Dict[str, Any]            # lms.get_assignments

    # ── Draft + checks ────────────────────────────────────────────────────────
    draft_response: str
    generated_by: str                      # bedrock | anthropic | demo-stub
    grounding_report: Dict[str, Any]
    compliance_findings: List[str]
    misconceptions: List[str]
    recommended_action: RecommendedAction
    revision_count: int

    # ── Disposition ───────────────────────────────────────────────────────────
    session_status: str          # TUTORING | PENDING_REVIEW | RESOLVED | ESCALATED

    # ── LangGraph / UI infra + audit ──────────────────────────────────────────
    messages: List[Any]
    current_step: str
    completed_steps: List[str]
    errors: List[Dict[str, Any]]
    audit_trail: List[Dict[str, Any]]
