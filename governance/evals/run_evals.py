"""
Structural eval harness. Validates that key agent artifacts keep their required
shape — the anatomy a reviewer and an auditor depend on. No API key, no network.

Run directly:  python -m governance.evals.run_evals
"""
from __future__ import annotations

import sys
from typing import Callable, Dict, List, Tuple

from .golden_artifacts import CONCIERGE_ANSWER, FEEDBACK_PACKAGE


def _concierge_answer_ok(a: Dict) -> Tuple[bool, str]:
    if not a.get("answer"):
        return False, "missing answer"
    if not a.get("citations"):
        return False, "concierge answer must carry citations to approved content"
    for c in a["citations"]:
        if not c.get("url"):
            return False, "every citation needs a URL"
    if a.get("consequential_action_taken") is not False:
        return False, "answer artifact must not record a consequential action (human gate)"
    return True, "ok"


def _feedback_package_ok(p: Dict) -> Tuple[bool, str]:
    if not p.get("rubric_id"):
        return False, "feedback must be grounded in a teacher-approved rubric"
    if "low_confidence_flags" not in p:
        return False, "feedback package must surface low-confidence work for manual review"
    if p.get("grade_released") is not False:
        return False, "agent artifact must not auto-release a grade (human gate)"
    return True, "ok"


CASES: List[Tuple[str, Callable, Dict]] = [
    ("concierge_answer_anatomy", _concierge_answer_ok, CONCIERGE_ANSWER),
    ("feedback_package_anatomy", _feedback_package_ok, FEEDBACK_PACKAGE),
]


def run() -> int:
    failures = 0
    for name, fn, art in CASES:
        ok, msg = fn(art)
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {msg}")
        failures += 0 if ok else 1
    print(f"\n{len(CASES) - failures}/{len(CASES)} eval cases passed")
    return failures


if __name__ == "__main__":
    sys.exit(0 if run() == 0 else 1)
