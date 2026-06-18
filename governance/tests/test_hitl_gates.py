"""
HITL gate enforcement — the human gate cannot be bypassed by ANY agent.

For every agent, the graph compiled WITH memory must interrupt before the
human_review_gate node — i.e., there is no path from intake to finalize that runs
a consequential action without a human. This is framework-enforced, not merely
documented. Each agent is checked in its OWN subprocess so the identically-named
`agent`/`tools` packages don't collide in one interpreter.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
AGENT_DIRS = sorted(p.name for p in REPO.glob("[0-9][0-9]-*") if (p / "agent" / "graph.py").exists())

_PROBE = """
import os, sys
os.environ["EXTRACT_MODE"] = "demo"; os.environ["CONNECTOR_MODE"] = "fixture"
agent_dir = sys.argv[1]
sys.path.insert(0, agent_dir)
sys.path.insert(0, os.path.join(os.path.dirname(agent_dir), "platform_core"))
sys.path.insert(0, os.path.dirname(agent_dir))
from agent.graph import build_graph, HUMAN_GATE_NODE
g = build_graph(use_memory=True)
cfg = {"configurable": {"thread_id": "hitl-probe"}}
# Minimal seed: every agent tolerates an empty-ish dict with demo defaults.
g.invoke({"acting_user_claims": {"sub": "probe", "custom:edu_role": "STUDENT"}}, cfg)
nxt = g.get_state(cfg).next
assert nxt == (HUMAN_GATE_NODE,), f"{agent_dir}: expected interrupt before {HUMAN_GATE_NODE}, got {nxt}"
print("OK")
"""


def test_every_agent_interrupts_before_human_gate():
    assert AGENT_DIRS, "no agents discovered"
    failures = []
    for name in AGENT_DIRS:
        agent_path = str(REPO / name)
        proc = subprocess.run(
            [sys.executable, "-c", _PROBE, agent_path],
            capture_output=True, text=True,
        )
        if proc.returncode != 0 or "OK" not in proc.stdout:
            failures.append(f"{name}: {proc.stdout.strip()} {proc.stderr.strip()[-400:]}")
    assert not failures, "HITL gate not enforced for:\n" + "\n".join(failures)
