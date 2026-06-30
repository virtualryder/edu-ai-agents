"""
Agent 01 routing: clean read-only skips the human gate; a consequential send is gated.

Each check runs in its OWN subprocess — the eight agents all expose an identically
named `agent`/`agent.state` package, so importing one agent's graph in the shared
test interpreter can collide with another's (same reason `governance/tests/
test_hitl_gates.py` uses subprocesses). Isolating here keeps the assertion about
THIS agent's routing correct regardless of suite order.
"""
import subprocess
import sys
from pathlib import Path

AGENT = Path(__file__).resolve().parent.parent

_PROBE = """
import os, sys
os.environ["EXTRACT_MODE"] = "demo"; os.environ["CONNECTOR_MODE"] = "fixture"
agent_dir = sys.argv[1]; want_gate = sys.argv[2] == "gate"
sys.path.insert(0, agent_dir)
sys.path.insert(0, os.path.join(os.path.dirname(agent_dir), "platform_core"))
from agent.graph import build_graph, HUMAN_GATE_NODE
claims = {"sub": "u-stu", "custom:edu_role": "STUDENT", "student_id": "S-1"}
seed = {"acting_user_claims": claims}
if want_gate:
    seed["action_request"] = {"type": "send_message", "payload": {}}
g = build_graph(use_memory=True)
cfg = {"configurable": {"thread_id": "probe"}}
g.invoke(seed, cfg)
gated = g.get_state(cfg).next == (HUMAN_GATE_NODE,)
assert gated == want_gate, f"want_gate={want_gate} but gated={gated}"
print("OK")
"""


def _run(mode):
    proc = subprocess.run([sys.executable, "-c", _PROBE, str(AGENT), mode],
                          capture_output=True, text=True)
    assert proc.returncode == 0 and "OK" in proc.stdout, \
        f"{mode}: {proc.stdout.strip()} {proc.stderr.strip()[-400:]}"


def test_clean_read_only_does_not_gate():
    _run("nogate")


def test_consequential_send_is_gated():
    _run("gate")
