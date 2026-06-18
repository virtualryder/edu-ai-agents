# MCP Authorization Gateway — Reference Logic
### Layer 3: The Governed Front Door Between Every Agent and Every System of Record

This package is the **readable, testable Python reference** for the **MCP Authorization Gateway (Layer 3)** — a model of **Amazon Bedrock AgentCore Gateway + AgentCore Identity**. **No agent calls a system of record directly.** Every tool call — read or write — passes through this **one enforcement point**.

The enforcement logic here is **identical regardless of the hosting choice**. Whether you run the managed AgentCore Gateway, assemble the controls from AWS primitives, or build your own FastMCP server, the decision, the human gate, and the audit behave the same. **The lock-in is in the operating model, not the controls** — see `docs/WHY-THE-MCP-LAYER.md` for the business case and the three implementation options.

---

## The enforcement pipeline (in order)

Every tool call runs through these six steps, in this order:

### 1. Identity verification
The request must carry **verified IdP claims** (the institution's own SSO via IAM Identity Center / Cognito). The gateway **denies on a missing subject** — no anonymous or unattributed calls.

### 2. Deny-by-default authorization with least-privilege role intersection
A tool is permitted only if it is granted to **both** the agent and the user's role(s):

```
permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[agent] ∩ ROLE_ENTITLEMENTS[user_roles]
```

Roles are distinct for **student, guardian, educator, counselor, and administrator**. A **guardian's** access is scoped by the **FERPA rights that transfer to the student at 18 / postsecondary enrollment** — a parent agent cannot surface records the parent no longer has a right to. The governing property: **the agent can never exceed the human** on whose behalf it acts. Anything not explicitly in the intersection is denied.

### 3. Human-approval gate
**High-risk / write / consequential** tools do not execute on the agent's say-so. They **block** with **`PENDING_APPROVAL`** until a **verified reviewer identity is bound into the record**. This is **the bright line** — the agent never autonomously decides **grades, admissions, discipline, financial aid, special-education eligibility, or student placement**. A named, authorized human approves, and that identity is bound into the audit record before the action proceeds.

### 4. Short-lived scoped tokens
On an allowed (and, where required, approved) call, a **short-lived, single-purpose token** is minted **per call** via **AgentCore Identity / STS** — scoped to exactly the requested tool. **No standing service accounts**; no master credentials live in the agent.

### 5. Connector invocation
The action runs through **one validated connection per system**. **Read and write are separated** as distinct tools with distinct grants. Results are **field-scoped** — connectors return only the fields the tool needs, preventing redisclosure of record-linkable data.

### 6. PII-masked append-only audit
**Every attempt** is logged with outcome **ALLOW / DENY / PENDING_APPROVAL / ERROR** and **lineage to the system of record**. **Masking runs before the record is written** — FERPA/COPPA identifiers never enter the audit trail in the clear. The trail is **append-only** (DynamoDB `deny:UpdateItem` / `deny:DeleteItem` on the audit partition + S3 Object Lock WORM), supporting **FERPA's recordkeeping of disclosures**.

---

## Tool naming

Tools are named **`connector_kind.operation`** and map **1:1 to AgentCore Gateway targets**. Examples:

| Tool | Kind | Operation |
|---|---|---|
| `sis.get_student_schedule` | SIS | read |
| `crm.create_advising_case` | CRM | write |
| `lms.update_assignment_due_date` | LMS | write |
| `itsm.submit_it_ticket` | ITSM | write |

Read and write capabilities of the same connector are **separate tools with separate grants** — `sis.get_student_schedule` (read) is granted independently of any `sis.*` write tool.

---

## Mapping to the three hosting options

The **enforcement semantics are the same in all three**. Only where each step physically runs differs.

| Pipeline step | A — AgentCore Gateway (managed, default) | B — AWS primitives | C — FastMCP (self-built) |
|---|---|---|---|
| Identity | AgentCore Identity / Cognito authorizer | **Lambda authorizer** | Auth middleware on the MCP server |
| Authorization | Gateway runs the deny-by-default decision | **Lambda authorizer** = deny-by-default decision | Same decision in middleware on every tool |
| Human gate | Gateway enforces the approval gate | **Step Functions `waitForTaskToken`** | Same human-gate middleware wraps every call |
| Scoped tokens | AgentCore Identity per-call credentials | **STS** scoped tokens | Tokens via AgentCore Identity / STS |
| Connector | Each tool = a **target** | API Gateway → backend connector | Each tool exposed as an **MCP tool** |
| Audit | Managed, append-only | **DynamoDB / S3 Object Lock** | Same audit-writer middleware |
| Hosting | Managed by AWS | API Gateway + Lambda + Step Functions | **ECS Fargate or Lambda**, fronted by AgentCore Gateway or API Gateway |

- **Option A — AgentCore Gateway (managed, recommended default).** Each tool is a **target**; the authorizer is **AgentCore Identity / Cognito**; the gateway runs the authorization **decision** and the **human gate**. Least custom plumbing.
- **Option B — API Gateway + Lambda.** A **Lambda authorizer** performs the deny-by-default decision; **Step Functions `waitForTaskToken`** is the human gate; **STS** mints scoped tokens; **DynamoDB / S3 Object Lock** holds the append-only audit. Every control is explicit and inspectable.
- **Option C — FastMCP (self-built).** Each narrowly-scoped tool is exposed as an **MCP tool**; the **same** authorization / human-gate / audit middleware wraps **every** call. Hosted on **ECS Fargate or Lambda**, fronted by **AgentCore Gateway or API Gateway**.

The decision tree (managed vs. primitives vs. self-built) is in `docs/WHY-THE-MCP-LAYER.md`.

---

## What this package is — and is not

This is **reference logic for reading and testing the controls without an AWS account.** It lets a CISO, privacy officer, or platform engineer read exactly how authorization, the human gate, and audit behave, and run the tests against them locally.

It is **not** the production enforcement plane. **Production enforcement is provisioned by `infra/cloudformation/agentcore-gateway.yaml`** (managed AgentCore Gateway) and, for the native deploy shape, by `infra/cloudformation/agent-service.yaml` (the Step Functions `waitForTaskToken` human gate and the deterministic core).

> **Honest reference / accelerator caveat.** This is a deployable accelerator, not a certified product. The customer must harden, validate, security-review, and accept accountability for the production enforcement plane — including IdP role mapping, connector validation against live systems, and the controls in `governance/README.md` §5.

---

## Cross-links

- Why the gateway exists and comes first, with the three options compared: `docs/WHY-THE-MCP-LAYER.md`
- Deployable gateway registration: `infra/cloudformation/agentcore-gateway.yaml`
- EDU compliance spine the gateway enforces (FERPA / COPPA / PPRA / IDEA-504 / the bright line): `governance/README.md`
- Six-layer architecture and where Layer 3 sits: `docs/SUITE-ARCHITECTURE.md`
- Step-by-step deploy and the deny-by-default + HITL walkthroughs: `docs/DEPLOYMENT-HANDBOOK.md`
