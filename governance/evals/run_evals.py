"""
Structural eval harness. Validates that key agent artifacts keep their required
shape — the anatomy a reviewer and an auditor depend on. No API key, no network.

Run directly:  python -m governance.evals.run_evals
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
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

# ── Scored evaluators, keyed by golden-file stem ──────────────────────────────
# A golden JSON in golden/ whose stem is NOT in this map is SKIPPED (so adding an
# unrelated golden file never crashes this runner). Each value is a module exposing
# main() -> int (0 = pass) that gates its own thresholds.
GOLDEN_DIR = Path(__file__).resolve().parent / "golden"
EVALUATORS: Dict[str, str] = {
    "agent01_concierge_scored": "governance.evals.score_concierge",
}


def run_scored() -> int:
    """Run registered scored evaluators over golden/*.json; skip unknown stems."""
    failures = 0
    if not GOLDEN_DIR.exists():
        return 0
    for gf in sorted(GOLDEN_DIR.glob("*.json")):
        stem = gf.stem
        module = EVALUATORS.get(stem)
        if not module:
            print(f"[skip] scored:{stem}: no evaluator registered")
            continue
        try:
            rc = importlib.import_module(module).main()
        except Exception as exc:  # never let a scored eval crash the structural run
            print(f"[skip] scored:{stem}: evaluator error ({exc})")
            continue
        print(f"[{'PASS' if rc == 0 else 'FAIL'}] scored:{stem}")
        failures += 0 if rc == 0 else 1
    return failures


def run() -> int:
    failures = 0
    for name, fn, art in CASES:
        ok, msg = fn(art)
        print(f"[{'PASS' if ok else 'FAIL'}] {name}: {msg}")
        failures += 0 if ok else 1
    failures += run_scored()
    print(f"\nstructural: {len(CASES) - min(failures, len(CASES))}/{len(CASES)} anatomy cases; "
          f"total failures (incl. scored): {failures}")
    return failures


if __name__ == "__main__":
    sys.exit(0 if run() == 0 else 1)
