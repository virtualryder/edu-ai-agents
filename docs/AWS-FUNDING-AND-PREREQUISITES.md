# AWS Funding Programs and Account Prerequisites
### EDU AI Agent Suite — How to Fund the POC/Pilot and Pre-Flight Checklist

---

# Part A — AWS Funding Programs Guide

> The question every education customer asks before signing a pilot SOW is "who pays for the infrastructure?" This section answers it — and gives the seller the 4-step sequence to get AWS funding committed before the customer signs.

---

## 1. Partner Originated Activation (PoA) Credits

**What they are:** AWS credits that an AWS Partner (the SI) requests on behalf of a customer to offset the cost of a proof-of-concept or pilot on AWS infrastructure. PoA credits are designed specifically for the "try before you buy" motion — they lower the barrier to a first AWS workload deployment.

**How they work:**
- The SI (must be an AWS Partner Network member) submits a PoA request via the AWS Partner Central portal, specifying the customer, the workload, the AWS services to be used, and the business justification.
- AWS reviews and approves (typically within 2–5 business days for standard requests).
- Credits are applied to the customer's AWS account for a defined period (typically 30–90 days).
- Credits cover AWS service consumption — Bedrock inference, ECS Fargate, DynamoDB, S3, Lambda, API Gateway, KMS, CloudWatch.

**Typical size for an EDU AI POC/pilot:** $2,500–$25,000 USD, depending on workload size, AWS relationship, and partner tier. POC-level (demo mode, no live systems) is on the low end; a 6–12 week pilot with live Bedrock inference and AgentCore can reach the higher end.

**Eligibility:** The SI must be an AWS Partner Network (APN) member. Preferred partners (Select, Advanced, Premier) have better approval rates and higher credit limits.

**How to request:**
1. Log into AWS Partner Central (partnercentral.awsamazon.com).
2. Navigate to **Funding > Partner Originated Activation**.
3. Complete the PoA request form: customer name, opportunity ID (from ACE), AWS services, justification, credit amount requested, and timeline.
4. Attach the opportunity from ACE (see §5 Co-sell below) — PoA requests tied to a registered ACE opportunity have significantly higher approval rates.

**Key message to the customer:** "AWS will fund the infrastructure costs for the POC. You pay nothing for the AWS services during the proof of concept period."

---

## 2. Migration Acceleration Program (MAP)

**What it is:** MAP is AWS's primary funding vehicle for migrations and modernizations to AWS. For EDU AI programs, MAP applies when the engagement is framed as a **modernization of student-services or administrative workflows** — moving from manual, legacy, or on-premises processes to governed AI on AWS.

**EDU AI applicability:** MAP is more appropriate for:
- Institutions moving document-processing workflows from on-premises or non-AWS tooling to AWS (Textract, Bedrock, AgentCore) — Agent 07 Document & Accessibility Services is the clearest MAP candidate.
- Institutions displacing a legacy knowledge-management or help-desk system with Agent 08 Operations Service Desk on AWS.
- Full-portfolio deployments framed as institutional modernization of student services.

MAP is less appropriate for greenfield AI additions where there is no legacy system being displaced.

**How MAP funding is structured:**
- **MAP Assess:** Funded discovery and readiness assessment — this maps directly to the suite's Assessment Offering (`offerings/ASSESSMENT-OFFERING.md`). Typical range: $10,000–$50,000 in credits.
- **MAP Mobilize:** Funded pilot/mobilization — maps to the Pilot Offering (`offerings/PILOT-OFFERING.md`). Typical range: $25,000–$150,000 in credits depending on workload scale.
- **MAP Migrate:** Migration execution — for full portfolio deployments.

**How to access MAP:** The SI must be an AWS MAP-qualified partner. Submit the MAP application via Partner Central, tied to the customer ACE opportunity. AWS assigns a Migration Partner Development Manager (PDM) who helps structure the funding.

**Key message to the customer:** "If you're replacing a legacy system or moving a workflow to AWS, MAP can fund the assessment and pilot — often covering the majority of the SI professional services cost, not just infrastructure."

