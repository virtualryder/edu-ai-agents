# Operations Service Desk — AWS Deployment Guide
### Services, deploy topology, runtime options, and the diagnostic/privileged-remediation division

> This guide is the AWS-specific companion to the agent README (`../README.md`) and the suite architecture (`../../docs/SUITE-ARCHITECTURE.md`). It assumes the shared platform — gateway, identity, PII masker, audit — is already deployed via the suite's CloudFormation quick-deploy. The step-by-step empty-account-to-running path is in `../../docs/DEPLOYMENT-HANDBOOK.md`.

---

## 1. Services used

Agent 08 maps onto the suite's six-layer architecture. The services below are named exactly as the canon names them (`../../docs/SUITE-ARCHITECTURE.md`).

| Architecture role | AWS service | Agent-08 use |
|---|---|---|
| Experience layer | **Amazon Connect** OR thin web/mobile front end; Microsoft Teams | Service-desk voice/SMS/chat; staff admin surface where staff already work |
| Agent runtime (container) | **Amazon Bedrock AgentCore Runtime** | Container lift — ARM64, `/invocations` + `/ping`, port 8080 |
| Agent runtime (native) | **AWS Step Functions + Lambda** | Native rebuild; `waitForTaskToken` HITL gate; deterministic core |
| MCP authorization gateway | **Amazon Bedrock AgentCore Gateway** | One target per system of record; deny-by-default; HITL enforcement |
| Federated identity + scoped tokens | **AgentCore Identity + Cognito / IAM Identity Center** | IdP federation; short-lived per-call credentials; role/group membership |
| LLM inference | **Amazon Bedrock (Claude models)** | Reached over PrivateLink (interface VPC endpoint), not the public internet; direct identifiers masked before inference |
| Content safety + PII controls | **Amazon Bedrock Guardrails** | PII denial; prohibited-behavior topic filters; age-appropriate filters for student-facing tickets |
| Knowledge base / search | **Amazon Bedrock Knowledge Bases**; **Amazon Q Business** | Document-level-permissioned IT and staff-policy retrieval; broad enterprise staff search |
| Safe diagnostics | **AWS Lambda** | Non-mutating diagnostic functions (ping, link check, service status) |
| Endpoint remediation | **AWS Systems Manager** | Gated service restart — **authorized institution-managed devices only** |
| Approvals / orchestration | **AWS Step Functions** | `waitForTaskToken` HITL gate for privileged remediation and admin workflows |
| Append-only audit | **Amazon DynamoDB** (append-only) | Every ALLOW/DENY/PENDING_APPROVAL/ERROR with lineage |
| WORM store | **Amazon S3 + Object Lock** (COMPLIANCE mode) | Finalized board material, records-request artifacts, audit snapshots |
| Encryption + keys | **AWS KMS** (customer-managed key) | Separate key per environment; key policy restricts to agent role |
| Operational observability | **Amazon CloudWatch** | HITL queue depth, approval latency, error-rate alarms; endpoint telemetry |
| API-level audit | **AWS CloudTrail** | All AWS API calls; unified compliance record |
| Network isolation | **Amazon VPC** | No public inbound; Bedrock via VPC endpoint |

---

## 2. Deploy topology

The agent deploys as one or more domain-scoped services behind the shared gateway. Because tool sets are **separated by administrative domain**, the recommended topology is one agent service (and one tool-grant set) per domain — IT service desk, HR, finance, procurement, facilities — rather than a single agent holding all grants. This is not cosmetic: it is the structural enforcement of "no unrestricted cross-domain search."

```
Layer 1   Amazon Connect / web / Teams
              │  (forwards verified IdP claims + role + group membership)
              ▼
Layer 2   Agent service(s)  — AgentCore Runtime container  OR  Strands + Step Functions
              │              (one service / grant-set per administrative domain)
              ▼
Layer 3   MCP Authorization Gateway (AgentCore Gateway + AgentCore Identity)
              │  deny-by-default · least-privilege intersection · purpose-of-use · HITL gate
              │  student-PII masker runs before any result enters a prompt or audit record
   ┌──────────┼───────────────────────────────────────────────┐
   ▼          ▼                          ▼                       ▼
READ/DIAG   WRITE/PRIVILEGED          Knowledge (Layer 4)      Audit (Layer 6)
Lambda      AWS Systems Manager       Bedrock KB / Q Business  DynamoDB append-only
telemetry   (authorized devices)      doc-level permissions    S3 Object Lock · CloudTrail
ITSM read   identity reset · restart  group membership →       CloudWatch
                                       retrieval scope
```

Provisioning uses the suite templates (`../../infra/cloudformation/`): `network.yaml`, `security.yaml` (KMS, Guardrail, IdP federation, agent role), `data.yaml` (append-only DynamoDB, S3 Object Lock, HITL table), `agentcore-gateway.yaml` (one target per system of record), and `agent-service.yaml` (the per-agent Step Functions + Lambdas, or the AgentCore Runtime container). Terraform parity is in `../../infra/terraform/`.

