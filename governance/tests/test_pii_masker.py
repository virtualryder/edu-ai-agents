"""Student-PII masker: redaction of FERPA/COPPA identifiers, idempotency, pseudonyms."""
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "platform_core"))

from edu_agent_platform.pii_masker import (
    RealDataMaskingError,
    luhn_valid,
    mask,
    masked_pseudonym,
)


def test_masks_core_identifiers():
    out = mask("SSN 123-45-6789, student STU-100245, email a@b.edu, phone (206) 555-0143")
    assert "123-45-6789" not in out
    assert "STU-100245" not in out
    assert "a@b.edu" not in out
    assert "555-0143" not in out
    assert "[SSN-REDACTED]" in out


def test_masks_dates_and_address():
    out = mask("DOB 2015-04-12 at 1421 Maple Street")
    assert "2015-04-12" not in out
    assert "Maple Street" not in out


def test_idempotent():
    once = mask("student STU-100245")
    assert mask(once) == once


def test_none_and_empty():
    assert mask(None) == ""
    assert mask("") == ""


def test_luhn():
    assert luhn_valid("4111111111111111")  # test Visa
    assert not luhn_valid("1234567890123")


def test_pseudonym_is_stable_and_not_raw():
    p1 = masked_pseudonym("STU-100245")
    p2 = masked_pseudonym("STU-100245")
    assert p1 == p2
    assert "100245" not in p1


# ── Real-data mode: NER mandatory + fail-closed (FERPA free-text names) ────────

def test_demo_mode_masks_structured_but_leaves_free_text_names(monkeypatch):
    """Default/demo mode is unchanged: regex masks structured identifiers and
    does NOT raise. Free-text names are a documented regex limitation."""
    monkeypatch.delenv("ALLOW_REAL_DATA", raising=False)
    monkeypatch.delenv("MASK_ENGINE", raising=False)
    out = mask("SSN 123-45-6789 for student Jane Doe")
    assert "[SSN-REDACTED]" in out
    assert "123-45-6789" not in out
    # Regex has no name signature; the name survives in demo mode (documented).
    assert "Jane Doe" in out


def test_real_data_without_ner_engine_fails_closed(monkeypatch):
    """ALLOW_REAL_DATA on but MASK_ENGINE!=ml must raise, not silently regex-mask."""
    monkeypatch.setenv("ALLOW_REAL_DATA", "1")
    monkeypatch.delenv("MASK_ENGINE", raising=False)
    with pytest.raises(RealDataMaskingError):
        mask("SSN 123-45-6789 for student Jane Doe")


def test_real_data_with_ml_but_missing_backend_fails_closed(monkeypatch):
    """ALLOW_REAL_DATA + MASK_ENGINE=ml but no NER backend importable must raise."""
    monkeypatch.setenv("ALLOW_REAL_DATA", "1")
    monkeypatch.setenv("MASK_ENGINE", "ml")
    monkeypatch.delitem(sys.modules, "edu_agent_platform._ml_ner", raising=False)
    with pytest.raises(RealDataMaskingError):
        mask("student Jane Doe enrolled")


def test_real_data_with_ner_backend_masks_names(monkeypatch):
    """With ALLOW_REAL_DATA + MASK_ENGINE=ml + a NER backend, names are masked
    on top of the always-on structured regex pass."""
    fake = types.ModuleType("edu_agent_platform._ml_ner")
    fake.redact = lambda t: t.replace("Jane Doe", "[NAME-REDACTED]")
    monkeypatch.setitem(sys.modules, "edu_agent_platform._ml_ner", fake)
    monkeypatch.setenv("ALLOW_REAL_DATA", "1")
    monkeypatch.setenv("MASK_ENGINE", "ml")
    out = mask("student Jane Doe SSN 123-45-6789")
    assert "Jane Doe" not in out
    assert "[NAME-REDACTED]" in out
    assert "[SSN-REDACTED]" in out
