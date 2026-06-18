# Pilot Offering
### A 6–12 Week Pilot — One Live System of Record, the MCP Gateway in Phase 1

> A pilot is where the governed platform meets the institution's real systems and real users. It deploys one agent against **one live system of record**, in the customer's AWS account, with the **MCP authorization gateway, identity wiring, and audit trail built first** — because the gateway is the thing that passes the security and privacy review, and because every subsequent agent inherits it. The pilot's job is to move the program from "we proved the controls" to "we put a governed agent into production and measured the outcome."

This offering assumes a POC (or equivalent) has established credibility with leadership and the security/privacy function, and that a readiness assessment has mapped the customer's FERPA/COPPA posture, IdP and role model, system inventory, accessibility baseline, and state-law obligations. If those are not yet done, run `ASSESSMENT-OFFERING.md` first or in parallel — the pilot depends on its outputs.

---

## 1. The gateway-first principle (why Phase 1 is the gateway, not the agent)

The single most important sequencing decision in the pilot is that **Phase 1 builds the MCP authorization gateway, identity federation, and audit trail — before the agent does anything consequential against the live system.** This is not architectural fussiness; it is the difference between a pilot that reaches production and one that stalls.

Three reasons, drawn directly from `docs/WHY-THE-MCP-LAYER.md`:

1. **The gateway is the unlock for production, not an add-on.** Every agent's path to go-live runs through the security and privacy review. The gateway — deny-by-default authorization, least-privilege role intersection, the human-approval gate, short-lived scoped tokens, and the PII-masked append-only audit — is what *passes* that review. Build the agent first and bolt on governance later, and you rebuild the integration when the controls finally land.
2. **It is built once and reused by all eight agents.** Pay for it on the pilot agent (typically the Concierge) and Agents 02–08 inherit it. Defer it and the institution pays the integration tax eight times.
3. **Retrofitting governance is the most expensive thing in the program.** Adding identity, least privilege, approval gates, and audit *after* an agent is wired means touching every integration and re-reviewing privacy and accessibility.

The customer chooses the gateway's hosting model during the assessment — managed **AgentCore Gateway**, AWS primitives (**API Gateway + Lambda + Step Functions**), or a self-built **FastMCP** server. The enforcement semantics are identical across all three (reference logic in `platform_core/edu_agent_platform/mcp_gateway/`), so the pilot's authorization, human-gate, and audit behavior do not change with the hosting choice.

---

## 2. Scope

### Pilot agent and system of record
The default pilot pairs **01 Concierge** with one live SIS or CRM (e.g., PowerSchool, Banner, Workday Student, Slate, or Salesforce EDU) for a status-and-case workflow — the same pattern proven at UA–Pulaski Tech (MyAgent) and Highline College (financial-aid self-service). Alternative pilots land on **08 Operations Service Desk** against a live ITSM (ServiceNow/Jira), **03 Educator Copilot** against a live LMS (Canvas/Blackboard/Schoology), or **07 Document & Accessibility Services** against the SIS/document store. These four are the best-first set. Higher-governance agents (02, 04, 05, 06) are pilot candidates only after the institution has run a best-first agent and its governance function is ready for the deeper evaluation, bias-testing, and evidence-retention they require.

### One system, on purpose
The pilot deliberately wires **one** live system of record. This bounds the security review, the connector validation, and the data-governance surface, and it lets the team prove the full governed loop end-to-end before fanning out. Additional systems and additional agents are the *expand* motion that follows a successful pilot (see `SOLUTION-FIELD-GUIDE.md`).

### In scope
- Phase 1 gateway, identity federation (customer IdP via IAM Identity Center / Cognito), and the append-only audit trail, in the customer's AWS account.
- One agent deployed against one live system of record through a validated connector.
- Role mapping operationalized for the roles relevant to the pilot (student / guardian / educator / counselor / administrator, with age-of-majority and guardian-relationship state carried in claims).
- The HITL gate enforced on the pilot's consequential actions, with a working reviewer queue.
- Bedrock Guardrail configuration appropriate to the pilot population (heightened for minors / under-13 where relevant).
- Grounding verification against a defined slice of approved institutional content.
- WCAG 2.2 AA conformance testing of the pilot's student- or staff-facing surface.
- Baseline capture and outcome measurement (see §5 and `COST-ROI-MODEL.md`).
- A bounded pilot user population and scenario set.

### Out of scope (deferred to production rollout / portfolio expansion)
- Additional agents beyond the pilot agent.
- Additional systems of record beyond the one live system.
- Full-population rollout (the pilot runs against a bounded cohort).
- The emerging/roadmap use cases (longitudinal orchestration, precision-learning teams, autonomous operations, dialogue-based assessment) — explicitly not pilot scope.

---

## 3. Phases and milestones (6–12 weeks)

