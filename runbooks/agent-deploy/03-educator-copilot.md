# Agent 03 — Educator Copilot — Deploy Runbook

> Per-agent runbook. The **shared secure request path** is in [`docs/AWS-DEPLOYMENT-REFERENCE.md`](../../docs/AWS-DEPLOYMENT-REFERENCE.md). Stand the platform up once per environment, then deploy Agent 03. This covers only Educator Copilot specifics.

**Agent id:** `03-educator-copilot`
**Governance intensity: lower (best-first)** — broad staff visibility, but it can publish to students, so two consequential tools are HITL-gated.

---

## 1. What it does + the bright line

A staff-facing copilot (surfaces in MS Teams / the LMS): reads roster, course content, assignments, engagement, and missing submissions; drafts assignments, rubrics, and announcements. Educators stay in control of anything that reaches students.

**Bright line — consequential, human-owned:**
- `lms.update_assignment_due_date` (affects a learner) — HITL-gated.
- `lms.publish_content` (to students) — HITL-gated.

The `*_draft` tools (assignment/rubric/announcement) are **not** consequential — drafts are safe; publishing is the gate.

---

## 2. Agent creation

- **Runtime config:** `agent-service.yaml`, `AgentId=03-educator-copilot`. Either `DeployMode`.
- **Prompt registry:** the Educator Copilot prompt (pinned).
- **Model + Guardrail:** Bedrock Claude under the env Guardrail. Staff-facing, but content may reach students on publish — keep age-appropriate filters active for the published surface.

---

## 3. Tools it needs

From `AGENT_TOOL_GRANTS["03-educator-copilot"]`:

| Tool | Connector | R/W | Consequential? |
|---|---|---|---|
| `lms.get_roster` | LMS | read | no |
| `lms.get_course_content` | LMS | read | no |
| `lms.get_assignments` | LMS | read | no |
| `lms.get_engagement` | LMS | read | no |
| `lms.identify_missing_submissions` | LMS | read | no |
| `kb.search_course_material` | KB | read | no |
| `lms.create_assignment_draft` | LMS | draft | no |
| `lms.create_rubric_draft` | LMS | draft | no |
| `lms.post_announcement_draft` | LMS | draft | no |
| **`lms.update_assignment_due_date`** | LMS | write | **YES — HITL** |
| **`lms.publish_content`** | LMS | write | **YES — HITL** |

- **Connectors:** LMS + curriculum/standards KB. **Secrets Manager:** `edu-agents/<env>/lms`.
- **Gateway targets:** `lms` ships (its `WriteTools`/`ConsequentialTools` already list `update_assignment_due_date` / `post_announcement`); **add `kb`**. Ensure `lms.publish_content` and `lms.update_assignment_due_date` are flagged consequential in the live target config.

---

## 4. Per-agent infra parameters

- **CMK / data domains:** shared env CMK; audit + HITL; WORM snapshots for published content provenance.
- **Roles that approve:** EDUCATOR is the acting role **and** the approver for due-date/publish actions (the educator owns what reaches their students). ADMINISTRATOR may oversee.

---

## 5. Step-by-step deploy

1. Build artifact (`scripts/local_smoke.sh 03-educator-copilot`).
2. Create the `lms` connector secret.
3. Register/extend gateway targets: `lms` (+ `kb`); confirm both consequential LMS writes are gated.
4. Deploy:
   ```bash
   scripts/deploy.sh --env prod --agent-id 03-educator-copilot --mode native \
     --template-bucket <cfn-bucket> --lambda-bucket <lambda-bucket> \
     --idp-metadata https://<idp-host>/.../saml/metadata --region <region>
   ```

---

## 6. Smoke test (Educator-specific)

- **Allowed read:** EDUCATOR pulls engagement → `lms.get_engagement` → ALLOW + audit.
- **Denied over-reach:** STUDENT (or an unentitled role) attempts `lms.publish_content` → DENY.
- **Consequential blocked:** EDUCATOR asks to publish content / change a due date → `lms.publish_content` / `lms.update_assignment_due_date` → PENDING_APPROVAL; completes only after an EDUCATOR approval binds identity.

---

## 7. Teardown notes

Standard reverse-order teardown (master §13). Drain pending publish/due-date approvals. Audit/HITL/WORM + CMK are `Retain`.
