# 03 — Educator Copilot — Instruction, Differentiation & LMS Workflow
### Drafts instruction, differentiates content, and executes scoped LMS actions — always educator-approved before publish

> **The educator's drafting and workflow partner: it retrieves approved curriculum and recent class results, drafts lessons / rubrics / quizzes / differentiated versions, and places a DRAFT in the LMS for the educator to approve — it never auto-publishes to students.**

The Educator Copilot is a **best-first-deployment-tier** agent (with the Concierge 01, Operations Service Desk 08, and Document & Accessibility Services 07): mature workflows, comparatively low decision-risk because nothing reaches students without educator approval, and measurable time-returned-to-instruction. It consolidates two production-oriented reference workflows — **instructional drafting/differentiation** and **LMS workflow execution** — into one copilot.

---

## What it does

**Instructional drafting & differentiation:**

| Capability |
|---|
| Lesson and course planning; standards alignment; learning objectives |
| Examples and explanations; differentiated versions; reading-level adjustments |
| Quizzes and discussion prompts; rubric creation |
| Remediation and enrichment material |
| Draft accommodations / accessibility alternatives |
| Announcements and syllabi |

**LMS workflow execution (scoped, draft-first):**

| Capability |
|---|
| Extend a deadline for a learner; create a rubric; copy course material |
| Draft an announcement; create a quiz from approved material |
| Summarize discussions; organize modules; create student groups |
| Update the calendar; identify missing submissions |

**The pattern, always:** the agent retrieves approved curriculum plus recent class results, drafts, and **places a DRAFT in the LMS for the educator to approve** — it **never auto-publishes** to students.

---

## What it solves

Educators spend disproportionate time adapting content for different levels, languages, and needs, and navigating complex LMS screens. The Copilot compresses both: it drafts and differentiates from approved curriculum, and it turns multi-click LMS chores into a single reviewed request — returning time to instruction while keeping the educator in control of everything students see.

---

## Where it sits in the rollout & why

**Deploy in the best-first tier.** The Copilot is a strong early deployment because:

1. **Draft-first means low decision-risk.** Nothing reaches a student without educator approval; the agent produces drafts and proposed LMS actions, never published artifacts.
2. **Mature, high-frequency workflows** with a clear time baseline (prep time per lesson, clicks per LMS task).
3. **Direct, attributable ROI** — time returned to instruction and administrative clicks eliminated are measurable from week one.
4. **Aligned to ED 2025 guidance**, which explicitly supports AI instructional materials, differentiated instruction, and reduced administrative burden.

It reuses the shared platform (gateway, identity, audit, Knowledge Bases) and the LTI 1.3 LMS integration that the suite standardizes.

---

## AWS implementation

| Architecture role | AWS service |
|---|---|
| Agent | **Amazon Bedrock Agent** (Claude) on **AgentCore Runtime** *or* **Step Functions + Lambda** |
| Knowledge | **Bedrock Knowledge Bases** — curriculum, standards, and policy content |
| Structured metadata | **Amazon Aurora / DynamoDB** — grade, subject, state standard, prerequisite, difficulty |
| Content gen + review | **AWS Step Functions** — content-generation-then-review workflow with HITL gate |
| Content safety | **Amazon Bedrock Guardrails** |
| LMS actions | **API Gateway + Lambda** connectors behind the **AgentCore Gateway** — actions **create drafts, not publish** |
| Version history | Source content + model config versioned for every draft (Aurora/DynamoDB + audit) |
| Identity | **Cognito / IAM Identity Center** + AgentCore Identity; LTI 1.3 launch |
| Audit | Append-only **DynamoDB** + **S3 Object Lock** + **CloudTrail** |

### Tools it exposes (read vs write)

