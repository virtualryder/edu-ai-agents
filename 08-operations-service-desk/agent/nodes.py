# agent/nodes.py
# ============================================================
# Node functions for the Operations & Service Desk workflow.
#
# Each node reads what it needs from ServiceDeskState, performs one step, writes
# its findings back, and appends an audit-trail entry. The AI diagnoses, answers,
# and drafts; a human approves privileged remediation and financial approvals. The
# human_review gate is framework-enforced via interrupt_before in graph.py, and the
# privileged tools do not execute without a verified approval. Any security,
# identity, or safeguarding concern is escalated immediately.
# ============================================================
from __future__ import annotations

import datetime as _dt
import sys
from pathlib import Path
from typing import Any, Dict

_HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "platform_core"))
sys.path.insert(0, str(_HERE.parent))

from agent.prompts import RESOLUTION_PROMPT, SYSTEM_PROMPT
from agent.state import RecommendedAction, ServiceDeskState
from tools import gateway_tools

try:
    from edu_agent_platform.generation import generate
    from governance.grounding import verify_grounding
except Exception:  # pragma: no cover - resilience for standalone import
    generate = None  # type: ignore
    verify_grounding = None  # type: ignore


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


def _audit(action: str, node: str, sources=None, model: str = "") -> Dict[str, Any]:
    return {
        "timestamp": _now(),
        "actor": "ai_agent",
        "action": action,
        "node": node,
        "data_sources_accessed": sources or [],
        "ai_model_used": model,
        "human_review_required": node in ("human_review_gate", "finalize"),
    }


def _claims(state: ServiceDeskState) -> Dict[str, Any]:
    # Demo default: an authenticated IT-staff identity if none supplied.
    return state.get("acting_user_claims") or {
        "sub": "demo-itstaff", "custom:edu_role": "IT_STAFF",
    }


def intake(state: ServiceDeskState) -> ServiceDeskState:
    state["current_step"] = "intake"
    state.setdefault("revision_count", 0)
    state.setdefault("completed_steps", [])
    state.setdefault("audit_trail", [])
    state.setdefault("track", "it")
    state["case_status"] = "TRIAGING"
    state["audit_trail"].append(_audit(f"Intake of {state.get('track')}-track service request", "intake"))
    state["completed_steps"].append("intake")
    return state


def retrieve(state: ServiceDeskState) -> ServiceDeskState:
    state["current_step"] = "retrieve"
    claims = _claims(state)
    sources = []
    if state.get("track") == "admin":
        try:
            state["kb_hits"] = gateway_tools.search_erp_policy(claims, state.get("request", ""))
            sources.append("erp")
        except Exception as exc:
            state.setdefault("errors", []).append({"step": "retrieve", "error": str(exc),
                                                   "timestamp": _now(), "recoverable": True})
            state.setdefault("kb_hits", [])
    else:  # IT track
        try:
            state["kb_hits"] = gateway_tools.search_policies(claims, state.get("request", ""))
            sources.append("kb")
        except Exception as exc:
            state.setdefault("errors", []).append({"step": "retrieve", "error": str(exc),
                                                   "timestamp": _now(), "recoverable": True})
            state.setdefault("kb_hits", [])
        try:
            state["diagnostic"] = gateway_tools.run_diagnostic(claims, state.get("request", ""))
            sources.append("itsm")
        except Exception:
            state.setdefault("diagnostic", {})
    state["audit_trail"].append(_audit("Retrieved policy / ran diagnostic", "retrieve", sources))
    state["completed_steps"].append("retrieve")
    return state


def _demo_resolution(state: ServiceDeskState) -> str:
    parts = []
    hits = state.get("kb_hits", []) or []
    if hits:
        titles = ", ".join(h.get("title", "a policy") for h in hits[:2])
        parts.append(f"Per institutional policy ({titles}), here is the guidance.")
    if state.get("track") == "admin":
        parts.append("I have outlined a procurement/scope document draft for review; "
                     "any spend approval will be routed to an authorized approver.")
        return " ".join(parts)
    diag = state.get("diagnostic", {}) or {}
    if diag:
        finding = diag.get("finding", "")
        parts.append(f"Diagnostic finding: {finding}.")
        parts.append("Recommended next step: file a ticket so the assigned technician can act. "
                     "Any privileged remediation (such as a password reset or service restart) "
                     "must be approved by authorized staff before it runs.")
    else:
        parts.append("I could not run a diagnostic; I will file a ticket for a technician.")
    return " ".join(parts)


def draft_resolution(state: ServiceDeskState) -> ServiceDeskState:
    state["current_step"] = "draft_resolution"
    kb = "\n".join(f"- {h.get('title','')} ({h.get('ref','')})" for h in state.get("kb_hits", []) or [])
    if generate is not None:
        out = generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=RESOLUTION_PROMPT.format(
                track=state.get("track", "it"),
                channel=state.get("channel", "web"),
                request=state.get("request", ""),
                kb_hits=kb or "(none found)",
                diagnostic=state.get("diagnostic", {}) or "(not applicable)",
            ),
            demo_fn=lambda: _demo_resolution(state),
        )
        state["draft_resolution"], state["generated_by"] = out["text"], out["generated_by"]
    else:  # pragma: no cover
        state["draft_resolution"], state["generated_by"] = _demo_resolution(state), "demo-stub"
    state["audit_trail"].append(_audit("Drafted grounded resolution / document", "draft_resolution",
                                       model=state["generated_by"]))
    state["completed_steps"].append("draft_resolution")
    return state


