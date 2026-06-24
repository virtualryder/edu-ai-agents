/* EDU AI Agent Suite — CIO / Director of Infrastructure Adoption Review
   Board-ready deck. Matches suite visual language (navy 1E2761 / teal 00A896 / amber accent).
*/
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const Fa = require("react-icons/fa");

// ---------- palette ----------
const NAVY   = "1E2761"; // primary
const NAVYDK = "12183A"; // dark title/closing
const NAVY2  = "232C57";
const TEAL   = "00A896"; // secondary
const TEALDK = "067A6E";
const TEALLT = "7FE3D2";
const AMBER  = "E8A33D"; // accent for callouts
const AMBERDK = "B5790F";
const SLATE  = "33384F"; // body text on light
const SLATE2 = "5A6485"; // muted
const ICE    = "CADCFC";
const BGLT   = "F4F7FC"; // light content bg
const CARD   = "FFFFFF";
const CARDTINT = "EEF2FB";
const WHITE  = "FFFFFF";
const LINE   = "D9E0EF";
const RED    = "C2543B"; // risk
const GREEN  = "2E7D5B";

// owner colors for the matrix
const OWN_USER = "5A6485";   // User  (slate)
const OWN_CUST = "1E2761";   // Customer (navy)
const OWN_DEV  = "00A896";   // Developer / SI (teal)

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3 x 7.5
pres.author = "EDU AI Agent Suite";
pres.title  = "EDU AI Agent Suite — Infrastructure & Adoption Review";
const PW = 13.333, PH = 7.5;

// ---------- icon helper ----------
const iconCache = {};
async function icon(Comp, color = "FFFFFF", size = 256) {
  const key = Comp.name + color + size;
  if (iconCache[key]) return iconCache[key];
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(Comp, { color: "#" + color, size: String(size) })
  );
  const png = await sharp(Buffer.from(svg)).png().toBuffer();
  const data = "image/png;base64," + png.toString("base64");
  iconCache[key] = data;
  return data;
}
const shadow = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 90, opacity: 0.16 });
const softShadow = () => ({ type: "outer", color: "000000", blur: 5, offset: 2, angle: 90, opacity: 0.10 });

// ---------- reusable: icon in a circle ----------
async function iconCircle(slide, Comp, cx, cy, d, circleColor, iconColor) {
  slide.addShape(pres.shapes.OVAL, { x: cx, y: cy, w: d, h: d, fill: { color: circleColor }, line: { type: "none" } });
  const ip = d * 0.26;
  slide.addImage({ data: await icon(Comp, iconColor), x: cx + ip, y: cy + ip, w: d - 2 * ip, h: d - 2 * ip });
}

// ---------- light content slide scaffold ----------
function lightHeader(slide, kicker, title, num) {
  slide.background = { color: BGLT };
  slide.addText(kicker.toUpperCase(), { x: 0.6, y: 0.34, w: 10.5, h: 0.3, fontFace: "Calibri",
    fontSize: 12, bold: true, color: TEAL, charSpacing: 2, margin: 0 });
  slide.addText(title, { x: 0.6, y: 0.62, w: 11.4, h: 0.7, fontFace: "Cambria",
    fontSize: 27, bold: true, color: NAVY, margin: 0 });
  slide.addText(String(num), { x: PW - 0.92, y: 0.34, w: 0.5, h: 0.34, align: "center",
    fontFace: "Calibri", fontSize: 12, bold: true, color: SLATE2, margin: 0 });
}

function footer(slide) {
  slide.addText("EDU AI Agent Suite  ·  Infrastructure & Adoption Review  ·  Governed accelerator, not a turnkey certified product",
    { x: 0.6, y: PH - 0.36, w: 12.1, h: 0.28, fontFace: "Calibri", fontSize: 8.5, color: SLATE2, margin: 0 });
}

// =====================================================================
// SLIDE 1 — TITLE (dark)
// =====================================================================
async function slideTitle() {
  const s = pres.addSlide();
  s.background = { color: NAVYDK };
  s.addShape(pres.shapes.OVAL, { x: 10.4, y: -1.4, w: 4.6, h: 4.6, fill: { color: NAVY2 }, line: { type: "none" } });
  s.addShape(pres.shapes.OVAL, { x: 11.6, y: 4.6, w: 3.4, h: 3.4, fill: { color: NAVY }, line: { type: "none" } });
  await iconCircle(s, Fa.FaShieldAlt, 0.7, 0.66, 0.92, TEAL, WHITE);
  s.addText("EDU AI AGENT SUITE", { x: 1.78, y: 0.74, w: 8, h: 0.4, fontFace: "Calibri",
    fontSize: 15, bold: true, color: TEALLT, charSpacing: 3, margin: 0 });

  s.addText("Infrastructure &\nAdoption Review", { x: 0.7, y: 2.05, w: 9.2, h: 2.0, fontFace: "Cambria",
    fontSize: 50, bold: true, color: WHITE, lineSpacingMultiple: 0.98, margin: 0 });
  s.addText("A CIO / Director of Infrastructure perspective", { x: 0.72, y: 4.05, w: 10, h: 0.5,
    fontFace: "Cambria", italic: true, fontSize: 21, color: ICE, margin: 0 });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 5.15, w: 11.9, h: 1.2, rectRadius: 0.08,
    fill: { color: NAVY2 }, line: { color: TEAL, width: 1 } });
  s.addText([
    { text: "THE VERDICT, UP FRONT   ", options: { bold: true, color: TEALLT, fontSize: 12, charSpacing: 1 } },
    { text: "Adopt as a governed accelerator to compress an SI-led build — not as a turnkey, certified product.",
      options: { color: WHITE, fontSize: 14.5 } },
  ], { x: 1.0, y: 5.34, w: 11.3, h: 0.84, fontFace: "Calibri", valign: "middle", margin: 0 });

  s.addText("8 governed agents · AWS-native · FERPA / COPPA / IDEA / ADA Title II / NIST AI RMF",
    { x: 0.72, y: 6.62, w: 11.8, h: 0.4, fontFace: "Calibri", fontSize: 12.5, color: SLATE2, margin: 0 });
  s.addNotes(
    "Frame the room: you are the CIO / Director of Infrastructure, and your job tonight is to tell the board honestly what this is and is not. " +
    "Lead with the verdict so no one waits for the punchline: this is a governed accelerator that compresses a systems-integrator-led build, NOT a shrink-wrapped certified product you switch on. " +
    "The whole deck earns that one sentence — strengths first, then the shortfalls candidly, then a phased path. " +
    "The decision you will ask for at the end is approval to fund a Phase-1 pilot on the lowest-risk agents, not a suite-wide commitment.");
}

