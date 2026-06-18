# Terraform Parity — EDU AI Agent Suite

> **Reference / accelerator IaC.** This is Terraform parity for platform teams
> standardized on Terraform. It mirrors the CloudFormation primary path
> (`infra/cloudformation/`) with an **identical resource topology** — the same
> VPC, KMS customer-managed key, Bedrock Guardrail, Cognito + IdP federation,
> append-only DynamoDB audit table, HITL approval-queue table, S3 Object Lock
> (COMPLIANCE) WORM store, least-privilege agent IAM role, and Step Functions
> state machine with a `waitForTaskToken` human-in-the-loop (HITL) gate. The
> customer must review, harden, security-review, and validate it before
> production use, exactly as with the CloudFormation path.

CloudFormation is the **primary** deploy path documented in
`docs/DEPLOYMENT-HANDBOOK.md`. This directory exists so an institution whose
platform team operates Terraform can provision the same governed environment
without learning a second IaC tool. **The controls are identical; only the
surface syntax differs.**

---

## Parity intent

The point of parity is that the *governance posture is the same* regardless of
IaC tool:

- **Deny-by-default Layer 3 gateway** — `custom:edu_role` drives least-privilege
  role intersection; the agent never exceeds the human.
- **Framework-enforced HITL gate** — the `waitForTaskToken` state suspends every
  consequential action until a verified reviewer identity is bound into the
  HITL record. No path to `Finalize` bypasses the gate (the bright line:
  grades, admissions, discipline, financial aid, special-education eligibility,
  student placement).
- **Append-only audit** — the agent role is granted `dynamodb:PutItem` only;
  `UpdateItem`/`DeleteItem` are intentionally absent. PITR is enabled.
- **WORM records** — S3 Object Lock in COMPLIANCE mode; retention cannot be
  shortened.
- **Per-environment KMS CMK** — one customer-managed key per environment;
  losing it loses the data it protects (see `runbooks/DR-RUNBOOK.md`).
- **In-account inference** — Bedrock reached via an interface VPC endpoint; no
  public inbound path to the agent runtime; student PII never egresses the VPC
  after masking.

The reference enforcement logic these resources host is the same Python model
in `platform_core/edu_agent_platform/mcp_gateway/` — readable and testable
without an AWS account.

---

## Resource topology — CloudFormation ↔ Terraform map

| CloudFormation nested stack | Terraform equivalent | Key resources |
|---|---|---|
| `network.yaml` | `main.tf` (NETWORK block) | `aws_vpc`, `aws_subnet` (public/private ×2 AZ), `aws_nat_gateway`, security groups, Bedrock/S3/DynamoDB VPC endpoints |
| `security.yaml` | `main.tf` (SECURITY blocks) | `aws_kms_key` + alias, `aws_bedrock_guardrail` + version, `aws_cognito_user_pool` + IdP + client + identity pool, `aws_iam_role` (least-privilege agent role) |
| `data.yaml` | `main.tf` (DATA blocks) | `aws_dynamodb_table.audit` (append-only, PITR), `aws_dynamodb_table.hitl_queue`, `aws_s3_bucket.worm` + Object Lock COMPLIANCE + versioning + encryption |
| `agentcore-gateway.yaml` | `main.tf` (GATEWAY block) | `aws_ssm_parameter` target specs (one per SoR) + authorizer config — topology-as-IaC, reconciled into AgentCore Gateway by the pipeline / a provisioner |
| `agent-service.yaml` | `main.tf` (AGENT SERVICE block) | `aws_sfn_state_machine.agent` with the `waitForTaskToken` HITL gate (native), or `aws_ssm_parameter.container_contract` (container) |

Outputs in `outputs.tf` mirror the CloudFormation master stack outputs in
`quickstart.yaml`.

---

## Module layout

This reference is intentionally provided as flat root files for readability:

```
infra/terraform/
├── main.tf        # All resources, organized in clearly-labeled blocks that
│                  # map 1:1 to the CloudFormation nested stacks
├── variables.tf   # Mirrors the quickstart.yaml parameter surface
├── outputs.tf     # Mirrors the quickstart.yaml outputs
└── README.md      # This file
```

For a production rollout, a customer would typically refactor these blocks into
child modules (`modules/network`, `modules/security`, `modules/data`,
`modules/gateway`, `modules/agent-service`) and call them from environment
root configurations (`environments/dev`, `environments/prod`) with a remote
backend (S3 + DynamoDB state locking) and per-environment workspaces. The flat
layout here keeps the parity mapping obvious; the module split is a
hardening step, not a logic change.

---

## Usage (reference)

```bash
terraform init

# Plan a native (Step Functions + Lambda) deployment of Agent 01 in dev.
terraform plan \
  -var="environment=dev" \
  -var="agent_id=01-concierge" \
  -var="deploy_mode=native" \
  -var="aws_region=us-east-1" \
  -var="lambda_code_bucket=my-edu-lambda-artifacts" \
  -var="idp_metadata_url=https://idp.example.edu/app/metadata"

terraform apply   # after review
```

Leave `idp_metadata_url` empty to provision the Cognito user pool without
federation for an early demo, then wire the institution IdP during IdP
integration (see `docs/DEPLOYMENT-HANDBOOK.md` step 3).

---

## What the customer still owns

This is a control *design*, not a turnkey product. Before production the
customer must, at minimum:

- Refactor to child modules with a remote, locked state backend.
- Tune the Bedrock Guardrail for their student population (minors / COPPA
  under-13) and validate the PII and topic policies.
- Wire their IdP and own the IdP group → `custom:edu_role` mapping and the
  age-of-majority / FERPA rights-transfer logic.
- Supply the AgentCore Gateway and (container path) AgentCore Runtime
  provisioner that reconciles the SSM topology records into the live services.
- Package and deploy the agent Lambda artifacts (native path).
- Validate connectors against live SIS/LMS/CRM/ITSM systems.
- Confirm the append-only invariant in IAM review, set retention windows to
  their records-retention schedule, and map state student-privacy / data-
  residency obligations to the chosen region.
- Run one NAT gateway per AZ (the reference uses a single NAT).

---

## Related

- `infra/cloudformation/` — the primary deploy path.
- `docs/DEPLOYMENT-HANDBOOK.md` — empty account → running, governed, human-gated agent.
- `docs/SUITE-ARCHITECTURE.md` — six-layer architecture + AWS service mapping.
- `docs/WHY-THE-MCP-LAYER.md` — the three gateway implementation options.
- `platform_core/edu_agent_platform/mcp_gateway/` — the reference enforcement logic.
- `runbooks/` — incident response, DR, HITL queue ops, model-degradation response.
