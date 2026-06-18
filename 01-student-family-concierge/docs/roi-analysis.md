# 01 — Student & Family Services Concierge — ROI Analysis

> ROI is measured on outcomes, not conversations. A high contact volume with no deflection is not success; moderate volume with a large cut in status contacts and faster enrollment completion is. Baseline first, then measure. Full model: `../../offerings/COST-ROI-MODEL.md`.

---

## 1. The baseline-then-measure model

Before deployment, capture a clean baseline for each relevant measure. After each rollout phase (public answers → authenticated retrieval → low-risk transactions), re-measure against that baseline and attribute change to the Concierge. The Concierge is the portfolio's cleanest ROI story because its baseline (call/email/walk-in volume, status-inquiry load, enrollment-completion rate) is already tracked by most front offices and financial-aid teams.

| Category | Example measures | Baseline source |
|---|---|---|
| **Labor** | Staff hours on routine inquiries; seasonal/overtime staffing during enrollment and FAFSA peaks; staff time redirected to higher-value work | Staffing records, ticket/call logs |
| **Service** | Call/email deflection rate, first-contact resolution, average response time, wait time, after-hours self-service usage | Contact-center + helpdesk metrics |
| **Student journey** | Enrollment/registration completion rate, required-document submission completion | SIS, document workflow |
| **Risk & quality** | Grounding-failure rate, escalation rate, privacy incidents, language-coverage equity | Audit trail, governance reports |

---

## 2. Anchoring to verified proof points

The two verified outcomes below are the realistic shape of the return; they are external evidence, not a guarantee for any specific institution:

- **Highline College** cut financial-aid **status emails/calls/visits by 75%** and **halved FAFSA processing time** — directly mapping to the Labor and Service categories.
- **UA – Pulaski Technical College (MyAgent)** reached **94.5% adoption**, became the **most-used app feature (21.8% of activity)**, and drove a **253% YoY rise in admissions-content engagement** — evidence for the Service and Student-journey categories.

---

## 3. Sample before/after illustration (ILLUSTRATIVE ONLY — not a guarantee)

> The figures below are **illustrative** placeholders to show how the model is populated, not projections for any institution. Replace every cell with the institution's own baseline during the assessment phase.

Assume a mid-size institution: a financial-aid/registrar front office handling ~4,000 routine status inquiries/month (call + email + walk-in), 6 FTE absorbing the load, peak season FAFSA processing averaging 10 business days.

| Measure | Before (baseline) | After (illustrative) | Basis |
|---|---|---|---|
| Routine status inquiries to staff / month | 4,000 | ~1,000 (−75%) | Deflection to self-service (Highline-shaped) |
| Avg first response time (after-hours inquiry) | next business day | minutes (24/7) | Public + authenticated self-service |
| FAFSA processing time (peak) | ~10 business days | ~5 business days (−50%) | Status self-service removes status-chasing load |
| Front-office staff hours / week on routine inquiries | ~120 | ~30 | Time redirected to complex cases |
| Enrollment-completion rate (cohort) | baseline | +X pts | Fewer abandoned steps; clearer next actions |
| Privacy incidents | baseline | 0 target | Gateway deny-by-default + audit |

**How to read it:** the dominant return is Labor + Service (deflection and cycle-time), with a secondary Student-journey lift (enrollment completion) and a Risk floor (no new privacy incidents). The Learning category does not apply to the Concierge — that is the Tutor (02) and Assessment (04) story.

---

## 4. Measurement cadence and caveats

- **Phase the measurement to the rollout.** Public-answer phase establishes the deflection baseline; authenticated phase adds status-inquiry deflection and FCR; transaction phase adds appointment/case/form completion.
- **Attribute carefully.** Seasonal peaks (open enrollment, FAFSA) distort raw counts — compare like-to-like periods year-over-year.
- **Track equity, not just totals.** Language-coverage and after-hours usage tell you whether deflection is reaching the families who most need it.
- **Risk metrics are guardrails, not vanity.** A rising grounding-failure or escalation rate is a signal to tune content/Guardrails before scaling, regardless of how good the deflection looks.

ROI roll-up across the portfolio is consolidated in `../../offerings/COST-ROI-MODEL.md`; the Concierge typically funds the shared platform (gateway, identity, audit) that Agents 02–08 then inherit.
