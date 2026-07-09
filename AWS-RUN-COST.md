# AWS Run-Cost Model — EDU (K-12 & Higher Education)

*The infrastructure "what does it cost to run" line items for the governed pattern, so a business case
and a finance review use the same list across the portfolio. **Illustrative framework, not a quote** —
prices change and vary by Region; populate each line with the [AWS Pricing Calculator](https://calculator.aws)
for your Region and volume. Pairs with the value-side model in `offerings/` (ROI/TCO). Worked example
below is for **Agent 01 (Student & Family Concierge)** at pilot scale.*

## Cost drivers (in rough order of impact)

1. **Amazon Bedrock inference (per token)** — usually the dominant variable cost; scales with
   invocations × tokens/call × model price. The single biggest lever (model choice, prompt/context size).
2. **Human-in-the-loop wait time** — Step Functions `waitForTaskToken` is cheap to hold, but the
   *human* is the real cost; see [`OPERATING-MODEL.md`](OPERATING-MODEL.md).

## Line items — every service the pattern uses

| # | Service | Billing basis | Scales with | Pilot magnitude* |
|---|---|---|---|---|
| 1 | **Amazon Bedrock** (inference) | per input/output token | invocations × tokens × model | **$$–$$$** (dominant) |
| 2 | **Bedrock Guardrails** | per text unit evaluated | every model call | $ |
| 3 | **AgentCore Gateway** *or* **API Gateway** | per request (+ AgentCore units) | tool calls / requests | $ |
| 4 | **AWS Lambda** | requests + GB-seconds | tool calls, workflow steps | $ |
| 5 | **AWS Step Functions** | per state transition | workflow steps × runs | $ |
| 6 | **Amazon DynamoDB** (on-demand) | R/W request units + storage | audit + approvals + jti writes | $ |
| 7 | **Amazon S3 + Object Lock (WORM)** | storage + requests | audit evidence retained | $ (grows with retention) |
| 8 | **Amazon CloudWatch** | logs GB + metrics + dashboards | log volume, custom metrics | $–$$ (watch log volume) |
| 9 | **AWS WAF** | web ACL + rules + requests | public edge traffic | $ |
| 10 | **AWS PrivateLink** (interface VPC endpoints) | per-AZ-hour + data processed | # endpoints × AZs (always-on) | **$$ (fixed, always-on)** |
| 11 | **Amazon Cognito** | monthly active users | workforce users | $ (free tier often covers pilots) |
| 12 | **AWS KMS** | keys + requests | CMK per data class + calls | $ |
| 13 | **AWS Support** | % of monthly AWS spend (Business/Enterprise) | total spend | % add-on |
| 14 | **Operations (customer staff)** | FTE time | monitoring, approvals, IR, break/fix | see OPERATING-MODEL |

*Magnitudes are relative ($ ≈ tens, $$ ≈ hundreds, $$$ ≈ thousands / month at pilot scale) — **replace
with real figures from the Pricing Calculator**. Data class for this pack: Student PII → PrivateLink for the record-touching variant.

## Worked estimate framework (fill in)

```
Monthly Bedrock       = invocations/mo × avg_tokens/call × price_per_1k_tokens/1000
Guardrails            = invocations/mo × text_units/call × guardrail_price
Gateway/API GW        = tool_calls/mo × request_price
Lambda                = (tool_calls + steps)/mo × (request_price + GB_s_price × avg_GB_s)
Step Functions        = runs/mo × transitions/run × transition_price
DynamoDB              = (audit + approval + jti writes)/mo × WRU_price + storage_GB × storage_price
S3 Object Lock        = retained_GB × storage_price + requests
CloudWatch            = log_GB × ingest_price + custom_metrics × metric_price + dashboards
WAF                   = web_ACL + rules + (requests/mo × request_price)
PrivateLink           = endpoints × AZs × 730h × hourly_price + data_GB × processing_price   # ALWAYS-ON
Cognito / KMS         = MAU × price (often free tier) ; CMKs × key_price + requests
Support               = support_tier_% × (sum of the above)
------------------------------------------------------------------
Monthly AWS run-cost  = Σ above     ·  + human reviewer time (operations)
```

## How to reduce it

- **Model & context size** dominate — right-size the model, trim prompt/context, cache retrieval.
- **PrivateLink is a fixed always-on cost** — share endpoints across agents in one VPC; don't
  provision per-agent endpoints if one set serves the account.
- **CloudWatch log volume** is a silent driver — set retention, sample verbose logs.
- **Marginal cost per additional agent is low** — the platform (gateway, audit, endpoints, WAF) is
  shared; agents 2..N mostly add Bedrock + Lambda/Step-Functions usage.

> Illustrative only; not a quote or a guarantee. Combine with the value-side model in `offerings/` for a
> full business case, and see [`NOT-CLAIMS.md`](NOT-CLAIMS.md) for scope.