// =====================================================================
// SLIDE 2 — BOTTOM LINE UP FRONT (dark)
// =====================================================================
async function slideBLUF() {
  const s = pres.addSlide();
  s.background = { color: NAVYDK };
  s.addText("BOTTOM LINE UP FRONT", { x: 0.7, y: 0.5, w: 10, h: 0.4, fontFace: "Calibri",
    fontSize: 13, bold: true, color: TEAL, charSpacing: 2, margin: 0 });
  s.addText("Adopt it as a governed accelerator — not a finished product", { x: 0.7, y: 0.86, w: 12, h: 0.8,
    fontFace: "Cambria", fontSize: 29, bold: true, color: WHITE, margin: 0 });

  const cards = [
    { ic: Fa.FaCheckCircle, col: TEAL, h: "What you are buying",
      b: "A governance spine in code + tests, AWS deployment runbooks, and a six-layer reference architecture. It hands an SI a compliant, auditable starting point across 8 education workflows." },
    { ic: Fa.FaTools, col: AMBER, h: "What you still build",
      b: "Edge & observability IaC, live SIS/LMS/ERP/ITSM connectors, the reviewer UI, IdP federation, accessibility conformance, and a penetration test. This is an engagement, not an install." },
    { ic: Fa.FaBalanceScale, col: ICE, h: "Why that is the right buy",
      b: "It moves the hard, slow, risky part — governed access, HITL, audit, PII masking — off your critical path. You compress months of SI build while keeping FERPA accountability where it belongs: with you." },
  ];
  let x = 0.7; const cw = 3.86, gap = 0.27, cy = 1.95, ch = 3.25;
  for (const c of cards) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: cy, w: cw, h: ch, rectRadius: 0.1,
      fill: { color: NAVY2 }, line: { type: "none" }, shadow: shadow() });
    await iconCircle(s, c.ic, x + 0.3, cy + 0.32, 0.78, c.col, NAVYDK);
    s.addText(c.h, { x: x + 0.3, y: cy + 1.22, w: cw - 0.6, h: 0.5, fontFace: "Cambria",
      fontSize: 16.5, bold: true, color: WHITE, margin: 0 });
    s.addText(c.b, { x: x + 0.3, y: cy + 1.72, w: cw - 0.6, h: ch - 1.9, fontFace: "Calibri",
      fontSize: 12, color: ICE, margin: 0, lineSpacingMultiple: 1.04 });
    x += cw + gap;
  }

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 5.5, w: 11.93, h: 1.28, rectRadius: 0.08,
    fill: { color: TEAL }, line: { type: "none" } });
  s.addText([
    { text: "Recommendation:  ", options: { bold: true, color: NAVYDK, fontSize: 15 } },
    { text: "Approve a funded Phase-1 pilot on the lowest-decision-risk agents. Prove the gateway, audit, and HITL gate in production, then expand. Do not present this to the board as a product you can turn on next week.",
      options: { color: NAVYDK, fontSize: 13.5 } },
  ], { x: 1.05, y: 5.62, w: 11.2, h: 1.04, fontFace: "Calibri", valign: "middle", margin: 0 });
  s.addNotes(
    "This is the slide you would put on screen if you only had one. Three columns: what you buy, what you still build, why the trade is right. " +
    "The honest tension you are managing: leadership hears 'AI agents' and assumes a SaaS subscription. Reset that expectation here, calmly. " +
    "The value is real but it is acceleration of an SI build, not elimination of one. If a board member pushes 'so it's not finished?' — agree plainly: correct, and that is normal and expected for governed AI touching student records in 2026. " +
    "Land on the recommendation bar: fund a pilot, prove the controls in production, expand on evidence.");
}

// =====================================================================
// SLIDE 3 — WHAT IT ACTUALLY IS (maturity ladder)  light
// =====================================================================
async function slideMaturity() {
  const s = pres.addSlide();
  lightHeader(s, "What it actually is", "The maturity ladder — positioned honestly", 3);

  const rungs = [
    { lvl: "Documented", col: SLATE2, txt: "Architecture, workflow & compliance design written and reviewed", reached: true },
    { lvl: "Demonstrated", col: TEAL, txt: "Runs end-to-end in demo mode — deterministic fixtures, no API key (80 tests green)", reached: true },
    { lvl: "Deployable", col: NAVY, txt: "CloudFormation + Terraform + container contract pass CI; needs your AWS account + Bedrock", reached: true },
    { lvl: "Production-ready", col: AMBER, txt: "Security review, IdP, live connectors, WCAG 2.2 AA conformance, pen test — the engagement", reached: false },
  ];
  let y = 1.55; const rh = 1.18, rw = 6.5;
  for (let i = 0; i < rungs.length; i++) {
    const r = rungs[i];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y, w: rw, h: rh - 0.16, rectRadius: 0.07,
      fill: { color: r.reached ? CARD : CARDTINT }, line: { color: r.reached ? r.col : LINE, width: r.reached ? 1.25 : 1 },
      shadow: r.reached ? softShadow() : undefined });
    s.addShape(pres.shapes.OVAL, { x: 0.82, y: y + 0.21, w: 0.62, h: 0.62, fill: { color: r.col }, line: { type: "none" } });
    s.addText(String(i + 1), { x: 0.82, y: y + 0.21, w: 0.62, h: 0.62, align: "center", valign: "middle",
      fontFace: "Cambria", fontSize: 18, bold: true, color: WHITE, margin: 0 });
    s.addText([
      { text: r.lvl, options: { bold: true, fontSize: 15, color: r.reached ? NAVY : SLATE2, breakLine: true } },
      { text: r.txt, options: { fontSize: 11, color: SLATE, breakLine: false } },
    ], { x: 1.62, y: y + 0.1, w: rw - 1.25, h: rh - 0.32, fontFace: "Calibri", valign: "middle", margin: 0, lineSpacingMultiple: 1.0 });
    if (!r.reached) {
      s.addText("BRIGHT LINE — the engagement starts here", { x: 0.6, y: y + rh - 0.2, w: rw, h: 0.26,
        fontFace: "Calibri", fontSize: 9.5, italic: true, bold: true, color: AMBERDK, align: "right", margin: 0 });
    }
    y += rh;
  }

  const rx = 7.4, rwc = 5.3;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: rx, y: 1.55, w: rwc, h: 2.42, rectRadius: 0.09,
    fill: { color: CARD }, line: { color: TEAL, width: 1.25 }, shadow: softShadow() });
  await iconCircle(s, Fa.FaCheckCircle, rx + 0.26, 1.78, 0.6, TEAL, WHITE);
  s.addText("Real today", { x: rx + 1.0, y: 1.83, w: rwc - 1.2, h: 0.5, fontFace: "Cambria", fontSize: 16, bold: true, color: NAVY, margin: 0 });
  s.addText([
    { text: "Governance spine in code + 80 passing tests (gateway intersection, HITL, masking, red-team)", options: { bullet: true, breakLine: true } },
    { text: "Empty-account-to-running deployment runbooks; 6 validated CloudFormation templates + Terraform", options: { bullet: true, breakLine: true } },
    { text: "AWS-native reference path: AgentCore Runtime container + Step Functions / Lambda HITL", options: { bullet: true } },
  ], { x: rx + 0.28, y: 2.42, w: rwc - 0.55, h: 1.5, fontFace: "Calibri", fontSize: 10.7, color: SLATE, margin: 0, paraSpaceAfter: 5, lineSpacingMultiple: 0.98 });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: rx, y: 4.12, w: rwc, h: 2.42, rectRadius: 0.09,
    fill: { color: CARDTINT }, line: { color: AMBER, width: 1.25 } });
  await iconCircle(s, Fa.FaSeedling, rx + 0.26, 4.35, 0.6, AMBER, WHITE);
  s.addText("A starting point, not finished", { x: rx + 1.0, y: 4.4, w: rwc - 1.2, h: 0.5, fontFace: "Cambria", fontSize: 16, bold: true, color: NAVY, margin: 0 });
  s.addText([
    { text: "Live connectors are stubs; agents are at Demonstrated depth, brought to Deployable per pass", options: { bullet: true, breakLine: true } },
    { text: "AgentCore Gateway / Runtime register via customer-supplied custom-resource placeholders", options: { bullet: true, breakLine: true } },
    { text: "No SOC 2 of its own, no 3rd-party cert, no conformance-tested production surface yet", options: { bullet: true } },
  ], { x: rx + 0.28, y: 5.0, w: rwc - 0.55, h: 1.5, fontFace: "Calibri", fontSize: 10.7, color: SLATE, margin: 0, paraSpaceAfter: 5, lineSpacingMultiple: 0.98 });
  footer(s);
  s.addNotes(
    "Use the ladder to set honest expectations. The suite is genuinely at Demonstrated and Deployable-by-design: the code runs, the tests pass, the IaC validates. " +
    "The bright line is rung 4 — Production-ready — which is explicitly the engagement, not a day-one deliverable. Don't let anyone read 'Deployable' as 'in production.' " +
    "Right column is the candor: real assets on top, the 'starting point' caveats on the bottom. If asked why connectors are stubs — that is deliberate: live connectors must be validated against the institution's own SIS/LMS and gated by a signed pilot SOW. " +
    "The 80 passing tests are your strongest credibility point: governance is in code and tested, not a slideware promise.");
}

