# EDU AI Agent Suite — Go-to-Market Decks

Nine PowerPoint decks for the **EDU AI Agent Suite** — eight governed AI agents for
education institutions plus the executive suite overview. All nine are generated from a
single pptxgenjs generator ([`build-agent-decks.js`](build-agent-decks.js)) so they share
one consistent professional layout, palette, and fonts; only the per-agent content object changes.

Audience: **CIO / CFO / Director of Infrastructure / CISO.** Board-defensible metrics, an
explicit cost of doing nothing, and source-class tags on every stat.

> **Figures are cited.** Every ROI/stat traces to an entry in
> [`../gtm/EDU-DECK-SOURCES.md`](../gtm/EDU-DECK-SOURCES.md) and carries its source class
> on-slide: `[gov/peer-reviewed]` · `[foundation/research]` · `[sector-press/estimate]` ·
> `[vendor]` · `[modeled]`. Vendor and estimate figures are flagged and never lead.
> Modeled cost-of-doing-nothing figures show their arithmetic on-slide and are substituted
> with the customer's actual volumes — never guaranteed.
>
> **Speaker notes** are on every slide: a `[MM:SS]` timing, a talk-track, how to position
> to a CIO/CFO/CISO, and — on the architecture and deploy slides — exactly what the customer
> must provide to deploy.

## Index

| Deck | Agent | Headline metric (cited) | Cost of doing nothing |
|------|-------|--------------------------|------------------------|
| `EDU-01-Student-Family-Concierge.pptx`        | 01 Student & Family Services Concierge | ~4M of 5.4M FAFSA calls unanswered (GAO-24-107407) | ~$1.2M–$1.6M/yr (modeled) |
| `EDU-02-Tutor-Study-Companion.pptx`           | 02 Personalized Tutor & Study Companion | >2× learned vs. class (Harvard RCT) | ~$1.2M–$2.5M+/yr (modeled) |
| `EDU-03-Educator-Copilot.pptx`                | 03 Educator Copilot | ~53 hrs/wk teacher workload (RAND 2024) | ~$11.9K–$24.9K/teacher (LPI, direct) |
| `EDU-04-Assessment-Grading-Feedback.pptx`     | 04 Assessment, Grading & Feedback | Comparable to human grading, faster (RCTs) | ~$4,270/instructor/yr (modeled) |
| `EDU-05-Student-Success-Engagement.pptx`      | 05 Student Success & Proactive Engagement | 22.4% don't return year two (NSC 2025) | ~$5.6M/yr forgone tuition (modeled) |
| `EDU-06-Pathway-Navigator.pptx`               | 06 Pathway Navigator | ~43% transfer credits lost (GAO/CHEPP) | $13,081–$26,396/student (CHEPP, direct) |
| `EDU-07-Document-Accessibility-Services.pptx` | 07 Document & Accessibility Services | ADA Title II 4/26/2027; ~95% complaints are PDFs | $30K–$815K exposure (sector-press) |
| `EDU-08-Operations-Service-Desk.pptx`         | 08 Operations / IT Service Desk | 20–50% of calls are password issues (~$70/reset) | ~$300K/yr deflectable (modeled) |
| `EDU-Agentic-AI-Suite-Executive-Overview.pptx`| Suite overview (executive) | The governed platform is the product | Suite-level cost-of-inaction summary |

> `EDU-CIO-Adoption-Review.pptx` is a separate board deck built by `build-cio-deck.js`; it is
> not part of this generator and is left untouched.

## Per-agent deck — 6-slide executive narrative

Every agent deck follows the user's required order — **ISSUE → COST OF DOING NOTHING → HOW WE
SOLVE IT → ARCHITECTURE → PROOF** — using a consistent professional layout:

1. **Title** *(navy)* — agent name; orange subtitle "A Governed Agentic AI Reference
   Architecture for Education"; footer "EDU AI Agent Suite · Built on AWS · June 2026".
2. **The issue at a glance** *(navy stat/hook)* — a punchy "FROM X TO Y"-style hero headline, an
   italic one-line value prop, and three stat cards (big orange numbers, gray labels, source tags).
3. **The issue & the cost of doing nothing** *(light, two cards + dark callout bar)* — left card
   "THE ISSUE" (navy accent); right card "THE COST OF DOING NOTHING" (orange accent) with the CFO
   dollar figure, the modeled arithmetic in plain text, and hard-risk bullets; a dark bottom bar
   carries the agent's **bright line** (the design line: the agent drafts/recommends; a named human
   owns every consequential decision).
