# Deployment Handbook
### EDU AI Agent Suite — From an Empty AWS Account to a Running, Governed, Human-Gated Agent

> **This is a deployable accelerator, not a certified product.** Following this handbook end-to-end gives you **one governed, human-gated agent running in a customer-isolated AWS environment** — with deny-by-default authorization, student-PII masking, a framework-enforced human-in-the-loop (HITL) gate, and an append-only audit trail. It does **not** give you a FERPA-certified, accessibility-conformance-tested, penetration-tested production system. The customer must harden, validate, security-review, and accept accountability for the deployment before it touches a live student record. The "customer must configure / harden" callouts throughout mark where that responsibility sits.

**Recommended first deployment: Agent 01 — Student & Family Services Concierge.** It is the most visible to the most users, the lowest decision-risk, and the easiest to measure. The platform controls you build here (gateway, identity, audit, HITL framework) are shared — Agents 02–08 inherit them. See `SOLUTION-FIELD-GUIDE.md` for the "land with 01, expand to the portfolio" motion.

This handbook assumes the six-layer architecture in `docs/SUITE-ARCHITECTURE.md` and the gateway model in `docs/WHY-THE-MCP-LAYER.md`. CloudFormation is the **primary** deploy path; Terraform parity lives in `infra/terraform/`.

---

## Prerequisites

Before Step 1, have the following in place.

| Item | Detail | Owner |
|---|---|---|
| **AWS account** | A clean account (or a dedicated OU/account per environment — dev/staging/prod). One KMS customer-managed key per environment is required, so keep environments isolated. | SI / customer |
| **IAM permissions** | A deploying principal able to create IAM roles, KMS keys, Cognito/IAM Identity Center resources, DynamoDB, S3 (with Object Lock), Step Functions, Lambda, VPC, and Bedrock AgentCore resources. CloudFormation deploys named IAM roles, so you will pass `CAPABILITY_NAMED_IAM`. | SI / customer |
| **AWS CLI v2** | Installed and configured (`aws configure`) for the target account and region. Verify with `aws sts get-caller-identity`. | SI |
| **Region selection** | Choose a region that satisfies the institution's **data-residency / state data-localization** obligations. Several states require student data to remain in-region. Confirm Bedrock model availability and AgentCore availability in that region before committing. | **Customer must confirm** |
| **Naming convention** | Decide a consistent prefix (e.g., `edu-concierge-prod`) for stacks, roles, buckets, and the KMS key alias. Used throughout. | SI |
| **Template staging bucket** | An S3 bucket to hold the nested CloudFormation templates (`TemplateBaseUrl`). Versioning on; encrypted; access restricted. | SI |
| **Lambda code bucket** | An S3 bucket to hold packaged Lambda deployment artifacts (`LambdaCodeBucket`) for the native deploy path. | SI |
| **IdP metadata URL** | The institution's identity-provider SAML/OIDC metadata endpoint (`IdpMetadataUrl`) for Okta, Microsoft Entra, Google Workspace, or AD. | **Customer must provide** |

> **Callout — customer must configure.** Region choice, IdP metadata, and the FERPA/COPPA/PPRA program that governs which roles may see which data are customer responsibilities and must be settled before deployment, not after.

---

## Step 1 — Enable Amazon Bedrock model access (Claude)

All inference runs **in-account on Amazon Bedrock (Claude models)**. After student-PII masking, the Bedrock API never carries student PII outside the customer's VPC — there is no PII egress to a third-party inference endpoint.

**Console:**
1. Open the **Amazon Bedrock** console in your target region.
2. Go to **Model access** → **Manage model access** (or **Modify model access**).
3. Request access to the **Anthropic Claude** models the agent uses.
4. Submit and wait for the status to read **Access granted**.

**CLI (verify access):**
```bash
aws bedrock list-foundation-models \
  --region <region> \
  --query "modelSummaries[?providerName=='Anthropic'].modelId"
```