// =====================================================================
// SLIDE 4 — WHY A CISO / PRIVACY OFFICER CAN SAY YES  light
// =====================================================================
async function slideWhyYes() {
  const s = pres.addSlide();
  lightHeader(s, "The strength", "Why a CISO or privacy officer can say yes", 4);
  s.addText("Governance-first: the controls are enforced in the gateway, outside the model — a prompt cannot turn them off.",
    { x: 0.6, y: 1.35, w: 12.1, h: 0.4, fontFace: "Calibri", fontSize: 13, italic: true, color: SLATE2, margin: 0 });

  const items = [
    { ic: Fa.FaLock, h: "Deny-by-default gateway", b: "permitted(tool) = agent-grant ∩ user-entitlement. An agent can never exceed the human it acts for. Denies on a missing subject." },
    { ic: Fa.FaUserCheck, h: "Framework-enforced HITL", b: "Consequential actions block as PENDING_APPROVAL until a named, correctly-roled reviewer binds their identity. Fails closed on timeout." },
    { ic: Fa.FaClipboardList, h: "Tamper-evident audit", b: "Append-only DynamoDB + S3 Object Lock WORM. Every ALLOW / DENY / PENDING / ERROR logged with lineage — FERPA disclosure recordkeeping." },
    { ic: Fa.FaUserSecret, h: "Student-PII masking", b: "FERPA/COPPA identifiers replaced with stable pseudonyms before any prompt or audit record. Stateless, runs before every call." },
    { ic: Fa.FaUniversalAccess, h: "Accessibility pre-flight", b: "Alt-text, heading order, link purpose, plain-language grade checks on generated content; Agent 07 produces accessible formats." },
    { ic: Fa.FaBalanceScale, h: "Four-fifths fairness screen", b: "Disparate-impact + representativeness check on any flag/rank workflow; outcomes routed to human equity review — no automated adverse action." },
  ];
  for (let i = 0; i < items.length; i++) {
    const it = items[i];
    const col = i % 3, row = Math.floor(i / 3);
    const cw = 3.92, ch = 1.62, gx = 0.18, gy = 0.18;
    const cx = 0.6 + col * (cw + gx), cyy = 1.95 + row * (ch + gy);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: cyy, w: cw, h: ch, rectRadius: 0.08,
      fill: { color: CARD }, line: { color: LINE, width: 1 }, shadow: softShadow() });
    await iconCircle(s, it.ic, cx + 0.24, cyy + 0.24, 0.62, NAVY, WHITE);
    s.addText(it.h, { x: cx + 0.98, y: cyy + 0.22, w: cw - 1.15, h: 0.62, fontFace: "Cambria",
      fontSize: 13.5, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText(it.b, { x: cx + 0.24, y: cyy + 0.86, w: cw - 0.45, h: ch - 0.96, fontFace: "Calibri",
      fontSize: 10, color: SLATE, margin: 0, lineSpacingMultiple: 0.98 });
  }
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 5.62, w: 12.13, h: 1.18, rectRadius: 0.07,
    fill: { color: NAVY }, line: { type: "none" } });
  await iconCircle(s, Fa.FaShieldAlt, 0.82, 5.84, 0.74, TEAL, WHITE);
  s.addText([
    { text: "Mapped to the EDU regulatory stack:  ", options: { bold: true, color: TEALLT, fontSize: 12 } },
    { text: "FERPA · COPPA · PPRA · IDEA / Section 504 · ADA Title II / 508 / WCAG 2.2 AA · GLBA · Title VI/OCR · NIST AI RMF 1.0. The bright line — grades, admissions, discipline, financial aid, IEP eligibility, placement — is never decided by the agent.",
      options: { color: WHITE, fontSize: 11.5 } },
  ], { x: 1.7, y: 5.74, w: 10.85, h: 0.95, fontFace: "Calibri", valign: "middle", margin: 0, lineSpacingMultiple: 0.98 });
  footer(s);
  s.addNotes(
    "This is the slide that gets your CISO and privacy officer to lean in. The key message: the controls live in the gateway, OUTSIDE the model. A prompt injection cannot disable deny-by-default, the HITL gate, or the audit trail. " +
    "Six control cards plus the regulatory-stack strip. Emphasize the intersection rule — the agent can never do more than the human on whose behalf it acts — and that the HITL gate fails closed: if the reviewer queue backs up, consequential actions pause, they do not silently execute. " +
    "Close on the bright line: the agent never decides grades, admissions, discipline, financial aid, special-ed eligibility, or placement. That is the sentence that lets academic leadership say yes.");
}

