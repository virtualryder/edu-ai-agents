# Operational Runbooks
### EDU AI Agent Suite — Running a Governed, Human-Gated Agent Platform

> These runbooks are for the people who operate the platform after it is deployed: the on-call engineer at 2 a.m., the privacy officer assessing a possible disclosure, the registrar working an approval queue, and the compliance reviewer reconstructing what happened from the audit trail. They assume the six-layer architecture described in [`docs/SUITE-ARCHITECTURE.md`](../docs/SUITE-ARCHITECTURE.md) is already stood up.

This is a **reference accelerator, not a turnkey operations program.** The procedures below are written to be genuinely useful, but every threshold, SLA, contact, and notification timeline in them is a *placeholder the customer must replace* with values from their own incident-response policy, FERPA program, state-law obligations, and service agreements. Where that is true, the runbook says so explicitly.

---

## The bright line (read this first, keep it visible)

The agents in this suite are **bounded decision-support agents.** They retrieve approved institutional information, analyze student and operational data, draft, recommend, call approved APIs, and escalate exceptions. They do **not** autonomously decide:

> **grades · admissions · discipline · financial aid · special-education eligibility · student placement**

Every consequential action is **HITL-gated** to a named, authorized human whose identity is bound into the audit record before any write token is minted. This is not advice that happens to be wise to follow — it is enforced at Layer 3 (the MCP Authorization Gateway) and tested in `governance/tests/test_hitl_gates.py`. Several of these runbooks turn on it: a "degradation" event surfaces as humans rejecting more drafts, not as a student receiving a wrong grade; a successful prompt injection cannot exceed the permissions of the human in the loop. Keep the bright line in mind when you triage anything.

---

## The four runbooks

| Runbook | Use it when | One-line purpose |
|---|---|---|
| [`INCIDENT-RESPONSE.md`](./INCIDENT-RESPONSE.md) | Something went wrong and you need to classify, contain, and report it | Severity model, response flow, roles, and two detailed playbooks — a FERPA/student-data privacy incident and a prompt-injection / PII-exfiltration incident. |
| [`DR-RUNBOOK.md`](./DR-RUNBOOK.md) | Loss of an AZ, a region, a table, or a key; or a scheduled DR test | RTO/RPO targets per data class, backup mechanisms, restore procedures that preserve append-only / WORM guarantees, and region-failover considerations including data residency. |
| [`HITL-QUEUE-OPERATIONS.md`](./HITL-QUEUE-OPERATIONS.md) | Operating, monitoring, or reviewing the human-approval queue day to day | What the HITL queue is, which actions require approval, who reviews what, SLAs, what a reviewer sees, how approval binds identity into the record, and how to handle stale task tokens. |
| [`MODEL-DEGRADATION-RESPONSE.md`](./MODEL-DEGRADATION-RESPONSE.md) | Eval regressions, prompt drift, grounding-failure or Guardrail-block spikes, rising reviewer rejection, fairness drift | Signals monitored, thresholds to tune, and a response/rollback procedure anchored on the prompt registry, with eval + fairness re-runs as the gate to resume. |

---

## Per-agent deploy runbooks

The four runbooks above are **operational** — they pick up after the platform is running. The runbooks under [`agent-deploy/`](./agent-deploy/) are **deployment** runbooks: how to stand up each of the eight agents on the shared secure request path. They build on the master AWS deployment reference and cover only what is specific to each agent (its tools, connectors, secrets, gateway targets, consequential/HITL-gated actions, agent-specific infra, and a per-agent smoke test).

> **Start with the master.** Read [`docs/AWS-DEPLOYMENT-REFERENCE.md`](../docs/AWS-DEPLOYMENT-REFERENCE.md) first — the step-by-step shared runbook for the secure request path (KMS → network → identity → edge → JWT exchange → runtime → tools → data → observability → HITL → validation → teardown), with the layer-to-CloudFormation map and the gaps the shipped IaC does not yet cover. Stand the shared platform up **once per environment**, then deploy agents on top of it.

| # | Agent | Runbook | Consequential / HITL-gated tools |
|---|---|---|---|
| 01 | Student & Family Services Concierge | [`agent-deploy/01-student-family-concierge.md`](./agent-deploy/01-student-family-concierge.md) | `comms.send_message` |
| 02 | Personalized Tutor & Study Companion | [`agent-deploy/02-tutor-study-companion.md`](./agent-deploy/02-tutor-study-companion.md) | none (Guardrail + grounding boundary) |
| 03 | Educator Copilot | [`agent-deploy/03-educator-copilot.md`](./agent-deploy/03-educator-copilot.md) | `lms.update_assignment_due_date`, `lms.publish_content` |
| 04 | Assessment, Grading & Feedback | [`agent-deploy/04-assessment-grading-feedback.md`](./agent-deploy/04-assessment-grading-feedback.md) | `assessment.release_grade` |
| 05 | Student Success & Proactive Engagement | [`agent-deploy/05-student-success-engagement.md`](./agent-deploy/05-student-success-engagement.md) | `comms.send_message` |
| 06 | Academic / College / Career Pathway Navigator | [`agent-deploy/06-pathway-navigator.md`](./agent-deploy/06-pathway-navigator.md) | none (placement is human; no consequential tools) |
| 07 | Document & Accessibility Services | [`agent-deploy/07-document-accessibility-services.md`](./agent-deploy/07-document-accessibility-services.md) | `sis.update_enrollment_record` |
| 08 | Operations Service Desk | [`agent-deploy/08-operations-service-desk.md`](./agent-deploy/08-operations-service-desk.md) | `itsm.reset_password`, `itsm.restart_service`, `erp.initiate_approval` |

