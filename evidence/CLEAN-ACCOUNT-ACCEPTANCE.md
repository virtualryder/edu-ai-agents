# Clean-Account Acceptance Report — EDU AI Agents (resource-level verification)

Sanitized evidence for the AWS verification run described in
`docs/AWS-DEPLOYMENT-VERIFICATION-RUN.md`. Validation account ID and IAM user are redacted;
raw CLI JSON is available on request. All verification queries were read-only.

**Account:** `<VALIDATION-ACCOUNT-ID>` · **Region:** us-east-1 · **Run date:** 2026-06-30 · **Independently re-verified:** 2026-07-07 via AWS CLI.

## 1. What this run was — and was not

This suite's verification was **direct-API resource provisioning, not a CloudFormation stack
deploy** (documented honestly in the run doc). Resources provisioned, exercised, and deleted:
KMS CMK; DynamoDB audit table (CMK SSE, PITR, deletion protection); S3 Object Lock GOVERNANCE
bucket; Cognito user pool carrying the `custom:edu_role` / `custom:under_13` /
`custom:rights_transferred` claims (the FERPA/COPPA enforcement inputs); Bedrock Guardrail
(verified `GUARDRAIL_INTERVENED` on an SSN prompt). Total cost < $1.

## 2. Independent re-verification (2026-07-07)

- **No `edu-*` CloudFormation stacks exist in the account's 90-day deleted-stack history** —
  consistent with the repo's claim that CFN-from-template was not exercised (no overclaim).
- The `eduverify` KMS key is gone, consistent with its documented auto-delete on 2026-07-06
  (7-day deletion window from the Jun 30 run).
- Zero `edu*` DynamoDB tables, S3 buckets, or Cognito pools remain.

## 3. Outstanding for full stack-level acceptance

A clean-account `quickstart.yaml` CloudFormation deploy (README Gap 1) remains open — the
templates lint clean (cfn-lint in CI) but a full-stack deploy has not been executed. Until then,
the README banner correctly describes this as resource-level verification. Offline suite:
120 tests green as of 2026-07-07 (`make test`).

## 4. Method

Read-only CLI: `cloudformation list-stacks --stack-status-filter DELETE_COMPLETE`,
`kms list-keys/describe-key`, `dynamodb list-tables`, `s3api list-buckets`,
`cognito-idp list-user-pools`. Portfolio-level export:
`Projects-DR/evidence/AWS-CLEAN-ACCOUNT-EVIDENCE-2026-07-07.md` (kept outside the repo).