// =====================================================================
// SLIDE 5 — WHERE IT FALLS SHORT  light
// =====================================================================
async function slideShortfalls() {
  const s = pres.addSlide();
  lightHeader(s, "The honest part", "Where it falls short — open risks today", 5);
  s.addText("Drawn directly from the deployment reference's own “gaps / what you must add” callouts. None are hidden; all are scoped.",
    { x: 0.6, y: 1.35, w: 12.1, h: 0.4, fontFace: "Calibri", fontSize: 13, italic: true, color: SLATE2, margin: 0 });

  const gaps = [
    { sev: "GAP", c: RED, t: "Edge layer not in IaC", d: "No CloudFront / WAF / ACM / Route 53 template. The production public front door is a customer build." },
    { sev: "GAP", c: RED, t: "Observability is thin", d: "No CloudWatch alarm/dashboard template ships. Runbooks assume alarms you must author. CloudTrail is manual." },
    { sev: "PART", c: AMBER, t: "VPC endpoints incomplete", d: "Secrets Manager / KMS / Logs egress via NAT today; single NAT is reference-only. Add endpoints + NAT-per-AZ." },
    { sev: "PART", c: AMBER, t: "AgentCore = placeholders", d: "Gateway & Runtime register via customer-supplied custom-resource Lambdas; blank token writes SSM placeholders only." },
    { sev: "PART", c: AMBER, t: "Connector secrets manual", d: "Secrets Manager entries are created by hand, not IaC. Target specs cover only sis/lms/crm/itsm." },
    { sev: "STUB", c: NAVY, t: "Live connectors are stubs", d: "SIS / LMS / ERP / ITSM run on fixtures; live validation against PowerSchool, Banner, Canvas, ServiceNow is yours." },
    { sev: "BUILD", c: NAVY, t: "Reviewer UI is your build", d: "The HITL gate + queue ship; the screen a reviewer uses to approve/reject is a customer/SI build." },
    { sev: "RISK", c: TEALDK, t: "No cert · cost · accuracy", d: "No SOC 2 / 3rd-party cert. Bedrock model cost & accuracy must be validated. KB ingestion IaC is a stub." },
  ];
  let i = 0; const cw = 5.92, ch = 1.12, gx = 0.28, gy = 0.18, x0 = 0.6, y0 = 1.92;
  for (const g of gaps) {
    const col = i % 2, row = Math.floor(i / 2);
    const cx = x0 + col * (cw + gx), cyy = y0 + row * (ch + gy);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: cyy, w: cw, h: ch, rectRadius: 0.07,
      fill: { color: CARD }, line: { color: LINE, width: 1 }, shadow: softShadow() });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx + 0.18, y: cyy + 0.2, w: 0.78, h: 0.34, rectRadius: 0.05, fill: { color: g.c }, line: { type: "none" } });
    s.addText(g.sev, { x: cx + 0.18, y: cyy + 0.2, w: 0.78, h: 0.34, align: "center", valign: "middle",
      fontFace: "Calibri", fontSize: 9, bold: true, color: WHITE, margin: 0 });
    s.addText(g.t, { x: cx + 1.06, y: cyy + 0.14, w: cw - 1.2, h: 0.34, fontFace: "Cambria", fontSize: 13, bold: true, color: NAVY, margin: 0, valign: "middle" });
    s.addText(g.d, { x: cx + 1.06, y: cyy + 0.47, w: cw - 1.22, h: 0.58, fontFace: "Calibri", fontSize: 9.8, color: SLATE, margin: 0, lineSpacingMultiple: 0.96 });
    i++;
  }
  footer(s);
  s.addNotes(
    "Do not soften this slide. Putting the shortfalls on screen yourself is what makes the rest of the deck credible — a board trusts the executive who names the gaps before they're asked. " +
    "Group the message into three buckets: (1) infrastructure not-yet-in-IaC (edge, alarms, endpoints) — real engineering work, well-understood, estimable; (2) AgentCore + connectors are reference placeholders that your SI wires to your systems; (3) the things only YOU can finish — no cert, cost/accuracy validation, reviewer UI. " +
    "Handling pushback: 'isn't this a lot?' Yes — and it is the same list for ANY governed AI build; the difference is here it is written down and scoped, not discovered mid-project. Every one of these is on the backlog slide with an owner.");
}

// =====================================================================
// SLIDE 6 — QUESTIONS TO ANSWER BEFORE YOU ADOPT  light
// =====================================================================
async function slideQuestions() {
  const s = pres.addSlide();
  lightHeader(s, "Due diligence", "The questions to answer before you adopt", 6);

  const qs = [
    { ic: Fa.FaMapMarkedAlt, h: "Data residency & FERPA terms", b: "Which region? Does it meet state data-localization law? Are the FERPA “school official / direct control” terms in the vendor agreement?" },
    { ic: Fa.FaFileSignature, h: "DPA / BAA in place", b: "Data-processing agreement executed; vendor TPRM questionnaire signed off before any live student record is touched." },
    { ic: Fa.FaIdBadge, h: "IdP federation", b: "Can your IdP (Okta / Entra / Google) express guardian relationships and age-of-majority? Cognito ↔ IdP claim mapping is the most common readiness gap." },
    { ic: Fa.FaUniversalAccess, h: "Accessibility conformance", b: "Who signs the WCAG 2.2 AA VPAT? Plan against the 2026/2027 ADA Title II web & content deadlines." },
    { ic: Fa.FaUserShield, h: "Penetration test", b: "Independent pen test of the deployed surface is a production-readiness gate — budget and schedule it before go-live." },
    { ic: Fa.FaDollarSign, h: "Total cost of ownership", b: "Bedrock inference + infra + SI delivery. Model the run-rate, not just the build; set Budgets + Cost Anomaly Detection on Bedrock." },
    { ic: Fa.FaHeadset, h: "Support & maintenance model", b: "Who owns prompt/model change control, patching, and the managed-service SLA after the SI hands off?" },
    { ic: Fa.FaChartLine, h: "Model-drift monitoring", b: "Who watches grounding-failure rate, Guardrail block rate, and eval regression once it is live, and on what cadence?" },
  ];
  let i = 0; const cw = 5.92, ch = 1.13, gx = 0.28, gy = 0.16, x0 = 0.6, y0 = 1.5;
  for (const q of qs) {
    const col = i % 2, row = Math.floor(i / 2);
    const cx = x0 + col * (cw + gx), cyy = y0 + row * (ch + gy);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: cyy, w: cw, h: ch, rectRadius: 0.07,
      fill: { color: CARD }, line: { color: LINE, width: 1 }, shadow: softShadow() });
    await iconCircle(s, q.ic, cx + 0.2, cyy + 0.26, 0.6, TEAL, WHITE);
    s.addText(q.h, { x: cx + 0.95, y: cyy + 0.13, w: cw - 1.1, h: 0.36, fontFace: "Cambria", fontSize: 12.5, bold: true, color: NAVY, margin: 0, valign: "middle" });
    s.addText(q.b, { x: cx + 0.95, y: cyy + 0.47, w: cw - 1.12, h: 0.6, fontFace: "Calibri", fontSize: 9.7, color: SLATE, margin: 0, lineSpacingMultiple: 0.95 });
    i++;
  }
  footer(s);
  s.addNotes(
    "These are the eight questions a diligent board should make you answer before signing. Present them as YOUR checklist, not the vendor's — it signals you are driving the evaluation. " +
    "The two highest-friction items in practice: IdP federation (most institutions' directories don't natively express guardian relationships or age-of-majority, which FERPA rights-transfer depends on) and accessibility conformance against the looming ADA Title II deadlines. " +
    "If a board member asks 'what's the one thing most likely to slow us down?' — it's IdP claim mapping. Flag it now so it isn't a surprise in month two. Cost: stress that you must model the Bedrock run-rate, not just the build cost.");
}

