# agent/nodes.py
# ============================================================
# Node functions for the Student & Family Services Concierge workflow.
#
# Each node reads what it needs from ConciergeState, performs one step, writes its
# findings back, and appends an audit-trail entry. The AI answers and assembles;
# staff own consequential decisions. The human_review gate is framework-enforced
# via interrupt_before in graph.py.
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

from agent.prompts import CONCIERGE_ANSWER_PROMPT, SYSTEM_PROMPT
from agent.state import ConciergeState, RecommendedAction
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


def _claims(state: ConciergeState) -> Dict[str, Any]:
    # Demo default: an authenticated student identity if none supplied.
    return state.get("acting_user_claims") or {
        "sub": "demo-student", "custom:edu_role": "STUDENT",
    }


def intake(state: ConciergeState) -> ConciergeState:
    state["current_step"] = "intake"
    state.setdefault("revision_count", 0)
    state.setdefault("completed_steps", [])
    state.setdefault("audit_trail", [])
    state.setdefault("intent", "INFO")
    state["case_status"] = "ANSWERING"
    state["audit_trail"].append(_audit(f"Intake of {state.get('intent')} request", "intake"))
    state["completed_steps"].append("intake")
    return state


def retrieve(state: ConciergeState) -> ConciergeState:
    state["current_step"] = "retrieve"
    claims = _claims(state)
    sources = []
    try:
        state["policy_hits"] = gateway_tools.search_policies(claims, state.get("question", ""))
        sources.append("kb")
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "retrieve", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
        state.setdefault("policy_hits", [])
    # Authenticated status retrieval only when the user is authenticated and asking status.
    if state.get("authenticated") and state.get("intent") == "STATUS":
        try:
            state["status_result"] = gateway_tools.check_application_status(claims)
            sources.append("sis")
        except Exception:
            state.setdefault("status_result", {})
    state["audit_trail"].append(_audit("Retrieved approved content / status", "retrieve", sources))
    state["completed_steps"].append("retrieve")
    return state


def _demo_answer(state: ConciergeState) -> str:
    hits = state.get("policy_hits", []) or []
    status = state.get("status_result", {}) or {}
    parts = []
    if hits:
        titles = ", ".join(h.get("title", "a policy") for h in hits[:2])
        parts.append(f"Based on the institution's published guidance ({titles}), here is what applies to your question.")
    else:
        parts.append("I could not find a published answer to that, so I will connect you to the right staff member.")
    if status:
        miss = status.get("missing") or []
        if miss:
            parts.append(f"Your application status is '{status.get('status','')}'. Still needed: {', '.join(miss)}.")
        explanation = status.get("explanation")
        if explanation:
            parts.append(explanation)
    parts.append("If you'd like, I can open a case or schedule an appointment with the right office.")
    return " ".join(parts)


def draft_response(state: ConciergeState) -> ConciergeState:
    state["current_step"] = "draft_response"
    policy = "\n".join(f"- {h.get('title','')} ({h.get('ref','')})" for h in state.get("policy_hits", []) or [])
    status = state.get("status_result", {}) or {}
    if generate is not None:
        out = generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=CONCIERGE_ANSWER_PROMPT.format(
                channel=state.get("channel", "web"),
                question=state.get("question", ""),
                policy=policy or "(none found)",
                status=status or "(not applicable)",
            ),
            demo_fn=lambda: _demo_answer(state),
        )
        state["draft_response"], state["generated_by"] = out["text"], out["generated_by"]
    else:  # pragma: no cover
        state["draft_response"], state["generated_by"] = _demo_answer(state), "demo-stub"
    state["audit_trail"].append(_audit("Drafted grounded response", "draft_response",
                                       model=state["generated_by"]))
    state["completed_steps"].append("draft_response")
    return state


