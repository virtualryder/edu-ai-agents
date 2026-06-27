# Pathway Navigator — ROI Analysis
### Agent 06 — baseline first, then measure outcomes (not conversations)

> **A Navigator with high chat volume but no measurable change in misregistration, wait time, or on-time completion is not a success.** The suite measures ROI on outcomes, not conversations (`../../governance/README.md`). This document gives the baseline-then-measure model for the Navigator, the categories it maps to, the concrete metrics to instrument, and an **illustrative** before/after table to frame the customer conversation — not a promise of results.

---

## 1. The model — baseline before deployment, then measure

Before the Navigator handles a single student, baseline the metrics below for a defined population and period. Deploy in the phased path (read-only options → recommendations + scheduling → advising-case integration; see `../README.md`). Then measure the same metrics on the same population and attribute the delta honestly — controlling for seasonality, enrollment changes, and any concurrent advising-process changes. The deterministic rules engine's testability is an asset here: because degree-audit, prerequisite, and articulation logic is consistent and auditable, the misregistration and prerequisite-error metrics reflect a real, reproducible control rather than model variance.

---

## 2. ROI categories and metrics

The Navigator maps to four of the governance ROI categories. (Learning is not a primary category here — the Navigator plans pathways; it does not deliver instruction.)

| Category | Metric | How to measure |
|---|---|---|
| **Labor** | Advisor capacity | Students served per advisor-hour, before vs after |
| **Labor** | Routine-question load absorbed | Share of planning questions resolved before reaching a human |
| **Service** | Appointment wait time | Median days from request to counselor appointment |
| **Service** | After-hours availability | Share of planning interactions outside business hours |
| **Student journey** | On-time graduation / credential completion | Cohort completion rate within the expected window |
| **Student journey** | Unnecessary credits attempted | Credits attempted that do not count toward the declared goal |
| **Student journey** | Transfer-credit utilization | Share of eligible transfer credit actually applied |
| **Student journey** | Student confidence / engagement | Survey + return-engagement rate |
| **Risk & quality** | Misregistration / prerequisite-error rate | Registrations later reversed for a prerequisite/requirement error |
| **Risk & quality** | Recommendation override rate | Share of agent recommendations a counselor changes at the HITL gate |
| **Risk & quality** | Equity differences | Differences in recommendation patterns across student groups (fairness monitoring) |

The override rate is a quality signal in both directions: a very high rate suggests the recommendation layer is poorly grounded; a very low rate with no human scrutiny suggests the HITL gate has become a rubber stamp. Either warrants attention.

---

## 3. Illustrative before/after

**Illustrative only.** The figures below are a framing device for the customer conversation — not benchmarks, not a commitment, and not drawn from any specific institution. Each customer baselines and measures its own numbers.

| Metric | Baseline (illustrative) | After (illustrative) | Direction |
|---|---|---|---|
| Median appointment wait time | 12 business days | 4 business days | ↓ better |
| Students served per advisor-hour | 1.4 | 2.6 | ↑ better |
| Misregistration / prerequisite-error rate | 9% of registrations | 3% of registrations | ↓ better |
| Unnecessary credits attempted (per graduating student) | 11 credits | 5 credits | ↓ better |
| Transfer-credit utilization | 62% of eligible | 84% of eligible | ↑ better |
| On-time completion (within expected window) | 51% | 58% | ↑ better |
| After-hours planning interactions | ~5% | ~38% | ↑ availability |
| Recommendation override rate | n/a (new) | 18% | monitored |

The reading of this table is the point, not the numbers: the Navigator's value shows up as **fewer wasted credits, better transfer utilization, shorter waits, and more advisor capacity for judgment** — with the misregistration metric resting on the deterministic rules engine and the override and equity metrics keeping the recommendation layer honest. A customer that cannot move the Student-journey and Risk & quality rows is not getting ROI from this agent, regardless of chat volume.

---

## 4. What to instrument from day one

Instrument the audit trail and CloudWatch from the first deployment so the measurement is not retrofitted: HITL queue depth and approval latency (Service + capacity), tool-call counts split read vs write (load absorbed), override decisions at the gate (Risk & quality), and the fairness monitors on recommendation patterns (equity). Tie misregistration and unnecessary-credit metrics back to SIS registration outcomes via the audit lineage. The full cost-and-ROI model is in `../../offerings/` per the suite structure; the category definitions are in `../../governance/README.md`.

---

**Maturity: Demonstrated locally — not AWS-deployed.** This agent runs end-to-end locally (demo mode + tests); a clean-account AWS deploy, real-model invocation, production identity, live connectors, and production sign-off remain customer/engagement work. Authoritative status: [`../../docs/STATUS-MANIFEST.md`](../../docs/STATUS-MANIFEST.md).