// =====================================================================
// MATRIX HELPERS
// =====================================================================
function ownerCell(owner) {
  const map = { U: { c: OWN_USER, l: "User" }, C: { c: OWN_CUST, l: "Customer" }, D: { c: OWN_DEV, l: "Dev / SI" } };
  return map[owner];
}

function matrixSlide(num, partLabel, title, rows) {
  const s = pres.addSlide();
  lightHeader(s, "Responsibility matrix  ·  " + partLabel, title, num);

  // R/A key sits up by the page number, clear of the legend row
  s.addText("R/A = Responsible / Accountable   ·   C/I = Consulted / Informed",
    { x: 6.6, y: 0.4, w: 5.4, h: 0.3, fontFace: "Calibri", fontSize: 9, italic: true, color: SLATE2, align: "right", margin: 0, valign: "middle" });
  const leg = [
    { col: OWN_DEV, t: "Developer / SI — deploys & maintains", w: 3.05 },
    { col: OWN_CUST, t: "Customer — institution IT / security / leadership", w: 3.65 },
    { col: OWN_USER, t: "User — staff operating the agents", w: 2.9 },
  ];
  let lx = 0.6;
  for (const l of leg) {
    s.addShape(pres.shapes.OVAL, { x: lx, y: 1.36, w: 0.2, h: 0.2, fill: { color: l.col }, line: { type: "none" } });
    s.addText(l.t, { x: lx + 0.26, y: 1.28, w: l.w, h: 0.34, fontFace: "Calibri", fontSize: 9.5, color: SLATE, margin: 0, valign: "middle" });
    lx += l.w + 0.35;
  }

  const hdr = [
    { text: "Responsibility domain", options: { fill: { color: NAVY }, color: WHITE, bold: true, align: "left", fontSize: 11, valign: "middle" } },
    { text: "User", options: { fill: { color: OWN_USER }, color: WHITE, bold: true, align: "center", fontSize: 11, valign: "middle" } },
    { text: "Customer (institution)", options: { fill: { color: OWN_CUST }, color: WHITE, bold: true, align: "center", fontSize: 11, valign: "middle" } },
    { text: "Developer / SI", options: { fill: { color: OWN_DEV }, color: WHITE, bold: true, align: "center", fontSize: 11, valign: "middle" } },
  ];
  const body = rows.map((r, idx) => {
    const zebra = idx % 2 === 0 ? CARD : CARDTINT;
    function cell(spec) {
      const owner = spec.who ? ownerCell(spec.who) : null;
      const isRA = spec.r === "R/A";
      return {
        text: spec.r,
        options: {
          fill: { color: isRA && owner ? owner.c : zebra },
          color: isRA && owner ? WHITE : SLATE2,
          bold: isRA, align: "center", fontSize: 10.5, valign: "middle",
        },
      };
    }
    return [
      { text: r.d, options: { fill: { color: zebra }, color: NAVY, bold: true, align: "left", fontSize: 10, valign: "middle" } },
      cell(r.u),
      cell(r.c),
      cell(r.dev),
    ];
  });

  s.addTable([hdr, ...body], {
    x: 0.6, y: 1.74, w: 12.13, colW: [4.93, 2.0, 3.2, 2.0],
    border: { type: "solid", pt: 0.5, color: "FFFFFF" },
    rowH: 0.3, valign: "middle", fontFace: "Calibri", margin: [3, 4, 3, 4],
    autoPage: false,
  });
  footer(s);
  return s;
}

function iconCircleSync(slide, Comp, cx, cy, d, circleColor, iconColor) {
  slide.addShape(pres.shapes.OVAL, { x: cx, y: cy, w: d, h: d, fill: { color: circleColor }, line: { type: "none" } });
  const ip = d * 0.26;
  const key = Comp.name + iconColor + 256;
  slide.addImage({ data: iconCache[key], x: cx + ip, y: cy + ip, w: d - 2 * ip, h: d - 2 * ip });
}

function matrixNoteCards(s, notes, circleColor) {
  let x = 0.6; const cw = 3.92, gx = 0.18, cy = 4.18, ch = 2.55;
  for (const n of notes) {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: cy, w: cw, h: ch, rectRadius: 0.08, fill: { color: CARD }, line: { color: LINE, width: 1 }, shadow: softShadow() });
    iconCircleSync(s, n.ic, x + 0.24, cy + 0.24, 0.6, circleColor, WHITE);
    s.addText(n.h, { x: x + 0.96, y: cy + 0.26, w: cw - 1.1, h: 0.55, fontFace: "Cambria", fontSize: 13.5, bold: true, color: NAVY, valign: "middle", margin: 0 });
    s.addText(n.b, { x: x + 0.26, y: cy + 0.92, w: cw - 0.5, h: ch - 1.1, fontFace: "Calibri", fontSize: n.fs || 9.8, color: SLATE, margin: 0, lineSpacingMultiple: 1.0 });
    x += cw + gx;
  }
}

function slideMatrixA() {
  const rows = [
    { d: "Platform & infrastructure — accounts, network, KMS, edge",
      u: { r: "—" }, c: { r: "C/I", who: "C" }, dev: { r: "R/A", who: "D" } },
    { d: "Identity & access — IdP, Cognito federation, IAM roles",
      u: { r: "—" }, c: { r: "R/A", who: "C" }, dev: { r: "C/I", who: "D" } },
    { d: "Security & compliance — FERPA/COPPA program, audits, pen test",
      u: { r: "C/I", who: "U" }, c: { r: "R/A", who: "C" }, dev: { r: "C/I", who: "D" } },
    { d: "Connectors & data — SIS/LMS/ERP integration, data quality, KB content",
      u: { r: "—" }, c: { r: "R/A", who: "C" }, dev: { r: "R/A", who: "D" } },
  ];
  const s = matrixSlide(7, "Part 1 of 3", "Who owns what — platform, identity, security, data", rows);
  s.addText("Where two parties show R/A, the control only holds if both act — e.g. the SI builds the connector; the institution provides credentials, approves scopes, and validates against the live system.",
    { x: 0.6, y: 3.62, w: 12.13, h: 0.5, fontFace: "Calibri", fontSize: 10.5, italic: true, color: SLATE2, margin: 0 });
  matrixNoteCards(s, [
    { ic: Fa.FaServer, h: "Platform & infra", b: "SI designs & deploys the VPC, KMS, and data plane per the templates; your cloud team approves network & key policy and owns the CMK. The edge layer is an SI build (not in IaC yet)." },
    { ic: Fa.FaIdBadge, h: "Identity & access", b: "The IdP is yours — role definitions, guardian relationships, and age-of-majority are institution policy. The SI implements the Cognito claim mapping; you own its accuracy." },
    { ic: Fa.FaDatabase, h: "Connectors & data", b: "No connector points at a live system without your scope approval and a signed pilot SOW. Stale or wrong KB content is an institution risk; the SI implements change control." },
  ], NAVY);
  s.addNotes(
    "This is the centerpiece — walk it slowly, it is what leadership remembers. Three owners across the top: User (the staff operating the agents), Customer (your institution's IT/security/data/leadership), and Developer/SI (whoever deploys and maintains). " +
    "Colour encodes the owner: teal = SI, navy = institution, slate = user. A filled cell means Responsible/Accountable; a pale cell means Consulted/Informed. " +
    "Part 1 covers platform, identity, security, and data. The two rows to dwell on: Identity & access is institution-owned (your IdP, your role policy) — this surprises people who assume the vendor handles it. And Connectors & data is shared R/A — both must act. " +
    "The takeaway for the board: every 'Customer R/A' cell is an accountability you cannot delegate to the SI. That is the readiness checklist.");
  return s;
}

