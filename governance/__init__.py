"""Governance & evaluation framework — the EDU compliance spine in code.

    grounding         verify_grounding(text, state) — claim traceability
    prompt_registry   versioned, hash-pinned prompts; CI fails on un-bumped drift
    fairness          representativeness + four-fifths disparate-impact screens
    accessibility     WCAG 2.1 AA / ADA Title II pre-flight on AI-generated content
    controls          obligation -> platform/AWS control mappings (FERPA/COPPA/IDEA/ADA/...)
    evals             structural golden-artifact regression (no API key)
    redteam           prompt-injection / PII-exfiltration / authz-bypass scenarios
    tests             HITL enforcement, consequential bright-line, policy intersection, masking
"""
from .grounding import GroundingReport, verify_grounding  # noqa: F401

__all__ = ["verify_grounding", "GroundingReport"]
