"""
Tracing — one OpenTelemetry span per graph node, with a no-op fallback.

Operational observability (latency, errors, model/version attributes) without
requiring OTel to be installed in dev. The audit trail in agent state is the
compliance record; this adds operational telemetry on top.

Usage:
    from edu_agent_platform import traced_node

    @traced_node("intake")
    def intake(state): ...

When opentelemetry is unavailable the decorator is a transparent pass-through.
"""
from __future__ import annotations

import functools
import logging
import os
from typing import Any, Callable

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    from opentelemetry import trace as _otel_trace

    _TRACER = _otel_trace.get_tracer("edu_agent_platform")
    _OTEL = True
except Exception:  # pragma: no cover
    _TRACER = None
    _OTEL = False


def traced_node(name: str) -> Callable:
    """Decorate a LangGraph node so each execution becomes a span (if OTel present)."""

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not _OTEL or os.getenv("DISABLE_TRACING", "").lower() in ("1", "true", "yes"):
                return fn(*args, **kwargs)
            with _TRACER.start_as_current_span(f"node.{name}") as span:  # type: ignore
                try:
                    span.set_attribute("edu.node", name)
                    span.set_attribute("edu.llm_provider", os.getenv("LLM_PROVIDER", "anthropic"))
                    result = fn(*args, **kwargs)
                    span.set_attribute("edu.status", "ok")
                    return result
                except Exception as exc:
                    span.set_attribute("edu.status", "error")
                    span.record_exception(exc)
                    raise

        return wrapper

    return decorator