function slideMatrixB() {
  const rows = [
    { d: "Model & guardrails — Bedrock access, Guardrails tuning, eval & change-control",
      u: { r: "—" }, c: { r: "R/A", who: "C" }, dev: { r: "R/A", who: "D" } },
    { d: "Accessibility — WCAG 2.2 AA conformance testing & sign-off",
      u: { r: "—" }, c: { r: "R/A", who: "C" }, dev: { r: "R/A", who: "D" } },
    { d: "HITL operations — approving consequential actions, reviewer roster",
      u: { r: "R/A", who: "U" }, c: { r: "R/A", who: "C" }, dev: { r: "C/I", who: "D" } },
    { d: "Reviewer UI / HITL handoff surface — build & operate",
      u: { r: "—" }, c: { r: "C/I", who: "C" }, dev: { r: "R/A", who: "D" } },
  ];
  const s = matrixSlide(8, "Part 2 of 3", "Who owns what — model, accessibility, human-in-the-loop", rows);
  s.addText("The human gate is the bright line. The SI builds it; the institution staffs it with qualified, correctly-roled reviewers — this cannot be fully delegated to the SI.",
    { x: 0.6, y: 3.62, w: 12.13, h: 0.5, fontFace: "Calibri", fontSize: 10.5, italic: true, color: SLATE2, margin: 0 });
  matrixNoteCards(s, [
    { ic: Fa.FaSlidersH, h: "Model & guardrails", fs: 9.4, b: "The SI recommends & implements per-agent Guardrail policy, prompt pinning, and the eval harness; your legal & student-services leadership approves it — especially under-13 / COPPA settings — and a named reviewer signs off promotions." },
    { ic: Fa.FaUniversalAccess, h: "Accessibility", b: "WCAG 2.2 AA is a production-readiness gate, not optional. The SI tests and remediates during pilot; you designate the accessibility coordinator and give final VPAT acceptance." },
    { ic: Fa.FaUserCheck, h: "HITL operations", b: "Consequential actions are approved by your named, correctly-roled reviewers (educator / counselor / registrar). The SI runs the technical gate and queue ops; you define what counts as “consequential.”" },
  ], TEAL);
  s.addNotes(
    "Part 2 is where the institution's accountability is heaviest — model governance, accessibility, and the human-in-the-loop gate. " +
    "HITL operations is the one row where the User column lights up R/A: the staff who actually approve consequential actions are accountable for those approvals. The institution designates and rosters them; the SI cannot do this for you. " +
    "Accessibility: stress the WCAG 2.2 AA gate and that final VPAT acceptance is yours. Model & guardrails: your legal and student-services leadership must approve Guardrail policy, especially for K-12 / under-13 populations. " +
    "If asked 'can't the SI just own all of this?' — no. FERPA accountability, what counts as consequential, and reviewer staffing are institution responsibilities by law and by design.");
  return s;
}

function slideMatrixC() {
  const rows = [
    { d: "Support & monitoring — alarms, dashboards, run-rate ops",
      u: { r: "—" }, c: { r: "C/I", who: "C" }, dev: { r: "R/A", who: "D" } },
    { d: "Incident response — detection, containment, breach notification",
      u: { r: "—" }, c: { r: "R/A", who: "C" }, dev: { r: "R/A", who: "D" } },
    { d: "Change management — prompt / model upgrades, production promotion",
      u: { r: "C/I", who: "U" }, c: { r: "R/A", who: "C" }, dev: { r: "R/A", who: "D" } },
    { d: "Training & acceptable-use — staff enablement, AUP, the bright line",
      u: { r: "R/A", who: "U" }, c: { r: "R/A", who: "C" }, dev: { r: "C/I", who: "D" } },
  ];
  const s = matrixSlide(9, "Part 3 of 3", "Who owns what — operations, change, training", rows);
  s.addText("Operationally: the SI builds and runs the technical controls; the institution makes every legal determination — breach notification, production sign-off, and acceptable-use enforcement.",
    { x: 0.6, y: 3.62, w: 12.13, h: 0.5, fontFace: "Calibri", fontSize: 10.5, italic: true, color: SLATE2, margin: 0 });
  matrixNoteCards(s, [
    { ic: Fa.FaBell, h: "Support & monitoring", b: "Alarm thresholds, pager routing, and retention windows are customer-owned; the SI builds the dashboards and runs managed-service operations. Note: the alarm template is a gap you must author." },
    { ic: Fa.FaExclamationTriangle, h: "Incident response", fs: 9.4, b: "The SI executes the runbook, produces audit evidence, and notifies you within 48h of confirmed discovery; you make the legal breach-notification determination to students, parents, and regulators." },
    { ic: Fa.FaChalkboardTeacher, h: "Change & training", b: "No prompt, model, or tool-grant change reaches production without your sign-off. You own the AUP and train staff on what the agent does and does not decide; the SI supplies capability docs." },
  ], AMBER);
  s.addNotes(
    "Part 3 closes the matrix on day-to-day operations, change, and people. The throughline of all three matrix slides: the SI builds and operates the technical controls; the institution makes every legal determination and owns the compliance program. " +
    "Incident response is the row to emphasize for the board: the SI contains and produces evidence and notifies you fast, but the breach-notification decision — the one with legal exposure — is yours. " +
    "Change management: nothing reaches production without your sign-off, which is exactly the control a CISO wants. Training & AUP is User + Customer R/A: your people must understand the bright line, because the agent's safety depends on humans owning consequential decisions. " +
    "After this slide, the board should be able to answer 'who is responsible for what' without ambiguity.");
  return s;
}

