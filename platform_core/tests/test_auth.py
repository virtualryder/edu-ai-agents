"""verify_jwt: a pre-decoded claims dict is trusted ONLY in demo mode."""
import os
import sys
from pathlib import Path

import pytest

PLATFORM = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLATFORM))

from edu_agent_platform.auth import AuthError, verify_jwt


def test_demo_mode_accepts_claims_dict(monkeypatch):
    monkeypatch.setenv("AUTH_ALLOW_UNVERIFIED_CLAIMS", "1")
    claims = verify_jwt({"sub": "u-stu", "custom:edu_role": "STUDENT"})
    assert claims["sub"] == "u-stu"


def test_demo_mode_still_requires_sub(monkeypatch):
    monkeypatch.setenv("AUTH_ALLOW_UNVERIFIED_CLAIMS", "1")
    with pytest.raises(AuthError):
        verify_jwt({"custom:edu_role": "STUDENT"})


def test_production_rejects_unverified_claims_dict(monkeypatch):
    # No demo flags -> production; a self-asserted claims dict must be refused.
    monkeypatch.delenv("AUTH_ALLOW_UNVERIFIED_CLAIMS", raising=False)
    monkeypatch.delenv("EXTRACT_MODE", raising=False)
    monkeypatch.delenv("CONNECTOR_MODE", raising=False)
    with pytest.raises(AuthError):
        verify_jwt({"sub": "attacker", "custom:edu_role": "REGISTRAR"})


def test_production_string_token_requires_jwks(monkeypatch):
    monkeypatch.delenv("AUTH_ALLOW_UNVERIFIED_CLAIMS", raising=False)
    monkeypatch.delenv("EXTRACT_MODE", raising=False)
    monkeypatch.delenv("CONNECTOR_MODE", raising=False)
    monkeypatch.delenv("AUTH_JWKS_URL", raising=False)
    with pytest.raises(AuthError):
        verify_jwt("a.b.c")
