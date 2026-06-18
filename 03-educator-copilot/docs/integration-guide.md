# 03 — Educator Copilot — Integration Guide

> How the Copilot connects to the LMS, SIS, and curriculum stores, federates identity, maps the educator role, and exposes its draft-first tools. No agent calls a vendor system directly; every call passes through the MCP authorization gateway.

---

## 1. Connectors and APIs

| Connector | Systems (examples) | Operations the Copilot uses |
|---|---|---|
| **LMS** | Canvas, Blackboard, Schoology, Moodle, D2L | Create drafts (announcement/page/module/quiz), create rubric draft, extend a learner's deadline, organize modules, summarize discussions, identify missing submissions |
| **SIS (roster)** | PowerSchool, Infinite Campus, Banner, Workday Student | Read the educator's own course/section roster |
| **Curriculum / standards KB** | Bedrock Knowledge Base over approved curriculum + state standards | Grounding for drafts and differentiation |
| **Structured metadata** | Aurora / DynamoDB | Grade, subject, state standard, prerequisite, difficulty |

The LMS and SIS remain systems of record. The Copilot **creates drafts and proposes actions** through the gateway — it never publishes to students.

---

## 2. LTI 1.3 integration

The Copilot embeds in the LMS via **LTI 1.3 / LTI Advantage**:

- **Launch** carries the verified educator identity, role (instructor), course, and section — establishing the scope for roster reads and draft creation.
- **Deep Linking** is used so a drafted artifact (quiz, page, rubric) is placed back into the course **as a draft** for the educator to review and publish.
- **Assignment and Grade Services (AGS)** is **not** used to post grades — the Copilot does not grade (that is Agent 04, and even there the educator owns the grade).
- **Names and Roles (NRPS)** supplies roster/section context where the SIS connector is not the source.

---

## 3. Identity and role mapping

Identity federates via **Cognito / IAM Identity Center + AgentCore Identity** against the institution's IdP. Authorization is at Layer 3, not the LMS UI.

| Role | What the Copilot may do |
|---|---|
| **Educator / instructor** | Draft instruction/differentiation; read own roster and class results; create LMS drafts and propose scoped actions for own course/section; approve before publish |
| **Instructional designer / coach** | Drafting and differentiation within assigned courses (per institution policy) |
| **Administrator** | Configuration and oversight; not a publisher of classroom content on an educator's behalf |

The Copilot can never exceed the educator it acts for: it reads only that educator's roster and class results, and drafts only into that educator's courses.

---

## 4. The tools and their grants

Deny-by-default with least-privilege intersection; read and write separated; every write is **preview + confirm**, **idempotent**, and **gated** to educator approval.

| Tool | Type | Connector | Grant / scope | Gate |
|---|---|---|---|---|
| `get_roster` | Read | SIS / LMS | Educator's own course/section roster | None (read) |
| `get_class_results` | Read | LMS | Recent results for the educator's own class | None |
| `get_curriculum` | Read | Curriculum KB | Approved curriculum/standards | None |
| `create_lms_draft` | Write (low-risk) | LMS | Creates a **draft** (announcement/page/module/quiz); never publishes | HITL — educator approval before publish; idempotent |
| `create_rubric_draft` | Write (low-risk) | LMS | Drafts a rubric for approval | HITL; idempotent |
| `update_assignment_due_date` | Write (low-risk) | LMS | Extends a deadline for a named learner; preview + confirm | HITL; idempotent (retry-safe) |

Each write mints a short-lived, single-purpose token; no standing service accounts. Every attempt is logged ALLOW/DENY/PENDING_APPROVAL/ERROR with LMS lineage and a **version record** (source content + model config) for change control and rollback.

---

## 5. Phased connector enablement

(1) Curriculum/standards KB only — draft-to-clipboard, no LMS write; (2) add LTI 1.3 + SSO + SIS roster reads for roster-aware grounded drafting; (3) enable the three gated LMS write tools with preview/confirm and idempotency. Validate LMS actions and rollback against the live LMS during assessment.

See: connector framework `../../platform_core/edu_agent_platform/connectors/`, gateway reference logic `../../platform_core/edu_agent_platform/mcp_gateway/`.
