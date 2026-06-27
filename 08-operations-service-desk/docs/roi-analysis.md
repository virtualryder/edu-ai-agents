# Operations Service Desk — ROI Analysis
### Baseline-then-measure model for IT support and staff administrative workflow

> ROI is measured on outcomes, not conversations. A service-desk agent with high chat volume but no change in deflection, MTTR, or cycle time is not a success; one with moderate usage but a measurable cut in classroom downtime and approval turnaround is. This analysis follows the governance ROI model (`../../governance/README.md`) and maps Agent 08's measures to the **Labor**, **Service**, and **Risk & quality** categories. The full cost model lives in `../../offerings/COST-ROI-MODEL.md`.

---

## 1. The method: baseline first, then measure

The discipline is the same for every agent in the suite: establish a pre-deployment baseline for each metric, deploy into a bounded scope, and measure the same metrics against that baseline. Without a baseline there is no ROI claim — only anecdote. For Agent 08, baseline both capability surfaces separately, because IT-support economics and administrative-workflow economics behave differently.

1. **Define the baseline window.** Pull historical ITSM data (ticket volume, MTTR, reopen rate, first-contact resolution) and administrative-workflow data (policy-search time, document-development cycle time, approval turnaround) for a representative period — ideally spanning a term-start or enrollment-season surge so seasonality is captured.
2. **Instrument the same metrics post-deployment.** CloudWatch and the append-only audit trail provide deflection, gate, and escalation data; the ITSM system provides MTTR, reopen, and first-contact resolution; the workflow systems provide cycle and turnaround times.
3. **Attribute conservatively.** Count deflected tickets only where the agent resolved or fully prepared the resolution; count cycle-time savings only against the baselined workflow.
4. **Watch the risk metrics alongside the efficiency metrics.** A deflection gain that comes with a rising reopen rate or a rising override rate on gated actions is not a real gain.

---

## 2. Metrics by category

| Category | Metric | What it tells you |
|---|---|---|
| **Labor** | Staff hours per ticket; staff hours per administrative request; overtime; seasonal staffing | Direct staff-time recovered, especially during surge periods |
| **Labor** | Policy-search time | Minutes staff spend hunting for the right HR/finance/procurement/facilities policy |
| **Labor** | Document-development cycle time | Time from request to a usable draft of a scope, RFP, SOW, or board packet |
| **Labor** | Staff-onboarding time | Time to complete onboarding and substitute-teacher processes |
| **Service** | Ticket deflection rate | Share of inbound resolved without human handling |
| **Service** | First-contact resolution | Share resolved on first interaction |
| **Service** | MTTR (mean time to resolution) | Speed of closing a ticket end to end |
| **Service** | Classroom downtime | Instructional time lost to unresolved classroom-tech faults |
| **Service** | Approval turnaround | Time a workflow waits at the human gate |
| **Service** | Cost per request; satisfaction; after-hours availability | Unit economics and experience |
| **Risk & quality** | Reopened-ticket rate | Quality of resolution — a guard against false deflection |
| **Risk & quality** | Incomplete-request rate | Share of admin requests that stall for missing information |
| **Risk & quality** | Procurement delays | Cycle slippage in procurement/finance workflows |
| **Risk & quality** | Escalation rate; override rate on gated actions; privacy/security incidents | Whether the bright line and HITL gate are holding |

---

## 3. Illustrative before/after table

The figures below are **illustrative** — placeholder values to show the shape of the model and how the metrics relate, **not** benchmarks, guarantees, or measured results. Every number is replaced by the customer's own baseline during the assessment phase.

| Metric | Category | Baseline (illustrative) | After (illustrative) | Direction |
|---|---|---|---|---|
| Ticket deflection rate | Service | 0% (agent absent) | 35–45% of repetitive tier | ↑ better |
| First-contact resolution | Service | 52% | 70% | ↑ better |
| MTTR — password/SSO & connectivity | Service | 5.5 hours | 1.5 hours | ↓ better |
| Classroom downtime per fault | Service | 40 min | 15 min | ↓ better |
| Staff hours per ticket | Labor | 22 min | 9 min | ↓ better |
| Policy-search time per query | Labor | 12 min | 3 min | ↓ better |
| Document-development cycle (RFP/SOW draft) | Labor | 6 business days | 2 business days | ↓ better |
| Approval turnaround (procurement) | Service | 4.5 days | 2 days | ↓ better |
| Staff-onboarding completion time | Labor | 9 days | 5 days | ↓ better |
| Reopened-ticket rate | Risk & quality | 14% | ≤ 14% (held flat) | → guard |
| Incomplete-request rate | Risk & quality | 23% | 11% | ↓ better |
| Override rate on gated actions | Risk & quality | n/a | tracked, target low & stable | → guard |
| Privacy/security incidents | Risk & quality | baseline | no increase | → guard |

The guard rows matter as much as the improvement rows: the model only counts a gain as real if reopen rate, override rate, and incident rate hold steady or improve. A deflection rate that rises while reopens climb is a quality regression disguised as a win.

---

## 4. Where the return concentrates

For most institutions the return concentrates in two places. On the IT side, the repetitive tier — password/SSO, connectivity, LMS access, classroom-tech faults — is high-volume and low-decision-risk, so deflection and MTTR improvements compound quickly, and the diagnostic surface lets humans start triage already informed (the **HubbleIQ** real-world analog in `../README.md`). On the administrative side, document-development cycle time is the standout: drafting scopes, bids, RFPs, and statements of work is disproportionately time-consuming, and a grounded drafting agent compresses it materially while a separate authorized human still approves under segregation of duties (the **Cal Poly ScopeBuilder** real-world analog). Both returns are realized without loosening the bright line — every privileged remediation and every consequential administrative action still requires a named human.

---

## 5. References

- Governance ROI model and five categories: `../../governance/README.md`
- Full cost model: `../../offerings/COST-ROI-MODEL.md`
- Agent capabilities and proof points: `../README.md`
- What is measured where (CloudWatch, audit trail): `aws-deployment-guide.md`

---

Maturity: **Demonstrated locally — not AWS-deployed.** This agent runs end-to-end locally (demo mode + tests); a clean-account AWS deploy, real-model invocation, production identity, live connectors, and production sign-off remain customer/engagement work. Authoritative status: [`../../docs/STATUS-MANIFEST.md`](../../docs/STATUS-MANIFEST.md).
