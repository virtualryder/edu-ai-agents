# EDU AI Agent Suite
### Governed AI Agents for Education — Built on AWS

> **The agents are not the product. The governed platform that makes them deployable, auditable, and compliant with student-privacy law is.**

A systems integrator deploying AI inside a K–12 district, a community college, a university, an online program, or a workforce-education provider cannot hand a customer a collection of LLM calls and call it done. Every record an education agent touches — a student's schedule, a financial-aid status, an IEP accommodation, a grade, a disciplinary note, a family message — is an *education record* the moment it is personally identifiable, and it carries FERPA, COPPA, PPRA, IDEA/Section 504, and state student-privacy obligations that exist before the first line of agent code is written. This suite embeds those controls from the first commit: deny-by-default authorization, student-PII masking, grounding verification against approved institutional content, prompt version pinning, a human gate that is framework-enforced (not merely documented), and a tamper-evident audit trail aligned to FERPA recordkeeping and the FERPA "school official / direct control" requirement for vendors.

The result is a deployable accelerator — not a certified product — that gives a delivery team a credible, compliant starting point across eight high-value education workflows that apply across the entire EDU spectrum: K–12 districts, charter and private schools, community colleges, universities, online programs, and adult/workforce education.

**What is deliberately out of scope:** university research administration, advancement/fundraising, and specialized laboratory agents. Those are narrower and do not generalize across institution types. This suite covers what every institution shares — student services, teaching and learning, student success, enrollment, accessibility, and operations.

---

## The problem, the cost of doing nothing, and how this solves it

Every institution is already paying for these problems — in staff time, lost tuition, replacement hiring, and accessibility-compliance exposure. The agents target the eight workflows where that bill is largest and most measurable. Figures below are grounded and cited in [`gtm/EDU-DECK-SOURCES.md`](gtm/EDU-DECK-SOURCES.md); dollar figures marked *modeled* show their arithmetic there. Outcomes are modeled to a reference institution, not guaranteed.

| Agent | The issue today | The cost of doing nothing |
|---|---|---|
| **01 · Student & Family Concierge** | Families can't self-serve; routine status/aid/deadline questions bury staff. ~4M of 5.4M FAFSA-cycle calls went unanswered *(GAO, 2024)* | **~$1.2M–$1.6M/yr** avoidable contact-handling *(modeled)* |
| **02 · Tutor & Study Companion** | No scalable, after-hours, equitable help; a purpose-built AI tutor drove **>2× learning** in an RCT *(Harvard, 2024)* | **~$1.2M–$2.5M/yr** to match with human tutoring for 1,000 students *(modeled)* |
| **03 · Educator Copilot** | Teachers work **53 vs. 44 hrs/wk** with ~4.4 hrs to plan *(RAND, 2024)* | **$11,860–$24,930** to replace one burned-out teacher (~$2.2B/yr nationally) *(LPI, 2024)* |
| **04 · Assessment & Feedback** | Instructors spend **~9.9 hrs/wk grading**; feedback lags *(2025 survey)* | **~$4,270/instructor/yr** recoverable grading labor *(modeled)* |
| **05 · Student Success** | Warning signs accrue before anyone acts; **22.4% of first-years don't return** *(NSC, 2025)* | **~$5.6M/yr** forgone recurring tuition *(modeled)* |
| **06 · Pathway Navigator** | Transfers lose **~43% of credits** on average *(GAO / CHEPP)* | **$13,081 (public) / $26,396 (private)** added cost per transfer student *(CHEPP, 2024)* |
| **07 · Document & Accessibility** | Document-heavy intake + **ADA Title II (WCAG 2.1 AA) due Apr 26 2027/2028**; ~95% of complaints are PDFs | Settlements ~$30k · judgments ~$85k · class actions ~$400k · program-scale remediation **$665k–$815k** + federal-funding risk |
| **08 · Operations / IT Service Desk** | Password/access tickets are **20–50% of help-desk volume**, ~$70/reset | **~$300K/yr** deflectable-ticket cost *(modeled)* |

**How the suite solves it.** Each agent follows the same governed pipeline: it **retrieves** only approved institutional content and the acting user's own records through a deny-by-default authorization gateway, **analyzes** the request, **drafts or recommends** an action, **stops at a framework-enforced human gate** for anything consequential, and **writes a tamper-evident audit record** of every access. The agent deflects routine load, answers any hour in any language, and assembles the evidence — while a named human keeps every grade, enrollment change, eligibility decision, financial commitment, and privileged action. The return is the deflected volume, reclaimed staff hours, retained tuition, and a closed accessibility-compliance gap above, captured without surrendering control of a single regulated decision.

### Regulatory alignment (the controls that let a CISO and privacy officer say yes)

The student-privacy and accessibility obligations exist *before* the first line of agent code. They are mapped to concrete platform/AWS controls in [`governance/controls/control_mappings.py`](governance/controls/control_mappings.py) and detailed in [`governance/README.md`](governance/README.md):

