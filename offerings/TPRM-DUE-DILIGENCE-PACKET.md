# Third-Party Risk Management & Vendor Due-Diligence Packet
### Answers for an Institution's Procurement & Security Teams

> This packet answers the questions an education institution's procurement, security, and privacy functions ask before they will approve a vendor or an SI to operate AI agents on student records. It is organized the way a TPRM / vendor-security questionnaire is organized: data flows, PII handling, subprocessors, model data usage, hosting, encryption, access control, audit, accessibility, incident response, and the FERPA/COPPA-specific questions. **This is a control-design disclosure, not a legal opinion or a certification.** Where an answer depends on the institution's own configuration or accountability, that is stated plainly. Customer-specific responses (subprocessor lists, region, retention windows, contract terms) are finalized during the assessment and pilot.

---

## 1. Data flow and architecture

**Q: Describe the end-to-end data flow.**
A user (student, guardian, educator, counselor, or administrator) interacts through a surface in an existing application (LMS panel via LTI 1.3, student/family portal, MS Teams, Amazon Connect, web/API). The surface forwards the **verified IdP identity and role** — it does not perform authorization. Every agent tool call (read or write) passes the **MCP authorization gateway**, which verifies identity, runs the deny-by-default authorization decision, enforces the human-approval gate on consequential actions, mints a short-lived scoped token, invokes the system of record through a validated connector, and writes a PII-masked audit record. **No agent has a direct network path to a system of record.** Inference runs on **Amazon Bedrock in the customer's account**; student PII does not egress the VPC after masking. Architecture detail: `docs/SUITE-ARCHITECTURE.md`.

**Q: Where does processing occur?**
In the **customer's own AWS account and VPC**. The deployment is customer-isolated (CloudFormation/Terraform provisions a dedicated environment). Region is configurable to meet data-residency obligations identified in the assessment.

---

## 2. PII handling

**Q: How is student PII protected?**
Structured entity recognition (the **student-PII masker**) replaces student identifiers, dates of birth, guardian details, and record-linkable fields with **stable pseudonyms before any content enters a prompt or an audit record**. The masker is stateless and runs before every gateway invocation. Stable pseudonyms allow cross-call tracing for audit without exposing FERPA-protected identifiers or COPPA-protected data for under-13 learners. This is the EDU analog of HIPAA Safe-Harbor masking, tuned to FERPA identifiers and COPPA's heightened bar.

**Q: What data does the agent see?**
Only the fields a given tool requires — connectors return narrowly-scoped results (data minimization), preventing record-linkable data from sprawling into prompts or logs. Read and write are separate tools with separate grants.

---

## 3. Subprocessors

**Q: Who are the subprocessors?**
The core processing subprocessor is **Amazon Web Services** (Bedrock for inference, AgentCore for runtime/gateway/identity, and the supporting services in `docs/SUITE-ARCHITECTURE.md` — DynamoDB, S3, KMS, CloudWatch, CloudTrail, and where used Textract/Transcribe/Translate/Polly/SageMaker). Inference runs in-account on Bedrock. The institution's existing **IdP** (Okta/Entra/Google Workspace/AD) and its **systems of record** (e.g., PowerSchool, Banner, Workday, Canvas, ServiceNow) remain under the institution's own contracts. **The definitive, deployment-specific subprocessor list is provided and maintained as a contract artifact** during the assessment/pilot; no subprocessor receives unmasked student PII for any non-educational purpose.

---

## 4. Model data usage (the critical AI question)

**Q: Is customer/student data used to train models?**
**No.** Inference runs on Amazon Bedrock in the customer's account; customer prompts and data are **not used to train foundation models**. The platform's posture is that student data is used **only for the authorized educational purpose** of the interaction and is never used to build advertising profiles, behavioral profiles, or any non-educational model — enforced as a **purpose-of-use policy at the gateway** and consistent with COPPA's school-authorized-consent limits. (The institution should confirm and retain the applicable AWS Bedrock data-handling terms as part of its records.)

**Q: Does any data leave the institution's boundary for model purposes?**
No. After masking, student PII does not egress the VPC; inference is in-account.

---

## 5. Hosting and region

**Q: Where is it hosted?**
In the customer's AWS account, customer-isolated, in a **configurable region** chosen to satisfy data-residency requirements mapped during the assessment. Network isolation is enforced via VPC with no public inbound; Bedrock is reached via VPC endpoint; inter-service traffic stays in the VPC.

---

## 6. Encryption and key management

**Q: How is data encrypted?**
Encryption at rest uses **AWS KMS with a customer-managed key** (a separate key per environment; the key policy restricts use to the agent role). Data in transit is encrypted (TLS). WORM document storage uses **S3 Object Lock in COMPLIANCE mode** for submitted enrollment documents and finalized audit snapshots; the audit trail uses **DynamoDB with point-in-time recovery** and an append-only policy (`deny:UpdateItem` / `deny:DeleteItem` on the audit partition).

---

## 7. Access controls