// =====================================================================
// SLIDE 10 — WHAT'S STILL TO BE DONE (backlog)  light
// =====================================================================
async function slideBacklog() {
  const s = pres.addSlide();
  lightHeader(s, "The honest backlog", "What is still to be done", 10);

  const items = [
    { ic: Fa.FaNetworkWired, h: "Edge + observability IaC", b: "CloudFront / WAF / ACM / Route 53 and CloudWatch alarms + dashboards authored as templates." },
    { ic: Fa.FaPlug, h: "Live connectors", b: "Validated adapters for live SIS / LMS / ERP / ITSM (PowerSchool, Banner, Canvas, ServiceNow)." },
    { ic: Fa.FaDatabase, h: "KB ingestion pipeline", b: "Bedrock Knowledge Base ingestion IaC built out from the current stub, with grounding wired in." },
    { ic: Fa.FaUniversalAccess, h: "axe-core in CI", b: "Automated accessibility checks in the pipeline plus a full WCAG 2.2 AA conformance pass." },
    { ic: Fa.FaFileContract, h: "Cedar / OPA policy export", b: "Export the gateway authorization model to a standard policy engine for external review & reuse." },
    { ic: Fa.FaUserShield, h: "Penetration test", b: "Independent pen test of the deployed surface — a production-readiness gate." },
    { ic: Fa.FaDesktop, h: "Reviewer UI", b: "The HITL approve/reject surface that authenticates the reviewer and binds identity into the record." },
    { ic: Fa.FaClipboardCheck, h: "Production-readiness review", b: "Full security & privacy review, IdP integration tested, and customer acceptance sign-off." },
  ];
  let i = 0; const cw = 5.92, ch = 1.13, gx = 0.28, gy = 0.16, x0 = 0.6, y0 = 1.5;
  for (const it of items) {
    const col = i % 2, row = Math.floor(i / 2);
    const cx = x0 + col * (cw + gx), cyy = y0 + row * (ch + gy);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: cyy, w: cw, h: ch, rectRadius: 0.07, fill: { color: CARD }, line: { color: LINE, width: 1 }, shadow: softShadow() });
    await iconCircle(s, it.ic, cx + 0.2, cyy + 0.26, 0.6, NAVY, WHITE);
    s.addText(it.h, { x: cx + 0.95, y: cyy + 0.13, w: cw - 1.1, h: 0.36, fontFace: "Cambria", fontSize: 12.5, bold: true, color: NAVY, margin: 0, valign: "middle" });
    s.addText(it.b, { x: cx + 0.95, y: cyy + 0.47, w: cw - 1.12, h: 0.6, fontFace: "Calibri", fontSize: 9.7, color: SLATE, margin: 0, lineSpacingMultiple: 0.95 });
    i++;
  }
  footer(s);
  s.addNotes(
    "This is the shortfalls slide turned into a plan — same items, now with an owner and a place in the sequence. It answers the board's natural next question: 'fine, but what does finishing it actually take?' " +
    "Roughly three streams: infrastructure-as-code (edge, observability, KB ingestion) is well-understood SI work; integration (live connectors, reviewer UI) is the bulk of the engagement and is gated on your systems and validation; and assurance (axe-core, conformance, pen test, production-readiness review) converts 'Deployable' to 'Production-ready.' " +
    "Cedar/OPA export is the credibility extra — it lets your own security team review the authorization model in a standard policy language. Use this slide to make the engagement feel finite and estimable, not open-ended.");
}

// =====================================================================
// SLIDE 11 — RECOMMENDED ADOPTION PATH (phased)  light
// =====================================================================
async function slidePath() {
  const s = pres.addSlide();
  lightHeader(s, "Recommended adoption path", "Land low-risk, prove the controls, then expand", 11);

  const phases = [
    { n: "1", col: TEAL, t: "Pilot — land here", sub: "Lowest decision-risk, highest visibility",
      agents: "01 Concierge · 03 Educator Copilot · 07 Document & Accessibility · 08 Service Desk",
      goal: "Prove the gateway, audit trail, and HITL gate in production on real users. Measure deflection & cycle-time." },
    { n: "2", col: NAVY, t: "Expand — on evidence", sub: "Higher-value, higher-governance",
      agents: "04 Assessment · 05 Student Success · 06 Pathway Navigator",
      goal: "Add agents that touch learning & outcomes — only after stronger eval, bias testing, and evidence retention are proven." },
    { n: "3", col: AMBER, t: "Operate — at scale", sub: "Managed service & continuous assurance",
      agents: "Full suite under change control · model-drift monitoring · annual pen test",
      goal: "Steady-state operations with named reviewers, alarms, and a production-readiness review behind each promotion." },
  ];
  let x = 0.6; const cw = 3.93, gx = 0.18, cy = 1.6, ch = 3.55;
  for (let i = 0; i < phases.length; i++) {
    const p = phases[i];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: cy, w: cw, h: ch, rectRadius: 0.1, fill: { color: CARD }, line: { color: p.col, width: 1.5 }, shadow: softShadow() });
    s.addShape(pres.shapes.OVAL, { x: x + 0.3, y: cy + 0.3, w: 0.78, h: 0.78, fill: { color: p.col }, line: { type: "none" } });
    s.addText(p.n, { x: x + 0.3, y: cy + 0.3, w: 0.78, h: 0.78, align: "center", valign: "middle", fontFace: "Cambria", fontSize: 30, bold: true, color: WHITE, margin: 0 });
    s.addText(p.t, { x: x + 1.22, y: cy + 0.33, w: cw - 1.4, h: 0.4, fontFace: "Cambria", fontSize: 16.5, bold: true, color: NAVY, margin: 0 });
    s.addText(p.sub, { x: x + 1.22, y: cy + 0.72, w: cw - 1.4, h: 0.36, fontFace: "Calibri", fontSize: 10.5, italic: true, color: p.col, margin: 0 });
    s.addText("AGENTS", { x: x + 0.3, y: cy + 1.32, w: cw - 0.6, h: 0.24, fontFace: "Calibri", fontSize: 8.5, bold: true, color: SLATE2, charSpacing: 1.5, margin: 0 });
    s.addText(p.agents, { x: x + 0.3, y: cy + 1.56, w: cw - 0.6, h: 0.85, fontFace: "Calibri", fontSize: 11, bold: true, color: NAVY, margin: 0, lineSpacingMultiple: 1.0 });
    s.addText("GOAL / PHASE GATE", { x: x + 0.3, y: cy + 2.4, w: cw - 0.6, h: 0.24, fontFace: "Calibri", fontSize: 8.5, bold: true, color: SLATE2, charSpacing: 1.5, margin: 0 });
    s.addText(p.goal, { x: x + 0.3, y: cy + 2.64, w: cw - 0.6, h: 0.85, fontFace: "Calibri", fontSize: 10, color: SLATE, margin: 0, lineSpacingMultiple: 1.0 });
    if (i < phases.length - 1) {
      s.addShape(pres.shapes.RIGHT_TRIANGLE, { x: x + cw + 0.005, y: cy + ch / 2 - 0.16, w: 0.17, h: 0.32, fill: { color: SLATE2 }, line: { type: "none" }, rotate: 90 });
    }
    x += cw + gx;
  }

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.6, y: 5.42, w: 12.13, h: 1.32, rectRadius: 0.08, fill: { color: NAVY }, line: { type: "none" } });
  await iconCircle(s, Fa.FaFlagCheckered, 0.82, 5.66, 0.84, TEAL, WHITE);
  s.addText([
    { text: "Phase gates:  ", options: { bold: true, color: TEALLT, fontSize: 13 } },
    { text: "Each phase advances only when the prior one clears its gate — clean audit trail, HITL gate exercised on real approvals, measured deflection/cycle-time, and a security sign-off. Single best entry point: Agent 01 (Concierge) — most visible, lowest-risk, easiest to measure.",
      options: { color: WHITE, fontSize: 12 } },
  ], { x: 1.82, y: 5.56, w: 10.75, h: 1.05, fontFace: "Calibri", valign: "middle", margin: 0, lineSpacingMultiple: 1.0 });
  footer(s);
  s.addNotes(
    "The adoption path de-risks the decision: you are not asking the board to bet the institution on eight agents at once. You land with the four lowest-decision-risk, highest-visibility agents — Concierge, Educator Copilot, Document & Accessibility, Service Desk — and prove the gateway, audit, and HITL gate on real users. " +
    "Only after Phase 1 clears its gate do you add the higher-governance agents (Assessment, Student Success, Pathway Navigator) that touch learning outcomes directly. " +
    "The single best first deployment is Agent 01, the Concierge: most visible to the most users, lowest risk, easiest to measure. " +
    "Stress the phase gates: advancement is earned with evidence, not scheduled by date. That is the discipline that protects the institution and gives the board a clean off-ramp at each stage.");
}

