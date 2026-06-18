# Battlecard — EDU AI Agent Suite
### For the SI Account Team: Qualify, Position, and Win

> This is the one-page combat reference. Carry it into discovery and into the competitive moment. Full depth lives in `SOLUTION-FIELD-GUIDE.md`, `COMPETITIVE-POSITIONING.md`, and `OBJECTION-HANDLING.md`.

---

## The one-sentence pitch

A **governed platform** — one MCP authorization gateway, one identity and audit layer, one compliance spine — that lets an institution put AI agents into production *on student records* in a way the CISO, privacy officer, and registrar will sign; eight high-value education workflows land on it, and every agent after the first inherits the control plane for free.

---

## What you are selling (and what you are not)

| You ARE selling | You are NOT selling |
|---|---|
| A governed, auditable accelerator with real, testable controls — deny-by-default authorization, enforced human gate, PII masking, append-only audit | Eight chatbots or a public-AI wrapper around student records |
| The MCP authorization gateway: built once on Agent 01, inherited by Agents 02–08 — the build-once economics are the commercial story | A certified, validated, production-ready SaaS product handed to the customer unchanged |
| Bounded agents: retrieve, analyze, draft, initiate low-risk workflows, escalate exceptions — humans own every grade, admission, discipline, financial-aid award, eligibility decision, and placement | An autonomous administrator or teacher that decides consequential outcomes |
| Three hosting options (managed AgentCore Gateway, AWS primitives, self-built FastMCP) so the institution is never locked in | Vendor lock-in — the enforcement logic is readable, testable Python in `platform_core/` |

---

## The "land with 01, expand to the portfolio" motion

**Why Agent 01 (Student & Family Services Concierge) is always the land:**

- Most visible to the most users — every student, family, and staff member touches it
- Lowest decision-risk — in public mode it answers; in authenticated mode it performs small, reversible, low-stakes actions
- Mature, measurable workflows — call/email deflection, first-contact resolution, and after-hours self-service are quantifiable from day one
- It builds the shared platform — the gateway, identity federation, audit trail, and HITL framework provisioned for 01 are reused by every later agent; pay the integration tax once

**Reference outcomes (verified, not guaranteed):**
- UA–Pulaski Tech (MyAgent): 94.5% adoption; 253% admissions-engagement lift year-over-year
- Highline College: ~75% reduction in financial-aid status contacts; FAFSA processing time roughly halved
- Illinois Tech: transcript evaluation from 4–6 weeks to ~1 day (Agent 07 pattern)

**Typical expansion order:** 01 → 08 (Operations Service Desk) or 07 (Document & Accessibility) or 03 (Educator Copilot) → then 06 (Pathway Navigator) or 05 (Student Success) once the governance function is ready → 02 (Tutor) and 04 (Assessment) last.

---

## The eight agents at a glance

| # | Agent | Best first? | Primary pain | Key ROI category |
|---|---|---|---|---|
| **01** | Student & Family Services Concierge | ✅ Default land | Families can't find anything; staff buried in routine contacts | Service, Labor, Student journey |
| **02** | Personalized Tutor & Study Companion | ⚠ Higher-governance | Students need help at scale outside class hours | Learning, Service |
| **03** | Educator Copilot | ✅ Best-first | Teachers spend hours differentiating and navigating the LMS | Labor, Learning |
| **04** | Assessment, Grading & Feedback | ⚠ Higher-governance | Grading and feedback are slow and inconsistent | Labor, Learning |
| **05** | Student Success & Proactive Engagement | ⚠ Higher-governance | Warning signs accumulate before anyone acts | Student journey, Labor, Risk & quality |
| **06** | Academic, College & Career Pathway Navigator | ⚠ Higher-governance | Degree/transfer rules are complex; advisors are overloaded | Student journey, Service |
| **07** | Document & Accessibility Services | ✅ Best-first | Enrollment is document-heavy; accessibility at scale | Labor, Service, Student journey |
| **08** | Operations Service Desk | ✅ Best-first | IT/admin staff drown in repetitive tickets | Labor, Service |

**If a customer's first instinct is a higher-governance agent (02/04/05/06):** acknowledge the value and redirect the landing to a best-first agent that shares the same gateway — then sequence the higher-governance agent after the control plane is proven.

---

## The gateway-first message (say this in 60 seconds)

> "Your interest is automating real work in PowerSchool, Banner, Canvas, ServiceNow. The instant an agent can read and write a student's record, your security and privacy teams care about three things: can the agent do more than the person it's acting for, does a qualified human approve the consequential steps, and can you prove every access to a parent or an auditor. If each agent just holds API keys and calls systems directly, the answer to all three is *no* — and that's where education AI programs stall. So we put one governed layer between the agents and your systems. We build it once on the Concierge and every other agent reuses it. Fund it in the first phase — it's the control layer your CISO, privacy officer, and registrar need to say yes, and it's far cheaper to build first than to retrofit across eight agents later."

