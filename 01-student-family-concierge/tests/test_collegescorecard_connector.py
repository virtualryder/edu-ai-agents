"""
Tests for the College Scorecard real institution-facts connector (Agent 01).

Two layers (mirrors the hcls openFDA connector tests):
  * Offline/deterministic (default): monkeypatch the connector's HTTP with recorded
    real-structure cassettes. No network. These are the CI source of truth and cover
    mapping, get + search, duplicate detection, fail-closed writes, factory routing,
    the governed round-trip through the EDU gateway (read allowed for the concierge
    role / consequential outbound message human-gated / least-privilege deny), and
    fail-closed student-PII masking (FERPA/COPPA).
  * Opt-in live smoke (RUN_LIVE_SCORECARD=1): actually calls api.data.gov and asserts
    the same governed read against real institution data. Skipped by default so CI
    needs no network and no API key.
"""
import json
import os
import sys
from pathlib import Path

import pytest

AGENT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(AGENT))
sys.path.insert(0, str(AGENT.parent / "platform_core"))

from edu_agent_platform.connectors import collegescorecard  # noqa: E402
from edu_agent_platform.connectors.factory import get_connector  # noqa: E402
from edu_agent_platform.mcp_gateway import MCPGateway  # noqa: E402
from edu_agent_platform.pii_masker import mask  # noqa: E402

_FIX = AGENT / "tests" / "fixtures"
_ONE = json.loads((_FIX / "collegescorecard_sample.json").read_text(encoding="utf-8"))
_DUPES = json.loads((_FIX / "collegescorecard_dupes_sample.json").read_text(encoding="utf-8"))

AGENT_ID = "01-student-family-concierge"
# A financial-aid staff member helping a family compare college costs: entitled to
# read approved content (kb.search_policies) AND to send family outreach — so the
# consequential send is human-gated (PENDING_APPROVAL), not merely denied.
FINANCIAL_AID = {"sub": "fa-officer-1", "custom:edu_role": "FINANCIAL_AID"}
STUDENT = {"sub": "stu-1", "custom:edu_role": "STUDENT"}

CScC = collegescorecard.CollegeScorecardConnector


@pytest.fixture(autouse=True)
def _governed_mode(monkeypatch):
    monkeypatch.setenv("CONNECTOR_MODE", "live")
    monkeypatch.setenv("CONCIERGE_SOURCE", "collegescorecard")
    monkeypatch.setenv("DISABLE_SECRETS_MANAGER", "1")


def _serve(monkeypatch, payload):
    """Monkeypatch the connector's HTTP layer to return a cassette (offline)."""
    monkeypatch.setattr(CScC, "_get", lambda self, params: payload)


# ── Mapping ──────────────────────────────────────────────────────────────────

def test_maps_real_scorecard_record_to_institution_shape():
    rec = CScC._map_record(_ONE["results"][0])
    assert rec["institution_name"] == "University of Washington-Seattle Campus"
    assert rec["city"] == "Seattle" and rec["state"] == "WA"
    assert rec["tuition_in_state"] == 12973 and rec["tuition_out_of_state"] == 43209
    assert rec["median_debt"] == 14615 and rec["admission_rate"] == 0.3915
    assert rec["valid"] is True
    # fixture core keys preserved (kb.search_policies result shape)
    assert rec["title"] == rec["institution_name"] and rec["ref"] == "236948"
    # summary claims ONLY record facts (grounding-friendly for the scored eval)
    assert "University of Washington-Seattle Campus" in rec["summary"]
    assert "$12,973" in rec["summary"] and "39%" in rec["summary"]


# ── Read: get + search (positive match) ──────────────────────────────────────

def test_get_institution_returns_mapped_record(monkeypatch):
    _serve(monkeypatch, _ONE)
    rec = CScC().get_institution(name="University of Washington")
    assert rec["valid"] is True and rec["state"] == "WA"


def test_search_institutions_positive_match(monkeypatch):
    _serve(monkeypatch, _DUPES)
    rows = CScC().search_institutions(state="WA", limit=5)
    assert len(rows) == 2
    assert all(r["institution_name"].startswith("University of Washington") for r in rows)


def test_search_policies_dispatches_state_search(monkeypatch):
    _serve(monkeypatch, _DUPES)
    out = CScC().search_policies(query="community colleges in Washington")
    assert out["intent"] == "SEARCH" and out["results"]
    assert out["source"].startswith("U.S. Department of Education")


# ── Duplicate / near-duplicate detection ─────────────────────────────────────

def test_duplicate_institution_detected(monkeypatch):
    _serve(monkeypatch, _DUPES)
    rows = CScC().search_institutions(state="WA")
    keys = {CScC.duplicate_key(r) for r in rows}
    # Same institution id under two name variants -> one identity key -> duplicate.
    assert len(keys) == 1 and next(iter(keys)) == "id:236948"


def test_near_miss_same_name_different_state_not_duplicate():
    a = CScC._map_record({"id": 100, "school.name": "Lincoln University",
                          "school.city": "Jefferson City", "school.state": "MO"})
    b = CScC._map_record({"id": 200, "school.name": "Lincoln University",
                          "school.city": "Lincoln University", "school.state": "PA"})
    assert CScC.duplicate_key(a) != CScC.duplicate_key(b)