| Phase | Weeks (12-wk plan) | Milestone | Exit gate |
|---|---|---|---|
| **Phase 1 — Gateway & identity foundation** | 1–4 | Gateway deployed in customer AWS account; IdP federated; role mapping live for pilot roles; audit trail recording ALLOW/DENY/PENDING_APPROVAL/ERROR; PII masker operating | Security reviewer can observe a deny, a PII mask, and an audited write; no standing service accounts; short-lived scoped tokens verified |
| **Phase 2 — Live connector & grounding** | 4–6 | One live system-of-record connector validated against the vendor API; grounding content loaded; Guardrails tuned to the pilot population | Connector returns only the fields each tool needs; grounding fails fast on ungrounded output; Guardrail behavior validated for minors where relevant |
| **Phase 3 — HITL & agent workflow** | 6–8 | Pilot agent live end-to-end; HITL queue operating; reviewers trained; consequential actions provably gated | No path from intake to a consequential finalize bypasses the human gate (asserted, not assumed) |
| **Phase 4 — Accessibility & pilot launch** | 8–10 | WCAG 2.2 AA conformance tested on the pilot surface; bounded user cohort live; baseline metrics confirmed captured | Accessibility conformance evidence in hand; baseline established against the five ROI categories |
| **Phase 5 — Measure & decide** | 10–12 | Outcome measurement against baseline; incident/escalation review; exit-criteria assessment | Go/no-go to production with documented results |

A compressed 6–8 week pilot keeps Phase 1 intact (the gateway is never compressed away) and narrows the agent scenario set and cohort size; the later phases telescope but none is skipped. The accessibility gate and the HITL-bypass assertion are non-negotiable regardless of timeline.

---

## 4. Deliverables

1. **A deployed, governed gateway** in the customer's AWS account — identity federation, deny-by-default authorization, role mapping, human-approval gate, short-lived scoped tokens, and PII-masked append-only audit — reusable by every future agent.
2. **One validated live connector** to the pilot system of record, returning only the fields each narrowly-scoped tool requires.
3. **The pilot agent in production** against the bounded cohort, with grounding, Guardrails, and the HITL gate operating.
4. **A WCAG 2.2 AA conformance test report** for the pilot surface.
5. **A measured outcome report** against the pre-pilot baseline across the relevant ROI categories (Labor, Service, Learning, Student journey, Risk & quality).
6. **A security and privacy evidence package** for the institution's records: audit-trail samples (PII-masked), the authorization model, the HITL-gate test evidence, the Guardrail configuration, and the connector data-flow documentation — feeding the `TPRM-DUE-DILIGENCE-PACKET.md`.
7. **A production rollout plan**: full-population scaling, additional systems, and the portfolio-expansion sequence (which agent next, and why).

---

## 5. Measurement — outcomes, not conversations

The pilot establishes a **pre-deployment baseline** and measures the change, on outcomes the institution actually cares about. A high-usage agent with no measurable improvement is not a success; a moderate-usage agent that cuts processing time substantially is. Baseline the five categories before launch (full methodology in `COST-ROI-MODEL.md`):

| Category | Example pilot measures |
|---|---|
| **Labor** | Minutes per case, staff hours reclaimed, seasonal/overtime staffing |
| **Service** | Response time, wait time, first-contact resolution, after-hours availability |
| **Learning** | (Where relevant to the pilot agent) feedback turnaround, engagement |
| **Student journey** | Status-inquiry deflection, enrollment/application completion, persistence signals |
| **Risk & quality** | Error rate, escalation rate, override rate, privacy incidents, equity differences across cohorts |

Concierge-class pilots have credible reference outcomes to target and compare against: Highline College's ~75% reduction in financial-aid status emails/calls/visits and roughly halved FAFSA processing; UA–Pulaski Tech's 94.5% adoption and 253% admissions-engagement lift. An Operations Service Desk pilot measures deflection and cycle time; a Document Services pilot measures processing cycle time (Illinois Tech took transcript evaluation from 4–6 weeks to about a day). The pilot reports the institution's *own* numbers, not the references — the references set expectations, the pilot proves the result.

---

## 6. Exit criteria to production

The pilot exits to production when **all** of the following hold:

- **Governance proven in the live environment:** a security reviewer has confirmed deny-by-default authorization, least-privilege role intersection, PII masking, short-lived scoped tokens, and the enforced HITL gate operating against the live system — and the audit trail demonstrably records who accessed what, on what basis, and who approved each consequential action.
- **The bright line held:** the pilot agent never decided a grade, admission, disciplinary outcome, financial-aid award, special-education eligibility, or placement; every consequential action was gated to a named, authorized human.
- **Accessibility conformance evidenced:** WCAG 2.2 AA testing of the pilot surface passed (or documented remediations are scheduled and accepted).
- **Outcome demonstrated:** a measurable improvement against the baseline in at least one primary ROI category, with no unacceptable regression in Risk & quality (error rate, escalation rate, privacy incidents, equity differences).
- **Operational readiness:** the HITL queue, model/prompt change control, and incident-response paths are operating and ready to hand to a managed-service model (`MANAGED-SERVICE-OFFERING.md`).
- **A signed production rollout plan** with the portfolio-expansion sequence.

If any criterion fails, the output is a remediation plan and a re-test, not a forced go-live.

---

## 7. Related offerings

- **Before:** `ASSESSMENT-OFFERING.md` (readiness) and `POC-OFFERING.md` (demo-mode proof).
- **After:** `MANAGED-SERVICE-OFFERING.md` (run/operate) and portfolio expansion per `SOLUTION-FIELD-GUIDE.md`.
- **Supporting:** `docs/WHY-THE-MCP-LAYER.md` (gateway-first funding argument and hosting options), `COST-ROI-MODEL.md` (baseline methodology), `TPRM-DUE-DILIGENCE-PACKET.md` (the evidence package the security review consumes), `governance/README.md` (the compliance spine the pilot operationalizes).
