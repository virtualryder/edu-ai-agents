# Operations Service Desk
### IT support and internal staff knowledge & administrative workflow — a bounded agent that diagnoses, drafts, and initiates, while a named human owns every privileged remediation and every consequential administrative action

> **Agent 08 consolidates two production use cases — UC10 IT Service Desk and UC11 Staff Knowledge & Admin Workflow — into one governed agent for the people who keep an institution running.** It is a best-first deployment: broad visibility, comparatively low decision-risk, mature workflows, and a deflection/cycle-time return that is straightforward to measure. The defining design choice is a **bright line between diagnostic actions and privileged remediation**, and a hard separation of tool sets by administrative domain so retrieval and action never cross a user's entitlements.

---

## What it does

The Operations Service Desk answers and acts across two capability surfaces that the canon keeps deliberately bounded.

**(A) IT service desk** — for students, families, teachers, and staff. It handles the high-volume, repetitive surface of education IT: password and SSO problems, Wi-Fi and connectivity, device configuration, LMS access, classroom-technology faults, application outages, printer and peripheral issues, software-install requests, and ticket creation and status. With approval it can reset a password, restart a managed service, gather diagnostics, and route an incident. The distinction the agent enforces is the one that matters: **diagnostics are read/low-risk** and run freely; **a password reset or a service restart is privileged remediation** and is HITL-gated to a named, authorized human.

**(B) Internal staff knowledge & administrative workflow** — for the people who run HR, procurement, finance, grants, records, facilities, and onboarding. It answers policy and procedure questions, gathers information, drafts documents (contract scopes, RFPs, statements of work, board-packet material, policy comparisons), initiates approval workflows, and tracks them to completion. The agent **drafts and initiates; a separate authorized human approves** — segregation of duties is the operating principle, not a courtesy.

In the suite's vocabulary, this is a **decision-support** agent. It retrieves approved institutional content, runs safe diagnostics, drafts documents, calls narrowly-scoped tools, and initiates low-risk workflows — and it escalates everything consequential to a human. It is not an autonomous administrator, and it never silently resolves a security, identity, or safeguarding event.

| What this is | What this is not |
|---|---|
| A governed front door for IT support and staff administrative workflow, with diagnostics and privileged remediation strictly separated | An unsupervised remote-administration tool that resets credentials or restarts services on its own judgment |
| A drafting and workflow-initiation engine where a separate authorized human approves every consequential step | An approver — it never signs off on its own draft, especially in finance and procurement |
| Retrieval bounded by identity, role, group membership, and document-level permissions | An enterprise search that returns whatever it can find regardless of who is asking |
| Separate agents / tool sets per administrative domain, with no unrestricted cross-domain reach | One agent with a master key to HR, finance, procurement, facilities, and the device fleet |

---

## What it solves

Education IT and administrative teams support large, distributed populations with limited staffing, and a large share of their inbound is repetitive: the same password resets, the same connectivity tickets, the same "where is the travel-reimbursement form" and "what is the procurement threshold" questions, asked thousands of times across a school year. That repetition is expensive in two currencies — staff hours and classroom time — and it crowds out the work that genuinely needs a human.

On the IT side, the agent deflects the repetitive tier, gathers diagnostics so a human starts triage already informed, and handles the low-risk remediations under an approval gate — shrinking mean time to resolution and classroom downtime without handing the agent standing administrative power. On the administrative side, it collapses the time staff spend hunting through policy PDFs and intranet pages, drafts the documents that consume disproportionate effort (scopes, bids, RFPs, board packets), and moves requests through approval with the workflow tracked rather than lost in an inbox. Throughout, the governance posture is what makes it deployable: **deny-by-default authorization, least-privilege intersection, document-level permissions, and group-membership propagation** ensure the agent never crosses a user's entitlements, and the **HITL gate** ensures a named human owns every privileged or consequential action.

---

## Where it sits in the rollout & why

Agent 08 is in the **best-first deployment tier** alongside Agent 01 (Concierge), Agent 03 (Educator Copilot), and Agent 07 (Document & Accessibility Services). These are the right places to land: broad visibility across the institution, comparatively low decision-risk, mature and well-understood workflows, and a measurable deflection/cycle-time return that builds the credibility the higher-governance agents (02, 04, 05, 06) will need.

The reason 08 deploys early is that almost everything it touches has a clean separation between a low-risk read and a consequential write, and the consequential side is small, well-bounded, and naturally gated. A diagnostic is a read; a password reset is a gated write. A policy answer is a read; initiating a purchase requisition is a gated, segregation-of-duties workflow. That structure maps directly onto the platform's deny-by-default gateway and HITL gate, so the agent reaches production value quickly without taking on the evaluation, bias-testing, and evidence-retention burden the learning-and-outcomes agents carry. See `../README.md` for the full sequencing and `../docs/SUITE-ARCHITECTURE.md` for where the agent sits in the six-layer architecture.

