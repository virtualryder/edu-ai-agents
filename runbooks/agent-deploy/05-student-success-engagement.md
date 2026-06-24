# Agent 05 — Student Success & Proactive Engagement — Deploy Runbook

> Per-agent runbook. The **shared secure request path** is in [`docs/AWS-DEPLOYMENT-REFERENCE.md`](../../docs/AWS-DEPLOYMENT-REFERENCE.md). Stand the platform up once per environment, then deploy Agent 05. This covers only Student Success specifics.

**Agent id:** `05-student-success-engagement`
**Governance intensity: higher** — outcomes + equity. Fairness-monitored; stronger evaluation and evidence retention apply. No PPRA-protected inference.

---

## 1. What it does + the bright line

Reads risk signals and intervention history, attendance, grades, and engagement; opens advising cases and drafts proactive outreach to students/families. Identifies students who may need support and routes them to a human.

**Bright line — consequential, human-owned:** `comms.send_message` (proactive outreach) is HITL-gated. The agent **recommends and drafts**; a counselor owns the decision to reach out. `crm.create_advising_case` is a low-risk workflow (not gated).

---

## 2. Agent creation

- **Runtime config:** `agent-service.yaml`, `AgentId=05-student-success`. Native path recommended for inspectable routing.
- **Prompt registry:** the Student Success prompt (pinned), with the no-PPRA-inference constraint.
- **Model + Guardrail:** Bedrock Claude under the env Guardrail. Predictive early-warning models (if used) run in **Amazon SageMaker AI**, kept separate from the explanation/human-decision stages — not in the LLM path. **No behavioral-profiling or PPRA-protected inference.**

---

## 3. Tools it needs

From `AGENT_TOOL_GRANTS["05-student-success-engagement"]`:

| Tool | Connector | R/W | Consequential? |
|---|---|---|---|
| `analytics.get_risk_signals` | analytics | read | no |
| `analytics.get_intervention_history` | analytics | read | no |
| `sis.get_attendance` | SIS | read | no |
| `sis.get_grades` | SIS | read | no |
| `lms.get_engagement` | LMS | read | no |
| `crm.create_advising_case` | CRM | write (low-risk) | no |
| `comms.draft_message` | comms | draft | no |
| **`comms.send_message`** | comms | write | **YES — HITL** |

- **Connectors:** analytics (governed student-data lake / risk signals), SIS, LMS, CRM, comms. **Secrets Manager:** `edu-agents/<env>/{analytics,sis,lms,crm,comms}`.
- **Gateway targets:** `sis`, `lms`, `crm` ship; **add `analytics` and `comms`** target specs (`comms.send_message` consequential).

---

## 4. Per-agent infra parameters

- **Stronger eval + fairness + evidence retention:** this agent is the primary consumer of `governance/fairness/` (equity / false-positive / false-negative monitoring on targeting). Retain intervention-decision evidence (the bound approver + rationale) in the WORM store.
- **Governed data lake:** `analytics.*` reads come from the S3 + Glue + Lake Formation + Redshift lake (Layer 4) with **strong limits on which data domains may be combined** — Lake Formation fine-grained access is customer-owned.
- **CMK / data domains:** shared env CMK; audit + HITL; WORM for outreach/intervention evidence.
- **Roles that approve:** COUNSELOR approves outreach (`comms.send_message`). COUNSELOR / ADMINISTRATOR are the entitled roles; STUDENT/GUARDIAN are not in this agent's user-facing path.

---

## 5. Step-by-step deploy

1. Build artifact (`scripts/local_smoke.sh 05-student-success-engagement`).
2. Create the connector secrets (`analytics`, `sis`, `lms`, `crm`, `comms`).
3. Register/extend gateway targets: `sis`, `lms`, `crm` (+ `analytics`, `comms`); gate `comms.send_message`.
4. Deploy:
   ```bash
   scripts/deploy.sh --env prod --agent-id 05-student-success --mode native \
     --template-bucket <cfn-bucket> --lambda-bucket <lambda-bucket> \
     --idp-metadata https://<idp-host>/.../saml/metadata --region <region>
   ```
5. Confirm fairness + eval checks pass in CI before pilot.

---

## 6. Smoke test (Student Success-specific)

- **Allowed read:** COUNSELOR pulls risk signals → `analytics.get_risk_signals` → ALLOW + audit.
- **Denied over-reach:** a role without analytics entitlement attempts `analytics.get_intervention_history` → DENY.
- **Consequential blocked:** agent drafts outreach and attempts to send → `comms.send_message` → PENDING_APPROVAL; sent only after a COUNSELOR approves.

---

## 7. Teardown notes

Standard reverse-order teardown (master §13). Drain pending outreach approvals. Intervention/outreach WORM evidence is immutable until retention expires. Audit/HITL + CMK are `Retain`.
