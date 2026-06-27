# Agent 07 — EDU Compliance
### Document & Accessibility Services — the compliance-spine reading for an enrollment and accessibility agent

> This is the agent-specific reading of the suite's EDU compliance spine (`../../governance/README.md`). It is not a legal opinion and not a certification — it is the control design the institution operationalizes, validates, and accepts accountability for. Agent 07 is unusual in the suite on two counts: it ingests education records and minors' data at the front door of enrollment, and it is the suite's **named accessibility transformation agent**. Both raise the bar.

---

## 1. Applicable parts of the compliance spine

| Regulation | How it lands on Agent 07 |
|---|---|
| **FERPA** (20 U.S.C. § 1232g; 34 CFR Part 99) | Every extracted field, application record, staged update, and family message is personally identifiable information in an education record. Retrieval is identity-scoped (deny-by-default + role intersection); the agent acts as a **school official under the institution's direct control**, with purpose-of-use enforced per tool and no standing credentials. Every disclosure and write is recorded in the append-only audit trail. |
| **COPPA** (16 CFR Part 312) | K–12 intake collects information from children **under 13**. An under-13 flag in the identity claims drives heightened Guardrails, heightened PII masking, data minimization, and a prohibition on any non-educational use, profiling, or advertising — enforced as purpose-of-use at the gateway. |
| **IDEA / Section 504** | Individualized plans are among the most sensitive education records. Agent 07 may *transform* an approved plan into an accessible format, but eligibility and placement are on the bright line — the agent never decides them, and consequential individualized material requires human verification before release. |
| **ADA / Section 504 / Section 508 + WCAG 2.2 AA** | This is Agent 07's signature obligation: its accessibility output must be conformant, and the family-facing surfaces it serves must meet WCAG 2.2 AA. See §5. |
| **Immunization / residency record rules** | High-sensitivity validation fields with state-specific requirements; always routed to human review regardless of extraction confidence. |
| **Records retention & data governance** | S3 Object Lock (COMPLIANCE mode) provides immutable retention of the original **and** the extracted version on the institution's schedule; data minimization reduces the retained surface. |
| **PPRA** | Intake does not collect or infer PPRA-protected categories; survey-derived data is used strictly within stated consent. |
| **State student-privacy laws** | Data-residency (region/VPC), retention windows, consent capture, and prohibited-use policies are configuration, mapped to the state's requirements during assessment. |

---

## 2. The bright line — decisions Agent 07 never makes

Encoded as policy and tested in `../../governance/tests/test_hitl_gates.py`. Agent 07 prepares for the human decision; it does not make it.

- **Admissions** — the agent classifies, extracts, validates completeness, identifies discrepancies, requests missing items, and **prepares** a structured file; a human decides admission.
- **Enrollment** — staged SIS updates are reviewed and committed by a registrar or administrator; the agent never commits the enrollment decision.
- **Special-education eligibility and placement** — drafted or retrieved only; the IEP/504 team decides.
- **Meaning of consequential content** — accessibility transformation preserves the meaning of approved source content; it never originates policy or alters a legal notice, safety instruction, or individualized plan.

For each, the distinction between an **option**, a **recommendation/prepared file**, and an **approved decision** is explicit in the agent's output and enforced by the HITL gate.

---

## 3. HITL gates

The human gate is framework-enforced (Step Functions `waitForTaskToken` in the native rebuild; the AgentCore Gateway human-approval gate in the container lift), not merely documented. Agent 07 has two gate points:

1. **SIS/CRM commit gate** — `sis.commit_record_update` and consequential `crm.update_case` calls block until a verified registrar or administrator identity is bound into the record. Staging is split from committing so the proposed change is reviewable first.
2. **Consequential-material verification gate** — accessibility/multilingual output for individualized plans, legal notices, or safety information blocks until a verified human confirms the transformation before release.

Additionally, the confidence-by-sensitivity router sends any low-confidence extraction or any high-sensitivity field (legal name, date of birth, immunization status, residency basis, income) to human review — this is a quality gate that sits ahead of the commit gate.

---

## 4. Data minimization, masking, and audit

- **Data minimization** — connectors return only the fields a tool needs; staged updates carry only the fields being changed. This is the operational form of FERPA's no-redisclosure expectation.
- **Student-PII masking** — the masker (`../../platform_core/edu_agent_platform/pii_masker/`) replaces identifiers, dates of birth, and guardian details with stable pseudonyms before any tool result enters a prompt or an audit record; disability and under-13 data are treated as heightened-sensitivity.
- **Append-only audit** — every attempt (ALLOW / DENY / PENDING_APPROVAL / ERROR) is logged to the append-only DynamoDB audit partition with lineage to the system of record and to the S3 Object Lock document version, satisfying FERPA's recordkeeping of disclosures. CloudTrail feeds the same unified record.
- **Immutable retention** — the original submission and the extracted version are held in S3 Object Lock (COMPLIANCE mode), so the record of what was submitted and what was extracted cannot be altered after the fact.

---

## 5. Accessibility — the emphasis for Agent 07

Agent 07 is the suite's named accessibility transformation agent, so accessibility is a build requirement here, not an afterthought.

- **The conformance target is WCAG 2.2 AA** for all student- and family-facing output and surfaces, under ADA, Section 504, and Section 508. Conformance testing is a production-readiness gate (see the maturity ladder in `../../README.md`).
- **The transformations the agent produces** — alt text, captions, transcripts, plain-language and reading-level variants, audio (Amazon Polly), and translated materials (Amazon Translate) — are themselves accessibility artifacts and must meet the standard.
- **Human verification is required for consequential material** — individualized plans, legal notices, safety information — before release. An accessible or translated version of a legal notice that drifts in meaning is a worse outcome than no transformation; the verification gate prevents it.
- **Grounding applies** — accessibility output is traced to approved source content; an ungrounded "plain-language" rewrite that introduces a claim not in the source fails fast.

The institution remains responsible for WCAG 2.2 AA conformance testing of the deployed surfaces; the accelerator provides the transformation capability and the grounding/verification controls around it.

---

## 6. What the customer still owns

Per `../../governance/README.md`, §5: the institution's FERPA/COPPA/PPRA compliance program and data-governance policy; IdP integration and role mapping (guardian relationships, age-of-majority); state student-privacy-law mapping; Bedrock Guardrail tuning for its population (including minors); **WCAG 2.2 AA conformance testing of deployed surfaces**; connector validation against live SIS/CRM; records-retention configuration (Object Lock windows); and change control for prompt/model updates.

This document provides the control design for Agent 07. The institution operationalizes, validates, and accepts accountability for it.

---

Maturity: **Demonstrated locally — not AWS-deployed.** This agent runs end-to-end locally (demo mode + tests); a clean-account AWS deploy, real-model invocation, production identity, live connectors, and production sign-off remain customer/engagement work. Authoritative status: [`../../docs/STATUS-MANIFEST.md`](../../docs/STATUS-MANIFEST.md).
