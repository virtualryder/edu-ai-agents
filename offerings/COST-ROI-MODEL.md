# Cost & ROI Model
### How to Measure the Value of Governed EDU AI Agents — Outcomes, Not Conversations

> The defining principle of this model: **education ROI is measured on outcomes — deflection, cycle time, learning, persistence, risk/quality — not on chat volume.** A tutoring agent with high usage and no measurable learning gain is not a success; an enrollment agent with moderate usage and a 70% cut in processing time is. This document gives the baseline methodology, per-agent example metrics, an illustrative total-cost frame, and the discipline of comparing measured outcomes against a pre-deployment baseline. **All specific numbers below are clearly labeled illustrative; the institution's own baseline and measured results are what count.**

---

## 1. The principle: outcomes, not conversations

Counting conversations rewards the wrong thing. A high-traffic agent can be a failure (it answered a lot and changed nothing) and a moderate-traffic agent can be a triumph (it quietly halved a processing time or lifted persistence). So this model refuses "messages handled" and "questions answered" as success metrics. It measures the change in the work the institution actually cares about, against a baseline captured *before* deployment.

The verified reference points the suite cites are all outcome-framed, never volume-framed:

| Institution | Workflow | Outcome (verified reference, not a guarantee) |
|---|---|---|
| UA–Pulaski Tech (MyAgent) | Concierge-class student services | 94.5% adoption; 253% lift in admissions engagement |
| Highline College | Financial-aid self-service | ~75% reduction in status emails/calls/visits; FAFSA processing roughly halved |
| Illinois Tech | Transcript evaluation | 4–6 weeks → ~1 day |
| UT Austin (UT Sage) | Faculty-guided Bedrock tutor | Faculty-controlled tutoring at scale |

These set expectations. The institution's pilot proves its *own* result against its *own* baseline.

---

## 2. The five baseline categories

Baseline these five before deployment; measure the change after. Every agent maps to one or more.

| # | Category | What it captures | Example measures |
|---|---|---|---|
| **1** | **Labor** | Staff time and capacity freed | Minutes per case, staff hours, overtime, seasonal staffing, caseload per advisor |
| **2** | **Service** | Quality and availability of service to students/families | Response time, wait time, first-contact resolution, after-hours availability, channel coverage |
| **3** | **Learning** | Educational effect | Mastery, course pass rate, feedback turnaround, engagement, time-to-feedback |
| **4** | **Student journey** | Movement through the institution | Enrollment/application completion, attendance, persistence, retention, graduation/credential completion, transfer success |
| **5** | **Risk & quality** | The cost side — errors, harm, inequity | Error rate, escalation rate, override rate, privacy incidents, equity differences across cohorts, accessibility conformance |

Category 5 is not optional. A "gain" in labor or cycle time that comes with a rising error rate, a privacy incident, or a widening equity gap is not a gain — it is a liability the model must surface. This is why Risk & quality is baselined and reported alongside the value categories.

---

## 3. Per-agent example metrics

The primary categories each agent moves (illustrative metric examples — the institution selects and baselines its own):

| Agent | Primary ROI categories | Illustrative example metrics |
|---|---|---|
| **01 Concierge** | Service, Labor, Student journey | Status-inquiry deflection rate; reduction in routine emails/calls/visits; after-hours self-service resolution; application/enrollment completion; staff hours reclaimed |
| **02 Tutor & Study Companion** | Learning, Service | Course pass rate; mastery on targeted concepts; engagement outside class hours; feedback turnaround — *not* tutoring-session count |
| **03 Educator Copilot** | Labor, Learning | Educator hours reclaimed on lesson/differentiation/rubric prep; differentiation coverage (levels/languages/needs served); time-to-publish on LMS tasks |
| **04 Assessment, Grading & Feedback** | Labor, Learning | Grading hours per assignment; feedback turnaround time; low-confidence routing rate; consistency against rubric (educator owns the grade) |
| **05 Student Success & Engagement** | Student journey, Labor, Risk & quality | Persistence/retention; time-to-intervention; outreach coverage; caseload capacity; **fairness: false-positive/false-negative parity across cohorts** |
| **06 Pathway Navigator** | Student journey, Service | On-time graduation/credential completion; transfer-credit cycle time; advising-caseload capacity; plan completeness |
| **07 Document & Accessibility** | Labor, Service, Student journey, Risk & quality | Document processing cycle time (cf. Illinois Tech 4–6 wks → ~1 day); enrollment completion; accessible/multilingual content coverage; WCAG conformance |
| **08 Operations Service Desk** | Labor, Service | Ticket deflection; mean time to resolution; first-contact resolution; after-hours coverage; staff time reclaimed |

---

## 4. Illustrative TCO frame

