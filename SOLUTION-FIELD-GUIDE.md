# Solution Field Guide
### For SI Sales and Solution Architects — Qualify, Land with 01, Expand to the Portfolio

> This is the working field guide for the people in front of the customer: the systems-integrator account team and the solution architects. It gives you the qualification questions, the discovery script, the pain-to-agent map, the gateway-first message, and the "land with the Concierge, expand to the portfolio" motion that walks an institution up the maturity ladder. It is deliberately practical — say-this, ask-this, map-this — and it points to the deeper collateral when you need it.

---

## 1. The one-page thesis (what you are selling)

You are not selling eight chatbots. You are selling a **governed platform** that lets an institution put AI agents into production *on student records* — across the SIS, LMS, ERP, CRM, and ITSM — in a way the CISO, privacy officer, and registrar will sign. The durable asset is the **MCP authorization gateway**: identity, deny-by-default authorization (the agent never exceeds the human), an enforced human gate on consequential actions, short-lived scoped tokens, and a PII-masked append-only audit. Built once, inherited by all eight agents. The agents are the visible surface; the gateway is the product.

The motion: **land with Agent 01 (Concierge)** because it is the most visible, lowest-risk, easiest-to-measure agent, **prove the outcome** against a baseline, and **expand to the portfolio** against a control plane that is already paid for.

---

## 2. Qualification questions (is this a real opportunity?)

Ask these early. Strong "yes" signals on the first four mean a real, near-term opportunity.

| Question | What a good answer tells you |
|---|---|
| "Where is your most acute, most *visible* student- or staff-facing pain — and can you measure it today?" | Confirms a landing use case with a baseline (favor 01/03/08/07). |
| "Are you trying to *act on* your systems of record, or just answer questions?" | If they want to act (open cases, write to the SIS, post LMS tasks), the gateway story is mandatory — that is your differentiator. |
| "Has an AI effort here stalled at security/privacy review before?" | If yes, you are selling the exact thing that unblocks it. Lead with the gateway. |
| "Who has to say yes — CISO, privacy/FERPA officer, registrar, academic leadership, the board?" | Maps your stakeholder set (use `docs/STAKEHOLDER-SECURITY-BRIEFINGS.md`). |
| "What's your IdP, and can it express student/guardian/educator/counselor/admin — and age-of-majority and guardian relationships?" | Surfaces the hardest readiness gap (especially K–12). Seeds the assessment. |
| "AWS account and Bedrock access — yes, or a path to it?" | Determines whether you can reach Deployable, or should start in demo-mode POC. |
| "One acute pain, or portfolio ambition over time?" | One pain → a point solution might suffice (be honest). Portfolio ambition → the platform's build-once economics win decisively. |

**Disqualifiers / slow-downs (be honest):** no appetite to act on systems of record (just wants a public-AI-style assistant); no path to an AWS account *and* unwilling to even do a demo-mode POC; only the higher-governance agents (02/04/05/06) wanted with no governance maturity and no willingness to land a best-first agent first.

---

## 3. The discovery script

A repeatable arc for the first substantive working session:

1. **Frame the reframe.** "Your systems already hold the answers — the pain is they're locked behind portals, PDFs, and staff inboxes. Agents are valuable because they can reach the systems safely. The hard part isn't the model; it's giving agents *governed* access to the data." (From `ENTERPRISE-PLATFORM.md`.)
2. **Find the pain.** Walk the five ROI categories (Labor, Service, Learning, Student journey, Risk & quality) and ask where it hurts and what they measure. (`COST-ROI-MODEL.md`.)
3. **Map pain to an agent** (§4 below). Converge on a landing agent — default 01.
4. **Introduce the gateway-first message** (§6). This is where you separate from point solutions and public AI.
5. **Name the path.** Assessment → POC (often parallel) → Pilot (gateway-first) → Managed service → Expansion. (`offerings/`.)
6. **Identify the deciders and pre-empt objections.** Pull the relevant stakeholder briefings and the top objections for this audience (`OBJECTION-HANDLING.md`).
7. **Propose the next step**, sized to their readiness: an assessment if identity/systems are murky; a demo-mode POC if they need to see the controls; both in parallel if they're ready to move.

---

## 4. Mapping customer pain to agents

| If the customer says… | Map to | Best-first? |
|---|---|---|
| "Families can't find anything; staff inboxes are buried; everyone calls the wrong office." | **01 Concierge** | ✅ The default landing agent |
| "IT and admin staff drown in repetitive tickets and policy questions." | **08 Operations Service Desk** | ✅ |
| "Teachers spend hours reformatting and differentiating; LMS busywork." | **03 Educator Copilot** | ✅ |
| "Enrollment is document-hell and seasonal; we can't serve everyone in their language / accessibly." | **07 Document & Accessibility Services** | ✅ |
| "Students need help after hours and our tutoring can't scale." | **02 Tutor & Study Companion** | ⚠ Higher-governance |
| "Grading and feedback eat instructor time; feedback is too slow to matter." | **04 Assessment, Grading & Feedback** | ⚠ Higher-governance |
| "We see students slipping but can't reach them in time; advisors are swamped." | **05 Student Success & Proactive Engagement** | ⚠ Higher-governance |
| "Degree/transfer/graduation rules are complex; advisor caseloads are huge." | **06 Pathway Navigator** | ⚠ Higher-governance |

