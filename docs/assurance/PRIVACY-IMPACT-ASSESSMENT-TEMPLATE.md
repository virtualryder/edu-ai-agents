# Privacy Impact Assessment (PIA) — Template

### EDU AI Agent Suite · FERPA / COPPA / PPRA / IDEA-504 / GLBA / State Student-Privacy Law

> **What this is.** A Privacy Impact Assessment **template** the deploying institution completes for a specific deployment of the EDU AI Agent Suite on AWS. The platform's technical controls are **pre-filled** from the actual code and IaC in this repository, with file citations. Everything the institution must determine, decide, or operate is marked **[CUSTOMER TO COMPLETE]**.
>
> **What this is not.** This is not legal advice, not a FERPA/COPPA compliance certification, and not a substitute for the institution's privacy counsel. The platform provides FERPA/COPPA/IDEA/ADA-**aligned control patterns**, not a certification (see [`docs/PRODUCTION-READINESS-ACTION-PLAN.md`](../PRODUCTION-READINESS-ACTION-PLAN.md), "Compliance & accessibility posture"). The institution operationalizes, validates, and accepts accountability for the result.
>
> **Audience.** Institutional privacy officer / data protection officer, FERPA compliance owner, CISO, registrar, special-education director, and the security/architecture review board evaluating deployment on AWS.

**Scope of this PIA (first deployment is typically Agent 01):** This template is written primarily around **Agent 01 — Student & Family Services Concierge**, the recommended first deployment, but the structure applies to any of the eight agents. Complete one PIA per agent (or per logically grouped deployment) before that agent reaches production.

| Field | Value |
|---|---|
| Institution | **[CUSTOMER TO COMPLETE]** |
| Deployment / agent(s) in scope | **[CUSTOMER TO COMPLETE]** — e.g., Agent 01 Concierge |
| AWS account / region | **[CUSTOMER TO COMPLETE]** |
| Institution type | **[CUSTOMER TO COMPLETE]** — K-12 district / charter / community college / university / online / workforce |
| Serves learners under 13? | **[CUSTOMER TO COMPLETE]** — drives COPPA section |
| PIA author / date | **[CUSTOMER TO COMPLETE]** |
| Review board / approval date | **[CUSTOMER TO COMPLETE]** |

---

## 1. Purpose, Use, and Legal Basis

The agent is a **decision-support accelerator** for qualified education professionals and authenticated students/families. It retrieves approved institutional content and the acting user's own records, analyzes, drafts, recommends, and initiates **low-risk** workflows; every **consequential** action is gated to a named, authorized human (the "bright line" — README §"The bright line"). The agent never autonomously decides grades, admissions, discipline, financial aid, special-education eligibility, or student placement.

The institution must record its legal-basis determination for each regime below. **These are institutional determinations, not platform representations or legal advice.**

