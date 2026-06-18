# agent/nodes.py
# ============================================================
# Node functions for the Educator Copilot workflow.
#
# Each node reads what it needs from CopilotState, performs one step, writes its
# findings back, and appends an audit-trail entry. The AI drafts instructional
# artifacts and places them as DRAFTS in the LMS; the educator owns publication.
# Consequential actions (publish_content, update_assignment_due_date) execute only
# with a verified approval bound at the gateway. The human_review gate is framework-
# enforced via interrupt_before in graph.py.
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

from agent.prompts import ARTIFACT_DRAFT_PROMPT, SYSTEM_PROMPT
from agent.state import CopilotState, RecommendedAction
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


def _claims(state: CopilotState) -> Dict[str, Any]:
    # Demo default: an authenticated educator identity if none supplied.
    return state.get("acting_user_claims") or {
        "sub": "demo-educator", "custom:edu_role": "EDUCATOR",
    }


# Maps each artifact_type to the low-risk LMS draft tool that places it.
_DRAFT_TOOL = {
    "lesson": "create_assignment_draft",
    "quiz": "create_assignment_draft",
    "differentiation": "create_assignment_draft",
    "rubric": "create_rubric_draft",
    "announcement": "post_announcement_draft",
}


def intake(state: CopilotState) -> CopilotState:
    state["current_step"] = "intake"
    state.setdefault("revision_count", 0)
    state.setdefault("completed_steps", [])
    state.setdefault("audit_trail", [])
    state.setdefault("artifact_type", "lesson")
    state.setdefault("published", False)
    state["case_status"] = "DRAFTING"
    state["audit_trail"].append(_audit(f"Intake of {state.get('artifact_type')} draft request", "intake"))
    state["completed_steps"].append("intake")
    return state


def retrieve(state: CopilotState) -> CopilotState:
    state["current_step"] = "retrieve"
    claims = _claims(state)
    course = state.get("course", "")
    sources = []
    try:
        state["curriculum_hits"] = gateway_tools.search_course_material(claims, state.get("instructions", ""))
        sources.append("kb")
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "retrieve", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
        state.setdefault("curriculum_hits", [])
    try:
        content = gateway_tools.get_course_content(claims, course)
        if content:
            for mod in content.get("modules", []) or []:
                state.setdefault("curriculum_hits", []).append(
                    {"course": content.get("course", course),
                     "title": mod.get("title", ""), "ref": mod.get("id", "")}
                )
            sources.append("lms")
    except Exception:
        state.setdefault("curriculum_hits", [])
    try:
        state["roster"] = gateway_tools.get_roster(claims, course)
        if state["roster"]:
            sources.append("lms")
    except Exception:
        state.setdefault("roster", {})
    # Recent class results inform differentiation.
    try:
        engagement = gateway_tools.get_engagement(claims, course)
        missing = gateway_tools.identify_missing_submissions(claims, course)
        state["class_results"] = {"engagement": engagement, "missing_submissions": missing}
        if engagement or missing:
            sources.append("lms")
    except Exception:
        state.setdefault("class_results", {})
    state["audit_trail"].append(_audit("Retrieved approved curriculum / roster / class results",
                                       "retrieve", sources))
    state["completed_steps"].append("retrieve")
    return state


def _demo_artifact(state: CopilotState) -> str:
    hits = state.get("curriculum_hits", []) or []
    artifact_type = state.get("artifact_type", "lesson")
    results = state.get("class_results", {}) or {}
    parts = [f"DRAFT {artifact_type} for educator review."]
    if hits:
        titles = ", ".join(h.get("title", "the curriculum") for h in hits[:2])
        parts.append(f"Grounded in the approved curriculum ({titles}).")
    else:
        parts.append("No approved curriculum was found; this outline needs the educator to attach source material.")
    if state.get("instructions"):
        parts.append(f"Addressing the request: {state.get('instructions')}.")
    if results.get("missing_submissions") or results.get("engagement"):
        parts.append("Includes differentiation: supports for students who are behind and an extension for those ahead.")
    parts.append("Student-facing text uses clear headings and plain language (WCAG 2.2 AA); add alt-text for any image.")
    return " ".join(parts)


def draft_artifact(state: CopilotState) -> CopilotState:
    state["current_step"] = "draft_artifact"
    curriculum = "\n".join(f"- {h.get('title','')} ({h.get('ref','')})" for h in state.get("curriculum_hits", []) or [])
    results = state.get("class_results", {}) or {}
    if generate is not None:
        out = generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=ARTIFACT_DRAFT_PROMPT.format(
                artifact_type=state.get("artifact_type", "lesson"),
                course=state.get("course", ""),
                instructions=state.get("instructions", ""),
                curriculum=curriculum or "(none found)",
                class_results=results or "(none)",
            ),
            demo_fn=lambda: _demo_artifact(state),
        )
        state["draft_artifact"], state["generated_by"] = out["text"], out["generated_by"]
    else:  # pragma: no cover
        state["draft_artifact"], state["generated_by"] = _demo_artifact(state), "demo-stub"
    state["audit_trail"].append(_audit("Drafted grounded instructional artifact", "draft_artifact",
                                       model=state["generated_by"]))
    state["completed_steps"].append("draft_artifact")
    return state


