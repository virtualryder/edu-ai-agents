# Agent 05 — ROI Analysis
### Baseline before deployment, then measure outcomes — not conversations

> ROI for Student Success is measured on **outcomes**, not activity. A high outreach volume with no improvement in signal-to-intervention time, no gain in persistence, and no movement on equity differences is not a success. This agent's value follows the IES finding: it comes from **assembling evidence and coordinating action faster and more equitably**, not from a prediction score. Baseline each metric *before* deployment so improvement is provable. Full cross-agent model in `../../offerings/COST-ROI-MODEL.md`; categories defined in `../../governance/README.md`.

---

## 1. The measurement model

For each metric: capture a **pre-deployment baseline**, deploy through the phased adoption path (`../README.md`), and measure the same metric on the same population. Pair every efficiency gain with a **Risk & quality** counter-metric so speed is never bought at the cost of fairness or a higher complaint rate. Map every metric to a governance category.

| Category | Metric | How it is measured |
|---|---|---|
| **Service** | Time from warning signal to intervention | Timestamp of signal → timestamp of first human-owned action |
| **Service** | Outreach response rate | Responses received ÷ outreach sent, by channel and language |
| **Service** | Outreach completion rate | Outreach sequences that reach intended resolution ÷ initiated |
| **Labor** | Caseload capacity | Active cases handled per counselor/advisor per period |
| **Labor** | Staff hours per case | Staff time from case open to follow-up close |
| **Learning** | Intervention completion rate | Interventions completed ÷ interventions opened |
| **Learning** | Course pass rate | Pass rate among intervened students vs comparable baseline |
| **Student journey** | Attendance improvement | Change in attendance after intervention |
| **Student journey** | Persistence / retention rate | Term-to-term or year-to-year persistence |
| **Student journey** | Missed-deadline reduction | Reduction in missed registration / aid / document deadlines |
| **Risk & quality** | False-positive / false-negative rates | Flagged-but-not-at-need vs at-need-but-missed |
| **Risk & quality** | Equity differences across subgroups | Differences in recommendations and outcomes by subgroup |
| **Risk & quality** | Opt-out rate | Recipients opting out ÷ recipients contacted |
| **Risk & quality** | Complaint rate | Complaints ÷ outreach sent |
| **Risk & quality** | Override / escalation rate | Human overrides of drafts; escalations per period |

---

## 2. Illustrative before/after

The table below is **illustrative** — it shows the *shape* of the measurement and plausible directions of movement, not a promised result or a benchmark. Every customer baselines its own numbers; targets are set with academic leadership during the assessment phase.

| Metric | Baseline (illustrative) | After Agent 05 (illustrative) | Category |
|---|---|---|---|
| Time from warning signal to intervention | 11 days | 3 days | Service |
| Caseload capacity per counselor | 180 active | 260 active | Labor |
| Staff hours per case | 2.4 hrs | 1.3 hrs | Labor |
| Outreach response rate | 22% | 41% | Service |
| Outreach completion rate | 48% | 71% | Service |
| Intervention completion rate | 54% | 68% | Learning |
| Course pass rate (intervened students) | 79% | 85% | Learning |
| Attendance improvement (post-intervention) | +1.2 pts | +3.6 pts | Student journey |
| Term-to-term persistence | 83% | 88% | Student journey |
| Missed-deadline reduction | — | −34% | Student journey |
| False-positive rate | not monitored | 9% (monitored) | Risk & quality |
| False-negative rate | not monitored | 7% (monitored) | Risk & quality |
| Largest subgroup equity difference | not measured | within tolerance, tracked | Risk & quality |
| Opt-out rate | not tracked | 2.8% (tracked) | Risk & quality |
| Complaint rate | not tracked | 0.4% (tracked) | Risk & quality |

The most important columns are the **Risk & quality** rows that move from *not monitored* to *monitored*. For a higher-governance agent, establishing FP/FN, equity, opt-out, and complaint instrumentation is itself a primary deliverable — it is what lets the institution prove the agent is not labeling students or distributing interventions inequitably.

---

## 3. How the architecture earns the numbers

- **Signal-to-intervention time** falls because EventBridge surfaces signals the moment they occur and the agent assembles grounded evidence and a draft case automatically — the counselor starts from an evidence summary, not a blank screen.
- **Caseload capacity** and **staff hours per case** improve because evidence assembly, drafting, translation, and outreach logistics are displaced from staff, while the **decision** stays with staff.
- **Response and completion rates** rise because outreach is personalized, in the family's preferred language, on the right channel, and timed by the cadence orchestration — with opt-out honored.
- **Risk & quality** metrics exist *because* prediction is fenced and the fairness control runs continuously; the QuickSight equity dashboard makes subgroup differences visible in operation, not only at audit.

---

## 4. Proof-point context (verified)

These external data points validate the *pattern and scale*, not a specific ROI figure:

- **Panorama (Solara)** demonstrates the evidence-assembly pattern — combining attendance, academic, behavioral, and survey data to help educators draft evidence-based response plans.
- **Otus** reported 2025–26 use by 8,500+ educators and 1,100+ administrators supporting 106,000+ students on AWS — district-scale operation of a governed student-data platform.
- **Blackboard's Student Success** organization handles 8M+ interactions/year and is modernizing on Amazon Connect with generative AI — the outreach-at-scale pattern.
- **IES caution:** predictive models do not always outperform traditional early-warning systems; value often comes from assembling evidence and coordinating action. This is why the ROI model centers on signal-to-intervention time, response/completion, and equity — not on a prediction score.

---

## 5. Cross-references

- Cross-agent ROI model: `../../offerings/COST-ROI-MODEL.md`
- Governance categories: `../../governance/README.md`
- Fairness control: `../../governance/fairness/`
- Agent overview: `../README.md`
- Compliance: `./edu-compliance.md`

---

**Maturity: Documented.**
