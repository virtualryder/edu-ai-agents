# 02 — Personalized Tutor & Study Companion
### Curriculum-grounded, instructor-controlled tutoring at a scale human tutoring cannot meet

> **24/7 help that stays inside the course — Socratic questioning, hints not answers, concept explanations, and practice — grounded in the instructor's own approved materials, with a hard bright line: it never completes a graded or prohibited assessment.**

The Tutor is a **higher-governance** agent: it touches learning and student outcomes directly, so it requires stronger evaluation, educator oversight, and safeguards than a service agent. Its differentiator is exactly what generic public AI lacks — **course context and institutional safeguards**. The instructor controls the source material, the pedagogy, the tone, the prohibited behaviors, and the level of assistance.

---

## What it does

A tutoring agent grounded in a specific course's approved content that provides:

| Capability | Behavior |
|---|---|
| **Socratic questioning** | Asks guiding questions rather than handing over answers |
| **Hints, not answers** | Scaffolds toward understanding at the instructor-set assistance level |
| **Concept explanations** | Explains using the course's own framing and vocabulary |
| **Practice questions & formative checks** | Generates practice and low-stakes checks for understanding |
| **Prerequisite review** | Reinforces foundational skills a student is missing |
| **Study planning** | Helps plan toward upcoming assessments and milestones |
| **Course-material navigation** | Points students to the right approved material |
| **Language / reading practice** | Supports language and reading fluency where the course calls for it |

The instructor configures whether the tutor leans toward **prerequisite reinforcement** or **deeper exploration**, and what it must refuse.

---

## What it solves

Students need help outside class hours at a scale human tutoring cannot meet. The default alternative — a generic public chatbot — has no knowledge of the course, no institutional safeguards, and will happily complete a graded assignment. The Tutor closes that gap: institution-controlled, curriculum-grounded, available 24/7, and bounded by instructor-set rules and platform Guardrails.

---

## Where it sits in the rollout & why

**Deploy after the best-first tier (01, 03, 07, 08).** The Tutor is high-value but **higher-governance** because it acts directly on learning:

- It requires **stronger evaluation** — outcome measurement (did learning improve?), not just usage.
- It requires **educator oversight** of source material, pedagogy, and prohibited behaviors.
- It requires the academic-integrity safeguard — **never completing a prohibited assessment** — enforced by Guardrails, not by hoping the model behaves.

It depends on the shared platform (gateway, identity, audit, Knowledge Bases) that the Concierge (01) stands up first. The honest sequencing: prove the platform and the low-risk service value with the best-first tier, then bring the learning-facing agents online with their heavier governance.

---

## AWS implementation

| Architecture role | AWS service |
|---|---|
| Course content store | **Amazon S3** (approved materials, segmented) |
| Document ingest | **Amazon Textract** (PDFs, slides, worksheets) |
| Grounded retrieval | **Amazon Bedrock Knowledge Bases**, segmented by **institution / course / section / role** |
| Semantic retrieval | **Amazon OpenSearch** (vector) |
| Tutoring strategies | **Amazon Bedrock Agent** (Claude) for Socratic/hint/explanation strategies |
| Session state | **Amazon DynamoDB** (tutoring session memory) |
| Identity | **Cognito / LMS SSO**, federating the institution's IdP |
| LMS embedding | **LTI 1.3 / LTI Advantage** integration |
| Content safety | **Amazon Bedrock Guardrails** — prevents completing prohibited assessments and unsafe content |
| Audit | Append-only **DynamoDB** + **CloudTrail** |

### Tools it exposes (read vs write)

| Tool | Type | Scope |
|---|---|---|
| `get_course_materials` | **Read** | Approved materials for the student's enrolled course/section only |
| `get_student_session_state` | **Read** | The student's own tutoring session memory |
| `generate_practice_item` | **Read-equivalent (generative, grounded)** | Practice/formative items from approved content; never live graded items |
| `surface_misconception_signal` | **Write (aggregate, gated)** | Contributes to the **teacher dashboard of common misconceptions** — aggregate patterns, **not** hidden student scores |

