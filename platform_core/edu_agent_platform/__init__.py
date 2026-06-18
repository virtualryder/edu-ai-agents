"""EDU Agent Platform — shared production primitives for all education agents.

Modules:
    llm_factory   get_llm(role) — Anthropic (default) / Bedrock + Guardrails (in-account)
    generation    generate(...) — demo-aware drafting (deterministic offline, real inference live)
    auth          verify_jwt, require_role, record_reviewer_identity, FERPA rights-transfer
    secrets       get_secret — Secrets Manager with env fallback
    pii_masker    mask(text), masked_pseudonym(id) — FERPA/COPPA identifier masking
    tracing       traced_node — OTel span per graph node, no-op fallback
    mcp_gateway   the governed front door to systems of record (SIS/LMS/CRM/ITSM/ERP).
                  Reference logic for Amazon Bedrock AgentCore Gateway + Identity.
    connectors    fixture/live connector framework for education systems of record

This package is the shared everything-else; per-agent durability lives in each
agent's agent/persistence.py. Designed so a single workflow is reviewed once and
reused across agents — a governance improvement here benefits all eight agents.
"""
from edu_agent_platform.generation import generate  # noqa: F401
from edu_agent_platform.llm_factory import demo_mode, get_llm  # noqa: F401
from edu_agent_platform.pii_masker import luhn_valid, mask, masked_pseudonym  # noqa: F401
from edu_agent_platform.secrets import get_secret  # noqa: F401
from edu_agent_platform.tracing import traced_node  # noqa: F401

__all__ = [
    "get_llm", "demo_mode", "generate", "mask", "masked_pseudonym",
    "luhn_valid", "get_secret", "traced_node",
]
__version__ = "0.1.0"
