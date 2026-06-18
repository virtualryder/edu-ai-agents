# Academic, College & Career Pathway Navigator
### Agent 06 — a bounded advising copilot that augments the counselor and never decides a student's placement

> **The Navigator helps a student and a counselor see the path. It does not choose it.** Course planning, graduation-requirement checks, transfer-credit mapping, and career exploration are high-value, high-leverage work — and they are also exactly where a confident-sounding wrong answer does real harm to a student's time, money, and trajectory. This agent is built so the authoritative pathway logic is a **deterministic rules engine, not the LLM**, and so every output is explicitly labeled as an **option**, a **recommendation**, or an **approved plan** — three different things the agent must never blur.

---

## What it does

The Navigator supports the full arc of academic, college, and career planning across every level the suite serves — middle and high school, community college, university, online programs, and adult/workforce education. In conversation with a student (or a guardian, educator, counselor, or administrator acting in their own role), it handles middle/high-school course planning, graduation-requirement checking, college exploration, CTE pathways, credential selection, degree planning, transfer-credit mapping, course sequencing, career and skills exploration, apprenticeship and workforce pathways, and scheduling time with a human counselor.

Underneath the conversation, the work splits cleanly. **Amazon Bedrock (Claude)** runs the dialogue, the explanation, and the framing — turning a degree audit into plain language a tenth-grader or a returning adult learner can act on. A separate **deterministic degree/graduation/prerequisite rules engine — which is not the LLM** — is authoritative for whether a requirement is met, whether a prerequisite is satisfied, and how a transfer credit articulates. The LLM explains; the rules engine decides the facts. This separation is the single most important design choice in the agent, and it is what lets the agent's pathway logic be fast, testable, and consistent enough to include in validation evidence.

The agent makes one distinction explicit in every output where it matters:

| Output type | What it means | Who owns it |
|---|---|---|
| **Option** | A path the student *could* take that is consistent with the rules — surfaced with its assumptions stated | The student, exploring |
| **Recommendation** | A path the agent *suggests*, with grounded reasoning and surfaced assumptions — but no authority | The counselor, to review |
| **Approved academic plan** | A plan a named, authorized human has signed — only this can be treated as binding | The counselor / advisor, by decision |

The agent must never present a recommendation as an approved plan, and must never bury the policy assumptions behind a recommendation. Assumptions are surfaced, not hidden — a "you appear to be on track to graduate" statement always carries the catalog year, the assumed major, and the in-progress courses it depended on.

## What it solves

Advisors and counselors carry large caseloads, and the rules they navigate — graduation requirements, prerequisite chains, transfer-articulation agreements, credential and CTE pathways, catalog-year differences — are genuinely complex and change every cycle. The result is a structural mismatch: the questions students have are constant and individualized, but human advising capacity is finite and seasonal. Students wait weeks for an appointment, register for courses that don't count toward their goal, miss a prerequisite and lose a term, or never discover the CTE or apprenticeship pathway that fit them. The Navigator absorbs the high-volume, rules-heavy first pass — *what counts, what's next, what transfers, what's possible* — so that scarce human advising time is spent on judgment, encouragement, and the consequential decision itself.

## Where it sits in the rollout & why

The Navigator is **#06 in the suite, and it is not a best-first deployment.** The best-first agents are 01 (Concierge), 03 (Educator Copilot), 08 (Operations Service Desk), and 07 (Document & Accessibility Services) — broad visibility, comparatively low decision-risk, mature workflows, and easily measured deflection or cycle-time return. The Navigator is a **high-value, higher-governance** agent: it augments the counselor and touches student outcomes directly, which means it requires stronger evaluation, advisor oversight, evidence retention, and escalation than a land-first agent. It should be deployed after the platform's MCP authorization gateway, identity wiring, audit trail, and human-approval framework are proven on an earlier agent — the gateway is built once and inherited, so the Navigator's job is to add the deterministic rules engine and the labor-market data layer on top of controls that already pass review. See `../README.md` and `../../docs/SUITE-ARCHITECTURE.md` for the full sequencing rationale.

## AWS implementation

The Navigator is a **LangGraph specialist agent** (Layer 2) following the suite pattern — `Intake → [Retrieval] → Rules-engine check → Draft / Analyze → [Policy gate] → Routing → HITL Gate → Finalize` — with no path from intake to a finalized advising-case or scheduling write that bypasses the HITL gate. Conversation and explanation run on **Amazon Bedrock (Claude)** in-account, with **Bedrock Guardrails** enforcing PII denial, age-appropriate content (heightened for minors), and topic filters on every LLM call. The authoritative pathway logic runs as a **deterministic rules engine in Lambda** — Layer 5 deterministic services — entirely separate from the LLM.

The program/course/prerequisite/credential/career graph is modeled in **Amazon Neptune** (for the relationship-heavy graph of prerequisites, articulation, and career adjacencies) or **Amazon Aurora** (relational model where the institution prefers it). Policies, catalogs, and program descriptions are grounded against **Amazon Bedrock Knowledge Bases**, segmented by institution and program so retrieval respects existing permissions. External program/credential/career data sits in a **governed data layer** (Layer 4 RWD/labor-market). Authorization, identity, and audit are inherited from the shared **AgentCore Gateway + AgentCore Identity** layer; every tool call — read or write — passes through it. Deployment targets either **AgentCore Runtime** (container lift) or **Strands + Step Functions** (native rebuild) per the suite's two-path model.

