# agent/nodes.py
# ============================================================
# Node functions for the Pathway Navigator workflow.
#
# Each node reads what it needs from PathwayState, performs one step, writes its
# findings back, and appends an audit-trail entry. The AI assembles grounded
# options from deterministic degree rules; a human counselor owns placement. The
# human_review gate is framework-enforced via interrupt_before in graph.py.
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

from agent.prompts import PATHWAY_PLAN_PROMPT, SYSTEM_PROMPT
from agent.state import PathwayState, RecommendedAction
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


def _claims(state: PathwayState) -> Dict[str, Any]:
    # Demo default: an authenticated student identity if none supplied.
    return state.get("acting_user_claims") or {
        "sub": "demo-student", "custom:edu_role": "STUDENT",
    }


def intake(state: PathwayState) -> PathwayState:
    state["current_step"] = "intake"
    state.setdefault("revision_count", 0)
    state.setdefault("completed_steps", [])
    state.setdefault("audit_trail", [])
    state.setdefault("goal", "plan")
    state["case_status"] = "PLANNING"
    state["audit_trail"].append(_audit(f"Intake of {state.get('goal')} planning request", "intake"))
    state["completed_steps"].append("intake")
    return state


def retrieve(state: PathwayState) -> PathwayState:
    state["current_step"] = "retrieve"
    claims = _claims(state)
    sources = []
    try:
        state["profile"] = gateway_tools.get_student_profile(claims)
        sources.append("sis")
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "retrieve", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
        state.setdefault("profile", {})
    try:
        state["grad_requirements"] = gateway_tools.get_graduation_requirements(claims)
        if "sis" not in sources:
            sources.append("sis")
    except Exception:
        state.setdefault("grad_requirements", {})
    # Transfer-credit mapping only when the goal involves transfer (or planning).
    if state.get("goal") in ("transfer", "plan", "graduation"):
        try:
            state["transfer_credits"] = gateway_tools.get_transfer_credits(claims)
        except Exception:
            state.setdefault("transfer_credits", {})
    # Career-pathway exploration only when the goal is career.
    if state.get("goal") == "career":
        try:
            state["career_pathways"] = gateway_tools.get_career_pathways(claims, state.get("question", ""))
            sources.append("labor")
        except Exception:
            state.setdefault("career_pathways", {})
    try:
        state["policy_hits"] = gateway_tools.search_policies(claims, state.get("question", ""))
        sources.append("kb")
    except Exception:
        state.setdefault("policy_hits", [])
    state["audit_trail"].append(_audit("Retrieved profile / requirements / transfer / content", "retrieve", sources))
    state["completed_steps"].append("retrieve")
    return state


def run_rules(state: PathwayState) -> PathwayState:
    """Deterministic degree rules — the authoritative completion + eligibility facts."""
    state["current_step"] = "run_rules"
    claims = _claims(state)
    try:
        state["degree_audit"] = gateway_tools.run_degree_audit(claims, state.get("profile", {}))
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "run_rules", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
        state.setdefault("degree_audit", {})
    try:
        state["prereq_check"] = gateway_tools.check_prerequisites(claims, state.get("question", ""))
    except Exception:
        state.setdefault("prereq_check", {})
    state["audit_trail"].append(_audit("Ran deterministic degree audit + prerequisite check", "run_rules", ["rules"]))
    state["completed_steps"].append("run_rules")
    return state


def _demo_plan(state: PathwayState) -> str:
    audit = state.get("degree_audit", {}) or {}
    prereq = state.get("prereq_check", {}) or {}
    transfer = state.get("transfer_credits", {}) or {}
    career = state.get("career_pathways", {}) or {}
    parts = []
    if audit:
        remaining = ", ".join(audit.get("remaining_requirements", []) or [])
        parts.append(f"OPTION: Per the degree audit, your plan is {audit.get('complete_pct','')}% complete; "
                     f"remaining requirements are {remaining or 'none listed'}.")
    else:
        parts.append("I could not run a degree audit, so I will connect you to a counselor.")
    if prereq:
        if prereq.get("eligible") is False:
            miss = ", ".join(prereq.get("missing_prereq", []) or [])
            parts.append(f"RECOMMENDATION: {prereq.get('course','That course')} is not yet open to you "
                         f"(missing prerequisite: {miss}). Plan that step first.")
        elif prereq.get("eligible") is True:
            parts.append(f"RECOMMENDATION: You meet the prerequisites for {prereq.get('course','that course')}.")
    if transfer.get("accepted"):
        acc = ", ".join(f"{c.get('course')} ({c.get('credits')} cr)" for c in transfer.get("accepted", []))
        parts.append(f"OPTION: Accepted transfer credits include {acc}.")
    if career.get("pathways"):
        p = career["pathways"][0]
        parts.append(f"OPTION: A pathway to consider is {p.get('credential')} "
                     f"(next steps: {', '.join(p.get('next_steps', []))}).")
    parts.append("Nothing here is an APPROVED PLAN until a counselor signs off. "
                 "I can schedule time with a counselor to review and approve placement.")
    return " ".join(parts)


