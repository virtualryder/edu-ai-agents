# Agent 07 — ROI Analysis
### Document & Accessibility Services — baseline-then-measure, on outcomes not conversations

> ROI is measured on outcomes, not usage. A document agent with high upload volume but no measurable cut in processing time is not a success; one with moderate volume but a 70% cut in cycle time is. This guide gives the baseline-then-measure model for Agent 07, concrete example metrics, and an **illustrative** before/after table. The full suite model is in `../../offerings/COST-ROI-MODEL.md`; the category framework is `../../governance/README.md`, §4.

---

## 1. The model — baseline before you deploy

You cannot claim a return you did not baseline. Before deployment, capture the current state of each metric below for the document type and family-communication channels the pilot targets. After deployment, measure the same metrics on the same scope. The difference — not the demo — is the ROI.

Agent 07 maps primarily to four of the five governance ROI categories: **Labor**, **Service**, **Student journey**, and **Risk & quality**. (The Learning category belongs to the teaching agents — 02, 03, 04 — not to Document Services.)

---

## 2. Example metrics by category

| Category | Metric | How to baseline |
|---|---|---|
| **Labor** | Manual touches per document | Count keystrokes/handoffs per document type, pre-deployment |
| **Labor** | Staff hours per application/registration | Time-and-motion sample across a representative week |
| **Labor** | Seasonal / overtime staffing load | Overtime hours and temp-staff cost during the enrollment peak |
| **Labor** | Time / cost per remediated document | Hours to remediate one PDF or notice for accessibility, times loaded labor cost |
| **Service** | Processing cycle time | Submission timestamp → ready-for-decision timestamp |
| **Service** | Translation turnaround | Request → delivered translated/accessible artifact |
| **Service** | Time to enrollment decision | File-complete → registrar decision |
| **Service** | Reduced accommodation delays | Request for accessible format → delivery |
| **Student journey** | Application / registration completion rate | Started vs completed applications |
| **Student journey** | Application abandonment rate | Started-then-stalled, by missing-document reason |
| **Student journey** | Family engagement by preferred language | Open/response rate on communications sent in preferred language |
| **Risk & quality** | Extraction accuracy | Sampled field-level accuracy vs human re-key |
| **Risk & quality** | Discrepancy-catch rate | Discrepancies caught pre-decision vs found later |
| **Risk & quality** | % of content meeting accessibility standards | Share of family-facing output conforming to WCAG 2.2 AA |
| **Risk & quality** | Privacy-incident / override rate | Incidents and human overrides per 1,000 documents |

---

## 3. Illustrative before/after

> **Illustrative — not a benchmark and not a guarantee.** The figures below show the *shape* of the return and how to present it; they are not measured results from any specific deployment. Real numbers come from the customer's own baseline. Where directional support exists, it is the verified proof points in `../README.md` (Illinois Tech credential-evaluation turnaround; AWS/Bedrock multilingual reading and the Ohio State / Arizona State PDF-remediation work).

| Metric | Category | Before (baseline) | After (illustrative) | Notes |
|---|---|---|---|---|
| Processing cycle time (transcript/credential) | Service | 4–6 weeks | ~1 day | Direction supported by the Illinois Tech proof point |
| Manual touches per document | Labor | ~9 | ~2 | Remaining touches are the human-review and approval steps |
| Staff hours per 100 registrations | Labor | ~40 | ~12 | Time shifts from keying to exception review |
| Extraction accuracy (sampled) | Risk & quality | n/a (manual) | high, with low-confidence routed to review | Accuracy is a routing input, not a release criterion |
| Application abandonment rate | Student journey | 18% | 9% | Driven by proactive missing-item requests |
| Translation turnaround (family notice) | Service | 3–5 days | same-day | Approved-content transformation, human-verified for consequential material |
| Cost per remediated document | Labor | $$ (manual hours) | fraction of baseline | Per-document remediation cost falls; volume capacity rises |
| % family-facing content at WCAG 2.2 AA | Risk & quality | partial / ad hoc | standing capability | Conformance testing remains the institution's gate |

The pattern to communicate: the agent does not eliminate staff effort — it **moves** it from low-value keying and per-request remediation to high-value exception review and decision-making, and it compresses the calendar that families and a hard enrollment deadline are running against.

---

## 4. How to present the return

1. **Lead with cycle time and abandonment** — these are the metrics enrollment leadership feels and that a board understands. The Illinois Tech proof point gives a credible upper bound on what credential automation can do.
2. **Show the labor shift, not just labor cut** — staff move to exception review; this is easier to fund than headcount reduction and is what the HITL design actually produces.
3. **Treat accessibility as risk reduction and reach** — % of content at WCAG 2.2 AA and accommodation-delay reduction are both a compliance-risk story and a family-reach story.
4. **Keep quality metrics visible** — extraction accuracy, discrepancy-catch rate, and override rate are how leadership trusts the cycle-time gains are real and not corner-cutting.

---

## 5. Why these are honest numbers

Every figure here is labeled illustrative, and the only attributed results are the verified proof points. The accelerator's claim is the **control design and the measurement model** — the customer produces the actual ROI from their own baseline. That is the difference between "we ran a demo" and "we cut our enrollment processing cycle and proved it against our own September numbers."

---

Maturity: **Documented.**
