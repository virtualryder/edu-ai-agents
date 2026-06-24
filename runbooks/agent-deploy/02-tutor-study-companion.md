# Agent 02 — Personalized Tutor & Study Companion — Deploy Runbook

> Per-agent runbook. The **shared secure request path** is in [`docs/AWS-DEPLOYMENT-REFERENCE.md`](../../docs/AWS-DEPLOYMENT-REFERENCE.md). Stand the platform up once per environment, then deploy Agent 02 on top. This covers only Tutor-specifics.

**Agent id:** `02-tutor-study-companion`
**Governance intensity: higher** — it touches learning directly and is frequently student-facing, including under-13 learners (COPPA).

---

## 1. What it does + the bright line

A learner-facing study companion: explains course material, walks through assignments, and quizzes — grounded only in approved course content. It **reads**; it has **no write tools at all**.

**Bright line:** the Tutor must never complete a graded assessment for a student (academic integrity) — this is a **Guardrail** concern (`ProhibitedAssessmentCompletion` topic in `security.yaml`), not a tool grant. There are **no consequential tools** in this agent's grant set, so no HITL gate fires for its own tools; the safety boundary is the Guardrail + grounding, plus instructor-controlled scope.

---

## 2. Agent creation

- **Runtime config:** `agent-service.yaml`, `AgentId=02-tutor`. Either `DeployMode`; native is lightweight given read-only tools.
- **Prompt registry:** the Tutor's hash-pinned prompt (academic-integrity guardrails baked in).
- **Model + Guardrail:** Bedrock Claude under the env Guardrail. **Tune the Guardrail hardest here:** age-appropriate filters at COPPA grade for under-13, and the `ProhibitedAssessmentCompletion` deny topic must be active and tested against representative student inputs.

---

## 3. Tools it needs

From `AGENT_TOOL_GRANTS["02-tutor-study-companion"]`:

| Tool | Connector kind | Read/Write | Consequential? |
|---|---|---|---|
| `kb.search_course_material` | KB | read | no |
| `lms.get_course_content` | LMS | read | no |
| `lms.get_assignments` | LMS | read | no |

- **Connectors:** LMS (Canvas / Blackboard / Schoology / Moodle / D2L) and the Bedrock Knowledge Base of approved course material.
- **Secrets Manager:** `edu-agents/<env>/lms`. No comms/SIS/CRM secret needed.
- **Gateway targets:** `lms` ships in `agentcore-gateway.yaml`. **Gap:** add a `kb` target spec.

---

## 4. Per-agent infra parameters

- **CMK / data domains:** shared env CMK; audit table. No WORM artifact production (read-only), though the audit trail of student interaction still applies.
- **Knowledge base:** Bedrock Knowledge Base **segmented by course/section/role** so retrieval respects existing permissions — the customer must segment content.
- **Roles that approve:** none (no consequential tools). Scope changes (what content/courses the Tutor may use) are **instructor-controlled** configuration, not runtime approvals. STUDENT is the primary role; GUARDIAN reads are scoped.

---

## 5. Step-by-step deploy

1. Build artifact (`scripts/local_smoke.sh 02-tutor-study-companion`; then image or Lambda zips).
2. Create the `lms` connector secret.
3. Register/extend gateway targets: `lms` (+ add `kb`).
4. Deploy:
   ```bash
   scripts/deploy.sh --env prod --agent-id 02-tutor --mode container \
     --template-bucket <cfn-bucket> --image "$IMAGE" \
     --idp-metadata https://<idp-host>/.../saml/metadata --region <region>
   ```
5. **Verify the academic-integrity Guardrail topic blocks** assessment-completion requests before any pilot.

---

## 6. Smoke test (Tutor-specific)

- **Allowed read:** STUDENT asks to explain a concept → `lms.get_course_content` / `kb.search_course_material` → ALLOW + audit.
- **Denied over-reach:** STUDENT attempts any LMS write (e.g., `lms.update_assignment_due_date`) → DENY (agent not granted **and** student not entitled).
- **Guardrail block (in place of a consequential test):** STUDENT asks the Tutor to write and submit a graded essay → Guardrail `ProhibitedAssessmentCompletion` blocks; verify the block is audited.

---

## 7. Teardown notes

Standard reverse-order teardown (master §13). No pending approvals to drain (no consequential tools). Audit table + CMK are `Retain`.
