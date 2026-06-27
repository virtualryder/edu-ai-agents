# Agent 05 — Integration Guide
### Connectors, identity and role mapping, tools and grants, and the gateway flow

> Agent 05 acts on student records and reaches families through real channels. Every one of those actions runs through the **MCP authorization gateway**: no connector is called directly, read and write are separate tools with separate grants, and any consequential or sensitive write blocks at the HITL gate until a named human is bound into the record. This guide describes the connectors, the identity/role mapping the gateway enforces, the tool grants, and the end-to-end flow. See `../../docs/WHY-THE-MCP-LAYER.md` for why this layer exists and `../../platform_core/edu_agent_platform/mcp_gateway/` for the reference logic.

---

## 1. Connectors and API integration

Each connector is a per-system adapter implementing the `invoke(method, args)` interface, returning only the fields a tool needs (data minimization, no redisclosure). The connector interface is identical in demo (deterministic fixtures) and production (live APIs) — the gateway does not know which backend is live.

| Connector | Example systems | Role in Agent 05 | Access |
|---|---|---|---|
| **SIS** | PowerSchool, Infinite Campus, Banner, Workday Student | Attendance, enrollment, application status, financial-aid item status | Read |
| **LMS** | Canvas, Blackboard, Schoology, Moodle, D2L | Engagement signals, missing assignments | Read |
| **Advising / case management** | Slate, Salesforce EDU, institutional case system | Prior advising history; case create/update/escalate | Read + **Write** |
| **Comms / contact center** | Amazon Connect, SES, SNS | Communication preferences and opt-out; approved outreach send | Read + **Write** |
| **Governed student-data lake** | S3 + Glue + Lake Formation + Redshift | Domain-limited analytics substrate for evidence assembly | Read |
| **Predictive model service** | SageMaker AI endpoint | Early-warning prediction, where justified — an input, never a verdict | Read |

The case-management connector is fronted by **API Gateway**; the comms connector fronts **Amazon Connect + SES + SNS**. Connectors are registered as **AgentCore Gateway** targets (one per system of record) in `../../infra/cloudformation/agentcore-gateway.yaml`.

---

## 2. Identity and role mapping

