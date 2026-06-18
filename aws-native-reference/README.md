# AWS-Native Reference
### Strands Agents SDK + Step Functions Rebuild, and the Shared Container Contract

There are **two AWS deploy shapes** for every agent in the suite, and they share the same governance:

1. **Container lift onto AgentCore Runtime** — package the existing agent as an ARM64 container and run it on **Amazon Bedrock AgentCore Runtime**. Fastest path from the demo code to a managed runtime.
2. **Native rebuild** — re-express the agent as a **deterministic core running as AWS Lambda** + the **Strands Agents SDK** for Bedrock inference + **AWS Step Functions** for orchestration, with a **`waitForTaskToken`** state as the human-in-the-loop (HITL) gate. Best when the platform team wants explicit, inspectable orchestration and AWS-primitive control points.

This directory documents the **native rebuild** and the **shared container contract** that both shapes honor. Which shape a stack deploys is selected by the `DeployMode` parameter (`native` | `container`) on `infra/cloudformation/quickstart.yaml`; the native path is provisioned by `infra/cloudformation/agent-service.yaml`.

> **The bright line holds in both shapes.** Whichever shape runs, agents never autonomously decide **grades, admissions, discipline, financial aid, special-education eligibility, or student placement.** The native path enforces the same HITL gate via `waitForTaskToken` — a consequential action resumes only when a verified approval record, binding a named reviewer identity, is written to the HITL queue table.

---

## The container contract

Both AgentCore Runtime and ECS honor the **same** HTTP contract. Build to it once and the agent is portable across both.

| Aspect | Contract |
|---|---|
| **Architecture** | **ARM64** container image. |
| **Server** | HTTP server listening on **port 8080**. |
| **Invocation** | **`POST /invocations`** — a **stateless** agent invocation. The request carries the **forwarded IdP claims + role** and the **task context**. No session state is held in the container between calls. |
| **Health** | **`GET /ping`** — health/readiness check. |

The request body to `/invocations` always carries the verified identity (claims + `custom:edu_role`) so that **authorization happens at Layer 3**, not in the container. The container forwards every tool call through the gateway; it never holds connector credentials or a direct path to a system of record.

---

## The native rebuild pattern

The native rebuild maps the **LangGraph specialist agent pattern** onto **Step Functions states**:

```
Intake → [Retrieval nodes] → Draft / Analyze → [Policy & compliance gate] → Routing → HITL Gate → Finalize
```

How each stage lands on AWS:

| Specialist stage | Native implementation |
|---|---|
| **Intake** | Step Functions entry state; validates forwarded IdP claims + role + task context. |
| **Retrieval nodes** | Gateway-authorized connector reads (via Layer 3) and Bedrock Knowledge Base lookups. **No direct system-of-record access** — every read is a gateway tool call. |
| **Draft / Analyze** | **Bedrock (Claude) via the Strands Agents SDK** for the generative steps. |
| **Policy & compliance gate** | **Deterministic services as Lambda** — degree/graduation/prerequisite rules, rubric score calculation, completeness validation, and prohibited-language detection. Fast, testable, no LLM. |
| **Routing** | A Step Functions Choice state: clean output → HITL gate; one bounded revision → loop back; prohibited → escalate. |
| **HITL Gate** | A **`waitForTaskToken`** state. **This state *is* the HITL gate.** Execution suspends and resumes **only** when a verified approval record is written to the **HITL queue table** — the task token is the resume key, and the gateway will not mint the downstream write token without a valid reviewer identity bound into the record. |
| **Finalize** | Mints the scoped write token, performs the gateway-authorized write, and writes the closing audit record. |

Cross-cutting, on every step:

- **Every gateway tool call goes through Layer 3** — there is no direct SoR access from any Lambda or container.
- **PII masking runs before any prompt or audit record** — FERPA/COPPA identifiers are replaced with stable pseudonyms before content enters a Claude prompt or the audit trail.
- **Append-only audit on every step** — each attempt (ALLOW / DENY / PENDING_APPROVAL / ERROR) is recorded with lineage to the system of record.

There is **no path from intake to finalize that bypasses the HITL gate** for a consequential action — the same property the LangGraph build enforces with `interrupt_before`.

---

## All eight agents share this skeleton

Every agent — 01 Concierge, 02 Tutor, 03 Educator Copilot, 04 Assessment, 05 Student Success, 06 Pathway Navigator, 07 Document & Accessibility, 08 Operations Service Desk — uses the **same** Step Functions skeleton above. The differences between agents are narrow:

- **Retrieval nodes** — which knowledge bases and connectors are read.
- **Deterministic services** — e.g., degree rules (06), rubric calc (04), completeness validation (07), prohibited-language detection (shared).
- **Tool grants** — the `AGENT_TOOL_GRANTS` entries for that agent.
- **Which roles approve** — which reviewer role the HITL gate routes to (educator, counselor, registrar, administrator).

### Intended per-agent layout

```
aws-native-reference/
├── README.md                       # This file
├── _shared/                        # Common building blocks reused by all agents
│   ├── container/                  # ARM64 container base honoring /invocations + /ping
│   ├── gateway_client/             # Layer 3 client — every tool call routes through the gateway
│   ├── pii_masker_hook/            # PII masking invoked before prompt and before audit
│   └── audit_writer/               # Append-only audit record writer
└── <agent>/                        # One per agent, e.g. 01-concierge/
    ├── statemachine/               # Step Functions definition (the skeleton above)
    ├── lambdas/                    # Deterministic services + step handlers
    └── container/                  # ARM64 container for the container-lift shape
```

`_shared/` holds the common container base, the gateway client, the PII-masker hook, and the audit writer — so a governance fix made once benefits every agent.

---

## Cross-links

- Provisions the native path (Step Functions + Lambdas) and the container path, gated by `DeployMode`: `infra/cloudformation/agent-service.yaml`
- Step-by-step deploy (empty account → running, governed, human-gated agent): `docs/DEPLOYMENT-HANDBOOK.md`
- Six-layer architecture and AWS service mapping: `docs/SUITE-ARCHITECTURE.md`
- Gateway reference logic (Layer 3 enforcement): `platform_core/edu_agent_platform/mcp_gateway/README.md`
- Why the gateway comes first + three implementation options: `docs/WHY-THE-MCP-LAYER.md`