---

## AWS implementation

Agent 08 follows the suite's six-layer reference architecture (`../docs/SUITE-ARCHITECTURE.md`). It surfaces in **Amazon Connect** (voice/SMS/chat for the service desk) or a thin **web/mobile** front end and **Microsoft Teams** where staff already work (Layer 1). The agent itself is an **Amazon Bedrock AgentCore Runtime** container or a **Strands + Step Functions** native rebuild (Layer 2); inference runs on **Amazon Bedrock (Claude models)** in-account, with **Bedrock Guardrails** on every call (Layer 5). Every tool call — read or write — passes through the **MCP authorization gateway** (**AgentCore Gateway** + **AgentCore Identity**, Layer 3); no agent has a direct network path to a system of record. IT knowledge and staff policy/procedure content live in **Amazon Bedrock Knowledge Bases** with document-level permissions, and broad enterprise staff search can use **Amazon Q Business**; structured transactions reach HR, finance, procurement, and facilities through **AgentCore Gateway / API Gateway** targets (Layer 4). Approvals are enforced by **Step Functions** `waitForTaskToken` (Layer 2). Observability is **CloudWatch** plus approved-endpoint telemetry; the audit trail is **DynamoDB** append-only and **S3 Object Lock**, with **CloudTrail** feeding the unified compliance record (Layer 6). Encryption is **AWS KMS** customer-managed keys.

The single most important control in this agent is the table below: tools are split into **READ / DIAGNOSTIC** (run freely, low-risk) and **WRITE / PRIVILEGED REMEDIATION** (HITL-gated to a named, authorized human). Read and write are always separate tools with separate grants, exactly as the canon requires.

| Tool (`connector_kind.operation`) | Class | Gate |
|---|---|---|
| `itsm.search_knowledge` | READ / DIAGNOSTIC | None — grounded retrieval from approved IT knowledge base |
| `itsm.get_ticket_status` | READ / DIAGNOSTIC | None — status lookup, identity-scoped to the requester's tickets |
| `endpoint.get_device_telemetry` | READ / DIAGNOSTIC | None — read-only health/connectivity signals from authorized, institution-managed devices |
| `endpoint.run_safe_diagnostic` | READ / DIAGNOSTIC | None — non-mutating Lambda diagnostic (ping, link check, service status) on authorized devices |
| `kb.search_staff_policy` | READ / DIAGNOSTIC | None — document-level-permissioned retrieval (HR/finance/procurement/facilities policy) |
| `hr.lookup_procedure` · `procurement.lookup_threshold` · `finance.lookup_procedure` | READ / DIAGNOSTIC | None — domain-scoped policy/procedure lookup, no cross-domain reach |
| `doc.draft_artifact` | READ / DIAGNOSTIC | None to draft; the *resulting action* is gated — a draft is not an approval |
| `itsm.create_ticket` | WRITE | HITL gate — confirmation; ticket is the audit anchor |
| `itsm.route_incident` | WRITE / PRIVILEGED REMEDIATION | HITL gate — named human; security/identity/safeguarding routes escalate immediately |
| `identity.reset_password` | WRITE / PRIVILEGED REMEDIATION | HITL gate — named, authorized human approver; bound into the record |
| `endpoint.restart_managed_service` | WRITE / PRIVILEGED REMEDIATION | HITL gate — named approver; Systems Manager scoped to authorized devices only |
| `procurement.initiate_requisition` · `finance.initiate_workflow` | WRITE | HITL gate — segregation of duties: agent initiates, a *separate* authorized human approves |
| `facilities.submit_request` · `hr.initiate_onboarding_task` | WRITE | HITL gate — named approver in the owning domain |

Privileged remediation on devices runs through **AWS Systems Manager**, and it is scoped **only to institution-managed, authorized devices** — never to personal or unmanaged endpoints. Diagnostic actions and privileged remediation are kept in separate tool sets with separate grants, and **tool sets are separated by administrative domain** (IT, HR, finance, procurement, facilities): there is **no unrestricted cross-domain search** and no single agent identity that can reach across all domains. Deployment topology and the AgentCore-Runtime-vs-Strands choice are detailed in `docs/aws-deployment-guide.md`.

---

## Systems of record / connectors

The agent calls every system of record through the gateway's connector framework (`../platform_core/edu_agent_platform/mcp_gateway/`); it never holds direct credentials to any of them.