_SECURITY_TRIGGERS = (
    "security", "breach", "phishing", "malware", "ransomware", "compromise",
    "compromised", "identity", "impersonation", "account takeover", "unauthorized",
    "data leak", "safeguarding", "abuse", "self-harm", "threat", "credential theft",
)


def checks(state: ServiceDeskState) -> ServiceDeskState:
    state["current_step"] = "checks"
    text = state.get("draft_resolution", "")
    request = (state.get("request", "") or "").lower()

    # Compliance: never claim a privileged remediation was performed in the draft.
    prohibited = ("password has been reset", "i have reset your password",
                  "the service has been restarted", "i restarted the service",
                  "the approval has been granted")
    findings = [f"prohibited remediation claim: {p}" for p in prohibited if p in text.lower()]
    state["compliance_findings"] = findings

    if verify_grounding is not None:
        report = verify_grounding(text, dict(state)).to_audit_dict()
    else:  # pragma: no cover
        report = {"grounded": True, "ungrounded_numbers": [], "ungrounded_entities": []}
    state["grounding_report"] = report

    # SAFEGUARDING / SECURITY guard: a security/identity/safeguarding concern
    # always escalates to a human (ESCALATE), no self-service path.
    is_security = any(t in request for t in _SECURITY_TRIGGERS)

    ungrounded = report.get("ungrounded_numbers", []) + report.get("ungrounded_entities", [])
    if findings or is_security:
        state["recommended_action"] = RecommendedAction.ESCALATE
    elif ungrounded and state.get("revision_count", 0) < 1:
        state["recommended_action"] = RecommendedAction.REVISE
        state["revision_count"] = state.get("revision_count", 0) + 1
    else:
        state["recommended_action"] = RecommendedAction.ANSWER

    state["audit_trail"].append(_audit("Ran grounding + safeguarding/security checks", "checks"))
    state["completed_steps"].append("checks")
    return state


def routing_decision(state: ServiceDeskState) -> str:
    if state.get("recommended_action") == RecommendedAction.REVISE:
        return "draft_resolution"
    return "human_review_gate"


def human_review_gate(state: ServiceDeskState) -> ServiceDeskState:
    """HITL pause point. graph compiles with interrupt_before=[human_review_gate].

    A human reviews the resolution and approves any privileged remediation or
    financial approval; security/identity/safeguarding concerns land here as
    escalations.
    """
    state["current_step"] = "human_review_gate"
    if state.get("recommended_action") == RecommendedAction.ESCALATE:
        state["case_status"] = "ESCALATED"
    else:
        state["case_status"] = "PENDING_REVIEW"
    state["audit_trail"].append({
        **_audit("Awaiting staff review / approval of any privileged action", "human_review_gate"),
        "actor": "system", "human_review_required": True,
    })
    state["completed_steps"].append("human_review_gate")
    return state


def finalize(state: ServiceDeskState) -> ServiceDeskState:
    """
    Execute any requested workflow. Low-risk actions (file a ticket, draft a
    document) run directly. Privileged remediation (password reset, service
    restart) and financial approval are CONSEQUENTIAL: they require a verified
    human approval bound at the gateway and will NOT execute without it.
    """
    state["current_step"] = "finalize"
    claims = _claims(state)
    action = state.get("action_request") or {}
    try:
        kind = action.get("type")
        if kind == "create_ticket":
            res = gateway_tools.create_ticket(claims, action.get("payload", {}))
            if getattr(res, "allowed", False):
                state["ticket_id"] = res.result.get("ticket_id", "INC-PENDING")
        elif kind == "draft_document":
            res = gateway_tools.draft_document(claims, action.get("payload", {}))
            if getattr(res, "allowed", False):
                state["document_id"] = res.result.get("doc_id", "DOC-PENDING")
        elif kind == "reset_password":
            res = gateway_tools.reset_password(claims, action.get("payload", {}),
                                               approval=state.get("approval"))
            if getattr(res, "allowed", False):
                state["remediation_id"] = res.result.get("account", "RESET-PENDING")
        elif kind == "restart_service":
            res = gateway_tools.restart_service(claims, action.get("payload", {}),
                                                approval=state.get("approval"))
            if getattr(res, "allowed", False):
                state["remediation_id"] = res.result.get("service", "RESTART-PENDING")
        elif kind == "initiate_approval":
            res = gateway_tools.initiate_approval(claims, action.get("payload", {}),
                                                  approval=state.get("approval"))
            if getattr(res, "allowed", False):
                state["approval_id"] = res.result.get("approval_id", "APR-PENDING")
        if state.get("case_status") != "ESCALATED":
            state["case_status"] = "RESOLVED"
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "finalize", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
    state["audit_trail"].append(_audit("Finalized resolution / executed approved workflow / audit",
                                       "finalize", ["itsm"]))
    state["completed_steps"].append("finalize")
    return state