def draft_plan(state: PathwayState) -> PathwayState:
    state["current_step"] = "draft_plan"
    policy = "\n".join(f"- {h.get('title','')} ({h.get('ref','')})" for h in state.get("policy_hits", []) or [])
    if generate is not None:
        out = generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=PATHWAY_PLAN_PROMPT.format(
                channel=state.get("channel", "web"),
                goal=state.get("goal", "plan"),
                question=state.get("question", ""),
                degree_audit=state.get("degree_audit", {}) or "(none)",
                prereq_check=state.get("prereq_check", {}) or "(none)",
                transfer_credits=state.get("transfer_credits", {}) or "(not applicable)",
                career_pathways=state.get("career_pathways", {}) or "(not applicable)",
                policy=policy or "(none found)",
            ),
            demo_fn=lambda: _demo_plan(state),
        )
        state["draft_plan"], state["generated_by"] = out["text"], out["generated_by"]
    else:  # pragma: no cover
        state["draft_plan"], state["generated_by"] = _demo_plan(state), "demo-stub"
    state["audit_trail"].append(_audit("Drafted grounded planning summary", "draft_plan",
                                       model=state["generated_by"]))
    state["completed_steps"].append("draft_plan")
    return state


def checks(state: PathwayState) -> PathwayState:
    state["current_step"] = "checks"
    text = state.get("draft_plan", "")
    # Compliance: the navigator must never assert a placement / eligibility decision.
    prohibited = ("you are placed", "you have been placed", "you are admitted",
                  "you are enrolled in", "you are ineligible to graduate",
                  "you are cleared to graduate", "your placement is")
    findings = [f"prohibited placement phrasing: {p}" for p in prohibited if p in text.lower()]
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

    state["audit_trail"].append(_audit("Ran grounding + placement-guard checks", "checks"))
    state["completed_steps"].append("checks")
    return state


def routing_decision(state: PathwayState) -> str:
    if state.get("recommended_action") == RecommendedAction.REVISE:
        return "draft_plan"
    return "human_review_gate"


def human_review_gate(state: PathwayState) -> PathwayState:
    """HITL pause point. graph compiles with interrupt_before=[human_review_gate].

    Placement is a human counselor's decision; the AI only assembles grounded
    options and recommendations for the counselor to approve.
    """
    state["current_step"] = "human_review_gate"
    if state.get("recommended_action") == RecommendedAction.ESCALATE:
        state["case_status"] = "ESCALATED"
    else:
        state["case_status"] = "PENDING_REVIEW"
    state["audit_trail"].append({
        **_audit("Awaiting counselor review / placement decision", "human_review_gate"),
        "actor": "system", "human_review_required": True,
    })
    state["completed_steps"].append("human_review_gate")
    return state


def finalize(state: PathwayState) -> PathwayState:
    """
    Execute any requested workflow. Scheduling a counselor appointment is a
    LOW-RISK workflow and runs directly; the navigator never executes a
    placement, which remains the counselor's human decision.
    """
    state["current_step"] = "finalize"
    claims = _claims(state)
    action = state.get("action_request") or {}
    try:
        kind = action.get("type")
        if kind == "schedule_appointment":
            res = gateway_tools.schedule_appointment(claims, action.get("payload", {}))
            if getattr(res, "allowed", False):
                state["appointment_id"] = res.result.get("appointment_id", "APPT-PENDING")
        if state.get("case_status") != "ESCALATED":
            state["case_status"] = "RESOLVED"
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "finalize", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
    state["audit_trail"].append(_audit("Finalized plan / scheduled counselor (low-risk) / audit",
                                       "finalize", ["crm"]))
    state["completed_steps"].append("finalize")
    return state