> **Callout — customer must configure.** Attach a **model-access IAM policy** that restricts `bedrock:InvokeModel` to the specific Claude model ARNs the agent role needs — least-privilege, not blanket Bedrock access. Confirm inference stays in-region and within the VPC (Bedrock via VPC endpoint, per `network.yaml`).

---

## Step 2 — Configure a Bedrock Guardrail

A **Bedrock Guardrail** runs on **every LLM call automatically** (Layer 5), supplementing — never replacing — Layer 3 authorization. It enforces:

- **PII denial** — blocks student identifiers from prompts/completions.
- **Age-appropriate content** for student-facing surfaces, heightened for **minors and under-13 learners per COPPA**.
- **Prohibited-behavior topic filters** — e.g., completing a prohibited assessment for a student, plus institution-defined disallowed topics.

`infra/cloudformation/security.yaml` provisions a **reference Guardrail**. It is a starting point, not a finished safety policy.

> **Callout — customer must harden.** Tune the Guardrail to the institution's **student population** — particularly the under-13 (COPPA) configuration, age-appropriateness thresholds, and the prohibited-topic set. Test it against representative student inputs before any pilot. Guardrail tuning is explicitly customer-owned (see `governance/README.md` §5).

**CLI (inspect the provisioned Guardrail after Step 4):**
```bash
aws bedrock get-guardrail --guardrail-identifier <guardrail-id> --region <region>
```

---

## Step 3 — Identity & IdP federation

Identity is federated from the **institution's own IdP**; the platform does not own user accounts. Authorization happens at Layer 3 against the **verified human identity** behind every request.

1. **Provision the identity substrate.** `security.yaml` creates either an **Amazon Cognito** user pool + identity pool, or wires **IAM Identity Center**, depending on the institution's standard.
2. **Federate the institution's IdP** via **SAML or OIDC**, using the `IdpMetadataUrl` parameter (Okta / Microsoft Entra / Google Workspace / Active Directory).
3. **Map the role attribute.** The platform reads a `custom:edu_role` attribute carrying one of: **student, guardian, educator, counselor, administrator**. Map the institution's IdP groups → these roles.
4. **Carry rights-transfer state in the claims.** FERPA rights transfer to the student at **age 18 / postsecondary enrollment**. The IdP must carry age-of-majority / rights-transfer state in the token claims so a **guardian** role is correctly scoped — a parent agent must not surface records the parent no longer has a right to.

**CLI (example — confirm the SAML identity provider after deploy):**
```bash
aws cognito-idp describe-identity-provider \
  --user-pool-id <pool-id> \
  --provider-name <idp-name> \
  --region <region>
```

> **Callout — customer must configure.** **IdP integration and role mapping are customer-owned.** Guardian-relationship modeling, group→role mapping, and the age-of-majority / FERPA rights-transfer logic must be implemented and validated by the institution. The gateway can only enforce what the claims correctly assert.

---

## Step 3.5 — Build the agent runtime artifacts (do this before Step 4)

Step 4 consumes a built artifact: a **container image URI** (container path) or **packaged Lambda zips**
(native path). The scripts in `scripts/` produce them. **Prove the artifact locally first** — no docker
or AWS needed:

```bash
scripts/local_smoke.sh 01-student-family-concierge      # starts the runtime, checks /ping + /invocations
```

**Container path (recommended — cleanest, and what `demo-in-a-box.yaml` uses):**
```bash
IMAGE=$(scripts/build_and_push_image.sh --agent 01-student-family-concierge --region <region> \
        | sed -n 's/^ContainerImageUri=//p')
# IMAGE is the ARM64 ECR image URI -> pass to Step 4 as ContainerImageUri (DeployMode=container)
```

**Native path (Step Functions + Lambda + `waitForTaskToken` HITL gate):**
```bash
scripts/package_lambdas.sh --agent 01-student-family-concierge \
  --bucket <lambda-code-bucket> --agent-id 01-concierge --region <region>
# produces & uploads core/policy_gate/hitl_enqueue/finalize.zip under lambdas/01-concierge/
```

