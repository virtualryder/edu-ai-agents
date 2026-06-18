# EDU AI Agent Suite
### Governed AI Agents for Education — Built on AWS

> **The agents are not the product. The governed platform that makes them deployable, auditable, and compliant with student-privacy law is.**

A systems integrator deploying AI inside a K–12 district, a community college, a university, an online program, or a workforce-education provider cannot hand a customer a collection of LLM calls and call it done. Every record an education agent touches — a student's schedule, a financial-aid status, an IEP accommodation, a grade, a disciplinary note, a family message — is an *education record* the moment it is personally identifiable, and it carries FERPA, COPPA, PPRA, IDEA/Section 504, and state student-privacy obligations that exist before the first line of agent code is written. This suite embeds those controls from the first commit: deny-by-default authorization, student-PII masking, grounding verification against approved institutional content, prompt version pinning, a human gate that is framework-enforced (not merely documented), and a tamper-evident audit trail aligned to FERPA recordkeeping and the FERPA "school official / direct control" requirement for vendors.

The result is a deployable accelerator — not a certified product — that gives a delivery team a credible, compliant starting point across eight high-value education workflows that apply across the entire EDU spectrum: K–12 districts, charter and private schools, community colleges, universities, online programs, and adult/workforce education.

**What is deliberately out of scope:** university research administration, advancement/fundraising, and specialized laboratory agents. Those are narrower and do not generalize across institution types. This suite covers what every institution shares — student services, teaching and learning, student success, enrollment, accessibility, and operations.

---

## Positioning

| What this is | What this is not |
|---|---|
| A governed, auditable accelerator — the controls a CISO, privacy officer, and academic leadership need to say yes | A certified, validated, production-ready SaaS product you can hand to a customer unchanged |
| Eight agents with shared platform controls that compound across the portfolio | Eight point tools built independently with no governance consistency |
| A reference for Amazon Bedrock AgentCore Gateway + Identity + Runtime semantics — testable locally, deployable on AWS | A vendor lock-in — the gateway semantics are replicated in `platform_core/` so the logic is readable and testable without an AWS account |
| Decision-support — retrieves, analyzes, drafts, recommends, initiates low-risk workflows, escalates exceptions — with humans owning every consequential decision | An autonomous administrator or teacher that decides grades, admissions, discipline, financial aid, special-education eligibility, or placement |

### The bright line: what these agents never decide

Production education agents in 2026 are **bounded agents**. They retrieve approved institutional information, analyze student or operational data, create drafts and recommendations, call approved APIs, initiate low-risk workflows, and escalate exceptions to a human. They do **not** independently make final decisions about **grades, admissions, discipline, financial aid, special-education eligibility, or student placement**. Every consequential action is gated to a named, authorized human whose identity is bound into the record.

---

## Maturity Ladder

Every agent and platform component is positioned honestly against four levels:

| Level | Description | What it means |
|---|---|---|
| **Documented** | Architecture, workflow, and compliance design are written and reviewed | Useful for customer discovery and architecture review; not runnable |
| **Demonstrated** | Code runs end-to-end in `EXTRACT_MODE=demo` (no API key, deterministic fixtures) | Proof of concept; suitable for internal demos and early customer workshops |
| **Deployable** | CloudFormation templates, container contracts (ARM64, `/invocations`, `/ping`), and CI pass; requires customer AWS account and Bedrock access | Suitable for a customer pilot with SI-managed infrastructure |
| **Production-ready** | Customer security & privacy review complete, IdP integrated, connectors tested against live SIS/LMS/ERP/ITSM, accessibility (WCAG 2.2 AA) conformance tested, penetration test passed | Engagement milestone, not a day-one deliverable |

**Current repository status:** foundation and positioning layer in active build. The platform architecture, the MCP authorization gateway design, the EDU compliance spine, the six-layer reference architecture, and the field/GTM collateral are being built first; the eight agents are written to **Documented** depth and brought to **Demonstrated/Deployable** in subsequent passes (mirroring the HCLS suite delivery model).

---

## The Eight Agents

Twelve broadly applicable production use cases, consolidated into eight flagship agents that share one platform.

