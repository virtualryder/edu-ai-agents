# Operations Service Desk — EDU Compliance
### The compliance spine as it applies to IT support and staff administrative workflow

> This is not a legal opinion and not a compliance certification. It is the **control design** the institution operationalizes, validates, and accepts accountability for — the part of the EDU compliance spine (`../../governance/README.md`) that bears on Agent 08. Treat it as the checklist a CISO, privacy officer, records manager, and procurement/finance lead will hold this agent to.

---

## 1. Applicable parts of the compliance spine

Agent 08 does not touch the full education-record surface that the learning agents do, but it touches student data whenever staff handle it through a ticket, a records request, or a workflow — and it touches the institution's administrative integrity directly. The relevant parts of the spine:

### FERPA — when staff handle student data
Whenever a ticket, a records request, or an administrative workflow involves personally identifiable student data, the agent operates under FERPA's terms.

- **School-official / direct-control exception.** The agent acts as a vendor under the institution's **direct control** and uses data only for the authorized **purpose-of-use** per tool. It holds no standing credentials, and the institution can disable any tool or agent immediately.
- **Identity-scoped retrieval.** A user reaches only the records their role and group membership entitle them to (Layer 3 deny-by-default + least-privilege intersection); a student-facing service-desk interaction surfaces that student's tickets and no other's.
- **Age-of-majority / rights transfer.** Guardian roles are scoped to the FERPA rights that transfer to the student at 18 / postsecondary enrollment, carried in the IdP claims.
- **Recordkeeping of disclosures.** The append-only, PII-masked audit trail records who accessed what, on what basis, and who approved any action.
- **No redisclosure.** Connectors return only the fields a tool needs; the PII masker prevents record-linkable data from sprawling into transcripts, drafts, or logs.

### Records management & retention
Records requests, board material, and finance/procurement artifacts fall under retention schedules. The agent integrates with the records-management system, and **S3 Object Lock** WORM storage plus configurable retention windows support the institution's schedule. The data-minimization posture — return only what a tool needs — reduces the retained surface.

### Segregation of duties
The defining administrative control. In finance and procurement especially, the human who **approves** must not be the agent that **initiated**. The agent drafts and initiates; a **separate, named, authorized human approves** through the HITL gate. The gateway enforces that the approval record carries a valid reviewer identity distinct from the initiating context before minting the write token.

### State student-privacy laws
Where staff workflows touch student data, state obligations (consent, data-residency, retention, breach notification, vendor-contract terms) apply. The control design is parameterized — region/VPC, retention windows, and prohibited-use policies are configuration, mapped during the assessment phase.

---

## 2. The bright line — what Agent 08 never decides

Agent 08 is a **bounded agent**. It diagnoses, drafts, initiates low-risk workflows, and escalates — it does not autonomously perform privileged remediation or approve consequential administrative action. The bright line for this agent:

| The agent may | The agent never (without a named human) |
|---|---|
| Run diagnostics; read telemetry; answer grounded IT and policy questions; draft scopes/RFPs/board packets; create tickets; initiate approval workflows | Reset a password or restart a managed service on its own judgment |
| Retrieve an approved policy or procedure within the user's entitlements | Approve a purchase requisition, finance workflow, or any item it itself initiated |
| Route an incident with confirmation | Resolve a security, identity, or safeguarding event |
| Track a workflow to completion | Take any irreversible or consequential administrative action autonomously |

The distinction between a **draft**, a **recommendation**, and an **approved decision** is explicit in the agent's output and enforced by the HITL gate. A draft is never an approval.

---

## 3. HITL gates and escalation rules

Every WRITE / PRIVILEGED-REMEDIATION action blocks on a **HITL gate** — implemented as the gateway's human-approval enforcement and, in the native rebuild, **Step Functions `waitForTaskToken`**. The graph suspends, the proposed action is surfaced to a named reviewer in the appropriate role, and execution resumes only when a verified approval record is written. There is no path from intake to a privileged action that bypasses the gate.

Escalation rules specific to this agent:

- **Privileged IT remediation** (password reset, managed-service restart, incident routing) requires a named, authorized human approver bound into the record.
- **Finance and procurement** require **segregation of duties** — the approver is a separate authorized human from the initiating agent context.
- **Security, identity, and safeguarding events go immediately to a human and are never auto-resolved.** A suspected account compromise, an identity-spoofing signal, a safeguarding concern, or anything touching student safety escalates the instant it is detected; the agent does not attempt remediation, does not close the ticket, and does not reason about whether it is "really" a concern.

---

## 4. Data minimization

The agent requests only the fields a tool needs and returns only what the user is entitled to. The **student-PII masker** runs before any tool result enters a prompt or an audit record, replacing FERPA-protected identifiers (and COPPA-protected data for under-13 learners) with stable pseudonyms that allow cross-call tracing without exposing record-linkable data. Document-level permissions and group-membership propagation (see `integration-guide.md`) ensure retrieval never crosses a user's entitlements — the agent cannot draft a board packet from documents the requester could not open, and cannot surface a ticket belonging to another student.

---

## 5. Audit

Every gateway event — ALLOW, DENY, PENDING_APPROVAL, ERROR — is logged to the **append-only DynamoDB** audit trail with lineage to the system of record, satisfying FERPA's recordkeeping of disclosures. Finalized administrative artifacts and records-request outputs are written to **S3 Object Lock** (COMPLIANCE mode) for tamper-evident retention. **CloudTrail** captures the API-level record and feeds the same unified compliance trail. For every privileged remediation and every initiated workflow, the audit answers the questions an auditor, a records request, or a privacy officer will ask: who acted, on what basis, what was done, and **who approved it**.

---

## 6. What the customer still owns

This document provides the control design. The institution remains responsible for: its FERPA compliance posture and data-governance program; IdP integration and role/group mapping (including guardian relationships and age-of-majority); state student-privacy-law mapping; Bedrock Guardrail tuning for its population (including minors using the service desk); connector validation against live ITSM/HR/ERP/procurement/facilities systems; records-retention configuration; segregation-of-duties policy definition; and change control for prompt and model updates. See `../../governance/README.md` for the full spine and `../../README.md` for the compliance disclaimer.

---

Maturity: **Demonstrated locally — not AWS-deployed.** This agent runs end-to-end locally (demo mode + tests); a clean-account AWS deploy, real-model invocation, production identity, live connectors, and production sign-off remain customer/engagement work. Authoritative status: [`../../docs/STATUS-MANIFEST.md`](../../docs/STATUS-MANIFEST.md).
