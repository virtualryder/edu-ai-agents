# agent/nodes.py
# ============================================================
# Node functions for the Assessment, Grading & Feedback workflow.
#
# Each node reads what it needs from GradingState, performs one step, writes its
# findings back, and appends an audit-trail entry. The AI evaluates against the
# rubric and drafts feedback; the educator owns the grade. The human_review gate
# is framework-enforced via interrupt_before in graph.py, and the consequential
# grade release runs only with a human approval bound at the gateway.
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

from agent.prompts import FEEDBACK_DRAFT_PROMPT, SYSTEM_PROMPT
from agent.state import GradingState, RecommendedAction
from tools import gateway_tools

try:
    from edu_agent_platform.generation import generate
    from governance.grounding import verify_grounding
except Exception:  # pragma: no cover - resilience for standalone import
    generate = None  # type: ignore
    verify_grounding = None  # type: ignore

# Below this evaluator confidence, the case is escalated for manual review.
CONFIDENCE_THRESHOLD = 0.7


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


def _claims(state: GradingState) -> Dict[str, Any]:
    # Demo default: an authenticated educator identity if none supplied.
    return state.get("acting_user_claims") or {
        "sub": "demo-educator", "custom:edu_role": "EDUCATOR",
    }


def intake(state: GradingState) -> GradingState:
    state["current_step"] = "intake"
    state.setdefault("revision_count", 0)
    state.setdefault("completed_steps", [])
    state.setdefault("audit_trail", [])
    state.setdefault("rubric_ref", "")
    state["case_status"] = "EVALUATING"
    state["audit_trail"].append(
        _audit(f"Intake of submission {state.get('submission_id')}", "intake"))
    state["completed_steps"].append("intake")
    return state


def retrieve(state: GradingState) -> GradingState:
    state["current_step"] = "retrieve"
    claims = _claims(state)
    sources = []
    try:
        state["assignment"] = gateway_tools.get_assignments(claims, state.get("course", ""))
        sources.append("lms")
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "retrieve", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
        state.setdefault("assignment", {})
    state["audit_trail"].append(_audit("Retrieved assignment / rubric reference", "retrieve", sources))
    state["completed_steps"].append("retrieve")
    return state


def evaluate(state: GradingState) -> GradingState:
    state["current_step"] = "evaluate"
    claims = _claims(state)
    sources = []
    try:
        payload = {
            "submission_id": state.get("submission_id", ""),
            "rubric_ref": state.get("rubric_ref", ""),
        }
        state["evaluation"] = gateway_tools.evaluate_rubric(claims, payload)
        sources.append("assessment")
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "evaluate", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
        state.setdefault("evaluation", {})
    evaluation = state.get("evaluation", {}) or {}
    # A low-confidence scan path (e.g. handwritten work) can force a manual review.
    state["confidence"] = float(state.get("confidence", evaluation.get("confidence", 0.0)))
    state["audit_trail"].append(_audit("Evaluated submission against rubric", "evaluate", sources))
    state["completed_steps"].append("evaluate")
    return state


def _demo_feedback(state: GradingState) -> str:
    evaluation = state.get("evaluation", {}) or {}
    scores = evaluation.get("criteria_scores", []) or []
    max_per = evaluation.get("max_per_criterion", 4)
    raw_total = evaluation.get("raw_total")
    max_total = evaluation.get("max_total")
    parts = []
    if scores:
        per = ", ".join(f"criterion {i + 1}: {s}/{max_per}" for i, s in enumerate(scores))
        parts.append(f"Against the rubric, the evaluator recorded {per}.")
    else:
        parts.append("The evaluator did not return criterion scores for this submission.")
    if raw_total is not None and max_total is not None:
        parts.append(f"That is {raw_total} of {max_total} rubric points (the educator confirms any final grade).")
    parts.append("Strongest next step: revisit the lowest-scoring criterion with specific evidence from the source material.")
    if state.get("confidence", 1.0) < CONFIDENCE_THRESHOLD:
        parts.append("Evaluator confidence is low here, so this should be reviewed manually before any release.")
    return " ".join(parts)


