# 03 — Educator Copilot — EDU Compliance

> Which parts of the EDU compliance spine apply to the Copilot, the bright lines it must never cross, its HITL gates, data minimization, and audit. Control design, not legal advice. Full spine: `../../governance/README.md`.

---

## 1. Which parts of the spine apply

| Spine element | Applies? | How it lands on the Copilot |
|---|---|---|
| **FERPA** | **Yes** | Roster and class-results reads touch education records; identity-scoped retrieval (the educator's own class only) and append-only audit. Drafts referencing student data are minimized and masked. |
| **COPPA (under-13)** | Yes (K–12) | The Copilot is educator-facing, but K–12 class context includes under-13 students; the under-13 flag drives minimization and educational-purpose-only handling of any referenced student data. |
| **PPRA** | Limited | The Copilot drafts from approved curriculum and operational class results; it does not survey for or infer PPRA-protected categories. |
| **IDEA / Section 504** | **Yes** | The Copilot may **draft accommodation alternatives and accessible content**; it never decides eligibility or placement (§2). |
| **ADA / 508 / WCAG 2.2 AA** | **Yes** | The Copilot drafts accessibility alternatives and the educator surface must support conformance; consequential accessibility material is human-verified (and Agent 07 transforms approved content). |
| **State content standards** | **Yes** | Drafts align to the applicable state standards via structured metadata. |
| **State student-privacy laws** | **Yes** | Residency, retention, consent parameterized per state. |
| **ED 2025 AI guidance** | **Yes — central** | The Copilot is built to ED's explicitly supported uses: instructional materials, differentiated instruction, and reduced administrative burden. |

---

## 2. Bright-line decisions this agent must never make

The Copilot is a **bounded agent**: it drafts and proposes; the educator decides and publishes. It never autonomously:

| Bright line | Copilot behavior |
|---|---|
| **Publishes to students** | **Never.** Every artifact is a **draft**; educator approval is required before any student distribution. |
| **Grades** | Never assigns or alters a grade (grading is Agent 04; the educator owns the grade there too). |
| **Special-education eligibility / placement** | May draft accommodation **alternatives**; the IEP/504 team decides eligibility and placement. |
| **Discipline / admissions / financial aid** | Out of scope; never inferred or decided. |

The distinction between a **draft**, a **proposed action**, and a **published artifact** is explicit in the output and enforced by the HITL gate.

---

## 3. HITL gates

The Copilot's defining control is **draft-first with educator approval**, framework-enforced (LangGraph `interrupt_before` / Step Functions `waitForTaskToken`) and tested in `../../governance/tests/test_hitl_gates.py`:

- **Read tools** (`get_roster`, `get_class_results`, `get_curriculum`) pass straight through.
- **Write tools** (`create_lms_draft`, `create_rubric_draft`, `update_assignment_due_date`) **suspend for educator review**. The gateway mints the LMS write token only after the named educator approves; the action is **preview + confirm** and **idempotent**, so a retry never double-applies. Even after approval the LMS artifact is a **draft** — publishing to students is a separate, deliberate educator step.

There is no path from intake to a student-visible publish that bypasses the educator.

---

## 4. Data minimization

- **Educator-scoped reads** — only the educator's own roster and class results.
- **Return only what a tool needs** — class-results reads return the minimum fields to ground differentiation/remediation; no unrelated record disclosure.
- **Mask before prompt or log** — the student-PII masker runs before any class data enters a prompt, a draft, or an audit record; drafts reference de-identified patterns where possible.
- **Heightened minimization for under-13** referenced data.
- **No standing credentials** — short-lived scoped tokens per call.

---

## 5. Audit

Every read and every gated write is written to the append-only, PII-masked audit (DynamoDB append-only + S3 Object Lock + CloudTrail), recording who acted, what tool, on what basis (educator role + course/section scope), the LMS lineage, and the approval. Each draft additionally carries a **version record** (source content + model configuration) supporting change control and rollback — and the institution can disable any tool or the agent immediately (FERPA direct control). Error/rollback events on LMS actions are tracked as a quality metric.

---

## 6. What the customer still owns

FERPA/COPPA program and data-governance; state content-standard mapping; IdP/LMS role mapping; Guardrail tuning; WCAG 2.2 AA conformance testing of drafted accessibility material and the educator surface; LMS-action and rollback validation against live systems; retention configuration; and prompt/model change control. See `../../governance/README.md` §5.