---

## 3. AgentCore Runtime (container lift) vs Strands + Step Functions (native rebuild)

The suite supports both paths; the distinction is exactly as the canon draws it.

| | AgentCore Runtime (container lift) | Strands + Step Functions (native rebuild) |
|---|---|---|
| What it is | The agent graph packaged as an ARM64 container meeting the AgentCore contract (`/invocations`, `/ping`, port 8080) | Deterministic core functions as **Lambda**, **Strands Agents SDK** for Bedrock inference, **Step Functions** for orchestration |
| HITL gate | Enforced by the gateway before the write token is minted | **Step Functions `waitForTaskToken`** suspends until a verified approval record is written |
| Best fit for Agent 08 | Fastest lift of an existing agent graph; minimal re-plumbing | When the institution wants the diagnostic/remediation split expressed as explicit, inspectable state-machine steps |
| Where defined | `agent-service.yaml` (container) | `agent-service.yaml` (native) + `../../aws-native-reference/` |

For Agent 08, the native rebuild has a particular advantage: the **diagnostic step and the privileged-remediation step are separate states**, and the `waitForTaskToken` pause sits between them, making the bright line visible in the orchestration itself rather than only in the gateway grants.

---

## 4. The diagnostic / privileged-remediation division (the load-bearing control)

This agent's defining design choice is a **strong division between diagnostic actions and privileged remediation**. It is enforced in three independent places, so no single failure collapses it.

1. **Separate tools, separate grants.** `endpoint.get_device_telemetry` and `endpoint.run_safe_diagnostic` are READ/DIAGNOSTIC tools with no approval gate. `identity.reset_password` and `endpoint.restart_managed_service` are WRITE/PRIVILEGED-REMEDIATION tools that block on a HITL gate. Read and write are never the same tool, and the diagnostic grant never implies the remediation grant.
2. **Gateway authorization.** The gateway computes `permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[agent] ∩ ROLE_ENTITLEMENTS[user_roles]` (`../../platform_core/edu_agent_platform/mcp_gateway/`). A privileged-remediation tool additionally blocks until a verified, named reviewer identity is bound into the record.
3. **Systems Manager scoping.** Privileged endpoint remediation runs through **AWS Systems Manager** and is scoped **only to institution-managed, authorized devices** — enforced by the SSM resource group / tag policy and the agent IAM role, never by the model's judgment. Personal and unmanaged devices are out of reach by construction.

Diagnostics inform a human; they do not act. Privileged remediation acts; it requires a named human approver every time.

---

## 5. Separation of agents / tool sets by administrative domain

There is **no unrestricted cross-domain search and no master-grant agent.** The IT service-desk agent cannot read HR records; the procurement agent cannot reach the device fleet; the finance agent cannot search facilities tickets. Each domain is a distinct grant set, and broad staff search via **Amazon Q Business** is itself constrained by the requester's group membership and the document-level permissions configured in **Amazon Bedrock Knowledge Bases**. Retrieval respects existing permissions — it never returns content the user is not entitled to see. Integration detail for identity and group-membership propagation is in `integration-guide.md`.

---

## 6. Bedrock Guardrail notes

**Bedrock Guardrails** are configured at the stack level (`../../infra/cloudformation/security.yaml`) and run on every LLM call, supplementing — never replacing — Layer 3 authorization. For Agent 08:

- **PII denial** prevents student or staff identifiers from surfacing in a service-desk transcript, a drafted document, or an audit record beyond what the masker has pseudonymized.
- **Prohibited-behavior topic filters** block the agent from describing how to perform a privileged action outside the gate (e.g., walking a user through a manual credential reset) and from emitting content that would constitute the agent making a consequential decision.
- **Age-appropriate filters** apply when the requester is a student — including the COPPA-heightened bar for under-13 learners — since students and families are first-class users of the service desk.

Guardrails are a model-layer safety net. The authoritative controls for who-can-do-what remain the gateway's deny-by-default authorization and the HITL gate.

---

## 7. References

- Suite architecture and AWS service mapping: `../../docs/SUITE-ARCHITECTURE.md`
- Why the governed access layer comes first, and the three implementation options: `../../docs/WHY-THE-MCP-LAYER.md`
- Gateway reference logic: `../../platform_core/edu_agent_platform/mcp_gateway/`
- CloudFormation quick-deploy and Terraform parity: `../../infra/cloudformation/`, `../../infra/terraform/`
- Step-by-step deployment: `../../docs/DEPLOYMENT-HANDBOOK.md`
- Compliance spine: `../../governance/README.md`

---

Maturity: **Documented.**
