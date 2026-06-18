# AWS Marketplace Guide
### EDU AI Agent Suite — Listing Path, Private Offer Mechanics, and Co-sell Motion

> This guide is for the SI account team and AWS co-sell partner. It covers why AWS Marketplace is the preferred procurement vehicle for EDU customers, how to structure a private offer for the pilot and managed service, the listing prerequisites, and how to run the co-sell conversation with the customer.

---

## 1. Why AWS Marketplace Matters for EDU

AWS Marketplace is not just a distribution channel — for education institutions, it is a procurement simplifier and a spend accelerator. Here is why EDU customers prefer it:

**Existing AWS committed spend drawdown.** Many universities, large community college districts, and state education agencies have AWS Enterprise Discount Program (EDP) commitments — negotiated spend commitments in exchange for pricing discounts. A Marketplace purchase counts against those commitments. An institution that has committed $500K/year to AWS can apply that commitment to the EDU AI managed service without a separate PO, separate vendor approval process, or separate budget line.

**Procurement simplification.** Marketplace purchases run through the institution's existing AWS billing relationship. One vendor (AWS), one invoice, one purchase order process. For procurement offices that have already approved AWS as a vendor, adding a Marketplace purchase is dramatically simpler than onboarding a new SI vendor through TPRM, legal review, and contract negotiation from scratch.

**Reduced legal friction.** AWS Marketplace uses standardized contract terms (AWS Marketplace Standard Contract, with custom amendments for the EDU-specific data-governance obligations in the SOW). Institutions with existing AWS relationships have often already reviewed and accepted the standard terms baseline.

**EDP alignment.** Marketplace purchases can be structured to maximize EDP discount realization — particularly valuable for institutions in the final year of an EDP commitment where they need to demonstrate spend to renew at favorable rates.

**Speed.** A Marketplace private offer can be accepted by the customer's AWS account owner in minutes once it is live. Compare this to a typical multi-month SI procurement cycle.

---

## 2. Listing Options — Which Fits This Suite

AWS Marketplace supports several listing types. The right structure for the EDU AI Agent Suite:

| Listing type | Fits? | Why |
|---|---|---|
| **SaaS contract** | ✅ Primary | Managed service with a recurring contract — maps to the suite's Managed Service offering (monthly or annual subscription, usage-based or flat-rate) |
| **Professional services** | ✅ Secondary | Assessment, POC, and Pilot engagements — time-bound professional services deliverables |
| **Container/AMI** | Possible | If the SI offers a self-managed version of the platform; secondary to the managed service model |
| **Free trial** | ✅ For POC | Can structure the demo-mode POC as a free-trial period within a SaaS contract, lowering the barrier to the first transaction |

**Recommended structure:** A single Marketplace listing that combines:
- A **SaaS contract** for the Managed Service (recurring: annual or monthly, per-agent or per-institution pricing)
- A **professional services** line item for the Assessment, POC, and Pilot (one-time, milestone-based)

This allows the institution to sign one Marketplace agreement that covers the full engagement path — from Assessment through ongoing Managed Service — with one approval cycle.

---

## 3. Private Offer Mechanics

A private offer is a customized Marketplace offer extended to a specific customer — with negotiated price, duration, and terms that override the public listing. Private offers are the standard vehicle for EDU enterprise deals.

**How a private offer works:**
1. The SI creates the private offer in the AWS Marketplace Management Portal (AMMP), specifying: customer AWS account ID, offer type (SaaS contract), pricing (flat, usage-based, or tiered), duration (1-year, 2-year, multi-year), and custom EULA/terms amendments.
2. AWS reviews the offer (typically within 1 business day for standard structures).
3. The SI sends the offer URL to the customer's AWS account owner.
4. The customer reviews and accepts the offer in their AWS console — no PO required from the SI.
5. Billing begins per the offer terms and appears on the customer's consolidated AWS invoice.

