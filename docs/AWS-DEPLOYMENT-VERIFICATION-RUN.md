# AWS Deployment Verification Run

*Run June 30, 2026 against AWS account `<VALIDATION-ACCOUNT-ID>` (us-east-1), IAM user `<VALIDATION-IAM-USER>`.
(Real account ID and IAM username redacted; evidence available on request.)
This records a REAL provisioning verification of the suite's signature resources, and an
honest account of what could and could not be exercised in that environment. All
resources created here were deleted at the end of the run (see Teardown).*

## What was verified (provisioned for real, then deleted)

| Suite control | Resource created | Verified | Result |
|---|---|---|---|
| Encryption foundation | KMS customer-managed key (CMK) | key Enabled, `ENCRYPT_DECRYPT` | ✅ created |
| Tamper-evident audit | DynamoDB table, CMK SSE, deletion protection, **PITR enabled** | `TableStatus=ACTIVE`, `SSE=ENABLED`, PITR `ENABLED` | ✅ created + active |
| WORM retention | S3 bucket, **Object Lock GOVERNANCE (1-day default)**, CMK SSE + bucket key, full public-access block | bucket created, lock + encryption + PAB applied | ✅ created |
| Federated identity | Cognito user pool with the suite's **custom EDU claims** (`custom:edu_role`, `custom:under_13`, `custom:rights_transferred`) + app-client schema | pool created with all three custom attributes | ✅ created |
| Model safety | Bedrock Guardrail (content filters HATE/PROMPT_ATTACK + PII: EMAIL anonymize, SSN block) | **`apply-guardrail` on an SSN input returned `GUARDRAIL_INTERVENED`** | ✅ created + **functionally blocks PII** |
| Model layer | Amazon Bedrock model access | Claude Sonnet 4 / 4.5 / 4.6 listed in-region | ✅ available |

Every resource type the agents depend on provisioned without error in this account, and
two controls were exercised functionally (the guardrail actually blocked an SSN; the audit
table came up ACTIVE with CMK encryption + point-in-time recovery).

## What could NOT be exercised here (environment limits + customer inputs)

- **CloudFormation-from-template was blocked by the tooling**, not by the templates: the AWS
  CLI bridge in this environment only reads files from its own sandboxed working directory
  and cannot read the repo's `infra/cloudformation/*.yaml` (and the unrestricted-file-access
  override is not settable here). So resources were provisioned by direct API calls that
  mirror the templates' configurations, rather than by `create-stack`. Template *structure*
  remains validated by `cfn-lint` (blocking in CI) and the permissive-loader parse in
  `AWS-DEPLOYMENT-VALIDATION.md`.
- **The full nested agent stack** additionally needs customer inputs that aren't available in
  this environment: real **IdP SAML/OIDC metadata** for Cognito federation, **Lambda zip
  artifacts** staged to S3, a container **image in ECR** (container path), and the
  **AgentCore control-plane** provisioning (the `bedrock-agentcore-control` API the
  provisioner calls — fails closed if absent). Those, plus NAT/Fargate cost items, are the
  clean-account deployment work tracked as customer-engagement in
  `SECOND-REVIEW-ACTION-PLAN.md` (Gap 1).

## Teardown (confirmed — no lingering billable resources)

DynamoDB table deleted · S3 WORM bucket deleted · Cognito user pool deleted · Bedrock
Guardrail deleted · KMS CMK **scheduled for deletion** (7-day minimum window; auto-deletes
2026-07-06; ~\$0.23 prorated — the only unavoidable residual). Post-teardown sweeps returned
empty for buckets, tables, user pools, and guardrails tagged/﻿named `eduverify`.

**Net AWS charge for this verification: under \$1** (on-demand DynamoDB idle, empty S3,
Cognito free tier, one Guardrail for minutes, KMS key prorated for its mandatory window).
