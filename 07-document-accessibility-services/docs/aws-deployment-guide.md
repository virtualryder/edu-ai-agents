# Agent 07 — AWS Deployment Guide
### Document & Accessibility Services — services, topology, and the two coordinated workflows

> This guide is the agent-specific companion to the suite's step-by-step `../../docs/DEPLOYMENT-HANDBOOK.md` (empty AWS account → running, governed, human-gated agent) and the shared architecture in `../../docs/SUITE-ARCHITECTURE.md`. It covers what is distinct about Agent 07: two coordinated Step Functions state machines, confidence thresholds by field sensitivity, and immutable retention of the original plus the extracted version.

---

## 1. Services used

| Architecture role | AWS service | Agent 07 use |
|---|---|---|
| Secure intake | **Amazon S3** | Encrypted intake bucket for submitted documents; event source for the pipeline |
| Classification & extraction | **Amazon Textract** + **Amazon Bedrock Data Automation** | Document-type classification; field extraction including handwriting and PDF |
| Deterministic validation | **AWS Lambda** | Completeness checks, discrepancy detection, confidence-threshold routing |
| Workflow orchestration | **AWS Step Functions** | Two state machines — document-processing pipeline and accessibility-review workflow |
| Case state | **Amazon DynamoDB** | Per-case state, field-level confidence, review status, lineage to S3 objects |
| Approved writes | **Amazon API Gateway** (tool front door) | SIS/CRM update tools, gateway-authorized and HITL-gated |
| Notifications | **Amazon EventBridge** | Missing-information and review-needed events |
| Immutable retention | **Amazon S3 + Object Lock (COMPLIANCE mode)** | Original submission **and** extracted version, retained on the institution's schedule |
| Translation & speech | **Amazon Translate**, **Amazon Polly**, **Amazon Transcribe** | Multilingual variants, text-to-speech audio, captions/transcripts |
| Inference | **Amazon Bedrock (Claude models)** | Reached over PrivateLink (interface VPC endpoint), not the public internet; direct identifiers masked before inference |
| Content safety + PII | **Amazon Bedrock Guardrails** | PII denial, age-appropriate filters (heightened for minors), prohibited-behavior topic filters |
| Authorization gateway | **Amazon Bedrock AgentCore Gateway** + **AgentCore Identity** | Deny-by-default; least-privilege intersection; short-lived per-call tokens; HITL gate |
| Audit | **Amazon DynamoDB** (append-only) + **AWS CloudTrail** | Who accessed what, on what basis, who approved — FERPA disclosure recordkeeping |
| Encryption | **AWS KMS** (customer-managed key) | At-rest encryption; key policy restricts to the agent role |
| Observability | **Amazon CloudWatch** | HITL queue depth, approval latency, extraction error rate |
| Knowledge base | **Amazon Bedrock Knowledge Bases** | Approved source content for accessibility/multilingual transformation |

---

## 2. Deploy topology

Agent 07 provisions through the shared CloudFormation quick-deploy (`../../infra/cloudformation/`), nested under `quickstart.yaml`:

- `network.yaml` — VPC, subnets, no public inbound; Bedrock and Textract reached via VPC endpoints.
- `security.yaml` — KMS customer-managed key, **Bedrock Guardrail**, Cognito / IAM Identity Center federation, the Agent 07 IAM role.
- `data.yaml` — append-only DynamoDB audit partition, **S3 Object Lock (COMPLIANCE mode)** document bucket, the HITL queue table, and the case-state table.
- `agentcore-gateway.yaml` — AgentCore Gateway + Identity; one target per system of record; the READ/WRITE tools registered with their grants.
- `agent-service.yaml` — the per-agent runtime: the **two Step Functions state machines**, the validation Lambdas, the Textract / Bedrock Data Automation integration, and the EventBridge rules.

`../../infra/terraform/` provides identical resource topology for teams standardized on Terraform.

---

## 3. The two coordinated workflows

Agent 07 is two **distinct Step Functions state machines** that share intake, case state, and the audit trail but never blur their responsibilities.

### 3.1 Document-processing pipeline

```
S3 intake event
  → classify (Textract / Bedrock Data Automation)
  → extract_fields
  → validate completeness + discrepancies (Lambda, deterministic)
  → confidence/sensitivity router
      ├─ above threshold & low-sensitivity → stage SIS update
      └─ low-confidence OR high-sensitivity → HUMAN REVIEW (waitForTaskToken)
  → [on missing items] EventBridge → comms.send_missing_info_request
  → HITL gate (registrar/admin approval, identity bound)
  → sis.commit_record_update (WRITE)
  → Object Lock retention of original + extracted version
```

