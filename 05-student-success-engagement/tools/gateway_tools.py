# tools/gateway_tools.py
# ============================================================
# Gateway-backed tool access for the Student Success & Engagement agent.
#
# Every system-of-record call (analytics, SIS, LMS, CRM, comms) goes through the
# MCP authorization gateway (reference logic for Bedrock AgentCore Gateway +
# Identity): the acting counselor's verified claims are authorized against
# deny-by-default policy with least-privilege intersection, the consequential
# action (an outbound student/family outreach) requires human approval, a
# short-lived scoped token is minted, and the attempt is audited (student-PII
# masked).
# ============================================================
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "platform_core"))

AGENT_ID = "05-student-success-engagement"

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
            "analytics/SIS/LMS/CRM must flow through the gateway (authorize -> token -> audit)."
        )
    return _GATEWAY.invoke(user_claims=claims, agent_id=AGENT_ID, tool=tool,
                           args=args, approval=approval)


def get_risk_signals(claims: Dict[str, Any]) -> Dict[str, Any]:
    res = _invoke(claims, "analytics.get_risk_signals", {})
    return res.result if res.allowed else {}


def get_intervention_history(claims: Dict[str, Any]) -> Dict[str, Any]:
    res = _invoke(claims, "analytics.get_intervention_history", {})
    return res.result if res.allowed else {}


def get_attendance(claims: Dict[str, Any]) -> Dict[str, Any]:
    res = _invoke(claims, "sis.get_attendance", {})
    return res.result if res.allowed else {}


def get_grades(claims: Dict[str, Any]) -> Dict[str, Any]:
    res = _invoke(claims, "sis.get_grades", {})
    return res.result if res.allowed else {}


def get_engagement(claims: Dict[str, Any]) -> Dict[str, Any]:
    res = _invoke(claims, "lms.get_engagement", {})
    return res.result if res.allowed else {}


def create_advising_case(claims: Dict[str, Any], payload: Dict[str, Any]) -> Any:
    """Low-risk workflow: open an advising case (no approval gate)."""
    return _invoke(claims, "crm.create_advising_case", payload)


def draft_message(claims: Dict[str, Any], payload: Dict[str, Any]) -> Any:
    """Draft-only: prepare outreach for counselor review (no approval gate)."""
    return _invoke(claims, "comms.draft_message", payload)


def send_message(claims: Dict[str, Any], payload: Dict[str, Any],
                 approval: Optional[Dict[str, Any]] = None) -> Any:
    """Consequential: an outbound student/family outreach requires human approval."""
    return _invoke(claims, "comms.send_message", payload, approval=approval)
