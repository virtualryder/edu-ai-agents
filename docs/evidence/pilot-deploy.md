# Agent 01 Concierge — Pilot Deploy Evidence

*Run 2026-07-12 · AWS account `864217980669` · us-east-1. A real CloudFormation stack
(`eduverify-pilot-concierge`, template `infra/cloudformation/pilot-concierge.template.json`)
was deployed (`create-stack` → CREATE_COMPLETE), the concierge Lambda invoked across four
governance scenarios, evidence captured from the deployed append-only audit table, then all
resources deleted. This is the pilot-depth deploy proof for the hero agent.*

## The deployed pilot (one governed Lambda)

Public info (real retrieval + model) · authenticated status (synthetic SIS) · deny-by-default
authorization · record-level scope · human-in-the-loop for consequential actions · runtime
PII masking · append-only, CMK-encrypted, PITR audit. IAM least-privilege
(`bedrock:InvokeModel` on model ARNs, `dynamodb:PutItem` on the table, KMS on the key).

## Four scenarios — all verified in the DEPLOYED audit table

| # | Input | Decision | Proof |
|---|---|---|---|
| 1 | STUDENT asks about "University of Michigan-Ann Arbor" (`kb.search`) | **ALLOW** | `source: collegescorecard` — the Lambda pulled **live College Scorecard** data and Bedrock produced a grounded answer citing the real figures: **15.6% admission rate, $17,736 in-state tuition**. Masked answer written to audit. |
| 2 | STUDENT `S-100` reads own status (`sis.status`) | **ALLOW** | `target: S-100` — synthetic SIS record returned; masked result audited. |
| 3 | STUDENT `S-100` tries to read `S-200`'s status | **DENY** | `reason: record-scope` — a student may reach only their own record. |
| 4 | COUNSELOR sends a family message (`comms.send`) | **PENDING_APPROVAL** | consequential action human-gated before execution (HITL). |

Real model answer captured (verbatim from the deployed audit record):

> "# University of Michigan-Ann Arbor … **Admission Rate:** 15.6% (highly selective) … **In-State
> Tuition:** $17,736 per year …"

Those figures came from the **live** `api.data.gov` College Scorecard API through the deployed
Lambda — genuine retrieval + generation, not fixtures.

## Issues found and resolved (honest)

- First model (`us.anthropic.claude-sonnet-4-6`) returned `AccessDeniedException` requiring
  `aws-marketplace:ViewSubscriptions/Subscribe`; granted those to the Lambda role and switched
  to `us.anthropic.claude-sonnet-4-5-20250929-v1:0`, after which the grounded answer succeeded.
  (The template defaults are documented in the pilot runbook so a customer avoids this.)

## Teardown

Stack deleted (Lambda, DynamoDB, IAM role, KMS scheduled) · guardrail deleted · swept clean.
Cost of the run: under **$1**.

## What this proves vs. what remains

Proven live: a CloudFormation-deployed governed concierge doing real retrieval, real grounded
generation, deny-by-default + record-scope authorization, HITL, PII masking, and append-only
audit. **Still customer-engagement:** real IdP (Cognito↔SAML) in front, the real SIS connector
(this pilot used synthetic SIS + the public College Scorecard), the full VPC/edge/AgentCore
nested stack, an independent pen test, and full manual WCAG conformance.
