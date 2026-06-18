# Agent 07 — Integration Guide
### Document & Accessibility Services — connectors, identity/role mapping, tools, and gateway flow

> Every tool call — read or write — passes through the MCP authorization gateway (`../../platform_core/edu_agent_platform/mcp_gateway/`). No agent has a direct network path to a system of record. This guide describes how Agent 07's tools, grants, identities, and connectors wire together. The business case for the gateway is in `../../docs/WHY-THE-MCP-LAYER.md`; the enforcement design is in `../../governance/README.md`.

---

## 1. Connector / API integration

Agent 07 talks to systems of record only through gateway-authorized connectors (`../../platform_core/edu_agent_platform/connectors/`). The connector interface (`invoke(method, args)`) is identical in demo and production; the gateway does not know which backend is live. In `EXTRACT_MODE=demo` the connectors return deterministic JSON fixtures; in production they point at the institution's live systems.

| Connector | System of record | Methods Agent 07 uses |
|---|---|---|
| SIS | PowerSchool, Infinite Campus, Banner, Workday Student | `get_application_status`, `get_required_documents`, `prepare_record_update`, `commit_record_update` |
| CRM | Slate, Salesforce EDU | `get_case`, `update_case` |
| Document store | S3 secure intake + S3 Object Lock WORM | object read for extraction; immutable write of original + extracted version |
| Knowledge base | Bedrock Knowledge Bases | `get_approved_content` for transformation |
| Media | Textract, Bedrock Data Automation, Translate, Polly, Transcribe | classification, extraction, translation, audio, captions |
| Comms | SES / SNS / Amazon Connect | `send_missing_info_request` |

Approved writes are fronted by **Amazon API Gateway** as the tool surface, with the gateway running the authorization decision and the HITL gate before any write token is minted.

---

## 2. Identity / role mapping

The agent acts on behalf of a verified human whose identity and role arrive as IdP claims (the institution's Okta / Entra / Google Workspace / AD via IAM Identity Center or Cognito). Authorization is the **least-privilege intersection** of what the agent is granted and what the human is entitled to: an agent can never do more than the person on whose behalf it acts. Guardian access is additionally scoped by the FERPA rights that transfer to the student at 18 or on postsecondary enrollment.

| Role | What they can do through Agent 07 | What they cannot do |
|---|---|---|
| **Student** | View their own application/enrollment status; submit documents; receive accessible/translated versions of their own materials | See another student's record; trigger SIS writes |
| **Guardian** | For a minor child only: submit documents, view status, request missing items, receive family communications in a preferred language | Access records after rights transfer (age of majority / postsecondary enrollment); commit any SIS change |
| **Educator** | Retrieve approved content for accessible/multilingual transformation for their students | Decide admissions; commit enrollment records |
| **Counselor** | Review document completeness for advising context; request accessible variants | Commit SIS enrollment writes; decide admissions |
| **Registrar** | Review staged updates, approve and commit SIS record updates (HITL), resolve discrepancies | Bypass the HITL gate; act without identity bound to the record |
| **Administrator** | All registrar capabilities plus configuration of thresholds and retention; disable any tool or agent immediately | Make a consequential decision without the gate; alter the append-only audit trail |

Role mapping (including guardian relationships and age-of-majority state) is owned and configured by the institution during the assessment phase.

---

## 3. Tools and grants — READ and WRITE are separate

Read and write are **separate tools with separate grants**. A grant to read application status never implies a grant to write the SIS. WRITE tools that touch consequential material are HITL-gated: they block until a verified reviewer identity is bound into the record.

| Tool | R/W | Default role grants | HITL gate |
|---|---|---|---|
| `document.classify` | READ | system (pipeline) | — |
| `document.extract_fields` | READ | system (pipeline) | low-confidence/high-sensitivity → review |
| `sis.get_application_status` | READ | student, guardian, counselor, registrar, admin | identity-scoped |
| `sis.get_required_documents` | READ | student, guardian, counselor, registrar, admin | identity-scoped |
| `kb.get_approved_content` | READ | educator, counselor, registrar, admin | identity-scoped |
| `translate.render_language` | READ | student, guardian, educator, counselor, admin | human verify for consequential material |
| `accessibility.render_variant` | READ | student, guardian, educator, counselor, admin | human verify for consequential material |
| `comms.send_missing_info_request` | WRITE | registrar, admin (templated for guardian/student notices) | identity-scoped; templated |
| `sis.prepare_record_update` | WRITE (staged) | registrar, admin | HITL gate |
| `sis.commit_record_update` | WRITE | registrar, admin | **HITL gate (named reviewer)** |
| `crm.update_case` | WRITE | registrar, admin | HITL gate for consequential changes |

**SIS/CRM update tools are WRITE and HITL-gated for consequential material.** Staging (`prepare_record_update`) is deliberately split from committing (`commit_record_update`) so the proposed change is visible and reviewable before anything touches the system of record.

---

## 4. Gateway flow

Every call follows the same six-step path through the gateway:

1. **Identity verification** — verified IdP claims; deny on missing subject; role and (for guardians) relationship/age-of-majority state carried in the claims.
2. **Deny-by-default authorization with least-privilege intersection** — `permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[07] ∩ ROLE_ENTITLEMENTS[user_roles]`.
3. **Human approval gate** — for WRITE/consequential tools, the call blocks until a verified reviewer identity is bound into the record (registrar/admin for SIS commits; verifier for consequential accessibility material).
4. **Short-lived scoped token** — minted per call via AgentCore Identity / STS; no standing service accounts.
5. **Connector invocation** — one validated connection per system; the student-PII masker runs on any inbound result before it enters a prompt or audit record; connectors return only the fields a tool needs (no redisclosure).
6. **PII-masked append-only audit** — every attempt (ALLOW / DENY / PENDING_APPROVAL / ERROR) logged with lineage to the system of record and the S3 Object Lock document version.

A read for application status passes straight through (subject to identity scope). A commit to the SIS pauses at the HITL gate until a named registrar or administrator approves — enforced by the framework, not by trusting the model.

---

## 5. Notes for the integrator

- Map the institution's document checklist to `sis.get_required_documents` so completeness validation reflects real policy, including state immunization/residency requirements.
- Tune confidence thresholds per document type and field sensitivity (see `aws-deployment-guide.md`, §4) before the enrollment season the pilot targets.
- Validate guardian-relationship and age-of-majority mapping in the IdP before any guardian-facing read is enabled — this is the most common FERPA misconfiguration.
- Confirm the connector field projection returns only what each tool needs; the masker is a backstop, not a substitute for least-privilege connector design.

---

Maturity: **Documented.**
