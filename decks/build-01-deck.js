/* EDU AI Agent Suite — Agent 01 GTM deck (customer-ready, standalone generator)
 * Student & Family Services Concierge — "The 24/7 governed front door to the institution"
 *
 * ~9-slide narrative: issue -> what students expect -> how colleges try (and fall short)
 * -> cost -> how we solve it -> architecture -> PROVEN DEPLOYABLE -> ROI / pilot offer.
 *
 * Design system: Squid-Ink navy dark slides, AWS-orange accents + left-edge bar on every
 * slide, teal solution cards, red HITL gate, AWS category colors on the architecture.
 *
 * Run:  NODE_PATH=/path/to/node_modules node decks/build-01-deck.js
 */
const pptxgen = require("pptxgenjs");

// ============================================================ PALETTE / FONTS
const SQUID   = "232F3E"; // deep navy — dark slide bg, titles
const SQUID2  = "2E3B4E"; // lighter navy (cards on dark)
const SQUID3  = "1B2530"; // deeper navy for takeaway bars
const ORANGE  = "FF9900"; // amber — accents, edge bar, stat numbers
const ORANGED = "E88A00"; // darker orange (labels on light)
const TEAL    = "16A085"; // solution / positive
const TEALLT  = "1ABC9C"; // brighter teal on dark
const RED     = "C0392B"; // HUMAN-GATE only
const REDLT   = "E74C3C"; // deny on dark
const GRAYBG  = "F2F3F4"; // light content background
const CARD    = "FFFFFF";
const WHITE   = "FFFFFF";
const INK     = "232F3E"; // body on light
const MUTED   = "6B7785"; // muted gray on light
const MUTEDLT = "9AA7B4"; // muted on dark
const LINE    = "D5DBE1";
// AWS architecture category colors
const C_COMPUTE = "FF9900"; // compute orange
const C_INTEG   = "E7157B"; // integration magenta
const C_STORAGE = "7AA116"; // storage olive/green
const C_MODEL   = "16A085"; // model/db teal
const C_NET     = "8C4FFF"; // networking purple

const F_BOLD = "Arial";
const F_REG  = "Calibri";
const F_TAG  = "Cambria";

const EDGE = 0.14;               // orange left-edge bar width (in)
const PW = 13.333, PH = 7.5;
const FOOT = "EDU AI Agent Suite  ·  Student & Family Concierge  ·  Built on AWS";

const sh   = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 90, opacity: 0.16 });
const shsm = () => ({ type: "outer", color: "000000", blur: 5, offset: 2, angle: 90, opacity: 0.10 });

// ------------------------------------------------------------ primitives
function edgeBar(P, s) {
  s.addShape(P.shapes.RECTANGLE, { x: 0, y: 0, w: EDGE, h: PH, fill: { color: ORANGE }, line: { type: "none" } });
}
function footer(P, s, onDark) {
  s.addText(FOOT, {
    x: 0.55, y: PH - 0.4, w: PW - 1.1, h: 0.3, fontFace: F_REG, fontSize: 9,
    color: onDark ? MUTEDLT : MUTED, align: "left", valign: "middle", margin: 0,
  });
}
function tag(P, s, x, y, w, txt, onDark) {
  if (!txt) return;
  s.addText(txt, {
    x, y, w, h: 0.22, fontFace: F_REG, fontSize: 7.5, italic: true,
    color: onDark ? MUTEDLT : MUTED, align: "left", valign: "middle", margin: 0,
  });
}

