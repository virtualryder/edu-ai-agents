# Agent 04 — Assessment, Grading & Feedback — Deploy Runbook

> Per-agent runbook. The **shared secure request path** is in [`docs/AWS-DEPLOYMENT-REFERENCE.md`](../../docs/AWS-DEPLOYMENT-REFERENCE.md). Stand the platform up once per environment, then deploy Agent 04. This covers only Assessment specifics.

**Agent id:** `04-assessment-grading-feedback`
**Governance intensity: higher** — grading integrity. Stronger evaluation + evidence retention apply.

---

## 1. What it does + the bright line

Evaluates work against a rubric, drafts feedback, and summarizes class-wide patterns for an educator. It **never decides a final grade** — it drafts and analyzes; the educator owns the grade.

**Bright line — consequential, human-owned:** `assessment.release_grade` is HITL-gated. This is the canonical bright-line action: an agent never autonomously posts a final grade. Low-confidence evaluations route to the educator rather than proceeding.

---

## 2. Agent creation

- **Runtime config:** `agent-service.yaml`, `AgentId=04-assessment`. **Native path recommended** — the deterministic rubric-score calculation belongs in the `policy_gate`/deterministic Lambda, and the `waitForTaskToken` gate makes the grade-release approval explicit and inspectable.
- **Prompt registry:** the Assessment prompt (pinned).
- **Model + Guardrail:** Bedrock Claude for drafting feedback; **rubric scoring is deterministic Python**, not the LLM (Layer 5 deterministic service). Guardrail active on the generative feedback step.

---

## 3. Tools it needs

From `AGENT_TOOL_GRANTS["04-assessment-grading-feedback"]`:

| Tool | Connector | R/W | Consequential? |
|---|---|---|---|
| `lms.get_assignments` | LMS | read | no |
| `assessment.evaluate_rubric` | assessment | analysis | no |
| `assessment.draft_feedback` | assessment | draft | no |
| `assessment.summarize_class_patterns` | assessment | analysis | no |
| **`assessment.release_grade`** | assessment | write | **YES — HITL (bright line)** |

- **Connectors:** LMS + an assessment/rubric service. **Secrets Manager:** `edu-agents/<env>/lms`, `edu-agents/<env>/assessment`.
- **Gateway targets:** `lms` ships; **add an `assessment` target spec** with `release_grade` flagged consequential.

---

## 4. Per-agent infra parameters

- **Stronger eval + evidence retention:** this agent leans hardest on `governance/evals/` (structural regression over golden rubric-graded feedback) and on **WORM evidence retention** — every released grade's rationale and the bound approver identity should land in the S3 Object Lock store as a finalized snapshot. Confirm the WORM retention window matches the institution's grade-records schedule.
- **CMK / data domains:** shared env CMK; audit + HITL; WORM for grade-release evidence.
- **Roles that approve:** EDUCATOR releases grades. No other role is entitled to `assessment.release_grade`.

---

## 5. Step-by-step deploy

1. Build artifact (`scripts/local_smoke.sh 04-assessment-grading-feedback`); native path:
   ```bash
   scripts/package_lambdas.sh --agent 04-assessment-grading-feedback --bucket <lambda-bucket> --agent-id 04-assessment --region <region>
   ```
2. Create `lms` and `assessment` connector secrets.
3. Register/extend gateway targets: `lms` (+ `assessment`); confirm `assessment.release_grade` is gated.
4. Deploy:
   ```bash
   scripts/deploy.sh --env prod --agent-id 04-assessment --mode native \
     --template-bucket <cfn-bucket> --lambda-bucket <lambda-bucket> \
     --idp-metadata https://<idp-host>/.../saml/metadata --region <region>
   ```
5. Confirm eval + fairness checks pass in CI before pilot.

---

## 6. Smoke test (Assessment-specific)

- **Allowed read/analysis:** EDUCATOR runs `assessment.evaluate_rubric` on submitted work → ALLOW + audit; deterministic score returned.
- **Denied over-reach:** STUDENT attempts `assessment.release_grade` → DENY.
- **Consequential blocked (bright line):** agent proposes a grade → `assessment.release_grade` → PENDING_APPROVAL; the grade is **not** posted until an EDUCATOR approves and identity binds into the WORM evidence + audit row.

---

## 7. Teardown notes

Standard reverse-order teardown (master §13). Drain pending grade-release approvals. **Grade-release WORM evidence is immutable until retention expires** — plan decommissioning around it. Audit/HITL + CMK are `Retain`.
