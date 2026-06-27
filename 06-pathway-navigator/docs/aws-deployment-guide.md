# Pathway Navigator — AWS Deployment Guide
### Agent 06 — services, topology, and the deterministic-rules-engine separation

> **The defining deployment fact for this agent: the authoritative pathway logic is a deterministic rules engine running as Lambda — Layer 5 deterministic services — and it is not the LLM.** Everything else in this guide hangs off that line. Get the separation wrong and you have an LLM guessing at graduation requirements; get it right and you have a fast, testable, consistent engine whose output can stand in validation evidence, with the LLM doing only what it is good at — conversation and explanation.

This guide covers the Navigator-specific deployment. The platform-wide, empty-account-to-running walkthrough is `../../docs/DEPLOYMENT-HANDBOOK.md`; the IaC lives in `../../infra/cloudformation/` (primary) and `../../infra/terraform/` (parity).

---

## 1. Services this agent uses

| Architecture role | AWS service | Navigator notes |
|---|---|---|
| Conversation & explanation | **Amazon Bedrock (Claude)** | Reached over PrivateLink (interface VPC endpoint), not the public internet; explains audits and pathways; never authoritative for rules |
| Content safety | **Amazon Bedrock Guardrails** | PII denial; age-appropriate filters (heightened for minors); topic filters |
| **Deterministic rules engine** | **AWS Lambda** | Degree-audit, graduation, prerequisite, and transfer-articulation logic — Layer 5 deterministic services; **not the LLM** |
| Program/course/prerequisite/credential/career model | **Amazon Neptune** or **Amazon Aurora** | Graph (Neptune) for relationship-heavy prerequisite/articulation/career adjacency, or relational (Aurora) where preferred |
| Grounded policy & program content | **Amazon Bedrock Knowledge Bases** | Catalogs, program descriptions, policy; segmented by institution/program |
| Labor-market / credential / career data | **Governed data layer** (S3 + Glue + Lake Formation) | Layer 4 RWD/labor-market; no PII join |
| Orchestration (native) | **AWS Step Functions + Lambda** | `waitForTaskToken` HITL gate on writes |
| Agent runtime (container) | **Amazon Bedrock AgentCore Runtime** | ARM64; `/invocations` + `/ping`; port 8080 |
| Authorization gateway | **Amazon Bedrock AgentCore Gateway** | Deny-by-default; role scoping; HITL gate (shared platform) |
| Identity + scoped tokens | **AgentCore Identity + Cognito / IAM Identity Center** | Short-lived per-call credentials; student/guardian/educator/counselor/admin roles |
| Append-only audit | **Amazon DynamoDB** (append-only) | `deny:UpdateItem`/`deny:DeleteItem` on audit partition; PITR |
| WORM snapshots | **Amazon S3 + Object Lock** (COMPLIANCE) | Finalized approved-plan and audit snapshots |
| Encryption + keys | **AWS KMS** (customer-managed key) | Per-environment key; policy restricts to agent role |
| Observability | **Amazon CloudWatch** + **AWS CloudTrail** | HITL queue depth, approval latency; API-level audit feeds unified record |
| Network isolation | **Amazon VPC** | No public inbound; Bedrock via VPC endpoint |

---

## 2. Deploy topology

The Navigator surfaces in **Layer 1** inside the existing student/family portal or an LMS panel (LTI 1.3), with the authenticated identity forwarded as IdP claims. The **Layer 2** LangGraph specialist graph orchestrates intake, retrieval, the rules-engine check, drafting/explanation, the policy gate, routing, and the HITL gate. Every tool call — read or write — leaves the graph through the **Layer 3** AgentCore Gateway; the agent has **no direct network path** to the SIS, the scheduling system, or the advising system. Reads flow through gateway-authorized connectors; writes (`book_counselor_appointment`, `create_advising_case`, `attach_proposed_plan`) suspend at the HITL gate until a named reviewer identity is bound into the record.