There is **no path from intake to a committed SIS write that bypasses the HITL gate**. The pipeline prepares the file; the registrar or admissions officer decides. The agent never commits the admissions or enrollment decision itself.

### 3.2 Accessibility-review workflow

```
Approved source content (Bedrock Knowledge Bases / explicit input)
  → render variant(s): Translate · plain-language/reading-level · Polly audio · Transcribe captions · alt text
  → grounding check (no meaning drift from approved source)
  → consequential-material router
      ├─ routine content → release
      └─ individualized plan / legal notice / safety info → HUMAN VERIFICATION (waitForTaskToken)
  → release accessible/multilingual artifact
```

This workflow only transforms **already-approved** content. Human verification is required before any consequential material is released, so the agent can never alter the meaning of a legal notice, a safety instruction, or an individualized plan.

---

## 4. Confidence thresholds by field sensitivity

Routing is a two-axis decision, enforced in the validation Lambda — not left to the model. A field proceeds automatically only when it clears **both** axes.

| Field sensitivity | Examples | Routing rule |
|---|---|---|
| Low | School preference, optional contact fields | Proceed if extraction confidence ≥ threshold |
| Medium | Address, prior school, transfer course titles | Proceed if confidence ≥ raised threshold; otherwise review |
| High | Legal name, date of birth, immunization status, residency basis, income figures | **Always** route to human review, regardless of confidence |

The thresholds are configuration, not code, so an institution can tune them per document type and per enrollment season. Any field that routes to review carries its confidence score and source bounding region into the human-review interface.

---

## 5. Bedrock Guardrail notes

Guardrails run on every LLM call (configured in `security.yaml`), supplementing — never replacing — Layer 3 authorization. For Agent 07 specifically:

- **PII denial** on prompts and outputs; raw student identifiers are masked by the student-PII masker (`../../platform_core/edu_agent_platform/pii_masker/`) before any tool result enters a prompt or audit record.
- **Age-appropriate filters heightened for minors and under-13 learners**, since K–12 intake handles children's data under COPPA.
- **Prompt-injection resistance** — a malicious instruction hidden inside a submitted document or an inbound email cannot grant the agent authority; authorization, the HITL gate, and audit live outside the model.
- **Topic filters** that block non-educational use of intake data (no profiling, no advertising).

---

## 6. Runtime choice — AgentCore Runtime vs Strands + Step Functions

Both paths are first-class, exactly as the canon distinguishes them.

| | AgentCore Runtime (container lift) | Strands + Step Functions (native rebuild) |
|---|---|---|
| Shape | One ARM64 container implementing `/invocations` + `/ping` on port 8080 | Deterministic core as Lambda; Strands Agents SDK for Bedrock inference; Step Functions orchestration |
| HITL gate | AgentCore Gateway human-approval gate | Step Functions `waitForTaskToken` on the review/commit step |
| Best for | Fastest lift of the existing agent graph onto managed runtime | Maximum inspectability; deterministic validation as discrete, testable Lambdas |
| In this repo | `agent-service.yaml` (container target) | `agent-service.yaml` (native path) + `../../aws-native-reference/` |

For Agent 07 the validation logic (completeness, discrepancy detection, confidence routing) is deterministic and benefits from being explicit Lambda functions, which makes the native rebuild a natural fit; the container lift is the faster path to a first pilot. The enforcement semantics are identical either way.

---

## 7. Retention — original + extracted version, immutable

Both the **original submitted document** and the **extracted/structured version** are written to the **S3 + Object Lock (COMPLIANCE mode)** bucket under the institution's retention schedule. COMPLIANCE mode means the objects cannot be deleted or overwritten — by anyone, including the root account — until the retention period elapses, which is what records-retention and audit obligations require. The case-state table in DynamoDB holds lineage pointers to both objects so any later inquiry can reconstruct what was submitted, what was extracted, and what was committed to the SIS.

---

## 8. Where to go next

- Suite step-by-step deploy: `../../docs/DEPLOYMENT-HANDBOOK.md`
- IaC: `../../infra/cloudformation/` and `../../infra/terraform/`
- Architecture reference: `../../docs/SUITE-ARCHITECTURE.md`
- Why the gateway comes first: `../../docs/WHY-THE-MCP-LAYER.md`
- Connector and identity integration: `integration-guide.md`
- Compliance reading: `edu-compliance.md`

---

Maturity: **Demonstrated locally — not AWS-deployed.** This agent runs end-to-end locally (demo mode + tests); a clean-account AWS deploy, real-model invocation, production identity, live connectors, and production sign-off remain customer/engagement work. Authoritative status: [`../../docs/STATUS-MANIFEST.md`](../../docs/STATUS-MANIFEST.md).
