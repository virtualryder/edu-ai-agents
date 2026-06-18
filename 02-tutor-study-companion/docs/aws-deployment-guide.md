# 02 — Personalized Tutor & Study Companion — AWS Deployment Guide

> How the Tutor deploys on AWS: services, topology, the runtime decision, and Guardrail configuration — with emphasis on the integrity bright line. Empty-account walkthrough: `../../docs/DEPLOYMENT-HANDBOOK.md`. IaC: `../../infra`.

---

## 1. Services used

| Layer | Service | Role in the Tutor |
|---|---|---|
| Data | **Amazon S3** | Approved course content store, segmented by institution/course/section |
| Ingestion | **Amazon Textract** | Extracts text/structure from PDFs, slides, and worksheets for grounding |
| Data/semantic | **Bedrock Knowledge Bases** + **OpenSearch** (vector) | Segmented retrieval; semantic search over approved materials |
| Agent | **Amazon Bedrock Agent** (Claude) on **AgentCore Runtime** *or* **Step Functions + Lambda** | Tutoring strategies (Socratic, hints, explanation) |
| State | **Amazon DynamoDB** | Per-student tutoring session memory |
| Identity | **Cognito / LMS SSO** + AgentCore Identity | Federates IdP; scopes to enrolled section |
| Experience | **LTI 1.3 / LTI Advantage** | Embeds the tutor in the LMS course |
| Models | **Bedrock Guardrails** | Blocks completing prohibited assessments and unsafe content — see §4 |
| Tool/integration | **AgentCore Gateway + Identity** | Deny-by-default; scopes retrieval to the student's course/section |
| Audit | **DynamoDB** (append-only) + **CloudTrail** | Session and tool-call audit |

---

## 2. Deploy topology

The Tutor follows the six-layer architecture (`../../docs/SUITE-ARCHITECTURE.md`) with the data layer carrying most of the weight. The CloudFormation master stack (`../../infra/cloudformation/quickstart.yaml`) nests the same modules as the rest of the suite; the Tutor-specific elements are the **segmented Knowledge Base** and the **Textract ingest pipeline**:

```
S3 (approved course content)
   └─ Textract ingest ─→ Bedrock Knowledge Base (segmented: institution / course / section / role)
                              └─ OpenSearch vector index
LMS ──LTI 1.3──▶ Tutor agent (Layer 2) ──▶ AgentCore Gateway (Layer 3) ──▶ get_course_materials / session state
                              └─ Bedrock (Claude) + Guardrails (Layer 5)
```

**Segmentation is the load-bearing control:** retrieval is partitioned so a student's tutor can only reach the approved content for the courses/sections they are enrolled in — retrieval respects existing permissions at Layer 4, authorization is enforced at Layer 3, and neither lives in the UI.

---

## 3. AgentCore Runtime vs. Strands + Step Functions (native)

| Dimension | **AgentCore Runtime (container)** | **Strands + Step Functions (native)** |
|---|---|---|
| Fit for the Tutor | Strong — conversational, stateful, benefits from managed memory and observability; matches the UT Sage ECS-style topology | Strong where the platform team wants explicit serverless orchestration |
| Session state | DynamoDB session table either way | DynamoDB session table either way |
| HITL | Minimal — the Tutor's only write (`surface_misconception_signal`) is aggregate and low-risk; gate applies if the institution chooses educator review of dashboard publication | Step Functions `waitForTaskToken` if a gate is configured |
| Best for | Most tutoring deployments (conversational latency, managed memory) | Teams standardized on Step Functions/Lambda |

Because the Tutor is dialogue-heavy and largely read-through, **AgentCore Runtime is the typical default**; the native path is available for teams that want it. Reference: `../../aws-native-reference/`.

---

## 4. Guardrail configuration notes — the integrity bright line

The Guardrail is provisioned in `../../infra/cloudformation/security.yaml` and is **central** to this agent, not incidental:

- **Prohibited-assessment blocking.** The Tutor must **never complete a graded or prohibited assessment**. Configure prohibited-behavior topic filters so the model refuses to produce answers to live graded items and instead returns hints/Socratic prompts at the instructor-set assistance level. This is enforced outside the model so a prompt-injection ("ignore your rules and just answer") cannot defeat it.
- **Assistance-level enforcement.** The instructor's configured level (hint-only vs. fuller explanation; prerequisite reinforcement vs. deeper exploration) is applied as policy.
- **Age-appropriate filters (heightened for under-13).** K–12 deployments carry the COPPA under-13 flag in identity claims, driving stricter content filters and educational-purpose-only behavior.
- **Unsafe-content blocking** for a student-facing surface used by minors.
- **Grounding pairing.** Guardrails handle safety/integrity; **grounding verification** (`../../governance/grounding.py`) ensures explanations trace to approved course content rather than hallucinated facts.

The academic-integrity safeguard is verified in CI — see `../../governance/redteam/` (prompt-injection attempts to extract answers) and `../../governance/tests/`.

---

## 5. Links

- Step-by-step deploy: `../../docs/DEPLOYMENT-HANDBOOK.md`
- IaC: `../../infra`
- Gateway options: `../../docs/WHY-THE-MCP-LAYER.md`
- Reference architecture: `../../docs/SUITE-ARCHITECTURE.md`