| Regime | What it requires | Platform alignment (pre-filled, with file cite) | Institution's determination |
|---|---|---|---|
| **FERPA** (20 U.S.C. §1232g; 34 CFR Part 99) | Protect PII in education records; a vendor/agent must act as a **"school official" under the institution's "direct control"** and use data only for the authorized educational purpose | Deny-by-default gateway (`platform_core/edu_agent_platform/mcp_gateway/policy.py`); per-tool purpose binding; **no standing credentials** (agent can be disabled per-tool immediately — `governance/README.md` §1 FERPA); PII-masked append-only audit of disclosures | **[CUSTOMER TO COMPLETE]** — Document the "school official / legitimate educational interest" determination; name the official direct-control owner; confirm DPA/contract terms bind the vendor to direct control and purpose limitation |
| **COPPA** (16 CFR Part 312) | Heightened protection for under-13; reliance on **school-authorized consent** is limited to a strictly **educational** context — **no secondary or commercial use, no behavioral profiling, no advertising** | `under_13` claim drives heightened Guardrails, heightened masking, data minimization, prohibited non-educational use (`platform_core/edu_agent_platform/auth.py` `is_under_13`; `governance/README.md` §1 COPPA; control_mappings COPPA row) | **[CUSTOMER TO COMPLETE]** — Confirm whether under-13 learners are in scope; confirm school-authorized-consent basis and its educational-purpose limit; approve Guardrail sensitivity for minors |
| **PPRA** (20 U.S.C. §1232h) | Restrict collection/disclosure of protected survey/personal categories; parental rights | Agent does not collect/infer PPRA-protected categories; intervention drafting grounded in operational signals only (`governance/README.md` §1 PPRA) | **[CUSTOMER TO COMPLETE]** — Confirm no PPRA-protected category enters grounding content or prompts; map parental-notice obligations |
| **IDEA / Section 504** | Protect IEP/504 records; **humans own eligibility and placement** | Least-privilege access to accommodation data; heightened-sensitivity masking; **bright-line HITL gate** — agent drafts/retrieves, a named human decides (`governance/README.md` §1 IDEA/504; policy.py HITL) | **[CUSTOMER TO COMPLETE]** — Name the IEP/504 team that owns eligibility/placement; confirm no agent output is treated as a determination |
| **GLBA Safeguards Rule** (Title IV financial-aid data) | Safeguard student financial information | KMS CMK encryption in transit/at rest; least privilege; **financial-identifier masking** (SSN, card via Luhn, long account IDs — `platform_core/.../pii_masker/__init__.py`); access logging (control_mappings GLBA row) | **[CUSTOMER TO COMPLETE]** — Confirm financial-aid data flows are in scope; map to the institution's GLBA safeguards program |
| **State student-privacy law** (e.g., **SOPIPA**, **NY Ed Law §2-d**, ~140 statutes) | Limit vendor use; deletion; security; transparency; data-localization; breach-notification; vendor-contract terms | Parameterized: data-residency (region/VPC), retention windows, consent capture, prohibited-use are **configuration, not code** (`governance/README.md` §1 state law; control_mappings state-law row) | **[CUSTOMER TO COMPLETE]** — Identify the applicable state statute(s); map each requirement (e.g., NY Ed Law §2-d data-privacy agreement + parents' bill of rights) to a configuration and contract term |

---

## 2. Data Inventory

Categories of education records / PII the **Agent 01 Concierge** touches, with source system and the four privacy properties for each. (Other agents touch additional categories — see `platform_core/edu_agent_platform/mcp_gateway/policy.py` `TOOL_REGISTRY` for the full per-agent tool surface.)

| Data category | Source system / tool | Purpose | Lawful basis | Minimization | Retention |
|---|---|---|---|---|---|
| **Student identity & profile** (name, student ID, DOB, contact) | SIS — `sis.get_student_profile` | Authenticate context; answer status/schedule questions | FERPA education record; institution's "school official" determination | Connector returns only fields the tool needs; identifiers masked to stable pseudonyms before prompt/audit (pii_masker) | **[CUSTOMER]** WORM window |
| **Class schedule** | SIS — `sis.get_schedule` | Answer "when/where is my class" questions | FERPA education record | Record-scoped to the acting student; record-scope enforced (`policy.record_scope_ok`) | **[CUSTOMER]** |
| **Application / financial-aid status** | SIS / aid — `sis.check_application_status` | Status look-up and plain-language explanation; **the agent never decides aid** | FERPA + **GLBA** (Title IV data) | Status only; financial identifiers masked (SSN/card/account) | **[CUSTOMER]** |
| **Family / guardian contact & relationship** | SIS / CRM identity claims | Scope guardian access; outreach drafting | FERPA (pre-transfer) / guardian relationship claim | Guardian access scoped; **dropped when rights transfer** (auth.py `roles_from_claims`) | **[CUSTOMER]** |
| **Case / advising records** | CRM — `crm.get_case`, `crm.create_advising_case` | Open/track a case; schedule an appointment (low-risk workflow) | FERPA education record | Record-scoped; create-case is low-risk (no HITL), commit-style writes are gated | **[CUSTOMER]** |
| **Approved institutional policy content** | Knowledge base — `kb.search_policies` | Grounded answers to policy/deadline questions | Institutional content (not student PII) | Grounding verification — answers trace to approved content or fail fast | **[CUSTOMER]** |
| **Outbound family/student message** | Comms — `comms.draft_message` (draft), `comms.send_message` (**consequential**) | Draft then send outreach | FERPA + consent | Draft is non-consequential; **send is HITL-gated** (policy.py `CONSEQUENTIAL_TOOLS`) | **[CUSTOMER]** |

**[CUSTOMER TO COMPLETE]** — Confirm this inventory against the agent's deployed tool grants, add any custom connectors, and assign a concrete retention window per row (see §10).

---

## 3. Data Flow & Residency

**Pre-filled (architecture, from `docs/AWS-DEPLOYMENT-REFERENCE.md` and the platform code):**

1. **Identity at the edge.** The institution's IdP (Okta / Microsoft Entra / Google Workspace / AD) federates via Amazon Cognito or IAM Identity Center; the agent **never manages its own user accounts** (auth.py module docstring). Roles derive from IdP group membership; `under_13` and `rights_transferred` are IdP-sourced claims (must **never** be self-asserted — `data.yaml` parameter guidance, PRODUCTION-READINESS P1).
2. **In-VPC processing.** The agent runtime runs in **private subnets only** (`MapPublicIpOnLaunch: false`); there is **no public inbound path to the runtime by design** (AWS-DEPLOYMENT-REFERENCE §3).
3. **Masking before inference.** The student-PII masker runs at the prompt/audit boundary, replacing identifiers, DOB, addresses, phone/email, cards, and long numeric IDs with stable pseudonyms **before** content enters a prompt or audit record (pii_masker `mask()` / `masked_pseudonym()`).
4. **Bedrock via PrivateLink.** Model inference reaches **Amazon Bedrock through an interface VPC endpoint (PrivateLink)** — the model runs in the AWS Bedrock service, reached privately, not over the public internet (AWS-DEPLOYMENT-REFERENCE §3; README "LLM Factory"). Bedrock Guardrails wrap inference.
5. **Governed egress to systems of record.** No agent calls a vendor system directly; every tool call passes the MCP gateway. S3/DynamoDB use gateway VPC endpoints; internet-facing connectors egress via NAT on HTTPS 443 only, constrained by `AllowedEgressCidr` (network.yaml).
6. **Audit & WORM.** Every attempt (ALLOW/DENY/PENDING_APPROVAL/ERROR) is written to an append-only DynamoDB audit partition; finalized artifacts to S3 Object Lock (WORM).

> **Honest scope note.** The repository describes direct identifiers as **minimized/masked before inference** and inference as **in-VPC via PrivateLink** — it does **not** claim "PII never egresses the VPC" or "in-account inference" (those overclaims were explicitly removed; see PRODUCTION-READINESS-ACTION-PLAN P0). Bedrock is an AWS service reached privately; the institution should treat Amazon Bedrock as a subprocessor under its DPA (§4).

**[CUSTOMER TO COMPLETE] — Residency decision:**
- Selected AWS **region** and confirmation it satisfies any state data-residency / in-state requirement: **[CUSTOMER]**
- Confirmation that no cross-region replication moves student data out of the chosen region unless explicitly configured: **[CUSTOMER]**
- Data-flow diagram reviewed and signed by the institution's network/security team: **[CUSTOMER]**
- Whether any connector reaches an internet-facing SoR, and the egress controls applied (`AllowedEgressCidr`, Network Firewall / egress proxy / data perimeter): **[CUSTOMER]**

---

## 4. Subprocessors

| Subprocessor | Role | Contract instrument the institution must confirm |
|---|---|---|
| **Amazon Web Services (AWS)** | Cloud infrastructure (compute, storage, KMS, networking, audit) in the institution's own account | **[CUSTOMER]** — DPA / AWS service terms; confirm AWS compliance attestations via AWS Artifact (SOC 2 Type II, ISO 27001, FedRAMP boundary if required) |
| **Amazon Bedrock** | Foundation-model inference (Claude family) reached via PrivateLink; Bedrock Guardrails | **[CUSTOMER]** — Confirm Bedrock data-handling terms (Bedrock does not use customer inference data to train base models per AWS terms); confirm in-scope under the institution's DPA; if a BAA-style instrument is required by institutional policy, confirm coverage |
| **Systems Integrator (SI)** | Builds/operates the technical controls; **does not hold standing access to student data** | **[CUSTOMER]** — TPRM review (`offerings/TPRM-DUE-DILIGENCE-PACKET.md`); FERPA "school official under direct control" determination for the SI |

**[CUSTOMER TO COMPLETE]** — Maintain the authoritative subprocessor list, execute/confirm each DPA, and confirm whether the institution's policy requires any subprocessor flow-down (e.g., NY Ed Law §2-d third-party-contractor obligations).

---

## 5. Privacy Risks & Mitigations

Each mitigation cites the actual control. Status reflects the repo's honest maturity (`PRODUCTION-READINESS-ACTION-PLAN.md`).

| Privacy risk | Mitigation (control + file) | Maturity |
|---|---|---|
| Unauthorized access to another student's record | **Deny-by-default authorization** = agent grant ∩ user entitlement; an agent can never exceed the acting human (`mcp_gateway/policy.py` `decide`); **record-level scope** — a self-scoped student/guardian may only reach their own/linked record (`policy.record_scope_ok`) | Implemented in code (live IdP wiring is Configurable) |
| PII leaking into prompts, logs, or audit | **Student-PII masking** at the prompt/audit boundary (SSN, student/case IDs, DOB/dates, email, phone, address, Luhn-validated cards, long numeric IDs) — `pii_masker/__init__.py` | Implemented |
| Agent autonomously taking a consequential action | **Framework-enforced HITL gate** — consequential tools (`comms.send_message`, `sis.update_enrollment_record`, `assessment.release_grade`, etc.) block until a verified approver identity is bound in; approvals are **signed, transaction-bound, single-use, expiring** (`policy.py` CONSEQUENTIAL_TOOLS; auth.py `record_reviewer_identity`; PRODUCTION-READINESS P0) | Implemented + tested |
| Guardian accessing records after rights transfer | At age 18 / postsecondary, **GUARDIAN role is dropped** from claims (`auth.py` `roles_from_claims`, keyed on `rights_transferred`) | Implemented |
| Tampering with or losing the disclosure record | **PII-masked append-only audit** (DynamoDB) + **WORM** finalized snapshots (S3 Object Lock); FERPA recordkeeping of disclosures | Implemented (enforcement of append-only via IAM is defense-in-depth; see action plan P1/P2) |
| Secondary / commercial use of student data | Purpose-of-use bound per tool; **no secondary use** policy at the gateway; COPPA prohibition on profiling/advertising for under-13 | Configurable (institution approves purpose policy) |
| Hallucinated policy, deadline, or status reaching a family | **Grounding verification** — facts trace to approved content or fail fast (`governance/grounding.py`) | Implemented |
| Unverified / mutable identity claims | `verify_jwt` **rejects pre-decoded claims outside demo mode**; production requires a signed JWT / verified authorizer context; claims must be IdP-sourced (auth.py; PRODUCTION-READINESS P0/P1) | Implemented (wiring to real authorizer is Configurable) |
| Disparate impact in any flag/rank workflow (Title VI/OCR) | **Four-fifths disparate-impact + representativeness screen**, human equity review, no automated adverse action (`governance/fairness/disparate_impact.py`) | Implemented |

### Residual risks (be honest — do not over-claim)

These remain open or customer-owned at the time of writing; cross-reference [`docs/PRODUCTION-READINESS-ACTION-PLAN.md`](../PRODUCTION-READINESS-ACTION-PLAN.md):

- **AgentCore Gateway/Runtime are provisioning *contracts*** — without a customer-supplied custom-resource provisioner the templates write config to SSM and return `PENDING-PROVISION`. The **native Step Functions + Lambda path with a `waitForTaskToken` HITL gate is real**. (Action plan, "Validation" + P2.)
- **Identity, real connectors, and live IdP federation are customer-engagement work** (action plan P2/P3) — the deployment is not FERPA-complete until these are wired and tested.
- **Externalized policy (Cedar / Verified Permissions)** to prevent drift between the Python model and the deployed authorizer is **planned** (P3).
- **No penetration test** has been performed on a customer deployment; that is a production-readiness gate (README maturity ladder).
- **Compliance is not certified** — the platform provides aligned control patterns; FERPA/COPPA/state-law compliance accountability is the institution's (action plan, "Compliance & accessibility posture").

**[CUSTOMER TO COMPLETE]** — Accept, mitigate, or transfer each residual risk; record the decision and owner.

---

## 6. Data-Subject Rights

| Right | How the platform supports it | Institution's process |
|---|---|---|
| **Access** (student/parent inspection of records) | The append-only, PII-masked audit trail records who accessed what, on what basis, and who approved any action — the institution can produce disclosure records (governance/README §1 FERPA; SHARED-RESPONSIBILITY-MATRIX "Audit trail") | **[CUSTOMER]** — Define the inspection-request workflow and SLA |
| **Correction / amendment** | Enrollment-record writes are **staged then human-committed** (`sis.update_enrollment_record` is consequential); corrections flow through the registrar with an audit record | **[CUSTOMER]** — Define the FERPA amendment-request procedure |
| **Deletion** | Configurable retention/deletion windows; data-class isolation; S3 lifecycle (state-law deletion requirements — control_mappings state-law row) | **[CUSTOMER]** — Map state deletion obligations; configure windows |
| **Rights transfer / guardian scope** | Automated drop of guardian access at age of majority (auth.py) | **[CUSTOMER]** — Ensure the IdP carries accurate age-of-majority and guardian-relationship data (the most common readiness gap — SHARED-RESPONSIBILITY-MATRIX) |

---

## 7. Retention & Deletion

- **WORM retention is now a forced parameter.** The 7-year default was removed; `data.yaml` requires `WormRetentionDays` and a `WormMode` (GOVERNANCE / COMPLIANCE) decision — the institution **must** choose a retention window aligned to its records schedule (PRODUCTION-READINESS P1).
- Append-only DynamoDB audit retains AI decision traces; S3 Object Lock (COMPLIANCE mode) immutably retains originals and derived versions (governance/README §1 retention; Agent 07 compliance doc §4).
- Data minimization (connectors return only needed fields) reduces the retained surface.

**[CUSTOMER TO COMPLETE]** — Set `WormRetentionDays` and `WormMode`; map to the institution's records-retention schedule; define legal-hold and deletion procedures; confirm state-law deletion timelines.

---

## 8. Incident & Breach Response

- The SI's technical role (detection, containment, evidence production) is defined in `runbooks/INCIDENT-RESPONSE.md`; the SI notifies the institution within **48 hours** of confirmed discovery (SHARED-RESPONSIBILITY-MATRIX).
- The **legal breach-notification determination** and notifications to students, parents, and regulators are the **institution's**, owned under FERPA and applicable state breach-notification law.

**[CUSTOMER TO COMPLETE]** — Confirm the institution's own breach-notification procedure, regulator/parent notification timelines (incl. state-specific), and the named incident owner.

---

## 9. Customer Responsibility Summary (cross-reference)

Per [`docs/SHARED-RESPONSIBILITY-MATRIX.md`](../SHARED-RESPONSIBILITY-MATRIX.md) and `governance/README.md` §5, the institution **owns**: the FERPA/COPPA/PPRA compliance program and data-governance policy; the "school official / direct control" determination and DPA; IdP integration and role mapping (guardian relationships, age-of-majority); Bedrock Guardrail tuning for its population (incl. minors); state student-privacy-law mapping; connector validation; records-retention configuration; Guardrail/Grounding content approval; reviewer roster for HITL; and change control for prompt/model updates.

---

## 10. Sign-off

| Role | Name | Determination / approval | Signature | Date |
|---|---|---|---|---|
| **Privacy Officer / DPO** | **[CUSTOMER]** | Legal basis & data inventory accepted | | |
| **CISO** | **[CUSTOMER]** | Security controls & residual risk accepted | | |
| **Data Owner / Registrar** | **[CUSTOMER]** | Data flows, retention, and rights processes accepted | | |
| **FERPA "school official" / direct-control owner** | **[CUSTOMER]** | Direct-control determination confirmed | | |

> This PIA must be re-reviewed on any change to: the agent's tool grants, the connector set, the IdP claim model, the retention configuration, the AWS region, or the Bedrock model/prompt version (change control — SHARED-RESPONSIBILITY-MATRIX).