| # | Agent | Problem it solves | Primary systems | Key regulations |
|---|---|---|---|---|
| **01** | **Student & Family Services Concierge** | Education information is scattered across websites, PDFs, departmental pages, portals, and staff inboxes; families don't know which department to contact or what institutional terms mean. After authentication the agent checks status, schedules appointments, opens cases, sends forms, and escalates. | SIS, CRM, scheduling, contact center (Amazon Connect) | FERPA, COPPA, state student-privacy, ADA/Section 508, Title VI language access |
| **02** | **Personalized Tutor & Study Companion** | Students need help outside class hours at a scale human tutoring cannot meet; generic public AI lacks course context and institutional safeguards. Curriculum-grounded, instructor-controlled Socratic support. | LMS, course content store, knowledge base | FERPA, COPPA (under-13), IDEA/504 accommodations, academic-integrity policy |
| **03** | **Educator Copilot — Instruction, Differentiation & LMS Workflow** | Educators spend disproportionate time adapting content for different levels, languages, and needs, and navigating complex LMS screens. Drafts lessons, differentiates, builds rubrics/quizzes, and executes scoped LMS actions — always educator-approved before publish. | LMS, curriculum/standards store, SIS (roster) | FERPA, ADA/508/WCAG, state content standards, ED 2025 AI guidance |
| **04** | **Assessment, Grading & Feedback** | Open-ended grading and detailed feedback are valuable but time-consuming; delayed feedback loses instructional value. Rubric-grounded draft evaluation, misconception detection, low-confidence routing — educator owns final grades. | LMS/assessment store, rubric service | FERPA, IDEA/504, accreditation/grading-integrity policy |
| **05** | **Student Success & Proactive Engagement** | Warning signs (attendance, missing work, disengagement) accumulate before anyone acts; staff lack capacity for timely, personalized outreach. Assembles evidence, drafts interventions, opens cases, and runs approved event-driven outreach. | SIS, LMS, attendance, advising/case mgmt, comms (Connect/SES/SNS) | FERPA, PPRA, state student-privacy, equity/anti-discrimination, opt-out/consent |
| **06** | **Academic, College & Career Pathway Navigator** | Advisors carry large caseloads; degree/graduation/transfer rules are complex. Course planning, graduation requirements, transfer-credit mapping, CTE and credential pathways, career exploration, and scheduling — augments the counselor. | SIS, degree-audit/rules engine, labor-market data | FERPA, accreditation, transfer-articulation policy |
| **07** | **Document & Accessibility Services** | Enrollment is document-heavy and seasonal; institutions must serve students and families across languages, disabilities, and reading levels. Classifies/extracts/validates enrollment documents **and** transforms approved content into accessible, multilingual formats. | SIS/CRM, document store, Textract/Transcribe/Translate/Polly | FERPA, COPPA, ADA/Section 504/508, WCAG 2.2 AA, immunization/residency record rules, records retention |
| **08** | **Operations Service Desk** | Education IT and administrative staff support large, distributed populations with limited staffing; many tickets and policy questions are repetitive. IT support + internal staff knowledge and administrative workflow (HR, procurement, finance, facilities). | ITSM (ServiceNow/Jira), HR/ERP, procurement, knowledge base | FERPA (staff handling student data), records management, procurement policy, segregation of duties |

**Why this sequencing:** Agents 01, 03, 08, and 07 are the **best first deployments** — broad visibility, comparatively low decision-risk, mature workflows, and measurable deflection/cycle-time return. Agents 02, 04, 05, and 06 are **high-value, higher-governance** — they touch learning and student outcomes directly, so they require stronger evaluation, educator oversight, bias testing, evidence retention, and escalation. The single-best entry point is **Agent 01 (Concierge)**: it is the most visible to the most users, the lowest-risk, and the easiest to measure. See `SOLUTION-FIELD-GUIDE.md` for the full adoption path and the "land with 01, expand to the portfolio" motion.

---

## Shared Platform

Every agent shares the same platform stack. Controls compound: a governance improvement to the student-PII masker, the grounding checker, or the audit trail benefits all eight agents simultaneously.

### LLM Factory
A single abstraction routes inference to **Anthropic Claude** (API) or **Amazon Bedrock** (in-account, no data leaves the customer VPC) depending on deployment mode. `EXTRACT_MODE=demo` bypasses the LLM entirely for local, deterministic testing.

