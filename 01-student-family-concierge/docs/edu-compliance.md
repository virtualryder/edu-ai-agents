# 01 — Student & Family Services Concierge — EDU Compliance

> Which parts of the EDU compliance spine apply to the Concierge, the bright-line decisions it must never make, its HITL gates, data minimization, and audit. This is control design, not a legal opinion or certification. Full spine: `../../governance/README.md`.

---

## 1. Which parts of the spine apply

| Spine element | Applies? | How it lands on the Concierge |
|---|---|---|
| **FERPA** | **Yes — core** | Status/schedule retrieval touches education records. Identity-scoped retrieval (deny-by-default + role intersection) is the technical enforcement of FERPA access limits; the agent reads the authenticated user's record and no other. Disclosure recordkeeping via the append-only audit. |
| **COPPA (under-13)** | **Yes (K–12)** | Children under 13 use the Concierge in K–12 deployments. Under-13 flag in identity claims drives heightened Guardrails, data minimization, educational-purpose-only use, and a ban on behavioral profiling. |
| **PPRA** | Limited | The Concierge does not collect or infer PPRA-protected categories; it answers and initiates low-risk workflows grounded in operational data only. |
| **IDEA / Section 504** | Limited | The Concierge may route a question to the right team but never surfaces or decides IEP/504 content; eligibility/placement is bright-line (§2). |
| **ADA / 508 / WCAG 2.2 AA** | **Yes** | Web, mobile, and chat surfaces are family-facing; WCAG 2.2 AA conformance is a production-readiness gate. |
| **Title VI language access** | **Yes** | Multilingual answers (Translate/Polly) support meaningful access for limited-English families. |
| **State student-privacy laws** | **Yes** | Data residency, retention, consent, and breach-notification are configuration tuned to the deployment state during assessment. |
| **Records retention** | Yes | WORM (S3 Object Lock) + configurable retention for case and disclosure records. |
| **ED 2025 AI guidance** | Yes | The Concierge sits squarely in the "reduced administrative burden" supported use; it augments staff and decides nothing consequential. |

---

## 2. Bright-line decisions this agent must never make

The Concierge is a **bounded agent**. It retrieves, explains, and initiates low-risk reversible workflows — it never autonomously decides any of the following:

| Bright line | Concierge behavior |
|---|---|
| **Financial aid** | **Checks status and explains** eligibility rules and next steps; it never commits, denies, or alters an award. Awards are human. |
| **Admissions** | Answers process/deadline questions and opens cases; it never renders an admissions outcome. |
| **Discipline** | Never inferred, discussed as a determination, or decided. |
| **Grades** | Out of scope; it does not view or alter grades. |
| **Special-education eligibility** | Routes to the authorized team only; never retrieves IEP/504 content or opines on eligibility. |
| **Student placement** | Never decides placement; routes placement questions to the appropriate human. |

The distinction between an **answer**, a **status**, and a **decision** is explicit in the agent's output and enforced by the gateway.

---

## 3. HITL gates

Reads (`check_application_status`, `get_student_schedule`) pass straight through. The human gate applies to the write tools, framework-enforced (not merely documented) and tested in `../../governance/tests/test_hitl_gates.py`:

- **`draft_family_message`** suspends at the `finalize` node (LangGraph `interrupt_before`; native: Step Functions `waitForTaskToken`). A named staff reviewer in the appropriate role reviews the draft; the gateway mints the send token only after a valid reviewer identity is bound into the record.
- **`create_advising_case`, `schedule_appointment`, `send_form`** are reversible and low-risk; they are audited and routed to staff ownership, with confirmation-before-action where the institution prefers a tighter gate. None can be configured to bypass audit.

There is no path from intake to a consequential outbound action that skips the gate.

---

## 4. Data minimization

- **Return only what a tool needs.** Connectors return the minimum fields for the operation (no redisclosure of unrelated record fields).
- **Mask before prompt or log.** The student-PII masker (`../../platform_core/edu_agent_platform/pii_masker/`) replaces FERPA-protected identifiers and COPPA-protected data with stable pseudonyms before any content enters a prompt or audit record.
- **Heightened minimization for under-13** records, per COPPA, with tighter retention.
- **No standing credentials.** The agent holds none; each call uses a short-lived scoped token.

---

## 5. Audit

Every gateway attempt is written to the append-only, PII-masked audit trail (**DynamoDB** with `deny:UpdateItem`/`deny:DeleteItem` on the audit partition + PITR; finalized snapshots to **S3 Object Lock** COMPLIANCE mode), recording **who acted, what tool, when, on what basis (role + purpose-of-use), the system-of-record lineage, and who approved** any gated action — satisfying FERPA's recordkeeping of disclosures. **CloudTrail** feeds the same unified record. The institution can disable any tool or the entire agent immediately (FERPA "direct control").

---

## 6. What the customer still owns

FERPA/COPPA/PPRA compliance program and data-governance policy; IdP integration and role mapping (guardian relationships, age-of-majority/rights-transfer); state student-privacy-law mapping; Bedrock Guardrail tuning for the population (including minors); WCAG 2.2 AA conformance testing of deployed surfaces; connector validation against live SIS/CRM; records-retention configuration; and change control for prompt/model updates. See `../../governance/README.md` §5.
