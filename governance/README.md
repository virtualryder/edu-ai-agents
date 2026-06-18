# Governance & Evaluation Framework
### The EDU Compliance Spine

> In life sciences, the load-bearing regulation is 21 CFR Part 11. In education, there is no single statute — there is a **stack** of federal and state law, plus accessibility mandates, that together define what an agent may do with a student's record. This framework treats that stack as the spine of the platform: every agent inherits it, and a fix to any control benefits all eight agents at once.

This is not a legal opinion and not a compliance certification. It is the **control design** an institution operationalizes, validates, and accepts accountability for. Treat it as the checklist a CISO, privacy officer, registrar, special-education director, and accessibility coordinator will hold the program to.

---

## 1. The regulatory stack the platform is built to honor

### FERPA — Family Educational Rights and Privacy Act (20 U.S.C. § 1232g; 34 CFR Part 99)
The core statute. Protects personally identifiable information in **education records** and governs who may access or disclose them.

**What the platform does about it:**
- **Identity-scoped retrieval.** An authenticated student's agent can access that student's record and no other (Layer 3 deny-by-default + role intersection). This is the technical enforcement of FERPA's access limits.
- **Age-of-majority / rights transfer.** Rights transfer to the student at 18 or on postsecondary enrollment. Guardian roles are scoped so a parent agent cannot surface records the parent no longer has a right to. Role mapping in the IdP carries this state.
- **School-official / "direct control" exception.** A vendor or agent acting as a "school official" must be under the institution's **direct control** and use data only for the authorized purpose. The gateway enforces purpose-of-use per tool, and the agent holds no standing credentials — the institution can disable any tool or agent immediately.
- **Recordkeeping of disclosures.** FERPA expects institutions to record certain disclosures. The append-only, PII-masked audit trail (DynamoDB + S3 Object Lock) records who accessed what, on what basis, and who approved any action.
- **No redisclosure.** Connectors return only the fields a tool needs; the PII masker prevents record-linkable data from sprawling into prompts or logs.

### COPPA — Children's Online Privacy Protection Act (16 CFR Part 312)
Applies to personal information collected from children **under 13**. In schools, operators often rely on **school-authorized consent**, which is limited to a strictly educational context.

**What the platform does about it:**
- **Under-13 flag carried in identity claims**, driving heightened Guardrails (age-appropriate content), data minimization, and a prohibition on any non-educational use or behavioral profiling.
- **No data used to build advertising or non-educational profiles** — enforced as a purpose-of-use policy at the gateway.
- Heightened PII masking and retention limits for under-13 records.

### PPRA — Protection of Pupil Rights Amendment (20 U.S.C. § 1232h)
Governs surveys, analysis, and evaluation that reveal protected information, and parental rights around them.

**What the platform does about it:** Student Success and outreach agents do not collect or infer PPRA-protected categories (political affiliation, religion, sex behavior, etc.); intervention drafting is grounded in operational signals (attendance, missing work, engagement) only, and survey-derived data is used strictly within stated consent.

### IDEA & Section 504 — special education and disability accommodations
IEP and 504 records are among the most sensitive education records. Eligibility and placement are consequential decisions.

**What the platform does about it:**
- **Special-education eligibility and placement are on the bright-line list the agent never decides.** The agent may *draft* proposed accommodations or *retrieve* an approved plan for an authorized educator; a qualified human owns every determination.
- IEP/504 content is access-gated to the student's authorized team; the masker treats disability data as heightened-sensitivity.

### ADA & Section 508 / WCAG 2.2 AA — accessibility
Student-facing surfaces and content must be accessible. This is a build requirement, not an afterthought.

**What the platform does about it:**
- Every student-facing UX (Layer 1) is built and tested to **WCAG 2.2 AA**; conformance testing is a production-readiness gate.
- Agent 07 (Document & Accessibility Services) transforms approved content into accessible formats (alt text, captions, transcripts, plain-language, reading-level variants, audio) with human verification for consequential material (individualized plans, legal notices, safety information).

