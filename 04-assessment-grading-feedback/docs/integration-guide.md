# 04 — Assessment, Grading & Feedback — Integration Guide

> How the Assessment agent connects to the LMS/assessment store and rubric service, federates identity, maps the educator role, and exposes its tools — with the grade-release gate at the center. No agent calls a vendor system directly; every call passes through the MCP authorization gateway.

---

## 1. Connectors and APIs

| Connector | Systems (examples) | Operations the agent uses |
|---|---|---|
| **LMS / assessment store** | Canvas, Blackboard, Schoology, Moodle, D2L | Read submissions and assignment context; post **educator-approved** grades only |
| **Rubric service** | Versioned rubric store (RDS/DynamoDB) | Read the teacher-approved rubric of record (by version) |
| **Artifact store** | S3 + Textract (handwritten/scanned) + Transcribe (oral-reading/spoken) | Normalize submitted work for evaluation |

The LMS gradebook is the system of record for grades. The agent reads submissions and rubrics through the gateway and **never writes a final/high-stakes grade autonomously**.

---

## 2. LTI 1.3 integration

The Assessment agent integrates via **LTI 1.3 / LTI Advantage**:

- **Launch** carries the verified educator, role, course, section, and the assignment context — scoping which submissions and rubric the agent may read.
- **Assignment and Grade Services (AGS)** is the channel for posting a grade — but **only after educator approval** through the hard grade-release gate. The agent never posts via AGS autonomously for final/high-stakes grades.
- **Deep Linking** surfaces draft feedback back to the educator's review queue, not directly to students.

---

## 3. Identity and role mapping

Identity federates via **Cognito / IAM Identity Center + AgentCore Identity** against the institution's IdP. Authorization is at Layer 3, not the LMS UI.

| Role | What the Assessment agent may do |
|---|---|
| **Educator / instructor** | Read own submissions and approved rubric; receive draft evaluations/feedback; approve (or correct) before any grade release; owns the final grade |
| **Reviewer (manual-review queue)** | Receives low-confidence escalations for human scoring |
| **Administrator** | Configures double-scoring/sampling and reviews agreement reports; not a grader on an educator's behalf |

The agent can never exceed the educator: it reads only that educator's assessment submissions and posts only grades the educator has approved.

---

## 4. The tools and their grants

Deny-by-default with least-privilege intersection; read, analyze, and write are separate with separate grants. The score is deterministic; grade release is hard-gated.

| Tool | Type | Connector | Grant / scope | Gate |
|---|---|---|---|---|
| `get_submission` | Read | LMS / artifact store | A submission for the educator's own assessment | None (read) |
| `get_approved_rubric` | Read | Rubric service | The versioned, teacher-approved rubric | None |
| `evaluate_against_rubric` | Analyze | — | Drafts rubric-aligned analysis; **score computed deterministically** (not the LLM) | None (advisory) |
| `draft_feedback` | Draft | — | Produces feedback for educator review | None (advisory) |
| `route_to_manual_review` | Write (low-risk) | Review queue | Escalates a low-confidence response to a human | Audited |
| `release_grade` | **Write — HARD-GATED** | LMS (AGS) | Posts **only** an educator-approved grade; **never autonomous for final/high-stakes** | **HITL — named educator approval bound into record** |

Each write mints a short-lived, single-purpose token; no standing service accounts. Every attempt is logged with LMS/rubric lineage, the rubric version used, the deterministic score, the confidence band, and the approving educator.

---

## 5. Double-scoring & agreement monitoring

A defining integration: a **sampling/double-scoring** path compares agent drafts to human scores on a configurable sample, writing **human-agent agreement** and **educator-correction-rate** metrics to the results store. These metrics gate trust — an institution does not enable an educator-approved low-stakes release path until agreement is demonstrated and monitored.

---

## 6. Phased connector enablement

(1) Read submissions + rubric, draft feedback only, **no grade write-back**; (2) add LTI 1.3 + SSO and run double-scoring/sampling to establish agreement on low-stakes formative work; (3) enable `route_to_manual_review` and educator-approved release for low-stakes work via the hard-gated `release_grade`. Final/high-stakes grades remain a human action. Validate AGS posting and rubric versioning against the live LMS during assessment.

See: connector framework `../../platform_core/edu_agent_platform/connectors/`, gateway reference logic `../../platform_core/edu_agent_platform/mcp_gateway/`.
