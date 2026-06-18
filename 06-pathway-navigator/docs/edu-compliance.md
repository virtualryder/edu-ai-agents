# Pathway Navigator — EDU Compliance
### Agent 06 — the bright line, HITL gates, data minimization, audit, and fairness

> **The Navigator augments the counselor. It never makes the placement decision, and it never hides the assumptions behind a recommendation.** Student placement is on the suite's bright-line list — the agent presents options and recommendations, and a qualified human decides. This document maps the Navigator onto the EDU compliance spine (`../../governance/README.md`), states the decisions it never makes, and describes how the option-vs-recommendation-vs-approved-plan distinction, the HITL gates, data minimization, audit, and fairness checks are enforced.

---

## 1. The bright line — what the Navigator never decides

The suite's bright line is encoded as policy and tested in `../../governance/tests/test_hitl_gates.py`. For the Navigator, the load-bearing entry is **student placement**:

| Bright-line decision | What the Navigator may do | Who decides |
|---|---|---|
| **Student placement** | Present **options** (paths consistent with the rules) and **recommendations** (grounded suggestions, assumptions surfaced); attach a proposed plan to a case for review | The counselor / advisor — a named, authorized human |

The agent draws — and surfaces — three distinct kinds of output, and must never blur them:

| Output type | Authority | Compliance meaning |
|---|---|---|
| **Option** | None — possibility only | Reflects what the deterministic rules engine says is allowed |
| **Recommendation** | None — suggestion only | Grounded reasoning with **assumptions surfaced, not buried** |
| **Approved academic plan** | Binding | Exists only after a counselor's HITL approval binds their identity |

Two failure modes are explicitly prohibited and tested: presenting a **recommendation as if it were an approved plan**, and **hiding policy assumptions** (catalog year, assumed major, in-progress courses) behind a confident statement. Assumptions are always stated alongside the output that depends on them.

---

## 2. Applicable parts of the compliance spine

### FERPA — identity-scoped retrieval
Transcript, program, and standing are retrieved only for the authenticated student's own record, enforced at Layer 3 by deny-by-default plus least-privilege role intersection — the technical enforcement of FERPA's access limits. Rights transfer to the student at 18 / postsecondary enrollment; guardian roles are scoped so a parent agent cannot surface records the parent no longer has a right to. The agent acts as a **school official under the institution's direct control**: the gateway enforces purpose-of-use per tool, the agent holds no standing credentials, and the institution can disable any tool or the whole agent immediately. Connectors return only the fields a tool needs, and the **student-PII masker** prevents record-linkable data from sprawling into prompts or logs.

### Accreditation and transfer-articulation policy
Graduation requirements and transfer-credit articulation are governed by accreditation and articulation policy — they have correct answers given a transcript and a catalog year. This is why the Navigator runs them as a **deterministic rules engine, not the LLM**: the logic is testable against advisor-reviewed golden audits and consistent enough to stand in validation evidence, rather than generated and potentially hallucinated. An LLM that invented a graduation requirement or mis-stated an articulation agreement would directly harm a student's time and money; the deterministic engine removes that failure mode from the consequential path.

### COPPA — under-13 learners
Because the Navigator serves middle-school course planning, the under-13 flag carried in identity claims drives heightened Guardrails (age-appropriate content), data minimization, and a prohibition on any non-educational use or profiling of children's data.

### Department of Education AI guidance (2025)
The Navigator is built to a use case ED explicitly identifies — college/career exploration, advising, navigation, career-aligned pathways, and personalized learning plans — and to the principle that AI augments educators and never makes consequential decisions autonomously.

---

## 3. HITL gates

Framework-enforced human approval — not documentation, not a hope that the model behaves — gates every consequential action. The graph suspends (LangGraph `interrupt_before` on `finalize`; Step Functions `waitForTaskToken` in the native rebuild) and resumes only when a verified counselor identity is written to the HITL queue table; the gateway will not mint the write token until that reviewer identity is present.

| Action | Gate | Why |
|---|---|---|
| `scheduling.book_counselor_appointment` | **HITL** | A write into the institution's scheduling system |
| `advising.create_advising_case` | **HITL** | Opens a case a human must own |
| `advising.attach_proposed_plan` | **HITL** | A plan that would be treated as approved requires a named human signature; the agent never self-marks "approved" |

There is no path through the agent graph from intake to a finalized write that bypasses the HITL gate.

---

## 4. Data minimization

The Navigator returns only the fields a tool needs: a degree audit needs completed/in-progress courses and a catalog year, not a full student profile; career exploration uses the **governed labor-market data layer with no join to student PII**. The PII masker runs before any inbound result enters a prompt or audit record, and WORM retention (S3 Object Lock) plus configurable retention windows keep the retained surface small and aligned to records-retention schedules.

---

## 5. Audit

Every tool attempt — ALLOW, DENY, PENDING_APPROVAL, ERROR — is logged to the PII-masked, append-only audit trail (DynamoDB with `deny:UpdateItem`/`deny:DeleteItem` on the audit partition, plus S3 Object Lock for finalized snapshots), with lineage to the system of record. This satisfies FERPA's recordkeeping of disclosures and answers the auditor's question — who accessed this record, on what basis, and who approved the action. CloudTrail feeds the same unified compliance record at the API level.

---

## 6. Fairness

The Navigator's recommendations touch student trajectories, so the suite's fairness checks (`../../governance/fairness/`) apply: equity and representativeness flags on recommendation patterns, with false-positive/false-negative monitoring to detect whether certain student groups are being systematically steered toward or away from particular pathways. Because the deterministic rules engine — not the LLM — is authoritative for what is *possible*, fairness monitoring focuses on the LLM's *recommendation* layer, where steering risk actually lives, and on whether assumptions are surfaced consistently across groups.

See the full spine in `../../governance/README.md` and the suite-wide bright-line framing in `../README.md`.

---

**Maturity: Documented.**
