# 04 — Assessment, Grading & Feedback
### Rubric-grounded draft evaluation and feedback — the educator owns every final grade

> **Evaluates open-ended work against a teacher-approved rubric, drafts feedback, flags misconceptions, and routes low-confidence responses to manual review — and never releases a final or high-stakes grade autonomously.**

The Assessment agent is the suite's **highest-governance** workflow: it operates on graded work, so it pairs a generative model with a **deterministic rubric and score-calculation service**, a **human-review stage**, and **sampling / double-scoring** to monitor human-agent agreement. Open-ended grading and detailed feedback are valuable but time-consuming, and delayed feedback loses instructional value — this agent compresses turnaround while keeping the educator in control of the grade.

---

## What it does

| Capability | Behavior |
|---|---|
| **Rubric-grounded evaluation** | Evaluates open-ended work against the **teacher-approved rubric** |
| **Draft feedback** | Produces specific, rubric-aligned feedback for educator review |
| **Misconception identification** | Flags recurring misconceptions in a response |
| **Reteaching suggestions** | Suggests reteaching groups based on patterns |
| **Reading fluency / spoken responses** | Evaluates oral-reading fluency and spoken responses (via Transcribe) |
| **Formative item generation** | Generates formative items from approved material |
| **Class-level patterns** | Summarizes class-level patterns for the educator |
| **Low-confidence routing** | Routes low-confidence responses to manual review |

**Final grades stay under educator control — especially high-stakes.**

---

## What it solves

Detailed, timely feedback is one of the highest-leverage things in education and one of the most time-expensive; feedback that arrives too late loses its instructional value. This agent drafts rubric-grounded evaluation and feedback fast, surfaces misconceptions and reteaching groups, and escalates the responses it is unsure about — so educators spend their time on judgment and the hard cases, not on first-pass mechanics, while keeping ownership of every grade.

---

## Where it sits in the rollout & why

**Deploy after the platform and the lower-risk learning agents are proven.** Assessment is **higher-governance** and carries the suite's strictest controls because it touches grades — a bright-line decision:

- It requires the **deterministic score service** (no LLM-arithmetic for scores), **human review on every release path**, and **double-scoring/sampling** to monitor agreement before anyone trusts the drafts.
- It depends on the shared platform, the LMS/assessment connectors, and the evidence-retention posture that earlier agents establish.

The honest sequencing: bring this online once the gateway, audit, evaluation harness, and educator trust are in place — never as a first deployment.

---

## AWS implementation

| Architecture role | AWS service |
|---|---|
| Assessment artifacts | **Amazon S3** (submitted work) |
| Handwritten / scanned ingest | **Amazon Textract** |
| Oral-reading / spoken responses | **Amazon Transcribe** |
| Rubric-grounded analysis | **Amazon Bedrock** (Claude) |
| **Deterministic rubric & score calculation** | **Deterministic service** (Lambda/Python) — **not** the LLM |
| Workflow | **AWS Step Functions** — ingest → evaluate → confidence check → human review → release |
| Results & versioned rubrics | **Amazon RDS / DynamoDB** |
| Content safety | **Amazon Bedrock Guardrails** |
| Identity | **Cognito / IAM Identity Center** + AgentCore Identity; LTI 1.3 |
| Audit | Append-only **DynamoDB** + **S3 Object Lock** + **CloudTrail** |

### Tools it exposes (read vs write)

| Tool | Type | Scope |
|---|---|---|
| `get_submission` | **Read** | A submission for the educator's own assessment |
| `get_approved_rubric` | **Read** | The versioned, teacher-approved rubric |
| `evaluate_against_rubric` | **Analyze (grounded + deterministic score)** | Drafts rubric-aligned evaluation; the **score is computed deterministically**, not by the LLM |
| `draft_feedback` | **Draft** | Produces feedback for educator review |
| `route_to_manual_review` | **Write (low-risk, gated)** | Escalates a low-confidence response to a human queue |
| `release_grade` | **Write — HARD-GATED** | Releases a grade **only** after educator approval; **never autonomous for final/high-stakes grades** |

---

## Systems of record / connectors

| Category | Examples | Used for |
|---|---|---|
| **LMS / assessment store** | Canvas, Blackboard, Schoology, Moodle, D2L | Submissions, assignment context, grade posting (educator-approved only) |
| **Rubric service** | Versioned rubric store (RDS/DynamoDB) | The teacher-approved rubric of record |
| **Artifact store** | S3 + Textract/Transcribe | Scanned/handwritten work and oral-reading audio |

The LMS gradebook remains the system of record for grades; this agent **never writes a final/high-stakes grade autonomously**.

---

## Phased adoption

1. **Read-only / draft-only (start here).** Evaluate against approved rubrics and **draft feedback for educator review with no grade write-back** — purely advisory. Begin with low-stakes formative work.
2. **Authenticated, double-scored.** Add LTI 1.3 + SSO; run **double-scoring/sampling** to measure human-agent agreement and the educator-correction rate before any release path is trusted.
3. **Low-risk transactions only.** Enable `route_to_manual_review` and, where the institution chooses, **educator-approved** grade release for **low-stakes** work via the hard-gated `release_grade`. Final/high-stakes grades remain a human action; there is **no automatic high-stakes grade release**.

---

## Regulations that apply

| Regulation | Why it applies here |
|---|---|
| **FERPA** | Submissions, feedback, and grades are education records; identity-scoped access and disclosure recordkeeping |
| **IDEA / Section 504** | Accommodations affect how work is assessed; the agent honors approved accommodations but never decides eligibility |
| **Accreditation / grading-integrity policy** | Grading integrity, evidence retention, and human-agent agreement monitoring |
| **ADA / 508 / WCAG 2.2 AA** | Feedback surfaces shown to students must conform |
| **State student-privacy laws** | Residency, retention, consent parameterized per state |

Full mapping: `docs/edu-compliance.md`.

---

## ROI — what to measure

| Category | Example measures |
|---|---|
| **Labor** | Grading time per item/class, educator hours on first-pass mechanics |
| **Service** | Feedback turnaround time, **% of work receiving feedback** |
| **Learning** | Student revision/learning improvement after feedback |
| **Risk & quality** | **Human-agent scoring agreement**, low-confidence escalation rate, **educator correction rate**, equity of scoring across groups |

---

## Proof points

- **Benchmark Education** built an AWS solution (**Bedrock, RDS, Step Functions, Lambda**) to help grade **open-ended literacy assessments** with faster feedback — the production reference for rubric-grounded draft evaluation with a deterministic, orchestrated pipeline.
- **Code.org** — AWS reports its **AI teaching assistant can cut the time assessing coding projects by up to 50%** — evidence for the Labor and Service (turnaround) categories.

---

## Maturity: **Demonstrated locally** (live-connector path) — not AWS-deployed

Architecture, the deterministic-score/human-review pattern, tool grants, and compliance design are written and reviewed, and the agent **runs end-to-end locally**: in demo mode (`EXTRACT_MODE=demo`, deterministic fixtures, no API key) and over a **local-HTTP live-connector path** (`CONNECTOR_MODE=live` against a local stand-in service of record — releasing a grade is gated at the gateway before any HTTP call; see `demo/DEMO-LIVE.md` and `tests/test_live_path.py`). Still customer/engagement work: a clean-account AWS deploy, real-model invocation, production IdP, a real gradebook/LMS connector, human-agent agreement validation, bias testing, evidence-retention, and accessibility conformance. Status is governed by [`../docs/STATUS-MANIFEST.md`](../docs/STATUS-MANIFEST.md); see also `../README.md`.
