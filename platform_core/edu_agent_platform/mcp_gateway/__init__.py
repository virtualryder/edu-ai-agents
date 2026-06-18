"""MCP authorization gateway — reference logic for Amazon Bedrock AgentCore Gateway + Identity."""
from .audit import GatewayAuditLog  # noqa: F401
from .errors import ApprovalRequired, GatewayError, PolicyDenied  # noqa: F401
from .gateway import GatewayResult, MCPGateway  # noqa: F401
from .policy import (  # noqa: F401
    AGENT_TOOL_GRANTS,
    CONSEQUENTIAL_TOOLS,
    ROLE_ENTITLEMENTS,
    TOOL_REGISTRY,
    decide,
    user_entitlements,
)

__all__ = [
    "MCPGateway", "GatewayResult", "GatewayAuditLog",
    "GatewayError", "PolicyDenied", "ApprovalRequired",
    "decide", "user_entitlements",
    "TOOL_REGISTRY", "AGENT_TOOL_GRANTS", "ROLE_ENTITLEMENTS", "CONSEQUENTIAL_TOOLS",
]