> **Fully turnkey demo:** for a POC workshop, `infra/cloudformation/demo-in-a-box.yaml` stands up Agent 01
> on **ECS Fargate behind an ALB** from the image above — a running URL with no IdP/SoR wiring. See
> `scripts/README.md`.

> **Authoring a NEW agent (not just deploying one)?** Follow `docs/CREATE-A-NEW-AGENT.md` first — it covers
> registering tool grants, the LangGraph workflow, prompts/manifest, and tests. A new agent inherits this
> entire deployment path unchanged.

`scripts/deploy.sh` wraps Step 4 below into a single command once the artifact exists.

---

## Step 4 — Stage and deploy CloudFormation

CloudFormation is the primary path. `quickstart.yaml` is the **master template** and **nests** the others.
`scripts/deploy.sh` runs 4.1–4.3 for you; the manual steps are documented here for transparency.

**4.1 Stage the nested templates** to the `TemplateBaseUrl` bucket:
```bash
aws s3 cp infra/cloudformation/ s3://<template-bucket>/cfn/ \
  --recursive --exclude "*" --include "*.yaml"
# TemplateBaseUrl = https://<template-bucket>.s3.<region>.amazonaws.com/cfn
```

**4.2 Package Lambda code** to the `LambdaCodeBucket` (native deploy path) — produced in Step 3.5 by
`scripts/package_lambdas.sh` (which also uploads when `--bucket` is given). To upload manually:
```bash
aws s3 cp ./build/lambda/01-concierge/ s3://<lambda-code-bucket>/lambdas/01-concierge/ --recursive
```

**4.3 Deploy the master stack** with parameters:
```bash
aws cloudformation deploy \
  --region <region> \
  --stack-name edu-concierge-prod \
  --template-file infra/cloudformation/quickstart.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    Environment=prod \
    AgentId=01-concierge \
    DeployMode=native \
    TemplateBaseUrl=https://<template-bucket>.s3.<region>.amazonaws.com/cfn \
    LambdaCodeBucket=<lambda-code-bucket> \
    IdpMetadataUrl=https://<idp-host>/app/<id>/sso/saml/metadata
```

Equivalent `create-stack` form:
```bash
aws cloudformation create-stack \
  --region <region> \
  --stack-name edu-concierge-prod \
  --template-url https://<template-bucket>.s3.<region>.amazonaws.com/cfn/quickstart.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameters \
    ParameterKey=Environment,ParameterValue=prod \
    ParameterKey=AgentId,ParameterValue=01-concierge \
    ParameterKey=DeployMode,ParameterValue=native \
    ParameterKey=TemplateBaseUrl,ParameterValue=https://<template-bucket>.s3.<region>.amazonaws.com/cfn \
    ParameterKey=LambdaCodeBucket,ParameterValue=<lambda-code-bucket> \
    ParameterKey=IdpMetadataUrl,ParameterValue=https://<idp-host>/app/<id>/sso/saml/metadata
```

> **`CAPABILITY_NAMED_IAM` is required** because the stack creates named IAM roles (notably the least-privilege agent role).

**Master parameters:**

| Parameter | Purpose |
|---|---|
| `Environment` | dev / staging / prod — drives naming and the **per-environment KMS key**. |
| `AgentId` | Which of the eight agents this stack deploys (e.g., `01-concierge`). |
| `DeployMode` | `native` (Step Functions + Lambda + Strands) or `container` (AgentCore Runtime). |
| `TemplateBaseUrl` | S3 base URL for the nested templates. |
| `LambdaCodeBucket` | S3 bucket holding packaged Lambda artifacts. |
| `IdpMetadataUrl` | Institution IdP SAML/OIDC metadata endpoint. |

**What each nested stack creates:**

