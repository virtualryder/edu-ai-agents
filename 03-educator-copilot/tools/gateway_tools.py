# tools/gateway_tools.py
# ============================================================
# Gateway-backed tool access for the Educator Copilot.
#
# Every system-of-record call (LMS, knowledge base) goes through the MCP
# authorization gateway (reference logic for Bedrock AgentCore Gateway +
# Identity): the acting educator's verified claims are authorized against deny-by-
# default policy with least-privilege intersection, consequential actions
# (publishing content to students, moving a learner's due date) require human
# approval, a short-lived scoped token is minted, and the attempt is audited.
#
# Three tiers map to the policy: READ tools, low-risk DRAFT writes (no approval
# gate), and CONSEQUENTIAL tools (publish / due-date change) that must NOT execute
# without a verified approval bound at the gateway.
# ============================================================
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "platform_core"))

AGENT_ID = "03-educator-copilot"

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
            "the LMS/knowledge base must flow through the gateway (authorize -> token -> audit)."
        )
    return _GATEWAY.invoke(user_claims=claims, agent_id=AGENT_ID, tool=tool,
                           args=args, approval=approval)


# ── Reads ─────────────────────────────────────────────────────────────────────
def get_roster(claims: Dict[str, Any], course: str) -> Dict[str, Any]:
    res = _invoke(claims, "lms.get_roster", {"course": course})
    return res.result if res.allowed else {}


def get_course_content(claims: Dict[str, Any], course: str) -> Dict[str, Any]:
    res = _invoke(claims, "lms.get_course_content", {"course": course})
    return res.result if res.allowed else {}


def get_assignments(claims: Dict[str, Any], course: str) -> Dict[str, Any]:
    res = _invoke(claims, "lms.get_assignments", {"course": course})
    return res.result if res.allowed else {}


def get_engagement(claims: Dict[str, Any], course: str) -> Dict[str, Any]:
    res = _invoke(claims, "lms.get_engagement", {"course": course})
    return res.result if res.allowed else {}


def identify_missing_submissions(claims: Dict[str, Any], course: str) -> Dict[str, Any]:
    res = _invoke(claims, "lms.identify_missing_submissions", {"course": course})
    return res.result if res.allowed else {}


def search_course_material(claims: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    res = _invoke(claims, "kb.search_course_material", {"query": query})
    return res.result.get("results", []) if res.allowed else []


# ── Low-risk DRAFT writes (no approval gate) ──────────────────────────────────
def create_assignment_draft(claims: Dict[str, Any], payload: Dict[str, Any]) -> Any:
    """Low-risk workflow: place an assignment DRAFT in the LMS (no approval gate)."""
    return _invoke(claims, "lms.create_assignment_draft", payload)


def create_rubric_draft(claims: Dict[str, Any], payload: Dict[str, Any]) -> Any:
    """Low-risk workflow: place a rubric DRAFT in the LMS (no approval gate)."""
    return _invoke(claims, "lms.create_rubric_draft", payload)


def post_announcement_draft(claims: Dict[str, Any], payload: Dict[str, Any]) -> Any:
    """Low-risk workflow: place an announcement DRAFT in the LMS (no approval gate)."""
    return _invoke(claims, "lms.post_announcement_draft", payload)


# ── Consequential (require human approval bound at the gateway) ───────────────
def update_assignment_due_date(claims: Dict[str, Any], payload: Dict[str, Any],
                               approval: Optional[Dict[str, Any]] = None) -> Any:
    """Consequential: changing a learner's due date requires human approval."""
    return _invoke(claims, "lms.update_assignment_due_date", payload, approval=approval)


def publish_content(claims: Dict[str, Any], payload: Dict[str, Any],
                    approval: Optional[Dict[str, Any]] = None) -> Any:
    """Consequential: making content live to students requires human approval."""
    return _invoke(claims, "lms.publish_content", payload, approval=approval)
