# Student Success & Proactive Engagement
### Assemble the evidence, draft the intervention, run approved event-driven outreach — and leave every consequential decision to a named human.

> **Agent 05 of the EDU AI Agent Suite.** A high-value, **higher-governance** agent: it touches student outcomes directly, so it carries stronger evaluation, educator oversight, bias testing, evidence retention, and escalation than the best-first agents. It is *not* a first deployment — land with Agents 01, 03, 08, and 07, then expand here once the platform's gateway, audit, and HITL framework are proven in production.

This agent consolidates two production-oriented reference workflows — **UC6 Student Success** (assemble warning-sign evidence, propose an intervention plan, open and track a case) and **UC12 Proactive Engagement** (event-driven, template-based outreach across voice, SMS, and email). They share the same governed substrate — the student-data lake, the MCP authorization gateway, the HITL gate, and the append-only audit trail — and the same architectural discipline: **the prediction stage, the explanation stage, and the human-decision stage are kept separate and are never collapsed into one.**

---

## What it does

Warning signs accumulate before anyone acts. Attendance slips, an assignment goes missing, an application stalls, a financial-aid item is outstanding, LMS engagement drops, a required document is incomplete — each is visible somewhere in a system of record, but no single person sees the whole picture in time, and staff lack the capacity for timely, personalized follow-up at scale.

Agent 05 closes that gap in two coordinated motions, both gateway-authorized and identity-scoped.

**Evidence assembly and intervention drafting (UC6).** The agent combines *authorized* attendance, grades, assessment results, LMS engagement, behavior, advising cases, surveys, and prior interventions — within strict limits on which data domains may be combined — summarizes the pattern in plain language, **proposes** an intervention plan grounded in those operational signals, identifies the appropriate staff member (advisor, counselor, teacher), drafts a case, and tracks follow-up. It assembles and explains; it does not decide.

**Proactive, event-driven outreach (UC12).** On an EventBridge signal — repeated absences, a missing assignment, an incomplete application, an approaching registration deadline, a missing financial-aid item, LMS disengagement, incomplete required documentation — the agent selects an **approved** message template, personalizes it against operational facts, translates it to the family's preferred language, and (after the required approval for any sensitive or stigmatizing outreach) sends it through an authorized channel. It records the outreach, monitors for a response, and opens a staff case if the signal persists or the response warrants human attention.

Both motions surface inside the tools staff and families already use (Layer 1): the **governed student-data lake** and **QuickSight** for program monitoring, and **Amazon Connect** (plus SES and SNS) for outreach across voice, SMS, and email.

---

## What it solves

| Problem today | What Agent 05 changes |
|---|---|
| Warning signals sit in separate systems; no one assembles them in time | Authorized signals are combined under domain limits into a single, **grounded** evidence summary for the right staff member |
| The time from a warning signal to an actual intervention is long and uneven | The agent compresses signal-to-intervention time by drafting the case and routing it to a named owner — who still decides |
| Staff cannot run timely, personalized outreach at the volume the population requires | Approved-template outreach is personalized, translated, and sent through authorized channels with preferences and opt-out enforced |
| Predictive "risk scores" risk becoming a **permanent label** on a student, and may not outperform traditional early-warning systems | Prediction is **separated** from evidence-assembly and from the human decision; value comes from assembling evidence and coordinating action, not from a score |
| Outreach can reach the wrong guardian, in the wrong language, after an opt-out | Communication preferences, guardian relationships, age-of-majority scoping, language, and opt-out are enforced at the gateway before any send |

**What this is** — a decision-support engine that assembles evidence, drafts interventions and outreach, and coordinates action under human ownership. **What this is not** — an autonomous system that scores, labels, disciplines, or places a student; the bright line holds.

---

## Where it sits in the rollout & why

Agent 05 is one of the four **high-value, higher-governance** agents (alongside 02, 04, and 06) that touch learning and student outcomes directly. The suite's adoption motion is "land with 01, expand to the portfolio": deploy the best-first agents (01 Concierge, 03 Educator Copilot, 08 Operations Service Desk, 07 Document & Accessibility) to prove the shared platform — the MCP authorization gateway, identity and role mapping, the HITL gate, the append-only audit trail, the fairness controls — then bring Agent 05 online on top of that proven foundation.

The sequencing is deliberate. Student Success requires the **strongest** evaluation discipline in the suite: false-positive/false-negative monitoring, equity-difference checks across subgroups, evidence retention, and educator/counselor oversight on every consequential step. Deploying it first would mean operationalizing those controls before the platform that enforces them has been validated in lower-risk workflows. See `../README.md` for the full maturity ladder and `../docs/SUITE-ARCHITECTURE.md` for the six-layer reference architecture this agent inherits.

---

