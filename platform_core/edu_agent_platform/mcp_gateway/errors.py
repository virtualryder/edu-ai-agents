"""Gateway error types (all fail-closed)."""
from __future__ import annotations


class GatewayError(Exception):
    """Base class for all MCP gateway errors."""


class PolicyDenied(GatewayError):
    """Raised when authorization is denied (deny-by-default)."""


class ApprovalRequired(GatewayError):
    """Raised when a consequential tool needs human approval before execution."""