| Nested template | Creates |
|---|---|
| `network.yaml` | VPC, subnets, NAT, security groups; **no public inbound**; Bedrock via VPC endpoint; inter-service traffic stays in-VPC. |
| `security.yaml` | **KMS customer-managed key** (one per environment, key policy restricted to the agent role), the **Bedrock Guardrail** (Step 2), **Cognito / IAM Identity Center** IdP federation (Step 3), and the **least-privilege agent IAM role**. |
| `data.yaml` | **Append-only DynamoDB audit table**, **HITL queue table**, **S3 Object Lock (COMPLIANCE mode) WORM** store, governed data-lake references. |
| `agentcore-gateway.yaml` | **Bedrock AgentCore Gateway + AgentCore Identity** — one target per system of record. |
| `agent-service.yaml` | Per-agent runtime: **native** path = Step Functions + Lambdas with a `waitForTaskToken` HITL gate; **container** path = AgentCore Runtime (ARM64, `/invocations` + `/ping`). Selected by `DeployMode`. |

**The `DeployMode` switch:** `native` provisions the deterministic-core + Strands + Step Functions path (best for explicit, inspectable orchestration and the `waitForTaskToken` gate); `container` provisions the AgentCore Runtime container lift (ARM64 container on port 8080). The enforcement semantics are identical either way. See `aws-native-reference/README.md`.

---

## Step 5 — Register AgentCore Gateway targets

The gateway is the governed front door: **no agent has a direct network path to a system of record.** Register **one target per system of record**.

1. **Register a target for each SoR** the agent uses (Agent 01 Concierge: **SIS**, **CRM**, **scheduling**; other agents add **LMS**, **ITSM**, **ERP** as needed).
2. **Wire the authorizer** to Cognito / AgentCore Identity so each call carries the verified IdP claims and role.
3. **Tool names are `connector_kind.operation`** (e.g., `sis.get_student_schedule`, `crm.create_advising_case`) and **map 1:1 to AgentCore Gateway targets**.
4. **Scoped tokens.** The gateway mints **short-lived, single-purpose** credentials per call via AgentCore Identity — **no standing service accounts**.
5. **Start in fixture/demo mode**, then point targets at **live connectors only after validation** against the live systems.

> **Callout — placeholders in CFN.** Some AgentCore Gateway resource types are represented in `agentcore-gateway.yaml` as **custom resources / placeholders** pending the customer's region and AgentCore configuration. Treat target registration as a customer-completed step, not a fully turnkey one.

> **Callout — customer must validate.** **Connector validation against live SIS/LMS/CRM/ITSM is customer-owned.** Do not point a target at a live system of record until the connector has been validated and the read/write field scoping confirmed (no redisclosure).

---

## Step 6 — Secrets

Connector credentials are **never embedded in the agent** and there are **no standing master keys** in the agent.

1. Store each connector's credentials in **AWS Secrets Manager**.
2. Encrypt each secret with the **environment KMS customer-managed key**.
3. Grant the **least-privilege agent role** read access to **only** the specific secret ARNs it needs.
4. The agent resolves a secret at call time; the short-lived scoped token (Step 5) — not a stored master credential — authorizes the downstream action.

```bash
aws secretsmanager create-secret \
  --name edu-concierge-prod/sis \
  --kms-key-id <env-cmk-arn> \
  --secret-string file://sis-credentials.json \
  --region <region>
```

> **Callout — customer must configure.** Credential rotation policy and the exact least-privilege secret grants are customer responsibilities.

---

## Step 7 — Step Functions smoke test (native path)

Confirm the deployed agent runs and writes audit on a **benign read**.

