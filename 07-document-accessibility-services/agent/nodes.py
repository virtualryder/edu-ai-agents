# agent/nodes.py
# ============================================================
# Node functions for the Document & Accessibility Services workflow.
#
# Each node reads what it needs from DocAccessState, performs one step, writes its
# findings back, and appends an audit-trail entry. The AI classifies, extracts,
# validates, and drafts; a human verifies and owns the consequential enrollment
# write. The human_review gate is framework-enforced via interrupt_before in
# graph.py, and the SIS write does not execute without a verified approval.
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

from agent.prompts import DOC_DRAFT_PROMPT, SYSTEM_PROMPT
from agent.state import DocAccessState, RecommendedAction
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


def _claims(state: DocAccessState) -> Dict[str, Any]:
    # Demo default: an authenticated enrollment-staff identity if none supplied.
    return state.get("acting_user_claims") or {
        "sub": "demo-staff", "custom:edu_role": "ENROLLMENT_STAFF",
    }


def intake(state: DocAccessState) -> DocAccessState:
    state["current_step"] = "intake"
    state.setdefault("revision_count", 0)
    state.setdefault("completed_steps", [])
    state.setdefault("audit_trail", [])
    state.setdefault("mode", "enrollment")
    state["case_status"] = "PROCESSING"
    state["audit_trail"].append(_audit(f"Intake of {state.get('mode')} document request", "intake"))
    state["completed_steps"].append("intake")
    return state


def classify_extract(state: DocAccessState) -> DocAccessState:
    """
    Enrollment mode: classify + extract fields (capturing low-confidence fields).
    Accessibility mode: transform to accessible + translate the content.
    """
    state["current_step"] = "classify_extract"
    claims = _claims(state)
    sources = []
    if state.get("mode") == "accessibility":
        try:
            state["accessible_artifacts"] = gateway_tools.transform_and_translate(
                claims, state.get("document_ref", ""), state.get("target_language", "es"))
            sources.append("docpipe")
        except Exception as exc:
            state.setdefault("errors", []).append({"step": "classify_extract", "error": str(exc),
                                                   "timestamp": _now(), "recoverable": True})
            state.setdefault("accessible_artifacts", {})
    else:  # enrollment
        try:
            cls = gateway_tools.classify_document(claims, state.get("document_ref", ""))
            state["doc_type"] = cls.get("doc_type", "")
            sources.append("docpipe")
        except Exception as exc:
            state.setdefault("errors", []).append({"step": "classify_extract", "error": str(exc),
                                                   "timestamp": _now(), "recoverable": True})
            state.setdefault("doc_type", "")
        try:
            ext = gateway_tools.extract_fields(claims, state.get("document_ref", ""))
            state["extracted_fields"] = ext.get("fields", {})
            state["low_confidence_fields"] = ext.get("low_confidence_fields", [])
        except Exception:
            state.setdefault("extracted_fields", {})
            state.setdefault("low_confidence_fields", [])
    state["audit_trail"].append(_audit("Classified / extracted or transformed document", "classify_extract", sources))
    state["completed_steps"].append("classify_extract")
    return state


def validate(state: DocAccessState) -> DocAccessState:
    """Enrollment mode: validate completeness and list missing items."""
    state["current_step"] = "validate"
    claims = _claims(state)
    if state.get("mode") != "accessibility":
        try:
            state["completeness"] = gateway_tools.validate_completeness(claims, state.get("document_ref", ""))
        except Exception as exc:
            state.setdefault("errors", []).append({"step": "validate", "error": str(exc),
                                                   "timestamp": _now(), "recoverable": True})
            state.setdefault("completeness", {})
    else:
        state.setdefault("completeness", {})
    state["audit_trail"].append(_audit("Validated document completeness", "validate", ["docpipe"]))
    state["completed_steps"].append("validate")
    return state


def _demo_draft(state: DocAccessState) -> str:
    parts = []
    if state.get("mode") == "accessibility":
        art = state.get("accessible_artifacts", {}) or {}
        outs = ", ".join(art.get("outputs", []) or [])
        parts.append(f"Accessibility outputs prepared: {outs or 'none listed'} "
                     f"(status: {art.get('status','DRAFT')}).")
        if art.get("language"):
            parts.append(f"A translation into '{art.get('language')}' was drafted.")
        parts.append("These are drafts: a human must verify accuracy and accessibility before release.")
        return " ".join(parts)
    # enrollment mode
    fields = state.get("extracted_fields", {}) or {}
    if fields:
        shown = ", ".join(f"{k}: {v}" for k, v in list(fields.items())[:3])
        parts.append(f"Thank you — we received your {state.get('doc_type','document')} and recorded {shown}.")
    else:
        parts.append("Thank you for your submission.")
    completeness = state.get("completeness", {}) or {}
    missing = completeness.get("missing", []) or []
    if missing:
        parts.append(f"To continue, please provide the following missing item(s): {', '.join(missing)}.")
    low = state.get("low_confidence_fields", []) or []
    if low:
        parts.append(f"Some fields ({', '.join(low)}) need staff verification before we update your record.")
    parts.append("No admissions decision is made here; staff will review and decide.")
    return " ".join(parts)


