# agent/state.py
# ============================================================
# ServiceDeskState — state for an IT / staff-admin service-desk interaction.
#
# Bounded agent: (A) IT service desk — it DIAGNOSES issues, answers from policy,
# files LOW-RISK tickets, and (only with approval) performs PRIVILEGED remediation
# (password reset, service restart); (B) staff admin/knowledge — policy Q&A,
# drafting RFP/scope documents, and routing approvals. There is a STRONG division
# between diagnostics (the agent does these) and privileged remediation (a human
# approves these). Any security/identity/safeguarding concern is escalated
# immediately. The privileged tools are CONSEQUENTIAL and do NOT execute without a
# verified human approval bound at the gateway. Every field maps to an input, a
# check, an action, or audit.
# ============================================================
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict


class RecommendedAction(str, Enum):
    ANSWER = "ANSWER"        # clean, grounded -> route to human gate / finalize
    REVISE = "REVISE"        # grounding issue -> redraft (bounded)
    ESCALATE = "ESCALATE"    # security/identity/safeguarding / out-of-scope -> human


class ServiceDeskState(TypedDict, total=False):
    # ── Request / context ─────────────────────────────────────────────────────
    request_id: str
    channel: str                 # web | portal | email | phone | chat
    track: str                   # it | admin
    request: str                 # the request text

    # Verified IdP claims for the acting user (IT staff/admin or staff/approver).
    # Gateway-backed tools require these; absent them the gateway denies (fail-closed).
    acting_user_claims: Dict[str, Any]

    # ── Retrieval ─────────────────────────────────────────────────────────────
    kb_hits: List[Dict[str, Any]]          # kb.search_policies / erp.search_policy
    diagnostic: Dict[str, Any]             # itsm.run_diagnostic (IT track)

    # ── Draft + checks ────────────────────────────────────────────────────────
    draft_resolution: str                  # answer / diagnostic summary / drafted doc
    generated_by: str                      # bedrock | anthropic | demo-stub
    grounding_report: Dict[str, Any]
    compliance_findings: List[str]
    recommended_action: RecommendedAction
    revision_count: int

    # ── Optional low-risk + consequential actions ─────────────────────────────
    action_request: Optional[Dict[str, Any]]  # create_ticket / draft_document (low-risk)
                                              # OR reset_password / restart_service /
                                              # initiate_approval (consequential)
    approval: Optional[Dict[str, Any]]        # verified human approval (REQUIRED for privileged)
    ticket_id: str
    document_id: str
    remediation_id: str
    approval_id: str

    # ── Disposition ───────────────────────────────────────────────────────────
    case_status: str             # TRIAGING | PENDING_REVIEW | RESOLVED | ESCALATED

    # ── LangGraph / UI infra + audit ──────────────────────────────────────────
    messages: List[Any]
    current_step: str
    completed_steps: List[str]
    errors: List[Dict[str, Any]]
    audit_trail: List[Dict[str, Any]]