---

## 3. Partner Development Funds (PDF) and GTMP

**Partner Development Funds (PDF):** Discretionary funds available to SI partners through their AWS Partner Development Manager (PDM) for go-to-market activities — joint marketing, workshop delivery, customer events, proof-of-concept labs. PDFs are not credits against customer AWS bills; they fund SI activities that support AWS business development.

**How to access:** Work with your AWS PDM. Submit a fund request via Partner Central with a business justification tied to an ACE opportunity. PDF requests are approved at the PDM level (no AWS HQ review for standard amounts).

**Use cases for EDU AI:** Fund a joint discovery workshop with the customer's IT/academic leadership; fund the facilitated POC stakeholder workshop; fund joint marketing (case study, webinar, event appearance).

**GTMP (Go-to-Market Programs):** AWS offers vertical-specific GTMP programs, including for EDU/EdTech. These can include co-branded marketing development funds, AWS Marketplace campaign support, and joint PR. Contact your AWS PDM for current EDU GTMP availability.

---

## 4. ISV Accelerate and AWS Marketplace Private Offers

**ISV Accelerate:** AWS's co-sell program for ISVs and SI partners with a solution listed (or listing-eligible) on AWS Marketplace. Enrollment unlocks:
- Access to AWS seller co-sell motion (AWS sellers can propose your solution to their customers)
- Higher PoA credit limits
- Dedicated AWS co-sell manager support
- Eligibility for AWS Marketplace Seller Incentive Program (MSIP) — AWS pays a referral fee to AWS sellers who co-sell your listed solution

**To qualify:** The SI/ISV must have a solution listed (or accepted for listing) on AWS Marketplace. See `offerings/AWS-MARKETPLACE-GUIDE.md` for the listing path.

**AWS Marketplace Private Offers:** The preferred procurement vehicle for EDU institutions with existing AWS committed spend (EDP — Enterprise Discount Program). A private offer lets the institution purchase the SI's managed service + professional services through Marketplace, drawing against their AWS committed spend.

**Why this matters for EDU procurement:** Many universities and larger K–12 districts have AWS Enterprise Discount Program commitments. A Marketplace private offer lets them fulfill that commitment with the EDU AI managed service — turning an existing obligation into funding for the program.

---

## 5. The 4-Step Funding Sequence

Follow this sequence before the customer signs the pilot SOW:

**Step 1 — Register the opportunity in ACE (Partner Central)**
Before any funding conversation, register the customer opportunity in AWS Partner Central's co-sell system (ACE). This is the anchor for all funding requests. Include: customer name, institution type, AWS services (Bedrock, AgentCore, ECS, DynamoDB), estimated AWS TCV, stage (POC / Pilot / Production), and SI engagement type.

**Step 2 — Identify the right funding vehicle**
- POC only → PoA credits (fastest, lightest)
- Pilot with modernization framing → MAP Assess + MAP Mobilize
- Go-to-market activities → PDF
- Production managed service procurement → AWS Marketplace private offer

**Step 3 — Submit funding request before the customer signs the SOW**
PoA and MAP funding must be approved *before* the pilot starts to be applied. Do not wait until the customer has signed — the approval process takes 5–15 business days. Submit as soon as the customer has verbally committed to the pilot.

**Step 4 — Structure the SOW to align with funding**
If MAP Mobilize funds the pilot, the SOW's deliverables and milestones must align with MAP's required outputs (readiness report, migration plan or equivalent, and pilot results). The suite's Assessment + Pilot deliverables map naturally to MAP requirements — confirm with the AWS PDM before finalizing the SOW.

---

# Part B — AWS Account Prerequisites Checklist

> Give this checklist to the customer's IT team before the engagement starts. Everything on this list must be confirmed before the pilot Phase 1 (Gateway) kickoff. Items marked **[BLOCKER]** will stop the engagement if not resolved.

---

## Account Structure

