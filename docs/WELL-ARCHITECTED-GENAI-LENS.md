# Well-Architected + Generative AI Lens Review Mapping
### EDU AI Agent Suite — AWS SA WAFR Preparation Guide

> This document maps the EDU AI Agent Suite against the AWS Well-Architected Framework (all six pillars) and the AWS Generative AI Lens. Use it to prepare for or conduct a WAFR session with a customer. Every question maps to a specific platform component — this is not a generic checklist but a suite-specific evidence guide.

---

## Why WAFR Matters for EDU AI Programs

A Well-Architected Framework Review is not optional for serious AWS education AI programs:

1. **AWS investment programs require it.** Partner Originated Activation (PoA) credits, MAP funding, and the ISV Accelerate program all expect — or require — WAFR evidence. An SA who shows up with a pre-mapped WAFR has already done the customer's procurement and funding work.
2. **CISOs and procurement teams use it as a vendor checklist.** Education institutions, especially those with existing AWS relationships, treat WAFR language as the shared vocabulary for security and architecture review.
3. **It surfaces real gaps before they become incidents.** The EDU context adds FERPA, COPPA, IDEA, and WCAG obligations that a generic WAFR misses — this mapping builds those into the review.
4. **The GenAI Lens is now standard for Bedrock workloads.** AWS SAs conducting reviews on Bedrock-based workloads are expected to apply the GenAI Lens; this mapping covers both simultaneously.

---

## Pillar 1 — Operational Excellence

### Key questions for EDU AI agents

- How do you know when an agent produces a degraded, incorrect, or unsafe output?
- How are prompt changes and model version changes controlled and communicated?
- How do you run and review operations — who is on-call, what does a shift look like?
- How do you improve the workload over time based on outcomes data?

### How the suite addresses this

| Design principle | Platform component | Evidence |
|---|---|---|
| Perform operations as code | CloudFormation templates in `infra/cloudformation/`; Terraform in `infra/terraform/`; `Makefile` build targets | All infrastructure changes go through IaC; no manual console changes |
| Make frequent, small, reversible changes | Hash-pinned prompts in `governance/prompt_manifest.json`; CI fails on un-bumped drift | Every prompt change is versioned, reviewed, and rollback-able |
| Refine operations procedures frequently | Monthly ops report in Managed Service (availability, HITL health, eval results, fairness, incidents) | Managed service SLA cadences in `offerings/MANAGED-SERVICE-OFFERING.md` |
| Anticipate failure | Runbooks for every failure mode in `runbooks/`; DR runbook in `runbooks/DR-RUNBOOK.md`; model-degradation response in `runbooks/MODEL-DEGRADATION-RESPONSE.md` | Four production runbooks covering DR, HITL queue, incident response, and model degradation |
| Learn from all operational failures | Root-cause analysis step in incident-response runbook; post-incident change required | `runbooks/INCIDENT-RESPONSE.md` §4 |

### Known gaps / customer deployment recommendations

- **Observability baseline:** CloudTrail must be enabled org-wide before deployment; CloudWatch log retention must be set (recommend 365 days minimum for EDU FERPA compliance). Confirm with `docs/AWS-FUNDING-AND-PREREQUISITES.md` §B checklist.
- **Runbook ownership:** Runbooks exist but must be adapted to the customer's operational model (who is their Tier-2 on-call; how does the SI handoff work). Cover this in the managed service kickoff.
- **Eval cadence:** Weekly eval regression is defined; the customer must designate a reviewer who signs off on every Bedrock model-version promotion.

---

## Pillar 2 — Security

### Key questions for EDU AI agents

- Who can access which student records, and how is that enforced — not just documented?
- How are credentials managed for the agents' access to systems of record?
- How is student PII protected in transit, at rest, and within the AI inference pipeline?
- How do you detect and respond to unauthorized access or a data exposure?

### How the suite addresses this

