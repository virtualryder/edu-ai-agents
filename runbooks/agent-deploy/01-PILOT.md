# Agent 01 Concierge — Pilot Runbook (deployable in one stack)

The fastest way to stand the **governed concierge** up in your own AWS account and prove the
controls end-to-end. This is the exact stack that was deployed and verified on 2026-07-12
(see [`docs/evidence/pilot-deploy.md`](../../docs/evidence/pilot-deploy.md)). It runs the
concierge as ONE governed Lambda: real **College Scorecard** retrieval for public questions,
**synthetic SIS** data for authenticated status (swap for the real SIS under FERPA sign-off),
deny-by-default authorization, record-level scope, HITL for consequential actions, runtime
PII masking, and an append-only, CMK-encrypted, PITR audit table.

> Scope note: this pilot stack is a **self-contained proof** of the governed pattern. The full
> production topology (Cognito↔IdP federation, CloudFront/WAF edge, AgentCore Gateway/Runtime,
> the real SIS/LMS connector, the reviewer UI) is the `quickstart.yaml` nested path in
> [`01-GOLDEN-PATH.md`](01-GOLDEN-PATH.md) and [`../../docs/AWS-DEPLOYMENT-REFERENCE.md`](../../docs/AWS-DEPLOYMENT-REFERENCE.md).

## Prerequisites

- AWS CLI v2, credentials for an account with **Amazon Bedrock model access enabled** for an
  Anthropic Claude model (Console → Bedrock → Model access).
- Region `us-east-1` (adjust as needed).
- (Optional) a College Scorecard API key from https://api.data.gov/signup/ — otherwise the
  stack defaults to `DEMO_KEY` (rate-limited, fine for a pilot).

## Step 1 — Create the Bedrock Guardrail (content + PII)

```bash
GID=$(aws bedrock create-guardrail --name concierge-pilot-guardrail \
  --blocked-input-messaging "Blocked by policy." --blocked-outputs-messaging "Blocked by policy." \
  --content-policy-config "filtersConfig=[{type=PROMPT_ATTACK,inputStrength=HIGH,outputStrength=NONE}]" \
  --sensitive-information-policy-config "piiEntitiesConfig=[{type=US_SOCIAL_SECURITY_NUMBER,action=BLOCK},{type=EMAIL,action=ANONYMIZE}]" \
  --region us-east-1 --query guardrailId --output text)
echo "GuardrailId=$GID"
```

## Step 2 — Deploy the pilot stack

```bash
aws cloudformation deploy \
  --template-file infra/cloudformation/pilot-concierge.template.json \
  --stack-name concierge-pilot \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides GuardrailId=$GID ModelId=us.anthropic.claude-sonnet-4-5-20250929-v1:0 \
  --region us-east-1

FN=$(aws cloudformation describe-stacks --stack-name concierge-pilot --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='FunctionName'].OutputValue" --output text)
TABLE=$(aws cloudformation describe-stacks --stack-name concierge-pilot --region us-east-1 \
  --query "Stacks[0].Outputs[?OutputKey=='AuditTableName'].OutputValue" --output text)
```

**✅ Gate:** stack reaches `CREATE_COMPLETE`; `describe-stacks` returns the function + table names.

> **Model-access gotcha (seen in the reference run):** if the first invoke returns
> `AccessDeniedException … aws-marketplace:Subscribe`, either enable that model in the Bedrock
> console, add `aws-marketplace:ViewSubscriptions`/`Subscribe` to the function role, or set
> `ModelId` to a model already enabled in your account.

## Step 3 — Acceptance scenarios (the four that must pass)

```bash
inv () { aws lambda invoke --function-name "$FN" --payload "$1" --region us-east-1 /tmp/out.json >/dev/null; }

# 1) Public info -> ALLOW with real College Scorecard retrieval + grounded answer
inv '{"claims":{"role":"STUDENT","sub":"u-1","student_id":"S-100"},"tool":"kb.search","query":"University of Michigan-Ann Arbor"}'
# 2) Own record -> ALLOW (synthetic SIS status)
inv '{"claims":{"role":"STUDENT","sub":"u-1","student_id":"S-100"},"tool":"sis.status"}'
# 3) Cross-record -> DENY (record scope)
inv '{"claims":{"role":"STUDENT","sub":"u-1","student_id":"S-100"},"tool":"sis.status","student_id":"S-200"}'
# 4) Consequential send -> PENDING_APPROVAL (HITL)
inv '{"claims":{"role":"COUNSELOR","sub":"u-c1"},"tool":"comms.send","query":"Please submit your verification documents"}'

# Verify every attempt in the DEPLOYED append-only audit table:
aws dynamodb scan --table-name "$TABLE" --region us-east-1 \
  --query "Items[*].{decision:decision.S,user:user.S,tool:tool.S,reason:reason.S,source:source.S}"
```

**✅ Gate (expected audit rows):** `kb.search → ALLOW (source=collegescorecard)`,
`sis.status → ALLOW`, `sis.status → DENY (record-scope)`, `comms.send → PENDING_APPROVAL`.

## Step 4 — Operate

- **Monitoring:** deploy `infra/cloudformation/observability.yaml` for CloudWatch alarms
  (authorization-denial spikes, PII-mask failures, HITL backlog, Bedrock throttling) + a dashboard.
- **HITL queue:** consequential actions return `PENDING_APPROVAL`; a named human approves via the
  reviewer service (`platform_core/edu_agent_platform/reviewer/`, `reviewer/app.py`), which issues
  a signed, single-use, transaction-bound approval the gateway accepts exactly once.
- **Audit review:** the DynamoDB table is append-only (the role holds `PutItem` only) with PITR;
  export to S3 Object Lock (WORM) for long-term immutability (see `data.yaml`).

## Step 5 — Disaster recovery

DynamoDB PITR is enabled (restore to any second in the last 35 days). The stack is
redeployable from `pilot-concierge.template.json` in minutes; the audit table is the only
stateful resource. For multi-Region DR, replicate the audit table via a global table and
redeploy the stack in the second Region.

## Step 6 — Teardown (no lingering cost)

```bash
aws cloudformation delete-stack --stack-name concierge-pilot --region us-east-1
aws bedrock delete-guardrail --guardrail-identifier $GID --region us-east-1
```

The KMS key created by the stack schedules for deletion on its window. Confirm zero residual:
`aws lambda list-functions`, `aws dynamodb list-tables` (no `concierge-pilot*`).

## Moving from pilot to production

Replace synthetic SIS with the real SIS connector under a FERPA "school official" DPA; put
Cognito↔your IdP (SAML/OIDC, MFA) and the CloudFront/WAF edge in front; wire the reviewer UI to
a durable queue + the Step Functions task token; run a pen test and full WCAG conformance. Those
are tracked in [`../../MATURITY.yaml`](../../MATURITY.yaml) and
[`../../docs/PRODUCTION-READINESS-ACTION-PLAN.md`](../../docs/PRODUCTION-READINESS-ACTION-PLAN.md).
