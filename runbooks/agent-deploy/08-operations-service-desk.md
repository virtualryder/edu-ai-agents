# Agent 08 — Operations Service Desk — Deploy Runbook

> Per-agent runbook. The **shared secure request path** is in [`docs/AWS-DEPLOYMENT-REFERENCE.md`](../../docs/AWS-DEPLOYMENT-REFERENCE.md). Stand the platform up once per environment, then deploy Agent 08. This covers only Operations Service Desk specifics.

**Agent id:** `08-operations-service-desk`
**Governance intensity: lower (best-first)** by visibility, but it holds the **most consequential tools** — privileged IT remediations and financial/procurement approvals — so the HITL gate is heavily exercised. Clear **MAP modernization** candidate (displacing a legacy help desk).

---

## 1. What it does + the bright line

A staff-facing service desk (surfaces in MS Teams / the ITSM portal): reads and creates tickets, runs diagnostics, searches policy, drafts documents, and — gated — performs privileged remediations and initiates approvals.

**Bright line — consequential, human-owned (four gated tools):**
- `itsm.reset_password` — privileged.
- `itsm.restart_service` — privileged.
- `erp.initiate_approval` — financial/procurement.

(`itsm.get_ticket`, `itsm.create_ticket`, `itsm.run_diagnostic`, `erp.search_policy`, `erp.draft_document`, `kb.search_policies` are reads / low-risk workflow writes.)

---

## 2. Agent creation

- **Runtime config:** `agent-service.yaml`, `AgentId=08-operations`. **Native path recommended** — the privileged-action approval path benefits from the explicit `waitForTaskToken` gate.
- **Prompt registry:** the Operations Service Desk prompt (pinned).
- **Model + Guardrail:** Bedrock Claude under the env Guardrail; staff-facing.

---

## 3. Tools it needs

From `AGENT_TOOL_GRANTS["08-operations-service-desk"]`:

| Tool | Connector | R/W | Consequential? |
|---|---|---|---|
| `itsm.get_ticket` | ITSM | read | no |
| `itsm.create_ticket` | ITSM | write (low-risk) | no |
| `itsm.run_diagnostic` | ITSM | read | no |
| **`itsm.reset_password`** | ITSM | write | **YES — HITL (privileged)** |
| **`itsm.restart_service`** | ITSM | write | **YES — HITL (privileged)** |
| `erp.search_policy` | ERP | read | no |
| `erp.draft_document` | ERP | draft | no |
| **`erp.initiate_approval`** | ERP | write | **YES — HITL (financial)** |
| `kb.search_policies` | KB | read | no |

- **Connectors:** ITSM (ServiceNow / Jira), ERP/HR/finance/procurement, KB. **Secrets Manager:** `edu-agents/<env>/{itsm,erp}`.
- **Gateway targets:** `itsm` ships (note: its shipped `ConsequentialTools` field is empty — **you must flag `itsm.reset_password` and `itsm.restart_service` as consequential** in the live target config); **add an `erp` and `kb` target spec** with `erp.initiate_approval` gated.

---

## 4. Per-agent infra parameters

- **ITSM + privileged-action approval path:** the four gated tools make this agent the heaviest HITL user. Wire reviewer roles carefully (below) and confirm the `waitForTaskToken` timeout / fail-closed behavior suits the operational SLAs in `runbooks/HITL-QUEUE-OPERATIONS.md`.
- **CMK / data domains:** shared env CMK; audit + HITL; WORM for privileged-action evidence (who approved a password reset / service restart / financial approval).
- **Roles that approve:**
  - `itsm.reset_password`, `itsm.restart_service` → **IT_ADMIN** (the only role entitled to the privileged remediations; IT_STAFF is not).
  - `erp.initiate_approval` → **STAFF_APPROVER** (financial/procurement authority).

---

## 5. Step-by-step deploy

1. Build artifact (`scripts/local_smoke.sh 08-operations-service-desk`); native:
   ```bash
   scripts/package_lambdas.sh --agent 08-operations-service-desk --bucket <lambda-bucket> --agent-id 08-operations --region <region>
   ```
2. Create connector secrets (`itsm`, `erp`).
3. Register/extend gateway targets: `itsm` (+ `erp`, `kb`); **explicitly flag the three privileged/financial tools consequential** (the shipped `itsm` target spec leaves `ConsequentialTools` empty).
4. Deploy:
   ```bash
   scripts/deploy.sh --env prod --agent-id 08-operations --mode native \
     --template-bucket <cfn-bucket> --lambda-bucket <lambda-bucket> \
     --idp-metadata https://<idp-host>/.../saml/metadata --region <region>
   ```

---

## 6. Smoke test (Operations-specific)

- **Allowed read / low-risk write:** IT_STAFF creates a ticket → `itsm.create_ticket` → ALLOW + audit.
- **Denied over-reach:** IT_STAFF (not IT_ADMIN) attempts `itsm.reset_password` → DENY (not entitled — the privileged remediation needs IT_ADMIN).
- **Consequential blocked:** agent proposes a password reset / service restart / procurement approval → `itsm.reset_password` / `itsm.restart_service` / `erp.initiate_approval` → PENDING_APPROVAL; executes only after an IT_ADMIN / STAFF_APPROVER approves, identity bound into the audit + WORM evidence.

---

## 7. Teardown notes

Standard reverse-order teardown (master §13). **Drain pending privileged-action and financial-approval items from the HITL queue first** — orphaning these is the riskiest teardown error for this agent. Privileged-action WORM evidence is immutable until retention expires. Audit/HITL + CMK are `Retain`.