| Regime | What it requires | How the platform aligns |
|---|---|---|
| **FERPA** | Protect PII in education records; vendor acts under "school official / direct control" | Deny-by-default gateway (agent-grant ∩ user-entitlement), security-trimmed retrieval, student-PII masking at the audit boundary, tamper-evident access log |
| **COPPA** | Heightened protection + parental consent for under-13 | Minor-aware masking, guardian-role entitlements, consent gating before family outreach |
| **IDEA / Section 504** | Protect IEP/504 records; humans own eligibility & placement | Least-privilege access, masking, bright-line HITL gate on every consequential decision |
| **ADA Title II / 508 / WCAG 2.1 AA** | Accessible AI output (deadlines 2027/2028) | Deterministic WCAG pre-flight on generated content; accessible-format transformation (Agent 07) |
| **GLBA** | Safeguard student financial-aid data | KMS CMK encryption, least privilege, financial-identifier masking |
| **Title VI / OCR** | No unjustified disparate impact | Four-fifths disparate-impact + representativeness screens on any flag/rank workflow; human equity review |
| **NIST AI RMF 1.0** | Govern / Map / Measure / Manage AI risk | Grounding verification, hash-pinned prompt registry, evals, red-team, fairness screens, enforced HITL |

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
| **Fairness checks** | Equity/representativeness flags on student-success recommendations and intervention targeting, plus the **four-fifths disparate-impact screen** (`governance/fairness/disparate_impact.py`) for any at-risk flag/rank workflow (Title VI / OCR exposure), with false-positive/false-negative monitoring |
| **Accessibility pre-flight** | Deterministic WCAG 2.1 AA checks on AI-generated content (alt text, heading order, link purpose, plain-language grade) — ADA Title II puts AI output in scope (deadlines Apr 26 2027 / 2028); `governance/accessibility/wcag.py` |
| **Consequential bright-line** | A test asserts every irreversible system-of-record commit is human-gated and **no agent can execute one without approval** — defense-in-depth, enforced in `governance/tests/test_consequential_bright_line.py` |
| **Control mappings** | `governance/controls/control_mappings.py` ties each obligation (FERPA, COPPA, IDEA/504, ADA Title II, GLBA, Title VI, NIST AI RMF, PCI) to the concrete platform/AWS control and its maturity |

---

## How to pitch this suite

**The one-line frame.** "The agents are not the product — the governed platform that makes them FERPA/ADA-defensible, auditable, and deployable on AWS is. We start where the decision-risk is low and the visible return is high, prove the gateway/audit/human-gate in production, then expand."

**Lead with the cost of doing nothing, not the technology.** Open on the institution's own version of the cost table above — unanswered contacts, grading hours, non-returning students, accessibility deadlines. The buyer feels the bill before they hear the word "agent."

**Tailor the value to the person in the room:**

- **CFO / VP Finance** — reclaimed staff hours, deflected contacts/tickets, retained tuition, and avoided accessibility-litigation exposure. Anchor on the *cost of doing nothing* figure and the modeled payback (typically 4–9 months at a reference institution).
- **CIO / Director of Infrastructure** — AWS-native, per-customer VPC isolation, deploys with the runbooks in this repo, no model lock-in (LLM factory abstracts Bedrock). Hand them `decks/EDU-CIO-Adoption-Review.pptx` — it states the shortfalls and the responsibility split honestly, which builds more trust than a flawless pitch.
- **CISO / Privacy Officer** — deny-by-default authorization, student-PII masking, framework-enforced HITL on consequential actions, tamper-evident audit, and the regulatory-alignment table above. The controls exist in code with passing tests, not as promises.
- **Provost / Academic leadership** — the bright line: the agent never decides a grade, admission, discipline, financial aid, special-education eligibility, or placement. It augments educators and advisors; humans stay accountable.

**Sequence the portfolio.** Land with the low-decision-risk, high-visibility agents (**01 Concierge, 03 Educator Copilot, 07 Document & Accessibility, 08 Service Desk**), then expand to the higher-governance agents (**04 Assessment, 05 Student Success, 06 Pathway**) once the platform is proven. Use `decks/EDU-Agentic-AI-Suite-Executive-Overview.pptx` for the portfolio story and the per-agent decks in `decks/` for the deep dive. Field collateral: `gtm/BATTLECARD.md`, `gtm/SOW-TEMPLATE.md`, `gtm/roi-calculator/`, and `SOLUTION-FIELD-GUIDE.md`.

## Qualifying questions to stage an engagement

Use these in discovery to scope the pilot, size the ROI, and surface the work that belongs to the customer (see `docs/SHARED-RESPONSIBILITY-MATRIX.md`):

