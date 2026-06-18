# Agent 05 — AWS Deployment Guide
### Student Success & Proactive Engagement — services, topology, and the two runtime paths

> This guide describes how Agent 05 deploys on AWS. It assumes the shared platform — the MCP authorization gateway, identity wiring, append-only audit, and HITL framework — is already provisioned by the master stack. Agent 05 is a **higher-governance** agent: its deployment leans on the separation of the prediction, explanation, and human-decision stages, and on outreach controls (preferences, consent, opt-out) that must be live before any message is sent. See `../../docs/DEPLOYMENT-HANDBOOK.md` for the empty-account-to-running walkthrough and `../../infra/cloudformation/` for the templates.

---

## 1. Services this agent provisions or consumes

| Architecture role | AWS service | Notes specific to Agent 05 |
|---|---|---|
| Agent runtime (container) | **Amazon Bedrock AgentCore Runtime** | ARM64 container; `/invocations` + `/ping`; autoscaling |
| Agent runtime (native) | **Strands Agents + AWS Step Functions + Lambda** | Native rebuild; orchestrates outreach cadence/consent/response/escalation with `waitForTaskToken` |
| MCP authorization gateway | **Amazon Bedrock AgentCore Gateway** | One target per system of record; deny-by-default; HITL gate on every write tool |
| Identity + scoped tokens | **AgentCore Identity + Cognito / IAM Identity Center** | Student/guardian/educator/counselor/administrator role mapping; short-lived per-call tokens |
| LLM inference | **Amazon Bedrock (Claude models)** | Evidence synthesis, pattern explanation, intervention and outreach drafting — explanation stage only |
| Predictive models | **Amazon SageMaker AI** | Existing early-warning endpoints, where prediction is justified; kept separate from explanation and decision |
| Content safety | **Amazon Bedrock Guardrails** | PII denial; age-appropriate filters (minors/under-13); prohibited-behavior and topic filters on outreach copy |
| Governed analytics | **S3 + AWS Glue + Lake Formation + Amazon Redshift** | Student-data lake; Lake Formation enforces domain-combination limits |
| Event signals | **Amazon EventBridge** | Attendance / missing-work / performance / deadline / missing-item / disengagement events route to the agent |
| Program monitoring | **Amazon QuickSight** | Caseload, intervention, outreach, equity dashboards over Redshift |
| Outreach channels | **Amazon Connect + Amazon SES + Amazon SNS** | Voice, SMS, email; preference and opt-out enforced before send |
| Translation & speech | **Amazon Translate + Amazon Polly** | Preferred-language outreach; accessible audio |
| Case management | **Amazon API Gateway** connector | Create/update/escalate success cases in the SoR |
| Append-only audit | **Amazon DynamoDB** (append-only policy) | `deny:UpdateItem`/`deny:DeleteItem` on audit partition; PITR |
| WORM evidence | **Amazon S3 + Object Lock** (COMPLIANCE mode) | Evidence-retention snapshots for review and equity audit |
| Encryption / keys | **AWS KMS** (customer-managed key) | Separate key per environment; key policy restricts to agent role |
| Observability | **Amazon CloudWatch + AWS CloudTrail** | HITL queue depth, approval latency, send/response rates; unified compliance record |
| Network isolation | **Amazon VPC** | No public inbound; Bedrock and SageMaker via VPC endpoint |

---

## 2. Deploy topology

Agent 05 deploys as a per-agent service on top of the shared platform stacks. The master template (`../../infra/cloudformation/quickstart.yaml`) nests the platform; the agent service stack adds the Student Success graph and its wiring.

```
infra/cloudformation/
├── quickstart.yaml          # Master — nests all stacks
├── network.yaml             # VPC, subnets, NAT, security groups, VPC endpoints
├── security.yaml            # KMS, Bedrock Guardrail, Cognito/IAM Identity Center, agent IAM role
├── data.yaml                # Append-only DynamoDB audit, S3 Object Lock WORM, HITL table, data-lake refs
├── agentcore-gateway.yaml   # AgentCore Gateway + Identity — one target per SoR (SIS, LMS, case mgmt, comms)
└── agent-service.yaml       # Agent 05: Step Functions + Lambdas (native) or AgentCore Runtime (container)
```

The event-driven path adds **EventBridge** rules (one per signal type) that invoke the agent service; the analytics path reads the **Lake Formation**-governed lake and renders **QuickSight**; the outreach path fronts **Amazon Connect + SES + SNS** behind gateway write tools. `../../infra/terraform/` provides identical topology in Terraform.

