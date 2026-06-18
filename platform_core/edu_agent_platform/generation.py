"""
Demo-aware text generation helper.

Every agent that drafts text (a family message, a lesson, feedback, an advising
plan, an accessible-content summary) calls `generate()`. It selects the path:

    EXTRACT_MODE=demo  -> deterministic local stub (no API key, no network).
                          Used for demos, CI, and the eval harness.
    LLM_PROVIDER=...   -> real inference via the LLM factory (Anthropic/Bedrock).
    no API key set     -> falls back to the demo stub rather than crashing, so a
                          first-run never fails for lack of a key (it warns).

The `demo_fn` argument lets each agent supply a grounded, deterministic draft
built ONLY from its state, so demo output stays faithful to the inputs and passes
the grounding checker. This keeps the whole suite runnable end-to-end offline.
"""
from __future__ import annotations

import logging
import os
from typing import Callable, Dict, Optional

from .llm_factory import demo_mode, get_llm, provider

logger = logging.getLogger(__name__)


def generate(
    *,
    system_prompt: str,
    user_prompt: str,
    demo_fn: Callable[[], str],
    role: str = "narrative",
) -> Dict[str, str]:
    """
    Return {"text": <draft>, "generated_by": <bedrock|anthropic|demo-stub>}.

    Falls back to the deterministic demo stub when in demo mode or when the
    selected provider has no credentials configured — so the agent always runs.
    """
    if demo_mode():
        return {"text": demo_fn(), "generated_by": "demo-stub"}

    prov = provider()
    has_key = bool(os.getenv("ANTHROPIC_API_KEY")) if prov == "anthropic" else True
    if not has_key:
        logger.warning("No credentials for provider %r; using deterministic demo stub.", prov)
        return {"text": demo_fn(), "generated_by": "demo-stub"}

    try:  # pragma: no cover - exercised only with live credentials
        llm = get_llm(role=role)  # type: ignore[arg-type]
        msg = llm.invoke([("system", system_prompt), ("human", user_prompt)])
        text = getattr(msg, "content", None) or str(msg)
        if isinstance(text, list):  # some providers return content blocks
            text = " ".join(str(p.get("text", p)) if isinstance(p, dict) else str(p) for p in text)
        return {"text": text, "generated_by": prov}
    except Exception as exc:  # pragma: no cover - resilience path
        logger.warning("LLM generation failed (%s); using deterministic demo stub.", exc)
        return {"text": demo_fn(), "generated_by": "demo-stub"}