1. Invoke the agent's Step Functions state machine with a **benign read** in fixture mode — e.g., a Concierge **check-status** request (`sis.get_student_schedule` or a financial-aid status check) carrying valid IdP claims for a `student` role.
```bash
aws stepfunctions start-execution \
  --state-machine-arn <agent-state-machine-arn> \
  --name smoke-$(date +%s) \
  --input '{"agent":"01-concierge","tool":"sis.get_student_schedule","claims":{"sub":"demo-student","custom:edu_role":"student"},"mode":"fixture"}' \
  --region <region>
```
2. Confirm the execution reaches a successful terminal state (`describe-execution`).
3. **Confirm an audit record was written** to the append-only DynamoDB audit table with an `ALLOW` outcome and lineage to the system of record:
```bash
aws dynamodb query \
  --table-name <audit-table> \
  --key-condition-expression "agent_id = :a" \
  --expression-attribute-values '{":a":{"S":"01-concierge"}}' \
  --region <region>
```

A clean read that produces an `ALLOW` audit row confirms identity → authorization → connector → audit is wired correctly.

---

## Step 8 — HITL approval walkthrough

Now confirm the **bright line**: a consequential action cannot complete without a named human.

1. **Trigger a consequential action** — e.g., `crm.draft_family_message` finalize, or another **write** tool. The gateway classifies it high-risk and the **`waitForTaskToken` gate fires**; the gateway returns **`PENDING_APPROVAL`** rather than acting.
2. **Confirm the item appears in the HITL queue table** (DynamoDB), holding the draft and the compliance report, awaiting a reviewer.
3. **A reviewer in the correct role** (e.g., counselor/administrator for a family message) reviews and **approves**. The approval **binds the reviewer's identity** into the audit record.
4. On approval, the gateway **mints the scoped write token** and the action completes; the audit row transitions to `ALLOW` with the bound reviewer identity and lineage to the SoR.
5. Verify the reverse: with **no** valid approval record, the execution stays suspended and the write token is never minted.

See `runbooks/HITL-QUEUE-OPERATIONS.md` for queue monitoring, reviewer assignment, escalation, and SLA operations.

> **The bright line stays visible.** Agents never autonomously decide **grades, admissions, discipline, financial aid, special-education eligibility, or student placement.** The HITL gate is **framework-enforced** (not documented-only) and is tested in `governance/tests/test_hitl_gates.py`.

---

## Step 9 — Validation checklist

Work through this before any pilot with real users. Each unchecked item is a go-live blocker.

- [ ] **Bedrock model access** granted; inference confirmed in-region, in-account, no PII egress (Step 1).
- [ ] **Guardrail attached and tested** against representative student inputs, including under-13 (COPPA) configuration (Step 2).
- [ ] **IdP federation + role mapping** working; `custom:edu_role` populated for student/guardian/educator/counselor/administrator; age-of-majority / rights-transfer carried in claims (Step 3).
- [ ] **KMS customer-managed key per environment**; key policy restricted to the agent role.
- [ ] **Audit table append-only** — `UpdateItem` and `DeleteItem` **denied** on the audit partition; **PITR** enabled.
- [ ] **S3 Object Lock COMPLIANCE mode (WORM)** enabled on the document/audit-snapshot store.
- [ ] **Gateway deny-by-default verified** — an unauthorized tool/role combination returns `DENY` and is audited.
- [ ] **PII masking active** before any prompt **and** before any audit record is written.
- [ ] **HITL gate cannot be bypassed** — confirmed by walkthrough (Step 8) and by `governance/tests/test_hitl_gates.py`.
- [ ] **Grounding, eval, and fairness checks in CI** — `governance/grounding.py`, `governance/evals/`, `governance/fairness/` passing.
- [ ] **CloudWatch alarms** configured for **HITL queue depth**, **approval latency**, and **error rate**.
- [ ] **CloudTrail on**, feeding the unified compliance record.
- [ ] **WCAG 2.2 AA conformance tested** on any deployed UI surface.
- [ ] **Connectors validated against live systems** (no longer fixture mode) with read/write field scoping confirmed.
- [ ] **State student-privacy law and data-residency mapped** to region/VPC, retention windows, and consent configuration.

