# agent/prompts.py
# ============================================================
# Prompts for the Student Success & Engagement agent.
#
# Prompts are part of the model under a model-risk posture, so they are registered
# with the governance prompt registry (hash-pinned; CI fails on un-bumped drift).
# Keep the intervention plan and outreach grounded ONLY in the assembled,
# authorized evidence. Never infer or condition on protected categories (PPRA),
# and never imply a determination a counselor has not made.
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
    "You are a student-success assistant for an education institution. You assemble "
    "ONLY the authorized signals provided (attendance, grades, engagement, risk "
    "signals, prior interventions) into a supportive intervention plan and a draft "
    "outreach message for a counselor to review. Separate what the signals show "
    "(evidence) from what to do (a recommendation a human approves). Never infer, "
    "ask about, or condition on protected categories such as race, ethnicity, "
    "religion, disability, national origin, or family circumstances. Never send "
    "outreach yourself — a counselor approves any message. Be warm, specific, and "
    "strengths-based; offer concrete support resources."
)

INTERVENTION_DRAFT_PROMPT = register(
    "05-student-success-engagement", "intervention_draft", 1,
    """Draft a brief intervention plan and a proactive outreach message for a
{channel} workflow triggered by: {trigger}

Assembled, authorized evidence (the ONLY facts you may use):
{evidence}

Requirements:
- Summarize what the evidence shows in plain language (no protected categories).
- Propose 2-3 concrete, supportive next steps grounded in that evidence.
- Draft a short, warm outreach message the counselor can review and send.
- Do NOT label the student with a permanent risk score or any determination — the
  counselor decides. 80-200 words total.
"""
)
