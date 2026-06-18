# tools/gateway_tools.py
# ============================================================
# Gateway-backed tool access for the Pathway Navigator.
#
# Every system-of-record call (SIS, degree rules, labor market, knowledge base,
# CRM/scheduling) goes through the MCP authorization gateway (reference logic for
# Bedrock AgentCore Gateway + Identity): the acting user's verified claims are
# authorized against deny-by-default policy with least-privilege intersection,
# consequential actions require human approval, a short-lived scoped token is
# minted, and the attempt is audited (student-PII masked). The navigator's tools
# are reads, deterministic rules, and one LOW-RISK scheduling action — it never
# holds a placement-writing tool.
# ============================================================
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "platform_core"))

AGENT_ID = "06-pathway-navigator"

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
            "SIS/rules/CRM must flow through the gateway (authorize -> token -> audit)."
        )
    return _GATEWAY.invoke(user_claims=claims, agent_id=AGENT_ID, tool=tool,
                           args=args, approval=approval)


def get_student_profile(claims: Dict[str, Any]) -> Dict[str, Any]:
    res = _invoke(claims, "sis.get_student_profile", {})
    return res.result if res.allowed else {}


def get_graduation_requirements(claims: Dict[str, Any]) -> Dict[str, Any]:
    res = _invoke(claims, "sis.get_graduation_requirements", {})
    return res.result if res.allowed else {}


def get_transfer_credits(claims: Dict[str, Any]) -> Dict[str, Any]:
    res = _invoke(claims, "sis.get_transfer_credits", {})
    return res.result if res.allowed else {}


def run_degree_audit(claims: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministic rules: authoritative degree-completion audit."""
    res = _invoke(claims, "rules.run_degree_audit", {"profile": profile})
    return res.result if res.allowed else {}


def check_prerequisites(claims: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Deterministic rules: prerequisite eligibility check."""
    res = _invoke(claims, "rules.check_prerequisites", {"query": query})
    return res.result if res.allowed else {}


def get_career_pathways(claims: Dict[str, Any], query: str) -> Dict[str, Any]:
    res = _invoke(claims, "labor.get_career_pathways", {"query": query})
    return res.result if res.allowed else {}


def search_policies(claims: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    res = _invoke(claims, "kb.search_policies", {"query": query})
    return res.result.get("results", []) if res.allowed else []


def schedule_appointment(claims: Dict[str, Any], payload: Dict[str, Any]) -> Any:
    """Low-risk workflow: schedule a counselor appointment (no approval gate)."""
    return _invoke(claims, "crm.schedule_appointment", payload)