// ============================================================ SLIDE 1 — TITLE
function slideTitle(P) {
  const s = P.addSlide();
  s.background = { color: SQUID };
  edgeBar(P, s);
  s.addText("Student & Family Services Concierge", {
    x: 0.85, y: 1.55, w: 11.8, h: 1.9, fontFace: F_BOLD, fontSize: 44, bold: true,
    color: WHITE, align: "left", valign: "middle", lineSpacingMultiple: 1.0, margin: 0 });
  s.addText("The 24/7 governed front door to the institution", {
    x: 0.87, y: 3.55, w: 11.6, h: 0.6, fontFace: F_BOLD, fontSize: 22, bold: true,
    color: ORANGE, align: "left", valign: "middle", margin: 0 });
  s.addText("Agent 01 of 8  ·  answers routine questions instantly, in any language — while staff own every account action", {
    x: 0.88, y: 4.35, w: 11.4, h: 0.5, fontFace: F_TAG, fontSize: 15, italic: true,
    color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
  s.addText("EDU AI Agent Suite", {
    x: 0.88, y: 5.55, w: 11.4, h: 0.35, fontFace: F_BOLD, fontSize: 14, bold: true,
    color: WHITE, align: "left", valign: "middle", margin: 0 });
  s.addText(FOOT + "  ·  July 2026", {
    x: 0.88, y: 5.9, w: 11.4, h: 0.3, fontFace: F_REG, fontSize: 11,
    color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
  s.addText("Reference accelerator — not an AWS service, not AWS-supported software, not a compliance certification, and not production-ready for regulated data without customer-specific engineering, testing, authorization, and operational ownership.", {
    x: 0.88, y: 6.75, w: 11.6, h: 0.55, fontFace: F_REG, fontSize: 8.5, italic: true,
    color: "6B788A", align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });
  s.addNotes(NOTES.s1);
}

// ============================================================ SLIDE 2 — THE ISSUE (hero stat)
function slideIssue(P) {
  const s = P.addSlide();
  s.background = { color: SQUID };
  edgeBar(P, s);
  s.addText("Families can't self-serve — and the phones can't keep up", {
    x: 0.85, y: 0.7, w: 11.9, h: 1.0, fontFace: F_BOLD, fontSize: 33, bold: true,
    color: WHITE, align: "left", valign: "middle", lineSpacingMultiple: 1.0, margin: 0 });
  s.addText("Routine status, aid, and deadline questions bury front-office staff — and seasonal peaks make it worse.", {
    x: 0.87, y: 1.68, w: 11.6, h: 0.5, fontFace: F_TAG, fontSize: 15, italic: true,
    color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
  // hero stat band
  s.addShape(P.shapes.RECTANGLE, { x: 0.85, y: 2.35, w: 11.78, h: 1.35, fill: { color: SQUID3 }, line: { color: "3A485A", width: 1 } });
  s.addText([
    { text: "~4M of 5.4M calls", options: { bold: true, color: ORANGE, fontSize: 40 } },
    { text: "   went unanswered", options: { bold: true, color: WHITE, fontSize: 24 } },
  ], { x: 1.2, y: 2.5, w: 8.2, h: 1.05, fontFace: F_BOLD, align: "left", valign: "middle", margin: 0 });
  s.addText([
    { text: "≈ 3 of every 4 calls", options: { bold: true, color: WHITE, fontSize: 15, breakLine: true } },
    { text: "to the federal aid line, 2024-25 FAFSA cycle", options: { color: MUTEDLT, fontSize: 11 } },
  ], { x: 9.35, y: 2.5, w: 3.05, h: 1.05, fontFace: F_REG, align: "left", valign: "middle", lineSpacingMultiple: 1.0, margin: 0 });
  s.addText("[gov — U.S. GAO, GAO-24-107407, 2024]", { x: 1.2, y: 3.42, w: 6, h: 0.22, fontFace: F_REG, fontSize: 8, italic: true, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });

  // three stat cards
  const cards = [
    { big: "24/7 + multilingual", sz: 21, label: "demand fixed staff and business hours simply can't cover", tag: "[design]" },
    { big: "Seasonal peaks", sz: 24, label: "FAFSA, registration, and move-in spike contact volume unpredictably", tag: "[design]" },
    { big: "Complex casework", sz: 22, label: "waits while advisors answer routine, repetitive questions", tag: "[design]" },
  ];
  const cw = 3.78, gap = 0.22, x0 = 0.85, cy = 4.0, ch = 2.35;
  cards.forEach((st, i) => {
    const x = x0 + i * (cw + gap);
    s.addShape(P.shapes.RECTANGLE, { x, y: cy, w: cw, h: ch, fill: { color: SQUID2 }, line: { color: "3A485A", width: 1 } });
    s.addText(st.big, { x: x + 0.28, y: cy + 0.28, w: cw - 0.52, h: 0.85, fontFace: F_BOLD, fontSize: st.sz, bold: true, color: ORANGE, align: "left", valign: "top", lineSpacingMultiple: 0.95, margin: 0 });
    s.addText(st.label, { x: x + 0.3, y: cy + 1.2, w: cw - 0.56, h: 0.85, fontFace: F_REG, fontSize: 12.5, color: "C9D2DC", align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });
    tag(P, s, x + 0.3, cy + ch - 0.28, cw - 0.5, st.tag, true);
  });
  footer(P, s, true);
  s.addNotes(NOTES.s2);
}

// ============================================================ SLIDE 3 — WHAT STUDENTS EXPECT (the expectation gap)
function slideExpect(P) {
  const s = P.addSlide();
  s.background = { color: GRAYBG };
  edgeBar(P, s);
  s.addText("What students & families now expect", {
    x: 0.78, y: 0.4, w: 12, h: 0.7, fontFace: F_BOLD, fontSize: 32, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
  s.addText("Gen-Z grew up on consumer apps. They expect an answer in seconds — on their phone, in their language, any hour — and they lose trust and walk when they can't get one.", {
    x: 0.8, y: 1.12, w: 11.9, h: 0.65, fontFace: F_TAG, fontSize: 14, italic: true, color: MUTED, align: "left", valign: "top", lineSpacingMultiple: 1.03, margin: 0 });

  const stats = [
    { big: "86%", label: "of students expect 24/7 support from an AI assistant", tag: "[research — survey, 2024]" },
    { big: "72%", label: "study on a smartphone — mobile-first is the default", tag: "[research — 2024]" },
    { big: "37%", label: "of applicants expect an answer within a single day", tag: "[sector-press — speed-to-lead]" },
    { big: "~30%", label: "lower enrollment likelihood when an inquiry sits >48 hrs", tag: "[sector-press — NACAC]" },
  ];
  const cw = 2.85, gap = 0.19, x0 = 0.78, cy = 2.0, ch = 2.55;
  stats.forEach((st, i) => {
    const x = x0 + i * (cw + gap);
    s.addShape(P.shapes.RECTANGLE, { x, y: cy, w: cw, h: ch, fill: { color: CARD }, line: { type: "none" }, shadow: sh() });
    s.addShape(P.shapes.RECTANGLE, { x, y: cy, w: cw, h: 0.09, fill: { color: ORANGE }, line: { type: "none" } });
    s.addText(st.big, { x: x + 0.25, y: cy + 0.32, w: cw - 0.45, h: 0.8, fontFace: F_BOLD, fontSize: 44, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
    s.addText(st.label, { x: x + 0.27, y: cy + 1.22, w: cw - 0.5, h: 0.95, fontFace: F_REG, fontSize: 12, color: INK, align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });
    tag(P, s, x + 0.27, cy + ch - 0.3, cw - 0.45, st.tag, false);
  });

  // the expectation gap callout
  const by = 4.95, bh = 1.35;
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: by, w: 11.78, h: bh, fill: { color: SQUID }, line: { type: "none" } });
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: by, w: 0.09, h: bh, fill: { color: ORANGE }, line: { type: "none" } });
  s.addText("THE EXPECTATION GAP", { x: x0 + 0.4, y: by + 0.2, w: 11, h: 0.35, fontFace: F_BOLD, fontSize: 13, bold: true, color: ORANGE, charSpacing: 1, align: "left", valign: "middle", margin: 0 });
  s.addText("The institution runs on business hours, forms, and phone queues. Students live in an instant, self-serve, mobile world. Every hour that gap stays open costs trust, staff time, and enrollment yield.", {
    x: x0 + 0.4, y: by + 0.56, w: 11.0, h: 0.7, fontFace: F_REG, fontSize: 14, color: WHITE, align: "left", valign: "top", lineSpacingMultiple: 1.05, margin: 0 });
  footer(P, s, false);
  s.addNotes(NOTES.s3);
}

// ============================================================ SLIDE 4 — HOW COLLEGES TRY (and fall short)
function slideApproaches(P) {
  const s = P.addSlide();
  s.background = { color: GRAYBG };
  edgeBar(P, s);
  s.addText("How colleges try to solve it — and where it falls short", {
    x: 0.78, y: 0.4, w: 12.2, h: 0.7, fontFace: F_BOLD, fontSize: 29, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
  s.addText("Every current approach either can't scale, can't personalize, or can't safely touch a student record.", {
    x: 0.8, y: 1.1, w: 11.9, h: 0.45, fontFace: F_TAG, fontSize: 14, italic: true, color: MUTED, align: "left", valign: "top", margin: 0 });

  // header row
  const x0 = 0.78, xW = 3.55, gap = 0.2, midX = x0 + xW + gap, midW = 3.5, gapX = 4.5;
  const gy = 1.72, rowH = 1.12, rowGap = 0.14;
  const colApproach = x0, colDoW = 4.55, colDoWw = 3.15, colGapX = 7.95, colGapW = 4.6;
  s.addText("CURRENT APPROACH", { x: colApproach + 0.05, y: gy, w: 3.6, h: 0.3, fontFace: F_BOLD, fontSize: 12, bold: true, color: SQUID, charSpacing: 0.5, align: "left", valign: "middle", margin: 0 });
  s.addText("WHAT IT DOES", { x: colDoW + 0.05, y: gy, w: colDoWw, h: 0.3, fontFace: F_BOLD, fontSize: 12, bold: true, color: SQUID, charSpacing: 0.5, align: "left", valign: "middle", margin: 0 });
  s.addText("WHY IT FALLS SHORT", { x: colGapX + 0.05, y: gy, w: colGapW, h: 0.3, fontFace: F_BOLD, fontSize: 12, bold: true, color: RED, charSpacing: 0.5, align: "left", valign: "middle", margin: 0 });

  const rows = [
    { a: "Hire more staff / call centers", d: "Humans answer phones and email during business hours.", g: "Expensive; can't scale to FAFSA/registration peaks; still no after-hours or multilingual coverage." },
    { a: "FAQ pages & self-service portals", d: "Static answers students look up themselves.", g: "Not personalized; can't see a student's own record; the hard questions still route to staff." },
    { a: "Generic website chatbots", d: "Bolt-on bots that field common questions.", g: "Hallucinate; no governance or audit; can't safely reach a student record — a FERPA risk." },
  ];
  const ry0 = gy + 0.36;
  rows.forEach((r, i) => {
    const y = ry0 + i * (rowH + rowGap);
    // approach card
    s.addShape(P.shapes.RECTANGLE, { x: colApproach, y, w: 3.6, h: rowH, fill: { color: CARD }, line: { type: "none" }, shadow: shsm() });
    s.addShape(P.shapes.RECTANGLE, { x: colApproach, y, w: 0.08, h: rowH, fill: { color: SQUID }, line: { type: "none" } });
    s.addText(r.a, { x: colApproach + 0.28, y, w: 3.2, h: rowH, fontFace: F_BOLD, fontSize: 13.5, bold: true, color: INK, align: "left", valign: "middle", lineSpacingMultiple: 1.0, margin: 0 });
    // what it does
    s.addText(r.d, { x: colDoW, y, w: 3.25, h: rowH, fontFace: F_REG, fontSize: 11.5, color: INK, align: "left", valign: "middle", lineSpacingMultiple: 1.02, margin: 0 });
    // why it falls short card (red tint)
    s.addShape(P.shapes.RECTANGLE, { x: colGapX, y, w: 4.6, h: rowH, fill: { color: "FBECEA" }, line: { type: "none" } });
    s.addShape(P.shapes.RECTANGLE, { x: colGapX, y, w: 0.08, h: rowH, fill: { color: RED }, line: { type: "none" } });
    s.addText(r.g, { x: colGapX + 0.26, y, w: 4.24, h: rowH, fontFace: F_REG, fontSize: 11.5, color: "8A2A22", align: "left", valign: "middle", lineSpacingMultiple: 1.02, margin: 0 });
  });

  // land line
  const by = ry0 + 3 * (rowH + rowGap) + 0.18, bh = 0.85;
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: by, w: 11.78, h: bh, fill: { color: TEAL }, line: { type: "none" } });
  s.addText([
    { text: "The missing piece:  ", options: { bold: true, color: WHITE } },
    { text: "a governed agent — self-service that can safely reach a student's own record, answer in any language, and produce an audit trail.", options: { color: WHITE } },
  ], { x: x0 + 0.4, y: by, w: 11.0, h: bh, fontFace: F_REG, fontSize: 14.5, align: "left", valign: "middle", lineSpacingMultiple: 1.03, margin: 0 });
  footer(P, s, false);
  s.addNotes(NOTES.s4);
}

// ============================================================ SLIDE 5 — THE COST OF DOING NOTHING
function slideCost(P) {
  const s = P.addSlide();
  s.background = { color: GRAYBG };
  edgeBar(P, s);
  s.addText("The cost of doing nothing", {
    x: 0.78, y: 0.4, w: 12, h: 0.7, fontFace: F_BOLD, fontSize: 33, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
  s.addText("For a mid-size institution, staffing routine contacts by phone and email instead of self-service leaves real money on the table every year.", {
    x: 0.8, y: 1.12, w: 11.9, h: 0.5, fontFace: F_TAG, fontSize: 14, italic: true, color: MUTED, align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });

  // big figure card
  const cy = 1.85, ch = 2.55, cw = 6.9, x0 = 0.78;
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: cy, w: cw, h: ch, fill: { color: CARD }, line: { type: "none" }, shadow: sh() });
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: cy, w: 0.09, h: ch, fill: { color: ORANGE }, line: { type: "none" } });
  s.addText("AVOIDABLE CONTACT-HANDLING COST", { x: x0 + 0.35, y: cy + 0.24, w: cw - 0.6, h: 0.35, fontFace: F_BOLD, fontSize: 14, bold: true, color: ORANGED, charSpacing: 1, align: "left", valign: "middle", margin: 0 });
  s.addText("~$1.2M–$1.6M / yr", { x: x0 + 0.32, y: cy + 0.6, w: cw - 0.6, h: 0.95, fontFace: F_BOLD, fontSize: 52, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
  s.addText([
    { text: "Modeled: ", options: { bold: true } },
    { text: "~120k routine contacts/yr  ×  ~60% deflectable  ×  ~$16 phone/email → self-service delta.  Self-service resolves at $1–$4 vs. $17–$25 by phone.", options: {} },
  ], { x: x0 + 0.35, y: cy + 1.62, w: cw - 0.68, h: 0.7, fontFace: F_REG, fontSize: 12, italic: true, color: MUTED, align: "left", valign: "top", lineSpacingMultiple: 1.05, margin: 0 });
  tag(P, s, x0 + 0.35, cy + ch - 0.3, cw - 0.6, "[modeled — cost-per-contact benchmark × institutional volume]", false);

  // right — the other costs
  const x1 = x0 + cw + 0.4, cw2 = 11.78 - cw - 0.4;
  s.addShape(P.shapes.RECTANGLE, { x: x1, y: cy, w: cw2, h: ch, fill: { color: CARD }, line: { type: "none" }, shadow: sh() });
  s.addShape(P.shapes.RECTANGLE, { x: x1, y: cy, w: 0.09, h: ch, fill: { color: SQUID }, line: { type: "none" } });
  s.addText("AND THE COSTS YOU CAN'T INVOICE", { x: x1 + 0.32, y: cy + 0.24, w: cw2 - 0.6, h: 0.35, fontFace: F_BOLD, fontSize: 13, bold: true, color: SQUID, charSpacing: 0.5, align: "left", valign: "middle", margin: 0 });
  s.addText([
    { text: "Lost enrollment yield when families can't reach anyone at peak.", options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 12 } },
    { text: "Staff burnout and turnover absorbing repetitive, routine volume.", options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 12 } },
    { text: "Equity gap — non-English-speaking and working families underserved after hours.", options: { bullet: { code: "2022" } } },
  ], { x: x1 + 0.36, y: cy + 0.72, w: cw2 - 0.66, h: ch - 1.0, fontFace: F_REG, fontSize: 12.5, color: INK, align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });

  // bottom dark bright-line callout
  const by = cy + ch + 0.32, bh = 1.35;
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: by, w: 11.78, h: bh, fill: { color: SQUID }, line: { type: "none" } });
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: by, w: 0.09, h: bh, fill: { color: ORANGE }, line: { type: "none" } });
  s.addText("THE BRIGHT LINE", { x: x0 + 0.4, y: by + 0.2, w: 11, h: 0.32, fontFace: F_BOLD, fontSize: 13, bold: true, color: ORANGE, charSpacing: 1, align: "left", valign: "middle", margin: 0 });
  s.addText("The agent answers and drafts; a named staff member approves every account-touching action; every record access is audited.", {
    x: x0 + 0.4, y: by + 0.54, w: 11.0, h: 0.72, fontFace: F_REG, fontSize: 15, color: WHITE, align: "left", valign: "top", lineSpacingMultiple: 1.05, margin: 0 });
  footer(P, s, false);
  s.addNotes(NOTES.s5);
}

