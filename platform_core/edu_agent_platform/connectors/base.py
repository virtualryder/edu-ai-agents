"""
Connector framework — one interface, two implementations (fixture / live).

A *connector* is the typed adapter to a system of record (SIS, LMS, CRM, ITSM,
ERP, knowledge base, degree-rules engine, document pipeline, labor-market data).
Agents never call a vendor SDK directly: they call the MCP gateway, which (after
authorizing) calls a connector method. That keeps three properties true:

  * One validated integration surface per system (the security review is bounded).
  * Fixture mode runs the entire suite offline for demos, CI, and evals.
  * Live mode swaps in the real client behind the SAME method signatures, so no
    agent code changes between demo and production.

Add a system of record by subclassing GenericConnector (or a typed subclass) and
registering it in connectors/factory.py. Method names here must match
policy.TOOL_REGISTRY.
"""
from __future__ import annotations

import abc
from typing import Any


class Connector(abc.ABC):
    """Base class for all system-of-record connectors."""

    kind: str = "base"

    def authorize_call(self, token: Any, expected_tool: str) -> None:
        """
        Zero-trust at the connector boundary: independently verify the short-lived,
        tool-scoped token the gateway minted for THIS call. A connector must refuse
        any invocation that does not carry a valid gateway token scoped to the tool
        being called — so a compromised or directly-exposed connector cannot be
        driven without going through the authorization gateway. Fails closed.
        """
        from edu_agent_platform.mcp_gateway import tokens as _tokens
        if not token:
            raise PermissionError(
                f"connector {self.kind!r} refused {expected_tool!r}: no gateway token"
            )
        try:
            _tokens.verify_scoped_token(token, expected_tool=expected_tool)
        except Exception as exc:
            raise PermissionError(
                f"connector {self.kind!r} refused {expected_tool!r}: invalid gateway token ({exc})"
            ) from exc


class GenericConnector(Connector):
    """
    Catch-all for systems of record in the reference implementation.

    Methods are resolved dynamically against the fixture/live backing store so we
    don't need a bespoke abstract class per system to demonstrate the pattern;
    production replaces each with a typed subclass + validated vendor client.
    """

    def __init__(self, kind: str) -> None:
        self.kind = kind

    def __getattr__(self, method: str) -> Any:  # pragma: no cover - overridden by subclasses
        raise NotImplementedError(
            f"{self.kind!r} connector has no method {method!r} in this mode"
        )
