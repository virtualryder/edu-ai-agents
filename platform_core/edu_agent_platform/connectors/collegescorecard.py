"""
College Scorecard connector — a REAL external institution-facts source (read-only).

This is the "one real connector per vertical" build for the EDU suite: it gives
the Student & Family Concierge (Agent 01) a genuine, public **system of record**
for institution / cost / aid facts instead of a fixture. It proves the governed
pattern (deny-by-default gateway -> least-privilege intersection -> scoped token ->
student-PII masking -> human gate -> append-only audit) against a real API.

  Endpoint : https://api.data.gov/ed/collegescorecard/v1/schools
  Docs     : https://collegescorecard.ed.gov/data/documentation/
  Data     : public U.S. Department of Education institution data — cost, aid,
             admissions. **No student PII / no education record** (this is
             institution-level, not student-level, data), so it needs no FERPA
             data-sharing agreement to read.

Design contract (matches connectors/base.py GenericConnector so it is drop-in
interchangeable with FixtureGeneric / LiveHTTPConnector for the `kb` kind):

  * search_policies                 -> the gateway entry point the concierge is
    granted (kb.search_policies). Dispatches a free-text / structured query to a
    real institution lookup or state search. READ-ONLY.
  * get_institution / search_institutions -> the typed read API (also used by the
    demo, tests, and the scored eval). READ-ONLY.
  * update_enrollment_record / send_message -> NOT SUPPORTED here. College
    Scorecard is a read-only public source; student-record writes and outbound
    family messages target the institution's own **SIS / comms** systems and stay
    **human-gated at the gateway**. Calling them raises, which is the correct,
    fail-closed behavior: the agent can read the real world but cannot write to it.

  * stdlib-only HTTP (urllib), timeouts, fail-closed (any error raises).
  * Student-PII masking still runs downstream on the composed summary even though
    Scorecard carries no PII — the control is exercised, not assumed (FERPA/COPPA).

Real SIS/LMS connectors (PowerSchool, Banner, Canvas, ...) that touch the student
education record are a separate, human-gated engagement with FERPA sign-off; this
public institution-facts source is the low-blast-radius reference implementation.
"""
from __future__ import annotations

import os
import re
import json
from typing import Any, Dict, List, Optional
from urllib import request as _urllib_request
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from .base import GenericConnector

_DEFAULT_BASE = "https://api.data.gov/ed/collegescorecard/v1"
_TIMEOUT = 20

SOURCE = "U.S. Department of Education College Scorecard (public institution data)"

# The real Scorecard fields the concierge needs, returned as FLAT dotted keys.
_FIELDS = ",".join([
    "id",
    "school.name",
    "school.city",
    "school.state",
    "latest.cost.tuition.in_state",
    "latest.cost.tuition.out_of_state",
    "latest.aid.median_debt.completers.overall",
    "latest.admissions.admission_rate.overall",
])

# Minimal state map so a free-text query mentioning a state routes to a search.
_STATES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY",
}


def _api_key() -> str:
    """College Scorecard API key. Env EDU_SCORECARD_API_KEY or Secrets Manager;
    defaults to DEMO_KEY (rate-limited, fine for demo/CI/tests)."""
    key = os.getenv("EDU_SCORECARD_API_KEY", "")
    if key:
        return key
    try:
        from edu_agent_platform.secrets import get_secret
        return get_secret("edu_scorecard_api_key", default="DEMO_KEY") or "DEMO_KEY"
    except Exception:
        return "DEMO_KEY"


