# 01 — Student & Family Services Concierge — AWS Deployment Guide

> How the Concierge deploys on AWS: services, topology, the AgentCore-Runtime-vs-native decision, and Guardrail configuration. For the empty-account-to-running walkthrough see `../../docs/DEPLOYMENT-HANDBOOK.md`; for the IaC see `../../infra`.

---

## 1. Services used

| Layer | Service | Role in the Concierge |
|---|---|---|
| Experience | **Amazon Connect** | Voice, SMS, and chat contact-center channel; after-hours self-service. Web/mobile front end forwards the same IdP claims |
| Experience | **Amazon Translate + Polly** | Real-time translation and natural voice for multilingual families (Title VI) |
| Agent | **Bedrock AgentCore Runtime** *or* **Step Functions + Lambda** | Hosts the Concierge graph; see §3 |
| Tool/integration | **AgentCore Gateway + AgentCore Identity** | Deny-by-default authorization, per-call scoped tokens, HITL gate for write tools |
| Tool/integration | **API Gateway + Lambda** | Connector functions for SIS/CRM/scheduling (Option B primitives also build the gateway here) |
| Data/semantic | **Bedrock Knowledge Bases** (OpenSearch Serverless / Aurora pgvector) | Grounded public answers over approved institutional content |
| Models | **Bedrock (Claude)** | In-account inference; no PII egress after masking |
| Models | **Bedrock Guardrails** | PII denial, age-appropriate filters, topic blocking — see §4 |
| Data | **DynamoDB** (append-only) + **S3 Object Lock** | FERPA-aligned disclosure audit; finalized snapshots |
| Identity | **Cognito / IAM Identity Center** | Federates the institution's Okta/Entra/Google Workspace/AD |
| Security | **AWS KMS** (customer-managed key), **Amazon VPC** | Per-environment encryption; no public inbound; Bedrock via VPC endpoint |
| Observability | **CloudWatch + CloudTrail** | Invocation counts, latency, HITL queue depth, approval latency; API-level audit |

---

## 2. Deploy topology

The Concierge follows the suite's six-layer reference architecture (`../../docs/SUITE-ARCHITECTURE.md`). The CloudFormation quick-deploy master stack (`../../infra/cloudformation/quickstart.yaml`) nests:

```
quickstart.yaml
├── network.yaml            # VPC, subnets, NAT, security groups — no public inbound to the agent
├── security.yaml           # KMS CMK, Bedrock Guardrail, Cognito/IAM Identity Center federation, agent IAM role
├── data.yaml               # Append-only DynamoDB audit, S3 Object Lock WORM, HITL table, KB data refs
├── agentcore-gateway.yaml  # AgentCore Gateway + Identity — one target per system of record (SIS, CRM, scheduling)
└── agent-service.yaml      # Concierge runtime: AgentCore Runtime container OR Step Functions + Lambdas
```

Request flow: **Amazon Connect / web / mobile → Concierge agent (Layer 2) → AgentCore Gateway (Layer 3) → connector → SIS/CRM/scheduling**. Public answers route through the Knowledge Base (Layer 4) and Bedrock + Guardrails (Layer 5) without touching the gateway. Authenticated reads and all writes pass through the gateway; every attempt (ALLOW / DENY / PENDING_APPROVAL / ERROR) lands in the append-only audit. Terraform parity in `../../infra/terraform/`.

---

## 3. AgentCore Runtime vs. Strands + Step Functions (native)

Both are first-class; the Concierge contract is identical either way.

| Dimension | **AgentCore Runtime (container lift)** | **Strands + Step Functions (native rebuild)** |
|---|---|---|
| What it is | The Concierge graph packaged as an ARM64 container honoring the AgentCore contract (`/invocations`, `/ping`, port 8080) | Deterministic core as Lambda, Strands Agents SDK for Bedrock inference, Step Functions for orchestration |
| HITL gate | Gateway-enforced human-approval on write tools | Step Functions **`waitForTaskToken`** suspends until a verified approval is written |
| Best for | Fastest path to a managed runtime, memory, and observability | Platform teams wanting explicit, serverless, pay-per-invocation orchestration |
| Scaling | Managed autoscaling | Lambda concurrency + Step Functions |

For the Concierge specifically, most authenticated traffic is **read-through** (status, schedule) and passes straight through; only `create_advising_case`, `schedule_appointment`, `send_form`, and `draft_family_message` may pause for a gate, so either runtime carries the load comfortably. Reference implementation: `../../aws-native-reference/`.

---

## 4. Guardrail configuration notes

The Bedrock Guardrail is provisioned at the stack level in `../../infra/cloudformation/security.yaml` and runs on **every** LLM call, supplementing — never replacing — Layer 3 authorization.

- **PII denial.** Block model emission of student identifiers, dates of birth, and guardian details; the platform student-PII masker still runs before any inbound tool result enters a prompt or audit record.
- **Age-appropriate filters (heightened for minors).** K–12 deployments serve children under 13 — set COPPA-grade content filters and prohibit any non-educational or behavioral-profiling use; the under-13 flag travels in the identity claims and drives the stricter profile.
- **Topic filters.** Block out-of-scope topics and any attempt to coax the agent toward a bright-line decision (committing a financial-aid award, an admissions outcome, a disciplinary stance).
- **Grounding pairing.** Guardrails handle safety; **grounding verification** (`../../governance/grounding.py`) handles truth — every deadline, policy, or status in a family-facing answer must trace to approved content or it fails fast.
- **Prompt-injection posture.** Inbound chat/email text is untrusted; authorization, the human gate, and audit live outside the model (Layer 3), so they hold regardless of what any injected instruction says. See `../../governance/redteam/`.

---

## 5. Links

- Step-by-step deploy (console + CLI): `../../docs/DEPLOYMENT-HANDBOOK.md`
- IaC (CloudFormation primary, Terraform parity): `../../infra`
- Gateway implementation options (managed / primitives / FastMCP): `../../docs/WHY-THE-MCP-LAYER.md`
- Six-layer reference architecture + service mapping: `../../docs/SUITE-ARCHITECTURE.md`
