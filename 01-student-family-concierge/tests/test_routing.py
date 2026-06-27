"""Agent 01 routing: clean read-only skips the human gate; a consequential send is gated."""
import os
import sys
from pathlib import Path

import pytest

AGENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AGENT))
sys.path.insert(0, str(AGENT.parent / "platform_core"))
os.environ.setdefault("EXTRACT_MODE", "demo")
os.environ.setdefault("CONNECTOR_MODE", "fixture")

pytest.importorskip("langgraph")
from agent.graph import build_graph, HUMAN_GATE_NODE

_CLAIMS = {"sub": "u-stu", "custom:edu_role": "STUDENT", "student_id": "S-1"}


def _next(seed, thread):
    g = build_graph(use_memory=True)
    cfg = {"configurable": {"thread_id": thread}}
    g.invoke(seed, cfg)
    return g.get_state(cfg).next


def test_clean_read_only_does_not_gate():
    assert _next({"acting_user_claims": _CLAIMS}, "clean") != (HUMAN_GATE_NODE,)


def test_consequential_send_is_gated():
    seed = {"acting_user_claims": _CLAIMS, "action_request": {"type": "send_message", "payload": {}}}
    assert _next(seed, "conseq") == (HUMAN_GATE_NODE,)
