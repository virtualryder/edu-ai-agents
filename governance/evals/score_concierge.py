"""
Scored eval runner for Agent 01 (Student & Family Concierge).

Loads the labeled golden set, runs the real connector-mapping + classifier pipeline
to produce predictions, scores the metrics, gates against thresholds, and writes an
evidence report (eval-report-concierge.md + .json). Exit code is non-zero if any
threshold is missed — so CI holds the quality line.

    python -m governance.evals.score_concierge
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent.parent))
sys.path.insert(0, str(_HERE.parent.parent / "platform_core"))

from governance.evals.scorers_concierge import (  # noqa: E402
    score_dataset, gate, THRESHOLDS, LOWER_IS_BETTER,
)

GOLDEN = _HERE / "golden" / "agent01_concierge_scored.json"
REPORT_MD = _HERE / "eval-report-concierge.md"
REPORT_JSON = _HERE / "eval-report-concierge.json"


def _load():
    return json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]


def build_report(result, passed, failures) -> str:
    m = result["metrics"]
    rows = []
    for name, thr in THRESHOLDS.items():
        val = m.get(name, 0.0)
        op = "<=" if name in LOWER_IS_BETTER else ">="
        ok = (val <= thr) if name in LOWER_IS_BETTER else (val >= thr)
        rows.append(f"| {name} | {val} | {op} {thr} | {'PASS' if ok else 'FAIL'} |")
    md = [
        "# Agent 01 (Student & Family Concierge) — scored eval report",
        "",
        f"**Result:** {'PASS' if passed else 'FAIL'} · **Cases:** {result['n_cases']} · "
        f"**Duplicate cases:** {result['duplicate_cases']}. Predictions from the real "
        "College Scorecard connector mapping + query classifier; grounding via "
        "`governance/grounding.py`; student-PII leak via the platform `pii_masker`.",
        "",
        "| Metric | Value | Threshold | Status |",
        "|---|---|---|---|",
        *rows,
        "",
        "The **student_pii_leak_rate is a hard gate (= 0)** — the FERPA/COPPA control. "
        "Even though College Scorecard is public institution data (no student PII), the "
        "masker is exercised on every ingested summary so the control is proven, not "
        "assumed. Predictions come from the REAL connector, not a stub. Regenerate with "
        "`python -m governance.evals.score_concierge`.",
        "",
        "> Honest scope: this benchmarks the public institution-facts connector. Real "
        "SIS/LMS connectors that touch the student education record are separate, "
        "human-gated engagement work with FERPA sign-off.",
    ]
    if failures:
        md += ["", "## Threshold failures", *[f"- {f}" for f in failures]]
    return "\n".join(md) + "\n"


def main() -> int:
    cases = _load()
    result = score_dataset(cases)
    passed, failures = gate(result["metrics"])
    REPORT_JSON.write_text(json.dumps({"passed": passed, **result, "failures": failures}, indent=2),
                           encoding="utf-8")
    REPORT_MD.write_text(build_report(result, passed, failures), encoding="utf-8")
    print(f"Agent 01 concierge scored eval — {'PASS' if passed else 'FAIL'} ({result['n_cases']} cases)")
    for k, v in result["metrics"].items():
        print(f"  {k:24s} {v}")
    for f in failures:
        print("  FAIL:", f)
    print(f"report -> {REPORT_MD}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
