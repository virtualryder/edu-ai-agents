# tools/gateway_tools.py
# ============================================================
# Gateway-backed tool access for the Assessment, Grading & Feedback agent.
#
# Every system-of-record call (LMS, assessment engine) goes through the MCP
# authorization gateway (reference logic for Bedrock AgentCore Gateway +
# Identity): the acting educator's verified claims are authorized against
# deny-by-default policy with least-privilege intersection, the consequential
# action (releasing a grade to a student) requires human approval, a short-lived
# scoped token is minted, and the attempt is audited (student-PII masked).
# ============================================================
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "platform_core"))

AGENT_ID = "04-assessment-grading-feedback"

try:
    from edu_agent_platform.mcp_gateway import MCPGateway

    _GATEWAY: Optional[Any] = MCPGateway()
except Exception:  # pragma: no cover - standalone demo without platform_core
    _GATEWAY = None


def _invoke(claims: Dict[str, Any], tool: str, args: Dict[str, Any],
            approval: Optional[Dict[str, Any]] = None) -> Any:
    if _GATEWAY is None:
        raise RuntimeError(
            "MCP gateway unavailable; install platform_core. Production access to "
            "LMS/assessment must flow through the gateway (authorize -> token -> audit)."
        )
    return _GATEWAY.invoke(user_claims=claims, agent_id=AGENT_ID, tool=tool,
                           args=args, approval=approval)


def get_assignments(claims: Dict[str, Any], course: str = "") -> Dict[str, Any]:
    res = _invoke(claims, "lms.get_assignments", {"course": course})
    return res.result if res.allowed else {}


def evaluate_rubric(claims: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Analysis only: score a submission against the rubric (no grade released)."""
    res = _invoke(claims, "assessment.evaluate_rubric", payload)
    return res.result if res.allowed else {}


def draft_feedback(claims: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Analysis only: draft feedback for educator review (no grade released)."""
    res = _invoke(claims, "assessment.draft_feedback", payload)
    return res.result if res.allowed else {}


def summarize_class_patterns(claims: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Analysis only: surface class-wide misconception patterns."""
    res = _invoke(claims, "assessment.summarize_class_patterns", payload)
    return res.result if res.allowed else {}


def release_grade(claims: Dict[str, Any], payload: Dict[str, Any],
                  approval: Optional[Dict[str, Any]] = None) -> Any:
    """Consequential: releasing a final grade to a student requires human approval."""
    return _invoke(claims, "assessment.release_grade", payload, approval=approval)