> **Callout — customer accepts accountability.** This accelerator provides the control *design*. The customer operationalizes, validates, security-reviews, and accepts accountability for the deployment (see `governance/README.md` §5 and the README compliance disclaimer).

---

## Appendix — Per-agent deploy notes

All eight agents share the same platform skeleton (gateway, identity, audit, HITL framework). Per-agent differences are the primary systems, the consequential actions that fire the HITL gate, and governance intensity. **The bright line applies to every agent.**

| # | Agent | Primary systems | Key approval / HITL actions | Governance intensity |
|---|---|---|---|---|
| **01** | Student & Family Services Concierge | SIS, CRM, scheduling, Amazon Connect | Send family message; open advising case; submit form | **Lower** — best-first |
| **03** | Educator Copilot | LMS, curriculum/standards store, SIS (roster) | Publish LMS content; create assignment; post announcement | **Lower** — best-first |
| **07** | Document & Accessibility Services | SIS/CRM, document store, Textract/Transcribe/Translate/Polly | Write extracted enrollment data to SIS; finalize accessible version of consequential material | **Lower** — best-first |
| **08** | Operations Service Desk | ITSM (ServiceNow/Jira), HR/ERP, procurement | Submit/resolve ticket; initiate scoped admin workflow | **Lower** — best-first |
| **02** | Personalized Tutor & Study Companion | LMS, course content store, knowledge base | Instructor-controlled scope changes; under-13 (COPPA) handling | **Higher** — touches learning |
| **04** | Assessment, Grading & Feedback | LMS/assessment store, rubric service | **Never decides final grades** — drafts feedback; low-confidence routing to educator | **Higher** — grading integrity |
| **05** | Student Success & Proactive Engagement | SIS, LMS, attendance, advising/case mgmt, comms | Send outreach; open counselor case; **no PPRA-protected inference**; fairness-monitored | **Higher** — outcomes + equity |
| **06** | Academic, College & Career Pathway Navigator | SIS, degree-audit/rules engine, labor-market data | Presents options/recommendations — **placement is human** | **Higher** — pathway/placement |

**Deploy 01/03/07/08 first** (broad visibility, lower decision-risk, measurable return), then expand to **02/04/05/06** (stronger evaluation, educator oversight, bias testing, evidence retention, escalation). Across all of them, agents draft, retrieve, analyze, recommend, and initiate low-risk workflows — **a named, authorized human owns every consequential decision.**

---

## Cross-links

- Six-layer architecture and AWS service mapping: `docs/SUITE-ARCHITECTURE.md`
- Why the gateway comes first + three implementation options: `docs/WHY-THE-MCP-LAYER.md`
- EDU compliance spine and the bright line: `governance/README.md`
- Gateway reference logic: `platform_core/edu_agent_platform/mcp_gateway/README.md`
- Native rebuild + container contract: `aws-native-reference/README.md`
- **Build & deploy scripts** (build image, package Lambdas, deploy, local smoke): `scripts/README.md`
- **Author a new agent**: `docs/CREATE-A-NEW-AGENT.md`
- **Turnkey POC demo** (ECS Fargate + ALB): `infra/cloudformation/demo-in-a-box.yaml`
- AWS prerequisites & funding (region/quotas/model access, MAP/POA): `docs/AWS-FUNDING-AND-PREREQUISITES.md`
- Shared-responsibility matrix · Well-Architected GenAI Lens: `docs/SHARED-RESPONSIBILITY-MATRIX.md`, `docs/WELL-ARCHITECTED-GENAI-LENS.md`
- Infrastructure templates: `infra/cloudformation/` (`quickstart.yaml`, `network.yaml`, `security.yaml`, `data.yaml`, `agentcore-gateway.yaml`, `agent-service.yaml`); Terraform parity in `infra/terraform/`
- Operations runbooks: `runbooks/` (HITL queue operations, incident response, key rotation)
