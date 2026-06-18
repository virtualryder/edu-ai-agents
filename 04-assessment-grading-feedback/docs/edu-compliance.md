# 04 — Assessment, Grading & Feedback — EDU Compliance

> Which parts of the EDU compliance spine apply to the Assessment agent, the bright line it must never cross, its hard HITL gate, data minimization, and audit. Control design, not legal advice. Full spine: `../../governance/README.md`.

---

## 1. Which parts of the spine apply

| Spine element | Applies? | How it lands on Assessment |
|---|---|---|
| **FERPA** | **Yes — core** | Submissions, feedback, scores, and grades are education records. Identity-scoped access (the educator's own assessment) and disclosure recordkeeping via the append-only audit. |
| **COPPA (under-13)** | Yes (K–12) | K–12 assessment includes under-13 students; under-13 flag drives minimization and educational-purpose-only handling of submission data. |
| **PPRA** | Limited | The agent evaluates submitted work against a rubric; it does not survey for or infer PPRA-protected categories. |
| **IDEA / Section 504** | **Yes** | Accommodations affect how work is assessed (e.g., modality, extended time). The agent honors approved accommodations; it never decides eligibility or placement. |
| **ADA / 508 / WCAG 2.2 AA** | **Yes** | Feedback surfaces shown to students must conform. |
| **Accreditation / grading-integrity policy** | **Yes — central** | Grading integrity, evidence retention, versioned rubrics, and human-agent agreement monitoring underpin the program's defensibility. |
| **State student-privacy laws** | **Yes** | Residency, retention, consent parameterized per state. |
| **ED 2025 AI guidance** | Yes | Drafting feedback/evaluation is supported; the bounded-agent posture (human owns the grade) is the controlling principle. |

---

## 2. Bright-line decision this agent must never make

The single most important bright line in the suite lives here:

| Bright line | Assessment behavior |
|---|---|
| **Final / high-stakes grades** | **Never released autonomously.** The agent drafts rubric-grounded evaluation and feedback; the **score is computed deterministically** (not by the LLM); the **educator owns and approves every grade**. There is **no automatic high-stakes grade release**. |

It also never decides discipline, special-education eligibility, placement, admissions, or financial aid. The distinction between a **draft evaluation**, a **deterministic score**, and a **released grade** is explicit in the output and enforced by the gate.

---

## 3. HITL gate — the hard gate

The grade-release gate is the strictest in the suite, framework-enforced (LangGraph `interrupt_before` / Step Functions `waitForTaskToken`) and tested in `../../governance/tests/test_hitl_gates.py`:

- **`evaluate_against_rubric` and `draft_feedback`** are advisory — they produce drafts for the educator, never grades.
- **`route_to_manual_review`** escalates low-confidence responses to a human queue rather than guessing.
- **`release_grade`** suspends until a **named educator approves**; the gateway mints the grade-write token only with a valid reviewer identity bound into the record. For **final/high-stakes** grades, release is always a human action — the gate cannot be configured to auto-release.
- **Double-scoring/sampling** monitors human-agent agreement and the educator-correction rate; trust in any release path is earned and continuously checked, not assumed.

---

## 4. Data minimization

- **Educator-scoped reads** — only the educator's own assessment submissions and rubric.
- **Return only what a tool needs** — no unrelated record disclosure; the rubric is read by version.
- **Mask before prompt or log** — the student-PII masker runs before any submission content enters a prompt or audit record; evaluation can run on de-identified work where the rubric allows.
- **Heightened minimization for under-13** submissions.
- **No standing credentials** — short-lived scoped tokens per call.

---

## 5. Audit & evidence retention

Every read, analysis, escalation, and gated release is written to the append-only, PII-masked audit (DynamoDB append-only + S3 Object Lock COMPLIANCE-mode WORM + CloudTrail), recording who acted, the **rubric version**, the **deterministic score**, the **confidence band**, the human-review decision, and the **approving educator**. Sampling/double-scoring **agreement metrics** are retained as grading-integrity evidence for accreditation. The institution can disable any tool or the agent immediately (FERPA direct control).

---

## 6. What the customer still owns

FERPA/COPPA program and data-governance; accreditation and grading-integrity policy; the approved rubrics and their versioning; configuration of double-scoring/sampling thresholds; IdP/LMS role mapping and accommodation handling; Guardrail and fairness tuning; WCAG 2.2 AA conformance testing of feedback surfaces; AGS/rubric validation against live systems; evidence-retention configuration; and prompt/model change control. See `../../governance/README.md` §5.
