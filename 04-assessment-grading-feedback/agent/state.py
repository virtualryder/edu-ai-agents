# agent/state.py
# ============================================================
# GradingState — state for a rubric-grounded assessment interaction.
#
# Bounded agent: it EVALUATES open-ended student work against an approved rubric,
# drafts grounded feedback, detects misconceptions, and routes low-confidence
# cases for manual review. It does NOT release a final/high-stakes grade
# autonomously — the educator owns the grade, and releasing it is a consequential
# action that requires a human approval bound at the gateway. Every field maps to
# an evaluation, draft, action, or audit requirement (FERPA/grade recordkeeping).
# ============================================================
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class RecommendedAction(str, Enum):
    APPROVE_DRAFT = "APPROVE_DRAFT"  # clean, grounded, confident -> human gate / finalize
    REVISE = "REVISE"                # grounding issue -> redraft feedback (bounded)
    ESCALATE = "ESCALATE"            # low confidence / sensitive -> manual educator review


class GradingState(TypedDict, total=False):
    # ── Request / context ─────────────────────────────────────────────────────
    request_id: str
    channel: str                 # web | lms | batch
    course: str
    submission_id: str
    rubric_ref: str
    assignment_id: str

    # Verified IdP claims for the acting user (the educator). Gateway-backed tools
    # require these; absent them the gateway denies (fail-closed).
    acting_user_claims: Dict[str, Any]

    # ── Retrieval ─────────────────────────────────────────────────────────────
    assignment: Dict[str, Any]             # lms.get_assignments

    # ── Evaluation ────────────────────────────────────────────────────────────
    evaluation: Dict[str, Any]             # assessment.evaluate_rubric
    confidence: float                      # evaluator confidence (0..1)
    class_patterns: Dict[str, Any]         # assessment.summarize_class_patterns

    # ── Draft + checks ────────────────────────────────────────────────────────
    draft_feedback: str
    generated_by: str                      # bedrock | anthropic | demo-stub
    grounding_report: Dict[str, Any]
    compliance_findings: List[str]
    recommended_action: RecommendedAction
    revision_count: int

    # ── Optional consequential grade release ──────────────────────────────────
    action_request: Optional[Dict[str, Any]]  # e.g. {"type":"release_grade", ...}
    approval: Optional[Dict[str, Any]]        # educator sign-off for grade release
    grade_id: str

    # ── Disposition ───────────────────────────────────────────────────────────
    case_status: str             # EVALUATING | PENDING_REVIEW | RESOLVED | ESCALATED

    # ── LangGraph / UI infra + audit ──────────────────────────────────────────
    messages: List[Any]
    current_step: str
    completed_steps: List[str]
    errors: List[Dict[str, Any]]
    audit_trail: List[Dict[str, Any]]