- [ ] **[BLOCKER]** Dedicated AWS account for the EDU AI platform (recommended: separate from production institutional systems; can be in the same AWS Organization)
- [ ] AWS Organizations enrollment (recommended for SCP-based guardrails; not strictly required for POC)
- [ ] Account naming convention and tagging strategy agreed (tag all resources with `Environment`, `AgentID`, `InstitutionID`)
- [ ] AWS Cost and Usage Report (CUR) enabled for cost tracking
- [ ] AWS Budgets alert configured (recommend alert at 80% of estimated monthly budget)

---

## Region Selection

- [ ] **[BLOCKER]** Confirm deployment region: **us-east-1** (N. Virginia) or **us-west-2** (Oregon) recommended — these have the broadest Bedrock model availability
- [ ] Confirm region meets any state data-residency requirements (most US state student-privacy laws do not specify AWS region; confirm with institution's legal counsel)
- [ ] Confirm Bedrock is available and not restricted by any existing SCP in the Organization

---

## Amazon Bedrock Model Access

Bedrock model access must be explicitly requested — it is not enabled by default.

- [ ] **[BLOCKER]** Request access to **Anthropic Claude 3.5 Sonnet** (model ID: `anthropic.claude-3-5-sonnet-20241022-v2:0`) in the deployment region
- [ ] **[BLOCKER]** Request access to **Anthropic Claude 3 Haiku** (model ID: `anthropic.claude-3-haiku-20240307-v1:0`) in the deployment region

**How to request model access:**
1. Sign in to the AWS Console → Amazon Bedrock → Model access (left nav)
2. Click "Manage model access"
3. Check the boxes for Claude 3.5 Sonnet and Claude 3 Haiku
4. Submit the access request
5. Anthropic models typically approve within minutes to a few hours; confirm before the engagement kicks off

- [ ] Confirm model access status: navigate to Bedrock → Model access → verify "Access granted" status for both models
- [ ] (Optional) Request access to **Amazon Titan Embeddings** if using Bedrock Knowledge Bases for the vector store

---

## Bedrock AgentCore Availability

- [ ] **[BLOCKER if using AgentCore Gateway Option A]** Confirm Bedrock AgentCore is available in the deployment region
- [ ] Confirm whether AgentCore is GA or in preview in the target region (check the [Bedrock AgentCore documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html) for current regional availability)
- [ ] If AgentCore is not available in the required region, confirm fallback gateway option: **AWS API Gateway + Lambda + Step Functions** (Option B) or **self-built FastMCP** (Option C) — both are supported with identical enforcement semantics

---

## Service Quota Review and Increase Requests

Default service quotas can be a bottleneck during enrollment peaks. Request increases before the pilot, not during.

| Service | Quota to check | Recommended request |
|---|---|---|
| Amazon Bedrock | Requests per minute (RPM) per model — check per model | Request 2x default for the pilot; 5–10x for production at scale |
| Amazon Bedrock | Tokens per minute (TPM) per model | Request based on estimated token consumption from the ROI calculator |
| AWS Lambda | Concurrent executions (if using Option B gateway) | Default 1,000 per region; request 3,000–5,000 for production |
| Amazon DynamoDB | On-demand capacity (audit table) | On-demand auto-scales; confirm no SCP blocks DynamoDB in the account |
| Amazon ECS/Fargate | Task vCPU and memory limits | Default typically sufficient for pilot; review for production |
| API Gateway | Requests per second | Default 10,000/s; confirm sufficient for expected peak volume |
| Step Functions | State machine executions per second (HITL flow) | Default typically sufficient; review for high-volume agents |

**How to request quota increases:**
1. AWS Console → Service Quotas → Amazon Bedrock → Select the quota → Request quota increase
2. Provide a business justification (e.g., "K–12 district concierge agent for enrollment peak season")
3. Quota increases for Bedrock are typically approved within 1–3 business days

---

## IAM Prerequisites

- [ ] Confirm the AWS account has no SCP that blocks Bedrock, Fargate, DynamoDB, S3, Lambda, API Gateway, KMS, or Secrets Manager
- [ ] Identify or create an IAM role for the SI deployment team with sufficient permissions to deploy CloudFormation stacks (suggest `PowerUserAccess` + KMS permissions scoped to the platform's key ARN — not `AdministratorAccess`)
- [ ] Confirm the institution's cloud team has reviewed and approved the IAM roles in `infra/cloudformation/security.yaml` before deployment
- [ ] Permission boundaries: if the institution uses IAM permission boundaries, confirm the boundary allows the permissions the platform roles require
- [ ] Service-linked roles: confirm no SCP blocks creation of service-linked roles for ECS, Fargate, and Bedrock

---

## Networking Prerequisites

- [ ] VPC with at least 2 public and 2 private subnets across 2 Availability Zones (the QuickStart creates this; confirm if deploying into an existing VPC)
- [ ] Internet Gateway for ALB (if student-facing UI is public-facing)
- [ ] NAT Gateway for private subnet egress (Fargate tasks in private subnets need NAT for Bedrock API calls unless using VPC endpoints)
- [ ] (Optional but recommended for high-security deployments) VPC endpoint for Bedrock (com.amazonaws.[region].bedrock-runtime) to keep inference traffic off the public internet
- [ ] (Optional) VPC endpoint for S3 (com.amazonaws.[region].s3) and DynamoDB (com.amazonaws.[region].dynamodb) for private subnet access
- [ ] Security group rules: confirm no existing account-level security groups will block ALB → Fargate → Bedrock traffic
- [ ] DNS: confirm Route 53 or existing DNS can resolve the ALB endpoint for the student-facing surface

---

## Logging and Observability Baseline

- [ ] **[BLOCKER]** AWS CloudTrail enabled and logging to S3 in the deployment account (required for the audit trail to be complete; CloudTrail records API calls; DynamoDB records agent-level audit events)
- [ ] CloudWatch log retention set to at least 365 days for the platform's log groups (FERPA recordkeeping)
- [ ] S3 access logging enabled on the audit bucket
- [ ] CloudWatch alarms baseline: CPU/memory on Fargate tasks, Lambda error rate, DynamoDB throttling, Bedrock quota utilization
- [ ] AWS Config enabled (recommended for compliance drift detection; required if the institution needs continuous compliance evidence for SOC 2 or FedRAMP)

---

## S3 and Audit Storage Configuration

- [ ] S3 Object Lock available in the deployment region and not blocked by SCP
- [ ] Audit bucket configured with Object Lock in **COMPLIANCE mode** (cannot be overridden even by account root) and a retention period aligned to the institution's FERPA records-retention schedule (recommend 7 years minimum)
- [ ] S3 bucket public access block enabled on all platform buckets (no exceptions)
- [ ] KMS encryption on all S3 buckets (SSE-KMS, not SSE-S3, for audit buckets — enables audit log encryption with a CMK the institution controls)

---

## Cost and Budget Controls

- [ ] AWS Cost Explorer enabled
- [ ] Budget alert configured: email alert at 80% of estimated monthly platform cost (see `gtm/roi-calculator/` for cost estimates)
- [ ] AWS Cost Anomaly Detection configured for Bedrock (inference cost is the largest variable line; anomaly detection catches runaway token consumption)
- [ ] Resource tagging enforced (recommend AWS Config rule to flag untagged resources in the platform account)

---

## Pre-Flight Sign-Off

The customer's cloud/IT lead and the SI delivery lead should both sign off on this checklist before the Phase 1 (Gateway) kickoff. Items marked [BLOCKER] that are not resolved will delay the engagement.

| Item | Status | Owner | Target date |
|---|---|---|---|
| AWS account structure confirmed | | | |
| Region selected and Bedrock available | | | |
| Claude 3.5 Sonnet model access granted | | | |
| Claude 3 Haiku model access granted | | | |
| AgentCore availability confirmed (or fallback gateway selected) | | | |
| Bedrock quota increases submitted | | | |
| IAM deployment role created and reviewed | | | |
| CloudTrail enabled | | | |
| S3 Object Lock configured on audit bucket | | | |
| Budget alert configured | | | |
