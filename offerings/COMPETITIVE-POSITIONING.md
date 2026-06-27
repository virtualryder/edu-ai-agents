# Competitive Positioning
### How the Governed EDU AI Agent Suite Compares — and Where the Alternatives Are Genuinely Strong

> The honest case for this accelerator is not that the alternatives are bad. It is that they solve a **narrower problem**. Point-solution chatbots, public AI assistants, a DIY in-house build, and LMS-native AI each have real strengths and a legitimate place. What none of them is, by design, is a **governed, cross-system platform** in which one authorization, identity, human-gate, and audit layer — the **MCP authorization gateway** — sits between *every* agent and *every* system of record. That is the differentiator: not a smarter model, but a control plane that makes agents that *act on student records* deployable across the institution and reusable across a portfolio. This document is written to be fair to each alternative and clear about the boundary.

---

## 1. The four alternatives at a glance

| | Point-solution edtech chatbot | Generic public AI assistant | DIY in-house build | LMS-native AI (e.g., Instructure IgniteAI) | **This accelerator** |
|---|---|---|---|---|---|
| Acts across SIS + LMS + ERP + CRM + ITSM | Rarely (single domain) | No | Possible, but you build every integration | Within the LMS's reach | **Yes — one governed gateway across all** |
| Governed authorization (deny-by-default, role-scoped, agent ≤ human) | Vendor-defined, varies | None | You build it | LMS-scoped | **Yes, uniform across agents** |
| Enforced human gate on consequential actions | Sometimes | No | You build it | Varies | **Framework-enforced, tested** |
| FERPA/COPPA-tuned PII masking + append-only audit | Varies | No | You build it | LMS audit, LMS scope | **Yes, shared platform** |
| Grounding to *your* approved content | Sometimes | No | You build it | Within LMS content | **Yes, fail-fast** |
| WCAG 2.2 AA as a gate | Varies | N/A | You own it | Vendor posture | **Build + production gate** |
| Reuse across many agents (build-once control plane) | No | No | Only if you architect it | LMS features only | **Yes — the core economic argument** |
| Hosting flexibility / code ownership | Vendor SaaS | Vendor SaaS | Total (you own it) | Vendor SaaS | **Three options: managed / primitives / self-built** |

---

## 2. Versus point-solution edtech chatbots

**What they're genuinely good at.** Purpose-built edtech assistants are fast to stand up in their domain and often arrive with domain content and a polished UX. Many are proven: the references this suite respects — Highline's financial-aid self-service, UA–Pulaski Tech's MyAgent — are exactly this class of focused, outcome-producing deployment, and a well-chosen point solution can be the right answer when an institution has one acute, bounded pain and no portfolio ambition.

**Where the boundary is.** A point solution governs *itself*. Deploy three of them and you have three authorization models, three audit trails, three PII postures, three security reviews, and three vendor-defined notions of "who is allowed to do what." Cross-system workflows (a Concierge that checks aid status *and* opens an advising case *and* drafts a family message across SIS, case management, and comms) fall between the products. The governance does not compound — improving one product's controls does nothing for the others.

**Our position.** Land where a point solution would (often the Concierge), but on a platform whose gateway, identity, human-gate, and audit are **built once and inherited** by every subsequent agent. The first agent costs about what a point solution costs to govern properly; agents two through eight are dramatically cheaper because they reuse the control plane. You are buying an integration-and-governance capability the institution keeps, not a sealed product.

---

## 3. Versus generic public AI assistants

**What they're genuinely good at.** General-purpose assistants are excellent at open-ended drafting, explanation, and ideation, are immediately available, and need no integration. For brainstorming a lesson outline or explaining a concept, they are a fine tool, and many educators already use them well.

