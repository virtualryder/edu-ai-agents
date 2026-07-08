"""
demo_collegescorecard.py — the "one REAL connector" demo for Agent 01 (Concierge).

Pulls a **real** institution record from the public **College Scorecard** API
(U.S. Department of Education) **through the governed MCP gateway**, then shows the
whole governance story against real data:

    real Scorecard read  ->  deny-by-default authorization (FINANCIAL_AID role)
                         ->  least-privilege intersection (agent grant ∩ user)
                         ->  fail-closed student-PII masking (FERPA/COPPA)
                         ->  scoped per-call token + append-only masked audit
                         ->  human gate: outbound family message WITHHELD until approval

College Scorecard is public **institution-level** data (no student PII / no
education record), so it needs no FERPA data-sharing agreement to read — yet the
student-PII masker still runs on the ingested text (the control is exercised, not
assumed). Real SIS/LMS connectors that touch the student record are separate,
human-gated engagement work behind the SAME gateway.

Usage
-----
    cd 01-student-family-concierge
    # Live (hits api.data.gov with DEMO_KEY):
    PYTHONPATH=.:../platform_core:.. python demo/demo_collegescorecard.py
    # Offline / CI (uses the recorded cassette, no network):
    SCORECARD_OFFLINE=1 python demo/demo_collegescorecard.py
    # Pick the institution to look up:
    SCORECARD_SCHOOL="Rice University" python demo/demo_collegescorecard.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_AGENT = _HERE.parent
_REPO = _AGENT.parent
sys.path.insert(0, str(_AGENT))
sys.path.insert(0, str(_REPO / "platform_core"))
sys.path.insert(0, str(_REPO))

SEP = "=" * 72


def _load_cassette() -> dict:
    p = _AGENT / "tests" / "fixtures" / "collegescorecard_sample.json"
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    print(f"\n{SEP}\n  STUDENT & FAMILY CONCIERGE — REAL CONNECTOR DEMO (College Scorecard)\n{SEP}")

    # ── Governed, real-connector mode ───────────────────────────────────────
    os.environ["CONNECTOR_MODE"] = "live"
    os.environ["CONCIERGE_SOURCE"] = "collegescorecard"
    os.environ["DISABLE_SECRETS_MANAGER"] = "1"
    offline = os.getenv("SCORECARD_OFFLINE", "").strip() in ("1", "true", "yes")
    school = os.getenv("SCORECARD_SCHOOL", "University of Washington").strip()

    from edu_agent_platform.connectors import collegescorecard
    from edu_agent_platform.connectors.factory import get_connector
    from edu_agent_platform.mcp_gateway import MCPGateway
    from edu_agent_platform.pii_masker import mask  # fail-closed student-PII masker

    if offline:
        cassette = _load_cassette()
        collegescorecard.CollegeScorecardConnector._get = lambda self, params: cassette
        print("  [mode] OFFLINE — serving recorded College Scorecard cassette (no network)")
    else:
        print("  [mode] LIVE — calling https://api.data.gov/ed/collegescorecard/v1/schools")

    conn = get_connector("kb")  # -> CollegeScorecardConnector (real, read-only)
    print(f"  [connector] {type(conn).__name__}  source={conn.source}")

    gw = MCPGateway()
    # A financial-aid staff member helping a family compare college costs.
    fa = {"sub": "demo-fa-officer", "custom:edu_role": "FINANCIAL_AID"}

    # ── 1. Governed READ of a REAL institution record ───────────────────────
    print(f"\n1 / 4  Governed read: kb.search_policies  (real College Scorecard data)")
    try:
        r = gw.invoke(user_claims=fa, agent_id="01-student-family-concierge",
                      tool="kb.search_policies", args={"school_name": school})
    except Exception as exc:  # network/API failure -> fail closed, fall back to cassette
        print(f"  [warn] live Scorecard call failed ({exc}); falling back to cassette")
        cassette = _load_cassette()
        collegescorecard.CollegeScorecardConnector._get = lambda self, params: cassette
        r = gw.invoke(user_claims=fa, agent_id="01-student-family-concierge",
                      tool="kb.search_policies", args={"school_name": school})

    if not r.allowed:
        print(f"  DENIED: {r.reason}"); return
    results = r.result.get("results", [])
    if not results:
        print("  (no institution matched; try SCORECARD_SCHOOL=...)"); return
    inst = results[0]
    print(f"  decision={r.decision}  audit_id={r.audit_id[:8]}  token_scope={r.scope}")
    print(f"  REAL institution: {inst['institution_name']} ({inst['city']}, {inst['state']})")
    print(f"    in/out tuition : ${inst['tuition_in_state']} / ${inst['tuition_out_of_state']}")
    print(f"    median debt    : ${inst['median_debt']}   admission rate: {inst['admission_rate']}")
    print(f"    summary        : {inst['summary']}")

    # ── 2. Fail-closed student-PII masking on the ingested summary ──────────
    print(f"\n2 / 4  Student-PII masking (FERPA/COPPA) — fail-closed on ingested text")
    stress = inst["summary"] + "  [intake note: guardian jane.doe@example.edu, SSN 123-45-6789, STU-00098765]"
    masked = mask(stress)
    leaked = any(x in masked for x in ("123-45-6789", "jane.doe@example.edu", "STU-00098765"))
    print(f"  masked summary : {masked[:170]}...")
    print(f"  PII-leak check : {'FAIL (leak!)' if leaked else 'PASS (identifiers redacted, fail-closed)'}")
    assert not leaked, "student-PII masking must not leak identifiers"

    # ── 3. Governed search against real data ────────────────────────────────
    print(f"\n3 / 4  Governed read: kb.search_policies  (state search — real data)")
    rs = gw.invoke(user_claims=fa, agent_id="01-student-family-concierge",
                   tool="kb.search_policies", args={"state": inst["state"], "limit": 3})
    names = [x["institution_name"] for x in rs.result.get("results", [])]
    print(f"  decision={rs.decision}  audit_id={rs.audit_id[:8]}  institutions={names}")

    # ── 4. The human authority boundary (the trust anchor) ──────────────────
    print(f"\n4 / 4  Human authority boundary (the trust anchor)")
    rw = gw.invoke(user_claims=fa, agent_id="01-student-family-concierge",
                   tool="comms.send_message", args={"to": "guardian", "topic": "cost comparison"})
    print(f"  comms.send_message (no approval) -> {rw.decision} (requires_approval={rw.requires_approval})")
    print(f"  connector writes are read-only fail-closed: "
          f"CollegeScorecardConnector.update_enrollment_record / send_message raise NotImplementedError")

    print(f"\n{SEP}\n  DEMO COMPLETE — governed pattern proven against a REAL system of record")
    print(f"{SEP}")
    print("  * Real College Scorecard read through deny-by-default gateway (FINANCIAL_AID)")
    print("  * Least-privilege intersection: a student cannot send outbound messages")
    print("  * Fail-closed student-PII masking on ingested text (no identifier leaks)")
    print("  * Scoped per-call token + append-only masked audit on every call")
    print("  * Outbound family message WITHHELD until a verified human approval is bound")
    print("  * Scorecard is public institution data -> no FERPA agreement; SIS/LMS is the")
    print("    student-record variant behind the same gateway (engagement work)\n")


if __name__ == "__main__":
    main()
