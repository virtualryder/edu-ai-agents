"""Student-PII masker: redaction of FERPA/COPPA identifiers, idempotency, pseudonyms."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "platform_core"))

from edu_agent_platform.pii_masker import luhn_valid, mask, masked_pseudonym


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
