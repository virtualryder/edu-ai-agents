"""Governance & evaluation framework — the EDU compliance spine in code.

    grounding         verify_grounding(text, state) — claim traceability
    prompt_registry   versioned, hash-pinned prompts; CI fails on un-bumped drift
    fairness          representativeness / equity checks for student-success targeting
    evals             structural golden-artifact regression (no API key)
    redteam           prompt-injection / PII-exfiltration / authz-bypass scenarios
    tests             HITL gate enforcement, policy intersection, masking, manifest
"""
from .grounding import GroundingReport, verify_grounding  # noqa: F401

__all__ = ["verify_grounding", "GroundingReport"]
