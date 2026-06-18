# tools/gateway_tools.py
# ============================================================
# Gateway-backed tool access for the Student & Family Services Concierge.
#
# Every system-of-record call (SIS, CRM, knowledge base, comms) goes through the
# MCP authorization gateway (reference logic for Bedrock AgentCore Gateway +
# Identity): the acting user's verified claims are authorized against deny-by-
# default policy with least-privilege intersection, consequential actions (an
# outbound family message) require human approval, a short-lived scoped token is
# minted, and the attempt is audited (student-PII masked).
# ============================================================
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "platform_core"))

AGENT_ID = "01-student-family-concierge"

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
            "SIS/CRM must flow through the gateway (authorize -> token -> audit)."
        )
    return _GATEWAY.invoke(user_claims=claims, agent_id=AGENT_ID, tool=tool,
                           args=args, approval=approval)


def search_policies(claims: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    res = _invoke(claims, "kb.search_policies", {"query": query})
    return res.result.get("results", []) if res.allowed else []


def check_application_status(claims: Dict[str, Any]) -> Dict[str, Any]:
    res = _invoke(claims, "sis.check_application_status", {})
    return res.result if res.allowed else {}


def get_schedule(claims: Dict[str, Any]) -> Dict[str, Any]:
    res = _invoke(claims, "sis.get_schedule", {})
    return res.result if res.allowed else {}


def create_advising_case(claims: Dict[str, Any], payload: Dict[str, Any]) -> Any:
    """Low-risk workflow: open an advising case (no approval gate)."""
    return _invoke(claims, "crm.create_advising_case", payload)


def schedule_appointment(claims: Dict[str, Any], payload: Dict[str, Any]) -> Any:
    """Low-risk workflow: schedule an appointment (no approval gate)."""
    return _invoke(claims, "crm.schedule_appointment", payload)


def send_message(claims: Dict[str, Any], payload: Dict[str, Any],
                 approval: Optional[Dict[str, Any]] = None) -> Any:
    """Consequential: an outbound family/student message requires human approval."""
    return _invoke(claims, "comms.send_message", payload, approval=approval)