**Rule of thumb:** if the customer's first instinct is a higher-governance agent (02/04/05/06), acknowledge the value and *redirect the landing* to a best-first agent (01/03/08/07) that shares the same gateway — then sequence the higher-governance agent for after the control plane is proven and their governance function is ready.

---

## 5. The "land with 01, expand to the portfolio" motion

**Why 01 is the land.** Most visible to the most users, lowest decision-risk, mature workflow, easiest to measure (deflection, cycle time, service availability). It is the cheapest place to prove both the *outcome* and the *governance* — and it builds the control plane every other agent reuses. Verified analogs: UA–Pulaski Tech's MyAgent (94.5% adoption, 253% admissions-engagement lift) and Highline College (75% reduction in financial-aid status contacts, FAFSA processing roughly halved).

**Why expansion is cheap.** The gateway, identity wiring, audit, PII masker, grounding, and HITL framework are **shared platform**. Agent #2 through #8 inherit them — so the marginal cost and the marginal security review shrink with each addition. This is the core commercial argument and it gets stronger the more the customer adds. (`COST-ROI-MODEL.md`, `docs/WHY-THE-MCP-LAYER.md`.)

**A typical expansion order** (tune to the customer): land **01**, add an adjacent best-first agent (**08** or **07** in operations-heavy institutions; **03** in instruction-led ones), then introduce a higher-governance agent (**06** Pathway Navigator or **05** Student Success) once the governance function is comfortable and the fairness/eval discipline is operating — leaving **02** and **04** (which touch learning and grading most directly) for when the institution is fully ready.

---

## 6. The gateway-first message (say this)

The 60-second version (full version in `docs/WHY-THE-MCP-LAYER.md` §7):

> "Your interest is automating real work in PowerSchool, Banner, Canvas, ServiceNow. The instant an agent can read and write a student's record, your security and privacy teams care about three things: can the agent do more than the person it's acting for, does a qualified human approve the consequential steps, and can you prove every access to a parent or an auditor. If each agent just holds API keys and calls systems directly, the answer to all three is *no* — and that's where education AI programs stall. So we put one governed layer between the agents and your systems. We build it once on the Concierge and every other agent reuses it. Fund it in the first phase — it's the control layer your CISO, privacy officer, and registrar need to say yes, and it's far cheaper to build first than to retrofit across eight agents later."

When they push on lock-in: three hosting options — managed **AgentCore Gateway**, **AWS primitives**, or self-built **FastMCP** — identical enforcement semantics, readable Python in `platform_core/`. When they say "isn't this just an API gateway?": it authorizes *per action, per user, per role*, gates consequential steps to a named human, issues short-lived scoped keys, and produces the FERPA-aligned audit trail — an authorization-and-accountability layer, not a proxy.

---

## 7. The adoption path across the maturity ladder

| Ladder rung | What it means in the field | Offering |
|---|---|---|
| **Documented** | Architecture and compliance design written; good for discovery and architecture review | `ASSESSMENT-OFFERING.md` |
| **Demonstrated** | Runs end-to-end in demo mode (no API key, fixtures); good for the workshop and the go/no-go | `POC-OFFERING.md` |
| **Deployable** | CloudFormation/Terraform, container contract, CI pass; needs the customer AWS account and Bedrock; good for a pilot | `PILOT-OFFERING.md` |
| **Production-ready** | Security/privacy review complete, IdP integrated, live connectors tested, WCAG 2.2 AA conformance tested, pen-tested | Pilot exit → `MANAGED-SERVICE-OFFERING.md` |

Position each rung honestly. The maturity ladder is a credibility asset, not a limitation — it tells the customer exactly what is proven and what is engagement work, which is precisely what a CISO and a procurement team want to hear.

---

## 8. Handling the deal-shaping moments

- **"Can we skip the gateway and add it later?"** No — that's the retrofit trap that costs the most. Fund it in Phase 1; every agent reuses it. (`docs/WHY-THE-MCP-LAYER.md` §6, §8.)
- **"Why not the LMS-native AI / a point solution / ChatGPT?"** Be fair, then draw the cross-system, governed-platform boundary. (`COMPETITIVE-POSITIONING.md`.)
- **"Prove it's not just slides."** Demo-mode POC — they watch a deny, a PII mask, and a human-gated write happen. (`POC-OFFERING.md`.)
- **"How do we measure success?"** Outcomes, not conversations — baseline the five categories, measure the lift. (`COST-ROI-MODEL.md`.)
- **Procurement/security questionnaire lands.** Hand them the TPRM packet. (`TPRM-DUE-DILIGENCE-PACKET.md`.)

---

## 9. Quick links

- Platform thesis: `ENTERPRISE-PLATFORM.md` · Gateway argument: `docs/WHY-THE-MCP-LAYER.md` · Architecture: `docs/SUITE-ARCHITECTURE.md`
- Offerings: `offerings/ASSESSMENT-OFFERING.md` · `POC-OFFERING.md` · `PILOT-OFFERING.md` · `MANAGED-SERVICE-OFFERING.md`
- Commercial: `offerings/COST-ROI-MODEL.md` · `COMPETITIVE-POSITIONING.md` · `OBJECTION-HANDLING.md` · `TPRM-DUE-DILIGENCE-PACKET.md`
- Stakeholders: `docs/STAKEHOLDER-SECURITY-BRIEFINGS.md` · Compliance spine: `governance/README.md`
