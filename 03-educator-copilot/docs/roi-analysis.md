# 03 — Educator Copilot — ROI Analysis

> ROI is measured on outcomes: time returned to instruction, administrative clicks eliminated, and consistency/coverage of materials — not on draft volume. Baseline first, then measure. Full model: `../../offerings/COST-ROI-MODEL.md`.

---

## 1. The baseline-then-measure model

The Copilot has two distinct ROI surfaces — **instructional drafting/differentiation** and **LMS workflow** — and each has a clean baseline. Capture both before deployment, then re-measure per phase.

| Category | Example measures | Baseline source |
|---|---|---|
| **Labor** | Prep time per lesson, time to differentiate a lesson, **admin time per course**, **clicks eliminated** per LMS task (extend deadline, build rubric, create quiz) | Educator time study, LMS task instrumentation |
| **Learning** | Curriculum consistency across sections, accessibility/language coverage of materials | Material audit, accessibility checks |
| **Service** | Adoption among educators, reuse of approved material | Usage + content reuse logs |
| **Student journey** | Time returned to instruction (educator hours redirected to students) | Derived from Labor savings |
| **Risk & quality** | Error/rollback rate on LMS actions, draft-to-publish approval rate, grounding-failure rate | Audit trail, governance reports |

---

## 2. Anchoring to verified proof points

- **U.S. Department of Education 2025 guidance** identifies AI **instructional materials, differentiated instruction, and reduced administrative burden** as supported uses — the policy basis for the Labor and Student-journey categories.
- **Instructure IgniteAI / IgniteAgent** (Bedrock-based) supports rubric creation, assignment generation, discussion summaries, announcements, and course-material management in Canvas, with a **review-then-permit** action model (e.g., a requested student extension) — the production reference for the LMS-workflow ROI surface (clicks eliminated, admin time per course).

These establish the supported-use and production-pattern basis; they are not a guaranteed time-savings figure for any institution.

---

## 3. Sample before/after illustration (ILLUSTRATIVE ONLY — not a guarantee)

> Figures are **illustrative** to show how the model is populated, not projections. Replace every cell with the institution's own baseline.

Assume a department of 40 educators, each preparing ~4 lessons/week, with differentiation done ad hoc, and routine LMS chores (deadline extensions, rubric builds, quiz creation) consuming measurable time.

| Measure | Before (baseline) | After (illustrative) | Basis |
|---|---|---|---|
| Prep time per lesson | ~90 min | ~55 min | Drafting from approved curriculum |
| Time to produce a differentiated version | ~45 min | ~10 min | Reading-level/level variants drafted |
| Clicks to extend a learner's deadline | ~12 LMS clicks | 1 reviewed request | `update_assignment_due_date` (preview+confirm) |
| Admin time per course / week | ~3 hrs | ~1 hr | LMS-workflow consolidation |
| Accessibility/language coverage of materials | partial | broader | Drafted alternatives |
| LMS-action rollback rate | n/a | <1% target | Idempotent, preview-confirm, draft-first |
| Draft-to-publish approval rate | n/a | tracked | Educator stays in control |

**How to read it:** the dominant return is Labor (prep + differentiation time, admin clicks), converting directly into the Student-journey measure of **time returned to instruction**, with Learning gains in consistency and coverage. Risk is held by the draft-first model: nothing reaches students unapproved, and rollback rates are a quality guardrail.

---

## 4. Measurement cadence and caveats

- **Instrument both surfaces.** Prep/differentiation time and LMS-task clicks are different baselines — measure each so the savings story is concrete, not anecdotal.
- **Adoption gates value.** Time savings only materialize if educators use the Copilot; track adoption and reuse, and pair the rollout with enablement.
- **Quality is a floor.** Rising error/rollback rates on LMS actions, or a low draft-to-publish approval rate, signal that drafts need better grounding before scaling — fix before expanding.
- **Attribute time-returned carefully.** Convert Labor savings to "time returned to instruction" conservatively; that is the measure leadership cares about.

Portfolio roll-up: `../../offerings/COST-ROI-MODEL.md`.
