# agent/nodes.py
# ============================================================
# Node functions for the Tutor & Study Companion workflow.
#
# Each node reads what it needs from TutorState, performs one step, writes its
# findings back, and appends an audit-trail entry. The AI tutors with hints and
# explanations grounded in instructor-approved material; a request to complete a
# graded/prohibited assessment is escalated, not answered. The human_review gate
# gives the teacher oversight and is framework-enforced via interrupt_before in
# graph.py.
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

from agent.prompts import SYSTEM_PROMPT, TUTOR_RESPONSE_PROMPT
from agent.state import RecommendedAction, TutorState
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


def _claims(state: TutorState) -> Dict[str, Any]:
    # Demo default: an authenticated student identity if none supplied.
    return state.get("acting_user_claims") or {
        "sub": "demo-student", "custom:edu_role": "STUDENT",
    }


# Phrases that signal a request to complete / hand over a graded or prohibited
# assessment rather than learn the concept. Matched against the student's question.
_PROHIBITED_REQUEST = (
    "give me the answer", "give me the answers", "just the answer", "just give me",
    "do my homework", "complete the quiz", "answers to the quiz", "answers to the test",
    "answers to the exam", "answer key", "solve the graded", "fill in the quiz",
    "take the test for me", "write my essay", "do the graded",
)


def intake(state: TutorState) -> TutorState:
    state["current_step"] = "intake"
    state.setdefault("revision_count", 0)
    state.setdefault("completed_steps", [])
    state.setdefault("audit_trail", [])
    state.setdefault("mode", "hint")
    state.setdefault("misconceptions", [])
    state["session_status"] = "TUTORING"
    state["audit_trail"].append(_audit(f"Intake of {state.get('mode')} tutoring request", "intake"))
    state["completed_steps"].append("intake")
    return state


def retrieve(state: TutorState) -> TutorState:
    state["current_step"] = "retrieve"
    claims = _claims(state)
    course = state.get("course", "")
    sources = []
    try:
        state["course_hits"] = gateway_tools.search_course_material(claims, state.get("question", ""))
        sources.append("kb")
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "retrieve", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
        state.setdefault("course_hits", [])
    try:
        content = gateway_tools.get_course_content(claims, course)
        if content:
            for mod in content.get("modules", []) or []:
                state.setdefault("course_hits", []).append(
                    {"course": content.get("course", course),
                     "title": mod.get("title", ""), "ref": mod.get("id", "")}
                )
            sources.append("lms")
    except Exception:
        state.setdefault("course_hits", [])
    try:
        state["assignments"] = gateway_tools.get_assignments(claims, course)
        if state["assignments"]:
            sources.append("lms")
    except Exception:
        state.setdefault("assignments", {})
    state["audit_trail"].append(_audit("Retrieved instructor-approved course material", "retrieve", sources))
    state["completed_steps"].append("retrieve")
    return state


def _demo_response(state: TutorState) -> str:
    hits = state.get("course_hits", []) or []
    mode = state.get("mode", "hint")
    parts = []
    if hits:
        titles = ", ".join(h.get("title", "the material") for h in hits[:2])
        parts.append(f"Let's work from the course material ({titles}).")
        if mode == "explain":
            parts.append("Here is the core idea explained in plain language, then a question for you to try.")
        elif mode == "practice":
            parts.append("Try a practice item modeled on the material, and I will give feedback on your approach.")
        else:
            parts.append("Here is a hint to get you started — not the final answer.")
        parts.append("What is the first step you think applies here, and why?")
    else:
        parts.append("I could not find approved course material for that yet; let's review the prerequisite concept together so you can study the source.")
    return " ".join(parts)