## AWS implementation

Agent 05 is a **LangGraph StateGraph** specialist (Layer 2) whose every tool call passes through the **MCP authorization gateway** (Layer 3). It targets the AgentCore container contract (`/invocations`, `/ping`, port 8080, ARM64) for the **AgentCore Runtime** container lift, or runs as **Strands Agents + Step Functions + Lambda** for the native rebuild — the latter being the natural fit here because the outreach cadence, consent, response-monitoring, and escalation orchestration map cleanly onto Step Functions with a `waitForTaskToken` HITL gate. See `docs/aws-deployment-guide.md`.

| Architecture role | AWS service | Use in Agent 05 |
|---|---|---|
| Agent runtime (container) | **Amazon Bedrock AgentCore Runtime** | Container lift of the LangGraph graph |
| Agent runtime (native) | **Strands Agents + AWS Step Functions + Lambda** | Native rebuild; orchestrates outreach cadence, consent, response, escalation; `waitForTaskToken` HITL gate |
| MCP authorization gateway | **Amazon Bedrock AgentCore Gateway** | Deny-by-default; least-privilege intersection; purpose-of-use; HITL gate on writes |
| Federated identity + scoped tokens | **AgentCore Identity + Cognito / IAM Identity Center** | Student/guardian/educator/counselor/administrator role mapping; short-lived per-call tokens |
| LLM inference | **Amazon Bedrock (Claude models)** | Evidence synthesis, pattern explanation, intervention drafting, outreach personalization — **explanation stage only** |
| Predictive models | **Amazon SageMaker AI** | Existing early-warning models **only where prediction is justified** — **prediction stage, kept separate** |
| Content safety + PII controls | **Amazon Bedrock Guardrails** | PII denial; age-appropriate filters (heightened for minors/under-13); prohibited-behavior and topic filters on outreach copy |
| Governed analytics substrate | **S3 + Glue + Lake Formation + Redshift** | Student-data lake with fine-grained, role-aware access; **strong limits on which domains may combine** |
| Event signals | **Amazon EventBridge** | Attendance / missing-work / performance-change / deadline / missing-item / disengagement triggers |
| Program monitoring | **Amazon QuickSight** | Caseload, intervention, outreach, and equity dashboards |
| Outreach channels | **Amazon Connect + SES + SNS** | Voice, SMS, email outreach via authorized channels with preference/opt-out enforcement |
| Translation & speech | **Amazon Translate + Polly** | Preferred-language outreach; accessible audio |
| Case management | **API Gateway connector** | Create/update/track advising or success cases in the system of record |
| Append-only audit | **DynamoDB (append-only)** | Every signal, evidence assembly, draft, approval, send, response, escalation logged |
| WORM evidence store | **S3 + Object Lock** | Evidence-retention snapshots for review and equity audit |
| Encryption / keys | **AWS KMS** (customer-managed) | Per-environment key; key policy restricts to the agent role |
| Observability | **CloudWatch + CloudTrail** | HITL queue depth, approval latency, send/response rates; unified compliance record |

### Narrowly-scoped tools — READ separated from WRITE

Read and write are **separate tools with separate grants**. Reads pass straight through the gateway; writes — anything that touches a student, a guardian, or a system of record — block at the HITL gate until a named, authorized reviewer's identity is bound into the record. The agent never receives database credentials or unrestricted API access.

| READ tools (retrieve / analyze — pass-through) | WRITE tools (act — HITL-gated) |
|---|---|
| `student_success.get_attendance_summary` | `outreach.send_approved_message` |
| `student_success.get_grade_summary` | `case.create_success_case` |
| `student_success.get_assessment_results` | `case.update_case_followup` |
| `student_success.get_lms_engagement` | `case.escalate_to_staff` |
| `student_success.get_advising_history` | `outreach.record_outreach_event` |
| `student_success.get_survey_signals` (consent-scoped) | `outreach.log_response_and_close` |
| `early_warning.get_prediction` (SageMaker, justified only) | |
| `comms.get_communication_preferences` | |
| `outreach.list_approved_templates` | |

The `early_warning.get_prediction` read is deliberately fenced: its output is one *input* to the evidence-assembly stage, never a label and never an action. The explanation stage (Bedrock) and the human-decision stage (HITL gate) consume evidence; they do not consume the prediction as a verdict.

---

## Systems of record / connectors

Per the platform principle, **no agent calls a vendor system directly** — every connector sits behind the gateway and returns only the fields a tool needs (data minimization, no redisclosure). See `../docs/SUITE-ARCHITECTURE.md` and `../platform_core/edu_agent_platform/mcp_gateway/`.