### Student-PII Masking
Structured entity recognition replaces student identifiers, dates of birth, guardian details, and record-linkable fields with stable pseudonyms before any content enters a prompt or an audit record. The masker is stateless and runs before every gateway invocation. This is the EDU analog of HIPAA Safe-Harbor masking, tuned to FERPA-protected identifiers and COPPA's heightened bar for children under 13.

### MCP Authorization Gateway
The governed front door between every agent and every system of record. **No agent calls a vendor system (SIS, LMS, ERP, CRM, ITSM) directly.** Every tool call passes through one enforcement point implementing:

1. **Identity verification** — verified IdP claims (the institution's own SSO via IAM Identity Center / Cognito); deny on missing subject.
2. **Deny-by-default authorization with least-privilege intersection** — `permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[agent] ∩ ROLE_ENTITLEMENTS[user_roles]`, where roles are distinct for **student, guardian, educator, counselor, and administrator**. An agent can never do more than the human on whose behalf it acts — and a guardian's access is scoped by the FERPA rights that transfer to the student at 18 / postsecondary enrollment.
3. **Human approval gate** — high-risk (write/irreversible/consequential) tools block until a verified reviewer identity is bound into the record.
4. **Short-lived scoped tokens** — minted per call via AgentCore Identity / STS; no standing service accounts.
5. **PII-masked append-only audit** — every attempt (ALLOW/DENY/PENDING_APPROVAL/ERROR) logged with lineage to the system of record, satisfying FERPA's recordkeeping of disclosures.

Reference logic: `platform_core/edu_agent_platform/mcp_gateway/` — a testable Python model of **Amazon Bedrock AgentCore Gateway + AgentCore Identity**. Tool names (`connector_kind.operation`) map 1:1 to AgentCore Gateway targets. See `infra/cloudformation/agentcore-gateway.yaml` for deployable registration.

**You have options for how to build this layer.** `docs/WHY-THE-MCP-LAYER.md` is the plain-English explainer (with a talk track and objection handling) for *why* agents that act on systems need a governed access layer and why to fund it in Phase 1 — and it compares the three implementation paths: **AgentCore Gateway** (managed), **Bedrock-native API Gateway + Lambda** (assembled from AWS primitives), and **FastMCP** (a self-built MCP server when the institution wants to own the code). The point that matters is the same in all three: clean, governed API access for agents to the data itself.

### Connector Framework
Adapter layer for each system category (SIS, LMS, ERP/SIS-finance, CRM, ITSM, scheduling, transportation, library, RWD/labor-market). Demo mode uses deterministic JSON fixtures; production connectors point at live PowerSchool, Banner/Workday, Canvas/Blackboard/Schoology, ServiceNow, and similar APIs. The connector interface is identical in both modes — the gateway does not know which backend is live.

### Governance & Evaluation Framework
Built in from the first commit, not added after a pilot. See `governance/README.md` for the full EDU compliance spine (FERPA, COPPA, PPRA, IDEA/Section 504, ADA/508/WCAG 2.2 AA, state student-privacy law) and these controls:

| Control | Implementation |
|---|---|
| **Grounding verification** | Every fact or figure in a student- or family-facing artifact is traceable to approved institutional content; grounding fails fast rather than producing a hallucinated policy, deadline, or status |
| **Prompt version registry** | Prompts are registered and hash-pinned in `governance/prompt_manifest.json`; CI fails on un-bumped drift (model-change control) |
| **Structural eval harness** | Golden-artifact regression for advising plans, intervention drafts, rubric-graded feedback, and accessible-content output; runs in CI with no API keys |
| **HITL gate tests** | Framework-enforced human approval is tested, not merely documented — `governance/tests/test_hitl_gates.py` |
| **Red team** | Prompt injection (incl. injection hidden in a student-submitted document or inbound email), PII exfiltration, and authorization-bypass scenarios — `governance/redteam/` |
| **Fairness checks** | Equity/representativeness flags on student-success recommendations and intervention targeting, with false-positive/false-negative monitoring |

---

## AWS Deployment

### CloudFormation Quick Deploy (primary path)
One master template provisions a customer-isolated environment:

```
infra/cloudformation/
├── quickstart.yaml          # Master — nests all stacks
├── network.yaml             # VPC, subnets, NAT, security groups
├── security.yaml            # KMS, Bedrock Guardrail, Cognito/IAM Identity Center federation, agent IAM role
├── data.yaml                # Append-only DynamoDB audit, S3 Object Lock WORM, HITL table, governed data-lake refs
├── agentcore-gateway.yaml   # Bedrock AgentCore Gateway + Identity — one target per SoR
└── agent-service.yaml       # Per-agent Step Functions + Lambdas (native) or AgentCore Runtime (container)
```

### Terraform Parity
`infra/terraform/` provides equivalent IaC for platform teams standardized on Terraform — identical resource topology, different surface syntax.

### AgentCore Runtime (container lift) and Strands + Step Functions (native rebuild)
All agents target the AgentCore container contract (`/invocations`, `/ping`, port 8080, ARM64). The native rebuild runs deterministic core functions as Lambda, Strands Agents SDK for Bedrock inference, and Step Functions for orchestration with a `waitForTaskToken` HITL gate. See `aws-native-reference/` and the step-by-step `docs/DEPLOYMENT-HANDBOOK.md` (empty AWS account → running, governed, human-gated agent).

---

## Repository Structure

```
edu-ai-agents/
├── README.md                            # This file
├── SUITE-STATUS.md                      # Current state + changelog
├── SOLUTION-FIELD-GUIDE.md              # SI sales + SA qualification and adoption path
├── ENTERPRISE-PLATFORM.md               # Platform story — API modernization, MCP gateway, compliance layers
│
├── 01-student-family-concierge/         # Best-first deployment (land here)
├── 02-tutor-study-companion/
├── 03-educator-copilot/
├── 04-assessment-grading-feedback/
├── 05-student-success-engagement/
├── 06-pathway-navigator/
├── 07-document-accessibility-services/
├── 08-operations-service-desk/
│   (each: README.md + docs/{aws-deployment-guide, integration-guide, edu-compliance, roi-analysis}.md)
│
├── platform_core/                       # Shared platform — LLM factory, student-PII masker, MCP gateway, connectors
│   └── edu_agent_platform/
│       ├── mcp_gateway/                 # Reference logic for Bedrock AgentCore Gateway + Identity
│       ├── pii_masker/                  # FERPA/COPPA student-PII masking
│       └── connectors/                  # SIS · LMS · ERP · CRM · ITSM · scheduling (fixture + live)
│
├── governance/                          # EDU compliance spine + grounding, evals, HITL tests, red team, fairness
├── aws-native-reference/                # AWS-native deployment (container + native) for all 8 agents
├── infra/
│   ├── cloudformation/                  # CloudFormation quick-deploy (primary path)
│   └── terraform/                       # Terraform parity
├── docs/
│   ├── DEPLOYMENT-HANDBOOK.md            # Console + CLI step-by-step deploy
│   ├── WHY-THE-MCP-LAYER.md              # Account-team explainer + gateway implementation options
│   ├── SUITE-ARCHITECTURE.md             # 6-layer reference architecture + AWS service mapping
│   └── STAKEHOLDER-SECURITY-BRIEFINGS.md # Per-stakeholder security pitch
└── offerings/                           # POC · pilot · assessment · managed service · ROI · objections · competitive · TPRM
```

---

## Compliance Disclaimer

This suite is a **decision-support accelerator** for qualified education professionals. It is not a validated student-information system, a certified accessibility product, or an autonomous decision-maker. AI-generated content requires human review and approval by a qualified professional before any consequential action — issuing a grade, making an admissions or financial-aid determination, deciding discipline, determining special-education eligibility, or placing a student. The AI never takes irreversible or consequential actions autonomously.

Customers are responsible for: their FERPA/COPPA/PPRA compliance posture and data-governance program; IdP integration and role mapping (including guardian-relationship and age-of-majority rules); connector validation against live SIS/LMS/ERP/ITSM systems; Bedrock Guardrail configuration appropriate to their student population (including minors); WCAG 2.2 AA conformance testing of any student-facing surface; state student-privacy-law obligations; and records-retention and change-control procedures for prompt and model updates.

This accelerator provides the control design. The customer operationalizes, validates, and accepts accountability for it.
