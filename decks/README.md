# EDU AI Agent Suite — Go-to-Market Decks

Nine PowerPoint decks for the **EDU AI Agent Suite** — eight governed AI agents for
education institutions plus a refreshed executive suite overview. All are generated
from a single pptxgenjs generator so they share one master, palette, fonts, and motif;
only the content changes per agent.

> **Figures are cited.** Every ROI/stat on these slides traces to an entry in
> [`../gtm/EDU-DECK-SOURCES.md`](../gtm/EDU-DECK-SOURCES.md) and carries its source class
> on-slide (gov/peer-reviewed · foundation/research · sector-press/estimate · vendor).
> Vendor and estimate figures are flagged and never lead. Outcomes are modeled to the
> customer's baseline — not guaranteed.
>
> **Speaker notes** are on every slide and carry a `[MM:SS]` timing, a talk-track, how to
> position the slide (CIO/CISO vs academic leader vs practitioner), and — for the
> architecture and deploy slides — what the customer needs to deploy it.

## Index

| Deck | Agent | Headline metric (cited) |
|------|-------|--------------------------|
| `EDU-01-Student-Family-Concierge.pptx`        | 01 Student & Family Services Concierge | ~3 of 4 FAFSA calls unanswered (GAO-24-107407, 2024) |
| `EDU-02-Tutor-Study-Companion.pptx`           | 02 Personalized Tutor & Study Companion | >2x learned vs class (Harvard RCT) |
| `EDU-03-Educator-Copilot.pptx`                | 03 Educator Copilot | ~53 hrs/wk teacher workload (RAND, 2024) |
| `EDU-04-Assessment-Grading-Feedback.pptx`     | 04 Assessment, Grading & Feedback | Comparable to human grading, faster (RCT) |
| `EDU-05-Student-Success-Engagement.pptx`      | 05 Student Success & Proactive Engagement | 22.4% don't return year two (NSC 2024) |
| `EDU-06-Pathway-Navigator.pptx`               | 06 Academic / College / Career Pathway Navigator | ~43% transfer credits lost (GAO) |
| `EDU-07-Document-Accessibility-Services.pptx` | 07 Document & Accessibility Services | ~95% a11y complaints are PDFs; ADA 2027/2028 |
| `EDU-08-Operations-Service-Desk.pptx`         | 08 Operations / IT Service Desk | ~$70 per password reset (estimate) |
| `EDU-Agentic-AI-Suite-Executive-Overview.pptx`| Suite overview (executive) | The governed platform is the product |

## Per-agent deck narrative (6 slides, identical across all eight)

1. **Title / hook** — agent name, one-line value prop, "EDU AI Agent Suite · Governed AI on AWS" footer.
2. **The problem today** — the pain anchored by the single sharpest cited metric as a big stat
   callout with its source label, plus 2–3 "what we solve for" points.
3. **How we solve it — the governed pipeline** — the 4–6 step flow (retrieve approved content →
   analyze → draft/recommend → HITL gate for consequential → audit), shown as a numbered process
   flow with the agent's **bright line** (what a human always owns) called out.
4. **AWS architecture & traffic flow** — the request path drawn as labeled service boxes connected
   by arrows: request → CloudFront+WAF → Cognito → AgentCore Gateway (deny-by-default) →
   Bedrock+Guardrails → agent-specific tools/connectors → S3 Object Lock + DynamoDB audit.
5. **How to deploy** — a compact 5–7 step path mirroring the runbooks, ending in the deploy
   one-liner. Points to `runbooks/agent-deploy/<NN>-*.md` and `docs/AWS-DEPLOYMENT-REFERENCE.md`.
6. **ROI & honest tradeoffs** — 2–3 quantified outcomes as stat callouts with source-class labels,
   plus a "what this is / isn't" honesty note.

## Suite overview deck (11 slides)

Title · the thesis ("the agents are not the product; the governed platform is") · the shared AWS
platform architecture · the 8 agents as a portfolio grid · the governance spine (deny-by-default
gateway, HITL, audit, PII masking, accessibility/WCAG, fairness/four-fifths, NIST AI RMF) · the
maturity ladder (Documented / Demonstrated / Deployable / Production-ready) · deployment story
(runbooks + reference architecture) · recommended land-and-expand path (start 01/03/07/08) ·
ROI summary · standards alignment · closing.

## Design system

- **Palette:** deep academic navy `#1B2A4A` (primary / dark slides), teal `#0E7C7B` +
  seafoam `#3AA6A4` (secondary), warm amber `#E8A33D` (stat-callout accent), light `#F4F6F8`
  content background.
- **Fonts:** Cambria headers (safe serif) + Calibri body (safe sans) — QA-trustworthy for text fit.
- **Motif:** icons in colored circles, repeated across every slide; dark title/closing slides,
  light content slides. No accent stripes or color bars.

## Regenerating

The generator lives in the scratch project (`outputs/`): `data.js` (content), `theme.js`
(palette/fonts/icons), `build.js` (agent decks + speaker notes), `overview.js` (suite deck),
`run.js` (pre-renders icons, builds all nine). After generation each file is recompressed with
the pptx skill's `rezip.py`.
