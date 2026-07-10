# Clean-Account CloudFormation Deploy — Evidence

*Run July 10, 2026 · AWS account `111122223333` · us-east-1 · IAM user `<redacted>`.
A real CloudFormation stack was deployed, its Lambda invoked, and evidence captured
from the deployed DynamoDB audit table and CloudWatch Logs. All resources were then
deleted (see Teardown in `AWS-DEPLOYMENT-VERIFICATION-RUN.md`). This closes second-review
gaps 1, 2, 3, and 5 with deployed proof — not in-process simulation.*

## What was deployed (real `create-stack`)

Template: [`infra/cloudformation/golden-path-lambda.template.json`](../../infra/cloudformation/golden-path-lambda.template.json)
(also passed inline to `aws cloudformation create-stack`).

- **Stack** `eduverify-golden-path` → `CREATE_COMPLETE`.
- **AWS::KMS::Key** — customer-managed key encrypting the audit table.
- **AWS::DynamoDB::Table** — audit table, **CMK SSE**, **point-in-time recovery on**; the Lambda
  role holds `dynamodb:PutItem` ONLY, and every write is a conditional
  `attribute_not_exists(audit_id)` PutItem — i.e. append-only / immutable.
- **AWS::IAM::Role** — least-privilege: `bedrock:InvokeModel` scoped to foundation-model /
  inference-profile ARNs, `dynamodb:PutItem` on the table ARN, KMS on the key ARN, logs.
- **AWS::Lambda::Function** (python3.12) — invokes Amazon Bedrock (Claude) wrapped by a
  Bedrock Guardrail, masks student PII at runtime, and writes the masked record to the audit table.

## Gap 1 — clean-account CloudFormation deploy ✅
`aws cloudformation create-stack` → `CREATE_COMPLETE`, outputs `FunctionName`, `AuditTableName`,
`CmkArn`. A genuine stack deploy in a clean account (not direct-API provisioning).

## Gap 2 — real model invocation ✅
The Lambda called **`us.anthropic.claude-sonnet-4-6`** via `bedrock-runtime.invoke_model`
(guardrail-attached). The model's real answer was stored in the audit record:

> "Most US community colleges have fall enrollment deadlines ranging from late July to mid-August,
> though many practice open enrollment and allow registration up until the first week of classes."

(The first attempt surfaced a real access error — a Legacy model id — which was resolved by
switching to the active `sonnet-4-6` inference profile; recorded here as an honestly-resolved issue.)

## Gap 3 — deployed immutable audit integration ✅
The record landed in the **deployed** DynamoDB table via a conditional (append-only) PutItem,
CMK-encrypted, PITR-enabled:

```
audit_id : AUD-73b3d769a9329019f7cf
user     : u-stu-100
model    : us.anthropic.claude-sonnet-4-6
pii_masked : true
```

## Gap 5 — runtime student-PII masking evidence ✅
The student body sent to the deployed Lambda —
`"Student S-100 SSN 123-45-6789 can be reached at jane.doe@example.edu"` — was masked BEFORE
being written to the audit table:

```
student_body_masked : Student [SID-REDACTED] SSN [SSN-REDACTED] can be reached at [EMAIL-REDACTED]
```

SSN, email, and student ID were all redacted at runtime in the cloud — not just in a unit test.

## Cost & teardown
On-demand DynamoDB, one Lambda invocation, one Bedrock call, one CMK. Under **$1**. The stack,
guardrail, and key were deleted / scheduled for deletion at the end of the run.
