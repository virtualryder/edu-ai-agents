# tools/gateway_tools.py
# ============================================================
# Gateway-backed tool access for the Tutor & Study Companion.
#
# Every system-of-record call (knowledge base, LMS) goes through the MCP
# authorization gateway (reference logic for Bedrock AgentCore Gateway +
# Identity): the acting student's verified claims are authorized against deny-by-
# default policy with least-privilege intersection, a short-lived scoped token is
# minted, and the attempt is audited (student-PII masked). This agent is granted
# ONLY read tools — it has no consequential or write capability at all.
# ============================================================
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "platform_core"))

AGENT_ID = "02-tutor-study-companion"

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


def search_course_material(claims: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
    res = _invoke(claims, "kb.search_course_material", {"query": query})
    return res.result.get("results", []) if res.allowed else []


def get_course_content(claims: Dict[str, Any], course: str) -> Dict[str, Any]:
    res = _invoke(claims, "lms.get_course_content", {"course": course})
    return res.result if res.allowed else {}


def get_assignments(claims: Dict[str, Any], course: str) -> Dict[str, Any]:
    res = _invoke(claims, "lms.get_assignments", {"course": course})
    return res.result if res.allowed else {}
