# 02 — Personalized Tutor & Study Companion — Integration Guide

> How the Tutor connects to the LMS and course content, federates identity, scopes retrieval to the enrolled section, and exposes its tools. No agent calls a vendor system directly; every call passes through the MCP authorization gateway.

---

## 1. Connectors and APIs

| Connector | Systems (examples) | Operations the Tutor uses |
|---|---|---|
| **LMS** | Canvas, Blackboard, Schoology, Moodle, D2L | LTI 1.3 launch context, enrollment/section, course material references |
| **Course content store** | S3 + Textract-ingested PDFs/slides/worksheets | Source of grounded explanations and practice |
| **Knowledge base** | Bedrock Knowledge Base, segmented institution/course/section/role | Permission-respecting retrieval |

The LMS is the system of record for enrollment and grades. The Tutor reads context through the gateway and **never writes grades**.

---

## 2. LTI 1.3 integration

The Tutor embeds in the LMS as an **LTI 1.3 / LTI Advantage** tool (the suite's standard institution-approved interoperability interface for LMS-embedded agents):

- **Launch** carries the verified user, role (learner/instructor), course, and section context.
- **Section scoping** from the launch is the key that selects which Knowledge Base segment the tutor may retrieve from — a student's tutor reaches only the approved content for the courses/sections they are enrolled in.
- **Names and Roles Provisioning Service (NRPS)** / launch claims supply roster context where needed; the Tutor uses it for scoping, not for surfacing other students' data.
- The **instructor** launching as an instructor sees the misconception dashboard; a **learner** launching sees only their own tutoring surface.

---

## 3. Identity and role mapping

Identity federates via **Cognito / LMS SSO + AgentCore Identity** against the institution's IdP. Authorization is at Layer 3, not the LMS UI.

| Role | What the Tutor may do |
|---|---|
| **Student / learner** | Tutoring dialogue, hints, explanations, practice — scoped to own enrolled section; read own session state |
| **Instructor** | Configure source material, pedagogy, tone, prohibited behaviors, assistance level; view the aggregate misconception dashboard |
| **Guardian (K–12)** | Visibility per institution policy and FERPA rights (scoped, narrows at age of majority) |

Accommodations under IDEA/504 may shape assistance level and modality; the Tutor honors an approved accommodation but never decides eligibility.

---

## 4. The tools and their grants

Deny-by-default with least-privilege intersection. Read and write are separate tools with separate grants; the Tutor's only write is an aggregate signal.

| Tool | Type | Connector | Grant / scope | Gate |
|---|---|---|---|---|
| `get_course_materials` | Read | KB / content store | Approved materials for the student's enrolled course/section only | None (read) |
| `get_student_session_state` | Read | DynamoDB | The student's own session memory only | None |
| `generate_practice_item` | Read-equivalent (grounded generative) | KB | Practice/formative items from approved content; **never live graded items** | Guardrail-enforced |
| `surface_misconception_signal` | Write (aggregate, low-risk) | Educator dashboard | Contributes to **class-level common-misconception patterns** — **not** individual hidden scores | Audited; optional educator-review gate on publication |

The misconception dashboard is the integration design that matters most: it gives instructors signal about where the class is struggling **without** exposing per-student hidden scores — a deliberate FERPA-minimizing choice.

---

## 5. Phased connector enablement

(1) Single-course Knowledge Base, no LMS write-back, no scores; (2) add LTI 1.3 launch + Cognito/LMS SSO for authenticated, section-scoped tutoring with session memory; (3) enable the aggregate misconception dashboard. Validate the LTI launch and segmentation against the live LMS during assessment.

See: connector framework `../../platform_core/edu_agent_platform/connectors/`, gateway reference logic `../../platform_core/edu_agent_platform/mcp_gateway/`.