# ── Query classifier (the concierge's real institution-question router) ───────

def test_classify_query_intents():
    assert collegescorecard.classify_query("How much is tuition at Rice University?") == "LOOKUP"
    assert collegescorecard.classify_query("community colleges in California") == "SEARCH"
    assert collegescorecard.classify_query("What is my application status?") == "STATUS"


# ── Writes are fail-closed (read-only public source) ─────────────────────────

def test_update_enrollment_record_raises():
    with pytest.raises(NotImplementedError):
        CScC().update_enrollment_record(student_id="X")


def test_send_message_raises():
    with pytest.raises(NotImplementedError):
        CScC().send_message(to="family")


# ── Factory routing ──────────────────────────────────────────────────────────

def test_factory_routes_kb_to_collegescorecard():
    assert type(get_connector("kb")).__name__ == "CollegeScorecardConnector"


def test_switch_is_guarded_and_fixture_default(monkeypatch):
    # The switch is additive + guarded: without CONCIERGE_SOURCE, live kb does NOT
    # route to Scorecard (stays a live stub / HTTP connector).
    monkeypatch.delenv("CONCIERGE_SOURCE", raising=False)
    assert type(get_connector("kb")).__name__ != "CollegeScorecardConnector"
    # The switch never hijacks a non-kb kind even when it is set.
    monkeypatch.setenv("CONCIERGE_SOURCE", "collegescorecard")
    assert type(get_connector("crm")).__name__ != "CollegeScorecardConnector"
    # Fixture default is unaffected (no regression): kb is the fixture connector.
    monkeypatch.setenv("CONNECTOR_MODE", "fixture")
    assert type(get_connector("kb")).__name__ == "FixtureGeneric"


# ── Governed round-trip through the real gateway ─────────────────────────────

def test_governed_read_allowed_send_gated_least_privilege_denied(monkeypatch):
    _serve(monkeypatch, _ONE)
    gw = MCPGateway()

    # Read of a real institution record is ALLOWED for the concierge staff role.
    read = gw.invoke(user_claims=FINANCIAL_AID, agent_id=AGENT_ID,
                     tool="kb.search_policies", args={"school_name": "University of Washington"})
    assert read.allowed and read.decision == "ALLOW"
    assert read.result["results"][0]["institution_name"] == "University of Washington-Seattle Campus"
    assert read.audit_id and read.scope == ["kb.search_policies"]

    # A consequential outbound family message is human-gated (withheld until approval).
    send = gw.invoke(user_claims=FINANCIAL_AID, agent_id=AGENT_ID,
                     tool="comms.send_message", args={"to": "guardian", "topic": "cost comparison"})
    assert not send.allowed and send.decision == "PENDING_APPROVAL" and send.requires_approval

    # Least privilege: a student is NOT entitled to send outbound messages -> DENY,
    # even though the agent is granted the tool (agent may never exceed the user).
    denied = gw.invoke(user_claims=STUDENT, agent_id=AGENT_ID,
                       tool="comms.send_message", args={"to": "guardian"})
    assert not denied.allowed and denied.decision == "DENY"


def test_governed_read_allowed_for_student(monkeypatch):
    _serve(monkeypatch, _ONE)
    gw = MCPGateway()
    read = gw.invoke(user_claims=STUDENT, agent_id=AGENT_ID,
                     tool="kb.search_policies", args={"query": "University of Washington"})
    assert read.allowed and read.result["results"]


# ── Fail-closed student-PII masking on ingested text (FERPA/COPPA) ───────────

def test_pii_masking_failclosed_on_ingested_text(monkeypatch):
    _serve(monkeypatch, _ONE)
    rec = CScC().get_institution(name="University of Washington")
    # Scorecard carries no PII; stress the control with injected identifiers to
    # prove the masker runs fail-closed on ingested text before it is logged.
    stressed = rec["summary"] + " advisor jane.doe@example.edu SSN 123-45-6789 STU-00098765"
    masked = mask(stressed)
    assert "123-45-6789" not in masked
    assert "jane.doe@example.edu" not in masked
    assert "STU-00098765" not in masked
    # Institution facts (public) survive masking so the answer stays useful.
    assert "University of Washington-Seattle Campus" in masked


# ── Opt-in live smoke against the real College Scorecard API ─────────────────

@pytest.mark.skipif(os.getenv("RUN_LIVE_SCORECARD", "") not in ("1", "true", "yes"),
                    reason="set RUN_LIVE_SCORECARD=1 to hit the real api.data.gov")
def test_live_scorecard_governed_read():
    gw = MCPGateway()
    r = gw.invoke(user_claims=FINANCIAL_AID, agent_id=AGENT_ID,
                  tool="kb.search_policies", args={"school_name": "University of Washington"})
    assert r.allowed and r.result["results"]
    top = r.result["results"][0]
    assert top["institution_name"] and top["state"]  # real institution facts
    assert r.audit_id                                 # audited