**Recommended first deployment: Agent 01.** Deploy 01/03/07/08 first (broad visibility, lower decision-risk), then expand to 02/04/05/06 (stronger evaluation, educator oversight, fairness testing, evidence retention). The bright line applies to every agent.

---

## Prerequisites — what must already exist before these runbooks work

These runbooks assume the platform was deployed per [`docs/DEPLOYMENT-HANDBOOK.md`](../docs/DEPLOYMENT-HANDBOOK.md) and that the following are live and observable. If any is missing, fix that first — a runbook that depends on an audit trail is useless without one.

| Prerequisite | Provisioned by | Why an operator needs it |
|---|---|---|
| **CloudWatch dashboards + alarms** | `infra/cloudformation/` (CloudWatch) | Invocation counts, latency, error rate, HITL queue depth, approval latency, Guardrail block rate, grounding-failure rate, deny rate — the signals every runbook triages on. |
| **CloudTrail** | `security.yaml` | API-level audit of all AWS calls; feeds the same unified compliance record as gateway events. |
| **Append-only audit table** | `data.yaml` (DynamoDB) | `deny:UpdateItem` / `deny:DeleteItem` on the audit partition, PITR enabled. The source of truth for "who accessed what, on what basis, who approved." |
| **WORM snapshot / document store** | `data.yaml` (S3 Object Lock, COMPLIANCE mode) | Tamper-evident retention for finalized audit snapshots and submitted documents. The evidence you preserve in an incident. |
| **HITL queue table** | `data.yaml` (DynamoDB) | The pending-approval queue; the `waitForTaskToken` / `interrupt_before` gate writes and reads here. |
| **KMS customer-managed keys** | `security.yaml` | Separate key per environment; key policy restricts to the agent role. Losing the CMK loses the data — treat it as a hard dependency in DR. |
| **Bedrock Guardrails** | `security.yaml` | Block-rate signal feeds incident and degradation triage; tuning is a customer responsibility. |
| **Prompt registry + manifest** | `governance/prompt_registry.py`, `prompt_manifest.json` | Hash-pinned prompts; the rollback target for degradation and the integrity check after a prompt-injection incident. |

> **Customer must configure:** alarm thresholds, alarm-to-pager routing, log-retention windows, the actual contact list behind each on-call role, and which environment's CMK maps to which alias. None of these ship with usable defaults.

---

## On-call roles

The runbooks reference these roles. Map each to named people and a paging path in your own runbook front-matter; the suite does not ship a roster.

| Role | Primary responsibility in operations |
|---|---|
| **On-call operator / SRE** | First responder. Detects, triages, contains (can disable any tool or agent at the gateway immediately), and drives recovery. |
| **Incident commander (IC)** | Owns the incident end to end once declared; coordinates roles, decisions, and the timeline. |
| **Privacy officer / FERPA program owner** | Owns any student-data privacy determination, the unauthorized-disclosure assessment, and breach-notification decisions. |
| **CISO / security lead** | Owns security containment, forensics, and the call on scope of compromise. |
| **Communications lead** | Owns internal and external messaging; works from the privacy officer's and IC's determinations. |
| **Reviewers (educator / counselor / registrar / administrator)** | The named humans behind the HITL gate. Not on-call for infrastructure, but on the hook for approval SLAs and the bright-line decisions. |

> **Customer must configure:** the actual roster, the paging tool, the escalation timers, and the authority each role holds. Identities are federated from the institution's IdP and carry the `custom:edu_role` attribute (student / guardian / educator / counselor / administrator); operational roles above are an overlay your organization defines.

---

## How these fit the rest of the documentation

- **Architecture and service mapping:** [`docs/SUITE-ARCHITECTURE.md`](../docs/SUITE-ARCHITECTURE.md) — the six layers, the AWS services, and where each control lives.
- **Compliance spine:** [`governance/README.md`](../governance/README.md) — FERPA, COPPA, PPRA, IDEA/Section 504, ADA/508/WCAG 2.2 AA, ~140 state student-privacy laws, the bright line, and what the customer still owns.
- **Deployment:** [`docs/DEPLOYMENT-HANDBOOK.md`](../docs/DEPLOYMENT-HANDBOOK.md) — empty AWS account to a running, governed, human-gated agent. The runbooks pick up where this leaves off.

Post-incident and post-degradation findings feed **back** into governance — new eval cases (`governance/evals/`), new red-team cases (`governance/redteam/`), and prompt-registry entries. Operations and governance are one loop, not two functions.