### State student-privacy laws (~140 statutes)
Most states have their own student-data-privacy laws (e.g., California's SOPIPA, plus state-specific consent, data-localization, breach-notification, and vendor-contract requirements).

**What the platform does about it:** The control design is parameterized — data-residency (region/VPC), retention windows, consent capture, and prohibited-use policies are configuration, not code changes — so a deployment can be tuned to a state's requirements. The customer maps their state obligations during the assessment phase.

### Records retention & data governance
**What the platform does about it:** WORM storage (S3 Object Lock) and configurable retention windows support records-retention schedules; the data-minimization posture (return only what a tool needs) reduces the retained surface.

### Department of Education AI guidance (2025) and the bounded-agent posture
The platform is designed to the supported use cases ED has identified — instructional materials, differentiated instruction, tutoring, advising/navigation, and reduced administrative burden — and to the principle that AI augments educators and never makes consequential decisions autonomously.

---

## 2. The bright line — decisions the agent never makes

Encoded as policy and tested in `tests/test_hitl_gates.py`. The agent never autonomously decides:

1. **Grades** (final/high-stakes) — Assessment drafts feedback and rubric-grounded evaluation; the educator owns the grade.
2. **Admissions** — Document Services validates and prepares; a human decides.
3. **Discipline** — never inferred or decided by the agent.
4. **Financial aid** — Concierge checks status and explains; eligibility/award decisions are human.
5. **Special-education eligibility** — drafted/retrieved only; the IEP/504 team decides.
6. **Student placement** — Pathway Navigator presents options and recommendations; placement is human.

For each, the distinction between an **option**, a **recommendation**, and an **approved decision** is explicit in the agent's output and enforced by the HITL gate.

---

## 3. Platform controls (the code that enforces the spine)

| Control | File | What it enforces |
|---|---|---|
| **Grounding verification** | `grounding.py` | Facts/figures/policies/deadlines in student-facing artifacts trace to approved content; ungrounded output fails fast |
| **Prompt version registry** | `prompt_registry.py`, `prompt_manifest.json` | Hash-pinned prompts; CI fails on un-bumped drift (model-change control) |
| **Structural eval harness** | `evals/` | Golden-artifact regression (advising plans, intervention drafts, rubric feedback, accessible content); no API key |
| **HITL gate tests** | `tests/test_hitl_gates.py` | Framework-enforced human approval cannot be bypassed on consequential actions |
| **Red team** | `redteam/` | Prompt injection (incl. via student-submitted docs/inbound email), PII exfiltration, authorization bypass |
| **Fairness** | `fairness/` | Equity/representativeness flags + false-positive/false-negative monitoring on student-success targeting |
| **Student-PII masking** | `../platform_core/edu_agent_platform/pii_masker/` | FERPA/COPPA identifier masking before prompt or audit |
| **Authorization** | `../platform_core/edu_agent_platform/mcp_gateway/` | Deny-by-default; least-privilege role intersection; purpose-of-use |

---

## 4. ROI is measured on outcomes, not conversations

A tutoring agent with high usage but no measurable learning improvement is not a success; an enrollment agent with moderate usage but a 70% cut in processing time is. Baseline five categories before deployment (full model in `offerings/COST-ROI-MODEL.md`):

| Category | Example measures |
|---|---|
| **Labor** | Minutes per case, staff hours, overtime, seasonal staffing |
| **Service** | Response time, wait time, first-contact resolution, after-hours availability |
| **Learning** | Mastery, course pass rate, feedback turnaround, engagement |
| **Student journey** | Enrollment completion, attendance, persistence, graduation/credential completion |
| **Risk & quality** | Error rate, escalation rate, overrides, privacy incidents, equity differences |

---

## 5. What the customer still owns

This framework provides the control *design*. The institution is responsible for: its FERPA/COPPA/PPRA compliance program and data-governance policy; IdP integration and role mapping (guardian relationships, age-of-majority); state student-privacy-law mapping; Bedrock Guardrail tuning for its population (including minors); WCAG 2.2 AA conformance testing of deployed surfaces; connector validation against live systems; records-retention configuration; and change control for prompt/model updates.