def draft_feedback(state: GradingState) -> GradingState:
    state["current_step"] = "draft_feedback"
    evaluation = state.get("evaluation", {}) or {}
    scores = ", ".join(str(s) for s in evaluation.get("criteria_scores", []) or []) or "(none)"
    if generate is not None:
        out = generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=FEEDBACK_DRAFT_PROMPT.format(
                channel=state.get("channel", "lms"),
                submission=state.get("submission_id", "(unknown)"),
                rubric=state.get("rubric_ref", "") or "(rubric reference not provided)",
                scores=scores,
            ),
            demo_fn=lambda: _demo_feedback(state),
        )
        state["draft_feedback"], state["generated_by"] = out["text"], out["generated_by"]
    else:  # pragma: no cover
        state["draft_feedback"], state["generated_by"] = _demo_feedback(state), "demo-stub"
    state["audit_trail"].append(_audit("Drafted rubric-grounded feedback", "draft_feedback",
                                       model=state["generated_by"]))
    state["completed_steps"].append("draft_feedback")
    return state


def checks(state: GradingState) -> GradingState:
    state["current_step"] = "checks"
    text = state.get("draft_feedback", "")
    # Compliance: the assistant must never assert a final/high-stakes grade.
    prohibited = ("your final grade is", "you receive an a", "you receive a b",
                  "you receive a c", "you failed", "you passed", "i am releasing your grade")
    findings = [f"prohibited final-grade phrasing: {p}" for p in prohibited if p in text.lower()]
    state["compliance_findings"] = findings

    if verify_grounding is not None:
        report = verify_grounding(text, dict(state)).to_audit_dict()
    else:  # pragma: no cover
        report = {"grounded": True, "ungrounded_numbers": [], "ungrounded_entities": []}
    state["grounding_report"] = report

    ungrounded = report.get("ungrounded_numbers", []) + report.get("ungrounded_entities", [])
    # Confidence-threshold rule: a low-confidence evaluation goes to manual review.
    if findings or state.get("confidence", 1.0) < CONFIDENCE_THRESHOLD:
        state["recommended_action"] = RecommendedAction.ESCALATE
    elif ungrounded and state.get("revision_count", 0) < 1:
        state["recommended_action"] = RecommendedAction.REVISE
        state["revision_count"] = state.get("revision_count", 0) + 1
    else:
        state["recommended_action"] = RecommendedAction.APPROVE_DRAFT

    state["audit_trail"].append(_audit("Ran grounding + confidence-threshold checks", "checks"))
    state["completed_steps"].append("checks")
    return state


def routing_decision(state: GradingState) -> str:
    if state.get("recommended_action") == RecommendedAction.REVISE:
        return "draft_feedback"
    return "human_review_gate"


def human_review_gate(state: GradingState) -> GradingState:
    """HITL pause point. graph compiles with interrupt_before=[human_review_gate]."""
    state["current_step"] = "human_review_gate"
    if state.get("recommended_action") == RecommendedAction.ESCALATE:
        state["case_status"] = "ESCALATED"
    else:
        state["case_status"] = "PENDING_REVIEW"
    state["audit_trail"].append({
        **_audit("Awaiting educator review / approval of any grade release", "human_review_gate"),
        "actor": "system", "human_review_required": True,
    })
    state["completed_steps"].append("human_review_gate")
    return state


def finalize(state: GradingState) -> GradingState:
    """
    Execute any requested workflow. The only consequential action here is
    releasing a final grade to a student, which requires a verified educator
    approval bound at the gateway; without it the grade stays PENDING_REVIEW.
    The agent never releases a final/high-stakes grade autonomously.
    """
    state["current_step"] = "finalize"
    claims = _claims(state)
    action = state.get("action_request") or {}
    try:
        kind = action.get("type")
        if kind == "release_grade":
            res = gateway_tools.release_grade(claims, action.get("payload", {}),
                                              approval=state.get("approval"))
            if getattr(res, "allowed", False):
                state["grade_id"] = res.result.get("grade_id", "GR-PENDING")
        if state.get("case_status") != "ESCALATED":
            state["case_status"] = "RESOLVED" if state.get("grade_id") else "PENDING_REVIEW"
    except Exception as exc:
        state.setdefault("errors", []).append({"step": "finalize", "error": str(exc),
                                               "timestamp": _now(), "recoverable": True})
    state["audit_trail"].append(_audit("Finalized feedback / executed approved grade release",
                                       "finalize", ["assessment"]))
    state["completed_steps"].append("finalize")
    return state
