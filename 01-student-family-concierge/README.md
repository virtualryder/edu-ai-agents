# 01 — Student & Family Services Concierge
### The 24/7 governed front door to the institution — the single best first deployment

> **The fastest way to prove the platform: a low-decision-risk, high-visibility agent that deflects routine contacts, answers in any language at any hour, and — only after authentication — checks a status, schedules an appointment, opens a case, or sends a form.**

The Concierge answers the questions families and students actually ask — about enrollment, financial aid, calendars, transportation, meals, deadlines, and required documents — and, once a user proves who they are, takes a small set of low-risk actions on their behalf. It is the recommended **land** of the "land with 01, expand to the portfolio" motion because it is the most visible to the most users, the lowest-risk decision-wise, and the easiest to measure. Critically, it is also where the **MCP authorization gateway, identity wiring, audit trail, and HITL framework are built once and then inherited by Agents 02–08 for free** (see `../docs/WHY-THE-MCP-LAYER.md`).

---

## What it does

A multilingual, multi-channel assistant — Amazon Connect (voice / SMS / chat), web, and mobile — that operates in two clearly separated modes:

| Mode | What it provides | Identity required |
|---|---|---|
| **Public (read-only)** | Grounded answers about enrollment and registration, financial aid and tuition, academic and athletic calendars, transportation and bus routes, meal programs, academic policies, course schedules, technology access, student-support services, deadlines, and required documents | No |
| **Authenticated** | Check *your* application or financial-aid status, retrieve *your* schedule, schedule an advising appointment, open a support case, request a form, and escalate to a named staff member | Yes — via the institution's SSO |

Every answer is **grounded** in approved institutional content; the agent fails fast rather than inventing a deadline, a policy, or a status. Every authenticated action passes through the gateway under **deny-by-default** authorization, so the agent can never read another student's record or do more than the authenticated person is permitted to do.

---

## What it solves

Education information is scattered across websites, PDFs, departmental pages, portals, and staff inboxes; families don't know which department to contact or what institutional terms mean. Front offices, registrars, and financial-aid teams absorb the cost in repetitive calls, emails, and walk-ins — concentrated in seasonal peaks (open enrollment, the start of term, FAFSA season) when staffing is most stretched and after-hours demand is highest. The Concierge meets that demand 24/7, deflects the routine contacts that consume staff time, and — once a user authenticates — resolves the common "what's my status / I need an appointment / I need this form" requests without a human in the loop, while still routing anything consequential to a person.

---

## Where it sits in the rollout & why

**Deploy this first.** It is the **best first deployment** for four reasons the buying committee cares about:

1. **Broad visibility.** More students, families, and staff touch the Concierge than any other agent, so it produces the adoption and value signal that funds the rest of the portfolio.
2. **Low decision risk.** In public mode it only answers; in authenticated mode it performs a small set of reversible, low-stakes actions. It never touches a bright-line decision (grades, admissions, discipline, financial-aid awards, special-education eligibility, placement).
3. **Mature, measurable workflows.** Call/email deflection, first-contact resolution, and after-hours self-service are quantifiable from day one against a clean baseline.
4. **It builds the shared platform.** The gateway, identity federation, audit trail, and human-approval framework provisioned for 01 are reused by every later agent — pay the integration tax once.

The Concierge is a **best-first-deployment-tier** agent alongside the Educator Copilot (03), Operations Service Desk (08), and Document & Accessibility Services (07); the single recommended entry point is this one.

---

## AWS implementation

| Architecture role | AWS service |
|---|---|
| Conversational channels | **Amazon Connect** (voice / SMS / chat) + web/mobile front end |
| Agent runtime | **Amazon Bedrock AgentCore Runtime** (container) or **Step Functions + Lambda** (native) |
| Grounded answers | **Amazon Bedrock Knowledge Bases** over approved institutional content (OpenSearch Serverless / Aurora pgvector) |
| Inference | **Amazon Bedrock (Claude)** — reached over PrivateLink (interface VPC endpoint), not the public internet; identifiers masked before inference |
| Content safety | **Amazon Bedrock Guardrails** (PII denial, age-appropriate filters for minors) |
| Authenticated tools | **API Gateway + Lambda** behind the **AgentCore Gateway**, calling SIS/CRM connectors |
| Case creation / escalation | **AWS Step Functions** (`waitForTaskToken` where a human gate applies) |
| Identity | **AgentCore Identity + Amazon Cognito / IAM Identity Center** federating the institution's IdP |
| Multilingual | **Amazon Translate** (text), **Amazon Polly** (voice), Title VI language access |
| Audit | Append-only **DynamoDB** + **S3 Object Lock**, **CloudTrail** |

### Tools it exposes (read and write separated)