**What the private offer includes:**
- Managed Service subscription fee (monthly or annual, covering HITL queue operations, model/prompt change control, eval/fairness monitoring, accessibility maintenance, incident response, monthly reporting)
- Professional services component (Assessment + POC + Pilot, milestone-based)
- AWS infrastructure costs are billed separately through the customer's AWS account (not through the Marketplace offer)
- Optional: support tiers (standard / premium / dedicated)

**Duration and auto-renewal:** Standard EDU contracts are 1-year with auto-renewal. Multi-year (2–3 year) private offers can provide price lock — valuable for institutions building multi-year budget plans. Include an amendment process clause for portfolio expansion (adding agents) without requiring a new Marketplace transaction.

**Custom EULA amendment:** The private offer's EULA should incorporate by reference the data-governance and FERPA-specific obligations from `gtm/SOW-TEMPLATE.md` §6 (Data Governance and Compliance Obligations). AWS Marketplace allows custom EULA terms — do not rely solely on the Standard Contract for EDU data-governance requirements.

---

## 4. AWS Marketplace Listing Prerequisites

Before listing, the SI must meet these requirements:

**AWS Partner Network tier:** Select Partner tier or above strongly recommended; Advanced or Premier tier improves visibility, search ranking, and eligibility for AWS seller co-sell and ISV Accelerate.

**AWS Marketplace Seller account:** Register at the AWS Marketplace Management Portal. Requires US bank account, W-9 (US entities), and tax documentation. Approval takes 3–5 business days.

**Listing review:** AWS Marketplace reviews all new listings for completeness, accuracy, and compliance with listing policies. For SaaS listings, AWS requires: a working product URL, documentation, pricing configuration, and support information. EDU-specific compliance claims (FERPA, COPPA, WCAG) must be substantiated — do not make unsubstantiated compliance certification claims.

**AWS Qualified Software:** The listing should note that the suite runs on AWS services and leverages Bedrock and AgentCore — this is eligible for the "Works with AWS" badge and co-sell eligibility.

**ISV Accelerate enrollment:** After listing acceptance, enroll in ISV Accelerate to unlock AWS seller co-sell, higher PoA credit limits, and access to the AWS Marketplace Seller Incentive Program (MSIP). ISV Accelerate requires a listed product and an active ACE pipeline.

---

## 5. Pricing Structures on Marketplace

Three pricing models work for the EDU AI suite on Marketplace:

| Model | Structure | Best for |
|---|---|---|
| **Flat annual SaaS contract** | Fixed annual fee per institution (e.g., $X for up to N agents, Y enrolled students) | Institutions that want budget predictability; most common for K–12 districts and smaller colleges |
| **Per-agent subscription** | Monthly fee per deployed agent (e.g., $X/month per active agent) | Institutions that want to land-and-expand — pay for one agent, add agents as the portfolio grows |
| **Usage-based** | Monthly fee based on interactions or inference tokens consumed | High-variability institutions (online programs with enrollment fluctuations); less common for EDU |

**Recommended default:** Per-agent subscription with a floor (minimum 1 agent) — aligns with the land-with-01, expand-the-portfolio motion. The first agent (typically Concierge) establishes the Marketplace relationship; each additional agent adds to the subscription without a new procurement cycle.

**What to include in the Marketplace price:** The Managed Service subscription (HITL operations, change control, eval/fairness, accessibility, incident response, monthly reporting). Do not bundle AWS infrastructure costs into the Marketplace price — those run directly through the customer's AWS bill.

---

## 6. How to Run the Conversation with the Customer

**The 5-sentence Marketplace pitch:**
> "You probably already have an AWS commitment. A Marketplace private offer lets you apply that commitment directly to the EDU AI managed service — no new vendor PO, no new vendor onboarding, one invoice. We structure the offer to cover the full engagement: the assessment, the pilot, and the ongoing managed service. Your procurement team has already approved AWS as a vendor; this adds one line item to your existing AWS bill. It's the fastest path from contract signature to platform live."

**When to introduce Marketplace:** At the point the customer has a verbal commitment to the pilot and you're discussing commercial structure — typically after the POC go/no-go. Do not introduce Marketplace prematurely (before the customer has decided to proceed) as it can create confusion about pricing before the value is established.

