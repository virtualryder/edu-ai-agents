"""
Student-PII masking — FERPA / COPPA identifier de-identification at log/audit boundaries.

Logs, traces, and audit records in an education workload must never contain raw
personally identifiable information from an education record. This module gives
every agent one masking function applied at the log/audit boundary. It targets the
identifier families most likely to appear in student-services, learning, and
operational text, and is tuned to FERPA-protected identifiers and COPPA's
heightened bar for learners under 13:

    * US SSN                      123-45-6789
    * Student / case / app IDs    long digit runs, STU-/SID-/CASE-/APP- prefixes
    * Dates more specific than year (DOB, event dates)
    * Email addresses, phone numbers
    * Street addresses (home/mailing — heightened sensitivity for minors)
    * Payment card numbers (Luhn-validated, for tuition / meal-account flows)
    * Generic long numeric identifiers (lunch number, transcript IDs, etc.)

Design notes:
  * Deterministic and dependency-free (regex + Luhn). An optional ML NER pass
    (Amazon Comprehend / Presidio) can be layered behind MASK_ENGINE=ml.
  * Conservative: over-masking a log line is acceptable; leaking a student ID is not.
  * mask() is idempotent and safe to call on already-masked text.
  * masked_pseudonym() yields a STABLE pseudonym for an identifier so the audit
    trail can be correlated across calls without exposing the raw value.

This is the de-identification *control point*; it does NOT replace a formal
de-identification of datasets, which is a data-governance activity governed by the
institution's privacy office (FERPA studies/exceptions, state law).
"""
from __future__ import annotations

import hashlib
import os
import re
from typing import Optional

# ── Identifier patterns (order matters: most specific first) ──────────────────
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
# Student / case / application identifiers with common education prefixes
_STUDENT_RE = re.compile(
    r"\b(?:STU|SID|STUDENT|PUPIL|LEARNER|CASE|APP|APPL|ENROLL)[-_ ]?\d{3,}\b", re.I
)
# Dates more specific than a bare year (YYYY-MM-DD, MM/DD/YYYY, DD-Mon-YYYY)
_DATE_RE = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|"
    r"\d{1,2}[-\s](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-\s]\d{2,4})\b",
    re.I,
)
# Street address (number + street + suffix) — home/mailing addresses are heightened-
# sensitivity, especially for minors. Work/campus addresses are acceptable but the
# masker is intentionally conservative.
_ADDRESS_RE = re.compile(
    r"\b\d{1,6}\s+(?:[A-Z][a-zA-Z]+\.?\s){1,4}"
    r"(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Lane|Ln|Drive|Dr|Court|Ct|Way|Place|Pl|Terrace|Ter)\b",
    re.I,
)
# 13-19 digit runs that pass Luhn -> payment cards (tuition / meal account)
_CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")
# Long bare digit runs (>=9) -> student number / account-style identifiers
_LONGNUM_RE = re.compile(r"\b\d{9,}\b")


def luhn_valid(number: str) -> bool:
    """Return True if the digit string passes the Luhn checksum."""
    digits = [int(c) for c in number if c.isdigit()]
    if len(digits) < 13:
        return False
    checksum = 0
    parity = len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def _mask_cards(text: str) -> str:
    def repl(m: "re.Match") -> str:
        raw = m.group(0)
        return "[CARD-REDACTED]" if luhn_valid(raw) else raw

    return _CARD_RE.sub(repl, text)


def mask(text: Optional[str]) -> str:
    """
    Mask student-PII identifiers in free text for safe logging and audit.

    Idempotent; returns "" for None. Set MASK_ENGINE=ml to additionally run an
    optional NER engine (not bundled — wired by the institution's privacy stack).
    """
    if not text:
        return ""
    out = str(text)
    out = _SSN_RE.sub("[SSN-REDACTED]", out)
    out = _EMAIL_RE.sub("[EMAIL-REDACTED]", out)
    out = _STUDENT_RE.sub("[STUDENT-ID-REDACTED]", out)
    out = _ADDRESS_RE.sub("[ADDRESS-REDACTED]", out)
    out = _mask_cards(out)
    out = _PHONE_RE.sub("[PHONE-REDACTED]", out)
    out = _DATE_RE.sub("[DATE-REDACTED]", out)
    out = _LONGNUM_RE.sub("[ID-REDACTED]", out)

    if os.getenv("MASK_ENGINE", "").strip().lower() == "ml":
        out = _ml_mask(out)
    return out


def masked_pseudonym(identifier: str, *, prefix: str = "STU") -> str:
    """
    Return a STABLE pseudonym for an identifier, so cross-call correlation in the
    audit trail is possible without exposing the raw value. Salt with
    PII_PSEUDONYM_SALT in production so pseudonyms are not reversible by guessing.
    """
    if not identifier:
        return ""
    salt = os.getenv("PII_PSEUDONYM_SALT", "edu-demo-salt").encode()
    digest = hashlib.sha256(salt + str(identifier).encode()).hexdigest()[:12]
    return f"{prefix}-{digest}"


def _ml_mask(text: str) -> str:
    """Optional ML NER hook (Amazon Comprehend / Presidio). No-op if absent."""
    try:  # pragma: no cover - optional dependency path
        from edu_agent_platform._ml_ner import redact  # type: ignore

        return redact(text)
    except Exception:
        return text