4. **How we solve it — a governed pipeline** *(light, numbered flow + 3 cards)* — the 5-step flow
   (retrieve approved content → analyze → draft/recommend → **HITL gate, in red** → audit), plus
   three assurance cards (Every action audited · Grounded & explainable · AI never decides
   *the consequential thing*).
5. **AWS architecture & traffic flow** *(light diagram)* — the most important slide. Dashed group
   containers (INSTITUTION/EXTERNAL; AWS CLOUD — PER-CUSTOMER VPC with EDGE/PUBLIC, PRIVATE/runtime,
   MODEL LAYER, DATA TIER), AWS-category-colored service boxes (compute orange, integration magenta,
   storage olive, model/db teal, networking purple), a dark SECURITY & OPS bar, numbered orange
   traffic-flow circles (1–8) and a numbered legend along the bottom. Agent-specific blocks are
   shown per agent (e.g. 05 EventBridge+SQS+Step Functions; 07 Textract+Translate; 04 Step Functions
   HITL gradebook gate; 01 Amazon Connect+Translate).
6. **Proof, payback & how to deploy** *(navy)* — left card "MEASURED OUTCOMES" (2×2 big orange stats
   with tags + payback framing); right card "WHAT IT TAKES TO DEPLOY" (compact 5–6 step path) ending
   in the deploy one-liner and a pointer to `runbooks/agent-deploy/<NN>-*.md` and
   `docs/AWS-DEPLOYMENT-REFERENCE.md`; a dark bottom bar carries the takeaway: *the agent isn't the
   product — the governed platform that makes it FERPA/ADA-defensible and deployable on AWS is.*

## Suite overview deck (~11 slides)

Title · the thesis ("everyone's moving, few are governed") · the **shared AWS architecture &
traffic flow** (same diagram, generalized to the platform) · the **8-agent portfolio grid**
(two slides: land-first 01/03/07/08, then higher-governance 02/04/05/06; each tile = name +
value + headline metric + cost of doing nothing) · the **governance/compliance spine**
(FERPA · COPPA · IDEA/ADA Title II · GLBA · Title VI · NIST AI RMF mapped to platform controls) ·
the **maturity ladder** (Assist → Draft → Proactive → Orchestrated) · the **deployment story**
(one platform, per-customer isolation, six stages) · the **land-and-expand path** (LAND 01/03/07/08
→ EXPAND 04/02 → SCALE 05/06) · the **suite-level cost-of-inaction summary** (all eight figures) ·
the takeaway.

## Design system (AWS standard)

- **Palette:** deep navy `#232F3E` (dark slides, titles); amber `#FF9900` (accents, big
  stat numbers, the thin left-edge brand bar on every slide, step numbers); teal/green `#16A085`
  (secondary / positive flow boxes); red `#C0392B` (reserved for the HUMAN-GATE box only); light
  gray `#F2F3F4` content backgrounds; white cards with subtle shadow. The architecture diagram uses
  AWS category colors — compute orange, integration magenta `#E7157B`, storage olive `#7AA116`,
  model/db teal, networking purple `#8C4FFF`.
- **Left-edge bar:** a thin (~0.14") AWS-orange bar runs down the far-left edge of **every** slide —
  intentional AWS-brand styling from the reference template.
- **Fonts:** Arial bold titles (white on dark, navy on light); Cambria italic taglines; Calibri body.
  All QA-safe fonts so text-fit checks are trustworthy. Stat numbers 28–40pt orange.
- **Footer** on content slides: "EDU AI Agent Suite · Governed Agentic AI on AWS" (or the
  Built-on-AWS line on navy slides).

## Regenerating

```bash
# from repo root, with pptxgenjs installed in node_modules
node decks/build-agent-decks.js
# then recompress each file with the pptx skill's rezip.py
```

The generator is fully self-contained: one `AGENTS` array of per-agent content objects drives the
eight agent decks, and `buildOverview()` drives the suite deck, all through shared slide-builder
functions so the layout stays identical across all nine. Each deck is a fresh `pptxgen` instance.
After generation, recompress every `.pptx` with the pptx skill's `rezip.py` (pptxgenjs writes an
uncompressed ZIP).