**Where the boundary is.** A public assistant can *talk*; it cannot safely *act on your student records*. It has no identity-scoped authorization (it cannot enforce that a student sees only their own record, or that a guardian's access ends at the FERPA age-of-majority transfer), no enforced human gate, no grounding to your approved content (so it will state a wrong deadline with confidence), no FERPA/COPPA-tuned PII masking, and no audit trail to answer a parent or an auditor. It typically lives outside the institution's data-residency and governance boundary. The moment the assistant needs to check a real financial-aid status or write to the SIS, it needs the governed layer it does not have.

**Our position.** The instant the use case crosses from "help me write something" to "act on a student's record," the public assistant is the wrong category. This suite runs inference on **Amazon Bedrock** reached over AWS PrivateLink (an interface VPC endpoint) rather than the public internet — Bedrock runs in the AWS service, reached privately — with direct identifiers minimized/masked before inference, grounds to the institution's content, and gates every consequential action — turning generative capability into a *governed* agent. Public AI is a consumer tool; this is a FERPA-governed system of action.

---

## 4. Versus a DIY in-house build

**What it's genuinely good at.** A capable institutional platform-engineering team can build exactly what it wants, owns all the code, and avoids vendor dependency. For a university with a strong platform org — or a district consortium building a shared service — this is a legitimate path, and the suite respects it enough to make the self-built **FastMCP** option a first-class hosting choice.

**Where the boundary is.** The hard part of "build agents on student data" is not the chat loop — it is the **governed access layer**: deny-by-default authorization, least-privilege role intersection across student/guardian/educator/counselor/administrator, age-of-majority and guardian-relationship handling, the enforced human gate, short-lived scoped tokens, PII masking tuned to FERPA/COPPA, grounding, an append-only audit aligned to FERPA recordkeeping, the eval/fairness/red-team frameworks, and WCAG 2.2 AA conformance. Building that well, then maintaining it under model and prompt drift, is most of the cost and most of the risk — and it is precisely where in-house efforts stall at the security and privacy review.

**Our position.** This accelerator *is* that governed layer, designed so an in-house team can adopt it without lock-in: the enforcement logic is readable, testable Python in `platform_core/`, and the FastMCP option lets the institution own the server outright. Build-vs-buy is not all-or-nothing — buy the control design and the compounding governance, own the code if you want to. You skip rebuilding the hardest, most compliance-sensitive part from scratch.

---

## 5. Versus LMS-native AI (e.g., Instructure IgniteAI / Canvas)

**What it's genuinely good at.** LMS-native AI is deeply integrated where teaching and learning already happen, with native access to course content, rosters, and gradebook context, and no extra surface for faculty to learn. For in-LMS instructional tasks it has a real home-field advantage, and the ecosystem is strong — this suite explicitly surfaces inside the LMS via **LTI 1.3**, and references such as Instructure IgniteAI/Canvas, Panorama Solara, Otus, and Blackboard on Amazon Connect are part of the landscape the platform interoperates with rather than fights.

**Where the boundary is.** The LMS governs and reaches the **LMS's** world. The institution's hardest, highest-value AI workflows are **cross-system**: enrollment and financial-aid status (SIS/CRM), document processing and accessibility transformation (SIS + document store), IT and staff operations (ITSM/ERP), proactive student-success outreach (SIS + attendance + case management + comms). Those live partly or wholly outside the LMS, and an LMS-native assistant has neither the reach nor the uniform authorization/audit posture across them.

**Our position.** Complement, don't compete. Use the LMS-native AI for in-LMS instructional work where it shines, and use this accelerator's governed gateway as the **cross-system control plane** for everything that spans SIS, ERP, CRM, ITSM, and comms — with the Educator Copilot surfacing inside the LMS via LTI 1.3 where the two worlds meet. The differentiator is not "instead of the LMS" but "across all the systems the LMS can't govern, under one auditable layer."

---

## 6. The one-paragraph differentiator

> Every alternative governs a slice — one product, one model, one codebase you must build, or one LMS. This accelerator governs the **whole surface**: one MCP authorization gateway — deny-by-default, role-scoped so an agent can never exceed the human, human-gated on consequential actions, PII-masked and fully audited — between every agent and every system of record, with the control plane built once and inherited by all eight agents. It runs inference in-account on Bedrock, grounds to the institution's approved content, meets WCAG 2.2 AA as a gate, monitors fairness as a metric, and offers three hosting options so the institution is never locked in. The competitors are good at their slice. The platform is good at the thing that actually blocks education AI programs: putting agents that *act on student records* into production, across the institution, in a way the CISO, privacy officer, and registrar will sign.

---

## 7. Related material

- `OBJECTION-HANDLING.md` (#6 lock-in, #10 "why not ChatGPT"), `ENTERPRISE-PLATFORM.md` (the platform-not-chatbots thesis), `docs/WHY-THE-MCP-LAYER.md` (the gateway and its three hosting options), `COST-ROI-MODEL.md` (build-once economics), `SOLUTION-FIELD-GUIDE.md` (how to position in a live deal).