A governed-platform deployment has two cost shapes: a **one-time build** (heaviest on the first agent, because the gateway/identity/audit control plane is built once and reused) and an **ongoing run cost**. The numbers below are an **illustrative frame to structure the conversation — not a quote**. Real figures depend on volume, model selection, region, agent count, and the chosen gateway hosting model.

### One-time build (illustrative shape)

| Cost element | Driver | Notes |
|---|---|---|
| Gateway / identity / audit control plane | Built once (Phase 1) | Heaviest on agent #1; agents #2–#8 inherit it — the marginal build cost drops sharply after the first |
| Connector validation | Per live system of record | One system in the pilot; more in expansion |
| IdP federation & role mapping | Customer IdP integration | Front-loaded; reused by all agents |
| Accessibility conformance testing | Per student-facing surface | WCAG 2.2 AA gate |
| Security & privacy review support | Per institution | Consumes the TPRM evidence package |

### Ongoing run cost (illustrative monthly shape)

| Cost element | AWS service | Driver |
|---|---|---|
| **Bedrock inference** | Amazon Bedrock (Claude) | Tokens per interaction × volume; in-account, no PII egress. Usually the largest variable line. |
| **AgentCore** (runtime + gateway + identity) | Bedrock AgentCore | Invocations, gateway target calls, identity token minting. (Lower in the AWS-primitives or FastMCP hosting options, which trade managed convenience for self-operated components.) |
| **Storage** | DynamoDB (append-only audit), S3 + Object Lock (WORM docs), Knowledge Bases vector store | Audit volume, document retention, KB size |
| **Gateway / integration** | API Gateway + Lambda (Options B/C), Step Functions (HITL `waitForTaskToken`) | Per-call authorization and orchestration |
| **Supporting** | KMS, CloudWatch, CloudTrail, Textract/Transcribe/Translate/Polly (Agents 02/07), SageMaker (Agent 05 early-warning) | Encryption, observability, media processing, prediction where justified |
| **Run/operate** | Managed service | HITL queue ops, change control, eval/fairness monitoring, accessibility maintenance, incident response (`MANAGED-SERVICE-OFFERING.md`) |

### The platform economics that matter
The control plane is the expensive part, and it is built **once**. That is the core financial argument for the gateway-first sequencing: pay for identity, authorization, the human gate, and audit on Agent 01, and Agents 02–08 inherit them. The marginal cost of each additional agent is dominated by its connector(s) and its agent-specific logic, not by rebuilding governance. Deferring the gateway inverts this — the institution pays the integration-and-retrofit tax eight times (see `docs/WHY-THE-MCP-LAYER.md`).

---

## 5. A worked illustrative example (clearly hypothetical)

> **Illustrative only — invented numbers to show the *method*, not a benchmark.** A mid-sized college deploys Agent 01 against its SIS for financial-aid and application status.

- **Baseline (pre-deployment):** financial-aid office handles ~6,000 routine status inquiries/month (email/call/walk-in), averaging ~8 staff-minutes each = ~800 staff-hours/month. After-hours inquiries go unanswered until the next business day. Application-completion rate is the journey metric.
- **Target (modeled on the Highline reference, not promised):** a 60–75% deflection of routine status inquiries to governed self-service.
- **Illustrative result at 65% deflection:** ~520 staff-hours/month reclaimed; after-hours self-service now available; staff redirected to complex casework. Application-completion measured for a journey effect.
- **Against run cost:** the reclaimed labor and the service/journey improvements are weighed against the monthly run cost (inference + AgentCore + storage + gateway + managed service). The verdict is the *net outcome*, with Risk & quality (error rate, escalation rate, privacy incidents, equity differences) confirmed flat or improved.

The point of the worked example is the **shape of the calculation**, not the digits: baseline → target informed by a verified reference → measured result → net of run cost → confirmed against Risk & quality.

---

## 6. How to use this model in an engagement

1. **Assessment:** decide which of the five categories to instrument and how (`ASSESSMENT-OFFERING.md`).
2. **Pilot:** capture the pre-deployment baseline, then measure the change against it (`PILOT-OFFERING.md` §5).
3. **Managed service:** report the outcome metrics monthly alongside risk metrics (`MANAGED-SERVICE-OFFERING.md` §3).
4. **Expansion:** use the demonstrated outcome of Agent 01 — and the now-built control plane — to justify Agents 02–08, whose marginal cost is far lower (`SOLUTION-FIELD-GUIDE.md`).

---

## 7. Related offerings

- `PILOT-OFFERING.md` (baseline capture and measurement), `MANAGED-SERVICE-OFFERING.md` (ongoing run cost and reporting), `ASSESSMENT-OFFERING.md` (choosing what to instrument), `docs/WHY-THE-MCP-LAYER.md` (build-once economics), `governance/README.md` §4 (the same five-category principle), `COMPETITIVE-POSITIONING.md` (why the cross-system platform outperforms point tools on outcome).