| Domain | System of record (examples) | Connector role |
|---|---|---|
| ITSM | ServiceNow, Jira Service Management | Ticket create/status, incident routing |
| Endpoint management | AWS Systems Manager (authorized managed devices only), endpoint telemetry | Safe diagnostics, gated service restart |
| Identity | IdP via IAM Identity Center / Cognito (Okta, Entra, Google Workspace, AD) | Identity claims, role/group membership, gated password reset |
| HR / ERP | Workday, Banner, PeopleSoft | Policy/procedure lookup, onboarding workflow initiation |
| Procurement | Institution procurement platform | Threshold lookup, requisition initiation (segregation of duties) |
| Finance | ERP finance module, grants management | Procedure lookup, travel/expense and finance workflow initiation |
| Facilities | Facilities/work-order system | Facilities request submission and tracking |
| Knowledge | Amazon Bedrock Knowledge Bases (document-level permissions); Amazon Q Business for broad staff search | Grounded retrieval, permission-respecting |
| Records | Records-management / retention system | Records-request handling, retention-schedule integration |

Connector and identity/role-mapping detail — including group-membership propagation into retrieval and document-level permissions in Bedrock Knowledge Bases — is in `docs/integration-guide.md`.

---

## Phased adoption

| Phase | Scope | What the agent does | Gate posture |
|---|---|---|---|
| **1 — Deflect & inform** | IT knowledge + staff policy search | Answers grounded IT and policy/procedure questions; creates tickets; reads ticket status | Reads pass through; ticket creation confirmed |
| **2 — Diagnose** | Endpoint telemetry + safe diagnostics | Gathers diagnostics on authorized managed devices so a human starts triage informed | Diagnostics are read/low-risk; no remediation yet |
| **3 — Gated remediation** | Privileged IT actions | Resets a password, restarts a managed service, routes an incident — each HITL-gated to a named human; security/identity/safeguarding escalates immediately | Every privileged remediation gated |
| **4 — Draft & initiate admin workflow** | HR/finance/procurement/facilities | Drafts scopes/RFPs/board packets, initiates approval workflows, tracks to completion | Segregation of duties: agent initiates, separate human approves |

Each phase adds capability without loosening the bright line. The maturity ladder advances per phase — Documented today; Demonstrated and Deployable in subsequent passes — exactly as the suite's delivery model intends (`../README.md`).

---

## Regulations that apply

| Regulation | Why it applies to Agent 08 |
|---|---|
| **FERPA** | Whenever staff handle personally identifiable student data through a ticket, a records request, or a workflow, the agent operates under FERPA's school-official / direct-control terms and purpose-of-use limits; the append-only audit supports recordkeeping of disclosures |
| **Records management & retention** | Records requests, board material, and finance/procurement artifacts are subject to retention schedules — supported by S3 Object Lock and configurable retention windows |
| **Segregation of duties** | Procurement and finance workflows require that the human who approves is not the agent that initiated — enforced by the HITL gate and separate-role authorization |
| **State student-privacy laws** | Where staff workflows touch student data, state obligations (residency, retention, breach notification, vendor-contract terms) apply and are parameterized in configuration |

The full compliance treatment — bright-line and escalation rules, HITL gates, immediate human escalation for security/identity/safeguarding, data minimization, and audit — is in `docs/edu-compliance.md`, anchored to the EDU compliance spine in `../governance/README.md`.

---

## ROI — what to measure

Following the governance model (`../governance/README.md`), ROI is measured on outcomes against a pre-deployment baseline, not on conversation volume. For Agent 08 the relevant categories are **Labor**, **Service**, and **Risk & quality**.

| Category | Example measures |
|---|---|
| **Labor** | Staff hours per ticket and per request; overtime; seasonal staffing (enrollment-season, term-start surges); policy-search time; document-development cycle time; staff-onboarding time |
| **Service** | Ticket deflection rate; first-contact resolution; mean time to resolution (MTTR); classroom downtime; approval turnaround; after-hours availability; cost per request; satisfaction |
| **Risk & quality** | Reopened-ticket rate; incomplete-request rate; procurement delays; escalation rate; override rate on gated actions; privacy/security incidents |

Concrete baseline-then-measure methodology and an illustrative before/after table are in `docs/roi-analysis.md`.

---

## Proof points

Two verified, real-world references — attributed exactly, not embellished:

- **HubbleIQ** operates an AWS-based autonomous IT-support agent that combines telemetry and generative AI to diagnose poor Wi-Fi, slow devices, and application outages, including remote student connectivity — a real-world analog for this agent's diagnostic surface.
- **Cal Poly's ScopeBuilder** uses AWS generative AI to guide staff through contract scopes, bids, RFPs, and statements of work — a real-world analog for this agent's administrative document-drafting surface.

---

Maturity: **Documented.**