- **Pain & baseline** — Which of the eight workflows hurts most right now? What's your current volume (contacts, tickets, applications, at-risk students) and what does a unit cost you today? *(This becomes the cost-of-doing-nothing number on the proposal.)*
- **Systems of record** — What are your SIS, LMS, ERP, and ITSM platforms, and can we reach them over PrivateLink/Direct Connect? Are there APIs, or is integration custom?
- **Identity** — What IdP do you run (Okta, Azure AD, Google)? SAML or OIDC? Is MFA enforced? How do roles (student, guardian, educator, counselor, registrar, staff) map to IdP groups?
- **AWS & data residency** — Do you have an AWS account/landing zone? Is Amazon Bedrock model access enabled in-region? Any data-residency or in-state requirements?
- **Compliance posture** — Who owns the FERPA "school official" determination and the DPA? Where are you on the ADA Title II (WCAG 2.1 AA) deadline? Do you need a disparate-impact review for any at-risk flagging?
- **Human-in-the-loop** — Who are the named approvers for each consequential action, and do they have a review queue/UI today or do we build one?
- **Knowledge content** — Is there an approved, current corpus (policies, catalog, rubrics, runbooks) to ground retrieval, or does it need curation first?
- **Success metrics & timeline** — What outcome would make this a win (deflection %, hours saved, retention points, turnaround), and what's the decision/pilot timeline?

---

## AWS Deployment

### Full step-by-step runbooks (anyone can follow them)
- **`docs/AWS-DEPLOYMENT-REFERENCE.md`** — the master, shared, step-by-step path every agent uses, in deploy order: prerequisites → KMS CMK → VPC/endpoints → Cognito + IdP federation + JWT → CloudFront + WAF → JWT exchange/authorization → application tier (AgentCore Runtime or Step Functions native) → tools/connectors + secrets → S3 Object Lock (WORM) + append-only DynamoDB audit → observability → HITL gate → validation/smoke → teardown. Includes a request-flow walkthrough, an architecture diagram, and a layer→template map.
- **`runbooks/agent-deploy/<NN>-*.md`** — one runbook per agent (agent creation, its exact tool grants and connectors, agent-specific infra, smoke test, teardown), building on the master reference.
- **`docs/AWS-DEPLOYMENT-VALIDATION.md`** — the automated checks behind "validated to be deployable on AWS" (governance + gateway tests, CloudFormation parse, container contract, WORM/CMK presence).

### Deploy it yourself — three commands (container path)
The `scripts/` directory builds and deploys an agent; `docs/DEPLOYMENT-HANDBOOK.md` is the full
empty-account→running-agent runbook (prerequisites, Bedrock model access, Guardrail, IdP, validation
checklist).

```bash
scripts/local_smoke.sh 01-student-family-concierge            # prove the runtime locally (no cloud)
IMAGE=$(scripts/build_and_push_image.sh --agent 01-student-family-concierge --region us-east-1 \
        | sed -n 's/^ContainerImageUri=//p')                  # build ARM64 image -> ECR
scripts/deploy.sh --env prod --agent-id 01-concierge --mode container \
  --template-bucket my-cfn-bucket --idp-metadata https://idp/.../metadata --image "$IMAGE"
```

- **Turnkey POC demo** (a running URL, no IdP/SoR wiring): `infra/cloudformation/demo-in-a-box.yaml` (ECS Fargate + ALB).
- **Native path** (Step Functions + Lambda + `waitForTaskToken` HITL gate): `scripts/package_lambdas.sh` then `scripts/deploy.sh --mode native`.
- **Author a NEW agent** (it inherits this whole deployment path): `docs/CREATE-A-NEW-AGENT.md`.
- **Scripts reference**: `scripts/README.md`. **AWS prerequisites & funding**: `docs/AWS-FUNDING-AND-PREREQUISITES.md`.

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
├── scripts/                             # build_and_push_image · package_lambdas · deploy · local_smoke (+ README)
├── governance/                          # EDU compliance spine + grounding, evals, HITL tests, red team, fairness
│   ├── accessibility/                   # WCAG 2.1 AA / ADA Title II pre-flight on AI-generated content
│   ├── fairness/                        # representativeness + four-fifths disparate-impact screen
│   ├── controls/                        # obligation → platform/AWS control mappings (FERPA/COPPA/IDEA/ADA/...)
│   └── evals/                           # structural golden-artifact regression (no API key)
├── aws-native-reference/                # AWS-native deployment (container + native) for all 8 agents
├── runbooks/
│   └── agent-deploy/                    # Step-by-step per-agent AWS deploy runbooks (8) + ops runbooks
├── decks/                               # GTM: 8 agent decks + suite overview + CIO adoption review (.pptx)
├── gtm/                                 # BATTLECARD · SOW · ROI calculator · EDU-DECK-SOURCES · DECK-CONTENT-SPEC
├── infra/
│   ├── cloudformation/                  # CloudFormation quick-deploy (primary path)
│   └── terraform/                       # Terraform parity
├── docs/
│   ├── AWS-DEPLOYMENT-REFERENCE.md       # Master step-by-step shared deploy path (edge→identity→app→data)
│   ├── AWS-DEPLOYMENT-VALIDATION.md      # Automated "deployable on AWS" validation report
│   ├── DEPLOYMENT-HANDBOOK.md            # Console + CLI step-by-step deploy
│   ├── SHARED-RESPONSIBILITY-MATRIX.md   # Who owns what: user / customer / developer-SI
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