```
Portal / LMS panel (LTI 1.3, identity forwarded)
        │
   LangGraph specialist graph (Layer 2)
        │  Intake → Retrieval → RULES-ENGINE CHECK → Draft/Explain → Policy gate → Routing → HITL gate → Finalize
        │
   AgentCore Gateway (Layer 3) ── AgentCore Identity ── Student-PII Masker
        │
   ┌────┴───────────────┬───────────────────┬─────────────────────┐
 SIS connector     Rules engine (Lambda)   KB (program/policy)   Labor-market data
 (PowerSchool/      Neptune / Aurora        Bedrock KB            governed RWD layer
  Banner/Workday)   (graph/relational)
```

---

## 3. AgentCore Runtime (container lift) vs Strands + Step Functions (native rebuild)

The Navigator supports both deployment paths, identical in behavior and governance, different in hosting model — consistent with the suite's two-path stance (`../../docs/SUITE-ARCHITECTURE.md`).

| | AgentCore Runtime (container lift) | Strands + Step Functions (native rebuild) |
|---|---|---|
| What runs the agent | The LangGraph graph packaged as an ARM64 container meeting the `/invocations` + `/ping` contract on port 8080 | Strands Agents SDK for Bedrock inference; **Step Functions** for orchestration |
| HITL gate | LangGraph `interrupt_before` on `finalize` | Step Functions **`waitForTaskToken`** |
| Rules engine | Same deterministic Lambda, invoked as a tool | Same deterministic Lambda, invoked as a state |
| Best for | Fastest lift of the reference graph onto managed runtime | Teams wanting an AWS-native, serverless decomposition with explicit state |
| In this repo | `agent-service.yaml` (AgentCore path) | `agent-service.yaml` (native) + `../../aws-native-reference/` |

In **both** paths, the deterministic degree/graduation/prerequisite/articulation logic is the **same Lambda** — it does not change between hosting models, and it is never folded into the LLM. The rules engine is invoked as a tool (`rules.run_degree_audit`, `rules.check_prerequisites`, `rules.map_transfer_credit`) through the gateway, so its outputs are authorization-checked and audited like any other tool call, and its results are what the LLM explains rather than what the LLM produces.

### Why the rules engine is deterministic Lambda, not the LLM

Graduation requirements, prerequisite chains, and transfer articulation are **rules, not judgments** — they have a correct answer given a transcript and a catalog year, and that answer must be reproducible, testable, and auditable. Running them as deterministic Python in Lambda makes them fast, unit-testable against advisor-reviewed golden audits, and consistent enough to stand in the suite's validation evidence (Layer 5 deterministic services, per `../../docs/SUITE-ARCHITECTURE.md`). The LLM's role is to *explain* the engine's output in language the student can act on — and to never be the thing that decides whether a requirement is met. This is the same architectural discipline the suite applies to rubric-score calculation (Assessment) and completeness validation (Document Services).

---

## 4. Bedrock Guardrail notes

Guardrails are configured at the stack level (`../../infra/cloudformation/security.yaml`) and run on every LLM call automatically, supplementing — never replacing — Layer 3 authorization. For the Navigator specifically:

- **PII denial** on identifiers that could leak into an explanation of a transcript or audit.
- **Age-appropriate content** filters, heightened for minors and (where applicable) under-13 learners per COPPA, since the agent serves middle-school students.
- **Topic filters** that keep the agent in its lane — it explains pathways; it does not opine on the consequential placement decision, and it does not present a recommendation as an approved plan.
- Guardrails do **not** validate pathway correctness — that is the deterministic rules engine's job. Guardrails govern the *language* of the LLM; the rules engine governs the *facts*.

---

## 5. Deploy references

- Master quick-deploy stack and per-stack templates: `../../infra/cloudformation/` (`quickstart.yaml`, `network.yaml`, `security.yaml`, `data.yaml`, `agentcore-gateway.yaml`, `agent-service.yaml`).
- Terraform parity: `../../infra/terraform/`.
- Empty-account-to-running, console + CLI step-by-step: `../../docs/DEPLOYMENT-HANDBOOK.md`.
- Gateway registration semantics (one target per system of record): `../../platform_core/edu_agent_platform/mcp_gateway/`.
- Connector integration and identity/role mapping: `integration-guide.md`.

---

**Maturity: Documented.**
