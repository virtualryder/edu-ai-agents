# 04 — Assessment, Grading & Feedback — ROI Analysis

> ROI is measured on outcomes: grading time, feedback turnaround, coverage, and — uniquely for this agent — **quality and agreement metrics** that gate trust. A grading agent that is fast but disagrees with educators is not a success. Baseline first, then measure. Full model: `../../offerings/COST-ROI-MODEL.md`.

---

## 1. The baseline-then-measure model

Before deployment, baseline grading time, feedback turnaround, and the share of work that currently receives detailed feedback. Crucially, also establish the **quality baseline** — there is no prior agent agreement, so the first measurement job is to *generate* the human-agent agreement and educator-correction-rate evidence that justifies any release path.

| Category | Example measures | Baseline source |
|---|---|---|
| **Labor** | Grading time per item/class; educator hours on first-pass mechanics | Educator time study |
| **Service** | Feedback turnaround time; **% of work receiving feedback** | LMS timestamps, instructor logs |
| **Learning** | Student revision/learning improvement after feedback | Pre/post revision scores |
| **Risk & quality** | **Human-agent scoring agreement**, low-confidence escalation rate, **educator correction rate**, equity of scoring across groups | Double-scoring/sampling, fairness reports |

---

## 2. Anchoring to verified proof points

- **Benchmark Education** built an AWS solution (Bedrock, RDS, Step Functions, Lambda) to grade **open-ended literacy assessments** with faster feedback — the production reference for the rubric-grounded, orchestrated-pipeline approach.
- **Code.org** — AWS reports its AI teaching assistant can **cut time assessing coding projects by up to 50%** — evidence for the Labor and Service (turnaround) categories.

These establish the architecture and the order of magnitude of the Labor return; they are not a guaranteed figure for any institution, and neither replaces the institution's own agreement measurement.

---

## 3. Sample before/after illustration (ILLUSTRATIVE ONLY — not a guarantee)

> Figures are **illustrative** to show how the model is populated, not projections. Replace every cell with the institution's own baseline.

Assume one course with frequent open-ended formative work, ~300 submissions per cycle, where detailed feedback currently reaches only a fraction of students due to time.

| Measure | Before (baseline) | After (illustrative) | Basis |
|---|---|---|---|
| Educator grading/feedback time per cycle | ~15 hrs | ~7–8 hrs (≈−50%) | Draft-first mechanics (Code.org-shaped) |
| Feedback turnaround | ~7 days | ~1–2 days | Pipeline drafts immediately for review |
| % of work receiving detailed feedback | ~60% | ~95% | Capacity freed for more coverage |
| Human-agent scoring agreement | n/a | measured, gating | Double-scoring/sampling |
| Educator correction rate | n/a | measured, trending down | Rubric grounding + deterministic score |
| Low-confidence escalation rate | n/a | tracked | `route_to_manual_review` |
| Equity gap in scoring | baseline | monitored | Fairness checks |
| Autonomous high-stakes grade releases | 0 | **0 (by design)** | Hard gate |

**How to read it:** the Labor and Service returns are real and large, but they are **conditioned on the quality metrics**. Until human-agent agreement is demonstrated and the correction rate is acceptable, the agent stays advisory (draft-only); the time savings are only "banked" once trust is earned and monitored.

---

## 4. Measurement cadence and caveats

- **Quality gates value, not the reverse.** Report agreement, correction rate, and escalation rate *before* claiming the time savings; a fast agent that educators frequently override is not delivering ROI.
- **Keep the hard line visible.** "Autonomous high-stakes grade releases = 0, by design" is itself a metric leadership and accreditors care about — track and report it.
- **Watch equity.** Scoring-equity monitoring (`../../governance/fairness/`) is non-negotiable for a grading agent; a disparity is a stop-and-fix signal regardless of speed.
- **Phase the trust.** Move from draft-only → double-scored → educator-approved low-stakes release only as agreement evidence accumulates; never extend to high-stakes autonomous release.

Portfolio roll-up: `../../offerings/COST-ROI-MODEL.md`.
