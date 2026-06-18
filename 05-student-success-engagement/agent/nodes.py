# agent/nodes.py
# ============================================================
# Node functions for the Student Success & Engagement workflow.
#
# Each node reads what it needs from EngagementState, performs one step, writes
# its findings back, and appends an audit-trail entry. The AI assembles evidence
# and drafts a plan + outreach; the counselor owns the decision to reach out. The
# human_review gate is framework-enforced via interrupt_before in graph.py, and a
# consequential send runs only with a human approval bound at the gateway.
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

from agent.prompts import INTERVENTION_DRAFT_PROMPT, SYSTEM_PROMPT
from agent.state import EngagementState, RecommendedAction
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


def _claims(state: EngagementState) -> Dict[str, Any]:
    # Demo default: an authenticated counselor identity if none supplied.
    return state.get("acting_user_claims") or {
        "sub": "demo-counselor", "custom:edu_role": "COUNSELOR",
    }


def intake(state: EngagementState) -> EngagementState:
    state["current_step"] = "intake"
    state.setdefault("revision_count", 0)
    state.setdefault("completed_steps", [])
    state.setdefault("audit_trail", [])
    state.setdefault("trigger_event", "disengagement")
    state["case_status"] = "ASSEMBLING"
    state["audit_trail"].append(
        _audit(f"Intake of {state.get('trigger_event')} trigger", "intake"))
    state["completed_steps"].append("intake")
    return state


def assemble_evidence(state: EngagementState) -> EngagementState:
    state["current_step"] = "assemble_evidence"
    claims = _claims(state)
    sources = []
    evidence: Dict[str, Any] = {}
    try:
        evidence["risk_signals"] = gateway_tools.get_risk_signals(claims)
        sources.append("analytics")
        evidence["attendance"] = gateway_tools.get_attendance(claims)
        sources.append("sis")
        evidence["grades"] = gateway_tools.get_grades(claims)
        evidence["engagement"] = gateway_tools.get_engagement(claims)
        sources.append("lms")
        evidence["intervention_history"] = gateway_tools.get_intervention_history(claims)
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "assemble_evidence", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
    state["evidence"] = evidence
    state["audit_trail"].append(_audit("Assembled authorized risk/engagement evidence",
                                       "assemble_evidence", sources))
    state["completed_steps"].append("assemble_evidence")
    return state


def _demo_intervention(state: EngagementState) -> str:
    evidence = state.get("evidence", {}) or {}
    signals = (evidence.get("risk_signals", {}) or {}).get("signals", []) or []
    attendance = evidence.get("attendance", {}) or {}
    engagement = evidence.get("engagement", {}) or {}
    parts = [f"Trigger: {state.get('trigger_event', 'disengagement')}."]
    if signals:
        named = ", ".join(f"{s.get('type')} ({s.get('value')})" for s in signals[:3])
        parts.append(f"The authorized signals show: {named}.")
    if attendance:
        parts.append(f"Attendance is at {attendance.get('present_pct', 'n/a')}% this term.")
    if engagement:
        parts.append(f"Last LMS login was {engagement.get('last_login_days_ago', 'n/a')} days ago.")
    parts.append("Suggested supportive steps: (1) a brief check-in, (2) connect to tutoring or "
                 "office hours, (3) confirm there are no logistical barriers.")
    parts.append("Draft outreach: 'Hi — I noticed you may have a lot on your plate lately and "
                 "wanted to check in. I'm here to help connect you with support. Could we find a "
                 "few minutes this week?'")
    return " ".join(parts)


def draft_intervention(state: EngagementState) -> EngagementState:
    state["current_step"] = "draft_intervention"
    evidence = state.get("evidence", {}) or {}
    evidence_str = "\n".join(f"- {k}: {v}" for k, v in evidence.items()) or "(no evidence assembled)"
    if generate is not None:
        out = generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=INTERVENTION_DRAFT_PROMPT.format(
                channel=state.get("channel", "sis"),
                trigger=state.get("trigger_event", "disengagement"),
                evidence=evidence_str,
            ),
            demo_fn=lambda: _demo_intervention(state),
        )
        text, gen_by = out["text"], out["generated_by"]
    else:  # pragma: no cover
        text, gen_by = _demo_intervention(state), "demo-stub"
    state["draft_plan"] = text
    # The draft outreach message is the same grounded text the counselor reviews/sends.
    state["draft_message"] = text
    state["generated_by"] = gen_by
    state["audit_trail"].append(_audit("Drafted intervention plan + outreach", "draft_intervention",
                                       model=gen_by))
    state["completed_steps"].append("draft_intervention")
    return state