**Q: How is access controlled?**
Authorization is **deny-by-default with least-privilege role intersection**: `permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[agent] ∩ ROLE_ENTITLEMENTS[user_roles]`, with distinct roles for **student, guardian, educator, counselor, and administrator**. The agent can **never exceed** the human it acts for. Guardian access is scoped to the FERPA rights that transfer to the student at 18 / postsecondary enrollment. Credentials are **short-lived, per-call scoped tokens** (AgentCore Identity / STS) — **no standing service accounts**. The institution can disable any agent or tool immediately.

---

## 8. Audit and logging

**Q: What is logged, and can it be tampered with?**
Every tool attempt — **ALLOW / DENY / PENDING_APPROVAL / ERROR** — is logged to a **PII-masked, append-only audit trail** with lineage to the system of record: who acted, what tool, on what basis, and who approved any consequential action. This satisfies FERPA's recordkeeping of disclosures. AWS-level activity is captured by **CloudTrail** and feeds the same unified compliance record. Operational signals (HITL queue depth, approval latency, error rates) are in **CloudWatch** with anomaly alarms.

---

## 9. Accessibility conformance (VPAT / WCAG 2.2 AA)

**Q: What is the accessibility posture?**
Student- and family-facing surfaces are built and **tested to WCAG 2.2 AA**; conformance is a **production-readiness gate** and is re-tested under the managed service as surfaces change. The institution receives conformance documentation suitable for a VPAT/accessibility-conformance record. Note the division of responsibility: the accelerator provides the control and the testing; the institution **accepts** the conformance of its deployed surfaces. Agent 07 additionally *produces* accessible and multilingual content (alt text, captions, transcripts, plain-language and reading-level variants, audio) with human verification on consequential material.

---

## 10. Incident response

**Q: What is the incident-response process?**
Detection via CloudWatch/CloudTrail alarms; **immediate containment** — the institution can disable any agent or tool at once (no standing service accounts to individually revoke); investigation using the append-only audit trail (who accessed what, on what basis, who approved); support for the institution's **state-specific breach-notification** obligations with the audit evidence (the institution owns the legal determination and notification); and post-incident root-cause and control improvement that compounds across all eight agents. Full operational detail: `MANAGED-SERVICE-OFFERING.md` §2E.

---

## 11. FERPA-specific due diligence

**Q: Will the vendor/agent operate as a FERPA "school official" under "direct control"?**
The design supports it. A "school official" must be under the institution's **direct control** and use data **only for the authorized purpose**. The gateway enforces **purpose-of-use per tool**, the agent holds **no standing credentials**, and the institution can **disable any tool or agent immediately** — concrete technical expressions of "direct control." The specific school-official designation and the use-restriction terms are codified in the institution's contract.

**Q: How is FERPA disclosure recordkeeping met?**
By the PII-masked, append-only audit trail (§8), which records the disclosures and accesses FERPA expects institutions to be able to account for.

**Q: How is the age-of-majority rights transfer handled?**
Rights transfer to the student at 18 / postsecondary enrollment; guardian roles are scoped so a parent agent cannot surface records the parent no longer has a right to. This state is carried in IdP claims and enforced at the gateway (mapped during the assessment).

---

## 12. COPPA-specific due diligence

**Q: How are under-13 learners handled?**
An **under-13 flag in identity claims** drives heightened Bedrock Guardrails (age-appropriate content), data minimization, heightened PII masking and retention limits, and a **prohibition on any non-educational use or behavioral profiling** — enforced as a purpose-of-use policy at the gateway. The platform relies on the institution's **school-authorized consent**, limited to the educational context.

---

## 13. Data deletion and retention

**Q: How are retention and deletion handled?**
Retention windows are **configuration, not code** — set to the institution's records-retention schedule and state-law obligations (mapped in the assessment). WORM storage (S3 Object Lock) supports retention requirements; the data-minimization posture (return only what a tool needs) reduces the retained surface. Deletion processes align to the institution's records-management policy; the institution directs and owns retention/deletion decisions.

---

## 14. The standing division of responsibility

This packet describes the **control design**. The institution operationalizes, validates, and accepts accountability for: its FERPA/COPPA/PPRA compliance program and data-governance policy; IdP integration and role mapping (guardian relationships, age-of-majority); state student-privacy-law mapping; Bedrock Guardrail tuning for its population; WCAG 2.2 AA conformance acceptance of deployed surfaces; connector validation against live systems; records-retention configuration; change control for prompt/model updates; and the legal determination on any breach notification. The accelerator provides the controls; the institution accepts accountability for operating them.

---

## 15. Supporting evidence and references

- Control design and enforcement logic: `governance/README.md`, `platform_core/edu_agent_platform/mcp_gateway/`, `platform_core/edu_agent_platform/pii_masker/`.
- Architecture and AWS service mapping: `docs/SUITE-ARCHITECTURE.md`.
- The gateway rationale and hosting options: `docs/WHY-THE-MCP-LAYER.md`.
- Operational commitments: `MANAGED-SERVICE-OFFERING.md`.
- Per-stakeholder security framing: `docs/STAKEHOLDER-SECURITY-BRIEFINGS.md`.
