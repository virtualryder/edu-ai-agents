# tools/gateway_tools.py
# ============================================================
# Gateway-backed tool access for Operations & Service Desk.
#
# Every system-of-record call (ITSM, knowledge base, ERP) goes through the MCP
# authorization gateway (reference logic for Bedrock AgentCore Gateway +
# Identity): the acting user's verified claims are authorized against deny-by-
# default policy with least-privilege intersection, consequential actions
# (privileged remediation, financial approval) require human approval, a short-
# lived scoped token is minted, and the attempt is audited (PII masked). Reads,
# diagnostics, ticket creation, and document drafting are low-risk; password
# reset, service restart, and approval initiation are the CONSEQUENTIAL tools and
# must NOT execute without an approval.
# ============================================================
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "platform_core"))

AGENT_ID = "08-operations-service-desk"

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
            "ITSM/ERP must flow through the gateway (authorize -> token -> audit)."
        )
    return _GATEWAY.invoke(user_claims=claims, agent_id=AGENT_ID, tool=tool,
                           args=args, approval=approval)


def get_ticket(claims: Dict[str, Any], ticket_id: str) -> Dict[str, Any]:
    res = _invoke(claims, "itsm.get_ticket", {"ticket_id": ticket_id})
    return res.result if res.allowed else {}


def run_diagnostic(claims: Dict[str, Any], request: str) -> Dict[str, Any]:
    res = _invoke(claims, "itsm.run_diagnostic", {"request": request})
    return res.result if res.allowed else {}


def search_policies(claims: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    res = _invoke(claims, "kb.search_policies", {"query": query})
    return res.result.get("results", []) if res.allowed else []


def search_erp_policy(claims: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    res = _invoke(claims, "erp.search_policy", {"query": query})
    return res.result.get("results", []) if res.allowed else []


def create_ticket(claims: Dict[str, Any], payload: Dict[str, Any]) -> Any:
    """Low-risk workflow: file an ITSM ticket (no approval gate)."""
    return _invoke(claims, "itsm.create_ticket", payload)


def draft_document(claims: Dict[str, Any], payload: Dict[str, Any]) -> Any:
    """Low-risk workflow: draft an RFP / scope-of-work document (draft only)."""
    return _invoke(claims, "erp.draft_document", payload)


def reset_password(claims: Dict[str, Any], payload: Dict[str, Any],
                   approval: Optional[Dict[str, Any]] = None) -> Any:
    """Consequential (privileged): a password reset requires human approval."""
    return _invoke(claims, "itsm.reset_password", payload, approval=approval)


def restart_service(claims: Dict[str, Any], payload: Dict[str, Any],
                    approval: Optional[Dict[str, Any]] = None) -> Any:
    """Consequential (privileged): a service restart requires human approval."""
    return _invoke(claims, "itsm.restart_service", payload, approval=approval)


def initiate_approval(claims: Dict[str, Any], payload: Dict[str, Any],
                      approval: Optional[Dict[str, Any]] = None) -> Any:
    """Consequential (financial/procurement): routing an approval requires human approval."""
    return _invoke(claims, "erp.initiate_approval", payload, approval=approval)