| Design principle | Platform component | Evidence |
|---|---|---|
| Implement a strong identity foundation | MCP authorization gateway with deny-by-default; verified IdP claims; no standing service accounts; short-lived scoped tokens via AgentCore Identity / STS | `platform_core/edu_agent_platform/mcp_gateway/gateway.py`, `tokens.py` |
| Enable traceability | PII-masked append-only audit trail; every ALLOW/DENY/PENDING_APPROVAL/ERROR logged with lineage | `platform_core/edu_agent_platform/mcp_gateway/audit.py` |
| Apply security at all layers | PII masker runs before model; gateway enforces authorization before tool execution; Bedrock Guardrails on model outputs; S3 Object Lock on WORM audit storage | `platform_core/edu_agent_platform/pii_masker/`, `governance/` |
| Automate security best practices | IAM roles with least-privilege policies in all CloudFormation templates; permission boundaries; no wildcard resource ARNs on student-data paths | `infra/cloudformation/security.yaml` |
| Protect data in transit and at rest | All AWS API calls over TLS; KMS encryption for DynamoDB (audit table), S3 (document/audit buckets), Secrets Manager (API keys); S3 Object Lock COMPLIANCE mode for WORM audit | `infra/cloudformation/data.yaml` |
| Keep people away from data | PII masker prevents human-readable identifiers from entering logs; gateway prevents direct SIS access from agent code; all SIS access channeled through validated connectors | `platform_core/edu_agent_platform/connectors/` |
| Prepare for security events | Incident-response runbook with detection, containment, investigation, notification, and post-incident steps aligned to FERPA breach-notification obligations | `runbooks/INCIDENT-RESPONSE.md` |

### Known gaps / customer deployment recommendations

- **Bedrock VPC endpoint:** For institutions with strict data-residency or network segmentation requirements, deploy a VPC endpoint for Bedrock (com.amazonaws.region.bedrock-runtime) so inference traffic never traverses the public internet. Not in the default QuickStart template; must be added.
- **Penetration test:** The SI provides the security evidence package; the institution's security team or a contracted third party should run a penetration test before production rollout. The TPRM packet (`offerings/TPRM-DUE-DILIGENCE-PACKET.md`) documents the architecture for the pen tester.
- **SCP guardrails:** In AWS Organizations, apply SCPs to prevent Bedrock model access outside approved regions and to prevent deletion of the audit DynamoDB table or S3 Object Lock buckets.
- **Secrets rotation:** The demo uses a static Secrets Manager secret for the API key. Production should configure automatic rotation.

---

## Pillar 3 — Reliability

### Key questions for EDU AI agents

- What happens if Bedrock is unavailable? If AgentCore is unavailable? If a SIS API times out?
- How do you recover from a failed HITL approval — is a consequential action silently dropped?
- What are the RTO/RPO targets, and are they appropriate for the institution's needs?
- How does the system handle high-volume enrollment and FAFSA peak seasons?

### How the suite addresses this

| Design principle | Platform component | Evidence |
|---|---|---|
| Automatically recover from failure | Dead-letter queues on Step Functions HITL waitForTaskToken; Lambda retry policies on connector calls; circuit-breaker pattern in connector base class | `platform_core/edu_agent_platform/connectors/base.py` |
| Test recovery procedures | DR runbook with defined RTO/RPO targets and recovery steps | `runbooks/DR-RUNBOOK.md` |
| Scale horizontally | ECS Fargate (horizontal scaling on agent containers); DynamoDB on-demand capacity (auto-scales for peak enrollment); API Gateway managed scaling | `infra/cloudformation/agent-service.yaml` |
| Stop guessing capacity | On-demand DynamoDB; Fargate (no pre-provisioned EC2); Bedrock managed capacity (on-demand inference unless provisioned throughput justified by volume) | Default template uses on-demand throughout |
| Manage change in automation | All infrastructure changes via CloudFormation change sets; no manual modifications | IaC-only policy in `Makefile` |

### Known gaps / customer deployment recommendations