// ============================================================ SLIDE 6 — HOW WE SOLVE IT (governed pipeline)
function slidePipeline(P) {
  const s = P.addSlide();
  s.background = { color: GRAYBG };
  edgeBar(P, s);
  s.addText("How we solve it — the governed concierge", {
    x: 0.78, y: 0.38, w: 12.2, h: 0.7, fontFace: F_BOLD, fontSize: 31, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
  s.addText("Retrieve approved content and live public data, govern access, answer in any language — then stop at a human gate for anything consequential, and audit everything.", {
    x: 0.8, y: 1.08, w: 12.1, h: 0.6, fontFace: F_TAG, fontSize: 14, italic: true, color: MUTED, align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });

  const steps = [
    { n: 1, title: "Retrieve", sub: "approved content + live College Scorecard (U.S. Dept. of Education)", kind: "auto" },
    { n: 2, title: "Govern", sub: "deny-by-default; record-scope — a student sees only their own record", kind: "auto" },
    { n: 3, title: "Answer in any language", sub: "grounded response via Bedrock + Guardrails", kind: "auto" },
    { n: 4, title: "HUMAN GATE", sub: "a named staff member approves every consequential action", kind: "gate" },
    { n: 5, title: "Audit", sub: "append-only, PII-masked record of every access", kind: "audit" },
  ];
  const n = steps.length, x0 = 0.78, top = 2.0, gap = 0.22, totalW = 11.78;
  const bw = (totalW - gap * (n - 1)) / n, bh = 1.9;
  steps.forEach((st, i) => {
    const x = x0 + i * (bw + gap);
    const fill = st.kind === "gate" ? RED : (st.kind === "audit" ? SQUID : TEAL);
    s.addShape(P.shapes.RECTANGLE, { x, y: top, w: bw, h: bh, fill: { color: fill }, line: { type: "none" }, shadow: shsm() });
    s.addText(String(st.n), { x: x + 0.2, y: top + 0.14, w: 0.6, h: 0.5, fontFace: F_BOLD, fontSize: 24, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
    s.addText(st.title, { x: x + 0.2, y: top + 0.66, w: bw - 0.4, h: 0.6, fontFace: F_BOLD, fontSize: 13, bold: true, color: WHITE, align: "left", valign: "top", lineSpacingMultiple: 0.98, margin: 0 });
    s.addText(st.sub, { x: x + 0.2, y: top + 1.16, w: bw - 0.38, h: 0.68, fontFace: F_REG, fontSize: 9.5, color: "EAF0F3", align: "left", valign: "top", lineSpacingMultiple: 0.98, margin: 0 });
    if (i < n - 1) s.addText("→", { x: x + bw - 0.05, y: top + bh / 2 - 0.22, w: gap + 0.1, h: 0.44, fontFace: F_BOLD, fontSize: 16, bold: true, color: MUTED, align: "center", valign: "middle", margin: 0 });
  });

  const fy = top + bh + 0.42, fh = 1.65, fw = 3.78, fgap = 0.22;
  const cards = [
    { title: "Answers grounded, never invented", body: "every reply cites approved content or live public data; Guardrails mask PII and bound the output." },
    { title: "A student only ever sees their own record", body: "record-scope authorization is deny-by-default and fail-closed — enforced in code, not a policy PDF." },
    { title: "Humans own every consequential action", body: "sends and account changes are human-gated; reads stay instant, self-service." },
  ];
  cards.forEach((c, i) => {
    const x = x0 + i * (fw + fgap);
    s.addShape(P.shapes.RECTANGLE, { x, y: fy, w: fw, h: fh, fill: { color: CARD }, line: { type: "none" }, shadow: sh() });
    s.addShape(P.shapes.RECTANGLE, { x, y: fy, w: 0.07, h: fh, fill: { color: ORANGE }, line: { type: "none" } });
    s.addText(c.title, { x: x + 0.3, y: fy + 0.22, w: fw - 0.55, h: 0.6, fontFace: F_BOLD, fontSize: 14, bold: true, color: INK, align: "left", valign: "top", lineSpacingMultiple: 1.0, margin: 0 });
    s.addText(c.body, { x: x + 0.32, y: fy + 0.82, w: fw - 0.6, h: fh - 0.98, fontFace: F_REG, fontSize: 11, color: MUTED, align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });
  });
  footer(P, s, false);
  s.addNotes(NOTES.s6);
}

// ============================================================ SLIDE 7 — AWS ARCHITECTURE & TRAFFIC FLOW
function archBox(P, s, x, y, w, h, title, sub, color, opts = {}) {
  s.addShape(P.shapes.RECTANGLE, { x, y, w, h, fill: { color }, line: { type: "none" } });
  s.addText([
    { text: title, options: { bold: true, breakLine: !!sub, fontSize: opts.tf || 9.5, color: WHITE } },
    ...(sub ? [{ text: sub, options: { fontSize: opts.sf || 8, color: "F0F4F6" } }] : []),
  ], { x: x + 0.1, y: y + 0.03, w: w - 0.18, h: h - 0.06, fontFace: F_REG, align: "left", valign: "middle", lineSpacingMultiple: 0.94, margin: 0 });
}
function flowNum(P, s, x, y, num) {
  const d = 0.32;
  s.addShape(P.shapes.OVAL, { x, y, w: d, h: d, fill: { color: ORANGE }, line: { color: WHITE, width: 1.5 } });
  s.addText(String(num), { x, y, w: d, h: d, fontFace: F_BOLD, fontSize: 11, bold: true, color: SQUID, align: "center", valign: "middle", margin: 0 });
}
function dashedGroup(P, s, x, y, w, h, label, labelColor) {
  s.addShape(P.shapes.RECTANGLE, { x, y, w, h, fill: { type: "none" }, line: { color: "9AA7B4", width: 1, dashType: "dash" } });
  s.addText(label, { x: x + 0.12, y: y + 0.06, w: w - 0.24, h: 0.28, fontFace: F_BOLD, fontSize: 9, bold: true, color: labelColor || MUTED, charSpacing: 0.5, align: "left", valign: "middle", margin: 0 });
}
function slideArch(P) {
  const s = P.addSlide();
  s.background = { color: WHITE };
  edgeBar(P, s);
  s.addText("AWS architecture & traffic flow", { x: 0.7, y: 0.2, w: 12.2, h: 0.55, fontFace: F_BOLD, fontSize: 29, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });

  const lgX = 0.6, lgY = 0.95, lgW = 2.55, lgH = 4.55;
  dashedGroup(P, s, lgX, lgY, lgW, lgH, "INSTITUTION / EXTERNAL", MUTED);
  const lbx = lgX + 0.13, lbw = lgW - 0.26;
  archBox(P, s, lbx, lgY + 0.42, lbw, 0.6, "Students & families (web / chat / voice)", "", SQUID, { tf: 9 });
  archBox(P, s, lbx, lgY + 1.18, lbw, 0.6, "IdP — Okta / Azure AD / Google", "SAML/OIDC + MFA", SQUID, { tf: 8.5, sf: 7.5 });
  archBox(P, s, lbx, lgY + 1.94, lbw, 0.7, "SIS + Financial-Aid system", "on-prem · PrivateLink / Direct Connect", SQUID, { tf: 8.5, sf: 7 });
  archBox(P, s, lbx, lgY + 2.8, lbw, 0.6, "College Scorecard (public API)", "live U.S. Dept. of Education data", SQUID, { tf: 8, sf: 7 });
  s.addText("PrivateLink / Direct Connect", { x: lbx, y: lgY + 3.5, w: lbw, h: 0.25, fontFace: F_REG, fontSize: 7.5, italic: true, color: MUTED, align: "left", valign: "middle", margin: 0 });

  const cX = 3.35, cY = 0.95, cW = 9.35, cH = 5.1;
  dashedGroup(P, s, cX, cY, cW, cH, "AWS CLOUD — PER-CUSTOMER VPC (dedicated account per institution)", SQUID);

  const e1x = cX + 0.18, e1y = cY + 0.48, e1w = 2.7, e1h = 1.95;
  dashedGroup(P, s, e1x, e1y, e1w, e1h, "EDGE / PUBLIC SUBNET", C_NET);
  archBox(P, s, e1x + 0.12, e1y + 0.4, e1w - 0.24, 0.44, "CloudFront + WAF", "", C_NET, { tf: 9 });
  archBox(P, s, e1x + 0.12, e1y + 0.92, e1w - 0.24, 0.44, "ALB — TLS 1.3 + Cognito auth", "", C_NET, { tf: 8 });
  archBox(P, s, e1x + 0.12, e1y + 1.44, e1w - 0.24, 0.44, "Amazon Cognito — SAML→JWT", "", C_NET, { tf: 8 });

  const e2x = e1x + e1w + 0.22, e2y = cY + 0.48, e2w = 3.05, e2h = 1.95;
  dashedGroup(P, s, e2x, e2y, e2w, e2h, "PRIVATE SUBNET — ECS FARGATE / AGENTCORE", C_COMPUTE);
  const rb = [
    { t: "UI task (concierge console)", color: C_COMPUTE },
    { t: "Agent worker + Amazon Translate", color: C_COMPUTE },
    { t: "MCP auth gateway", s: "all outbound tool calls", color: C_INTEG },
  ];
  const rbh = (e2h - 0.42) / rb.length;
  rb.forEach((b, i) => archBox(P, s, e2x + 0.12, e2y + 0.4 + i * rbh, e2w - 0.24, rbh - 0.07, b.t, b.s || "", b.color, { tf: 8, sf: 6.8 }));

  const e3x = e2x + e2w + 0.22, e3y = cY + 0.48, e3w = 2.55, e3h = 1.95;
  dashedGroup(P, s, e3x, e3y, e3w, e3h, "MODEL LAYER — VPC ENDPOINT", C_MODEL);
  archBox(P, s, e3x + 0.12, e3y + 0.42, e3w - 0.24, 0.62, "Amazon Bedrock", "Claude (analysis + draft)", C_MODEL, { tf: 9, sf: 7.5 });
  archBox(P, s, e3x + 0.12, e3y + 1.14, e3w - 0.24, 0.62, "Bedrock Guardrails", "PII + content filters (mandatory)", C_MODEL, { tf: 9, sf: 7 });

  const dtx = cX + 0.18, dty = cY + 2.6, dtw = cW - 0.36, dth = 1.25;
  dashedGroup(P, s, dtx, dty, dtw, dth, "DATA TIER — KMS CMK-ENCRYPTED", C_STORAGE);
  const dtiles = [
    { t: "Aurora / DynamoDB", s: "session + case state", color: C_MODEL },
    { t: "DynamoDB audit", s: "append-only", color: C_INTEG },
    { t: "S3 Object Lock", s: "WORM records", color: C_STORAGE },
    { t: "Secrets Manager", s: "scoped tokens", color: C_STORAGE },
  ];
  const dtn = dtiles.length, dtgap = 0.18;
  const dtbw = (dtw - 0.24 - dtgap * (dtn - 1)) / dtn;
  dtiles.forEach((b, i) => archBox(P, s, dtx + 0.12 + i * (dtbw + dtgap), dty + 0.42, dtbw, 0.68, b.t, b.s || "", b.color, { tf: 8.5, sf: 7 }));

  const sox = cX + 0.18, soy = cY + 4.02, sow = cW - 0.36, soh = 0.78;
  s.addShape(P.shapes.RECTANGLE, { x: sox, y: soy, w: sow, h: soh, fill: { color: SQUID3 }, line: { type: "none" } });
  s.addText([
    { text: "SECURITY & OPS:  ", options: { bold: true, color: ORANGE } },
    { text: "KMS CMK per data class  ·  IAM least privilege  ·  CloudWatch  ·  X-Ray  ·  CloudTrail  ·  Security Hub + Config", options: { color: "E6ECF1" } },
  ], { x: sox + 0.22, y: soy, w: sow - 0.4, h: soh, fontFace: F_REG, fontSize: 10.5, align: "left", valign: "middle", margin: 0 });

  flowNum(P, s, lgX + lgW - 0.04, lgY + 0.5, 1);
  flowNum(P, s, lgX + lgW - 0.04, lgY + 1.28, 2);
  flowNum(P, s, e1x + e1w - 0.02, e1y + 0.95, 3);
  flowNum(P, s, lgX + lgW - 0.04, lgY + 2.1, 4);
  flowNum(P, s, e2x + e2w / 2 - 0.16, e2y + e2h - 0.04, 5);
  flowNum(P, s, e3x - 0.2, e3y + 0.6, 6);
  flowNum(P, s, dtx + dtw - 0.4, dty - 0.16, 7);
  flowNum(P, s, e2x + e2w - 0.4, e2y + e2h - 0.04, 8);

  s.addText("1 student sign-in   2 SAML federation (MFA at IdP; Cognito issues JWT — no credentials in AWS)   3 authenticated session to concierge   4 SIS / financial-aid + live College Scorecard read over governed connectivity   5 demand scales the agent workers   6 model calls stay inside AWS via VPC endpoint   7 every record access & answer persisted to append-only audit   8 connectors reachable only through the governed MCP gateway",
    { x: 0.6, y: 6.25, w: 12.2, h: 0.95, fontFace: F_REG, fontSize: 9, color: INK, align: "left", valign: "top", lineSpacingMultiple: 1.03, margin: 0 });
  s.addNotes(NOTES.s7);
}

// ============================================================ SLIDE 8 — PROVEN DEPLOYABLE & TESTED
function slideProof(P) {
  const s = P.addSlide();
  s.background = { color: SQUID };
  edgeBar(P, s);
  s.addText("Proven deployable & tested", { x: 0.78, y: 0.34, w: 9, h: 0.6, fontFace: F_BOLD, fontSize: 32, bold: true, color: WHITE, align: "left", valign: "middle", margin: 0 });
  s.addText([
    { text: "Deployed to a real AWS account and verified live on 2026-07-12", options: { bold: true, color: ORANGE } },
    { text: " — then torn down.", options: { color: MUTEDLT } },
  ], { x: 0.8, y: 0.98, w: 11.9, h: 0.35, fontFace: F_REG, fontSize: 13.5, align: "left", valign: "middle", margin: 0 });

  const x0 = 0.78, cw = 5.69, gap = 0.4, ch = 2.46, gy = 1.5, ry = 4.12;
  const cx = [x0, x0 + cw + gap], cyv = [gy, ry];
  const card = (col, row) => ({ x: cx[col], y: cyv[row] });

  // helper to draw a card frame with a colored header label
  function frame(x, y, labelParts, labelColor) {
    s.addShape(P.shapes.RECTANGLE, { x, y, w: cw, h: ch, fill: { color: SQUID2 }, line: { color: "3A485A", width: 1 } });
    s.addShape(P.shapes.RECTANGLE, { x, y, w: cw, h: 0.09, fill: { color: labelColor }, line: { type: "none" } });
    s.addText(labelParts, { x: x + 0.3, y: y + 0.22, w: cw - 0.55, h: 0.32, fontFace: F_BOLD, fontSize: 13, bold: true, color: labelColor, charSpacing: 0.5, align: "left", valign: "middle", margin: 0 });
  }

  // CARD 1 — live data + real answer
  let p = card(0, 0);
  frame(p.x, p.y, "LIVE DATA + REAL ANSWER", TEALLT);
  s.addText("The deployed concierge pulled live College Scorecard data for “University of Michigan-Ann Arbor”; Amazon Bedrock returned a grounded answer citing the real figures:", {
    x: p.x + 0.32, y: p.y + 0.62, w: cw - 0.6, h: 0.8, fontFace: F_REG, fontSize: 11, color: "D6DEE6", align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });
  s.addText([
    { text: "15.6%", options: { bold: true, color: ORANGE, fontSize: 26 } },
    { text: "  admission rate", options: { color: "C9D2DC", fontSize: 12 } },
    { text: "        ", options: { fontSize: 12 } },
    { text: "$17,736", options: { bold: true, color: ORANGE, fontSize: 26 } },
    { text: "  in-state tuition", options: { color: "C9D2DC", fontSize: 12 } },
  ], { x: p.x + 0.32, y: p.y + 1.5, w: cw - 0.6, h: 0.6, fontFace: F_BOLD, align: "left", valign: "middle", margin: 0 });
  s.addText("Genuine retrieval + generation via api.data.gov — not fixtures.", { x: p.x + 0.32, y: p.y + ch - 0.36, w: cw - 0.6, h: 0.28, fontFace: F_REG, fontSize: 9, italic: true, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });

  // CARD 2 — governance proven live (4/4)
  p = card(1, 0);
  frame(p.x, p.y, "GOVERNANCE PROVEN LIVE (4/4)", ORANGE);
  const rows = [
    { l: "Public info", d: "ALLOW", c: TEALLT },
    { l: "Own record", d: "ALLOW", c: TEALLT },
    { l: "Another student's record", d: "DENY  ·  record-scope", c: REDLT },
    { l: "Consequential send", d: "PENDING_APPROVAL  ·  human-gated", c: ORANGE },
  ];
  const r0 = p.y + 0.64, rh = 0.34;
  rows.forEach((r, i) => {
    const y = r0 + i * rh;
    s.addText(r.l, { x: p.x + 0.32, y, w: 2.15, h: rh, fontFace: F_REG, fontSize: 11, color: "D6DEE6", align: "left", valign: "middle", margin: 0 });
    s.addText("→", { x: p.x + 2.34, y, w: 0.24, h: rh, fontFace: F_BOLD, fontSize: 11, color: MUTEDLT, align: "center", valign: "middle", margin: 0 });
    s.addText(r.d, { x: p.x + 2.62, y, w: cw - 2.85, h: rh, fontFace: F_BOLD, fontSize: 10.5, bold: true, color: r.c, align: "left", valign: "middle", margin: 0 });
  });
  s.addText("All confirmed in the deployed append-only audit table.", { x: p.x + 0.32, y: p.y + ch - 0.32, w: cw - 0.6, h: 0.28, fontFace: F_REG, fontSize: 9, italic: true, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });

  // CARD 3 — deploy in an afternoon
  p = card(0, 1);
  frame(p.x, p.y, "DEPLOY IN AN AFTERNOON", TEALLT);
  s.addText([
    { text: "One CloudFormation stack ", options: { color: "D6DEE6" } },
    { text: "(infra/cloudformation/pilot-concierge.template.json)", options: { color: "9FB6C4", italic: true } },
    { text: " + the copy-paste runbook ", options: { color: "D6DEE6" } },
    { text: "runbooks/agent-deploy/01-PILOT.md", options: { color: "9FB6C4", italic: true } },
    { text: ".", options: { color: "D6DEE6" } },
  ], { x: p.x + 0.32, y: p.y + 0.62, w: cw - 0.6, h: 1.05, fontFace: F_REG, fontSize: 11, align: "left", valign: "top", lineSpacingMultiple: 1.05, margin: 0 });
  s.addText([
    { text: "< $1", options: { bold: true, color: ORANGE, fontSize: 26 } },
    { text: "   cost of the entire verification run", options: { color: "C9D2DC", fontSize: 12 } },
  ], { x: p.x + 0.32, y: p.y + 1.62, w: cw - 0.6, h: 0.5, fontFace: F_BOLD, align: "left", valign: "middle", margin: 0 });

  // CARD 4 — tested
  p = card(1, 1);
  frame(p.x, p.y, "TESTED", TEALLT);
  s.addText([
    { text: "200 automated tests pass", options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 8, color: "E6ECF1" } },
    { text: "axe-core WCAG scan — 0 violations", options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 8, color: "E6ECF1" } },
    { text: "Runtime student-PII masking — SSN / email / ID redacted in the cloud", options: { bullet: { code: "2022" }, color: "E6ECF1" } },
  ], { x: p.x + 0.5, y: p.y + 0.66, w: cw - 0.85, h: 1.4, fontFace: F_REG, fontSize: 12, align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });

  s.addText("Reference-accelerator pilot proof — full production needs your IdP, your SIS connector, and a security review.", {
    x: x0, y: PH - 0.52, w: 11.9, h: 0.3, fontFace: F_REG, fontSize: 9, italic: true, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
  s.addNotes(NOTES.s8);
}

// ============================================================ SLIDE 9 — ROI & WHY NOW / PILOT OFFER
function slideROI(P) {
  const s = P.addSlide();
  s.background = { color: SQUID };
  edgeBar(P, s);
  s.addText("ROI & why now", { x: 0.78, y: 0.36, w: 9, h: 0.6, fontFace: F_BOLD, fontSize: 32, bold: true, color: WHITE, align: "left", valign: "middle", margin: 0 });
  s.addText("Outcomes documented at reference institutions — and the payback math for your own baseline.", {
    x: 0.8, y: 0.98, w: 11.9, h: 0.4, fontFace: F_TAG, fontSize: 14, italic: true, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });

  const stats = [
    { big: "75%", label: "reduction in financial-aid status contacts", src: "Highline College", tag: "[vendor — AWS]" },
    { big: ">15 min → <30 sec", label: "student wait time at similar staffing", src: "UT Austin", tag: "[vendor — AWS]", sz: 26 },
    { big: "$1–$4", label: "self-service contact cost vs. $17–$25 by phone", src: "industry benchmark", tag: "[sector-press/estimate]" },
    { big: "4–9 mo", label: "modeled payback at a mid-size institution", src: "your baseline", tag: "[modeled]" },
  ];
  const x0 = 0.78, cw = 5.69, gap = 0.4, ch = 2.02, gy = 1.55, ry = 3.72;
  const cx = [x0, x0 + cw + gap], cyv = [gy, ry];
  stats.forEach((st, i) => {
    const x = cx[i % 2], y = cyv[Math.floor(i / 2)];
    s.addShape(P.shapes.RECTANGLE, { x, y, w: cw, h: ch, fill: { color: SQUID2 }, line: { color: "3A485A", width: 1 } });
    s.addShape(P.shapes.RECTANGLE, { x, y, w: 0.09, h: ch, fill: { color: ORANGE }, line: { type: "none" } });
    s.addText(st.big, { x: x + 0.34, y: y + 0.22, w: cw - 0.62, h: 0.8, fontFace: F_BOLD, fontSize: st.sz || 40, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
    s.addText(st.label, { x: x + 0.36, y: y + 1.06, w: cw - 0.66, h: 0.55, fontFace: F_REG, fontSize: 13, color: "D6DEE6", align: "left", valign: "top", lineSpacingMultiple: 1.0, margin: 0 });
    s.addText([
      { text: st.src + "   ", options: { color: TEALLT, bold: true } },
      { text: st.tag, options: { color: MUTEDLT, italic: true } },
    ], { x: x + 0.36, y: y + ch - 0.36, w: cw - 0.62, h: 0.28, fontFace: F_REG, fontSize: 9, align: "left", valign: "middle", margin: 0 });
  });

  // close bar
  const by = ry + ch + 0.3, bh = 1.12;
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: by, w: 11.78, h: bh, fill: { color: SQUID3 }, line: { color: "3A485A", width: 1 } });
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: by, w: 0.09, h: bh, fill: { color: ORANGE }, line: { type: "none" } });
  s.addText([
    { text: "The offer:  ", options: { bold: true, color: ORANGE } },
    { text: "land the governed front door in a 6–12 week pilot on one live system of record — then expand the same platform to the other seven agents.", options: { color: WHITE } },
  ], { x: x0 + 0.4, y: by, w: 11.0, h: bh, fontFace: F_REG, fontSize: 15, align: "left", valign: "middle", lineSpacingMultiple: 1.05, margin: 0 });
  footer(P, s, true);
  s.addNotes(NOTES.s9);
}

// ============================================================ SPEAKER NOTES
const NOTES = {
  s1: "[00:20] Open on the promise: this is the 24/7 governed front door to the institution. Frame Agent 01 as the land-first motion — the safest, most visible, most measurable first deployment that proves the shared governed platform. To the CIO it's the lowest-decision-risk agent; to the CFO it's a fast contact-cost ROI. The one line that lands: 'the same governed platform under this concierge runs all eight agents.' Note the disclaimer up front — this is a reference accelerator, not an AWS product — so the room trusts every later claim.",
  s2: "[00:45] The issue. Lead with the GAO headline: during the 2024-25 FAFSA cycle, about three of every four calls to the federal aid line went unanswered — roughly 4 million of 5.4 million. That is the sharpest public proxy for the routine-inquiry overload every institution's front office feels at peak. The one line: 'families can't self-serve, and the phones can't keep up.' The three cards make it concrete — 24/7 and multilingual demand, seasonal peaks, and complex casework waiting behind routine questions.",
  s3: "[01:10] What students expect. The bar is now set by consumer apps, not by the registrar. 86% of students expect 24/7 support, 72% are mobile-first, and a third of applicants expect an answer within a day. When an inquiry sits more than 48 hours, enrollment likelihood drops about 30% — so the gap isn't cosmetic, it costs yield. The one line: 'students live in an instant, self-serve, mobile world; the institution runs on business hours and phone queues — that's the expectation gap.' Tag the softer figures as sector-press so the room knows what's rigorous.",
  s4: "[01:35] How colleges try today — and why each falls short. Walk the three rows: more staff can't scale to peaks or cover after-hours; FAQ portals are static and can't see a student's record; generic chatbots hallucinate, have no audit, and can't safely touch a record — a FERPA risk. Land the teal line: the missing piece is a governed agent — self-service that can safely reach the student's own record, answer in any language, and produce an audit trail. This is the frame for everything that follows.",
  s5: "[02:00] The cost of doing nothing. For a mid-size institution the modeled avoidable contact-handling cost is ~$1.2M–$1.6M/yr — and the arithmetic is on the slide, so it's defensible, not invented; swap in their real volumes live. Then the costs you can't invoice: lost enrollment yield at peak, staff burnout, and an equity gap for non-English-speaking and working families. Close on the bright line — the agent answers and drafts; a named human approves every account-touching action; every access is audited. CISOs care most about that line.",
  s6: "[02:30] How we solve it. Five governed steps: retrieve approved content plus live public data (College Scorecard), govern with deny-by-default record-scope, answer in any language through Bedrock + Guardrails, stop at the human gate (red) for anything consequential, and audit everything append-only. The one line: 'reads are instant and self-serve; consequential actions are human-only.' The three cards are the assurances every regulated buyer asks for — grounded answers, own-record-only, humans own the account action.",
  s7: "[03:00] Architecture — trace the eight numbered flow steps. To deploy, the customer provides an IdP (Okta/Azure AD/Google), governed reachability to SIS + financial-aid, approved KB content, and a named approver group; the live College Scorecard read needs only outbound API access through the gateway. Bedrock + Guardrails are reached over a VPC endpoint and are mandatory — student PII never egresses to an external AI API after masking. If someone asks 'is this real / is this safe?', this slide plus slide 8 are your proof.",
  s8: "[03:45] The differentiator — this isn't a slideware concept. We deployed this concierge to a real AWS account on 2026-07-12, verified it live, and tore it down. It pulled live College Scorecard data for Michigan and Bedrock returned a grounded answer with the real figures — 15.6% admission rate, $17,736 in-state tuition. Governance held 4/4: public info allowed, own record allowed, another student's record denied by record-scope, a consequential send held for human approval — all in the deployed append-only audit. One CloudFormation stack plus a copy-paste runbook, whole run under a dollar; 200 tests pass, axe-core clean, PII masked at runtime. To a skeptical CIO: 'you can reproduce this in your own account in an afternoon.' Be honest about the footer — production still needs your IdP, your SIS connector, and a security review.",
  s9: "[04:20] ROI and the ask. Reference outcomes: Highline cut financial-aid status contacts 75%; UT Austin took waits from >15 minutes to under 30 seconds at similar staffing; self-service resolves at $1–$4 vs $17–$25 by phone; modeled payback is 4–9 months at a mid-size institution. Tag vendor vs modeled honestly — don't oversell. To the CFO: 'the payback is months, not years, and the math uses your baseline.' To the CIO: 'land the governed front door in a 6–12 week pilot on one live system of record, then expand the same platform to the other seven agents.' That's the close — one platform, eight agents, start here.",
};

// ============================================================ BUILD
const P = new pptxgen();
P.defineLayout({ name: "EDU", width: PW, height: PH });
P.layout = "EDU";
P.author = "EDU AI Agent Suite";
P.title = "Student & Family Services Concierge — GTM";

slideTitle(P);
slideIssue(P);
slideExpect(P);
slideApproaches(P);
slideCost(P);
slidePipeline(P);
slideArch(P);
slideProof(P);
slideROI(P);

P.writeFile({ fileName: "EDU-01-Student-Family-Concierge.pptx" }).then((f) => console.log("WROTE", f));
