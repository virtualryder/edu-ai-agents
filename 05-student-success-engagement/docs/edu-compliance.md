# Agent 05 — EDU Compliance
### The compliance spine as it binds Student Success & Proactive Engagement

> Agent 05 touches student outcomes directly, so the compliance spine binds harder here than anywhere else in the suite. This is the agent most exposed to two specific failure modes: assembling data domains that should not be combined, and turning a prediction into a **permanent label** on a student. The control design answers both by separating the prediction, explanation, and human-decision stages and by holding the bright line absolutely. This is the **control design**, not a legal opinion or certification — the institution operationalizes, validates, and accepts accountability for it. See `../../governance/README.md` for the full spine.

---

## 1. The bright line — decisions Agent 05 never makes

Encoded as policy and tested in `../../governance/tests/test_hitl_gates.py`. Agent 05 assembles evidence, explains patterns, drafts interventions and outreach, opens and tracks cases, and coordinates action. It **never autonomously decides**:

| Bright-line decision | What Agent 05 does instead |
|---|---|
| **Discipline** | Never inferred or decided — not by the agent, not by a prediction. Behavior signals inform a *human's* review of a case, never an automated determination |
| **Placement** | Presents evidence and intervention options; a human owns any placement decision |
| **Grades** | Out of scope for this agent; owned by the educator (Agent 04) |
| **Admissions** | Out of scope; a human decides |
| **Financial aid** | Surfaces a *missing-item* signal for outreach; eligibility/award decisions are human |
| **Special-education eligibility** | Out of scope; the IEP/504 team decides |

For every output, the distinction between an **option**, a **recommendation**, and an **approved decision** is explicit and enforced by the HITL gate. A prediction is none of the three — it is an input to evidence assembly.

---

## 2. Applicable parts of the compliance spine

### FERPA — Family Educational Rights and Privacy Act
- **Identity-scoped retrieval.** Agent 05 accesses only records the acting human may access (Layer 3 deny-by-default + role intersection). A counselor's caseload, an educator's roster, a guardian's student.
- **Age-of-majority / rights transfer.** At 18 / postsecondary enrollment, FERPA rights transfer to the student; guardian outreach and access narrow accordingly. Role mapping in the IdP carries this state.
- **School-official / direct-control.** The agent holds no standing credentials; purpose-of-use is enforced per tool; the institution can disable any tool or agent immediately.
- **Recordkeeping of disclosures.** Every signal read, evidence assembly, draft, approval, send, response, and escalation is recorded in the append-only, PII-masked audit (DynamoDB + S3 Object Lock).
- **No redisclosure.** Connectors return only the fields a tool needs; the masker prevents record-linkable data from sprawling into prompts or logs.

### PPRA — Protection of Pupil Rights Amendment
The hardest-binding statute for this agent. Agent 05 **does not collect or infer PPRA-protected categories** (political affiliation, religion, sexual behavior, and the rest). **Intervention drafting and outreach personalization are grounded in operational signals only** — attendance, missing work, engagement, deadlines, incomplete items. Survey-derived data is used strictly within stated consent. The Guardrail and grounding controls block any output that implies a protected-category inference.

### COPPA — under-13 learners
The under-13 flag in identity claims drives heightened Guardrails (age-appropriate outreach copy), data minimization, retention limits, and a prohibition on any non-educational profiling or behavioral targeting — enforced as a purpose-of-use policy at the gateway.

### Equity / anti-discrimination and the fairness control
Agent 05 is the suite's primary subject of the fairness control (`../../governance/fairness/`). The control monitors **false-positive and false-negative rates** and **equity differences across subgroups** in both *recommendations* and *outcomes*, and is designed to prevent a **permanent label** on a student: a prediction is transient, fenced as an input, and never written back to a record or surfaced to a student as a score.

### Records retention & data governance
Evidence snapshots are retained in WORM storage (S3 Object Lock) for review and equity audit; retention windows are configurable to the institution's schedule and state obligations.

### State student-privacy laws
Data-residency, retention windows, consent capture, and prohibited-use policies are configuration, not code — tuned to a state's requirements during the assessment phase.

### Department of Education AI guidance (2025)
Agent 05 is built to the bounded-agent posture: AI augments counselors and educators and **never makes consequential decisions autonomously**; value is framed as assembling evidence and coordinating action, consistent with the IES caution that prediction does not always outperform traditional early-warning systems.

---

## 3. HITL gates

Every consequential or sensitive action suspends at a framework-enforced gate (LangGraph `interrupt_before` / Step Functions `waitForTaskToken`) until a named, authorized reviewer's identity is bound into the record. The gateway mints the downstream write token only after the approval record is verified.

| Gated action | Reviewer role | What is surfaced for the decision |
|---|---|---|
| `case.create_success_case` | Counselor / advisor | Grounded evidence summary, proposed plan, compliance report |
| `case.escalate_to_staff` | Counselor / administrator | Persistence/response evidence, escalation rationale |
| `outreach.send_approved_message` (sensitive) | Counselor | Template, personalization (operational signals only), recipient scoping, opt-out state |
| Any write touching a guardian record | Per role + age-of-majority scoping | Guardian-relationship resolution, rights-transfer state |

**No path from signal to a consequential write bypasses the gate.** Low-stigma, deadline-style outreach on approved templates may run under a configured standing approval, but sensitive or stigmatizing outreach always requires a named human sign-off.

---

## 4. Data minimization

- **Domain-combination limits.** Lake Formation enforces *which* data domains may be combined for evidence assembly; the agent cannot assemble an arbitrary cross-domain profile.
- **Field minimization.** Connectors return only the fields a tool needs; no redisclosure.
- **PII masking before prompt.** FERPA/COPPA identifiers are replaced with stable pseudonyms before any result enters a Bedrock prompt or an audit record.
- **Prediction fencing.** The prediction is an input, consumed by the evidence-assembly stage only; it is not persisted as a label.

---

## 5. Audit

The append-only audit trail (DynamoDB with `deny:UpdateItem`/`deny:DeleteItem` on the audit partition, PITR; finalized snapshots in S3 Object Lock COMPLIANCE mode) records every signal read, evidence assembly, draft, approval, outreach send, response, and escalation — with lineage to the system of record and the bound reviewer identity — satisfying FERPA's recordkeeping of disclosures. CloudTrail provides the API-level record into the same unified compliance trail.

---

## 6. Fairness — the central control for this agent

Because Agent 05 can shape who receives an intervention, fairness is not an add-on. The control (`../../governance/fairness/`):

- monitors **false-positive / false-negative rates** so the agent neither floods low-need students nor misses high-need ones;
- checks **equity differences across subgroups** in both recommendations and outcomes;
- enforces that prediction stays **transient and fenced**, preventing a permanent label;
- feeds the QuickSight equity dashboard so administrators can see subgroup differences continuously, not at audit time only.

These metrics are part of the ROI model (`./roi-analysis.md`) and the Risk & quality category in `../../governance/README.md`.

---

## 7. What the customer still owns

FERPA/COPPA/PPRA compliance program and data-governance policy; IdP integration and role mapping (guardian relationships, age-of-majority); state student-privacy-law mapping; Bedrock Guardrail tuning for its population (including minors); consent capture and opt-out configuration; connector validation against live systems; records-retention configuration; and change control for prompt/model updates.

---

**Maturity: Documented.**
