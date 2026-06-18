# 03 — Educator Copilot — AWS Deployment Guide

> How the Copilot deploys on AWS: services, topology, the runtime decision, and Guardrail configuration — with emphasis on the draft-first, create-not-publish workflow. Empty-account walkthrough: `../../docs/DEPLOYMENT-HANDBOOK.md`. IaC: `../../infra`.

---

## 1. Services used

| Layer | Service | Role in the Copilot |
|---|---|---|
| Agent | **Bedrock Agent** (Claude) on **AgentCore Runtime** *or* **Step Functions + Lambda** | Drafting, differentiation, and LMS-workflow reasoning |
| Data/semantic | **Bedrock Knowledge Bases** | Curriculum, standards, and policy content for grounding |
| Data | **Amazon Aurora / DynamoDB** | Structured instructional metadata — grade, subject, state standard, prerequisite, difficulty |
| Orchestration | **AWS Step Functions** | Content-generation → review workflow with the HITL gate (`waitForTaskToken` native path) |
| Tool/integration | **API Gateway + Lambda** behind **AgentCore Gateway + Identity** | LMS connectors that **create drafts, not publish**; SIS roster reads |
| Models | **Bedrock Guardrails** | Content safety; standards/policy adherence — see §4 |
| Data | **DynamoDB** + **S3 Object Lock** + **CloudTrail** | Versioned source-content + model-config history; append-only action audit |
| Identity | **Cognito / IAM Identity Center** + AgentCore Identity; LTI 1.3 | Federates IdP; educator role; course/section scope |

---

## 2. Deploy topology

Six-layer architecture (`../../docs/SUITE-ARCHITECTURE.md`). The CloudFormation master stack (`../../infra/cloudformation/quickstart.yaml`) nests the standard modules; the Copilot-specific elements are the **content-generation-then-review Step Functions workflow**, the **structured-metadata store**, and **version history**:

```
LMS ──LTI 1.3──▶ Educator Copilot (Layer 2)
       │
       ▼
  Step Functions: retrieve approved curriculum + recent class results
       │            (Bedrock KB + Aurora/DynamoDB metadata)
       ▼
  draft (Bedrock Claude + Guardrails)  ──▶  HITL gate (educator review)
       │                                         │
       └──────── version history (source + model config) ───────┘
       ▼  on approval
  AgentCore Gateway ──▶ LMS connector: create_lms_draft / create_rubric_draft / update_assignment_due_date
                          (CREATE DRAFT — never publish to students)
```

Every write tool is **preview + confirm** and **idempotent**, so a retried request never double-creates a draft or double-extends a deadline. Every draft carries a version record (source content + model config) for change control and rollback.

---

## 3. AgentCore Runtime vs. Strands + Step Functions (native)

| Dimension | **AgentCore Runtime (container)** | **Strands + Step Functions (native)** |
|---|---|---|
| Fit for the Copilot | Good for the conversational drafting surface | **Strong** — the content-generation-then-review and LMS-action flows are naturally Step Functions state machines |
| HITL gate | Gateway-enforced educator approval before any LMS write | **Step Functions `waitForTaskToken`** suspends until the educator approves the proposed action — the IgniteAgent review-then-permit pattern |
| Idempotency | Implemented in the connector Lambda either way | Implemented in the connector Lambda either way |
| Best for | Teams wanting a managed conversational runtime | Teams wanting explicit, inspectable action workflows |

Because the Copilot's value is the **review-then-permit** workflow on LMS actions, the **native Step Functions path is a particularly natural fit**; AgentCore Runtime is equally supported. Reference: `../../aws-native-reference/`.

---

## 4. Guardrail configuration notes

Guardrail provisioned in `../../infra/cloudformation/security.yaml`:

- **No autonomous publish.** The decisive control is architectural, not just a Guardrail: LMS write tools are scoped to **create drafts**; publishing to students requires educator approval at the HITL gate. The Guardrail backstops by blocking any attempt to phrase an action as a direct student-facing publish.
- **Standards/policy adherence.** Drafts align to the applicable state standards via the structured-metadata store; the Guardrail blocks out-of-scope or policy-violating content.
- **Accessibility-aware drafting.** When drafting accommodations or accessible alternatives, outputs are structured to support WCAG 2.2 AA; final conformance is verified by a human (and by Agent 07 for consequential material).
- **Grounding pairing.** Grounding verification (`../../governance/grounding.py`) ties drafted facts/standards/figures to approved curriculum content; ungrounded claims fail fast.
- **Prompt-injection posture.** Class results and discussion text are untrusted input; authorization, the human gate, and audit live outside the model. See `../../governance/redteam/`.

---

## 5. Links

- Step-by-step deploy: `../../docs/DEPLOYMENT-HANDBOOK.md`
- IaC: `../../infra`
- Gateway options: `../../docs/WHY-THE-MCP-LAYER.md`
- Reference architecture: `../../docs/SUITE-ARCHITECTURE.md`
