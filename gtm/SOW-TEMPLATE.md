# Statement of Work — EDU AI Agent Suite
### Template for SI Delivery Engagements

> This template covers four engagement types: (A) Discovery & Readiness Assessment, (B) Demo-Mode Proof of Concept, (C) Pilot Deployment, and (D) Managed Service. Use the relevant section(s). Placeholder text in [brackets] must be completed for each engagement. All figures and timelines are illustrative; actual scope, pricing, and milestones are negotiated per engagement.

---

## Cover Terms

**Client Institution:** [Full legal name of the education institution]
**Institution Type:** [K–12 District / Charter or Private School / Community College / University / Online Program / Workforce Education Provider]
**Engagement Type:** [Assessment / POC / Pilot / Managed Service — select one or more]
**Systems Integrator:** [SI legal name]
**Statement of Work Number:** [SOW-YYYY-NNN]
**Effective Date:** [Date]
**Estimated Period of Performance:** [Start date] to [End date]
**Governing Agreement:** This SOW is issued under and incorporates [Master Services Agreement / Professional Services Agreement] dated [date].

---

## 1. Background and Purpose

The institution seeks to evaluate and deploy governed AI agents on its student records and systems of record in a manner consistent with FERPA, COPPA, PPRA, IDEA/Section 504, ADA/Section 508, applicable state student-privacy law, and the institution's own data-governance program. The engagement uses the **EDU AI Agent Suite**, a governed accelerator built on Amazon Web Services that provides one MCP authorization gateway, one identity and audit layer, and a shared compliance spine across eight high-value education workflows.

The platform is not a certified product or a validated student-information system. It is a governed accelerator the institution operationalizes, validates, and accepts accountability for. The institution retains responsibility for its FERPA/COPPA/PPRA compliance posture, IdP integration and role mapping, connector validation against live systems, state-law obligations, Bedrock Guardrail configuration for its population, WCAG 2.2 AA conformance testing of deployed surfaces, and records-retention and change-control procedures.

---

## 2. Scope of Work

### Section A — Discovery & Readiness Assessment *(include if applicable)*

**Objective:** Produce a signed readiness roadmap that maps the institution's FERPA/COPPA posture, IdP and role model, system inventory, accessibility baseline, state-law obligations, and use-case priorities to the platform's control design.

**Activities:**

| Workstream | SI Responsibility | Institution Responsibility |
|---|---|---|
| A1. Data governance & FERPA/COPPA posture | Review data-governance documentation; map each federal obligation to the platform control that honors it; identify gaps | Provide relevant policies, vendor agreements, current disclosure records; designate FERPA officer as primary contact |
| A2. IdP & role mapping | Analyze IdP (Okta / Entra ID / Google Workspace / Active Directory / other); design role mapping for student, guardian, educator, counselor, administrator; document age-of-majority and under-13 handling | Provide IdP documentation and administrator access for architecture review; identify role-mapping gaps |
| A3. System inventory | Catalog SIS / LMS / ERP / CRM / ITSM and other systems of record; assess API availability, auth model, rate limits, data ownership; produce reachability rating per system | Designate system owners; provide API documentation; facilitate interviews |
| A4. Accessibility baseline | Assess current conformance posture of portals against WCAG 2.2 AA; identify multilingual and reading-level obligations | Provide existing VPAT documentation; identify accessibility coordinator |
| A5. State student-privacy law mapping | Map applicable state statutes; document data-residency, consent, breach-notification, and vendor-contract obligations | Confirm operating states; provide state contracts and DPA templates if available |
| A6. Use-case prioritization | Score each agent candidate on value, decision-risk, system readiness, and governance readiness; produce ranked list and recommended landing agent | Participate in prioritization workshop; identify service and academic owners for each candidate workflow |
| A7. Hosting & gateway-model selection | Present three gateway hosting options (managed AgentCore Gateway, AWS primitives, self-built FastMCP) with rationale; recommend based on operating-model preferences | Designate platform team representative; provide AWS account status |

**Timeline:** Approximately 3–5 weeks.