- **Bedrock service quotas:** Bedrock default quotas (tokens/min, requests/min) can be a reliability risk during enrollment peaks. Increase before peak season — see `docs/AWS-FUNDING-AND-PREREQUISITES.md` for the quota-increase checklist.
- **Multi-AZ:** The default QuickStart deploys to two AZs. For production, confirm the customer's RTO/RPO tolerance and whether a third AZ or cross-region DR is warranted. K–12 districts may tolerate lower availability; universities with 24/7 student services expectations may not.
- **Connector timeout handling:** SIS APIs (Banner, PowerSchool) can have variable latency and maintenance windows. The connector base class handles retries but the customer must document maintenance window expectations in the managed service SLA.

---

## Pillar 4 — Performance Efficiency

### Key questions for EDU AI agents

- Which model is the right fit for each task — Claude 3.5 Sonnet for complex reasoning, Claude 3 Haiku for high-volume simple queries?
- Is the Knowledge Base (vector store) sized and indexed appropriately for the institution's content volume?
- What are the expected latency targets for student-facing interactions?

### How the suite addresses this

| Design principle | Platform component | Evidence |
|---|---|---|
| Democratize advanced technologies | Amazon Bedrock managed inference (no GPU provisioning); Bedrock Knowledge Bases managed vector store (no Opensearch cluster management) | Managed inference and KB in all agent configurations |
| Go global in minutes | CloudFormation parameterized by region; Bedrock available in us-east-1 and us-west-2 (and expanding); see region checklist | `docs/AWS-FUNDING-AND-PREREQUISITES.md` §B |
| Use serverless architectures | Lambda for gateway enforcement points (Options B/C); Fargate for agent containers; DynamoDB serverless; API Gateway | Default QuickStart |
| Experiment more often | `EXTRACT_MODE=demo` allows testing new agent behaviors against fixtures with zero AWS cost | Demo mode in all agents |
| Consider mechanical sympathy | Haiku for classification and simple retrieval; Sonnet for complex multi-step reasoning and grading; model selection is configurable per agent | `platform_core/edu_agent_platform/llm_factory.py` |

### Known gaps / customer deployment recommendations

- **Knowledge Base refresh latency:** Bedrock Knowledge Bases sync on a schedule. For institutions with rapidly changing policy content (FAFSA deadlines, enrollment dates), confirm the sync cadence meets the institution's accuracy requirements.
- **Cold start on Lambda-hosted gateway:** If the gateway is deployed as Lambda (Option B), the first call after inactivity has a cold-start penalty. For student-facing production use, configure Lambda provisioned concurrency during business hours or migrate to Option A (AgentCore Gateway).
- **Latency SLA:** Define acceptable latency targets before production. Student-facing interactions should target <3s end-to-end for routine queries; complex multi-turn advising conversations can tolerate more.

---

## Pillar 5 — Cost Optimization

### Key questions for EDU AI agents

- What does the monthly AWS run cost look like, and how does it scale with student volume?
- Are there cost controls in place to prevent runaway inference spend?
- How does the build-once gateway economics play out over the agent portfolio?

### How the suite addresses this

| Design principle | Platform component | Evidence |
|---|---|---|
| Implement cloud financial management | AWS Budgets alerts in prerequisites checklist; Cost Explorer tagging by agent for per-agent cost visibility | `docs/AWS-FUNDING-AND-PREREQUISITES.md` §B |
| Adopt a consumption model | On-demand DynamoDB; Fargate pay-per-use; Bedrock on-demand inference (no pre-provisioned capacity unless justified) | Default QuickStart template |
| Measure overall efficiency | Monthly TCO report in managed service; per-agent cost tagging | `offerings/MANAGED-SERVICE-OFFERING.md` |
| Stop spending money on undifferentiated heavy lifting | Bedrock managed inference (no model hosting); AgentCore managed gateway (no gateway infrastructure to operate) | AgentCore Option A |
| Analyze and attribute expenditure | Resource tagging strategy: `AgentID`, `Environment`, `InstitutionID` on all resources | `infra/cloudformation/agent-service.yaml` Tags section |