def tutor_respond(state: TutorState) -> TutorState:
    state["current_step"] = "tutor_respond"
    material = "\n".join(f"- {h.get('title','')} ({h.get('ref','')})" for h in state.get("course_hits", []) or [])
    assignments = state.get("assignments", {}) or {}
    if generate is not None:
        out = generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=TUTOR_RESPONSE_PROMPT.format(
                mode=state.get("mode", "hint"),
                course=state.get("course", ""),
                question=state.get("question", ""),
                material=material or "(none found)",
                assignments=assignments or "(none)",
            ),
            demo_fn=lambda: _demo_response(state),
        )
        state["draft_response"], state["generated_by"] = out["text"], out["generated_by"]
    else:  # pragma: no cover
        state["draft_response"], state["generated_by"] = _demo_response(state), "demo-stub"
    state["audit_trail"].append(_audit("Drafted grounded Socratic response", "tutor_respond",
                                       model=state["generated_by"]))
    state["completed_steps"].append("tutor_respond")
    return state


def checks(state: TutorState) -> TutorState:
    state["current_step"] = "checks"
    question = (state.get("question", "") or "").lower()
    text = state.get("draft_response", "")

    # Prohibited-behavior check: the student is asking the agent to complete or hand
    # over the answers to a graded/prohibited assessment. Refuse and escalate.
    findings = [f"prohibited assessment request: {p}" for p in _PROHIBITED_REQUEST if p in question]
    state["compliance_findings"] = findings

    if verify_grounding is not None:
        report = verify_grounding(text, dict(state)).to_audit_dict()
    else:  # pragma: no cover
        report = {"grounded": True, "ungrounded_numbers": [], "ungrounded_entities": []}
    state["grounding_report"] = report

    # Surface the misconception(s) the session touched, for teacher oversight.
    miscon = list(state.get("misconceptions", []) or [])
    if findings and "asked the tutor to bypass learning the material" not in miscon:
        miscon.append("asked the tutor to bypass learning the material")
    state["misconceptions"] = miscon

    ungrounded = report.get("ungrounded_numbers", []) + report.get("ungrounded_entities", [])
    if findings:
        # Bright line: do NOT provide the answer; replace the draft with a refusal.
        state["draft_response"] = (
            "I can't provide the answers to a graded or prohibited assessment, but I'm "
            "glad to help you learn the concept. Tell me where you're stuck and I'll give "
            "you a hint or walk through a related example."
        )
        state["recommended_action"] = RecommendedAction.ESCALATE
    elif ungrounded and state.get("revision_count", 0) < 1:
        state["recommended_action"] = RecommendedAction.REVISE
        state["revision_count"] = state.get("revision_count", 0) + 1
    else:
        state["recommended_action"] = RecommendedAction.ANSWER

    state["audit_trail"].append(_audit("Ran grounding + prohibited-behavior checks", "checks"))
    state["completed_steps"].append("checks")
    return state


def routing_decision(state: TutorState) -> str:
    if state.get("recommended_action") == RecommendedAction.REVISE:
        return "tutor_respond"
    return "human_review_gate"


def human_review_gate(state: TutorState) -> TutorState:
    """HITL pause point. graph compiles with interrupt_before=[human_review_gate].

    Teacher oversight: surfaces the misconceptions the session touched, NOT hidden
    scores. The teacher controls the source material and can review the tutoring.
    """
    state["current_step"] = "human_review_gate"
    if state.get("recommended_action") == RecommendedAction.ESCALATE:
        state["session_status"] = "ESCALATED"
    else:
        state["session_status"] = "PENDING_REVIEW"
    state["audit_trail"].append({
        **_audit("Awaiting teacher oversight of tutoring session", "human_review_gate"),
        "actor": "system", "human_review_required": True,
    })
    state["completed_steps"].append("human_review_gate")
    return state


def finalize(state: TutorState) -> TutorState:
    """
    Close the tutoring session. There are no consequential writes: the tutor never
    completes a graded assessment and never posts a score. Finalize logs the session
    and surfaces a misconceptions summary for the teacher.
    """
    state["current_step"] = "finalize"
    if state.get("session_status") != "ESCALATED":
        state["session_status"] = "RESOLVED"
    state["audit_trail"].append(_audit("Logged tutoring session; surfaced misconceptions summary",
                                       "finalize"))
    state["completed_steps"].append("finalize")
    return state