def draft(state: DocAccessState) -> DocAccessState:
    state["current_step"] = "draft"
    if generate is not None:
        out = generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=DOC_DRAFT_PROMPT.format(
                mode=state.get("mode", "enrollment"),
                channel=state.get("channel", "portal"),
                doc_type=state.get("doc_type", "") or "(not classified)",
                extracted_fields=state.get("extracted_fields", {}) or "(none)",
                low_confidence_fields=state.get("low_confidence_fields", []) or "(none)",
                completeness=state.get("completeness", {}) or "(not applicable)",
                accessible_artifacts=state.get("accessible_artifacts", {}) or "(not applicable)",
            ),
            demo_fn=lambda: _demo_draft(state),
        )
        state["draft_message"], state["generated_by"] = out["text"], out["generated_by"]
    else:  # pragma: no cover
        state["draft_message"], state["generated_by"] = _demo_draft(state), "demo-stub"
    state["audit_trail"].append(_audit("Drafted missing-items request / artifact summary", "draft",
                                       model=state["generated_by"]))
    state["completed_steps"].append("draft")
    return state


def checks(state: DocAccessState) -> DocAccessState:
    state["current_step"] = "checks"
    text = state.get("draft_message", "")
    # Compliance: never assert an admissions/eligibility decision in the draft.
    prohibited = ("you are admitted", "you are denied", "your application is approved",
                  "your application is denied", "you are accepted", "you are rejected")
    findings = [f"prohibited determination phrasing: {p}" for p in prohibited if p in text.lower()]
    state["compliance_findings"] = findings

    if verify_grounding is not None:
        report = verify_grounding(text, dict(state)).to_audit_dict()
    else:  # pragma: no cover
        report = {"grounded": True, "ungrounded_numbers": [], "ungrounded_entities": []}
    state["grounding_report"] = report

    # CONFIDENCE / SENSITIVITY rule: uncertain fields, incomplete docs, or
    # individualized/legal material always require human verification (ESCALATE).
    low_conf = state.get("low_confidence_fields", []) or []
    incomplete = (state.get("completeness", {}) or {}).get("complete") is False
    sensitive_types = ("individualized_education_program", "iep", "504_plan",
                       "legal_notice", "subpoena", "504")
    is_sensitive = (state.get("doc_type", "") or "").lower() in sensitive_types

    ungrounded = report.get("ungrounded_numbers", []) + report.get("ungrounded_entities", [])
    if findings:
        state["recommended_action"] = RecommendedAction.ESCALATE
    elif low_conf or incomplete or is_sensitive:
        state["recommended_action"] = RecommendedAction.ESCALATE
    elif ungrounded and state.get("revision_count", 0) < 1:
        state["recommended_action"] = RecommendedAction.REVISE
        state["revision_count"] = state.get("revision_count", 0) + 1
    else:
        state["recommended_action"] = RecommendedAction.ANSWER

    state["audit_trail"].append(_audit("Ran grounding + confidence/sensitivity checks", "checks"))
    state["completed_steps"].append("checks")
    return state


def routing_decision(state: DocAccessState) -> str:
    if state.get("recommended_action") == RecommendedAction.REVISE:
        return "draft"
    return "human_review_gate"


def human_review_gate(state: DocAccessState) -> DocAccessState:
    """HITL pause point. graph compiles with interrupt_before=[human_review_gate].

    A human verifies extracted data and approves any consequential enrollment
    write; individualized/legal material always requires human verification.
    """
    state["current_step"] = "human_review_gate"
    if state.get("recommended_action") == RecommendedAction.ESCALATE:
        state["case_status"] = "ESCALATED"
    else:
        state["case_status"] = "PENDING_REVIEW"
    state["audit_trail"].append({
        **_audit("Awaiting staff verification / approval of enrollment update", "human_review_gate"),
        "actor": "system", "human_review_required": True,
    })
    state["completed_steps"].append("human_review_gate")
    return state


def finalize(state: DocAccessState) -> DocAccessState:
    """
    Execute any requested workflow. The enrollment-record update is CONSEQUENTIAL:
    it requires a verified human approval bound at the gateway and will NOT execute
    without it — otherwise the update is prepared and missing items are requested.
    """
    state["current_step"] = "finalize"
    claims = _claims(state)
    action = state.get("action_request") or {}
    try:
        kind = action.get("type")
        if kind == "update_enrollment_record":
            res = gateway_tools.update_enrollment_record(claims, action.get("payload", {}),
                                                         approval=state.get("approval"))
            if getattr(res, "allowed", False):
                state["enrollment_record_id"] = res.result.get("record_id", "ENR-PENDING")
        if state.get("case_status") != "ESCALATED":
            state["case_status"] = "RESOLVED"
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "finalize", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
    state["audit_trail"].append(_audit("Finalized draft / committed approved enrollment update / audit",
                                       "finalize", ["sis"]))
    state["completed_steps"].append("finalize")
    return state
