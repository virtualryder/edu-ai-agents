"""
Agent 04 — LIVE-PATH demo.

Runs the Assessment, Grading & Feedback agent end-to-end with the connector in
LIVE mode, so every system-of-record call is a REAL HTTP round-trip through the
MCP gateway -> LiveHTTPConnector -> a system endpoint. By default it targets the
bundled local reference service (demo/reference_service.py); point the
<KIND>_BASE_URL env vars at the customer's API gateway to hit real systems (Canvas
LMS + assessment engine) with no code change.

Inference auto-selects: Amazon Bedrock (if LLM_PROVIDER=bedrock) -> Anthropic
(if ANTHROPIC_API_KEY set) -> deterministic demo stub. The LIVE part being
proven here is the governed connector path, not the model.

Bright line: the educator owns the grade. The agent evaluates against the rubric
and drafts feedback; it never releases a final/high-stakes grade autonomously.

What it demonstrates:
  1. A read/analysis workflow (evaluate an essay against the rubric + draft
     feedback) executing over live HTTP — the evaluation came from the service.
  2. A CONSEQUENTIAL action (releasing a final grade) BLOCKED by the gateway
     until a verified EDUCATOR approval is bound — then executing over live HTTP
     and returning grade_id GR-live-0001.
  3. A PII-masked, append-only audit trail with live lineage for every attempt.

Run:
    python demo/demo_live.py                       # starts the reference service in-process
    REFERENCE_EXTERNAL=1 python demo/demo_live.py  # expect an already-running service
Point at real systems:
    export CONNECTOR_MODE=live
    export LMS_BASE_URL=https://gw.example.edu/lms  ASSESSMENT_BASE_URL=https://gw.example.edu/assessment
"""
from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_AGENT = _HERE.parent
sys.path.insert(0, str(_AGENT))
sys.path.insert(0, str(_AGENT.parent / "platform_core"))
sys.path.insert(0, str(_AGENT.parent))

# ── Configure the LIVE connector path BEFORE importing the agent ───────────────
REF_PORT = int(os.getenv("REFERENCE_PORT", "8901"))
REF_URL = os.getenv("REFERENCE_URL", f"http://localhost:{REF_PORT}")
os.environ["CONNECTOR_MODE"] = "live"
for kind in ("LMS", "ASSESSMENT"):
    os.environ.setdefault(f"{kind}_BASE_URL", REF_URL)  # default to the reference service
# Do NOT force EXTRACT_MODE=demo — let generation auto-select the provider.


def _start_reference_service() -> None:
    from demo.reference_service import Handler
    from http.server import ThreadingHTTPServer

    srv = ThreadingHTTPServer(("127.0.0.1", REF_PORT), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.4)
    print(f"[setup] started local reference service on :{REF_PORT}")


def _inference_path() -> str:
    prov = os.getenv("LLM_PROVIDER", "anthropic").strip().lower()
    if os.getenv("EXTRACT_MODE", "").lower() == "demo":
        return "deterministic demo stub"
    if prov == "bedrock":
        return "Amazon Bedrock (in-account)"
    if os.getenv("ANTHROPIC_API_KEY"):
        return "Anthropic API"
    return "deterministic demo stub (no model credentials found)"


def _print_audit(state) -> None:
    print("  audit trail (gateway + workflow):")
    for e in state.get("audit_trail", []):
        line = f"    - {e.get('node','')}: {e.get('action','')}"
        srcs = e.get("data_sources_accessed")
        if srcs:
            line += f"  [sources: {', '.join(srcs)}]"
        print(line)


def main() -> None:
    if os.getenv("REFERENCE_EXTERNAL", "").lower() not in ("1", "true", "yes"):
        _start_reference_service()

    print(f"[setup] CONNECTOR_MODE=live -> {REF_URL}  (real HTTP per tool call)")
    print(f"[setup] inference path: {_inference_path()}\n")

    from agent.graph import build_graph
    graph = build_graph(use_memory=False)
    claims = {"sub": "edu-live-07", "custom:edu_role": "EDUCATOR"}

    # ── Scenario 1: evaluate + draft feedback over LIVE HTTP (read/analysis) ───
    print("=" * 78)
    print("Scenario 1 — evaluate an essay against the rubric + draft feedback (read/analysis)")
    print("=" * 78)
    out = graph.invoke({
        "request_id": "LIVE-1", "channel": "lms", "course": "ENG-101",
        "submission_id": "SUB-live-0001", "rubric_ref": "RUB-live-101",
        "acting_user_claims": claims,
    })
    evaluation = out.get("evaluation", {}) or {}
    print(f"\n  recommended_action: {out.get('recommended_action')}  |  status: {out.get('case_status')}")
    print(f"  evaluation (from live service): served_by={evaluation.get('served_by')!r}  "
          f"raw_total={evaluation.get('raw_total')}/{evaluation.get('max_total')}  "
          f"confidence={evaluation.get('confidence')}")
    print(f"  generated_by: {out.get('generated_by')}")
    print(f"  draft_feedback: {out.get('draft_feedback','')[:200]}...")
    _print_audit(out)

    # ── Scenario 2: consequential grade release — gated, then approved (LIVE) ──
    print("\n" + "=" * 78)
    print("Scenario 2 — release a final grade (consequential, educator-gated)")
    print("=" * 78)
    base = {
        "request_id": "LIVE-2", "channel": "lms", "course": "ENG-101",
        "submission_id": "SUB-live-0003", "rubric_ref": "RUB-live-101",
        "acting_user_claims": claims,
        "action_request": {"type": "release_grade",
                           "payload": {"submission_id": "SUB-live-0003", "rubric_ref": "RUB-live-101"}},
    }
    out2 = graph.invoke(dict(base))
    print(f"\n  without approval -> grade_id: {out2.get('grade_id')!r}  (blocked at gateway, no live call)")

    approved = dict(base)
    approved["approval"] = {"approved": True,
                            "reviewer": {"sub": "edu-live-07", "roles": ["EDUCATOR"],
                                         "name": "Course Educator"},
                            "signature_meaning": "Approved release of final grade"}
    out3 = graph.invoke(approved)
    print(f"  with verified approval -> grade_id (from live service): {out3.get('grade_id')!r}")

    print("\n[done] Live path exercised: authorization + human gate enforced BEFORE any HTTP call;")
    print("       the educator owns the grade — the agent never releases autonomously; every attempt audited.")


if __name__ == "__main__":
    main()