def classify_query(text: Optional[str]) -> str:
    """
    Deterministic query router for the concierge's institution questions.

    The concierge has no LLM intent classifier (intent is supplied by the caller),
    so this is the *real* routing logic used to pick the connector read for a
    natural-language institution question. Returned intents:

      STATUS  -> a personal application/record question -> route to the SIS, NOT
                 to this public institution-facts source.
      SEARCH  -> list/compare institutions (e.g. by state) -> search_institutions.
      LOOKUP  -> facts about one named institution (cost/aid/admissions) ->
                 get_institution.

    The scored eval measures this classifier's accuracy against a labeled set.
    """
    raw = text or ""
    t = raw.lower()
    if any(k in t for k in (
        "my application", "my status", "application status", "did you receive",
        "my transcript", "my file", "my account", "my aid", "my fafsa",
    )):
        return "STATUS"
    # A full state NAME anywhere (word-bounded), or an explicit uppercase 2-letter
    # state ABBREVIATION as its own token in the original text ("colleges in WA").
    # The abbreviation is matched only in the original case so it does not collide
    # with common lowercase English words (in, or, me, hi, pa, ...).
    mentions_state_name = bool(
        re.search(r"\b(?:" + "|".join(re.escape(n) for n in _STATES) + r")\b", t)
    )
    mentions_state_abbr = bool(re.search(r"\b(?:" + "|".join(_STATES.values()) + r")\b", raw))
    if mentions_state_name or mentions_state_abbr or any(k in t for k in (
        "colleges in", "schools in", "universities in", "list ", "compare",
        "cheapest", "options", "which colleges", "which schools", "near me",
    )):
        return "SEARCH"
    return "LOOKUP"