**How to handle the objection "we don't use AWS Marketplace":**
> "Your AWS procurement team may not have used Marketplace for professional services before — it's newer than software-only listings. But if you have an AWS EDP commitment, every dollar you spend here counts against it. I can send you a one-pager your procurement team can use to understand how Marketplace private offers work with your existing AWS agreement. It often turns out to be simpler than the standard SI procurement path."

**If the institution has no AWS account or EDP:** Marketplace is not the right vehicle. Proceed with a standard SI contract and the institution can establish their AWS account through the engagement (see `docs/AWS-FUNDING-AND-PREREQUISITES.md`). Marketplace can be introduced at the renewal/expansion stage after the first year.

---

## 7. Co-sell with AWS

**Why co-sell matters:** AWS sellers (account executives and SAs) have existing relationships with education institution IT and procurement leaders. A co-sell motion — where both the SI and the AWS seller are actively working the opportunity — dramatically accelerates deal cycles, improves funding outcomes, and increases the probability of a successful deployment.

**ACE pipeline registration:** Register every qualified EDU AI opportunity in AWS Partner Central's co-sell system (ACE) as early as possible — ideally at or before the POC stage. Include: institution name and type, AWS services in scope, estimated AWS TCV, estimated deployment timeline, and the SI's engagement type. An ACE registration is required for PoA credits, MAP funding, ISV Accelerate eligibility, and for the AWS seller to officially engage.

**What to put in the ACE opportunity to get AWS support:**
- Customer name and account ID
- AWS services: Amazon Bedrock (Claude 3.5 Sonnet, Claude 3 Haiku), Bedrock AgentCore (or API Gateway + Lambda + Step Functions), ECS Fargate, DynamoDB, S3, KMS, CloudWatch, CloudTrail
- Use case: "Governed AI agents for EDU — student services, educator support, operations"
- AWS TCV estimate (12-month Bedrock inference + AgentCore + storage + supporting services)
- SI managed service TCV (for MSIP eligibility — AWS pays the SI a referral fee when the AWS seller co-sells an ISV Accelerate-listed solution)
- Stage: POC / Pilot / Production
- Requested AWS support: SA engagement, PoA credits, MAP funding

**How AWS sellers benefit:** Through ISV Accelerate and MSIP, the AWS seller earns a co-sell incentive (typically a % of the Marketplace transaction) when they co-sell a listed ISV solution. This gives the AWS seller a financial reason to actively push the solution — make sure they know the MSIP eligibility early.

---

## 8. Private Offer Checklist

Step-by-step for creating and executing a private offer:

- [ ] Confirm customer AWS account ID (the offer is tied to a specific account)
- [ ] Confirm customer has reviewed and is ready to accept: pricing, duration, EULA amendment (SOW §6 data-governance obligations)
- [ ] Confirm customer's EDP commitment (if applicable) — verify Marketplace purchases count against their specific EDP contract with their AWS account team
- [ ] Log into AWS Marketplace Management Portal → Offers → Create private offer
- [ ] Select the base listing (SaaS contract or professional services)
- [ ] Configure pricing: per-agent subscription fee, duration (1-year / 2-year), auto-renewal terms
- [ ] Attach custom EULA amendment incorporating FERPA/COPPA data-governance obligations from `gtm/SOW-TEMPLATE.md` §6
- [ ] Set offer expiration date (recommend 30 days from send — creates urgency without being aggressive)
- [ ] Submit for AWS Marketplace review (1 business day typical turnaround)
- [ ] Send offer URL to customer's AWS account owner with a brief cover note explaining what they're accepting and confirming the SOW deliverables are separate (Marketplace covers the commercial vehicle; the SOW covers the scope and obligations)
- [ ] Follow up with the customer's procurement team to confirm they understand how Marketplace purchases are invoiced through their AWS consolidated bill
- [ ] Confirm acceptance in AMMP — you will receive a notification when the customer accepts
- [ ] Register the Marketplace transaction in ACE (required for MSIP eligibility)
- [ ] Begin engagement per SOW milestones
