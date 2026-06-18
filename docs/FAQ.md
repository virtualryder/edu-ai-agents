# Frequently Asked Questions
### EDU AI Agent Suite

---

## Section 1 — General / What Is This

**Q: What is the EDU AI Agent Suite?**
A: A governed accelerator for deploying AI agents in education institutions — K–12 districts, community colleges, universities, online programs, and workforce education providers. It delivers eight high-value education workflows (student services, tutoring, educator support, grading, student success, advising, document processing, and operations) on a shared platform built on Amazon Bedrock. The platform provides the governed controls that make AI agents deployable on student records: deny-by-default authorization, PII masking, a human-approval gate on consequential actions, and a FERPA-aligned audit trail — built once and reused across all eight agents. The agents are the visible surface; the governed platform is the product.

**Q: Who is this for?**
A: Three audiences. (1) **Education institutions** (CIOs, VP Student Success, academic leaders, CISOs, privacy officers) evaluating governed AI for student services, instruction, advising, operations. (2) **Systems integrators** and AWS partners deploying AI solutions for education customers — the suite provides the accelerator, the field collateral, and the platform controls they need to reach production. (3) **AWS sales and solution architecture teams** working EDU AI opportunities — the suite maps to AWS Well-Architected, Bedrock AgentCore, and AWS co-sell motions.

**Q: What is the maturity level of this suite?**
A: The suite uses a four-rung maturity ladder: **Documented** (architecture and compliance design written — useful for discovery), **Demonstrated** (runs end-to-end in demo mode with no API keys or live systems — suitable for POC workshops), **Deployable** (CloudFormation/Terraform, container contracts, CI pass; requires customer AWS account and Bedrock access — suitable for pilots), and **Production-ready** (security/privacy review complete, IdP integrated, live connectors tested, WCAG 2.2 AA conformance tested, penetration test passed). Current status: the platform architecture, compliance spine, field/GTM collateral, and governance framework are at Documented/Demonstrated. The eight agents are brought to Deployable/Production-ready through customer engagements.

**Q: What is explicitly out of scope?**
A: University research administration, advancement/fundraising, and specialized laboratory agents. The four emerging/roadmap use cases: longitudinal learner-success orchestrator, precision-learning agent teams, cross-system autonomous institutional operations, and dialogue-based assessment/simulations. The suite also does not include penetration testing (separately contracted), legal opinions, or compliance certifications of any kind.

**Q: Is this a SaaS product I can hand to a customer unchanged?**
A: No. It is a governed accelerator — a credible, compliant starting point that a delivery team operationalizes for a specific institution. The institution retains FERPA/COPPA/PPRA compliance accountability, IdP integration and role mapping, connector validation against live systems, Bedrock Guardrail configuration for its population, and WCAG 2.2 AA conformance testing of its deployed surfaces. The distinction is explicit in every SOW and in the suite README. This transparency is a credibility asset with CISOs and procurement teams, not a liability.

---

## Section 2 — Compliance and Privacy

**Q: How does this handle FERPA?**
A: FERPA has three key requirements for an AI agent acting on student records: (1) the agent can only access records for a user's legitimate educational interest; (2) a qualified human approves consequential decisions; (3) every disclosure is recorded. The MCP authorization gateway addresses all three: deny-by-default authorization enforces legitimate educational interest scoping at the tool level; the HITL gate blocks consequential actions until a named human reviewer approves; and the PII-masked append-only audit trail records every access with the identity, tool, basis, and timestamp. FERPA compliance accountability remains with the institution — the SI provides the technical controls the institution uses to meet its obligations. See `docs/SHARED-RESPONSIBILITY-MATRIX.md` for the full FERPA responsibility division.

**Q: How does this handle COPPA for K–12 and under-13 students?**
A: COPPA imposes heightened requirements for children under 13. The platform addresses this through: (1) PII masking tuned to COPPA's heightened identifier categories; (2) Bedrock Guardrail configuration with heightened sensitivity for under-13 populations (the institution approves the Guardrail policy for its population); (3) the FERPA/COPPA overlap addressed through deny-by-default authorization that enforces parental consent state in the IdP claims. The institution is the COPPA-obligated operator — it must obtain verifiable parental consent where required and configure the platform for its under-13 population. The SI provides a recommended Guardrail configuration; the institution approves it.

**Q: How does the suite handle IDEA and Section 504 (special education)?**
A: IEP and 504 accommodations are treated as the highest-sensitivity FERPA-protected records. The authorization model enforces strict role-scoping: only educators, counselors, and administrators with the appropriate role entitlement can access accommodation records, and only through the MCP gateway. The platform's bright line is explicit: the agent never decides special-education eligibility or IEP placement — those decisions are gated to a named, authorized human (the IEP/504 team). The agent can retrieve accommodation information for the relevant authorized users and draft materials for review, but every determination is human.

