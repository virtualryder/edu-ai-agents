"""
Grounding verification — claim traceability for student- and family-facing text.

A student-, family-, or educator-facing artifact (a financial-aid status
explanation, a deadline, a lesson, feedback, an advising plan, a family message)
must contain ONLY claims traceable to the state that produced it. An LLM
hallucination in a policy answer, a fabricated deadline, or an invented
graduation requirement is a trust and compliance defect — families act on these.
verify_grounding flags any number or capitalized entity in the text that is not
traceable to the input state, so a human reviewer (and CI) can catch fabricated
dates, dollar amounts, requirements, or institution names before anything is sent.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Set

# Common education terms / authorities that are acceptable without being in state.
_ENTITY_ALLOWLIST = {
    "FAFSA", "FERPA", "COPPA", "PPRA", "IDEA", "ADA", "WCAG", "Section",
    "Department of Education", "U.S. Department of Education", "Title IV",
    "Free Application", "Federal Student Aid", "Satisfactory Academic Progress",
    "Individualized Education Program", "Common Core", "Advanced Placement",
    "Grade Point Average", "Add Drop", "Add/Drop", "Office Hours",
    "Financial Aid", "Student Services", "Registrar", "Academic Advisor",
    "Career Services", "Help Desk", "Service Desk",
    "United States", "European Union",
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "Fall", "Spring", "Summer", "Winter",
    "The", "This", "These", "Per", "Student", "Family", "Parent", "Guardian",
    "Counselor", "Instructor", "Educator", "Teacher",
}

# Small integers and ubiquitous values that are not meaningful claims.
_NUMBER_ALLOWLIST = {"1", "2", "3", "4", "5", "7", "12", "18", "13", "21", "30", "60", "90", "100"}

_NUMBER_RE = re.compile(r"\$?\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b|\$?\b\d+(?:\.\d+)?%?\b")
_ENTITY_RE = re.compile(r"\b(?:[A-Z][a-zA-Z&'-]+(?:\s+[A-Z][a-zA-Z&'-]+)+)\b")


@dataclass
class GroundingReport:
    ungrounded_numbers: List[str] = field(default_factory=list)
    ungrounded_entities: List[str] = field(default_factory=list)
    checked_numbers: int = 0
    checked_entities: int = 0

    @property
    def grounded(self) -> bool:
        return not self.ungrounded_numbers and not self.ungrounded_entities

    def to_audit_dict(self) -> Dict[str, Any]:
        return {
            "grounded": self.grounded,
            "ungrounded_numbers": self.ungrounded_numbers,
            "ungrounded_entities": self.ungrounded_entities,
            "checked_numbers": self.checked_numbers,
            "checked_entities": self.checked_entities,
        }


def _normalize_number(tok: str) -> str:
    return tok.replace("$", "").replace(",", "").replace("%", "").rstrip(".")


def _state_number_corpus(state: Dict[str, Any]) -> Set[str]:
    blob = json.dumps(state, default=str)
    nums: Set[str] = set()
    for tok in _NUMBER_RE.findall(blob):
        n = _normalize_number(tok)
        nums.add(n)
        try:
            f = float(n)
            nums.add(f"{f:g}")
            if f == int(f):
                nums.add(str(int(f)))
        except ValueError:
            pass
    return nums


def verify_grounding(narrative: str, state: Dict[str, Any]) -> GroundingReport:
    report = GroundingReport()
    if not narrative:
        return report

    state_numbers = _state_number_corpus(state)
    state_text = json.dumps(state, default=str).lower()

    for tok in _NUMBER_RE.findall(narrative):
        n = _normalize_number(tok)
        try:
            value = float(n)
        except ValueError:
            continue
        if value <= 12:
            continue
        if n in _NUMBER_ALLOWLIST or f"{value:g}" in _NUMBER_ALLOWLIST:
            continue
        report.checked_numbers += 1
        aliases = {n, f"{value:g}"}
        if value == int(value):
            aliases.add(str(int(value)))
        if not aliases & state_numbers:
            report.ungrounded_numbers.append(tok)

    leading_stop = {"Between", "On", "In", "At", "During", "After", "Before",
                    "Within", "The", "This", "These", "Per", "From", "By", "Under", "Each",
                    "Your", "Our", "We", "You", "Please", "If", "When", "For"}
    for ent in set(_ENTITY_RE.findall(narrative)):
        words = ent.split()
        while words and words[0] in leading_stop:
            words = words[1:]
        if len(words) < 2:
            continue
        ent = " ".join(words)
        if ent in _ENTITY_ALLOWLIST or any(ent.startswith(a + " ") for a in _ENTITY_ALLOWLIST):
            continue
        report.checked_entities += 1
        if ent.lower() not in state_text:
            report.ungrounded_entities.append(ent)

    report.ungrounded_numbers.sort()
    report.ungrounded_entities.sort()
    return report
