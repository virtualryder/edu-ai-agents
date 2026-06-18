# 02 — Personalized Tutor & Study Companion — ROI Analysis

> For the Tutor, ROI is measured on **learning outcomes, not usage**. A tutoring agent with high usage but no measurable learning improvement is not a success. Baseline first, then measure. Full model: `../../offerings/COST-ROI-MODEL.md`.

---

## 1. The baseline-then-measure model

Before deployment, baseline the learning measures for the pilot course(s). After each phase, re-measure and attribute change — being honest about confounders (a single instructor's configuration, cohort differences, concurrent interventions). The dominant categories are **Learning** and **Student journey**; Service is secondary; Risk & quality is a guardrail.

| Category | Example measures | Baseline source |
|---|---|---|
| **Learning** | Formative-assessment gains, mastery on targeted skills, course pass/completion rate, reduction in repeated instructor questions | LMS gradebook (formative), instructor logs |
| **Service** | After-hours help volume, time-to-help, 24/7 availability | Tutor session logs |
| **Student journey** | Persistence, course completion, prerequisite remediation success | SIS, LMS |
| **Risk & quality** | Integrity-violation attempts blocked, grounding-failure rate, equity of learning gains across groups | Audit trail, fairness reports |

---

## 2. The honest caveat — anchor expectations to the evidence

The U.S. Department of Education's **IES (Feb 2026) review** found intelligent tutoring systems show **promising but implementation-dependent** results. Translate that to the customer directly: the gain comes from **instructor configuration, grounding quality, and integration into the course** — not from deploying the tool alone. This is why the ROI model measures outcomes from day one and why the pilot is scoped to a course with an engaged instructor.

Verified production references for the **architecture** (not for a specific learning-gain figure):
- **UT Austin "UT Sage"** — faculty-guided, curriculum-grounded tutors on AWS (Bedrock/Textract/Lambda/DynamoDB/OpenSearch/Cognito/ECS/S3/Amplify), configurable for prerequisite reinforcement or deeper exploration.
- **Loyola Marymount University** — a course-specific AI Study Companion for institution-controlled 24/7 assistance.

Neither is cited here as a learning-gain number; they establish that the bounded, course-scoped pattern runs in production.

---

## 3. Sample before/after illustration (ILLUSTRATIVE ONLY — not a guarantee)

> Figures are **illustrative** to show how the model is populated, not projections. Replace every cell with the pilot course's own baseline.

Assume one gateway course, ~300 students, a high-DFW (drop/fail/withdraw) gateway subject, with a formative-quiz mastery baseline and an instructor who configures the tutor for prerequisite reinforcement.

| Measure | Before (baseline) | After (illustrative) | Basis |
|---|---|---|---|
| Mean formative-quiz mastery | baseline | +X pts | Targeted hint/Socratic practice |
| Repeated "office-hours basics" instructor questions | baseline | −X% | Tutor handles routine prerequisite questions |
| After-hours help availability | office hours only | 24/7 | Tutor coverage |
| Course completion / pass rate | baseline | +X pts | Earlier remediation of prerequisite gaps |
| Integrity-violation attempts (requests to complete graded work) | n/a | 100% blocked | Guardrail bright line |
| Equity gap in learning gains | baseline | monitored | Fairness checks |

**How to read it:** the value lives in Learning (mastery, completion) and the relief of routine instructor load (Service), with Risk held at zero integrity breaches. Usage volume alone is **not** in the success definition.

---

## 4. Measurement cadence and caveats

- **Tie every measure to a learning instrument**, not to session counts. If mastery and completion don't move, the deployment is not yet successful regardless of engagement.
- **Hold integrity as a hard floor** — track and report blocked attempts to complete prohibited assessments; this protects the academic-integrity case for the program.
- **Watch equity** — confirm gains are not concentrated in already-advantaged groups (fairness monitoring, `../../governance/fairness/`).
- **Attribute conservatively** — the IES caveat means a single positive course is encouraging, not proof; expand only after replicating the gain.

Portfolio roll-up: `../../offerings/COST-ROI-MODEL.md`.
