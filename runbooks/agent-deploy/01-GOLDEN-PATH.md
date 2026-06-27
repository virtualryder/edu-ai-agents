# Agent 01 — Golden Path: Empty Account → Working, Observable, Human-Gated Deployment

> **The single end-to-end, copy-pasteable runbook** that takes **Agent 01 (Student & Family Services Concierge)** from a brand-new AWS account to a running, observable, human-gated deployment — with a **verification gate at every step** ("you should see X"). This is the *opinionated golden path*; the comprehensive layer-by-layer reference is [`docs/AWS-DEPLOYMENT-REFERENCE.md`](../../docs/AWS-DEPLOYMENT-REFERENCE.md) and the Concierge-specific detail (tools, bright line, connectors) is in [`01-student-family-concierge.md`](01-student-family-concierge.md).

**This is a deployable accelerator, not a certified product.** Completing this gives you one governed, human-gated agent in a customer-isolated AWS environment: deny-by-default authorization, student-PII masking, a framework-enforced HITL gate, and an append-only audit trail. It does **not** give you a FERPA-certified, accessibility-conformance-tested, pen-tested production system. Harden and security-review before a live student record is touched.

**The bright line (constant):** the agent never autonomously sends a message to a family/student. `comms.send_message` is the consequential action and is **HITL-gated** to a named, authorized human whose identity is bound into the audit record before any write token is minted.

---

## Deploy order at a glance

| # | Step | Provisioned by | Verification gate |
|---|------|----------------|-------------------|
| 0 | Prerequisites | manual / `docs/AWS-FUNDING-AND-PREREQUISITES.md` | account, CLI, CloudTrail on |
| 1 | KMS + network | `quickstart.yaml` → `security.yaml`, `network.yaml` | CMK + VPC exist |
| 2 | Identity (Cognito + IdP + MFA) | `security.yaml` | user pool federates, MFA enforced |
| 3 | Edge (CloudFront + WAF + TLS) | `edge.yaml` | distribution Deployed, WAF attached |
| 4 | Data (WORM + audit + HITL) | `data.yaml` | tables + Object-Lock bucket exist |
| 5 | Package + deploy app | `make golden-path-01` | stack `CREATE_COMPLETE` |
| 6 | AgentCore provisioner | `infra/lambdas/agentcore_provisioner` | gateway endpoint ≠ `PENDING-PROVISION` |
| 7 | Connectors + secrets | manual (Secrets Manager) | secrets resolve under `/edu-agents/<env>/*` |
| 8 | Observability | `observability.yaml` | alarms in `OK`, email subscribed |
| 9 | Smoke tests | manual (4 cases) | allow / deny / HITL / record-authz |
| 10 | Teardown | `cloudformation delete-stack` (+ provisioner) | stacks gone, WORM retained |