Identity arrives as verified IdP claims (the institution's own SSO via **IAM Identity Center / Cognito**, federating Okta / Entra / Google Workspace / AD). The gateway never trusts the UI for authorization — the UX layer only forwards claims and role. Authorization is **deny-by-default with least-privilege intersection**: the agent can never do more than the human on whose behalf it acts.

`permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[05] ∩ ROLE_ENTITLEMENTS[user_roles]`

| Role | What Agent 05 may do for this role | Hard scoping the gateway enforces |
|---|---|---|
| **Student** | View their own assembled signals and any outreach addressed to them | Own record only; survey signals only within stated consent (PPRA) |
| **Guardian** | View signals and outreach for a student they have rights to | **Age-of-majority / rights transfer**: at 18 / postsecondary enrollment, FERPA rights transfer to the student and guardian access narrows; guardian-relationship scoping enforced |
| **Educator** | Read engagement/grade/attendance evidence for their roster; receive routed cases | Roster-scoped; no protected-category inference surfaced |
| **Counselor** | Read full assembled evidence; **approve** interventions and sensitive outreach; own and escalate cases | Caseload-scoped; named reviewer identity bound at the HITL gate |
| **Administrator** | Program-level QuickSight monitoring; configure approved templates, cadence, opt-out policy | Aggregate/de-identified where possible; no autonomous decision authority |

Guardian-relationship and age-of-majority state is carried in the IdP role mapping — a customer responsibility validated during the assessment phase (`../../governance/README.md`, §5).

---

## 3. Tools and grants — READ separated from WRITE

Read and write are distinct tools with distinct grants. Reads pass straight through; every write is **HITL-gated** — the gateway mints a short-lived, single-purpose write token only after a verified reviewer's approval is bound into the record.

| READ tool | Purpose | Source |
|---|---|---|
| `student_success.get_attendance_summary` | Authorized attendance signal | SIS |
| `student_success.get_grade_summary` | Authorized grade signal | SIS / LMS |
| `student_success.get_assessment_results` | Authorized assessment results | Assessment store |
| `student_success.get_lms_engagement` | Engagement / disengagement signal | LMS |
| `student_success.get_advising_history` | Prior interventions and cases | Case mgmt |
| `student_success.get_survey_signals` | Survey-derived signals, **consent-scoped** | Survey store |
| `early_warning.get_prediction` | Prediction input, **justified use only** | SageMaker |
| `comms.get_communication_preferences` | Channel, language, opt-out state | Comms |
| `outreach.list_approved_templates` | Approved message templates | Template registry |

| WRITE tool (HITL-gated) | Consequential / sensitive action |
|---|---|
| `case.create_success_case` | Open a student-success case with a named owner |
| `case.update_case_followup` | Record follow-up against an open case |
| `case.escalate_to_staff` | Escalate when a signal persists or a response warrants it |
| `outreach.send_approved_message` | Send approved, personalized, translated outreach via Connect/SES/SNS |
| `outreach.record_outreach_event` | Record an outreach attempt and channel |
| `outreach.log_response_and_close` | Log a response and close or route the outreach |

**The prediction read is fenced.** `early_warning.get_prediction` returns one input to the evidence-assembly stage — never a label written back to a record, never an action. The explanation stage (Bedrock) and the human-decision stage (HITL) consume *evidence*, not the score as a verdict. This separation is the architectural answer to the IES caution that prediction does not always outperform traditional early-warning systems.

---

## 4. Gateway flow

Every tool call, read or write, follows the same six-step path through the gateway (`../../docs/WHY-THE-MCP-LAYER.md`, §4):

1. **Identity verification** — verified IdP claims and role; deny on missing subject.
2. **Deny-by-default authorization** — least-privilege intersection of Agent 05's grants and the role's entitlements; purpose-of-use checked per tool (FERPA school-official / direct-control).
3. **Student-PII masking** — FERPA/COPPA identifiers replaced with stable pseudonyms before any result enters a prompt or audit record.
4. **Human approval (writes only)** — the graph suspends at the HITL gate (`interrupt_before` / `waitForTaskToken`); the draft, the grounded evidence, and the compliance report are surfaced to a named reviewer in the appropriate role; execution resumes only when a verified approval record is written.
5. **Short-lived scoped token** — minted per call via AgentCore Identity / STS; no standing service accounts.
6. **Append-only audit** — every attempt (ALLOW / DENY / PENDING_APPROVAL / ERROR) logged with lineage to the system of record.

### Outreach-specific gating

Before `outreach.send_approved_message` can be invoked, the compliance gate verifies, in order: the message uses an **approved template**; personalization is **grounded** in operational signals only (no PPRA-protected inference); the recipient's **communication preferences, guardian relationship, age-of-majority scoping, and language** resolve to an authorized channel; **opt-out is honored**; and — for any **sensitive or stigmatizing** outreach — a named human has approved it at the HITL gate. Only then is a write token minted.

---

## 5. Cross-references

- Gateway business case and options: `../../docs/WHY-THE-MCP-LAYER.md`
- Gateway reference logic: `../../platform_core/edu_agent_platform/mcp_gateway/`
- Connector framework: `../../platform_core/edu_agent_platform/`
- Gateway target registration: `../../infra/cloudformation/agentcore-gateway.yaml`
- Architecture: `../../docs/SUITE-ARCHITECTURE.md`
- Compliance: `./edu-compliance.md` and `../../governance/README.md`

---

**Maturity: Demonstrated locally — not AWS-deployed.** This agent runs end-to-end locally (demo mode + tests); a clean-account AWS deploy, real-model invocation, production identity, live connectors, and production sign-off remain customer/engagement work. Authoritative status: [`../../docs/STATUS-MANIFEST.md`](../../docs/STATUS-MANIFEST.md).
