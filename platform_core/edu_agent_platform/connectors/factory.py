"""
Connector factory — resolve a connector by kind and mode.

    get_connector("sis")                 # mode from CONNECTOR_MODE (default fixture)
    get_connector("sis", mode="live")    # explicit live

Modes:
    fixture  deterministic offline store (demos, CI, evals)   [default]
    live     production adapters (connectors/live.py)

Live mode: if <KIND>_BASE_URL is set, returns LiveHTTPConnector (real HTTP
round-trip to the customer system or a local reference service). Otherwise
returns the LiveConnector stub so the missing-implementation error is explicit.
"""
from __future__ import annotations

import os
from typing import Optional

from .base import Connector
from .fixtures import FixtureGeneric
from .live import LiveConnector, LiveHTTPConnector

_KNOWN_KINDS = {
    "sis", "lms", "crm", "kb", "comms", "assessment", "analytics",
    "rules", "labor", "docpipe", "itsm", "erp",
}


def get_connector(kind: str, mode: Optional[str] = None) -> Connector:
    if kind not in _KNOWN_KINDS:
        raise ValueError(f"unknown connector kind {kind!r}")

    mode = (mode or os.getenv("CONNECTOR_MODE", "fixture")).strip().lower()

    if mode == "live":
        # CONCIERGE_SOURCE=collegescorecard -> real, public, read-only institution
        # facts from the U.S. Dept of Education College Scorecard API, backing the
        # concierge's `kb` reads (kb.search_policies). Additive + guarded: it only
        # engages for kind='kb' in live mode when the switch is explicitly set, so
        # the fixture default and every other live kind are unchanged. Student-
        # record writes stay human-gated to the SIS (see collegescorecard.py).
        if kind == "kb" and os.getenv("CONCIERGE_SOURCE", "").strip().lower() == "collegescorecard":
            from .collegescorecard import CollegeScorecardConnector
            return CollegeScorecardConnector()
        base_url = os.getenv(f"{kind.upper()}_BASE_URL", "")
        if base_url:
            return LiveHTTPConnector(kind, base_url=base_url)
        return LiveConnector(kind)

    # fixture mode (default)
    return FixtureGeneric(kind)
