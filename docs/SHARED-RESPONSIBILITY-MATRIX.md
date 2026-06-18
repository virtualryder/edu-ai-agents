# Shared Responsibility Matrix
### EDU AI Agent Suite — AWS · Systems Integrator · Institution

> This document is for procurement teams and CISOs. It defines who owns, shares, or enables each responsibility domain across the three parties in a governed EDU AI deployment. Use it to answer the procurement question "who is responsible for what?" and to pre-empt TPRM (third-party risk management) questionnaire items.

**Legend:**
- **Owns** — primary accountability; if this goes wrong, this party is accountable
- **Shares** — joint responsibility; both parties must act for the control to hold
- **Enables** — provides the capability, tooling, or evidence; the other party operationalizes it
- **N/A** — not applicable to this party's role in the deployment

---

## Responsibility Matrix

| Domain | AWS | Systems Integrator (SI) | Institution | Notes |
|---|---|---|---|---|
| **Infrastructure security** — physical security of data centers, hypervisor, managed service infrastructure | Owns | N/A | N/A | AWS SOC 2 Type II / ISO 27001 / FedRAMP documentation covers this. AWS publishes Customer Responsibility Model. |
| **Network security** — VPC configuration, security groups, NACLs, VPC endpoints | Enables | Owns (per CloudFormation templates) | Shares (approves VPC design; owns network policy) | SI designs and deploys per `infra/cloudformation/network.yaml`; institution's network security team approves before production |
| **Compute security** — OS patching, container image security, Fargate runtime | Enables (Fargate manages OS) | Owns (container image build, dependency scanning) | N/A | Fargate eliminates OS patching burden; SI owns container image supply chain security |
| **Storage encryption** — KMS key management, S3/DynamoDB encryption at rest | Enables (KMS service) | Owns (key policies, rotation config) | Shares (owns the KMS CMK; approves key policy) | Institution should own the CMK for student-data buckets; SI configures key policy per `infra/cloudformation/security.yaml` |
| **Identity and access management** — IAM roles, permission boundaries, SCPs | Enables (IAM service, Organizations) | Owns (role design, least-privilege policies in CloudFormation) | Shares (approves roles; applies SCPs at org level; owns IdP) | Institution's cloud team must review and approve IAM roles before production; institution controls the IdP that feeds the gateway |
| **IdP federation and role mapping** — SSO integration, student/guardian/educator/admin role claims | Enables (IAM Identity Center, Cognito) | Owns (federation design, claim mapping implementation) | Owns (IdP is the institution's system; role definitions are institution policy; age-of-majority and guardian-relationship data accuracy) | The most common readiness gap: the institution's IdP may not express guardian relationships or age-of-majority today |
| **Data residency and sovereignty** — student records stay in institution's AWS account and region | Enables (region selection, no cross-region replication by default) | Owns (architecture design; no SI systems receive student PII) | Owns (selects AWS region; approves data-flow architecture; ensures region meets state data-residency law) | All inference runs in the institution's own AWS account; no student PII transits SI infrastructure |
| **Student PII protection (FERPA/COPPA)** — masking, access control, disclosure recordkeeping | Enables (Bedrock Guardrails, KMS, DynamoDB, Macie) | Owns (PII masker implementation, gateway authorization logic, audit trail design) | Owns (FERPA compliance program; defines legitimate educational interest; approves role entitlements; age-of-majority determination) | FERPA accountability stays with the institution; SI provides the technical controls the institution uses to meet its obligations |
| **Model governance** — prompt version pinning, eval harness, model selection | N/A | Owns (prompt manifest, eval harness, CI enforcement, change-control procedure) | Shares (designates a reviewer who signs off on model/prompt promotions) | Institution must have a named human who approves changes that affect student-facing agent behavior |
| **Human-in-the-loop gate** — consequential action approval, reviewer roster | Enables (Step Functions waitForTaskToken, SQS) | Owns (gateway implementation; HITL queue operations in managed service) | Owns (designates reviewers; sets approval policies; defines what counts as "consequential" for each workflow) | The institution must staff the HITL queue with qualified reviewers in the correct roles — this cannot be fully delegated to the SI |
| **Audit trail and recordkeeping** — append-only FERPA-aligned audit, disclosure records | Enables (DynamoDB, S3 Object Lock) | Owns (audit trail implementation, PII masking of records, WORM configuration) | Owns (FERPA recordkeeping obligation; must produce records in response to parent requests, audits, or OCR investigations; records retention schedule) | SI builds and maintains the technical audit system; the institution is the records custodian under FERPA |
| **Bedrock Guardrails configuration** — content filtering, topic denial, PII detection | Enables (Guardrails service) | Owns (recommended configuration; implements per-agent Guardrail policies) | Owns (approves Guardrail configuration; determines appropriate sensitivity levels for its student population, including under-13 settings) | The institution's legal and student-services leadership must approve Guardrail policy — especially for K–12 and COPPA populations |
| **Grounding content and knowledge base** — approved institutional content, update cadence | Enables (Bedrock Knowledge Bases) | Owns (KB setup, ingestion pipeline, grounding verification implementation) | Owns (authorizes which content enters the KB; approves updates; owns accuracy of policy/catalog content) | Stale or incorrect grounding content is an institution risk — the SI implements change control; the institution approves content |
| **Incident response** — detection, containment, investigation, notification | Enables (CloudTrail, CloudWatch, GuardDuty) | Owns (runbook execution, technical containment, audit evidence production) | Owns (legal breach-notification determination; required notifications to students, parents, and regulators; final authority on containment decisions affecting academic operations) | `runbooks/INCIDENT-RESPONSE.md` defines the SI's role; institution must have its own breach-notification procedure |
| **Accessibility (WCAG 2.2 AA)** — student/family-facing surface conformance | N/A | Owns (conformance testing during pilot; remediation; accessibility maintenance in managed service) | Owns (approves accessibility conformance standard; designates accessibility coordinator; final acceptance of VPAT/conformance report) | WCAG 2.2 AA is a production-readiness gate, not optional |
| **Business continuity / DR** — RTO/RPO targets, failover, backup | Enables (multi-AZ, S3 cross-region replication, RDS snapshots) | Owns (DR runbook, backup configuration, recovery procedures) | Owns (RTO/RPO policy for student-facing services; approves DR plan; owns decisions to activate failover during incidents) | `runbooks/DR-RUNBOOK.md` covers the SI's DR procedures |
| **Vendor/TPRM risk management** — SI vendor review, Anthropic/AWS vendor review | N/A | Shares (provides security evidence package, architecture documentation, compliance attestations) | Owns (FERPA "school official under direct control" determination; vendor agreement execution; security questionnaire sign-off) | `offerings/TPRM-DUE-DILIGENCE-PACKET.md` provides the evidence package |
| **AWS compliance attestations** — SOC 2, ISO 27001, HIPAA-eligible, FedRAMP | Owns (for AWS services) | N/A | Shares (must confirm AWS services used are within FedRAMP authorization boundary if FedRAMP is required; SOC 2 report access via AWS Artifact) | AWS Artifact provides current compliance reports; institution's compliance team reviews for their obligations |
| **SI compliance attestations** — SI's own SOC 2, security certifications | N/A | Owns | Shares (requests and reviews as part of TPRM) | SI provides attestations in the TPRM evidence package |
| **Connector / integration security** — SIS/LMS/ERP API credentials, connector validation | Enables (Secrets Manager, VPC private endpoints) | Owns (connector implementation, credential management in Secrets Manager, least-privilege API scopes) | Owns (provides API credentials; approves the scopes the connector requests; validates connector behavior against live system in pilot) | No connector goes to a live system without the institution's explicit approval of the scope and a signed pilot SOW |
| **Change management** — prompt changes, model upgrades, feature additions | N/A | Owns (change-control procedure, change calendar, rollback documentation) | Shares (designates a reviewer who approves changes that affect student-facing behavior; institution approves production promotion) | No change to prompts, model version, or tool grants reaches production without institution sign-off |
| **Staff training and acceptable-use policy** — educator and staff training on agent capabilities and limits, AUP | N/A | Enables (training materials, capability documentation) | Owns (AUP drafting and enforcement; staff training program; communicating the bright line to faculty and advisors) | The institution must train its staff on what the agent does and does not decide; the SI provides capability documentation |

---

## How to Present This to a CISO

**1. Lead with the data-residency statement.**
> "Student records never leave your AWS account. Inference runs in your account, in your selected region. No student PII transits SI infrastructure. AWS's shared responsibility model means AWS owns physical security, hypervisor, and managed-service infrastructure; you own the data and the IAM policies."

**2. Distinguish the SI's role: we build and operate the technical controls; you own the compliance program.**
> "We implement the MCP gateway, the PII masker, the HITL gate, and the audit trail. We run those controls in production. But FERPA compliance accountability stays with you — you define legitimate educational interest, you approve role entitlements, you are the records custodian. We give you the controls that make it possible; you accept compliance accountability."

**3. The HITL gate cannot be circumvented — by us or by a prompt.**
> "The human approval gate runs outside the model, in the gateway. We can't turn it off remotely. A prompt injection can't bypass it. The institution's designated reviewers hold the keys. If the HITL queue backs up, consequential actions pause — they don't silently execute."

**4. The audit trail is the institution's evidence, not ours.**
> "The append-only DynamoDB audit trail with WORM S3 backup is your record — FERPA's recordkeeping of disclosures, automatic. You own the KMS key. You can produce that record to a parent, an auditor, or OCR. We don't have access to your data; we have access to the configuration that protects it."

**5. Show the "Owns" column in the matrix — the CISO's accountability surface.**
> "Walk through the matrix with the CISO: every row where you see 'Owns' in the Institution column is a question I need answered before we go to production. That's the readiness checklist — IdP accuracy, Guardrail approval, reviewer roster, FERPA program, breach-notification procedure, acceptable-use policy. Those are not things the SI can do for you. But this matrix tells you exactly what they are, up front."

---

## Common CISO/Procurement Questions and Where to Point

| Question | Answer source |
|---|---|
| "What compliance certifications does AWS have?" | AWS Artifact — SOC 2 Type II, ISO 27001, HIPAA BAA, FedRAMP Moderate (for applicable services) |
| "What compliance certifications does the SI have?" | TPRM evidence package: `offerings/TPRM-DUE-DILIGENCE-PACKET.md` |
| "Who has access to our student data?" | The institution's own AWS account admins and the IAM roles defined in the deployment — the SI does not have standing access to the customer's data environment |
| "What happens if the SI goes out of business?" | The enforcement logic is readable Python in `platform_core/` — the institution can operate or migrate it; the infrastructure is standard CloudFormation/Terraform in the institution's own account |
| "Is this FERPA-compliant?" | The platform provides the technical controls; FERPA compliance is the institution's accountability. See §2 (FERPA) of `gtm/SOW-TEMPLATE.md` for the full legal framing. |
| "What is the data breach notification procedure?" | `runbooks/INCIDENT-RESPONSE.md`; the SI notifies the institution within 48 hours of confirmed discovery; the institution makes the legal breach-notification determination |