---

## Qualification questions — use these first

| Question | Strong "yes" signal means |
|---|---|
| "Where is your most acute, most *visible* student- or staff-facing pain — and can you measure it today?" | A landing use case with a baseline; favor 01/03/08/07 |
| "Are you trying to *act on* your systems of record, or just answer questions?" | If they want to act (write to SIS, open cases), the gateway story is mandatory and differentiating |
| "Has an AI effort here stalled at security/privacy review before?" | You are selling exactly the thing that unblocks it — lead with the gateway |
| "Who has to say yes — CISO, privacy/FERPA officer, registrar, academic leadership, the board?" | Maps your stakeholder set; use `docs/STAKEHOLDER-SECURITY-BRIEFINGS.md` |
| "What's your IdP, and can it express student/guardian/educator/counselor/admin — and age-of-majority and guardian relationships?" | Surfaces the hardest readiness gap, especially K–12 |
| "AWS account and Bedrock access — yes, or a path to it?" | Determines whether you can reach Deployable, or start in demo-mode POC |
| "One acute pain, or portfolio ambition over time?" | Portfolio ambition → the platform's build-once economics win decisively |

**Disqualify / slow down:** no appetite to act on systems of record; no path to AWS *and* unwilling to do a demo-mode POC; only higher-governance agents wanted with no governance maturity and no willingness to land a best-first agent first.

---

## Discovery cheat-sheet

| Question | What you're listening for | Red flag |
|---|---|---|
| "Walk me through what happens when a family member needs something urgently — say a FAFSA status at 9 PM." | Specific pain, named channel, volume language ("hundreds of emails"), measurable baseline | "It's not really a problem" — no baseline, no urgency |
| "Tell me about your AI governance posture — any AI policy, vendor AI review, FERPA/data officer involvement?" | Governance awareness, privacy officer engaged, past stalled effort | No governance function; "we just want to move fast" without any privacy involvement |
| "What's your IdP, and how do you manage student, guardian, educator, and staff access today?" | Named IdP (Okta, Entra, Google), some role differentiation | No IdP, AD only, or "everyone shares logins" |
| "What does your security team say when a vendor wants to access student records via API?" | Standard review process, DPA experience, named CISO or security delegate | "We haven't talked to security yet" — loop them in immediately |
| "What does the CFO or board want to see before expanding?" | Outcome metrics, pilot results, ROI model | "No budget" before discovery is done — often a sequencing issue, not a real no |

---

## Competitive positioning — the short version

| Alternative | Their strength | The boundary |
|---|---|---|
| **Point-solution edtech chatbot** | Fast to stand up, domain content, polished UX | Governs itself only; three products = three auth models, three audits, three security reviews; cross-system workflows fall between products |
| **Generic public AI (ChatGPT, etc.)** | Immediate, open-ended drafting, no integration needed | Cannot safely *act on* student records — no identity-scoped auth, no enforced human gate, no grounding to your content, no FERPA/COPPA audit trail |
| **DIY in-house build** | Full code ownership, no vendor dependency | The hard part is the governed access layer (auth, gate, masking, audit, fairness, red-team, accessibility) — exactly where in-house efforts stall |
| **LMS-native AI (e.g., Instructure IgniteAI)** | Deep LMS integration, faculty already there | Governs and reaches the LMS's world only; cross-system workflows (SIS + ERP + ITSM + comms) live outside it |
| **Microsoft Copilot for Education** | M365 integration, familiar interface, broad rollout | Microsoft-ecosystem only; no deny-by-default gateway across SIS/ERP/ITSM; FERPA/COPPA audit model built for enterprise IT, not EDU-specific disclosure recordkeeping |

**One-paragraph differentiator:** Every alternative governs a slice. This accelerator governs the whole surface: one MCP authorization gateway — deny-by-default, role-scoped, human-gated, PII-masked, fully audited — between every agent and every system of record, with the control plane built once and inherited by all eight agents. The competitors are good at their slice. The platform is good at the thing that actually blocks education AI programs: putting agents that *act on student records* into production, across the institution, in a way the CISO, privacy officer, and registrar will sign.

---

## Top objections and the short answer