class CollegeScorecardConnector(GenericConnector):
    """Real, read-only College Scorecard connector, backing the `kb` kind."""

    kind = "kb"
    source = SOURCE

    def __init__(self, base_url: str = "", api_key: str = "") -> None:
        super().__init__("kb")
        self._base_url = (base_url or os.getenv("SCORECARD_BASE_URL", _DEFAULT_BASE)).rstrip("/")
        self._api_key = api_key  # empty -> resolved lazily (env / secrets / DEMO_KEY)

    # -- HTTP -----------------------------------------------------------------
    def _get(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """GET /schools with params. Fail-closed: any error raises."""
        key = self._api_key or _api_key()
        params = {"api_key": key, "fields": _FIELDS, **params}
        url = f"{self._base_url}/schools?{urlencode(params)}"
        req = _urllib_request.Request(url, headers={"Accept": "application/json"}, method="GET")
        try:
            with _urllib_request.urlopen(req, timeout=_TIMEOUT) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 404:
                return {"results": []}
            raise RuntimeError(f"College Scorecard API error [{exc.code}] for {url}: {exc}") from exc
        except (URLError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"College Scorecard API call failed for {url}: {exc}") from exc

    # -- Mapping a raw Scorecard record -> the suite's institution shape -------
    @staticmethod
    def _map_record(r: Dict[str, Any]) -> Dict[str, Any]:
        name = r.get("school.name", "") or ""
        city = r.get("school.city", "") or ""
        state = r.get("school.state", "") or ""
        rec = {
            # fixture core keys (kb.search_policies result shape) preserved so
            # agent code that expects the kb shape still works unchanged:
            "title": name,
            "ref": str(r.get("id", "")),
            "relevance": 1.0,
            # real institution fields added by this connector:
            "id": str(r.get("id", "")),
            "institution_name": name,
            "city": city,
            "state": state,
            "tuition_in_state": r.get("latest.cost.tuition.in_state"),
            "tuition_out_of_state": r.get("latest.cost.tuition.out_of_state"),
            "median_debt": r.get("latest.aid.median_debt.completers.overall"),
            "admission_rate": r.get("latest.admissions.admission_rate.overall"),
            "source": SOURCE,
            "valid": bool(name),
        }
        rec["summary"] = CollegeScorecardConnector._compose_summary(rec)
        return rec

    @staticmethod
    def _compose_summary(rec: Dict[str, Any]) -> str:
        """
        Compose a factual, grounding-friendly summary that claims ONLY what the
        record contains (this is what the grounding eval scores against).
        """
        def money(v: Any) -> str:
            return f"${int(v):,}" if isinstance(v, (int, float)) else "not reported"

        def pct(v: Any) -> str:
            return f"{round(float(v) * 100):.0f}%" if isinstance(v, (int, float)) else "not reported"

        name = rec.get("institution_name") or "This institution"
        loc = ", ".join(x for x in (rec.get("city"), rec.get("state")) if x)
        where = f" ({loc})" if loc else ""
        return (
            f"{name}{where} reports in-state tuition of {money(rec.get('tuition_in_state'))} "
            f"and out-of-state tuition of {money(rec.get('tuition_out_of_state'))}. "
            f"The reported median debt of completers is {money(rec.get('median_debt'))} "
            f"and the overall admission rate is {pct(rec.get('admission_rate'))}. "
            f"(Source: College Scorecard, id {rec.get('id') or 'n/a'}.)"
        )

    @staticmethod
    def duplicate_key(rec: Dict[str, Any]) -> str:
        """
        Transparent identity key for duplicate / near-duplicate institution
        detection: the Scorecard institution id when present, else a normalized
        name+city+state. Two records with the same key are the same institution;
        a same-named campus in a different city/state has a different key.
        """
        rid = str(rec.get("id") or "").strip()
        if rid:
            return f"id:{rid}"
        norm = lambda s: " ".join(str(s or "").lower().split())
        return f"nc:{norm(rec.get('institution_name'))}|{norm(rec.get('city'))}|{norm(rec.get('state'))}"

    # -- Typed read API --------------------------------------------------------
    def get_institution(self, name: Optional[str] = None, school_name: Optional[str] = None,
                        query: Optional[str] = None, **_: Any) -> Dict[str, Any]:
        """READ a single institution by (partial) name. Returns the mapped shape."""
        term = name or school_name or query or ""
        if not term:
            return {"valid": False, "institution_name": "", "source": self.source,
                    "summary": "", "title": "", "ref": ""}
        data = self._get({"school.name": term, "per_page": 1})
        results = data.get("results", []) or []
        if not results:
            return {"valid": False, "institution_name": term, "source": self.source,
                    "summary": "", "title": term, "ref": ""}
        return self._map_record(results[0])

    def search_institutions(self, state: Optional[str] = None, name: Optional[str] = None,
                            limit: int = 5, **_: Any) -> List[Dict[str, Any]]:
        """READ a list of institutions by state (and/or partial name)."""
        params: Dict[str, Any] = {"per_page": max(1, min(int(limit), 20))}
        if state:
            params["school.state"] = state.upper()
        if name:
            params["school.name"] = name
        if not state and not name:
            return []
        data = self._get(params)
        return [self._map_record(r) for r in (data.get("results", []) or [])]

    # -- Gateway entry point (kb.search_policies, granted to the concierge) -----
    def search_policies(self, query: str = "", state: Optional[str] = None,
                        school_name: Optional[str] = None, limit: int = 5,
                        **_: Any) -> Dict[str, Any]:
        """
        The tool the concierge is granted (kb.search_policies). Routes a query to a
        real institution lookup or state search and returns the fixture-compatible
        {"results": [...]} shape (each item carries the added real fields + summary).
        """
        intent = "SEARCH" if state else classify_query(query or school_name or "")
        if state or intent == "SEARCH":
            st = state or self._state_from_query(query)
            results = self.search_institutions(state=st, name=(school_name or None), limit=limit)
        else:
            rec = self.get_institution(name=school_name or query)
            results = [rec] if rec.get("valid") else []
        return {"results": results, "source": self.source, "intent": intent}

    @staticmethod
    def _state_from_query(text: Optional[str]) -> Optional[str]:
        t = (text or "").lower()
        for name, abbr in _STATES.items():
            if f" {name}" in f" {t}":
                return abbr
        for abbr in _STATES.values():
            if f" {abbr.lower()} " in f" {t} " or t.strip().upper().endswith(abbr):
                return abbr
        return None

    # -- Writes are intentionally unsupported (read-only public source) --------
    def update_enrollment_record(self, **kwargs: Any) -> Dict[str, Any]:
        raise NotImplementedError(
            "College Scorecard is a READ-ONLY public data source. Student-record "
            "writes (enrollment changes) target the institution's validated SIS and "
            "remain human-gated at the gateway — never against Scorecard. Use the "
            "SIS connector (SIS_BASE_URL) or FixtureGeneric for write paths."
        )

    def send_message(self, **kwargs: Any) -> Dict[str, Any]:
        raise NotImplementedError(
            "College Scorecard is a READ-ONLY public data source. Outbound family/"
            "student messages are consequential, human-gated actions performed via "
            "the institution's comms system — never by the agent, never against "
            "Scorecard."
        )
