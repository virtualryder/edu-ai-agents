# What We Will *Not* Claim

*Read this first. It is deliberately blunt so that a director of architecture, a CISO, a
regulator, or AWS leadership can trust every other claim in this repository.*

**Scope for this repo:** EDU AI Agents (K-12 & higher education).

---

## This is NOT

- **Not an AWS service.** This is an independent reference accelerator that *runs on* AWS. It is not offered, sold, or operated by AWS.
- **Not AWS-supported software.** AWS Support does not cover this code. There is no AWS SLA, hotfix path, or managed lifecycle behind it.
- **Not an AWS official solution.** It is not an AWS Solution, an AWS Quick Start, an AWS Competency offering, or otherwise endorsed, reviewed, or certified by AWS.
- **Not a compliance certification.** Nothing here certifies, attests, or proves compliance with any law, regulation, or framework.
- **Not HITRUST / SOC 2 / FedRAMP / StateRAMP authorized.** The accelerator holds no such authorization. Where those programs apply, they attach to the **AWS services** under the shared-responsibility model — and only when the customer configures, operates, and authorizes them accordingly.
- **Not production-ready for regulated data without customer-specific validation.** The code is a deployable reference pattern. Running it against real regulated data (FERPA/COPPA and student PII (the platform provides technical controls; FERPA/COPPA compliance remains the institution's accountability)) requires the customer's own security engineering, testing, and formal authorization first.
- **Not a substitute for customer legal / compliance review.** Every statement about controls, regimes, or data flows is an engineering description, not legal advice. The customer's legal, privacy, and compliance teams own the determination.

## What it therefore IS

A **governed reference architecture and implementation accelerator** — architecture, deployable infrastructure-as-code, a deny-by-default MCP authorization gateway, worked agent examples, evidence templates, and go-to-market material — intended for **discovery, architecture workshops, envisioning, and scoped pilots**. It is a fast, credible starting point that the customer hardens, validates, and authorizes inside their own AWS account.

## On the data-location and compliance language in this repo

Where this repository describes inference, it means: **Amazon Bedrock is a regional AWS service reached from the customer's VPC over AWS PrivateLink (private connectivity) — not "Bedrock runs inside your VPC."** Sensitive fields are masked before any model call, and there is no egress to external (non-AWS) AI APIs. This is a strong data-handling posture; it is **not** an absolute "data never leaves the VPC" guarantee, and it does not by itself make a deployment compliant. Customer compliance depends on the applicable BAA/agreements, service eligibility, configuration, operations, and the AWS shared-responsibility model.

---

*If any wording elsewhere in this repository reads as stronger than this page, **this page governs.** Please open an issue so it can be corrected.*
