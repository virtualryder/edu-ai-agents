# 02 — Personalized Tutor & Study Companion — EDU Compliance

> Which parts of the EDU compliance spine apply to the Tutor, the bright line it must never cross, its HITL/oversight model, data minimization, and audit. Control design, not legal advice. Full spine: `../../governance/README.md`.

---

## 1. Which parts of the spine apply

| Spine element | Applies? | How it lands on the Tutor |
|---|---|---|
| **FERPA** | **Yes** | Session content, enrollment/section context, and any progress signal are education records. Retrieval is identity-scoped and **segmented by institution/course/section/role**; the misconception dashboard is aggregate, minimizing individual disclosure. |
| **COPPA (under-13)** | **Yes — heightened** | The Tutor is a student-facing surface used by children under 13 in K–12. The under-13 flag drives stricter Guardrails, data minimization, educational-purpose-only use, no behavioral profiling, and tighter retention of session data. |
| **PPRA** | Limited | The Tutor does not survey for or infer PPRA-protected categories; it works from approved course content and the student's own work. |
| **IDEA / Section 504** | **Yes** | Accommodations may shape assistance level/modality. The Tutor honors an approved accommodation and may reinforce skills, but **never decides eligibility or placement** (§2). |
| **ADA / 508 / WCAG 2.2 AA** | **Yes** | The tutoring surface must conform; conformance is a production-readiness gate. |
| **Academic-integrity policy** | **Yes — central** | Never completing graded/prohibited assessments is an integrity control (§2). |
| **State student-privacy laws** | **Yes** | Residency, retention, consent parameterized per state. |
| **ED 2025 AI guidance** | Yes | Tutoring is an ED-identified supported use; the Tutor augments learning and decides nothing consequential. |

---

## 2. Bright-line decisions this agent must never make

The Tutor is a **bounded agent** that supports learning; it never autonomously decides anything consequential, and it carries one additional hard line specific to its function:

| Line | Tutor behavior |
|---|---|
| **Completing a graded or prohibited assessment** | **Never.** It returns hints, Socratic prompts, and explanations at the instructor-set assistance level — Guardrail-enforced so an injection cannot coax it into producing answers to live graded items. |
| **Grades** | Never views, assigns, or alters a grade. |
| **Special-education eligibility / placement** | Honors approved accommodations only; never decides. |
| **Surfacing other students' data** | Section-scoped retrieval; the misconception dashboard is aggregate, never per-student hidden scores. |

---

## 3. HITL & educator oversight

As a higher-governance agent, the Tutor's oversight is configured by the educator rather than enforced as a per-utterance approval (which would defeat 24/7 tutoring):

- **Instructor controls up front.** The educator owns source material, pedagogy, tone, prohibited behaviors, and assistance level before the tutor goes live — a design-time gate.
- **Aggregate-publication gate (optional).** Where the institution prefers, publication of the misconception dashboard can require educator confirmation; framework-enforced and tested in `../../governance/tests/test_hitl_gates.py`.
- **Integrity enforcement is a hard gate, not a human one.** The never-complete-a-prohibited-assessment line is enforced by Guardrails at every turn, independent of any human review.

---

## 4. Data minimization

- **Segmented retrieval** — the tutor reaches only the approved content for the student's enrolled course/section.
- **Aggregate dashboard** — class-level misconception patterns, not individual hidden scores, reduce the disclosed surface.
- **Mask before prompt or log** — the student-PII masker runs before any inbound context enters a prompt or audit record.
- **Heightened minimization & retention for under-13** session data, per COPPA.
- **No standing credentials** — short-lived scoped tokens per call.

---

## 5. Audit

Tool calls, retrieval scope, and session events are written to the append-only, PII-masked audit (DynamoDB append-only + CloudTrail), recording who acted, what was retrieved, on what basis (role + course/section scope), and any dashboard-publication approval. The institution can disable the Tutor or any tool immediately (FERPA direct control). Integrity-violation attempts (e.g., requests to complete a graded item) are logged for academic-integrity review.

---

## 6. What the customer still owns

Instructor configuration and validation of grounding/source material; FERPA/COPPA program and data-governance; IdP/LMS role mapping and accommodation handling; Guardrail tuning for the population (including minors and integrity rules); WCAG 2.2 AA conformance testing; LMS/LTI validation against live systems; retention configuration; and prompt/model change control. See `../../governance/README.md` §5.