**Q: What about state student-privacy laws?**
A: The suite includes a state-law mapping workstream in the Readiness Assessment offering. The platform is parameterized for the most common state-law configuration points: data-residency requirements, student consent and opt-out, third-party disclosure restrictions, breach-notification timelines, and prohibited-use restrictions. The assessment produces a state-law obligation map expressed as platform configuration. The SI cannot guarantee compliance with every state's requirements — the institution's legal counsel makes legal determinations; the SI provides the technical configuration.

**Q: How is the audit trail designed for FERPA compliance?**
A: The audit trail is: append-only (no records can be edited or deleted retroactively — enforced by DynamoDB's write-once semantics and S3 Object Lock WORM backup); PII-masked (student identifiers are replaced with stable pseudonyms — real identifiers are not stored in the audit log, only in the authoritative SIS); complete (every ALLOW/DENY/PENDING_APPROVAL/ERROR is logged with the identity, tool, basis, timestamp, and reviewer identity for approved actions); and stored in the institution's own AWS account (the institution is the records custodian). This log is the FERPA recordkeeping of disclosures the institution must maintain. It is produced automatically for every agent interaction across all eight agents.

**Q: Does student data leave the institution's control?**
A: No student PII leaves the institution's AWS account. All inference runs in the institution's own account and region. The PII masker replaces student identifiers before any content enters a model prompt — the model reasons over pseudonyms, not real records. No student data transits SI infrastructure. AWS model inference (Bedrock) runs in the institution's account under AWS's standard data-processing terms. See `docs/SHARED-RESPONSIBILITY-MATRIX.md` for the full data-flow and data-residency picture.

**Q: How do guardian rights and age-of-majority work?**
A: The MCP gateway enforces guardian relationship and age-of-majority access controls through the IdP claims the institution provides. When a student turns 18 (or enrolls in postsecondary education for K–12 → higher-ed transitions), FERPA rights transfer to the student — and the guardian's role entitlements in the gateway reflect that transfer. A guardian attempting to access a post-18 student's record is denied at the gateway with a logged DENY entry. The accuracy of the age-of-majority and guardian-relationship state is the institution's responsibility to maintain in its IdP; this is the most common readiness gap, especially in K–12 deployments.

---

## Section 3 — AWS and Infrastructure

**Q: What AWS services does this use?**
A: Core services: **Amazon Bedrock** (Claude inference, Knowledge Bases for grounding, Guardrails for content filtering), **Bedrock AgentCore** (runtime, gateway, identity — Option A) or **API Gateway + Lambda + Step Functions** (Option B). Storage: **DynamoDB** (append-only audit trail), **S3 with Object Lock** (WORM audit backup, documents), **Secrets Manager** (API credentials). Compute: **ECS Fargate** (agent containers). Supporting: **KMS** (encryption), **CloudWatch + CloudTrail** (observability and audit), **IAM + IAM Identity Center / Cognito** (identity federation), **Textract / Transcribe / Translate / Polly** (Agent 07 document and accessibility processing).

**Q: Which AWS regions are supported?**
A: **us-east-1 (N. Virginia)** and **us-west-2 (Oregon)** are recommended — they have the broadest Bedrock model availability. Other regions are available but may have limited Bedrock model access or AgentCore availability. Always confirm regional availability before deployment. See `docs/AWS-FUNDING-AND-PREREQUISITES.md` for the region-selection checklist.

**Q: Which Bedrock model does the suite use?**
A: **Claude 3.5 Sonnet** for complex reasoning, multi-step advising, grading, and intervention analysis. **Claude 3 Haiku** for high-volume simple classification, retrieval, and routing tasks. Model selection is configurable per agent via `platform_core/edu_agent_platform/llm_factory.py`. `EXTRACT_MODE=demo` bypasses inference entirely for local testing with no API key required.

**Q: What is the expected monthly AWS cost?**
A: Highly dependent on volume, model selection, agent count, and gateway hosting option. The largest variable line item is Bedrock inference (tokens/month × $/token). Use `gtm/roi-calculator/EDU-AI-Suite-ROI-Calculator.xlsx` to model your specific institution's volume. Narrative guidance in `offerings/COST-ROI-MODEL.md` §4. The build-once economics: the governance control plane (gateway, identity, audit, HITL) is paid for once on the first agent and reused by all subsequent agents.

**Q: Can this run without Amazon Bedrock AgentCore?**
A: Yes. Three gateway hosting options are supported with identical enforcement semantics: (A) Managed **AgentCore Gateway** (AWS-managed, least operational overhead), (B) **API Gateway + Lambda + Step Functions** (AWS-primitives, full customer control), (C) **Self-built FastMCP server** (institution owns the code outright). The enforcement logic is the same in all three — implemented in `platform_core/edu_agent_platform/mcp_gateway/` and testable locally without an AWS account.

---

## Section 4 — Security and CISO Questions

**Q: Has this been penetration tested?**
A: Not by the SI as a pre-packaged product test. The SI provides the security evidence package — architecture documentation, IAM role definitions, authorization model, audit trail samples, HITL gate test evidence, connector data-flow documentation, and Guardrail configuration — that the institution's security team or a contracted third party uses to conduct a penetration test. Penetration testing is a production-readiness gate and is scoped separately. See `offerings/TPRM-DUE-DILIGENCE-PACKET.md`.

**Q: Does the SI have SOC 2 certification?**
A: The SI's compliance attestations (SOC 2, etc.) are provided in the TPRM due-diligence packet for the institution's vendor risk review. AWS's SOC 2 Type II, ISO 27001, and HIPAA-eligible service documentation are available via AWS Artifact.

**Q: Who has access to our student data?**
A: The institution's own AWS account administrators and the IAM roles defined in the CloudFormation deployment. The SI does not have standing access to the customer's data environment in production. SI access for managed service operations is through scoped, time-limited IAM session credentials — not standing service accounts — and every action is logged in CloudTrail.

**Q: What happens if there is a data breach?**
A: The incident-response runbook (`runbooks/INCIDENT-RESPONSE.md`) defines the SI's procedure: detection via CloudWatch/CloudTrail alarms, immediate containment (disable the affected agent or tool — no standing credentials to revoke across the board), investigation via the PII-masked append-only audit trail, and notification to the institution within 48 hours of confirmed discovery. The institution makes the legal breach-notification determination and owns notifications to students, parents, and regulators. The audit trail is the evidence base for the investigation.

**Q: How is the authorization model structured — how do I know an agent can't access more than it should?**
A: The authorization equation is: `permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[agent] ∩ ROLE_ENTITLEMENTS[user_roles]`. Both sides of the intersection must include the tool — the agent's grant list AND the user's role entitlement list. An agent can never do more than the human it acts for, and the human can never grant the agent more than the agent's own grant list permits. This logic runs in the gateway, outside the model — a prompt injection cannot change the authorization outcome because the model doesn't evaluate authorization. The gateway does, before any tool call is made.

---

## Section 5 — Implementation and Timelines

**Q: How long does a typical engagement take?**
A: Assessment: 3–5 weeks. Demo-mode POC: 2–4 weeks. Pilot (one agent, one live system): 6–12 weeks. Production rollout (full population): follows the pilot. Portfolio expansion (additional agents): each agent after the first is faster because the gateway is already built. The most important variable is the institution's readiness — particularly IdP maturity, system API availability, and governance function engagement.

**Q: What staff do we need from the institution's side?**
A: Named points of contact for: FERPA/privacy officer (weekly engagement through gateway Phase 1), CISO/security delegate (gateway Phase 1 exit gate), IdP administrator (identity federation, typically 1–2 weeks of active work), system-of-record owner (connector validation, typically 2–3 weeks), accessibility coordinator (WCAG 2.2 AA conformance, pilot Phase 4), executive sponsor (go/no-go decisions at each phase exit), and service owner/academic lead for the pilot workflow (scenario validation and baseline data).

**Q: What is the difference between a POC, a pilot, and a production deployment?**
A: **POC**: runs in `EXTRACT_MODE=demo` — no live systems, no API keys, no student data. Purpose: prove the governance controls are real, get the go/no-go decision. Deliverable: POC findings memo and recommended pilot scope. **Pilot**: one agent against one live system of record, in the customer's AWS account, with the gateway built first. Purpose: prove the controls hold against live systems, and demonstrate a measured outcome against a pre-deployment baseline. **Production**: full population rollout, all exit criteria met (WCAG, security review, pen test, outcome demonstrated, HITL operational). The readiness assessment is what determines which engagement type is the right first step.

**Q: Can we start with just one agent without committing to all eight?**
A: Yes — and this is the recommended motion. Land with Agent 01 (Concierge) or one of the other best-first agents (03, 07, 08). The pilot proves the value and builds the shared platform. Portfolio expansion to additional agents is the natural next step, and each additional agent is cheaper because the gateway, identity, audit, and HITL framework are already in production.

**Q: What if we want to start with a higher-governance agent (02, 04, 05, or 06)?**
A: The recommendation is to land with a best-first agent first, then sequence the higher-governance agent after the control plane is proven. If the institution insists on a higher-governance agent as the first deployment, the engagement requires a Readiness Assessment first — higher-governance agents require stronger governance maturity (bias testing, educator oversight protocols, evidence retention, specialized equity review) that the assessment maps. The platform works for any agent as the first deployment; the sequencing recommendation is about risk management and time-to-value.

---

## Section 6 — The Agents

**Q: Which agent should we deploy first?**
A: Almost always **Agent 01 (Student & Family Services Concierge)**. It is the most visible to the most users, lowest decision-risk, most measurable (call/email deflection), and it builds the shared platform that every subsequent agent reuses. Reference proof point: UA–Pulaski Tech, 94.5% adoption, 253% admissions-engagement lift. Alternatives for a first deployment if Agent 01 is not the right fit: Agent 08 (Operations Service Desk) for an IT-led entry, Agent 07 (Document & Accessibility Services) for an enrollment-led entry, or Agent 03 (Educator Copilot) for an academic-led entry.

**Q: Can we customize the agents for our institution?**
A: Yes. The suite is a starting point, not a fixed product. The grounding content (knowledge base), the role entitlements, the Guardrail configuration, the connector (which SIS/LMS/ERP fields each tool accesses), and the agent-specific prompts are all configurable and are the primary customization surface during the pilot. The governance controls (deny-by-default authorization logic, PII masker, HITL gate, audit trail) are shared platform and should not be customized away — they are what passes the security review.

**Q: What happens when the agent is wrong or produces a bad answer?**
A: The platform has three lines of defense: (1) grounding verification — if the answer doesn't trace to approved institutional content, the agent fails fast rather than producing a fabricated answer; (2) Bedrock Guardrails — content filtering on inputs and outputs; (3) the HITL gate — for consequential actions, a qualified human reviews and approves before the action executes. Override rates and grounding-failure rates are tracked as managed-service quality signals. The managed service's eval harness runs golden-artifact regression on every change to catch quality drift before it reaches students.

**Q: How is this different from ChatGPT or Microsoft Copilot?**
A: Public AI (ChatGPT, Copilot) can answer questions. It cannot safely *act on student records* — there is no identity-scoped authorization, no deny-by-default, no enforced human gate, no FERPA-aligned audit trail, and no grounding to the institution's approved content. The moment the use case crosses into acting on a real education record — checking a student's financial-aid status, opening a case, drafting a personalized intervention, sending a communication — it requires the governed layer this platform provides. Public AI is genuinely useful for open-ended drafting tasks; it is not suitable for agent workflows that touch personally identifiable education records. Microsoft Copilot for Education is deeper in the M365/LMS stack but does not provide a deny-by-default gateway across SIS, ERP, and ITSM, nor does it produce FERPA-aligned disclosure recordkeeping.

**Q: What is the "bright line" — what do these agents never decide?**
A: Grades, admissions, discipline, financial-aid awards, special-education eligibility, and student placement. These are encoded as policy and tested in the codebase — not merely documented. Every one of these actions requires a named, authorized human who is bound into the record. The agent drafts, recommends, retrieves, and routes; the human decides every consequential outcome.

---

## Section 7 — Pricing and Procurement

**Q: How is this priced?**
A: The engagement is priced per the SI's standard professional services model: Assessment, POC, Pilot, and Managed Service are scoped and priced per the SOW template in `gtm/SOW-TEMPLATE.md`. AWS infrastructure costs are the institution's (or can be offset via AWS funding programs — see `docs/AWS-FUNDING-AND-PREREQUISITES.md`). There is no per-seat or per-agent SaaS fee for the accelerator itself; pricing is SI professional services plus AWS run cost.

**Q: Can we purchase through AWS Marketplace?**
A: Yes. The suite's Managed Service offering is available via AWS Marketplace private offer — allowing institutions with existing AWS committed spend (EDP) to use that commitment for the managed service. See `offerings/AWS-MARKETPLACE-GUIDE.md` for the full Marketplace procurement guide and private offer mechanics.

**Q: Can AWS fund the POC or pilot?**
A: In many cases, yes. AWS Partner Originated Activation (PoA) credits can offset POC and pilot AWS infrastructure costs. For modernization workloads, the AWS Migration Acceleration Program (MAP) can fund both the assessment and the pilot. Partner Development Funds (PDF) can support joint discovery workshops and POC delivery activities. The 4-step funding sequence to get credits committed before the SOW is signed is in `docs/AWS-FUNDING-AND-PREREQUISITES.md` Part A.