The Tutor's primary work is grounded retrieval and dialogue; its only "write" is an aggregate, de-identified misconception signal to the educator dashboard.

---

## Systems of record / connectors

| Category | Examples | Used for |
|---|---|---|
| **LMS** | Canvas, Blackboard, Schoology, Moodle, D2L | LTI 1.3 launch, roster/enrollment context, course/section scoping |
| **Course content store** | S3 + Textract-ingested materials | The grounding substrate |
| **Knowledge base** | Bedrock Knowledge Base segmented by institution/course/section/role | Retrieval respecting existing permissions |

The LMS remains the system of record for enrollment and grades; the Tutor reads context through the gateway and **never writes grades**.

---

## Phased adoption

1. **Read-only (start here).** Stand up a single course's approved content in a segmented Knowledge Base and offer grounded explanations, hints, and practice — no LMS write-back, no scores. Pilot with one instructor's course.
2. **Authenticated, LMS-embedded.** Add LTI 1.3 launch and Cognito/LMS SSO so the tutor scopes to the authenticated student's enrolled section and remembers session state under deny-by-default.
3. **Low-risk transactions only.** Enable the aggregate `surface_misconception_signal` to the **teacher dashboard** — common misconceptions across the class, never individual hidden scores. The Tutor still never completes a graded assessment.

---

## Regulations that apply

| Regulation | Why it applies here |
|---|---|
| **FERPA** | Session content and enrollment context are education records; identity-scoped, segmented retrieval |
| **COPPA (under-13)** | K–12 use by children under 13; heightened Guardrails, data minimization, educational-purpose-only |
| **IDEA / Section 504** | Accommodations may shape assistance level and modality; the tutor honors approved accommodations but never decides eligibility |
| **ADA / 508 / WCAG 2.2 AA** | The student-facing tutoring surface must conform |
| **Academic-integrity policy** | The bright line — never completing graded/prohibited assessments — is an integrity control |
| **State student-privacy laws** | Residency, retention, consent parameterized per state |

Full mapping: `docs/edu-compliance.md`.

---

## ROI — what to measure

Measure **learning improvement, not usage**. A tutoring agent with high usage but no measurable learning gain is not a success. Relevant categories:

| Category | Example measures |
|---|---|
| **Learning** | Formative-assessment gains, course pass/completion rate, mastery on targeted skills, reduction in repeated instructor questions |
| **Service** | 24/7 availability, after-hours help volume, time-to-help |
| **Student journey** | Persistence, course completion |
| **Risk & quality** | Integrity-violation attempts blocked, grounding-failure rate, equity of learning gains across groups |

**Caution (state it to customers):** the U.S. Department of Education's IES (Feb 2026) review found intelligent tutoring systems show **promising but implementation-dependent** results — the gain depends on instructor configuration, grounding quality, and integration, not on deploying the tool alone. Measure outcomes from the start.

---

## Proof points

- **UT Austin — "UT Sage":** a faculty-guided generative-AI tutor built on AWS using **Bedrock, Textract, Lambda, DynamoDB, OpenSearch, Cognito, ECS, S3, and Amplify**. Faculty create tutors **grounded in approved course materials**, configurable for **prerequisite reinforcement or deeper exploration** — the reference pattern for instructor-controlled, curriculum-grounded tutoring.
- **Loyola Marymount University:** deployed a **course-specific AI Study Companion** for institution-controlled, 24/7 assistance — evidence that the bounded, course-scoped model is viable in production.

---

## Maturity: **Documented**

Architecture, pedagogy controls, tool grants, and compliance design are written and reviewed — useful for discovery and architecture review; not yet runnable. Subsequent passes bring it to Demonstrated, Deployable, and Production-ready (including educator-configured grounding validation, WCAG 2.2 AA conformance, and integrity red-teaming). See `../README.md`.