**Build-once economics (the core cost argument):**
The MCP authorization gateway, identity federation, PII masker, HITL framework, and audit trail are built once on the first agent (typically Agent 01 Concierge) and reused by every subsequent agent. The marginal cost of Agent 2 through 8 is dominated by the connector and agent-specific logic — not rebuilding governance. This is the primary financial argument for the gateway-first sequencing: the amortization of the control plane across the portfolio makes the per-agent economics improve with every addition.

See `gtm/roi-calculator/EDU-AI-Suite-ROI-Calculator.xlsx` for the monthly AWS TCO model.

### Known gaps / customer deployment recommendations

- **Bedrock inference is the largest variable line item.** Monitor token consumption per agent and per interaction type. High-volume agents (Concierge, Operations Service Desk) at scale should evaluate provisioned throughput if daily volume justifies it.
- **S3 Object Lock COMPLIANCE mode** on the audit bucket prevents deletion but incurs standard S3 storage costs for the full retention period. For FERPA compliance, the retention period is typically the longer of 5 years or the period the institution's records-retention schedule requires.

---

## Pillar 6 — Sustainability

### Key questions for EDU AI agents

- Is the workload right-sized for actual usage patterns (especially for seasonal EDU traffic)?
- Are we using managed services to avoid overprovisioning?
- Can we reduce inference token consumption without degrading quality?

### How the suite addresses this

| Design principle | Platform component | Evidence |
|---|---|---|
| Understand your impact | Per-agent resource tagging enables carbon footprint reporting via AWS Customer Carbon Footprint Tool | Tagging strategy in CloudFormation templates |
| Establish sustainability goals | Use smaller models (Haiku) for simpler tasks; prompt engineering to reduce token waste | `platform_core/edu_agent_platform/llm_factory.py` model selection |
| Maximize utilization | Fargate right-sizing; on-demand DynamoDB; no always-on EC2 instances in default deployment | Serverless-first architecture |
| Anticipate and adopt new, more efficient hardware | Fargate uses AWS's latest Graviton infrastructure; no customer action required | Fargate managed |
| Use managed services | Bedrock, AgentCore, Fargate, DynamoDB, API Gateway — all fully managed | Default architecture |

---

## Generative AI Lens

The AWS Generative AI Lens (released 2024) adds a set of best practices and questions specifically for GenAI workloads. The following maps the suite to the GenAI Lens design principles and question areas.

### GenAI Lens — Responsible AI

| Lens principle | Suite implementation |
|---|---|
| Define responsible AI policies before deploying | `governance/README.md` — comprehensive responsible-AI policy including the bright line (what agents never decide), fairness monitoring, red-team cadence, and human oversight requirements |
| Implement human oversight for high-stakes decisions | MCP gateway HITL gate — framework-enforced, not procedural; every consequential action requires a named human reviewer bound into the record |
| Monitor for bias and fairness | `governance/tests/test_fairness.py`; false-positive/false-negative monitoring by cohort in managed service; fairness alarm triggers immediate review |
| Establish an AI governance committee or function | Recommended in `governance/README.md`; the institution must designate an AI governance function — the SI provides the platform controls |
| Maintain auditability | PII-masked append-only DynamoDB audit trail; satisfies FERPA disclosure recordkeeping |

### GenAI Lens — Model Selection and Management

| Lens principle | Suite implementation |
|---|---|
| Select the right model for the task | `llm_factory.py` routes by task type: Claude 3 Haiku for classification/simple retrieval, Claude 3.5 Sonnet for complex reasoning, grading, and multi-step advising |
| Evaluate models before deployment | Eval harness in `governance/`; golden-artifact regression; grounding-failure rate monitoring |
| Manage model versions and drift | Hash-pinned prompts in `governance/prompt_manifest.json`; CI blocks on un-bumped drift; sign-off required before any model version promotion |
| Use Bedrock Guardrails | Guardrail configuration per agent in deployment templates; configurable for under-13 populations (heightened sensitivity) |

