"""
Live connectors — production adapters to real systems of record.

In production each connector kind points at the institution's real API:

    sis        PowerSchool, Infinite Campus, Banner, Workday Student
    lms        Canvas, Blackboard, Schoology, Moodle, D2L (via LTI 1.3 / REST)
    crm        Slate, Salesforce Education Cloud
    itsm       ServiceNow, Jira Service Management
    erp        Workday, Banner Finance, procurement/HR systems
    kb         Bedrock Knowledge Bases (approved institutional content)
    rules      degree-audit / rules engine (deterministic)
    docpipe    Textract + Bedrock Data Automation + Translate + Polly
    analytics  governed student-data lake (S3 + Glue + Lake Formation)
    labor      governed labor-market data layer

This module ships an explicit stub so the *intent* is visible and the failure
mode is informative: calling a live method without a configured client raises
NotImplementedError rather than silently doing nothing. Implement a typed
subclass per system when the institution provides credentials and the connector
passes its integration validation (see each agent's integration-guide).

`LiveHTTPConnector` is a minimal real-HTTP reference: set <KIND>_BASE_URL and it
performs an authenticated round-trip, demonstrating the live path end-to-end
against a customer gateway or a local reference service.
"""
from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict

from .base import GenericConnector


class LiveConnector(GenericConnector):
    """Explicit not-implemented stub for live mode (fail-loud, not silent)."""

    def __getattr__(self, method: str) -> Any:
        def call(**kwargs: Any) -> Dict[str, Any]:
            raise NotImplementedError(
                f"Live {self.kind!r}.{method} is not implemented. Provide a typed live "
                f"connector and credentials, or set {self.kind.upper()}_BASE_URL to use "
                f"LiveHTTPConnector. Production access must flow through the gateway."
            )

        return call


class LiveHTTPConnector(GenericConnector):
    """
    Minimal real-HTTP connector: POST {method, args} to <BASE_URL>/<method>.

    The gateway has already authorized the call and minted a scoped token; in a
    full implementation that token is forwarded as a bearer credential. Here we
    forward an optional static token from <KIND>_API_TOKEN for the reference path.
    """

    def __init__(self, kind: str, base_url: str) -> None:
        super().__init__(kind)
        self._base = base_url.rstrip("/")
        self._token = os.getenv(f"{kind.upper()}_API_TOKEN", "")

    def __getattr__(self, method: str) -> Any:
        def call(**kwargs: Any) -> Dict[str, Any]:  # pragma: no cover - requires a live endpoint
            url = f"{self._base}/{method}"
            body = json.dumps(kwargs).encode()
            req = urllib.request.Request(url, data=body, method="POST")
            req.add_header("Content-Type", "application/json")
            if self._token:
                req.add_header("Authorization", f"Bearer {self._token}")
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())

        return call
