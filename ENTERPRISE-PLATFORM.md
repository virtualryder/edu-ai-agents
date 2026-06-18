# The Enterprise Platform Story
### Why the EDU AI Agent Suite is a platform, not eight chatbots

> The agents are the visible surface. The durable asset an institution buys is the **governed platform** beneath them: modernized API access to systems of record, one authorization and audit layer, and a compliance spine that every agent inherits. This document is the architecture-and-strategy narrative for a CIO, CISO, or chief academic/technology officer evaluating the program.

---

## 1. The strategic problem

Every institution already owns the systems that hold the answers — the SIS, the LMS, the ERP, the CRM, the ITSM. The pain isn't missing data; it's that the data is **locked behind portals, PDFs, and staff inboxes**, reachable only by a human who knows which screen to open. AI agents are valuable precisely because they can bridge that gap — but only if they can reach the systems safely.

That reframes the program. The hard part of "deploy AI agents in education" is not the model and not the chat interface. It is **giving agents clean, governed API access to the data itself**, with identity, least privilege, human approval on consequential actions, and a complete audit trail. Solve that once and every agent benefits; skip it and every agent stalls at the security and privacy review.

---

## 2. Three things the platform delivers

### A. API modernization as a byproduct
To let agents act, you expose narrowly-scoped tools (`get_student_schedule`, `check_application_status`, `create_advising_case`, `submit_it_ticket`) over your systems of record. That is, in effect, a modern, governed API surface for the institution — useful well beyond agents (portals, integrations, reporting). The agent program funds an integration capability the institution keeps.

### B. One authorization and audit layer for all agents
The MCP authorization gateway (Layer 3) is built once and reused by all eight agents. Identity, role scoping (student/guardian/educator/counselor/administrator), human-approval gating, short-lived scoped tokens, and the PII-masked append-only audit are shared platform. The marginal cost of agent #2 through #8 is dramatically lower than agent #1 because they inherit the control plane. See `docs/WHY-THE-MCP-LAYER.md` for the funding argument and the three implementation options (managed AgentCore Gateway, AWS primitives, or a self-built FastMCP server).

### C. A compliance spine that compounds
FERPA, COPPA, PPRA, IDEA/504, ADA/508/WCAG, and state student-privacy controls are implemented as shared platform services (governance layer + PII masker + Guardrails). A single improvement — a better masker, a tighter grounding check — raises the compliance posture of every agent simultaneously. See `governance/README.md`.

---

## 3. The control plane, concretely

Every tool call, read or write, passes one enforcement point:

1. **Identity** — verified IdP claims from the institution's own SSO; role and (where relevant) under-13 and age-of-majority state carried in claims.
2. **Authorization** — `permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[agent] ∩ ROLE_ENTITLEMENTS[user_roles]`; deny-by-default; the agent can never exceed the human.
3. **Human gate** — consequential/irreversible tools block until a verified reviewer identity is bound to the record.
4. **Scoped token** — minted per call; no standing service accounts.
5. **Audit** — every attempt logged, PII-masked, append-only, lineage to the system of record.

Reference logic is readable, testable Python in `platform_core/edu_agent_platform/mcp_gateway/` — so a security reviewer can see exactly how the controls behave without an AWS account, and so the logic is portable across the three hosting options.

---

## 4. Deployment model

- **Primary:** CloudFormation quick-deploy provisions a customer-isolated environment (VPC, KMS, Cognito/IAM Identity Center federation, Guardrail, append-only audit, AgentCore Gateway, per-agent runtime). Terraform parity for teams standardized on Terraform.
- **Runtime:** AgentCore Runtime (ARM64 container, `/invocations` + `/ping`) or the native Strands + Step Functions rebuild with a `waitForTaskToken` HITL gate.
- **Inference:** Amazon Bedrock (Claude) in-account; student PII never egresses the VPC after masking.

Step-by-step in `docs/DEPLOYMENT-HANDBOOK.md`; architecture and AWS service mapping in `docs/SUITE-ARCHITECTURE.md`.

---

## 5. ADR-001 — Orchestration stance (multi-agent / A2A)

**Decision:** Use in-process **LangGraph** orchestration within each specialist agent today. Adopt **agent-to-agent (A2A) coordination through AgentCore** only when a workflow genuinely spans agents and needs cross-agent autonomy (e.g., a student-success case that must invoke the Pathway Navigator and the Concierge in one flow).

**Rationale:** In-process orchestration is deterministic, testable, and auditable — properties an education compliance function requires. A supervisor agent can route intent across specialists *without holding tool grants* (it can call specialists, never systems of record), which keeps the authorization boundary clean. Premature multi-agent autonomy adds non-determinism and audit complexity without clear value at the current maturity.

**Status:** Accepted. A runnable, governed reference hop is provided so the A2A path is real, not hypothetical, when the customer needs it.

**Consequences:** Each agent remains independently deployable and reviewable. Cross-agent workflows are explicit and gated. The orchestration choice does not leak into the authorization or audit design.

---

## 6. Where the emerging use cases fit

Four use cases are receiving heavy attention but are **emerging, not routinely mature**, and are explicitly *roadmap* in this suite: a longitudinal learner-success orchestrator; precision-learning agent teams; cross-system autonomous institutional operations; and dialogue-based assessment/simulations. Each raises the bar on longitudinal privacy, permissioning, segregation of duties, and academic-integrity controls. The platform is built so these are reachable — AgentCore memory with strict retention boundaries, event-driven ingestion, a supervisor pattern — without committing the institution to them before the governance is ready. The reframe for leadership: **land the bounded agents now; the platform is the on-ramp to the orchestrated future when your governance catches up to it.**
