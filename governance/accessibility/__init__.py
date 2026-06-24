"""
Accessibility governance — WCAG / ADA Title II / Section 508 pre-flight for
AI-generated content.

Public schools, colleges, and universities are covered entities under the ADA and
(for federally funded institutions) Section 504 / Section 508. DOJ's ADA Title II
rule adopts WCAG 2.1 Level AA for web content and mobile apps, with compliance
dates of April 26, 2027 (institutions serving populations >= 50,000) and
April 26, 2028 (smaller entities and special districts). AI-generated output —
a family message, a posted announcement, a transformed enrollment document — is
in scope. This package gives every agent a deterministic accessibility pre-flight
that catches the most common WCAG AA failures before content ships.

This is the suite's flagship accessibility control point and is wired into
Agent 07 (Document & Accessibility Services); it is a fast pre-flight, not a
substitute for full WCAG auditing (axe-core in CI, manual screen-reader testing).
"""
from .wcag import AccessibilityReport, check_html, check_plain_language  # noqa: F401

__all__ = ["AccessibilityReport", "check_html", "check_plain_language"]
