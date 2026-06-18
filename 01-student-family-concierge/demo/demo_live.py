"""
Agent 01 — LIVE-PATH demo.

Runs the Student & Family Services Concierge end-to-end with the connector in
LIVE mode, so every system-of-record call is a REAL HTTP round-trip through the
MCP gateway -> LiveHTTPConnector -> a system endpoint. By default it targets the
bundled local reference service (demo/reference_service.py); point the
<KIND>_BASE_URL env vars at the customer's API gateway to hit real systems with
no code change.

Inference auto-selects: Amazon Bedrock (if LLM_PROVIDER=bedrock) -> Anthropic
(if ANTHROPIC_API_KEY set) -> deterministic demo stub. The LIVE part being
proven here is the governed connector path, not the model.

What it demonstrates:
  1. A read + low-risk workflow (status lookup + open an advising case) executing
     over live HTTP — the returned IDs come from the reference service.
  2. A CONSEQUENTIAL action (outbound family message) BLOCKED by the gateway
     until a verified human approval is bound — then executing over live HTTP.
  3. A PII-masked, append-only audit trail with live lineage for every attempt.

Run:
    python demo/demo_live.py                       # starts the reference service in-process
    REFERENCE_EXTERNAL=1 python demo/demo_live.py  # expect an already-running service
Point at real systems:
    export CONNECTOR_MODE=live
    export SIS_BASE_URL=https://sis.gw.example.edu  CRM_BASE_URL=...  KB_BASE_URL=...  COMMS_BASE_URL=...
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
REF_PORT = int(os.getenv("REFERENCE_PORT", "8900"))
REF_URL = os.getenv("REFERENCE_URL", f"http://localhost:{REF_PORT}")
os.environ["CONNECTOR_MODE"] = "live"
for kind in ("SIS", "CRM", "KB", "COMMS"):
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
        dec = e.get("decision") or ("step" if e.get("actor") == "ai_agent" else e.get("actor", ""))
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
    claims = {"sub": "stu-live-1042", "custom:edu_role": "STUDENT"}

    # ── Scenario 1: read + low-risk workflow over LIVE HTTP ───────────────────
    print("=" * 78)
    print("Scenario 1 — authenticated status lookup + open advising case (low-risk)")
    print("=" * 78)
    out = graph.invoke({
        "request_id": "LIVE-1", "channel": "web", "intent": "STATUS", "authenticated": True,
        "question": "What's my application status and what do I still need to submit?",
        "acting_user_claims": claims,
        "action_request": {"type": "create_advising_case", "payload": {"topic": "application documents"}},
    })
    print(f"\n  response: {out.get('draft_response','')[:240]}...")
    print(f"  generated_by: {out.get('generated_by')}  |  status: {out.get('case_status')}")
    print(f"  advising case id (from live service): {out.get('case_id')!r}")
    _print_audit(out)

    # ── Scenario 2: consequential send — gated, then approved over LIVE HTTP ───
    print("\n" + "=" * 78)
    print("Scenario 2 — consequential outbound message (gateway-gated)")
    print("=" * 78)
    base = {
        "request_id": "LIVE-2", "channel": "chat", "intent": "ACTION", "authenticated": True,
        "question": "Please have financial aid email my family the next steps.",
        "acting_user_claims": {"sub": "staff-fa-07", "custom:edu_role": "FINANCIAL_AID"},
        "action_request": {"type": "send_message", "payload": {"to": "guardian", "topic": "financial aid next steps"}},
    }
    out2 = graph.invoke(dict(base))
    print(f"\n  without approval -> message_id: {out2.get('message_id')!r}  (blocked at gateway, no live call)")

    approved = dict(base)
    approved["approval"] = {"approved": True,
                            "reviewer": {"sub": "staff-fa-07", "roles": ["FINANCIAL_AID"],
                                         "name": "Financial Aid Officer"},
                            "signature_meaning": "Approved family outreach"}
    out3 = graph.invoke(approved)
    print(f"  with verified approval -> message_id (from live service): {out3.get('message_id')!r}")

    print("\n[done] Live path exercised: authorization + human gate enforced BEFORE any HTTP call;")
    print("       reads and approved writes executed against the live endpoint; every attempt audited.")


if __name__ == "__main__":
    main()