| Tool | Type | Scope |
|---|---|---|
| `get_roster` | **Read** | The educator's own course/section roster |
| `get_class_results` | **Read** | Recent results for the educator's own class (to ground differentiation/remediation) |
| `get_curriculum` | **Read** | Approved curriculum/standards content |
| `create_lms_draft` | **Write (gated)** | Creates a **draft** (announcement, page, module, quiz) in the LMS — never publishes |
| `create_rubric_draft` | **Write (gated)** | Drafts a rubric for educator approval |
| `update_assignment_due_date` | **Write (gated)** | Extends a deadline for a named learner; preview + confirm; idempotent |

All writes are **gated** with **preview + confirm** and **idempotency**; educator approval is required before any student distribution.

---

## Systems of record / connectors

| Category | Examples | Used for |
|---|---|---|
| **LMS** | Canvas, Blackboard, Schoology, Moodle, D2L | Create drafts, rubrics, quizzes; extend deadlines; organize modules; identify missing submissions |
| **Curriculum / standards store** | Approved curriculum + state-standards content (Bedrock KB) | Grounding for drafts and differentiation |
| **SIS (roster)** | PowerSchool, Infinite Campus, Banner, Workday Student | Roster/section context |
| **Structured metadata** | Aurora / DynamoDB | Grade, subject, standard, prerequisite, difficulty tagging |

The LMS and SIS remain systems of record; the Copilot drafts and proposes through gateway-authorized connectors and **never publishes autonomously**.

---

## Phased adoption

1. **Read-only / drafting-to-clipboard (start here).** Stand up curriculum/standards Knowledge Bases and let the Copilot draft lessons, rubrics, quizzes, and differentiated versions that the educator copies into the LMS manually. No LMS write access — fastest, lowest-risk start.
2. **Authenticated, roster-aware.** Add LTI 1.3 + SSO and the read tools (`get_roster`, `get_class_results`, `get_curriculum`) so drafts are grounded in the educator's own class context under deny-by-default.
3. **Low-risk transactions only.** Enable the gated write tools — `create_lms_draft`, `create_rubric_draft`, `update_assignment_due_date` — each preview-and-confirm, idempotent, and creating **drafts, not published content**.

---

## Regulations that apply

| Regulation | Why it applies here |
|---|---|
| **FERPA** | Roster and class-results reads touch education records; identity-scoped retrieval and audit |
| **ADA / Section 508 / WCAG 2.2 AA** | The Copilot drafts accessibility alternatives and accommodations; outputs and the educator surface must support conformance |
| **State content standards** | Drafts align to the applicable state standards (structured metadata) |
| **ED 2025 AI guidance** | The Copilot operates squarely within ED-supported uses (instructional materials, differentiation, reduced burden) |
| **IDEA / Section 504** | May draft accommodation alternatives; never decides eligibility |

Full mapping: `docs/edu-compliance.md`.

---

## ROI — what to measure

| Category | Example measures |
|---|---|
| **Labor** | Prep time per lesson, time to differentiate, **admin time per course**, **clicks eliminated** per LMS task |
| **Learning** | Curriculum consistency, accessibility/language coverage of materials |
| **Service** | Adoption, reuse of approved material |
| **Student journey** | Time returned to instruction (more educator time for students) |
| **Risk & quality** | Error/rollback rates on LMS actions, draft-to-publish approval rate, grounding-failure rate |

---

## Proof points

- **U.S. Department of Education 2025 guidance** explicitly identifies **AI instructional materials, differentiated instruction, tutoring, and reduced administrative burden** as supported uses — the Copilot is designed to those supported uses.
- **Instructure's Bedrock-based IgniteAI** supports **rubric creation, assignment generation, discussion summaries, announcements, and course-material management in Canvas**; **IgniteAgent** lets an educator request, for example, a student extension, **review the proposed steps, then permit the approved Canvas API calls** — the exact review-then-permit pattern this Copilot implements.

---

## Maturity: **Documented**

Architecture, the draft-first pattern, tool grants, and compliance design are written and reviewed — useful for discovery and architecture review; not yet runnable. Subsequent passes bring it to Demonstrated, Deployable, and Production-ready (including LMS-action validation, accessibility conformance, and rollback testing). See `../README.md`.