def checks(state: CopilotState) -> CopilotState:
    state["current_step"] = "checks"
    text = state.get("draft_artifact", "")

    # Compliance: student-facing artifacts must meet WCAG 2.2 AA. Flag (advisory)
    # when the draft omits the accessibility cues a reviewer should confirm.
    findings = []
    student_facing = state.get("artifact_type") in ("lesson", "quiz", "announcement", "differentiation")
    if student_facing and "wcag" not in text.lower() and "accessib" not in text.lower():
        findings.append("accessibility: confirm student-facing output meets WCAG 2.2 AA before publishing")
    state["compliance_findings"] = findings

    if verify_grounding is not None:
        report = verify_grounding(text, dict(state)).to_audit_dict()
    else:  # pragma: no cover
        report = {"grounded": True, "ungrounded_numbers": [], "ungrounded_entities": []}
    state["grounding_report"] = report

    ungrounded = report.get("ungrounded_numbers", []) + report.get("ungrounded_entities", [])
    if ungrounded and state.get("revision_count", 0) < 1:
        state["recommended_action"] = RecommendedAction.REVISE
        state["revision_count"] = state.get("revision_count", 0) + 1
    else:
        state["recommended_action"] = RecommendedAction.APPROVE_DRAFT

    state["audit_trail"].append(_audit("Ran grounding + accessibility checks", "checks"))
    state["completed_steps"].append("checks")
    return state


def routing_decision(state: CopilotState) -> str:
    if state.get("recommended_action") == RecommendedAction.REVISE:
        return "draft_artifact"
    return "human_review_gate"


def human_review_gate(state: CopilotState) -> CopilotState:
    """HITL pause point. graph compiles with interrupt_before=[human_review_gate].

    Educator approval before anything is published. The draft can be created without
    a gate, but publish_content / update_assignment_due_date require approval bound
    at the gateway and only run after the educator resumes the graph.
    """
    state["current_step"] = "human_review_gate"
    if state.get("recommended_action") == RecommendedAction.ESCALATE:
        state["case_status"] = "ESCALATED"
    else:
        state["case_status"] = "PENDING_REVIEW"
    state["audit_trail"].append({
        **_audit("Awaiting educator review / approval before any publish", "human_review_gate"),
        "actor": "system", "human_review_required": True,
    })
    state["completed_steps"].append("human_review_gate")
    return state


def finalize(state: CopilotState) -> CopilotState:
    """
    Place the artifact in the LMS as a DRAFT via the low-risk tool. Any consequential
    action (publish_content, update_assignment_due_date) runs ONLY with a verified
    approval bound at the gateway; without it, the gateway does not execute and the
    content stays unpublished.
    """
    state["current_step"] = "finalize"
    claims = _claims(state)
    artifact_type = state.get("artifact_type", "lesson")

    # 1) Low-risk: create the LMS draft (no approval gate).
    try:
        tool_name = _DRAFT_TOOL.get(artifact_type, "create_assignment_draft")
        tool = getattr(gateway_tools, tool_name)
        res = tool(claims, {"artifact_type": artifact_type, "course": state.get("course", "")})
        if getattr(res, "allowed", False):
            result = res.result or {}
            state["draft_id"] = (result.get("assignment_id") or result.get("rubric_id")
                                 or result.get("announcement_id") or "DRAFT-PENDING")
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "finalize", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})

    # 2) Consequential: only with a verified approval bound at the gateway.
    action = state.get("action_request") or {}
    try:
        kind = action.get("type")
        if kind == "update_assignment_due_date":
            res = gateway_tools.update_assignment_due_date(claims, action.get("payload", {}),
                                                           approval=state.get("approval"))
            if getattr(res, "allowed", False):
                state["published"] = True
        elif kind == "publish_content":
            res = gateway_tools.publish_content(claims, action.get("payload", {}),
                                                approval=state.get("approval"))
            if getattr(res, "allowed", False):
                state["published"] = bool((res.result or {}).get("published"))
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "finalize", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})

    if state.get("case_status") != "ESCALATED":
        state["case_status"] = "RESOLVED"
    state["audit_trail"].append(_audit("Created LMS draft; executed approved actions only",
                                       "finalize", ["lms"]))
    state["completed_steps"].append("finalize")
    return state
