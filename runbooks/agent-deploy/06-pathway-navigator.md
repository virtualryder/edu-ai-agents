# Agent 06 — Academic / College / Career Pathway Navigator — Deploy Runbook

> Per-agent runbook. The **shared secure request path** is in [`docs/AWS-DEPLOYMENT-REFERENCE.md`](../../docs/AWS-DEPLOYMENT-REFERENCE.md). Stand the platform up once per environment, then deploy Agent 06. This covers only Pathway Navigator specifics.

**Agent id:** `06-pathway-navigator`
**Governance intensity: higher** — pathway/placement. It presents options; **placement is human.**

---

## 1. What it does + the bright line

Runs degree audits and prerequisite checks, reads graduation requirements and transfer credits, surfaces career pathways from labor-market data, and schedules advising appointments. It **presents options and recommendations**.

**Bright line — human-owned (not a tool gate here):** **placement is a human decision.** This agent has **no consequential tools** in its grant set — `crm.schedule_appointment` is a low-risk workflow write. The safety property is that the Navigator never *enrolls* or *places* a student; it recommends, and a human (and the SIS as system of record) owns the actual placement/enrollment. Degree/prerequisite logic is **deterministic** (Layer 5), so outputs are consistent and inspectable.

---

## 2. Agent creation

- **Runtime config:** `agent-service.yaml`, `AgentId=06-pathway`. Either `DeployMode`; native suits the deterministic rules engine.
- **Prompt registry:** the Pathway Navigator prompt (pinned).
- **Model + Guardrail:** Bedrock Claude for narrative explanation; **degree audit / graduation / prerequisite rules are deterministic Python**, not the LLM. Guardrail active on generative steps.

---

## 3. Tools it needs

From `AGENT_TOOL_GRANTS["06-pathway-navigator"]`:

| Tool | Connector | R/W | Consequential? |
|---|---|---|---|
| `sis.get_student_profile` | SIS | read | no |
| `sis.get_graduation_requirements` | SIS | read | no |
| `sis.get_transfer_credits` | SIS | read | no |
| `rules.run_degree_audit` | rules | deterministic | no |
| `rules.check_prerequisites` | rules | deterministic | no |
| `labor.get_career_pathways` | labor | read | no |
| `kb.search_policies` | KB | read | no |
| `crm.schedule_appointment` | CRM | write (low-risk) | no |

- **Connectors:** SIS, a degree-audit/rules engine, labor-market data, KB, scheduling/CRM. **Secrets Manager:** `edu-agents/<env>/{sis,rules,labor,crm}`.
- **Gateway targets:** `sis`, `crm` ship; **add `rules`, `labor`, `kb`** target specs. No consequential tools to gate.

---

## 4. Per-agent infra parameters

- **CMK / data domains:** shared env CMK; audit table. No HITL writes (no consequential tools), though the audit trail of recommendations applies.
- **Real-world / labor-market data** lives in a governed data layer (Layer 4) — customer-owned sourcing/refresh.
- **Roles that approve:** none (no consequential tools). STUDENT, COUNSELOR are the entitled roles; scheduling is a low-risk write.

---

## 5. Step-by-step deploy

1. Build artifact (`scripts/local_smoke.sh 06-pathway-navigator`).
2. Create the connector secrets (`sis`, `rules`, `labor`, `crm`).
3. Register/extend gateway targets: `sis`, `crm` (+ `rules`, `labor`, `kb`).
4. Deploy:
   ```bash
   scripts/deploy.sh --env prod --agent-id 06-pathway --mode container \
     --template-bucket <cfn-bucket> --image "$IMAGE" \
     --idp-metadata https://<idp-host>/.../saml/metadata --region <region>
   ```

---

## 6. Smoke test (Pathway-specific)

- **Allowed read/analysis:** STUDENT runs a degree audit → `rules.run_degree_audit` → ALLOW + audit; deterministic result.
- **Denied over-reach:** STUDENT attempts `sis.update_enrollment_record` (placement/enrollment write — not in this agent's grants, not student-entitled) → DENY. This is the bright line surfacing as a denial.
- **Low-risk workflow allowed:** STUDENT schedules an advising appointment → `crm.schedule_appointment` → ALLOW (no HITL gate; it is non-consequential).

---

## 7. Teardown notes

Standard reverse-order teardown (master §13). No pending approvals to drain. Audit table + CMK are `Retain`.
