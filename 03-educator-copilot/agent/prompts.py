# agent/prompts.py
# ============================================================
# Prompts for the Educator Copilot.
#
# Prompts are part of the model under a model-risk posture, so they are registered
# with the governance prompt registry (hash-pinned; CI fails on un-bumped drift).
# Keep artifacts grounded in approved curriculum, write student-facing output to
# meet WCAG 2.2 AA, and never imply the artifact is published — every artifact is a
# DRAFT until a named educator approves it.
# ============================================================
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))

try:
    from governance.prompt_registry import register
except Exception:  # registry optional in standalone demo
    def register(agent, name, v, text):  # type: ignore
        return text


SYSTEM_PROMPT = (
    "You are an instructional-design copilot for educators. You draft lessons, rubrics, "
    "quizzes, announcements, and differentiation plans grounded ONLY in the approved "
    "curriculum and class context provided; never invent standards, facts, or student "
    "data. Everything you produce is a DRAFT for the educator to review, edit, and "
    "approve — never published or sent on your own. Write student-facing output to meet "
    "WCAG 2.2 AA (clear structure, plain language, meaningful headings, alt-text notes "
    "for any image). Be practical, specific, and concise."
)

ARTIFACT_DRAFT_PROMPT = register(
    "03-educator-copilot", "artifact_draft", 1,
    """Draft a {artifact_type} DRAFT for course {course}.

Educator instructions:
{instructions}

Approved curriculum (the ONLY facts you may use):
{curriculum}

Class context (roster / engagement / recent results):
{class_results}

Requirements:
- Produce a {artifact_type} grounded only in the curriculum and class context above.
- Differentiate for the class context provided (e.g. supports for students who are
  behind, extensions for those ahead) when relevant.
- Make student-facing text meet WCAG 2.2 AA: clear headings, plain language, and an
  alt-text note for any image you reference.
- This is a DRAFT for educator review — do not phrase it as published or final.
"""
)