### GenAI Lens — RAG and Grounding

| Lens principle | Suite implementation |
|---|---|
| Ground responses in authoritative sources | Grounding verification in all agents — every fact must trace to approved institutional content or the agent fails fast |
| Chunk and index content appropriately | Bedrock Knowledge Bases with institution-specific content (catalog, policy docs, FA guidance); content versioning in change control |
| Evaluate retrieval quality | Grounding-failure rate monitored in managed service; retrieval quality is a managed-service KPI |
| Prevent grounding gaps from producing fabricated answers | Fail-fast behavior: ungrounded outputs are blocked, not silently passed to the student |

### GenAI Lens — Prompt Engineering and Security

| Lens principle | Suite implementation |
|---|---|
| Version and test prompts | Hash-pinned in `governance/prompt_manifest.json`; CI enforced; eval regression on every change |
| Protect against prompt injection | PII masker runs before model (injection gets pseudonyms); authorization check lives outside the model (prompt cannot grant elevated access); red-team scenarios in `governance/redteam/` |
| Apply input/output filtering | Bedrock Guardrails on inputs and outputs; topic denial for off-policy content; PII detection layer |
| Separate system and user trust boundaries | Gateway enforces identity and authorization before any user input reaches a tool call; user input cannot escalate privileges |

### GenAI Lens — Evaluation and Continuous Improvement

| Lens principle | Suite implementation |
|---|---|
| Establish evaluation baselines before deployment | Five ROI baseline categories captured before pilot launch (Labor, Service, Learning, Student journey, Risk & quality) |
| Run automated evaluations continuously | Weekly eval regression in managed service; structural golden-artifact regression over advising plans, intervention drafts, accessible-content output |
| Use human evaluation for high-stakes outputs | HITL gate is the human-evaluation layer for consequential outputs; override rate is a managed-service quality signal |
| Track outcome metrics, not proxy metrics | Outcome-framed ROI model (deflection, cycle time, persistence, accuracy) — not conversation volume; see `offerings/COST-ROI-MODEL.md` |

---

## WAFR Session Prep Checklist for the SA

**Before the session:**
- [ ] Read `docs/SUITE-ARCHITECTURE.md` — six-layer reference architecture
- [ ] Read `docs/WHY-THE-MCP-LAYER.md` — gateway justification (Security and Reliability pillars)
- [ ] Pull the customer's current AWS account architecture (Organizations structure, existing SCPs, CloudTrail status)
- [ ] Confirm Bedrock region and model availability with `docs/AWS-FUNDING-AND-PREREQUISITES.md`
- [ ] Identify which agents are in scope for the review (pilot agent only vs. full portfolio)

**During the session — questions to ask the customer:**
- Operational Excellence: "Who owns the prompt change-control process? Who signs off on model-version promotions?"
- Security: "Is CloudTrail enabled org-wide? Do you have a FERPA breach-notification procedure?"
- Reliability: "What are your availability expectations during FAFSA season and enrollment peaks?"
- Performance: "What latency is acceptable for student-facing interactions? Are there peak-hours patterns?"
- Cost: "Do you have AWS Budgets alerts configured? How do you want to track per-agent costs?"
- Sustainability: "Are there carbon-footprint reporting obligations to your board or accreditor?"
- GenAI Responsible AI: "Has the institution designated an AI governance function? Who approves the Guardrail configuration for under-13 populations?"

**After the session:**
- [ ] Produce a WAFR findings report mapping risks to the gaps listed in each pillar above
- [ ] Prioritize gaps by risk level (Security and Reliability gaps are blocking; Cost and Sustainability gaps are advisory)
- [ ] Link WAFR gaps to the AWS funding programs that fund remediation — see `docs/AWS-FUNDING-AND-PREREQUISITES.md`