### Request and event flow

```
EventBridge signal  ──►  Agent 05 graph (Layer 2)
   (or scheduled / on-demand evidence request)
        │
        ▼
   READ tools  ──►  MCP Gateway (deny-by-default · role intersection · purpose-of-use)
        │                    │
        │                    ├─► Student-PII masker (FERPA/COPPA) before any result enters a prompt
        │                    └─► Connectors → SIS · LMS · case mgmt · data lake · SageMaker
        ▼
   Stage 1 PREDICTION (SageMaker, justified only) ── kept separate ──┐
   Stage 2 EXPLANATION (Bedrock: synthesize evidence, draft plan/outreach)
        │
        ▼
   Compliance gate (grounding · PPRA no-inference · preferences/opt-out check)
        │
        ▼
   Stage 3 HUMAN DECISION ── HITL gate (interrupt_before / waitForTaskToken)
        │   named reviewer (counselor/teacher/advisor) approves
        ▼
   WRITE tools  ──►  MCP Gateway (mint short-lived write token only after approval bound)
        │
        ▼
   case.create / outreach.send (Connect/SES/SNS) · record · monitor response · escalate
        │
        ▼
   Append-only audit (DynamoDB) + WORM evidence snapshot (S3 Object Lock)
```

**No path from signal to send or case-write bypasses the HITL gate** for a consequential or sensitive action. Reads pass straight through; only consequential writes pause.

---

## 3. AgentCore Runtime (container lift) vs Strands + Step Functions (native rebuild)

Both paths enforce identical controls; they differ in hosting and in how the workflow is expressed.

| | AgentCore Runtime (container lift) | Strands + Step Functions (native rebuild) |
|---|---|---|
| What it is | The LangGraph graph packaged as an ARM64 container against the AgentCore contract (`/invocations`, `/ping`, port 8080) | Deterministic core as Lambda; Strands Agents SDK for Bedrock inference; Step Functions for orchestration |
| HITL gate | LangGraph `interrupt_before` on `finalize`; approval written to the HITL queue table | Step Functions `waitForTaskToken` suspends until a verified approval resumes the task |
| Best fit for Agent 05 | Fastest lift of an existing graph; managed runtime, memory, observability | **Preferred** — outreach cadence, consent, response-monitoring, and escalation map naturally onto Step Functions state machines |
| Orchestration shape | In-process graph routing | Explicit state machine: signal intake → evidence → review (waitForTaskToken) → send → monitor → escalate |
| In this repo | `agent-service.yaml` (AgentCore Runtime mode) | `agent-service.yaml` (native mode) + `../../aws-native-reference/` |

Because Agent 05's outreach is inherently a long-running, multi-step cadence with human pauses and timed response windows, the **native Strands + Step Functions** path is the recommended default; the container lift remains available where a team wants to ship the existing graph quickly under AgentCore's managed runtime.

---

## 4. Bedrock Guardrail notes

Guardrails are configured at the stack level (`../../infra/cloudformation/security.yaml`) and run on every Bedrock call automatically, **supplementing — never replacing — Layer 3 authorization**. For Agent 05 specifically:

- **PII denial** on all model input/output; the student-PII masker has already run at the gateway, and Guardrails are a second line.
- **Age-appropriate content**, heightened for minors and under-13 per COPPA, on all student- and family-facing outreach copy.
- **Prohibited-behavior and topic filters** tuned to outreach: no protected-category inference (PPRA), no stigmatizing or labeling language, no content that implies a determination the agent is not permitted to make.
- **Grounding alignment** — outreach and intervention drafts must trace to approved templates and operational signals; ungrounded claims fail fast at the governance layer (`../../governance/`).

Guardrail tuning for the specific student population — including minors — is a customer responsibility and a production-readiness gate.

---

## 5. Cross-references

- Step-by-step deploy: `../../docs/DEPLOYMENT-HANDBOOK.md`
- Templates (primary path): `../../infra/cloudformation/`
- Terraform parity: `../../infra/terraform/`
- Native reference: `../../aws-native-reference/`
- Six-layer architecture + service mapping: `../../docs/SUITE-ARCHITECTURE.md`
- Gateway reference logic: `../../platform_core/edu_agent_platform/mcp_gateway/`
- Integration & identity mapping: `./integration-guide.md`
- Compliance spine: `./edu-compliance.md` and `../../governance/README.md`

---

**Maturity: Documented.**