| Tool | Type | Grant scope |
|---|---|---|
| `check_application_status` | **Read** | Authenticated user's own application only |
| `get_student_schedule` | **Read** | Authenticated student's own schedule only |
| `create_advising_case` | **Write (low-risk, gated)** | Opens a case in the CRM/case system for the authenticated user |
| `schedule_appointment` | **Write (low-risk, gated)** | Books against published staff availability |
| `send_form` | **Write (low-risk, gated)** | Sends an approved form/packet to the authenticated user |
| `draft_family_message` | **Write (low-risk, gated)** | Drafts an outbound message for staff review before send |

Read and write are distinct tools with distinct grants. The agent never holds direct SIS/CRM credentials; each write tool requires the authenticated identity bound into the record and, where consequential, a named staff approval before the gateway mints a write token.

---

## Systems of record / connectors

| Category | Examples | Used for |
|---|---|---|
| **SIS** | PowerSchool, Infinite Campus, Banner, Workday Student | Application/enrollment status, schedule, financial-aid status retrieval |
| **CRM / case management** | Slate, Salesforce EDU | Advising cases, inquiry tracking |
| **Scheduling** | Institution scheduling system | Appointment booking against published availability |
| **Contact center** | **Amazon Connect** | Voice/SMS/chat channel and routing |
| **Knowledge base** | Approved institutional content (policies, catalogs, FA/enrollment guidance) | Grounded public answers |

The SIS/CRM remain the **systems of record**; the Concierge reads and initiates through gateway-authorized connectors, never direct database access.

---

## Phased adoption

1. **Public read-only answers (start here).** Stand up the Knowledge Base over approved content and ship grounded answers across web, voice, and chat in the institution's languages. No authentication, no system-of-record access — fastest path to value and the cleanest deflection baseline.
2. **Authenticated status retrieval.** Federate the IdP, add `check_application_status` and `get_student_schedule`. The agent now answers "where is *my* application / what is *my* schedule" under deny-by-default, identity-scoped authorization.
3. **Low-risk transactions only.** Enable `create_advising_case`, `schedule_appointment`, `send_form`, and `draft_family_message` — all reversible, all gated, all audited. The agent never crosses the bright line into a consequential decision.

---

## Regulations that apply

| Regulation | Why it applies here |
|---|---|
| **FERPA** | Status and schedule retrieval touch education records; identity-scoped retrieval and disclosure recordkeeping are mandatory |
| **COPPA (under-13)** | K–12 deployments serve children under 13; heightened Guardrails, data minimization, and educational-purpose-only use |
| **ADA / Section 508 / WCAG 2.2 AA** | Web, mobile, and chat surfaces are student/family-facing and must conform |
| **Title VI language access** | Multilingual answers (Translate/Polly) support meaningful access for limited-English families |
| **State student-privacy laws** | Data residency, consent, breach-notification, and vendor-contract terms parameterized per state |

Full control mapping: `docs/edu-compliance.md` and the suite spine in `../governance/README.md`.

---

## ROI — what to measure

Baseline before deployment, then measure (full model in `../offerings/COST-ROI-MODEL.md`). Relevant categories:

| Category | Example measures |
|---|---|
| **Labor** | Staff hours on routine calls/emails/walk-ins; seasonal/overtime staffing during enrollment and FAFSA peaks; staff time redirected to higher-value work |
| **Service** | Call/email deflection rate, first-contact resolution, average response time, wait time, after-hours self-service usage |
| **Student journey** | Enrollment/registration completion, document-submission completion |
| **Risk & quality** | Grounding-failure rate, escalation rate, privacy incidents, language-coverage equity |

A high contact volume with no deflection is not success; moderate volume with a large cut in status emails/calls and faster enrollment completion is.

---

## Proof points

- **University of Arkansas – Pulaski Technical College (MyAgent, Modo Labs + AWS):** reached **94.5% adoption** across students, faculty, and staff, became the **most-used app feature (21.8% of activity)**, and drove a **253% year-over-year increase** in admissions-content engagement — evidence that a well-grounded concierge becomes the front door students actually use.
- **Highline College (AWS financial-aid status self-service):** cut financial-aid **status emails, calls, and visits by 75%** and **halved FAFSA processing time** — the deflection-and-cycle-time return that makes the Concierge the cleanest ROI story in the portfolio.

---

## Maturity: **Demonstrated locally** (golden path) — not AWS-deployed

Architecture, workflow, tool grants, and compliance design are written and reviewed, and the agent **runs end-to-end locally**: in demo mode (`EXTRACT_MODE=demo`, deterministic fixtures, no API key) and over a **local-HTTP live-connector path** (`CONNECTOR_MODE=live` against a local stand-in service of record, gated at the gateway before any HTTP call). Agent 01 is the **golden path** — record-level authorization, durable single-use signed approvals, edge/observability templates, an AgentCore provisioner, and a one-command `make golden-path-01` all exist and are test/lint-verified. Still customer/engagement work: an independently-proven deploy in a clean AWS account, real-model invocation, production IdP federation, a real SIS/CRM connector, WCAG 2.2 AA conformance testing, and a penetration test. Status is governed by [`../docs/STATUS-MANIFEST.md`](../docs/STATUS-MANIFEST.md); see also the suite maturity ladder in `../README.md`.