def checks(state: EngagementState) -> EngagementState:
    state["current_step"] = "checks"
    text = " ".join([state.get("draft_plan", ""), state.get("draft_message", "")])
    # PPRA guard: the agent must not infer or condition on protected categories.
    protected = ("race", "ethnicity", "religion", "religious", "disability", "disabled",
                 "national origin", "immigration", "sexual orientation", "income level",
                 "family income", "political")
    findings = [f"protected-category reference: {p}" for p in protected if p in text.lower()]
    state["compliance_findings"] = findings

    if verify_grounding is not None:
        report = verify_grounding(text, dict(state)).to_audit_dict()
    else:  # pragma: no cover
        report = {"grounded": True, "ungrounded_numbers": [], "ungrounded_entities": []}
    state["grounding_report"] = report

    # Fairness note: only when aggregate base/selected rates are supplied in state.
    fairness_report: Dict[str, Any] = {}
    base_rates = state.get("base_rates")
    selected_rates = state.get("selected_rates")
    if base_rates and selected_rates:
        try:  # defensive: governance.fairness is optional in standalone demo
            from governance.fairness import representativeness_flag

            rep = representativeness_flag(base_rates, selected_rates)
            fairness_report = {
                "equitable": rep.equitable,
                "flagged_groups": rep.flagged_groups,
                "detail": rep.detail,
                "tolerance": rep.tolerance,
            }
        except Exception as exc:  # pragma: no cover - resilience path
            fairness_report = {"skipped": True, "reason": str(exc)}
    else:
        fairness_report = {"skipped": True, "reason": "no aggregate rates supplied"}
    state["fairness_report"] = fairness_report

    ungrounded = report.get("ungrounded_numbers", []) + report.get("ungrounded_entities", [])
    fairness_flagged = bool(fairness_report.get("flagged_groups"))
    if findings or fairness_flagged:
        state["recommended_action"] = RecommendedAction.ESCALATE
    elif ungrounded and state.get("revision_count", 0) < 1:
        state["recommended_action"] = RecommendedAction.REVISE
        state["revision_count"] = state.get("revision_count", 0) + 1
    else:
        state["recommended_action"] = RecommendedAction.PROCEED

    state["audit_trail"].append(_audit("Ran grounding + PPRA + fairness checks", "checks"))
    state["completed_steps"].append("checks")
    return state


def routing_decision(state: EngagementState) -> str:
    if state.get("recommended_action") == RecommendedAction.REVISE:
        return "draft_intervention"
    return "human_review_gate"


def human_review_gate(state: EngagementState) -> EngagementState:
    """HITL pause point. graph compiles with interrupt_before=[human_review_gate]."""
    state["current_step"] = "human_review_gate"
    if state.get("recommended_action") == RecommendedAction.ESCALATE:
        state["case_status"] = "ESCALATED"
    else:
        state["case_status"] = "PENDING_REVIEW"
    state["audit_trail"].append({
        **_audit("Awaiting counselor review / approval of any outreach", "human_review_gate"),
        "actor": "system", "human_review_required": True,
    })
    state["completed_steps"].append("human_review_gate")
    return state


def finalize(state: EngagementState) -> EngagementState:
    """
    Execute any requested workflow. Opening an advising case is low-risk and runs
    directly. A consequential outreach send requires a verified counselor approval
    bound at the gateway; without it, no message is sent. The agent never sends
    outreach autonomously.
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
    state["audit_trail"].append(_audit("Finalized plan / executed approved workflow",
                                       "finalize", ["crm"]))
    state["completed_steps"].append("finalize")
    return state
