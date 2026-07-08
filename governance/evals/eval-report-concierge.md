# Agent 01 (Student & Family Concierge) — scored eval report

**Result:** PASS · **Cases:** 20 · **Duplicate cases:** 3. Predictions from the real College Scorecard connector mapping + query classifier; grounding via `governance/grounding.py`; student-PII leak via the platform `pii_masker`.

| Metric | Value | Threshold | Status |
|---|---|---|---|
| classification_accuracy | 1.0 | >= 0.9 | PASS |
| entity_f1 | 1.0 | >= 0.85 | PASS |
| grounding_rate | 1.0 | >= 0.9 | PASS |
| student_pii_leak_rate | 0.0 | <= 0.0 | PASS |
| answer_completeness | 1.0 | >= 0.95 | PASS |
| duplicate_accuracy | 1.0 | >= 0.9 | PASS |

The **student_pii_leak_rate is a hard gate (= 0)** — the FERPA/COPPA control. Even though College Scorecard is public institution data (no student PII), the masker is exercised on every ingested summary so the control is proven, not assumed. Predictions come from the REAL connector, not a stub. Regenerate with `python -m governance.evals.score_concierge`.

> Honest scope: this benchmarks the public institution-facts connector. Real SIS/LMS connectors that touch the student education record are separate, human-gated engagement work with FERPA sign-off.