// =====================================================================
// SLIDE 12 — DECISION SUMMARY (dark)
// =====================================================================
async function slideDecision() {
  const s = pres.addSlide();
  s.background = { color: NAVYDK };
  s.addShape(pres.shapes.OVAL, { x: 11.0, y: -1.2, w: 4.0, h: 4.0, fill: { color: NAVY2 }, line: { type: "none" } });
  s.addText("DECISION SUMMARY", { x: 0.7, y: 0.5, w: 10, h: 0.4, fontFace: "Calibri", fontSize: 13, bold: true, color: TEAL, charSpacing: 2, margin: 0 });
  s.addText("Go / no-go criteria", { x: 0.7, y: 0.86, w: 12, h: 0.7, fontFace: "Cambria", fontSize: 29, bold: true, color: WHITE, margin: 0 });

  const gx = 0.7, gw = 5.85, gy = 1.85, gh = 3.5;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: gx, y: gy, w: gw, h: gh, rectRadius: 0.1, fill: { color: NAVY2 }, line: { color: GREEN, width: 1.5 }, shadow: shadow() });
  await iconCircle(s, Fa.FaCheckCircle, gx + 0.28, gy + 0.28, 0.66, GREEN, WHITE);
  s.addText("GO if you can commit to…", { x: gx + 1.06, y: gy + 0.32, w: gw - 1.2, h: 0.58, fontFace: "Cambria", fontSize: 17, bold: true, color: WHITE, valign: "middle", margin: 0 });
  s.addText([
    { text: "A funded SI-led engagement, not a product purchase", options: { bullet: true, breakLine: true } },
    { text: "Owning the FERPA/COPPA program, IdP, and reviewer roster", options: { bullet: true, breakLine: true } },
    { text: "A pilot scoped to Agents 01 / 03 / 07 / 08 with phase gates", options: { bullet: true, breakLine: true } },
    { text: "Budget for accessibility conformance + a pen test before go-live", options: { bullet: true, breakLine: true } },
    { text: "Validating Bedrock cost & accuracy against your own data", options: { bullet: true } },
  ], { x: gx + 0.32, y: gy + 1.12, w: gw - 0.6, h: gh - 1.3, fontFace: "Calibri", fontSize: 12, color: ICE, margin: 0, paraSpaceAfter: 7, lineSpacingMultiple: 1.0 });

  const nx = 6.88, nw = 5.85;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: nx, y: gy, w: nw, h: gh, rectRadius: 0.1, fill: { color: NAVY2 }, line: { color: RED, width: 1.5 }, shadow: shadow() });
  await iconCircle(s, Fa.FaTimesCircle, nx + 0.28, gy + 0.28, 0.66, RED, WHITE);
  s.addText("NO-GO / wait if…", { x: nx + 1.06, y: gy + 0.32, w: nw - 1.2, h: 0.58, fontFace: "Cambria", fontSize: 17, bold: true, color: WHITE, valign: "middle", margin: 0 });
  s.addText([
    { text: "You need a certified, turnkey product to switch on now", options: { bullet: true, breakLine: true } },
    { text: "There is no budget or partner for SI delivery & maintenance", options: { bullet: true, breakLine: true } },
    { text: "Your IdP cannot express guardian / age-of-majority and there is no plan to fix it", options: { bullet: true, breakLine: true } },
    { text: "You expect the vendor to assume FERPA accountability", options: { bullet: true, breakLine: true } },
    { text: "You cannot staff qualified HITL reviewers", options: { bullet: true } },
  ], { x: nx + 0.32, y: gy + 1.12, w: nw - 0.6, h: gh - 1.3, fontFace: "Calibri", fontSize: 12, color: ICE, margin: 0, paraSpaceAfter: 7, lineSpacingMultiple: 1.0 });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.7, y: 5.62, w: 12.03, h: 1.28, rectRadius: 0.08, fill: { color: TEAL }, line: { type: "none" } });
  s.addText([
    { text: "Recommendation:  ", options: { bold: true, color: NAVYDK, fontSize: 15 } },
    { text: "Approve a funded Phase-1 pilot on Agents 01 / 03 / 07 / 08. It compresses an SI-led build with a governance spine your CISO and privacy officer can stand behind — while you keep FERPA accountability and prove the controls in production before expanding.",
      options: { color: NAVYDK, fontSize: 13 } },
  ], { x: 1.05, y: 5.72, w: 11.3, h: 1.06, fontFace: "Calibri", valign: "middle", margin: 0, lineSpacingMultiple: 1.0 });
  s.addNotes(
    "Close decisively. Two columns — Go and No-Go — so the board sees this is a conditional yes with clear criteria, not a hand-wave. " +
    "GO if leadership can commit to: a funded SI engagement, owning the compliance program/IdP/reviewers, a phased pilot, budget for conformance + pen test, and validating Bedrock cost/accuracy. NO-GO or wait if any of the disqualifiers hold — especially expecting a turnkey product or expecting the vendor to take FERPA accountability. " +
    "Then deliver the one-line recommendation verbatim and ask for the specific decision: approval to fund a Phase-1 pilot on Agents 01/03/07/08. " +
    "If the board hesitates, the smallest viable yes is a single-agent (01 Concierge) pilot — keep that in your pocket as the fallback ask.");
}

// =====================================================================
async function main() {
  const warm = [
    [Fa.FaServer, "FFFFFF"], [Fa.FaIdBadge, "FFFFFF"], [Fa.FaDatabase, "FFFFFF"],
    [Fa.FaSlidersH, "FFFFFF"], [Fa.FaUniversalAccess, "FFFFFF"], [Fa.FaUserCheck, "FFFFFF"],
    [Fa.FaBell, "FFFFFF"], [Fa.FaExclamationTriangle, "FFFFFF"], [Fa.FaChalkboardTeacher, "FFFFFF"],
  ];
  for (const [c, col] of warm) await icon(c, col);

  await slideTitle();
  await slideBLUF();
  await slideMaturity();
  await slideWhyYes();
  await slideShortfalls();
  await slideQuestions();
  slideMatrixA();
  slideMatrixB();
  slideMatrixC();
  await slideBacklog();
  await slidePath();
  await slideDecision();

  await pres.writeFile({ fileName: process.argv[2] || "EDU-CIO-Adoption-Review.pptx" });
  console.log("WROTE deck");
}

main().catch((e) => { console.error(e); process.exit(1); });
