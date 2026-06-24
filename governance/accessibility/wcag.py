"""
Accessibility checks for AI-generated interfaces, documents, and messages.

DOJ's ADA Title II rule (28 CFR Part 35) adopts WCAG 2.1 Level AA for state/local
government and public-institution web content and mobile apps; Section 508 applies
the same bar to federally funded programs. Compliance dates were extended by DOJ's
April 2026 Interim Final Rule: entities serving >= 50,000 by April 26, 2027;
smaller entities and special districts (which includes many districts and small
colleges) by April 26, 2028. AI-generated output is in scope — so every agent's
rendered text/HTML passes these deterministic checks, which catch the most common
WCAG AA failures (the large majority of OCR accessibility complaints involve
untagged PDFs and missing text alternatives) before content ships.

This is a fast pre-flight, not a substitute for full WCAG auditing (e.g., axe-core
in CI, manual screen-reader testing, PDF/UA tagging review).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List

_IMG_RE = re.compile(r"<img\b[^>]*>", re.I)
_ALT_RE = re.compile(r'\balt\s*=', re.I)
_H_RE = re.compile(r"<h([1-6])\b", re.I)
_LINK_TEXT_RE = re.compile(r"<a\b[^>]*>(.*?)</a>", re.I | re.S)
_VAGUE_LINKS = {"click here", "here", "read more", "link", "this", "more"}


@dataclass
class AccessibilityReport:
    issues: List[str] = field(default_factory=list)

    @property
    def passes(self) -> bool:
        return not self.issues


def check_html(html: str) -> AccessibilityReport:
    """Deterministic WCAG 2.1 AA pre-flight for generated HTML/rich text."""
    rep = AccessibilityReport()
    if not html:
        return rep
    # 1.1.1 Non-text content: every <img> needs an alt attribute
    for img in _IMG_RE.findall(html):
        if not _ALT_RE.search(img):
            rep.issues.append(f"WCAG 1.1.1: <img> missing alt attribute: {img[:60]}")
    # 1.3.1 / 2.4.6 Heading order: no skipped levels (assistive-tech navigation)
    levels = [int(m) for m in _H_RE.findall(html)]
    for prev, cur in zip(levels, levels[1:]):
        if cur > prev + 1:
            rep.issues.append(f"WCAG 1.3.1: heading level jumps from h{prev} to h{cur}")
    # 2.4.4 Link purpose: no vague link text
    for txt in _LINK_TEXT_RE.findall(html):
        clean = re.sub(r"<[^>]+>", "", txt).strip().lower()
        if clean in _VAGUE_LINKS:
            rep.issues.append(f"WCAG 2.4.4: non-descriptive link text {clean!r}")
    return rep


def check_plain_language(text: str, max_grade: float = 9.0) -> AccessibilityReport:
    """
    Flesch-Kincaid grade-level check (proxy for plain-language / cognitive
    accessibility). Public-facing student and family communications are commonly
    targeted at a 6th-9th grade reading level so they are usable by multilingual
    families and learners with disabilities. Deterministic, dependency-free.
    """
    rep = AccessibilityReport()
    sentences = max(1, len(re.findall(r"[.!?]+", text)))
    words_list = re.findall(r"[A-Za-z]+", text)
    words = max(1, len(words_list))

    def syllables(w: str) -> int:
        w = w.lower()
        groups = re.findall(r"[aeiouy]+", w)
        n = len(groups)
        if w.endswith("e") and n > 1:
            n -= 1
        return max(1, n)

    syl = sum(syllables(w) for w in words_list)
    grade = 0.39 * (words / sentences) + 11.8 * (syl / words) - 15.59
    if grade > max_grade:
        rep.issues.append(f"Plain language: reading grade {grade:.1f} exceeds target {max_grade}")
    return rep