def checks(state: ConciergeState) -> ConciergeState:
    state["current_step"] = "checks"
    text = state.get("draft_response", "")
    # Compliance: the concierge must never state a consequential decision.
    prohibited = ("you are admitted", "you are denied", "your aid is approved",
                  "your aid is denied", "you are expelled", "you are suspended")
    findings = [f"prohibited determination phrasing: {p}" for p in prohibited if p in text.lower()]
    state["compliance_findings"] = findings

    if verify_grounding is not None:
        report = verify_grounding(text, dict(state)).to_audit_dict()
    else:  # pragma: no cover
        report = {"grounded": True, "ungrounded_numbers": [], "ungrounded_entities": []}
    state["grounding_report"] = report

    ungrounded = report.get("ungrounded_numbers", []) + report.get("ungrounded_entities", [])
    if findings:
        state["recommended_action"] = RecommendedAction.ESCALATE
    elif ungrounded and state.get("revision_count", 0) < 1:
        state["recommended_action"] = RecommendedAction.REVISE
        state["revision_count"] = state.get("revision_count", 0) + 1
    else:
        state["recommended_action"] = RecommendedAction.ANSWER

    state["audit_trail"].append(_audit("Ran grounding + compliance checks", "checks"))
    state["completed_steps"].append("checks")
    return state


# Outbound actions that are consequential and therefore require a human gate. Low-risk
# workflows (open an advising case, schedule an appointment) are authorized by the
# gateway and audited, but do not require a staff approval pause.
_CONSEQUENTIAL_ACTION_TYPES = {"send_message"}


def routing_decision(state: ConciergeState) -> str:
    if state.get("recommended_action") == RecommendedAction.REVISE:
        return "draft_response"          # bounded redraft
    if state.get("recommended_action") == RecommendedAction.ESCALATE:
        return "human_review_gate"       # sensitive / out-of-scope -> staff
    # Clean ANSWER: gate ONLY when a consequential outbound action is requested.
    # A pure read-only answer (and low-risk workflows) goes straight to finalize —
    # the gateway still authorizes and audits it; over-gating routine reads is not
    # required and is the behavior a reviewer flagged.
    action = state.get("action_request") or {}
    if action.get("type") in _CONSEQUENTIAL_ACTION_TYPES:
        return "human_review_gate"
    return "finalize"


def human_review_gate(state: ConciergeState) -> ConciergeState:
    """HITL pause point. graph compiles with interrupt_before=[human_review_gate]."""
    state["current_step"] = "human_review_gate"
    if state.get("recommended_action") == RecommendedAction.ESCALATE:
        state["case_status"] = "ESCALATED"
    else:
        state["case_status"] = "PENDING_REVIEW"
    state["audit_trail"].append({
        **_audit("Awaiting staff review / approval of any consequential action", "human_review_gate"),
        "actor": "system", "human_review_required": True,
    })
    state["completed_steps"].append("human_review_gate")
    return state


def finalize(state: ConciergeState) -> ConciergeState:
    """
    Execute any requested workflow. Low-risk actions (open a case, schedule an
    appointment) run directly. A consequential outbound message requires a
    verified human approval bound at the gateway; without it, it stays pending.
    """
    state["current_step"] = "finalize"
    claims = _claims(state)
    action = state.get("action_request") or {}
    try:
        kind = action.get("type")
        if kind == "create_advising_case":
            res = gateway_tools.create_advising_case(claims, action.get("payload", {}))
            if getattr(res, "allowed", False):
                state["case_id"] = res.result.get("case_id", "CASE-PENDING")
        elif kind == "schedule_appointment":
            res = gateway_tools.schedule_appointment(claims, action.get("payload", {}))
            if getattr(res, "allowed", False):
                state["appointment_id"] = res.result.get("appointment_id", "APPT-PENDING")
        elif kind == "send_message":
            res = gateway_tools.send_message(claims, action.get("payload", {}),
                                             approval=state.get("approval"))
            if getattr(res, "allowed", False):
                state["message_id"] = res.result.get("message_id", "MSG-PENDING")
        if state.get("case_status") != "ESCALATED":
            state["case_status"] = "RESOLVED"
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "finalize", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
    state["audit_trail"].append(_audit("Finalized response / executed approved workflow",
                                       "finalize", ["crm"]))
    state["completed_steps"].append("finalize")
    return state
