# TCO Model — Education AI Agent Suite
### Monthly AWS run-cost model: Pilot vs Production

> **MODEL ASSUMPTION — illustrative estimate** built from published us-east-1 on-demand list
> prices as of mid-2026; prices and token economics change frequently; validate with the AWS
> Pricing Calculator and your AWS account team before quoting. **Bedrock token volume is the
> dominant, workload-dependent variable** — every Bedrock line below is the sensitivity driver.
> No figure here is a quote.

Run-cost companion to `offerings/COST-ROI-MODEL.md` (value side) — net the value model there
against the AWS run cost here. Demo mode uses zero Bedrock tokens and effectively zero cloud cost.

---

## Scenario assumptions

| Assumption | **Pilot** (1 agent, dept-scale) | **Production** (8-agent suite) |
|---|---|---|
| Governed requests/month | ~10,000 (e.g., Agent 01 concierge for one campus/school) | ~500,000 (district / mid-size institution, all 8 agents) |
| Active users (MAU) | ~50 staff/educators | ~2,000 staff/educator MAU (student-facing channels may federate via the institution IdP — re-price Cognito if students are direct MAUs) |
| Bedrock tokens/month | ~5M input + ~1M output | ~250M input + ~50M output |
| Model class | Mid-tier Claude (Sonnet-class): ~$3.00/M input, ~$15.00/M output tokens `[MODEL ASSUMPTION]` | same |
| Architecture | Serverless reference path (API Gateway HTTP API → Lambda → Step Functions → Bedrock), private-by-default (VPC interface endpoints even in pilot) | same, plus production hardening (NAT, WAF, CloudFront) |
| Per-request shape | ~2 API calls, ~5 Lambda invocations, ~15 Step Functions state transitions, ~10 DynamoDB writes + 20 reads (audit + state) | same |

Tutoring and grading-feedback workflows (Agents 02, 04) are token-heavier per request; concierge
and service-desk (01, 08) are lighter but higher-volume — the suite figures below blend them.
Re-weight to the institution's actual mix before presenting.

## Monthly cost estimate (us-east-1, on-demand list, mid-2026)

| Line item | Basis | **Pilot ($/mo)** | **Production ($/mo)** |
|---|---|---:|---:|
| **Bedrock inference** ← *sensitivity driver* | Sonnet-class; 5M in + 1M out (pilot) / 250M in + 50M out (prod) | **30** | **1,500** |
| Bedrock Guardrails ← *scales with request volume* | Content filters, prompt-side; ~2 text units/request @ ~$0.75/1K units | 15 | 750 |
| Lambda | ~5 invocations/request; 512 MB × ~800 ms | 1 | 17 |
| API Gateway (HTTP API) | ~2 calls/request @ ~$1.00/M | 1 | 1 |
| Step Functions (Standard) | ~15 state transitions/request @ ~$25/M | 4 | 188 |
| DynamoDB (on-demand) | ~10 WRU + 20 RRU/request + storage (1 GB pilot / 25 GB prod) | 1 | 11 |
| S3 + Object Lock (WORM audit) | 5 GB pilot / 200 GB prod + requests | 2 | 7 |
| KMS | $1/CMK (4 pilot / 6 prod) + ~20 requests/request @ $0.03/10K | 5 | 36 |
| Cognito | MAU-based (~$0.015/MAU); 50 pilot / 2,000 prod | 1 | 30 |
| CloudWatch | Logs ingest + metrics + dashboards | 3 | 50 |
| VPC interface endpoints | ~$7.30/endpoint-mo + data; 5 endpoints pilot / 8 prod (Bedrock, KMS, STS, Logs, Secrets…) | 36 | 68 |
| NAT Gateway | Prod only; ~$33/mo + ~100 GB processed | — | 37 |
| WAF | Prod only; web ACL + 5 rules + request fees | — | 11 |
| CloudFront | Prod only; student/family web channel, low-GB tier | — | 10 |
| **TOTAL** | | **~$99/mo** | **~$2,716/mo** |

**Sensitivity (one line):** 2× Bedrock token volume ≈ **+$1,500/mo** at production scale
(inference is ~55% of the production total); every other line moves slowly.

Rounding: whole dollars; sub-dollar lines shown as $1. Annualized production: ~$32.6K/yr.

## What's NOT included

- Personnel (program owner, educator reviewers, platform operations)
- ProServe / SI partner delivery fees (Assessment, POC, Pilot — see `offerings/PILOT-OFFERING.md`)
- Data egress at scale (SIS/LMS bulk sync, cross-Region)
- AWS enterprise support plan (typically 3–10% of spend)
- Non-prod environments (dev/test/staging — commonly +30–60% of the prod infra baseline, minimal Bedrock in demo mode)

## ROI netting (worksheet)

```
Net monthly value = modeled monthly value              ← offerings/COST-ROI-MODEL.md and
                                                          per-agent docs/roi-analysis.md
                  − monthly AWS run cost (this model)
                  − monthly share of SI fees / managed service
```

At the README's per-agent value figures (e.g., $1.2M–$1.6M/yr deflected contacts for Agent 01
alone), the full production suite run cost (~$2.7K/mo ≈ $33K/yr) is a rounding error against the
value model — the business case is decided by adoption and the value assumptions, not the AWS bill.

---

*Related: `offerings/COST-ROI-MODEL.md` (value side), `offerings/PILOT-OFFERING.md`,
`gtm/roi-calculator/`, per-agent `docs/roi-analysis.md`.*

---
**Value side:** see [ROI-CASE-STUDY.md](ROI-CASE-STUDY.md) for a fully worked, illustrative ROI example with totals.