### Narrowly-scoped tools — READ separated from WRITE

Each tool has a single purpose; read and write are separate tools with separate grants. The agent never holds direct database credentials or unrestricted API access, and never exceeds the human on whose behalf it acts.

| Tool | Kind | Purpose | Grant / gate |
|---|---|---|---|
| `sis.get_student_transcript` | **READ** | Retrieve the authenticated student's completed/in-progress courses | Identity-scoped; student's own record only |
| `sis.get_student_program` | **READ** | Retrieve declared program / catalog year / standing | Identity-scoped |
| `rules.run_degree_audit` | **READ** (deterministic) | Run the authoritative degree/graduation audit in the rules engine | Deterministic Lambda; no LLM authority |
| `rules.check_prerequisites` | **READ** (deterministic) | Authoritatively evaluate prerequisite satisfaction for a candidate course | Deterministic Lambda |
| `rules.map_transfer_credit` | **READ** (deterministic) | Apply articulation rules to inbound transfer credit | Deterministic Lambda |
| `kb.search_program_policy` | **READ** | Retrieve grounded program, catalog, and policy content | Grounding-verified |
| `labor.get_career_pathway_data` | **READ** | Retrieve governed labor-market / credential / career data | Governed data layer; no PII join |
| `scheduling.find_counselor_availability` | **READ** | Surface open counselor appointment slots | Identity-scoped |
| `scheduling.book_counselor_appointment` | **WRITE** | Book time with a human counselor | **HITL gate** |
| `advising.create_advising_case` | **WRITE** | Open an advising case for human follow-up | **HITL gate** |
| `advising.attach_proposed_plan` | **WRITE** | Attach a draft plan to a case for counselor review | **HITL gate**; never marked "approved" by the agent |

## Systems of record / connectors

The SIS remains the system of record for transcripts, program declarations, and standing; the Navigator reads it only through gateway-authorized connectors, never via direct database access. The connector framework (`../../platform_core/edu_agent_platform/connectors/`) provides adapters for **PowerSchool, Infinite Campus, Banner, and Workday Student** (SIS), the institution's **scheduling** system, and the **advising/case-management** system. The program/course/prerequisite/credential/career graph lives in **Neptune or Aurora**; grounded policy and program content in **Bedrock Knowledge Bases**; and labor-market/credential/career data in the **governed RWD layer** (Layer 4). Demo mode uses deterministic JSON fixtures; the gateway does not know which backend is live.

## Phased adoption

| Phase | Scope | Maturity target |
|---|---|---|
| **1 — Read-only exploration** | Course planning, graduation checks, transfer mapping, and career exploration as **options only** — no writes; deterministic rules engine validated against advisor-reviewed golden audits | Demonstrated |
| **2 — Recommendations + scheduling** | Adds grounded recommendations (assumptions surfaced) and the `book_counselor_appointment` write behind the HITL gate | Deployable |
| **3 — Advising-case integration** | Adds `create_advising_case` and `attach_proposed_plan` writes; full audit lineage to the SIS and advising system; fairness monitoring on recommendation patterns | Production-ready |

## Regulations that apply

FERPA is the load-bearing statute: transcript and program retrieval is **identity-scoped** so a student's agent reads that student's record and no other, and guardian access is bounded by the rights that transfer to the student at 18 / postsecondary enrollment. Accreditation and **transfer-articulation policy** govern how requirements and transfer credit are evaluated — which is precisely why that logic is deterministic and testable, not generated. **Student placement is on the suite's bright-line list**: the agent presents options and recommendations, and a human decides. The option-vs-recommendation-vs-approved-plan distinction is enforced and surfaced wherever the agent presents a path. See `docs/edu-compliance.md` and `../../governance/README.md`.

## ROI — what to measure

Baseline before deployment, then measure. The Navigator maps primarily to the **Labor**, **Service**, **Student journey**, and **Risk & quality** categories of the governance ROI model (`../../governance/README.md`):

| Category | Example measures for the Navigator |
|---|---|
| **Labor** | Advisor capacity (students served per advisor-hour); routine-question load absorbed before it reaches a human |
| **Service** | Appointment wait time; after-hours availability of planning support |
| **Student journey** | On-time graduation / credential-completion rate; unnecessary credits attempted; transfer-credit utilization; student confidence / engagement |
| **Risk & quality** | Misregistration / prerequisite-error rate; recommendation override rate; equity differences in recommendation patterns |

Detailed model with an illustrative before/after table in `docs/roi-analysis.md`.

## Proof points

The U.S. Department of Education identifies college/career exploration, advising, navigation, career-aligned pathways, and personalized learning plans as important AI opportunities — aligning with the ED 2025 AI guidance referenced in the suite's compliance spine (`../../governance/README.md`). This is the verified external signal that the Navigator's workflow is a recognized, supported use of AI in education; it is not a claim of any specific outcome at any specific institution.

---

**Maturity: Documented.**
