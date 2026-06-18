# 01 — Student & Family Services Concierge — Integration Guide

> How the Concierge connects to systems of record, federates identity, maps roles, and exposes its tools. No agent calls a vendor system directly; every call passes through the MCP authorization gateway (`../../docs/WHY-THE-MCP-LAYER.md`).

---

## 1. Connectors and APIs

The Concierge integrates through the platform connector framework (`../../platform_core/edu_agent_platform/connectors/`). Each connector implements the `invoke(method, args)` interface; fixture mode in demo, live in production. The gateway does not know which backend is live.

| Connector | Systems (examples) | Operations the Concierge uses |
|---|---|---|
| **SIS** | PowerSchool, Infinite Campus, Banner, Workday Student | Read application/enrollment status, financial-aid status, student schedule |
| **CRM / case** | Slate, Salesforce EDU | Create advising case, look up inquiry, attach context |
| **Scheduling** | Institution scheduling system | Read published availability, book appointment |
| **Contact center** | **Amazon Connect** | Channel ingress (voice/SMS/chat), transfer to live agent |
| **Knowledge base** | Bedrock Knowledge Base over approved content | Grounded public answers (no SoR access) |

The Concierge does not require LTI 1.3 — it is portal/contact-center surfaced, not LMS-embedded. (LTI 1.3 applies to the LMS-embedded agents: 02, 03, 04.)

---

## 2. Identity and role mapping

Identity federates through **AgentCore Identity + Cognito / IAM Identity Center** against the institution's own IdP (Okta, Entra, Google Workspace, AD). The verified subject and roles travel with every request; the UI layer captures them but **authorization happens at Layer 3, not the UI**.

| Role | What the Concierge may do on their behalf |
|---|---|
| **Public / unauthenticated** | Public read-only answers only — no SoR access |
| **Student** | Read own status/schedule; open own case; schedule own appointment; request own forms |
| **Guardian** | Read records for a linked minor child **only while FERPA rights have not transferred** (under 18 / pre-postsecondary); scope narrows automatically at age of majority / postsecondary enrollment |
| **Staff (advisor/registrar/FA officer)** | Receives escalations, reviews `draft_family_message` before send, resolves cases |

The guardian-relationship link and the **age-of-majority / rights-transfer** state are carried in the IdP claims and enforced by the gateway: at 18 or postsecondary enrollment, a guardian agent can no longer surface the student's record.

---

## 3. The tools and their grants

Authorization is **deny-by-default with least-privilege intersection**: `permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[concierge] ∩ ROLE_ENTITLEMENTS[user_roles]`. The agent can never exceed the human it acts for, and read/write are separate tools with separate grants.

| Tool | Type | Connector | Grant / scope | Gate |
|---|---|---|---|---|
| `check_application_status` | Read | SIS / CRM | Authenticated user's own application only | None (read passes through) |
| `get_student_schedule` | Read | SIS | Authenticated student's own schedule only | None |
| `create_advising_case` | Write (low-risk) | CRM | Case for the authenticated user; identity bound into record | Reversible; audited; staff-owned thereafter |
| `schedule_appointment` | Write (low-risk) | Scheduling | Books against published availability | Reversible; audited |
| `send_form` | Write (low-risk) | CRM / comms | Sends an approved form to the authenticated user | Audited |
| `draft_family_message` | Write (low-risk) | CRM / comms | **Drafts** an outbound message; **staff approval before send** | HITL gate — named reviewer bound into record |

Each write tool mints a **short-lived, single-purpose token** per call via AgentCore Identity / STS; there are no standing service accounts. Every attempt is logged ALLOW / DENY / PENDING_APPROVAL / ERROR with lineage to the system of record.

---

## 4. Channel integration notes

- **Amazon Connect** provides voice/SMS/chat ingress; the authenticated identity (after SSO step-up in chat or verified caller flow in voice) is forwarded as IdP claims. Transfers to a live agent carry the case context.
- **Web/mobile** front ends forward the same claims; the reference Streamlit dashboard suffices for internal demos and early pilots before deep integration.
- **Multilingual**: Translate handles inbound/outbound text; Polly voices responses. Language coverage is tracked as an equity measure (`roi-analysis.md`).

---

## 5. Phased connector enablement

Mirrors the README rollout: (1) Knowledge Base only — public answers, no connectors; (2) add SIS read connectors for `check_application_status` / `get_student_schedule`; (3) add CRM/scheduling/comms write connectors for the four gated low-risk tools. Validate each connector against the live system during the assessment phase before production.

See also: connector framework `../../platform_core/edu_agent_platform/connectors/`, gateway reference logic `../../platform_core/edu_agent_platform/mcp_gateway/`.
