# tools/gateway_tools.py
# ============================================================
# Gateway-backed tool access for Document & Accessibility Services.
#
# Every system-of-record call (document pipeline, SIS, comms) goes through the MCP
# authorization gateway (reference logic for Bedrock AgentCore Gateway +
# Identity): the acting user's verified claims are authorized against deny-by-
# default policy with least-privilege intersection, consequential actions (the SIS
# enrollment-record write) require human approval, a short-lived scoped token is
# minted, and the attempt is audited (student-PII masked). Classification,
# extraction, validation, transformation, and translation are reads/analysis; the
# enrollment write is the one CONSEQUENTIAL tool and must NOT execute without an
# approval.
# ============================================================
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "platform_core"))

AGENT_ID = "07-document-accessibility-services"

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
            "docpipe/SIS must flow through the gateway (authorize -> token -> audit)."
        )
    return _GATEWAY.invoke(user_claims=claims, agent_id=AGENT_ID, tool=tool,
                           args=args, approval=approval)


def classify_document(claims: Dict[str, Any], document_ref: str) -> Dict[str, Any]:
    res = _invoke(claims, "docpipe.classify_document", {"document_ref": document_ref})
    return res.result if res.allowed else {}


def extract_fields(claims: Dict[str, Any], document_ref: str) -> Dict[str, Any]:
    res = _invoke(claims, "docpipe.extract_fields", {"document_ref": document_ref})
    return res.result if res.allowed else {}


def validate_completeness(claims: Dict[str, Any], document_ref: str) -> Dict[str, Any]:
    res = _invoke(claims, "docpipe.validate_completeness", {"document_ref": document_ref})
    return res.result if res.allowed else {}


def transform_and_translate(claims: Dict[str, Any], content_ref: str, language: str) -> Dict[str, Any]:
    """Accessibility mode: produce accessible outputs, then a translated draft."""
    acc = _invoke(claims, "docpipe.transform_accessible", {"content_ref": content_ref})
    out: Dict[str, Any] = acc.result if acc.allowed else {}
    tr = _invoke(claims, "docpipe.translate_content", {"content_ref": content_ref, "language": language})
    if tr.allowed:
        out = dict(out)
        out["language"] = tr.result.get("language", language)
        out["translation_artifact_id"] = tr.result.get("artifact_id", "")
    return out


def draft_message(claims: Dict[str, Any], payload: Dict[str, Any]) -> Any:
    """Low-risk draft: a missing-items request message (draft only, no send)."""
    return _invoke(claims, "comms.draft_message", payload)


def update_enrollment_record(claims: Dict[str, Any], payload: Dict[str, Any],
                             approval: Optional[Dict[str, Any]] = None) -> Any:
    """Consequential: writing the SIS enrollment record requires human approval."""
    return _invoke(claims, "sis.update_enrollment_record", payload, approval=approval)
