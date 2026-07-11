# DO NOT CLAIM — the portfolio honesty boundary

*Portfolio-level consolidation of every repo's `NOT-CLAIMS.md`. Read this before writing a slide, an
email, or a statement of work. If any other document reads stronger than this page, **this page
governs** — open an issue so it can be corrected. This is deliberately blunt so a CISO, a regulator,
or AWS leadership can trust every other claim in the portfolio.*

---

## This portfolio is NOT
- **Not an AWS service, AWS-supported software, or an official AWS solution.** It is an independent
  reference accelerator that *runs on* AWS. No AWS SLA, hotfix path, endorsement, or Competency.
- **Not a compliance certification.** Nothing here certifies HIPAA, FERPA, CJIS, GxP/21 CFR Part 11,
  SOC 2, HITRUST, FedRAMP, or StateRAMP. Those authorizations attach to the customer's configured,
  operated, and authorized deployment under the AWS shared-responsibility model — not to this code.
- **Not production-ready for real regulated data without customer-specific validation.** Running it
  against real PHI/PII/CJI requires the customer's own security engineering, testing, and formal
  authorization first.
- **Not a substitute for customer legal / privacy / compliance review.** Control descriptions are
  engineering statements, not legal advice.

## Do NOT claim (specific)
- ❌ "40+ production AI agents." → ✅ *One deep hero per vertical + governed reference scaffolds.*
- ❌ "The agents are autonomous reasoning AI." → ✅ *Governed reference workflows, deterministic by
  default; one real Bedrock path per hero. The **governance** is the product.*
- ❌ "Every agent is equally validated / deployed." → ✅ *Lead only with the clean-account-validated
  heroes; the scorecard says which.*
- ❌ "Live integration with Epic / Veeva / Argus / a real 835 feed / ServiceNow / an SIS." → ✅
  *Tier-3 public read-only reference connectors only; tier-4 systems of record are engagement work.*
- ❌ "Scored quality benchmarks prove model accuracy." → ✅ *The evals are harnesses over the
  deterministic reference pipeline with a real PII/PHI-leak gate — not a model-quality benchmark.*
- ❌ "Data never leaves the VPC." → ✅ *Bedrock is a regional AWS service reached over PrivateLink;
  sensitive fields are masked at the audit and model-output boundaries (input filterable by Bedrock Guardrails, not blanket pre-scrubbed); no egress to external non-AWS AI APIs by default.
  This is a strong posture, not an absolute guarantee, and does not by itself make a deployment
  compliant.*
- ❌ "AWS endorses / sponsors this." → ✅ *Built on AWS; not affiliated with, endorsed by, or
  supported by AWS.*

## What it therefore IS
A **governed reference architecture and implementation accelerator** — deployable IaC, a
deny-by-default authorization gateway, worked governed agent examples, honest evidence, and
go-to-market material — for **discovery, architecture workshops, envisioning, and scoped pilots on
synthetic or de-identified data**. A fast, credible starting point the customer hardens, validates,
and authorizes inside their own AWS account.

---
*Per-repo detail: each repository's `NOT-CLAIMS.md` and `MATURITY.yaml`. Machine-checked by
`tools/check_maturity.py`.*