| Connector | Example systems | Read / Write |
|---|---|---|
| SIS | PowerSchool, Infinite Campus, Banner, Workday Student | Read (attendance, enrollment, application/aid status) |
| LMS | Canvas, Blackboard, Schoology, Moodle, D2L | Read (engagement, missing work) |
| Advising / case management | Slate, Salesforce EDU, institutional case system | Read history; **write** case create/update/escalate |
| Comms / contact center | Amazon Connect, SES, SNS | **Write** approved outreach; read preferences/opt-out |
| Governed student-data lake | S3 + Glue + Lake Formation + Redshift | Read (domain-limited analytics substrate) |
| Predictive model service | SageMaker AI endpoint | Read (prediction, where justified only) |

---

## Phased adoption

| Phase | Scope | Maturity target |
|---|---|---|
| **1 — Evidence assembly, read-only** | Combine authorized signals under domain limits; produce grounded evidence summaries to QuickSight and to staff; no outreach, no case writes | Demonstrated |
| **2 — Human-gated case creation** | Draft intervention plans and success cases; route to a named owner through the HITL gate; track follow-up | Deployable |
| **3 — Approved-template outreach** | Event-driven outreach on low-stigma signals (deadline reminders, missing items) with preference/opt-out enforcement and human approval for sensitive content | Deployable |
| **4 — Full coordinated engagement** | Cadence, consent, response-monitoring, and escalation orchestrated end-to-end; equity and FP/FN monitoring live; evidence retained | Production-ready |

Prediction (SageMaker) is introduced **only** where it demonstrably adds value over a traditional early-warning rule — and always as an input to evidence assembly, never as a standalone score surfaced to a student.

---

## Regulations that apply

This agent inherits the full EDU compliance spine (`../governance/README.md`); the parts that bind hardest here:

- **FERPA** — identity-scoped retrieval; the agent accesses only records the acting human may access; guardian-relationship and age-of-majority scoping on every outreach; recordkeeping of disclosures in the append-only audit; school-official / direct-control posture with no standing credentials and per-tool purpose-of-use.
- **PPRA** — **no protected-category inference.** Intervention drafting is grounded in operational signals (attendance, missing work, engagement) only; survey-derived data is used strictly within stated consent.
- **COPPA** — under-13 flag in identity claims drives heightened Guardrails, data minimization, and a prohibition on non-educational profiling.
- **Equity / anti-discrimination** — fairness controls (`../governance/fairness/`): false-positive/false-negative monitoring and equity-difference checks across subgroups, designed to prevent a **permanent label** on a student.
- **Opt-out / consent** — communication preferences and opt-out are enforced at the gateway before any send.
- **The bright line** — Agent 05 **never decides discipline or placement**, and never decides grades, admissions, financial aid, or special-education eligibility. It assembles, explains, drafts, and coordinates; a human owns every consequential decision.

See `docs/edu-compliance.md` for the full treatment.

---

## ROI — what to measure

Baseline before deployment, then measure. Map outcomes to the governance categories (`../governance/README.md`); a high outreach volume with no improvement in signal-to-intervention time or persistence is not a success.

| Category | Example measures for Agent 05 |
|---|---|
| **Labor** | Staff hours per case; caseload capacity per counselor/advisor; outreach hours displaced |
| **Service** | Time from warning signal to intervention; outreach response rate; outreach completion rate; after-hours reach |
| **Learning** | Course pass rate; intervention completion rate |
| **Student journey** | Attendance improvement; persistence/retention rate; missed-deadline reduction |
| **Risk & quality** | False-positive / false-negative rates; equity differences across subgroups; opt-out rate; complaint rate; override and escalation rates |

See `docs/roi-analysis.md` for the baseline-then-measure model and an illustrative before/after table.

---

## Proof points

Honest, verified, and attributed — used to validate the architecture, not to promise a result.

- **Panorama (Solara)** combines attendance, academic, behavioral, and survey data to help educators understand student needs and draft evidence-based response plans — the same evidence-assembly pattern Agent 05 implements.
- **Otus**, built on AWS, reported 2025–26 use by **8,500+ educators and 1,100+ administrators** supporting **106,000+ students** — evidence that a governed, AWS-based student-data platform operates at district scale.
- **Blackboard's Student Success** organization handles **8M+ interactions per year** and is modernizing on **Amazon Connect** with generative AI across enrollment, financial-aid, registration, tech-support, and retention workflows — the Layer 1 outreach pattern Agent 05 uses.
- **A necessary caution (IES).** The Institute of Education Sciences notes that predictive models **do not always outperform** traditional early-warning systems; the value often comes from **assembling evidence and coordinating action**, not from prediction itself. This is precisely why Agent 05 separates the prediction stage from the evidence-assembly and human-decision stages, and why prediction is introduced only where it is justified.

---

**Maturity: Documented.**
