# Agent 01 — Student & Family Services Concierge — Deploy Runbook

> Per-agent runbook. The **shared secure request path** (KMS → network → identity → edge → gateway → runtime → data → observability → HITL) is in [`docs/AWS-DEPLOYMENT-REFERENCE.md`](../../docs/AWS-DEPLOYMENT-REFERENCE.md). Stand the shared platform up **once per environment**, then follow this to deploy Agent 01 on top of it. This runbook covers only what is specific to the Concierge.

**Agent id:** `01-student-family-concierge` (CFN `AgentId` short form: `01-concierge`)
**Recommended first deployment** — most visible to the most users, lowest decision-risk, easiest to measure. The platform controls you build here are inherited by Agents 02–08.

---

## 1. What it does + the bright line

A student/family-facing concierge: answers status/schedule/application questions, searches institutional policy, opens advising cases, schedules appointments, and drafts family messages. Surfaces in the student/family portal and **Amazon Connect** (voice/SMS/chat, after-hours), with Translate + Polly for multilingual families (Title VI).

**Bright line — consequential, human-owned:** `comms.send_message` (sending a message to a family/student) is HITL-gated. Everything else this agent does is a read or a low-risk workflow write (open a case, schedule, draft).

---

## 2. Agent creation

- **Runtime config:** `agent-service.yaml` with `AgentId=01-concierge`. `DeployMode=native` (Step Functions + `waitForTaskToken`) or `container` (AgentCore Runtime ARM64). For the Concierge most authenticated traffic is read-through, so either path carries the load.
- **System prompt / prompt registry:** the agent's hash-pinned prompt from `governance/prompt_registry.py` / `prompt_manifest.json` (Concierge entry). See `01-student-family-concierge/`.
- **Model + Guardrail:** Bedrock Claude (Sonnet for drafting, Haiku for routing) under the env Bedrock Guardrail (`GuardrailId` from `security.yaml`). K–12 deployments serve under-13 learners — confirm the COPPA-grade Guardrail profile and that `custom:under_13` drives it.

---

## 3. Tools it needs

From `AGENT_TOOL_GRANTS["01-student-family-concierge"]` in `policy.py`:

| Tool | Connector kind | Read/Write | Consequential? |
|---|---|---|---|
| `sis.get_student_profile` | SIS | read | no |
| `sis.get_schedule` | SIS | read | no |
| `sis.check_application_status` | SIS | read | no |
| `kb.search_policies` | KB | read | no |
| `crm.get_case` | CRM | read | no |
| `crm.create_advising_case` | CRM | write (low-risk) | no |
| `crm.schedule_appointment` | CRM | write (low-risk) | no |
| `comms.draft_message` | comms | draft only | no |
| **`comms.send_message`** | comms | write | **YES — HITL-gated** |

- **Connectors:** SIS (PowerSchool / Banner / Workday Student / Infinite Campus), CRM (Slate / Salesforce EDU), scheduling, comms (incl. Amazon Connect), and the Bedrock Knowledge Base for `kb.search_policies`.
- **Secrets Manager:** `edu-agents/<env>/sis`, `edu-agents/<env>/crm`, `edu-agents/<env>/comms` — CMK-encrypted (master §8).
- **Gateway targets:** `sis`, `crm` ship as target specs in `agentcore-gateway.yaml`. **Gap:** `kb` and `comms` have no target spec — add them (mirror the `SisTargetParam` block), marking `comms.send_message` consequential.

---

## 4. Per-agent infra parameters

- **CMK / data domains:** shared env CMK; audit + HITL tables; WORM bucket for finalized family-message snapshots and disclosure audit. No agent-specific store.
- **Experience layer:** Amazon Connect + Translate + Polly are Concierge-specific and **not in the shipped IaC** — wire separately; forward the same IdP claims.
- **Roles that approve:** `comms.send_message` routes to COUNSELOR / ADMINISTRATOR / FINANCIAL_AID (whichever owns the outreach). STUDENT and GUARDIAN drive reads only; GUARDIAN is scoped down once `custom:rights_transferred` is set.

---

## 5. Step-by-step deploy

Assumes the shared platform (master §1–6, §9–11) is up.

1. **Build the artifact** (master §7):
   ```bash
   scripts/local_smoke.sh 01-student-family-concierge          # prove locally
   IMAGE=$(scripts/build_and_push_image.sh --agent 01-student-family-concierge --region <region> | sed -n 's/^ContainerImageUri=//p')
   ```
   or native: `scripts/package_lambdas.sh --agent 01-student-family-concierge --bucket <lambda-bucket> --agent-id 01-concierge --region <region>`.
2. **Create the connector secrets** (master §8) for `sis`, `crm`, `comms`.
3. **Register/extend gateway targets** for `sis`, `crm`, `kb`, `comms` (add the missing `kb`/`comms` specs).
4. **Deploy the agent stack:**
   ```bash
   scripts/deploy.sh --env prod --agent-id 01-concierge --mode container \
     --template-bucket <cfn-bucket> --image "$IMAGE" \
     --idp-metadata https://<idp-host>/app/<id>/sso/saml/metadata --region <region>
   ```
   (native: add `--lambda-bucket <bucket>`, `--mode native`).
5. **Confirm** `comms.send_message` is in the gateway's consequential set so it fires the HITL gate.

---

## 6. Smoke test (Concierge-specific)

- **Allowed read:** STUDENT asks application status → `sis.check_application_status` → ALLOW + audit row.
- **Denied over-reach:** STUDENT attempts `comms.send_message` directly → DENY (not entitled) audited.
- **Consequential blocked:** Concierge drafts then attempts to **send** a family message → `comms.send_message` → PENDING_APPROVAL in HITL queue; completes only after a COUNSELOR/ADMINISTRATOR approves.

---

## 7. Teardown notes

Standard reverse-order teardown (master §13). Drain pending family-message approvals from the HITL queue first. Audit/WORM/HITL tables and the CMK are `Retain`. De-provision Amazon Connect flows separately (not in suite IaC).
