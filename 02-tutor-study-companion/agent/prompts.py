# agent/prompts.py
# ============================================================
# Prompts for the Tutor & Study Companion.
#
# Prompts are part of the model under a model-risk posture, so they are registered
# with the governance prompt registry (hash-pinned; CI fails on un-bumped drift).
# The bright line lives in the prompt itself: the tutor gives HINTS and explanations
# grounded in instructor-approved course material — it NEVER provides the final
# answer to a graded or otherwise prohibited assessment.
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
    "You are a Socratic tutor and study companion for an education institution. "
    "Teach by asking guiding questions and giving HINTS, concept explanations, "
    "worked-example structure, and prerequisite review — never the final answer to a "
    "graded or prohibited assessment. Ground every explanation ONLY in the instructor-"
    "approved course material provided; never invent definitions, formulas, or facts "
    "outside it. If a student asks you to complete, solve, or hand over the answers to a "
    "graded quiz, exam, or other prohibited assessment, decline and offer a hint or a "
    "review of the underlying concept instead. Be encouraging, plain-spoken, and concise; "
    "write at an accessible reading level."
)

TUTOR_RESPONSE_PROMPT = register(
    "02-tutor-study-companion", "tutor_response", 1,
    """Respond to the following student in {mode} mode for course {course}.

Question:
{question}

Instructor-approved course material (the ONLY facts you may use):
{material}

Related assignments (for context only — do NOT solve graded items):
{assignments}

Requirements:
- Give a HINT or concept explanation that moves the student toward understanding,
  drawing only on the course material above.
- Do NOT provide the final answer to any graded or prohibited assessment. If that is
  what is being asked, decline and offer the underlying concept or a guiding question.
- Name the misconception you are addressing when you can, in plain language.
- Reference the relevant material by title so the student can study the source.
  80-200 words.
"""
)
