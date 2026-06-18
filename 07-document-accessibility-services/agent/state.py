# agent/state.py
# ============================================================
# DocAccessState — state for a document-intake / accessibility interaction.
#
# Bounded agent: (A) enrollment-document intake — it CLASSIFIES, EXTRACTS, and
# VALIDATES documents, lists missing items, and PREPARES a SIS enrollment update;
# (B) accessibility/multilingual — it TRANSFORMS approved content into accessible
# or translated drafts. It NEVER decides admissions; it prepares material for a
# human decision. The enrollment-record write is CONSEQUENTIAL and does NOT
# execute without a verified human approval bound at the gateway. Uncertain
# fields, incomplete documents, and individualized/legal material always require
# human verification. Every field maps to an input, a check, an action, or audit.
# ============================================================
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class RecommendedAction(str, Enum):
    ANSWER = "ANSWER"        # clean, complete, grounded -> route to human gate / finalize
    REVISE = "REVISE"        # grounding issue -> redraft (bounded)
    ESCALATE = "ESCALATE"    # low-confidence / incomplete / sensitive -> human verification


class DocAccessState(TypedDict, total=False):
    # ── Request / context ─────────────────────────────────────────────────────
    request_id: str
    channel: str                 # web | mobile | portal | email
    mode: str                    # enrollment | accessibility
    document_ref: str            # reference to the source document or content
    target_language: str         # for accessibility/translation mode

    # Verified IdP claims for the acting user (enrollment staff). Gateway-backed
    # tools require these; absent them the gateway denies (fail-closed).
    acting_user_claims: Dict[str, Any]

    # ── Classification / extraction (enrollment mode) ─────────────────────────
    doc_type: str                          # docpipe.classify_document
    extracted_fields: Dict[str, Any]       # docpipe.extract_fields
    low_confidence_fields: List[str]       # uncertain fields -> escalate
    completeness: Dict[str, Any]           # docpipe.validate_completeness (missing items)

    # ── Accessibility / multilingual (accessibility mode) ─────────────────────
    accessible_artifacts: Dict[str, Any]   # docpipe.transform_accessible / translate_content

    # ── Draft + checks ────────────────────────────────────────────────────────
    draft_message: str                     # missing-items request OR artifact summary
    generated_by: str                      # bedrock | anthropic | demo-stub
    grounding_report: Dict[str, Any]
    compliance_findings: List[str]
    recommended_action: RecommendedAction
    revision_count: int

    # ── Consequential action (prepare / commit SIS enrollment update) ─────────
    action_request: Optional[Dict[str, Any]]  # e.g. {"type":"update_enrollment_record", ...}
    approval: Optional[Dict[str, Any]]        # verified human approval (REQUIRED to write)
    enrollment_record_id: str

    # ── Disposition ───────────────────────────────────────────────────────────
    case_status: str             # PROCESSING | PENDING_REVIEW | RESOLVED | ESCALATED

    # ── LangGraph / UI infra + audit ──────────────────────────────────────────
    messages: List[Any]
    current_step: str
    completed_steps: List[str]
    errors: List[Dict[str, Any]]
    audit_trail: List[Dict[str, Any]]