Conventions used below: `ENV=test` (the pilot environment — a valid non-prod value in every template's `Environment` `AllowedValues [dev,test,stage,prod]`), `REGION=us-east-1`, `AGENT_ID=01-concierge`, `AGENT=01-student-family-concierge`. Set them once:

```bash
export ENV=test REGION=us-east-1 AGENT_ID=01-concierge AGENT=01-student-family-concierge
export TEMPLATE_BUCKET=my-edu-cfn-bucket      # holds nested templates
export LAMBDA_BUCKET=my-edu-lambda-bucket      # holds packaged Lambda zips
export IDP_METADATA="https://idp.example.edu/app/x/sso/saml/metadata"
```

---

## 0. Prerequisites

> Full pre-flight: [`docs/AWS-FUNDING-AND-PREREQUISITES.md`](../../docs/AWS-FUNDING-AND-PREREQUISITES.md).

- A dedicated AWS account (or isolated OU) for this environment.
- AWS CLI v2 authenticated with admin-equivalent rights for the bootstrap.
- **Bedrock model access** enabled for the Claude models the agent uses (Console → Bedrock → Model access).
- **CloudTrail enabled** account-wide to a dedicated, locked S3 bucket (BLOCKER — the audit story depends on it).
- Two S3 buckets created: one for nested CloudFormation templates (`TEMPLATE_BUCKET`), one for packaged Lambda artifacts (`LAMBDA_BUCKET`).
- `make`, `bash`, `zip`, Python 3.12, and Docker (only if you take the container path) on the deploy host.

```bash
aws sts get-caller-identity                                  # who am I / which account
aws cloudtrail describe-trails --query 'trailList[].Name'    # at least one trail
aws s3 mb s3://$TEMPLATE_BUCKET --region $REGION
aws s3 mb s3://$LAMBDA_BUCKET   --region $REGION
```

**✅ Verification gate.** `get-caller-identity` returns the expected account; `describe-trails` lists ≥1 trail; both buckets exist. Bedrock model access shows **Access granted** for the Claude models.

---

## 1. KMS / network

The master `quickstart.yaml` nests `network.yaml` (VPC, private subnets, NAT, security groups, Bedrock VPC endpoints) and `security.yaml` (per-environment CMK with rotation, Bedrock Guardrail, agent IAM role) in dependency order. Steps 1–5 are deployed by the **one command in Step 5**; you do not deploy them piecemeal. This section is the *verification contract* for the platform layers that come up first.

After the Step-5 deploy completes, confirm the foundation:

```bash
STACK="edu-${AGENT_ID}-${ENV}"
aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='KmsKeyArn'||OutputKey=='VpcId'].{K:OutputKey,V:OutputValue}" --output table
```

**✅ Verification gate.** `KmsKeyArn` resolves to a real `arn:aws:kms:...:key/...`; `VpcId` resolves to a `vpc-...`. `aws kms describe-key --key-id <arn>` shows `KeyRotationStatus`/rotation enabled and `Enabled: true`.

---

## 2. Identity — Cognito + IdP + MFA

`security.yaml` provisions the Cognito user pool that federates the institution IdP and issues the JWT carrying `sub`, `custom:edu_role`, and the COPPA `custom:under_13` claim. You pass the IdP metadata via `IdpMetadataUrl` (the `make` target wires `IDP_METADATA`).

- **MFA:** enforce MFA on the user pool (`MfaConfiguration: ON` or step-up via the IdP). K–12 deployments serve under-13 learners — confirm the COPPA-grade Guardrail profile is selected and that `custom:under_13` drives it.
- **Role claim:** the gateway authorizer reads `custom:edu_role` for the least-privilege intersection. No role claim → deny-by-default.

```bash
UP=$(aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='UserPoolId'].OutputValue" --output text)
aws cognito-idp describe-user-pool --user-pool-id "$UP" --region "$REGION" \
  --query 'UserPool.{Mfa:MfaConfiguration,Name:Name}'
aws cognito-idp list-identity-providers --user-pool-id "$UP" --region "$REGION" \
  --query 'Providers[].ProviderName'
```

**✅ Verification gate.** `UserPoolId` resolves; `MfaConfiguration` is `ON` (or step-up enforced upstream); the institution IdP shows in `list-identity-providers`. A test federated login returns a JWT containing `custom:edu_role`.

---

## 3. Edge — CloudFront + WAF + ACM/TLS

`edge.yaml` provisions the public edge: CloudFront distribution, AWS WAF web ACL (rate-limit + managed rule groups), ACM/TLS, and an optional Route 53 alias. Deploy it pointed at the application origin (the AgentCore Runtime / API front door from Step 5/6).

```bash
aws cloudformation deploy --region "$REGION" \
  --stack-name "edu-edge-${ENV}" \
  --template-file infra/cloudformation/edge.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides Environment="$ENV" \
    OriginDomainName="<runtime-or-api-origin-domain>" \
    AcmCertificateArn="<acm-cert-arn-in-us-east-1>" \
    DomainName="concierge.${ENV}.example.edu" HostedZoneId="<zone-id>"

aws cloudformation describe-stacks --stack-name "edu-edge-${ENV}" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='DistributionId'||OutputKey=='WebAclArn'].{K:OutputKey,V:OutputValue}" --output table
```

**✅ Verification gate.** `DistributionId` resolves; `aws cloudfront get-distribution --id <id> --query 'Distribution.Status'` reads `Deployed`; `WebAclArn` resolves and the WAF is associated. A request to the distribution returns over TLS; an obvious flood is rate-limited.

> Edge ACM certs must live in **us-east-1** for CloudFront regardless of `REGION`.

---

## 4. Data — WORM / audit / HITL

`data.yaml` (nested by `quickstart.yaml`) provisions all three durable stores, all `DeletionPolicy: Retain`: the append-only **AuditTable** (`outcome-index` GSI, PITR, SSE-KMS), the **HitlQueueTable** (`status-index` GSI, TTL, PITR, SSE-KMS), and the **WormBucket** (S3 Object Lock, versioning, SSE-KMS, TLS-only policy). `WormRetentionDays` is **required, no default** — choose it against your records-retention schedule. Use `WormMode=GOVERNANCE` for the pilot, `COMPLIANCE` for production records.

```bash
aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='AuditTableName'||OutputKey=='HitlQueueTableName'||OutputKey=='WormBucketName'].{K:OutputKey,V:OutputValue}" --output table
WORM=$(aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='WormBucketName'].OutputValue" --output text)
aws s3api get-object-lock-configuration --bucket "$WORM"
```

**✅ Verification gate.** All three names resolve; `get-object-lock-configuration` returns `ObjectLockEnabled: Enabled` with your retention `Days`/`Mode`; both DynamoDB tables show SSE-KMS and PITR enabled.

---

## 5. Package + deploy the app — one command

This is the **golden-path one-command deploy** (`Makefile` target `golden-path-01`). It packages the four native-path Lambda zips for Agent 01, uploads them to `LAMBDA_BUCKET`, stages the nested templates, and deploys `quickstart.yaml` with pilot parameters (`ENV=test`, `--mode native`). It is a thin wrapper over `scripts/package_lambdas.sh` + `scripts/deploy.sh`.

```bash
# Dry-run first (no AWS calls) to see exactly what will run:
make -n golden-path-01 LAMBDA_BUCKET=$LAMBDA_BUCKET TEMPLATE_BUCKET=$TEMPLATE_BUCKET IDP_METADATA=$IDP_METADATA

# Then deploy:
make golden-path-01 \
  LAMBDA_BUCKET=$LAMBDA_BUCKET \
  TEMPLATE_BUCKET=$TEMPLATE_BUCKET \
  IDP_METADATA=$IDP_METADATA \
  REGION=$REGION ENV=$ENV AGENT_ID=$AGENT_ID
```

`WormRetentionDays` has no default; if `deploy.sh` does not pass it for your environment, add `--parameter-overrides WormRetentionDays=<n>` (or set it in the script) — CloudFormation will reject the stack without it.

**✅ Verification gate.** `aws cloudformation describe-stacks --stack-name edu-${AGENT_ID}-${ENV} --query "Stacks[0].StackStatus"` returns `CREATE_COMPLETE` (or `UPDATE_COMPLETE`). The four Lambdas `edu-agents-${ENV}-${AGENT_ID}-{core,policy-gate,hitl-enqueue,finalize}` exist, and the Step Functions state machine `edu-agents-${ENV}-${AGENT_ID}` exists.

> At this point the gateway/runtime are still **contracts**: `aws ssm get-parameter --name /edu-agents/$ENV/gateway/endpoint --query 'Parameter.Value' --output text` reads `PENDING-PROVISION`. Step 6 makes them real.

---

## 6. AgentCore provisioner — make the contracts real

The shipped templates expose the AgentCore Gateway and Runtime as custom resources gated by `GatewayCustomResourceServiceToken` / `RuntimeProvisionerServiceToken` (both default `""`, preserving the SSM-contract behaviour). Wiring the **provisioner Lambda** (`infra/lambdas/agentcore_provisioner/`, see its [README](../../infra/lambdas/agentcore_provisioner/README.md)) into those tokens provisions the real AgentCore Gateway (+ targets + JWT authorizer + Identity) and Runtime.

**Fail-closed:** every control-plane call is marked `# TODO(confirm-api)` and wrapped so that **any** error during Create/Update sends `FAILED` to CloudFormation and the stack rolls back — it never records a gateway/runtime that does not exist. Confirm the `bedrock-agentcore-control` operation names against your installed boto3 before first deploy.

```bash
# (a) Package and deploy the provisioner Lambda (zip index.py; handler index.lambda_handler; python3.12).
cd infra/lambdas/agentcore_provisioner && zip -qr /tmp/provisioner.zip index.py && cd -
aws s3 cp /tmp/provisioner.zip s3://$LAMBDA_BUCKET/lambdas/agentcore_provisioner.zip --region $REGION
# Create the function + its scoped execution role (IAM in the module docstring), then capture its ARN:
PROV_ARN="arn:aws:lambda:${REGION}:<acct>:function:edu-agents-${ENV}-agentcore-provisioner"

# (b) Re-deploy quickstart passing the provisioner ARN into BOTH service-token params:
aws cloudformation deploy --region "$REGION" --stack-name "edu-${AGENT_ID}-${ENV}" \
  --template-file infra/cloudformation/quickstart.yaml --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides Environment="$ENV" AgentId="$AGENT_ID" DeployMode=native \
    TemplateBaseUrl="https://${TEMPLATE_BUCKET}.s3.${REGION}.amazonaws.com/cfn" \
    LambdaCodeBucket="$LAMBDA_BUCKET" IdpMetadataUrl="$IDP_METADATA" \
    WormRetentionDays=<n> \
    GatewayCustomResourceServiceToken="$PROV_ARN" \
    RuntimeProvisionerServiceToken="$PROV_ARN"

# (c) Read the resolved gateway endpoint:
aws ssm get-parameter --name "/edu-agents/$ENV/gateway/endpoint" --region "$REGION" \
  --query 'Parameter.Value' --output text
```

**✅ Verification gate.** The gateway endpoint SSM parameter is now a real URL (no longer `PENDING-PROVISION`). The provisioner's CloudWatch log shows `gateway ... provisioned with targets: [...]` and a `SUCCESS` cfnresponse. If anything failed, the stack is in `ROLLBACK_COMPLETE` and the gateway endpoint stays `PENDING-PROVISION` — that is the fail-closed contract working.

> Run the provisioner unit tests any time (no AWS): `make test-provisioner`.

---

## 7. Connectors + secrets

The agent execution role can read `secretsmanager:GetSecretValue` only under `/edu-agents/<env>/*`. Create one secret per system-of-record connector the Concierge uses (SIS, CRM, KB/policy search, comms), encrypted with the env CMK. The gateway targets (SIS/LMS/CRM/ITSM read/write/consequential tool lists) come from the SSM target specs reconciled in Step 6.

```bash
KMS=$(aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='KmsKeyArn'].OutputValue" --output text)
aws secretsmanager create-secret --name "/edu-agents/$ENV/connectors/sis" \
  --kms-key-id "$KMS" --secret-string '{"base_url":"...","token":"..."}' --region "$REGION"
# repeat for crm, kb, comms
aws secretsmanager list-secrets --region "$REGION" \
  --query "SecretList[?starts_with(Name, '/edu-agents/$ENV/')].Name"
```

**✅ Verification gate.** Each connector secret is listed under `/edu-agents/$ENV/...` and decrypts with the env CMK. A read-only tool call through the gateway (e.g. `sis.check_application_status`) resolves the SIS secret and returns data — proving the gateway → Secrets Manager → SoR path works end-to-end.

---

## 8. Observability

`observability.yaml` provisions the alarm/dashboard layer: an SNS alarm topic (email-subscribed), and the metric alarms the runbooks assume — **tool-authorization denial spike**, **PII-masking failure**, **HITL approval backlog age**, **HITL approval timeout**, **grounding failure**, and an optional **estimated-charges** cost alarm.

```bash
aws cloudformation deploy --region "$REGION" --stack-name "edu-observability-${ENV}" \
  --template-file infra/cloudformation/observability.yaml --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides Environment="$ENV" KmsKeyArn="$KMS" AlarmEmail="ops@example.edu" \
    CoreFunctionName="edu-agents-${ENV}-${AGENT_ID}-core" \
    PolicyGateFunctionName="edu-agents-${ENV}-${AGENT_ID}-policy-gate" \
    HitlEnqueueFunctionName="edu-agents-${ENV}-${AGENT_ID}-hitl-enqueue" \
    FinalizeFunctionName="edu-agents-${ENV}-${AGENT_ID}-finalize" \
    AuditTableName="<AuditTableName from Step 4>"

aws cloudwatch describe-alarms --region "$REGION" \
  --query "MetricAlarms[?starts_with(AlarmName, 'edu-')].{Name:AlarmName,State:StateValue}" --output table
```

**✅ Verification gate.** The alarms exist and are in `OK` (or `INSUFFICIENT_DATA` before traffic). The `AlarmEmail` recipient received and **confirmed** the SNS subscription. The denial-spike and PII-masking-failure alarms are present — these are the two that prove the security posture is being watched.

---

## 9. Smoke tests — prove the four behaviours

Run these against the deployed agent (authenticated, with a federated JWT carrying `custom:edu_role`). Each one has a verification gate that proves a specific governance property. The audit trail (`AuditTable`) must record the outcome of every one.

**9a. An allowed read.** As an authorized staff user, ask the Concierge to *check a student's application status* (`sis.check_application_status` — a read the role is granted).
- **✅ Gate:** the agent returns the status; `AuditTable` shows an `ALLOW` record with the masked subject. No HITL gate fired (it is a read).

**9b. A denied over-reach.** As the **same** user, ask for something the role is **not** granted (e.g. a tool outside `AGENT_TOOL_GRANTS["01-student-family-concierge"]`, or a write the role lacks).
- **✅ Gate:** the gateway **denies** (deny-by-default / role-intersection); `AuditTable` shows a `DENY` record; the **tool-authorization denial-spike** metric increments (Step 8 alarm watches it). The action does **not** occur.

**9c. A consequential action — blocked, then approved.** Ask the agent to **send a message to a family** (`comms.send_message` — the bright-line consequential action).
- **✅ Gate (blocked):** the agent does **not** send. The Step Functions execution suspends at the `waitForTaskToken` HITL gate; a `PENDING` row appears in `HitlQueueTable`; `AuditTable` shows `PENDING_APPROVAL`. See [`runbooks/HITL-QUEUE-OPERATIONS.md`](../HITL-QUEUE-OPERATIONS.md).
- Now have a **named, authorized reviewer** approve it (their identity is bound into the record before resume).
- **✅ Gate (approved):** the execution resumes to `Finalize`, the scoped write token is minted, the message sends, and `AuditTable` shows an `ALLOW` record carrying the **reviewer's identity**. Rejecting instead routes to `Escalate` and the message never sends.

**9d. A record-level authorization denial.** As an authorized user who lacks a relationship to a *specific* student (record-level scope, not just tool-level), request that student's record.
- **✅ Gate:** even though the user holds the tool grant, the request is **denied at the record level**; `AuditTable` shows a record-scoped `DENY`. (Confirm your record-level authz layer is wired — golden-path task #15.)

---

## 10. Teardown

Application and edge/observability stacks tear down cleanly; the **data stores are `DeletionPolicy: Retain` by design** (the audit trail and WORM bucket must survive). The AgentCore Gateway/Runtime live outside plain CloudFormation, so removing the provisioner custom resources (Delete) tears them down idempotently first.

```bash
# 1) Delete the app stack — the provisioner's Delete handler tears down the
#    AgentCore Gateway + Runtime idempotently (absent == success).
aws cloudformation delete-stack --stack-name "edu-${AGENT_ID}-${ENV}" --region "$REGION"
aws cloudformation wait stack-delete-complete --stack-name "edu-${AGENT_ID}-${ENV}" --region "$REGION"

# 2) Delete edge + observability.
aws cloudformation delete-stack --stack-name "edu-edge-${ENV}" --region "$REGION"
aws cloudformation delete-stack --stack-name "edu-observability-${ENV}" --region "$REGION"

# 3) Retained on purpose: AuditTable, HitlQueueTable, WormBucket, the CMK.
#    Dispose of these deliberately per your records-retention policy.
```

**✅ Verification gate.** The three stacks reach `DELETE_COMPLETE` (or show only `Retain`-policy resources remaining). The **WORM bucket and audit table still exist** — that is correct; deleting them is a separate, deliberate, policy-governed action. The gateway endpoint SSM parameter is gone and no AgentCore Gateway/Runtime remains.

---

## Cross-references

- **Master shared request path (every layer, every control):** [`docs/AWS-DEPLOYMENT-REFERENCE.md`](../../docs/AWS-DEPLOYMENT-REFERENCE.md)
- **Concierge specifics (tools, bright line, connectors, ROI):** [`01-student-family-concierge.md`](01-student-family-concierge.md)
- **The AgentCore provisioner Lambda:** [`infra/lambdas/agentcore_provisioner/README.md`](../../infra/lambdas/agentcore_provisioner/README.md)
- **HITL queue operations:** [`runbooks/HITL-QUEUE-OPERATIONS.md`](../HITL-QUEUE-OPERATIONS.md)
- **Funding + pre-flight:** [`docs/AWS-FUNDING-AND-PREREQUISITES.md`](../../docs/AWS-FUNDING-AND-PREREQUISITES.md)
- **Shared responsibility:** [`docs/SHARED-RESPONSIBILITY-MATRIX.md`](../../docs/SHARED-RESPONSIBILITY-MATRIX.md)

## Appendix — unified one-shot deploy (regional + edge)

Steps 3–9 above can be run as a single orchestrated command once your origin (the
public ALB / API Gateway in front of the AgentCore runtime) exists. `make deploy-all-01`
(→ `scripts/deploy_full.sh`) deploys the **regional** application stack in `--region`
and then the **edge** stack (CloudFront + WAFv2) in **us-east-1** (required for the
CloudFront ACM viewer certificate), wiring the origin into the distribution:

```bash
make deploy-all-01 \
  TEMPLATE_BUCKET=my-cfn-bucket  LAMBDA_BUCKET=my-lambda-bucket \
  IDP_METADATA=https://your-idp/metadata \
  ORIGIN_DOMAIN=app-alb-123.us-west-2.elb.amazonaws.com \
  ACM_CERT_ARN=arn:aws:acm:us-east-1:111122223333:certificate/abc \
  LOGGING_BUCKET=my-cloudfront-logs
```

**✅ Verification gate:** the command prints the regional stack name and the CloudFront
`DistributionDomainName`. Then complete the customer-owned hardening it lists — lock the
origin to the distribution (Origin-Verify header / CloudFront prefix list), point Cognito
callback URLs at the CloudFront domain, and smoke-test the authenticated endpoint through
CloudFront (a read, a denied over-reach, a consequential action blocked then approved).