| Objection | Short answer (full version in `OBJECTION-HANDLING.md`) |
|---|---|
| **"Student data / FERPA?"** | Every access passes the MCP gateway: deny-by-default, identity-scoped, human-gated on consequential actions, PII-masked audit trail aligned to FERPA disclosure recordkeeping. The gateway is the FERPA control. |
| **"AI replaces teachers/advisors?"** | Design forbids it. Bright line tested in code: agent never decides grades, admissions, discipline, financial aid, eligibility, or placement. It drafts, recommends, and routes; a named human owns every consequential action. |
| **"AI hallucinates?"** | Grounding verification — every fact traces to approved institutional content or fails fast. Prompt version pinning + eval harness catch drift. Human approves before any consequential action executes. |
| **"Accessible? ADA/508?"** | WCAG 2.2 AA is a build requirement and a production-readiness gate, not an afterthought. Agent 07 actively produces accessible content at scale with human verification on high-stakes material. |
| **"Biased / inequitable?"** | Fairness monitored as a metric: false-positive/false-negative monitoring by cohort on student-success targeting. Disparate impact surfaces as a number, not a complaint. PPRA-protected categories never inferred. |
| **"AWS/vendor lock-in?"** | Three hosting options: managed AgentCore Gateway, AWS primitives, or self-built FastMCP you own outright. Enforcement logic is readable Python in `platform_core/`. Systems of record stay yours. |
| **"Too expensive?"** | Control plane built once; Agents 02–08 inherit it — marginal cost of each addition drops sharply. Start with one agent, prove the outcome, expand against a control plane already paid for. Measure net of run cost. |
| **"Why not ChatGPT?"** | Public AI can *talk*; it cannot safely *act on student records*. No identity auth, no human gate, no grounding, no PII masking, no FERPA audit trail. The moment the use case crosses into acting on a real record, it needs the governed layer this platform provides. |
| **"We tried AI before and it stalled."** | It stalled at the security/privacy review — the exact gap this platform fills. The demo shows the controls working, not slides claiming they exist. Run the POC: your CISO watches a deny, a PII mask, and a human gate fire. |

---

## Deal-shaping moments

- **"Can we skip the gateway and add it later?"** No — that is the retrofit trap. Fund it in Phase 1; every agent reuses it. See `docs/WHY-THE-MCP-LAYER.md` §6, §8.
- **"Prove it's not just slides."** Demo-mode POC — they watch a deny, a PII mask, and a human-gated write happen. No API keys, no live systems. See `offerings/POC-OFFERING.md`.
- **"How do we measure success?"** Outcomes, not conversations. Baseline the five categories (Labor, Service, Learning, Student journey, Risk & quality) before deployment; measure the change. See `gtm/roi-calculator/` and `offerings/COST-ROI-MODEL.md`.
- **Procurement/security questionnaire lands.** Hand them the TPRM packet: `offerings/TPRM-DUE-DILIGENCE-PACKET.md`.
- **"Who pays for the pilot?"** AWS funding programs — PoA credits, MAP, Partner Development Funds. See `docs/AWS-FUNDING-AND-PREREQUISITES.md`.

---

## The maturity ladder — position honestly

| Rung | What it means | Offering |
|---|---|---|
| **Documented** | Architecture and compliance design written; good for discovery and architecture review | `ASSESSMENT-OFFERING.md` |
| **Demonstrated** | Runs end-to-end in demo mode (`EXTRACT_MODE=demo`, no API key, fixtures); good for the workshop and go/no-go | `POC-OFFERING.md` |
| **Deployable** | CloudFormation/Terraform, container contract, CI pass; needs customer AWS account and Bedrock | `PILOT-OFFERING.md` |
| **Production-ready** | Security/privacy review complete, IdP integrated, live connectors tested, WCAG 2.2 AA conformance tested, pen-tested | Pilot exit → `MANAGED-SERVICE-OFFERING.md` |

---

## Quick links

- Platform thesis: `ENTERPRISE-PLATFORM.md` | Gateway argument: `docs/WHY-THE-MCP-LAYER.md` | Architecture: `docs/SUITE-ARCHITECTURE.md`
- Stakeholders: `docs/STAKEHOLDER-SECURITY-BRIEFINGS.md` | Objections: `offerings/OBJECTION-HANDLING.md`
- Competitive: `offerings/COMPETITIVE-POSITIONING.md` | ROI: `offerings/COST-ROI-MODEL.md` | Calculator: `gtm/roi-calculator/`
- Offerings: `offerings/ASSESSMENT-OFFERING.md` · `POC-OFFERING.md` · `PILOT-OFFERING.md` · `MANAGED-SERVICE-OFFERING.md`
- TPRM: `offerings/TPRM-DUE-DILIGENCE-PACKET.md` | Compliance spine: `governance/README.md`
- AWS: `docs/AWS-FUNDING-AND-PREREQUISITES.md` | WAF: `docs/WELL-ARCHITECTED-GENAI-LENS.md` | Marketplace: `offerings/AWS-MARKETPLACE-GUIDE.md`