**Deliverables:**
1. Privacy posture summary: each federal and state obligation mapped to the platform control that honors it, plus a gap list.
2. Role-mapping design: IdP claim-to-role mapping, age-of-majority and guardian-relationship handling plan, and remediation list.
3. System inventory: reachability rating per system and recommended single pilot target.
4. Accessibility baseline and conformance gap list.
5. State-law obligation map expressed as platform configuration.
6. Ranked use-case list with recommended landing agent and expansion order.
7. Recommended gateway hosting model with rationale.
8. Readiness roadmap: all seven workstreams synthesized into a prioritized, signable document.

---

### Section B — Demo-Mode Proof of Concept *(include if applicable)*

**Objective:** Prove the governed-platform controls are real and enforced — with running software, not slides — before any live system is touched. Deliver a go/no-go decision input for the pilot.

**Landing agent:** [Agent 01 Student & Family Services Concierge / Agent 03 Educator Copilot / Agent 07 Document & Accessibility Services / Agent 08 Operations Service Desk — select one; higher-governance agents 02/04/05/06 are not POC subjects]

**Customer scenarios (to be confirmed in Week 0):**
1. [Customer scenario 1 — expressed in institution's vocabulary and department structure]
2. [Customer scenario 2]
3. [Customer scenario 3 — optional]

**Governance moments demonstrated (non-negotiable):**
- A **deny** — an unauthorized tool call blocked at the gateway before any system is reached
- A **PII mask** — student identifier replaced by a stable pseudonym before it enters a prompt or audit log
- A **human-gated write** — a consequential action blocked until a named reviewer identity is bound into the record, then executed
- An **audit entry** — the reviewer reads the PII-masked, append-only record of the entire interaction

**Activities:**

| Week | Activities |
|---|---|
| **0 (pre-start)** | Confirm landing agent and 2–3 customer scenarios; identify workshop stakeholders; agree go/no-go criteria in writing |
| **1** | Configure the suite in `EXTRACT_MODE=demo`; load fixtures appropriate to institution type; tailor grounding content and vocabulary |
| **2** | Script the demo against customer scenarios; wire governance moments into the script; rehearse internally |
| **3** | Facilitated stakeholder workshop; capture objections and questions live; adjust the demo to address the sharpest concerns |
| **4 (or end of Week 3)** | Deliver POC findings memo, recorded demo, and recommended pilot scope; hold the go/no-go conversation |

**Deliverables:**
1. A running demo of the landing agent in `EXTRACT_MODE=demo`, configured to the institution's type, scenarios, and vocabulary.
2. A recorded walkthrough including all governance moments, suitable for circulation to stakeholders who could not attend live.
3. A facilitated stakeholder workshop and a captured objection/question log with responses.
4. A POC findings memo: what was demonstrated, which scenarios it addressed, which objections were raised and answered, and what the POC deliberately did not prove.
5. A recommended pilot scope: proposed live system of record, gateway-first sequencing, baseline metrics to capture, and exit criteria to production.

**Success criteria:** All of the following must hold —
- Stakeholders have *seen* — not been told — that the agent operates under deny-by-default authorization, masks student PII, blocks consequential actions behind a named human approver, and produces a tamper-evident audit trail.
- The security and privacy stakeholders can articulate in their own words why this is "an agent that acts under governed control" rather than "a chatbot with API keys."
- At least two customer scenarios were demonstrated in the institution's vocabulary and confirmed recognizable and valuable by the relevant service or academic owner.

**Out of scope:** any connection to a live SIS/LMS/ERP/CRM/ITSM; real student, family, or staff data; IdP integration; Guardrail tuning for the customer's population; WCAG 2.2 AA conformance testing; production AWS account provisioning.

---

### Section C — Pilot Deployment *(include if applicable)*

**Objective:** Deploy one agent against one live system of record in the institution's AWS account, with the MCP authorization gateway and identity wiring built first (Phase 1), and measure a demonstrated outcome against a pre-deployment baseline.

**Pilot agent:** [Agent 01 / 03 / 07 / 08 — best-first agents only for an initial pilot]

**Live system of record:** [PowerSchool / Infinite Campus / Banner / Workday Student / Canvas / Blackboard / Schoology / ServiceNow / Jira / Slate / Salesforce EDU / other — one system only]

**Gateway hosting model:** [Managed AgentCore Gateway / AWS API Gateway + Lambda + Step Functions / self-built FastMCP]

**Timeline:** [6 weeks (compressed) / 8 weeks / 10 weeks / 12 weeks]

**Phases and milestones:**

| Phase | Weeks (12-week plan) | Milestone | Exit gate |
|---|---|---|---|
| **Phase 1 — Gateway & identity foundation** | 1–4 | Gateway deployed in customer AWS account; IdP federated; role mapping live; audit trail recording ALLOW/DENY/PENDING_APPROVAL/ERROR; PII masker operating | Security reviewer can observe a deny, a PII mask, and an audited write; no standing service accounts; short-lived scoped tokens verified |
| **Phase 2 — Live connector & grounding** | 4–6 | One live system-of-record connector validated against the vendor API; grounding content loaded; Guardrails tuned | Connector returns only the fields each tool needs; grounding fails fast on ungrounded output |
| **Phase 3 — HITL & agent workflow** | 6–8 | Pilot agent live end-to-end; HITL queue operating; reviewers trained; consequential actions provably gated | No path from intake to a consequential finalize bypasses the human gate |
| **Phase 4 — Accessibility & pilot launch** | 8–10 | WCAG 2.2 AA conformance tested on the pilot surface; bounded user cohort live; baseline metrics confirmed captured | Accessibility conformance evidence in hand; baseline established |
| **Phase 5 — Measure & decide** | 10–12 | Outcome measurement against baseline; incident/escalation review; exit-criteria assessment | Go/no-go to production with documented results |

*Phase 1 (the gateway) is never compressed regardless of timeline reduction. Accessibility gate and HITL-bypass assertion are non-negotiable.*

**Baseline metrics (captured before Phase 4 pilot launch):**

| Category | Baseline metric to capture | Institution data source |
|---|---|---|
| **Labor** | [e.g., Staff minutes per routine status inquiry; staff hours in peak season] | [e.g., Time-tracking system / supervisor estimate] |
| **Service** | [e.g., Average response time to routine inquiries; after-hours inquiry volume unanswered] | [e.g., Contact center logs / email system] |
| **Learning** | [If applicable — e.g., feedback turnaround time] | [e.g., LMS gradebook] |
| **Student journey** | [e.g., Enrollment completion rate; application completion rate] | [e.g., SIS enrollment reports] |
| **Risk & quality** | [e.g., Error/override/escalation rate baseline; equity baseline across cohorts] | [e.g., Manual review logs] |

**Deliverables:**
1. A deployed, governed gateway in the customer's AWS account — reusable by every future agent.
2. One validated live connector to the pilot system of record.
3. The pilot agent in production against the bounded cohort, with grounding, Guardrails, and the HITL gate operating.
4. A WCAG 2.2 AA conformance test report for the pilot surface.
5. A measured outcome report against the pre-pilot baseline across all relevant ROI categories.
6. A security and privacy evidence package for the institution's records.
7. A production rollout plan: full-population scaling, additional systems, and the portfolio-expansion sequence.

**Exit criteria to production — all of the following must hold:**
- Governance proven in the live environment: deny-by-default authorization, PII masking, short-lived scoped tokens, and enforced HITL gate operating against the live system — confirmed by a security reviewer.
- The bright line held: the agent never decided a grade, admission, disciplinary outcome, financial-aid award, special-education eligibility, or placement; every consequential action gated to a named, authorized human.
- WCAG 2.2 AA conformance evidenced on the pilot surface (or documented remediations accepted).
- Outcome demonstrated: measurable improvement against the baseline in at least one primary ROI category, with no unacceptable regression in Risk & quality.
- Operational readiness: HITL queue, model/prompt change control, and incident-response paths operating and ready to transition to managed service.

**Out of scope:** additional agents beyond the pilot agent; additional systems of record beyond the one live system; full-population rollout; emerging roadmap use cases.

---

### Section D — Managed Service *(include if applicable)*

**Objective:** Operate the governed platform in production — HITL queue, model and prompt change control, evaluation and fairness monitoring, accessibility maintenance, incident response, and monthly outcome reporting.

**Agents in scope at service commencement:** [List by number and name]
**Service commencement date:** [Date — conditioned on pilot exit criteria being met]
**Service model:** [Fully SI-run / Co-managed / Advisory]

**Service components:**

**A. HITL Queue Operations** — Monitor queue depth and approval latency; alarm on backlog and aging items; maintain reviewer roster and role bindings; track override and escalation rates.

**B. Model & Prompt Change Control** — Maintain hash-pinned prompts in `governance/prompt_manifest.json`; run eval harness and require sign-off before any Bedrock model version change; version grounding-content updates.

**C. Evaluation & Fairness Monitoring** — Run structural eval regression on every change and weekly; monitor grounding-failure rate; run fairness monitoring by cohort monthly with immediate review on a fairness alarm; run red-team scenarios periodically.

**D. Accessibility Conformance Maintenance** — Re-test student- and family-facing surfaces against WCAG 2.2 AA when they change and quarterly; maintain VPAT documentation.

**E. Incident Response** — Detection via CloudWatch/CloudTrail; containment (disable any agent or tool immediately); investigation via PII-masked append-only audit trail; support institution's breach-notification obligations with audit evidence.

**Illustrative SLA targets:**

| Dimension | Illustrative target |
|---|---|
| Platform availability | 99.5%+ (business-critical agents), excluding scheduled change windows |
| HITL approval-queue health | Alarm if any consequential item ages beyond [4 business hours — to be agreed] |
| Sev-1 incident response | Acknowledge within 1 hour; contain (disable agent/tool) immediately on confirmed disclosure risk |
| Eval regression | Run on every change + weekly; block promotion on regression |
| Fairness review | Monthly cohort report; immediate review on a fairness alarm |
| Accessibility re-test | On surface change + quarterly |

**Reporting:** Monthly operations report covering availability, HITL queue health, eval and fairness results, grounding-failure rates, accessibility status, incidents, and outcome metrics.

---

## 3. Assumptions

1. The institution has, or is pursuing, an AWS account with Amazon Bedrock access enabled in [us-east-1 / us-west-2 / other region — confirm].
2. The institution will provide access to the relevant system-of-record API documentation and administrator contacts within [5 business days] of SOW execution.
3. The institution will designate named points of contact for: FERPA/privacy officer, CISO/security delegate, IdP administrator, system-of-record owner, accessibility coordinator, and executive sponsor.
4. Workshop and review participation by institution stakeholders will be available at the cadences specified in the timeline.
5. The institution acknowledges that the platform is a governed accelerator, not a certified product, and that operationalization, validation, and compliance accountability remain with the institution.
6. Bedrock Guardrail configuration appropriate to the institution's student population (including any under-13 considerations) is the institution's responsibility to approve; the SI will provide a recommended configuration.
7. WCAG 2.2 AA conformance testing in the Pilot is performed by [SI / institution / named third party — confirm]. Any conformance gaps requiring remediation are escalated to the institution's accessibility coordinator.

---

## 4. Exclusions

The following are explicitly out of scope unless separately contracted:

- University research administration, advancement/fundraising, and specialized laboratory agents.
- The four emerging/roadmap use cases: longitudinal learner-success orchestrator, precision-learning agent teams, cross-system autonomous institutional operations, and dialogue-based assessment/simulations.
- Full production rollout to the institution's entire user population (pilot scope is a bounded cohort).
- Additional agents or systems of record beyond those specified in the in-scope sections above.
- Legal opinions or compliance certifications of any kind.
- Penetration testing (may be separately contracted to a qualified third party; the SI provides the security evidence package the penetration tester consumes).

---

## 5. Change Control

Any addition to scope, timeline extension, or change to the in-scope system of record or agent requires a written Change Order signed by both parties. Changes to prompt content or model version within the Managed Service follow the change-control procedures in Section D-B above and do not require a Change Order; changes to the agent's tool grants or role entitlements do.

---

## 6. Data Governance and Compliance Obligations

### 6.1 FERPA
The institution is the educational agency responsible for its FERPA compliance. The SI provides and operates the governed platform — the MCP authorization gateway, identity federation, deny-by-default authorization, human-approval gate, PII-masked append-only audit trail, and Bedrock Guardrails — as tools the institution uses to meet its obligations. The SI does not make determinations of FERPA compliance on behalf of the institution.

Specific obligations:
- **Legitimate educational interest:** The institution defines and documents the legitimate educational interest that justifies each agent's access to education records, and encodes it in the role-entitlement grants and tool-grant authorizations in the platform configuration.
- **Disclosure recordkeeping:** The platform's append-only audit trail is designed to satisfy FERPA's recordkeeping of disclosures (34 CFR §99.32). The institution's records custodian is responsible for the accuracy of role entitlements that generate these records and for producing them in response to parent/student requests or audits.
- **School official / direct control:** The institution is responsible for ensuring the SI and the platform meet the FERPA "school official under direct control" exception criteria (34 CFR §99.31(a)(1)(i)(B)) where applicable, and for documenting this in its vendor agreements.
- **Age-of-majority and guardian rights:** The institution is responsible for maintaining the accuracy of the age-of-majority and guardian-relationship state expressed in the IdP claims the platform relies upon.

### 6.2 COPPA
For institution types serving children under 13, the institution is the operator responsible for COPPA compliance. The SI provides a platform with configurable protections (heightened Guardrails for under-13 populations, PII masking tuned to COPPA identifiers). The institution is responsible for obtaining verifiable parental consent where required and for configuring the platform for its under-13 population.

### 6.3 Data Residency
All student education records processed by the platform in production remain within the institution's own AWS account and the selected AWS region. No student PII is transmitted to SI systems or to Anthropic/AWS systems outside the scope of model inference in the institution's account. The institution selects its AWS region based on data-residency requirements; see `docs/AWS-FUNDING-AND-PREREQUISITES.md` for region-selection guidance.

### 6.4 Breach Notification
The SI will notify the institution without undue delay (and in any event within [48 / 72 hours — to be agreed] of confirmed discovery) of any security incident affecting the governed platform that involves or is reasonably suspected to involve unauthorized access to student education records. The institution is responsible for making the legal determination of whether a reportable breach has occurred under applicable state law and for any required notifications to students, parents, or regulators. The SI provides audit-trail evidence to support the institution's investigation and notification obligations.

---

## 7. Fees and Payment Schedule

*[This section to be completed per engagement. Illustrative structure below — not a quote.]*

| Milestone | Amount | Condition |
|---|---|---|
| SOW execution | [X]% of total engagement fee | Upon signature |
| Assessment readiness roadmap delivered | [X]% | Upon client acceptance |
| POC go/no-go memo delivered | [X]% | Upon client acceptance |
| Phase 1 (Gateway) exit gate passed | [X]% | Security reviewer sign-off per Section C milestones |
| Pilot exit to production (all exit criteria met) | [X]% | Per Section C exit criteria |
| Managed service: monthly | [Monthly run rate] | Net [30] days from invoice |

Expenses: [per governing agreement / billed at cost with receipts / not billed separately — confirm].

---

## 8. Intellectual Property and Confidentiality

**Suite accelerator:** The EDU AI Agent Suite (including `platform_core/`, agent code, governance framework, and CloudFormation/Terraform templates) is the SI's intellectual property, licensed to the institution for use during the term of this SOW under the terms of the governing agreement. The institution receives a right to use the deployed platform in its AWS account; it does not receive a license to sublicense, sell, or distribute the accelerator.

**Customer data and configurations:** Role entitlements, connector configurations, grounding content, and institutional data processed by the platform are the institution's property. Upon termination, the SI will return or destroy institution-owned configuration data as directed, consistent with applicable records-retention obligations.

**Confidentiality:** Both parties agree that all non-public information exchanged under this SOW — including system-of-record API details, IdP configurations, student data, audit records, and pricing — is confidential information subject to the governing agreement's confidentiality provisions.

---

## 9. Term and Termination

**Term:** This SOW is effective on the Effective Date and expires on completion of all milestones or [end date], whichever comes first, unless extended by mutual written agreement. Managed Service SOWs have a [12-month / 24-month — to be agreed] initial term with auto-renewal provisions per the governing agreement.

**Termination for convenience:** Either party may terminate this SOW for convenience with [30 / 60 — to be agreed] days' written notice. The institution is responsible for fees incurred through the notice period plus any non-cancelable commitments. The SI will provide a transition plan and documentation for orderly handoff.

**Termination for cause:** Either party may terminate for material breach with [10 business days'] written notice and opportunity to cure.

---

## 10. Signatures

**For the Systems Integrator:**

Name: _______________________________
Title: _______________________________
Date: _______________________________
Signature: ___________________________

**For the Institution:**

Name: _______________________________
Title: _______________________________
Date: _______________________________
Signature: ___________________________

*By signing, both parties confirm that: (a) this SOW is issued under and governed by the Master Services Agreement referenced on the cover page; (b) the institution has read and understands the compliance disclaimer in Section 2 above and in the suite README; and (c) the institution accepts that operationalization, validation, and compliance accountability for the platform remain with the institution.*
