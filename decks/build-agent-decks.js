/* EDU AI Agent Suite — Go-to-Market deck generator
 * ONE generator drives all 9 decks (8 agents + suite overview) from per-agent
 * content objects, replicating the AWS-standard reference layout supplied by
 * the user (navy title / navy stat hook / light issue+cost / light governed
 * pipeline / light AWS architecture+traffic flow / navy proof+payback).
 *
 * Audience: CIO / CFO / Director of Infrastructure. Board-defensible metrics,
 * source-class tags on-slide, explicit cost-of-doing-nothing.
 *
 * Run:  node decks/build-agent-decks.js
 */
const pptxgen = require("pptxgenjs");

// ============================================================ PALETTE / FONTS
const SQUID   = "232F3E"; // Squid Ink navy — dark slide bg, titles
const SQUID2  = "2E3B4E"; // lighter navy (stat cards on dark)
const SQUID3  = "1B2530"; // deeper navy for takeaway bars
const ORANGE  = "FF9900"; // AWS orange — accents, edge bar, stat numbers
const ORANGED = "E88A00"; // darker orange
const TEAL    = "16A085"; // secondary cards / positive flow
const RED     = "C0392B"; // HUMAN-GATE only
const GRAYBG  = "F2F3F4"; // light content background
const CARD    = "FFFFFF";
const WHITE   = "FFFFFF";
const INK     = "232F3E"; // body text on light
const MUTED   = "6B7785"; // muted gray labels / taglines
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
const F_TAG  = "Cambria"; // italic taglines

const EDGE = 0.14; // orange left-edge bar width (inches) — AWS-brand styling per user template
const PW = 13.333, PH = 7.5;

const sh   = () => ({ type: "outer", color: "000000", blur: 7, offset: 3, angle: 90, opacity: 0.16 });
const shsm = () => ({ type: "outer", color: "000000", blur: 5, offset: 2, angle: 90, opacity: 0.10 });

// ------------------------------------------------------------ primitives (all take P = active pptx instance)
function edgeBar(P, s) {
  s.addShape(P.shapes.RECTANGLE, { x: 0, y: 0, w: EDGE, h: PH, fill: { color: ORANGE }, line: { type: "none" } });
}
function footer(P, s, text, onDark) {
  s.addText(text || "EDU AI Agent Suite · Governed Agentic AI on AWS", {
    x: 0.55, y: PH - 0.42, w: PW - 1.1, h: 0.3, fontFace: F_REG, fontSize: 9.5,
    color: onDark ? MUTEDLT : MUTED, align: "left", valign: "middle", margin: 0,
  });
}
function tag(P, s, x, y, txt, onDark) {
  if (!txt) return;
  const w = Math.min(4.2, 0.10 + txt.length * 0.062);
  s.addText(txt, {
    x, y, w, h: 0.22, fontFace: F_REG, fontSize: 7.5, italic: true,
    color: onDark ? MUTEDLT : MUTED, align: "left", valign: "middle", margin: 0,
  });
}

// ============================================================ SLIDE 1 — TITLE
function slideTitle(P, d) {
  const s = P.addSlide();
  s.background = { color: SQUID };
  edgeBar(P, s);
  s.addText(d.name, { x: 0.85, y: 1.7, w: 11.6, h: 1.9, fontFace: F_BOLD, fontSize: 42, bold: true, color: WHITE, align: "left", valign: "middle", lineSpacingMultiple: 1.02, margin: 0 });
  s.addText("A Governed Agentic AI Reference Architecture for Education", { x: 0.87, y: 3.75, w: 11.4, h: 0.6, fontFace: F_BOLD, fontSize: 21, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
  s.addText(`Agent ${d.num} of 8  ·  ${d.tagline}`, { x: 0.88, y: 4.55, w: 11.4, h: 0.5, fontFace: F_TAG, fontSize: 15, italic: true, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
  s.addText("EDU AI Agent Suite", { x: 0.88, y: 5.7, w: 11.4, h: 0.35, fontFace: F_BOLD, fontSize: 14, bold: true, color: WHITE, align: "left", valign: "middle", margin: 0 });
  s.addText("EDU AI Agent Suite  ·  Built on AWS  ·  June 2026", { x: 0.88, y: 6.05, w: 11.4, h: 0.3, fontFace: F_REG, fontSize: 11, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
  s.addNotes(d.notes.s1);
}

// ============================================================ SLIDE 2 — HOOK
function slideHook(P, d) {
  const s = P.addSlide();
  s.background = { color: SQUID };
  edgeBar(P, s);
  s.addText(d.hero, { x: 0.85, y: 0.85, w: 11.7, h: 1.15, fontFace: F_BOLD, fontSize: 42, bold: true, color: WHITE, align: "left", valign: "middle", charSpacing: 1, margin: 0, lineSpacingMultiple: 1.0 });
  s.addText(d.name, { x: 0.87, y: 2.0, w: 11.6, h: 0.55, fontFace: F_BOLD, fontSize: 22, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
  s.addText(d.valueProp, { x: 0.88, y: 2.65, w: 11.3, h: 0.85, fontFace: F_TAG, fontSize: 15, italic: true, color: MUTEDLT, align: "left", valign: "top", lineSpacingMultiple: 1.05, margin: 0 });
  const cw = 3.62, gap = 0.32, x0 = 0.85, cy = 3.9, ch = 2.05;
  d.hookStats.forEach((st, i) => {
    const x = x0 + i * (cw + gap);
    const wraps = st.big.length > 9; // long stats wrap to 2 lines — give the label more room
    s.addShape(P.shapes.RECTANGLE, { x, y: cy, w: cw, h: ch, fill: { color: SQUID2 }, line: { color: "3A485A", width: 1 } });
    s.addText(st.big, { x: x + 0.28, y: cy + 0.18, w: cw - 0.5, h: wraps ? 0.98 : 0.8, fontFace: F_BOLD, fontSize: wraps ? 28 : 33, bold: true, color: ORANGE, align: "left", valign: "top", lineSpacingMultiple: 0.95, margin: 0 });
    s.addText(st.label, { x: x + 0.3, y: cy + 1.12, w: cw - 0.55, h: 0.6, fontFace: F_REG, fontSize: 12, color: "C9D2DC", align: "left", valign: "top", lineSpacingMultiple: 1.0, margin: 0 });
    tag(P, s, x + 0.3, cy + ch - 0.26, st.tag, true);
  });
  footer(P, s, "EDU AI Agent Suite  ·  Built on AWS  ·  June 2026", true);
  s.addNotes(d.notes.s2);
}

// ============================================================ SLIDE 3 — ISSUE + COST
function slideIssueCost(P, d) {
  const s = P.addSlide();
  s.background = { color: GRAYBG };
  edgeBar(P, s);
  s.addText("The Issue & The Cost of Doing Nothing", { x: 0.78, y: 0.4, w: 12, h: 0.8, fontFace: F_BOLD, fontSize: 33, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
  const cw = 5.78, x0 = 0.78, cy = 1.45, ch = 3.7, gap = 0.45;
  // LEFT — THE ISSUE
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: cy, w: cw, h: ch, fill: { color: CARD }, line: { type: "none" }, shadow: sh() });
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: cy, w: 0.08, h: ch, fill: { color: SQUID }, line: { type: "none" } });
  s.addText("THE ISSUE", { x: x0 + 0.35, y: cy + 0.22, w: cw - 0.7, h: 0.45, fontFace: F_BOLD, fontSize: 16, bold: true, color: SQUID, charSpacing: 1, align: "left", valign: "middle", margin: 0 });
  s.addText(d.issueBullets.map((b) => ({ text: b, options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 9, color: INK } })), { x: x0 + 0.4, y: cy + 0.78, w: cw - 0.75, h: ch - 1.0, fontFace: F_REG, fontSize: 13, color: INK, align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });
  // RIGHT — COST OF DOING NOTHING
  const x1 = x0 + cw + gap;
  s.addShape(P.shapes.RECTANGLE, { x: x1, y: cy, w: cw, h: ch, fill: { color: CARD }, line: { type: "none" }, shadow: sh() });
  s.addShape(P.shapes.RECTANGLE, { x: x1, y: cy, w: 0.08, h: ch, fill: { color: ORANGE }, line: { type: "none" } });
  s.addText("THE COST OF DOING NOTHING", { x: x1 + 0.35, y: cy + 0.22, w: cw - 0.7, h: 0.45, fontFace: F_BOLD, fontSize: 16, bold: true, color: ORANGED, charSpacing: 1, align: "left", valign: "middle", margin: 0 });
  s.addText(d.costBig, { x: x1 + 0.34, y: cy + 0.66, w: cw - 0.7, h: 0.78, fontFace: F_BOLD, fontSize: 36, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
  s.addText(d.costMath, { x: x1 + 0.38, y: cy + 1.5, w: cw - 0.78, h: 0.95, fontFace: F_REG, fontSize: 11, italic: true, color: MUTED, align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });
  s.addText(d.costRisks.map((b) => ({ text: b, options: { bullet: { code: "2022" }, breakLine: true, paraSpaceAfter: 7, color: INK } })), { x: x1 + 0.4, y: cy + 2.5, w: cw - 0.78, h: ch - 2.7, fontFace: F_REG, fontSize: 12, color: INK, align: "left", valign: "top", lineSpacingMultiple: 1.0, margin: 0 });
  tag(P, s, x1 + 0.36, cy + ch - 0.3, d.costTag, false);
  // bottom dark callout bar — BRIGHT LINE
  const by = cy + ch + 0.35, bh = 1.0;
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: by, w: 11.78, h: bh, fill: { color: SQUID }, line: { type: "none" } });
  s.addText([
    { text: "The design line:  ", options: { bold: true, color: ORANGE } },
    { text: d.brightLine, options: { color: WHITE } },
  ], { x: x0 + 0.4, y: by, w: 11.0, h: bh, fontFace: F_REG, fontSize: 14.5, align: "left", valign: "middle", lineSpacingMultiple: 1.04, margin: 0 });
  footer(P, s, null, false);
  s.addNotes(d.notes.s3);
}

// ============================================================ SLIDE 4 — GOVERNED PIPELINE
function slidePipeline(P, d) {
  const s = P.addSlide();
  s.background = { color: GRAYBG };
  edgeBar(P, s);
  s.addText("How We Solve It — A Governed Pipeline", { x: 0.78, y: 0.38, w: 12, h: 0.7, fontFace: F_BOLD, fontSize: 31, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
  s.addText(d.pipelineTagline, { x: 0.8, y: 1.06, w: 12.0, h: 0.6, fontFace: F_TAG, fontSize: 14, italic: true, color: MUTED, align: "left", valign: "top", lineSpacingMultiple: 1.02, margin: 0 });
  const steps = d.pipeline;
  const n = steps.length, x0 = 0.78, top = 2.0, gap = 0.22, totalW = 11.78;
  const bw = (totalW - gap * (n - 1)) / n, bh = 1.7;
  steps.forEach((st, i) => {
    const x = x0 + i * (bw + gap);
    const fill = st.kind === "gate" ? RED : (st.kind === "audit" ? SQUID : TEAL);
    s.addShape(P.shapes.RECTANGLE, { x, y: top, w: bw, h: bh, fill: { color: fill }, line: { type: "none" }, shadow: shsm() });
    s.addText(String(st.n), { x: x + 0.18, y: top + 0.12, w: 0.6, h: 0.5, fontFace: F_BOLD, fontSize: 22, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
    s.addText(st.title, { x: x + 0.18, y: top + 0.58, w: bw - 0.36, h: 0.6, fontFace: F_BOLD, fontSize: 12.5, bold: true, color: WHITE, align: "left", valign: "top", lineSpacingMultiple: 0.98, margin: 0 });
    s.addText(st.sub, { x: x + 0.18, y: top + 1.16, w: bw - 0.34, h: 0.5, fontFace: F_REG, fontSize: 9, color: "EAF0F3", align: "left", valign: "top", lineSpacingMultiple: 0.96, margin: 0 });
    if (i < n - 1) s.addText("→", { x: x + bw - 0.05, y: top + bh / 2 - 0.22, w: gap + 0.1, h: 0.44, fontFace: F_BOLD, fontSize: 15, bold: true, color: MUTED, align: "center", valign: "middle", margin: 0 });
  });
  const fy = top + bh + 0.5, fh = 1.6, fw = 3.78, fgap = 0.22;
  d.pipelineCards.forEach((c, i) => {
    const x = x0 + i * (fw + fgap);
    s.addShape(P.shapes.RECTANGLE, { x, y: fy, w: fw, h: fh, fill: { color: CARD }, line: { type: "none" }, shadow: sh() });
    s.addShape(P.shapes.RECTANGLE, { x, y: fy, w: 0.07, h: fh, fill: { color: ORANGE }, line: { type: "none" } });
    s.addText(c.title, { x: x + 0.3, y: fy + 0.2, w: fw - 0.55, h: 0.55, fontFace: F_BOLD, fontSize: 14, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
    s.addText(c.body, { x: x + 0.32, y: fy + 0.74, w: fw - 0.6, h: fh - 0.9, fontFace: F_REG, fontSize: 11, color: MUTED, align: "left", valign: "top", lineSpacingMultiple: 1.0, margin: 0 });
  });
  footer(P, s, null, false);
  s.addNotes(d.notes.s4);
}

// ============================================================ SLIDE 5 — AWS ARCHITECTURE & TRAFFIC FLOW
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
function slideArch(P, d) {
  const s = P.addSlide();
  s.background = { color: WHITE };
  edgeBar(P, s);
  s.addText(d.archTitle || "AWS Architecture & Traffic Flow", { x: 0.7, y: 0.2, w: 12.2, h: 0.55, fontFace: F_BOLD, fontSize: 29, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });

  // LEFT dashed group
  const lgX = 0.6, lgY = 0.95, lgW = 2.55, lgH = 4.55;
  dashedGroup(P, s, lgX, lgY, lgW, lgH, "INSTITUTION / EXTERNAL", MUTED);
  const lbx = lgX + 0.13, lbw = lgW - 0.26;
  archBox(P, s, lbx, lgY + 0.42, lbw, 0.6, d.arch.users, "", SQUID, { tf: 9 });
  archBox(P, s, lbx, lgY + 1.18, lbw, 0.6, "IdP — Okta / Azure AD / Google", "SAML/OIDC + MFA", SQUID, { tf: 8.5, sf: 7.5 });
  archBox(P, s, lbx, lgY + 1.94, lbw, 0.7, d.arch.sor, "on-prem · PrivateLink / Direct Connect", SQUID, { tf: 8.5, sf: 7 });
  archBox(P, s, lbx, lgY + 2.8, lbw, 0.6, d.arch.ext, "", SQUID, { tf: 8.5 });
  s.addText("PrivateLink / Direct Connect", { x: lbx, y: lgY + 3.5, w: lbw, h: 0.25, fontFace: F_REG, fontSize: 7.5, italic: true, color: MUTED, align: "left", valign: "middle", margin: 0 });

  // BIG AWS CLOUD group
  const cX = 3.35, cY = 0.95, cW = 9.35, cH = 5.1;
  dashedGroup(P, s, cX, cY, cW, cH, "AWS CLOUD — PER-CUSTOMER VPC (dedicated account per institution)", SQUID);

  // EDGE / PUBLIC SUBNET
  const e1x = cX + 0.18, e1y = cY + 0.48, e1w = 2.7, e1h = 1.95;
  dashedGroup(P, s, e1x, e1y, e1w, e1h, "EDGE / PUBLIC SUBNET", C_NET);
  archBox(P, s, e1x + 0.12, e1y + 0.4, e1w - 0.24, 0.44, "CloudFront + WAF", "", C_NET, { tf: 9 });
  archBox(P, s, e1x + 0.12, e1y + 0.92, e1w - 0.24, 0.44, "ALB — TLS 1.3 + Cognito auth", "", C_NET, { tf: 8 });
  archBox(P, s, e1x + 0.12, e1y + 1.44, e1w - 0.24, 0.44, "Amazon Cognito — SAML→JWT", "", C_NET, { tf: 8 });

  // PRIVATE SUBNET — runtime
  const e2x = e1x + e1w + 0.22, e2y = cY + 0.48, e2w = 3.05, e2h = 1.95;
  dashedGroup(P, s, e2x, e2y, e2w, e2h, "PRIVATE SUBNET — ECS FARGATE / AGENTCORE", C_COMPUTE);
  const rb = d.arch.runtime;
  const rbh = (e2h - 0.42) / rb.length;
  rb.forEach((b, i) => archBox(P, s, e2x + 0.12, e2y + 0.4 + i * rbh, e2w - 0.24, rbh - 0.07, b.t, b.s || "", b.color || C_COMPUTE, { tf: 8, sf: 6.8 }));

  // MODEL LAYER
  const e3x = e2x + e2w + 0.22, e3y = cY + 0.48, e3w = 2.55, e3h = 1.95;
  dashedGroup(P, s, e3x, e3y, e3w, e3h, "MODEL LAYER — VPC ENDPOINT", C_MODEL);
  archBox(P, s, e3x + 0.12, e3y + 0.42, e3w - 0.24, 0.62, "Amazon Bedrock", "Claude (analysis + draft)", C_MODEL, { tf: 9, sf: 7.5 });
  archBox(P, s, e3x + 0.12, e3y + 1.14, e3w - 0.24, 0.62, "Bedrock Guardrails", "PII + content filters (mandatory)", C_MODEL, { tf: 9, sf: 7 });

  // DATA TIER
  const dtx = cX + 0.18, dty = cY + 2.6, dtw = cW - 0.36, dth = 1.25;
  dashedGroup(P, s, dtx, dty, dtw, dth, "DATA TIER — KMS CMK-ENCRYPTED", C_STORAGE);
  const dtiles = d.arch.data, dtn = dtiles.length, dtgap = 0.18;
  const dtbw = (dtw - 0.24 - dtgap * (dtn - 1)) / dtn;
  dtiles.forEach((b, i) => archBox(P, s, dtx + 0.12 + i * (dtbw + dtgap), dty + 0.42, dtbw, 0.68, b.t, b.s || "", b.color || C_STORAGE, { tf: 8.5, sf: 7 }));

  // SECURITY & OPS bar
  const sox = cX + 0.18, soy = cY + 4.02, sow = cW - 0.36, soh = 0.78;
  s.addShape(P.shapes.RECTANGLE, { x: sox, y: soy, w: sow, h: soh, fill: { color: SQUID3 }, line: { type: "none" } });
  s.addText([
    { text: "SECURITY & OPS:  ", options: { bold: true, color: ORANGE } },
    { text: "KMS CMK per data class  ·  IAM least privilege  ·  CloudWatch  ·  X-Ray  ·  CloudTrail  ·  Security Hub + Config", options: { color: "E6ECF1" } },
  ], { x: sox + 0.22, y: soy, w: sow - 0.4, h: soh, fontFace: F_REG, fontSize: 10.5, align: "left", valign: "middle", margin: 0 });

  // numbered orange flow circles
  flowNum(P, s, lgX + lgW - 0.04, lgY + 0.5, 1);
  flowNum(P, s, lgX + lgW - 0.04, lgY + 1.28, 2);
  flowNum(P, s, e1x + e1w - 0.02, e1y + 0.95, 3);
  flowNum(P, s, lgX + lgW - 0.04, lgY + 2.1, 4);
  flowNum(P, s, e2x + e2w / 2 - 0.16, e2y + e2h - 0.04, 5);
  flowNum(P, s, e3x - 0.2, e3y + 0.6, 6);
  flowNum(P, s, dtx + dtw - 0.4, dty - 0.16, 7);
  flowNum(P, s, e2x + e2w - 0.4, e2y + e2h - 0.04, 8);

  // bottom numbered legend
  s.addText(d.arch.legend, { x: 0.6, y: 6.25, w: 12.2, h: 0.95, fontFace: F_REG, fontSize: 9, color: INK, align: "left", valign: "top", lineSpacingMultiple: 1.03, margin: 0 });
  s.addNotes(d.notes.s5);
}

// ============================================================ SLIDE 6 — PROOF / PAYBACK / DEPLOY
function slideProof(P, d) {
  const s = P.addSlide();
  s.background = { color: SQUID };
  edgeBar(P, s);
  s.addText("Proof, Payback & How to Deploy", { x: 0.78, y: 0.38, w: 12, h: 0.7, fontFace: F_BOLD, fontSize: 32, bold: true, color: WHITE, align: "left", valign: "middle", margin: 0 });
  const cy = 1.35, ch = 4.05, cw = 5.78, x0 = 0.78, gap = 0.45;
  // LEFT — MEASURED OUTCOMES 2x2
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: cy, w: cw, h: ch, fill: { color: SQUID2 }, line: { color: "3A485A", width: 1 } });
  s.addText("MEASURED OUTCOMES", { x: x0 + 0.32, y: cy + 0.22, w: cw - 0.6, h: 0.4, fontFace: F_BOLD, fontSize: 15, bold: true, color: ORANGE, charSpacing: 1, align: "left", valign: "middle", margin: 0 });
  const gx = [x0 + 0.32, x0 + cw / 2 + 0.12], gy = [cy + 0.78, cy + 2.1];
  d.proofStats.forEach((st, i) => {
    const x = gx[i % 2], y = gy[Math.floor(i / 2)];
    s.addText(st.big, { x, y, w: cw / 2 - 0.4, h: 0.6, fontFace: F_BOLD, fontSize: 28, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
    s.addText(st.label, { x, y: y + 0.58, w: cw / 2 - 0.42, h: 0.6, fontFace: F_REG, fontSize: 10.5, color: "C9D2DC", align: "left", valign: "top", lineSpacingMultiple: 0.98, margin: 0 });
    tag(P, s, x, y + 1.16, st.tag, true);
  });
  // RIGHT — DEPLOY
  const x1 = x0 + cw + gap;
  s.addShape(P.shapes.RECTANGLE, { x: x1, y: cy, w: cw, h: ch, fill: { color: SQUID2 }, line: { color: "3A485A", width: 1 } });
  s.addText("WHAT IT TAKES TO DEPLOY", { x: x1 + 0.32, y: cy + 0.22, w: cw - 0.6, h: 0.4, fontFace: F_BOLD, fontSize: 15, bold: true, color: TEAL, charSpacing: 1, align: "left", valign: "middle", margin: 0 });
  s.addText(d.deploySteps.map((b) => ({ text: b, options: { bullet: { type: "number" }, breakLine: true, paraSpaceAfter: 4, color: "E6ECF1" } })), { x: x1 + 0.45, y: cy + 0.72, w: cw - 0.8, h: 2.4, fontFace: F_REG, fontSize: 10.5, color: "E6ECF1", align: "left", valign: "top", lineSpacingMultiple: 1.0, margin: 0 });
  s.addText([
    { text: "Deploy:  ", options: { bold: true, color: ORANGE } },
    { text: d.deployOneLiner, options: { color: "DCE3EA", italic: true } },
  ], { x: x1 + 0.32, y: cy + 3.12, w: cw - 0.62, h: 0.6, fontFace: F_REG, fontSize: 9.5, align: "left", valign: "top", lineSpacingMultiple: 1.0, margin: 0 });
  s.addText(`runbooks/agent-deploy/${d.runbook}  ·  docs/AWS-DEPLOYMENT-REFERENCE.md`, { x: x1 + 0.32, y: cy + ch - 0.4, w: cw - 0.6, h: 0.3, fontFace: F_REG, fontSize: 8.5, italic: true, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
  // takeaway bar
  const by = cy + ch + 0.32, bh = 0.92;
  s.addShape(P.shapes.RECTANGLE, { x: x0, y: by, w: 11.78, h: bh, fill: { color: SQUID3 }, line: { color: "3A485A", width: 1 } });
  s.addText([
    { text: "The takeaway:  ", options: { bold: true, color: ORANGE } },
    { text: "the agent isn't the product — the governed platform that makes it FERPA/ADA-defensible and deployable on AWS is.", options: { color: WHITE } },
  ], { x: x0 + 0.4, y: by, w: 11.0, h: bh, fontFace: F_REG, fontSize: 14, align: "left", valign: "middle", lineSpacingMultiple: 1.03, margin: 0 });
  s.addNotes(d.notes.s6);
}

function buildAgentDeck(P, d) {
  slideTitle(P, d); slideHook(P, d); slideIssueCost(P, d); slidePipeline(P, d); slideArch(P, d); slideProof(P, d);
}

// ============================================================ shared pipeline assurance cards
const stdCards = (consequential) => ([
  { title: "Every action audited", body: "node, timestamp, actor, data sources, model version — append-only and examiner-ready by design." },
  { title: "Grounded & explainable", body: "answers cite approved sources; Bedrock Guardrails mask PII before any model call and bound the output." },
  { title: `AI never decides ${consequential}`, body: "the consequential action is a human-only step, enforced in the orchestration framework — not a policy PDF." },
]);

// ============================================================ AGENT CONTENT
const AGENTS = [
{
  num: "01", name: "Student & Family Services Concierge",
  tagline: "deflect routine inquiries, 24/7 and multilingual — humans own every account action",
  runbook: "01-student-family-concierge.md",
  hero: "FROM HOLD MUSIC TO INSTANT ANSWERS",
  valueProp: "A governed concierge that answers routine status, eligibility, and deadline questions in the family's language — while staff approve every account-touching action and every access is audited.",
  hookStats: [
    { big: "~4M of 5.4M", label: "FAFSA-cycle calls to the federal center went UNANSWERED (2024-25)", tag: "[gov/peer-reviewed — GAO-24-107407]" },
    { big: "75%", label: "fewer financial-aid status emails/calls/visits (Highline College)", tag: "[vendor — AWS]" },
    { big: ">15 min → <30 sec", label: "wait times at similar staffing (UT Austin)", tag: "[vendor — AWS]" },
  ],
  issueBullets: [
    "Families can't self-serve answers; routine status/eligibility/deadline questions crowd out complex casework.",
    "Fixed staff can't cover after-hours and multilingual demand.",
    "Seasonal peaks (FAFSA, registration, move-in) spike contact volume unpredictably.",
    "In the 2024-25 FAFSA cycle ~3 of 4 federal-center calls went unanswered — the sharpest proxy for routine-inquiry overload.",
  ],
  costBig: "~$1.2M–$1.6M / yr",
  costMath: "Modeled: ~120k routine contacts/yr × ~60% deflectable × ~$16 phone/email → self-service cost delta. Self-service resolves at $1–$4 vs. $17–$25 phone.",
  costRisks: [
    "Lost goodwill and enrollment yield when families can't reach anyone at peak.",
    "Staff burnout and turnover absorbing repetitive volume.",
  ],
  costTag: "[modeled — cost-per-contact benchmark × institutional volume]",
  brightLine: "the agent answers and drafts; a named staff member approves every account-touching action, and every record access is audited.",
  pipelineTagline: "Retrieve approved knowledge + the student's own record through a scoped gateway, answer or draft — then stop at a human gate for anything consequential.",
  pipeline: [
    { n: 1, title: "Retrieve KB + record", sub: "policy/KB + student record via gateway-scoped connectors", kind: "auto" },
    { n: 2, title: "Analyze intent & entitlement", sub: "classify the ask; check what this role may see", kind: "auto" },
    { n: 3, title: "Answer / translate / draft", sub: "respond in the family's language or draft a staff reply", kind: "auto" },
    { n: 4, title: "HUMAN GATE", sub: "staff approves account-touching actions; reads stay self-service", kind: "gate" },
    { n: 5, title: "Append-only audit", sub: "every record access logged to immutable store", kind: "audit" },
  ],
  pipelineCards: stdCards("the account action"),
  arch: {
    users: "Students & families (web / chat / voice)",
    sor: "SIS + Financial-Aid system",
    ext: "Amazon Connect / chat channel",
    runtime: [
      { t: "UI task (concierge console)", color: C_COMPUTE },
      { t: "Agent worker + Amazon Translate", color: C_COMPUTE },
      { t: "MCP auth gateway", s: "all outbound tool calls", color: C_INTEG },
    ],
    data: [
      { t: "Aurora / DynamoDB", s: "session + case state", color: C_MODEL },
      { t: "DynamoDB audit", s: "append-only", color: C_INTEG },
      { t: "S3 Object Lock", s: "WORM records", color: C_STORAGE },
      { t: "Secrets Manager", s: "scoped tokens", color: C_STORAGE },
    ],
    legend: "1 student sign-in   2 SAML federation (MFA at IdP; Cognito issues JWT — no credentials in AWS)   3 authenticated session to concierge   4 SIS / financial-aid read over private connectivity   5 demand scales the agent workers   6 model calls stay inside AWS via VPC endpoint   7 every record access & answer persisted to append-only audit   8 connectors reachable only through the governed MCP gateway",
  },
  proofStats: [
    { big: "75%", label: "fewer status emails/calls/visits (Highline College)", tag: "[vendor — AWS]" },
    { big: "<30 sec", label: "wait from >15 min at similar staffing (UT Austin)", tag: "[vendor — AWS]" },
    { big: "$1–$4", label: "self-service contact cost vs. $17–$25 phone", tag: "[sector-press/estimate]" },
    { big: "~$1.2–1.6M", label: "modeled avoidable contact cost/yr addressed", tag: "[modeled]" },
  ],
  deploySteps: [
    "Provision KMS CMK per data class + per-customer VPC / network.",
    "Stand up Cognito SAML→JWT federation with role scoping.",
    "Front with CloudFront + WAF, ALB TLS 1.3.",
    "Deploy the agent + grant tools via the MCP gateway (deny-by-default).",
    "Connect SIS + financial-aid; load approved KB; wire Connect/chat.",
    "Enable S3 Object Lock + append-only audit; run smoke + HITL test.",
  ],
  deployOneLiner: "CloudFormation quick-deploy provisions the isolated environment + gateway + Connect/chat channel; point connectors at SIS and financial-aid; load approved KB.",
  notes: {
    s1: "[00:20] Title. Agent 01 is the land-first motion: visible, low decision-risk, measurable. Position to the CIO as the safest first deployment that proves the shared control plane; to the CFO as a fast, contact-cost ROI. Set up that the whole suite shares one governed AWS platform — this agent is the on-ramp.",
    s2: "[00:45] Hook. Lead with the GAO figure — three of four FAFSA-cycle calls went unanswered — as the strongest (gov) proxy for routine-inquiry overload. The two AWS customer stats are vendor-attributed and shown as such. To the CFO: a contact-cost story. To the CIO: 24/7 multilingual coverage without adding headcount.",
    s3: "[01:10] Issue + cost. Walk the left card as the operational reality, then land the modeled ~$1.2–1.6M/yr avoidable contact cost with the arithmetic visible — defensible, not invented; substitute their real volumes. The bright line is the governance promise: reads are self-serve, account actions need a named human. CISOs care most about this line.",
    s4: "[01:35] Pipeline. Five steps, human gate in red. Emphasize the gate is enforced in the orchestration framework, not a policy document. The three cards are the audit/grounding/never-decides assurances every regulated buyer asks for.",
    s5: "[02:15] Architecture — the most important slide. Trace the eight numbered flow steps. To deploy, the customer must provide: an IdP (Okta/Azure AD/Google), network reachability to SIS + financial-aid (PrivateLink/Direct Connect), approved KB content, and a named approver group. Bedrock + Guardrails are in-VPC and mandatory; PII never egresses after masking.",
    s6: "[02:45] Proof + deploy. Outcomes are documented-at-institution or modeled-at-your-baseline, never guaranteed. Six deploy steps map to the runbook. Close on the takeaway: the governed platform is the product. The customer provides IdP, connectors, KB, and approvers; we provide the FERPA-defensible AWS reference.",
  },
},
{
  num: "02", name: "Personalized Tutor & Study Companion",
  tagline: "24/7 Socratic help grounded in the course's own materials — escalates to a human on distress",
  runbook: "02-tutor-study-companion.md",
  hero: "LEARN 2× AS MUCH, ANY HOUR",
  valueProp: "A governed tutor grounded in the course's own materials that coaches one step at a time — democratizing high-impact tutoring while protecting academic integrity and escalating to a human when a student struggles or is in distress.",
  hookStats: [
    { big: ">2×", label: "more learned, in less time, vs. an active-learning class (Harvard RCT)", tag: "[gov/peer-reviewed]" },
    { big: "$1.2–2.5M+", label: "to match the same support with human tutoring for 1,000 students/yr", tag: "[modeled]" },
    { big: "~0.37 SD", label: "human-tutoring gain — the value ceiling AI helps democratize", tag: "[gov/peer-reviewed]" },
  ],
  issueBullets: [
    "Students need help at scale outside class hours; human tutoring is expensive and access is uneven.",
    "High-impact tutoring runs ~$1,200–$2,500+ per student/year — out of reach for most.",
    "Ungoverned chatbots dump answers and undermine academic integrity.",
    "No scalable way to escalate a struggling or distressed student to a human.",
  ],
  costBig: "~$1.2M–$2.5M+ / yr",
  costMath: "Modeled: 1,000 students × $1,200–$2,500/student/yr for human high-impact tutoring — the recurring spend a fixed-cost AI tutor scales against, or most students get no after-hours help at all.",
  costRisks: [
    "Equity gap: students who can't afford private tutoring fall behind.",
    "Integrity exposure from ungoverned tools used off-platform.",
  ],
  costTag: "[modeled — high-impact-tutoring unit cost × served population]",
  brightLine: "the agent coaches and explains within Guardrails; it never grades, never answer-dumps, and escalates struggle or distress to a named human.",
  pipelineTagline: "Retrieve approved course content, coach one step at a time within Guardrails — escalate to an instructor or counselor when a student struggles or shows distress.",
  pipeline: [
    { n: 1, title: "Retrieve course content", sub: "approved LMS/course materials via Knowledge Base", kind: "auto" },
    { n: 2, title: "Analyze question & level", sub: "gauge the student's intent and mastery", kind: "auto" },
    { n: 3, title: "Socratic step coaching", sub: "one step at a time; Guardrails block answer-dumping", kind: "auto" },
    { n: 4, title: "HUMAN ESCALATION", sub: "distress or repeated struggle routes to instructor/tutor", kind: "gate" },
    { n: 5, title: "Integrity audit", sub: "interactions logged for review", kind: "audit" },
  ],
  pipelineCards: stdCards("grades or answers"),
  arch: {
    users: "Students (course portal / LMS)",
    sor: "LMS / content (Canvas etc.)",
    ext: "Course materials → Knowledge Base",
    runtime: [
      { t: "UI task (study console)", color: C_COMPUTE },
      { t: "Tutor agent + AgentCore memory", s: "retention-bounded", color: C_COMPUTE },
      { t: "MCP auth gateway", s: "all outbound tool calls", color: C_INTEG },
    ],
    data: [
      { t: "Bedrock Knowledge Base", s: "course materials (RAG)", color: C_MODEL },
      { t: "DynamoDB audit", s: "append-only", color: C_INTEG },
      { t: "S3 Object Lock", s: "WORM logs", color: C_STORAGE },
      { t: "Secrets Manager", s: "scoped tokens", color: C_STORAGE },
    ],
    legend: "1 student sign-in   2 SAML federation (MFA at IdP; Cognito issues JWT)   3 authenticated session to study console   4 course materials retrieved from the Knowledge Base   5 demand scales the tutor workers   6 Socratic coaching via Bedrock + Guardrails inside the VPC   7 integrity-review interactions persisted to append-only audit   8 LMS reachable only through the governed MCP gateway",
  },
  proofStats: [
    { big: ">2×", label: "more learned in less time (Harvard physics RCT)", tag: "[gov/peer-reviewed]" },
    { big: "~0.37 SD", label: "human-tutoring gain AI helps democratize", tag: "[gov/peer-reviewed]" },
    { big: "~⅓", label: "tutoring-cost reduction from tech substitution", tag: "[gov/peer-reviewed]" },
    { big: "24/7", label: "grounded, equitable access at fixed cost", tag: "[design]" },
  ],
  deploySteps: [
    "Provision KMS CMK per data class + per-customer VPC / network.",
    "Stand up Cognito SAML→JWT federation with role scoping.",
    "Front with CloudFront + WAF, ALB TLS 1.3.",
    "Deploy the tutor agent + grant tools via the MCP gateway.",
    "Connect the LMS; index course materials into a Knowledge Base.",
    "Set integrity Guardrails + memory-retention boundaries; smoke test escalation.",
  ],
  deployOneLiner: "Quick-deploy environment + gateway; connect LMS, index course materials into a Knowledge Base, set integrity guardrails and memory-retention boundaries.",
  notes: {
    s1: "[00:20] Title. Agent 02 is higher-governance — sequence it after the control plane is proven by 01/03/07/08. Position to the CIO as integrity-bounded, not a free-for-all chatbot; to the CFO as the scalable alternative to per-student tutoring spend.",
    s2: "[00:45] Hook. Lead with the Harvard RCT (gov/peer-reviewed): >2× learning in less time. The $1.2–2.5M is the modeled human-tutoring substitution cost for 1,000 students. Present as documented-at-study, modeled-at-your-baseline.",
    s3: "[01:10] Issue + cost. The cost-of-nothing is either large recurring tutoring spend or an equity gap where most students get no help. Bright line: the tutor coaches, never grades, never dumps answers, and escalates distress.",
    s4: "[01:35] Pipeline. Note step 4 is a human ESCALATION, not an approval gate — distress or repeated struggle routes to a counselor/instructor. Integrity audit supports academic-integrity review.",
    s5: "[02:15] Architecture. To deploy, the customer provides: IdP, LMS connectivity, and the approved course corpus to index. AgentCore memory is retention-bounded; PII is masked before any model call. Guardrails enforce Socratic, no-answer-dumping behavior in-VPC.",
    s6: "[02:45] Proof + deploy. Outcomes are documented at the Harvard study or modeled at the customer baseline. Close on governance as the product: integrity guardrails + escalation are what make an AI tutor defensible to a provost.",
  },
},
{
  num: "03", name: "Educator Copilot",
  tagline: "first-draft lessons, rubrics, quizzes & differentiation in minutes — the educator edits and owns every output",
  runbook: "03-educator-copilot.md",
  hero: "RECLAIM THE 9-HOUR WEEK",
  valueProp: "A governed copilot that drafts standards-aligned lessons, rubrics, quizzes, and differentiated variants in minutes — on-template and educator-owned, with nothing published unedited.",
  hookStats: [
    { big: "~53 hrs/wk", label: "teachers work vs. 44 for comparable adults — a 9-hr gap (RAND 2024)", tag: "[gov/peer-reviewed — RAND]" },
    { big: "~5.9 hrs/wk", label: "saved by teachers using AI weekly (~6 weeks/yr)", tag: "[foundation/research]" },
    { big: "$11.9K–24.9K", label: "to replace one burned-out teacher (~$2.2B/yr nationally)", tag: "[foundation/research — LPI]" },
  ],
  issueBullets: [
    "Teachers work ~53 hrs/week (vs. 44 for peers) on only ~4.4 hrs of planning time.",
    "Hours lost to prep, differentiation, rubric-building, and LMS navigation.",
    "Workload is a named burnout driver; turnover costs $11,860–$24,930 per teacher.",
    "Standards alignment and template consistency are manual and slow.",
  ],
  costBig: "~$11.9K–$24.9K / teacher",
  costMath: "Direct (LPI 2024): replacing one burned-out teacher costs $11,860 (small) to $24,930 (large districts) — ~$2.2B/yr nationally. Inaction keeps paying this recurring bill.",
  costRisks: [
    "Recurring turnover and rehire cost driven by workload burnout.",
    "Lost instructional quality when prep time is squeezed.",
  ],
  costTag: "[foundation/research — Learning Policy Institute 2024]",
  brightLine: "the agent drafts standards-aligned materials; the educator reviews, edits, and owns every output — nothing publishes unedited.",
  pipelineTagline: "Retrieve standards + approved curriculum, draft lessons/rubrics/quizzes and differentiated variants — the educator approves before anything publishes.",
  pipeline: [
    { n: 1, title: "Retrieve standards + curriculum", sub: "approved standards/templates via Knowledge Base", kind: "auto" },
    { n: 2, title: "Analyze educator intent", sub: "grade, standard, level, differentiation need", kind: "auto" },
    { n: 3, title: "Draft + differentiate", sub: "lesson / rubric / quiz + variants, on-template", kind: "auto" },
    { n: 4, title: "EDUCATOR APPROVES", sub: "reviews & edits; nothing publishes unedited", kind: "gate" },
    { n: 5, title: "Audit drafts & approvals", sub: "every draft + approval logged", kind: "audit" },
  ],
  pipelineCards: stdCards("what students see"),
  arch: {
    users: "Educators (web / LMS)",
    sor: "LMS (publish-on-approval)",
    ext: "Standards / curriculum → Knowledge Base",
    runtime: [
      { t: "UI task (copilot console)", color: C_COMPUTE },
      { t: "Drafting agent + templating", color: C_COMPUTE },
      { t: "MCP auth gateway", s: "all outbound tool calls", color: C_INTEG },
    ],
    data: [
      { t: "Bedrock Knowledge Base", s: "standards + curriculum", color: C_MODEL },
      { t: "DynamoDB audit", s: "append-only", color: C_INTEG },
      { t: "S3 Object Lock", s: "drafts (WORM)", color: C_STORAGE },
      { t: "Secrets Manager", s: "scoped tokens", color: C_STORAGE },
    ],
    legend: "1 educator sign-in   2 SAML federation (MFA at IdP; Cognito issues JWT)   3 authenticated session to copilot   4 standards/curriculum retrieved from the Knowledge Base   5 drafting workers scale with demand   6 drafting via Bedrock + Guardrails inside the VPC   7 drafts & approvals persisted to append-only audit   8 LMS publish reachable only through the governed MCP gateway (on approval)",
  },
  proofStats: [
    { big: "9 hrs/wk", label: "above-peer workload targeted (RAND)", tag: "[gov/peer-reviewed]" },
    { big: "~5.9 hrs/wk", label: "saved weekly with AI (~6 wks/yr)", tag: "[foundation/research]" },
    { big: "$11.9–24.9K", label: "avoided turnover cost per retained teacher", tag: "[foundation/research]" },
    { big: "in prod", label: "Vanderbilt 'Amplify' runs lesson-plan agents", tag: "[vendor]" },
  ],
  deploySteps: [
    "Provision KMS CMK per data class + per-customer VPC / network.",
    "Stand up Cognito SAML→JWT federation with role scoping.",
    "Front with CloudFront + WAF, ALB TLS 1.3.",
    "Deploy the copilot agent + grant tools via the MCP gateway.",
    "Index standards/curriculum/templates into a Knowledge Base.",
    "Connect the LMS for publish-on-approval; enable audit + smoke test.",
  ],
  deployOneLiner: "Quick-deploy + gateway; index standards/curriculum/templates into a Knowledge Base; connect the LMS for publish-on-approval.",
  notes: {
    s1: "[00:20] Title. Agent 03 is a strong land-first companion to 01 — high visibility, low decision-risk, and a direct line to the teacher-time and turnover story. Position to the CFO via turnover cost; to the CIO as educator-owned output with full audit.",
    s2: "[00:45] Hook. Lead with RAND's 53-vs-44-hour gap (gov/peer-reviewed). The Walton-Gallup 5.9 hrs/week and LPI turnover cost are foundation/research. Frame the AI as giving teachers their week back, not replacing their judgment.",
    s3: "[01:10] Issue + cost. This agent uses a DIRECT cost figure (LPI turnover) rather than a model — call that out as a strength. Bright line: educator reviews, edits, and owns; nothing publishes unedited.",
    s4: "[01:35] Pipeline. The gate is the educator approval — students never see unedited AI output. Standards grounding via Knowledge Base keeps drafts aligned.",
    s5: "[02:15] Architecture. Customer provides: IdP, LMS connectivity, and the standards/curriculum/template corpus. Publish-to-LMS happens only on approval, through the governed gateway. Bedrock + Guardrails in-VPC.",
    s6: "[02:45] Proof + deploy. Vanderbilt Amplify is the vendor proof that this pattern runs in production. Close on the platform-as-product takeaway and the runbook pointer.",
  },
},
{
  num: "04", name: "Assessment, Grading & Feedback",
  tagline: "draft score + rationale against the approved rubric — the instructor stays grader of record",
  runbook: "04-assessment-grading-feedback.md",
  hero: "FEEDBACK IN HOURS, NOT WEEKS",
  valueProp: "A governed grading assistant that drafts a score and targeted feedback against the approved rubric — consistently and fast — while the instructor reviews and overrides every grade. No autonomous grades, ever.",
  hookStats: [
    { big: "~9.9 hrs/wk", label: "teachers spend grading; 95% take it home (2025 survey)", tag: "[sector-press — flag on slide]" },
    { big: "comparable", label: "AI-assisted vs. human grading, faster turnaround (RCTs)", tag: "[gov/peer-reviewed]" },
    { big: "~$4,270/yr", label: "recoverable grading labor per instructor (modeled)", tag: "[modeled]" },
  ],
  issueBullets: [
    "Grading and feedback are slow and inconsistent, especially in large/online sections.",
    "Teachers spend ~9.9 hrs/week grading; 95% take it home; ~62% call it one of the worst parts of the job.",
    "Delayed feedback is the feedback students need most, lost.",
    "An estimated ~40% of teaching time goes to grading (estimate — flag on slide).",
  ],
  costBig: "~$4,270 / instructor / yr",
  costMath: "Modeled: ~356 grading hrs/yr × 30% reduction × ~$40/hr loaded ≈ $4,270/instructor — scaled across faculty, plus grading-driven attrition risk.",
  costRisks: [
    "Grading-driven burnout and attrition (~1 in 3 considered leaving over it).",
    "Inconsistent rubric application creates fairness and appeal exposure.",
  ],
  costTag: "[modeled — grading hours × reduction × loaded rate]",
  brightLine: "the agent drafts a score and rationale; the instructor reviews and overrides every grade before any write-back — the human is the grader of record.",
  pipelineTagline: "Retrieve the approved rubric, draft a score and targeted feedback — then stop at a mandatory instructor gate before any grade reaches the gradebook.",
  pipeline: [
    { n: 1, title: "Retrieve rubric + context", sub: "approved rubric + assignment via Knowledge Base", kind: "auto" },
    { n: 2, title: "Analyze submission", sub: "score against each rubric criterion", kind: "auto" },
    { n: 3, title: "Draft score + feedback", sub: "targeted, criterion-linked rationale", kind: "auto" },
    { n: 4, title: "INSTRUCTOR GATE", sub: "reviews/overrides every grade — mandatory (waitForTaskToken)", kind: "gate" },
    { n: 5, title: "Audit + gradebook write", sub: "draft, override, final grade all logged", kind: "audit" },
  ],
  pipelineCards: stdCards("the grade"),
  arch: {
    users: "Instructors (LMS / gradebook)",
    sor: "LMS gradebook",
    ext: "Rubrics → Knowledge Base",
    runtime: [
      { t: "UI task (grading console)", color: C_COMPUTE },
      { t: "Grading agent", color: C_COMPUTE },
      { t: "Step Functions HITL", s: "waitForTaskToken gate", color: C_INTEG },
      { t: "MCP auth gateway", s: "all outbound tool calls", color: C_INTEG },
    ],
    data: [
      { t: "Bedrock Knowledge Base", s: "rubrics", color: C_MODEL },
      { t: "DynamoDB audit", s: "draft+override+final", color: C_INTEG },
      { t: "S3 Object Lock", s: "WORM", color: C_STORAGE },
      { t: "Secrets Manager", s: "scoped tokens", color: C_STORAGE },
    ],
    legend: "1 instructor sign-in   2 SAML federation (MFA at IdP; Cognito issues JWT)   3 authenticated session to grading console   4 rubric retrieved from the Knowledge Base   5 grading workers scale with submission volume   6 draft scoring via Bedrock + Guardrails inside the VPC   7 Step Functions holds at the instructor gate; draft/override/final persisted to append-only audit   8 gradebook write reachable only through the governed MCP gateway (after approval)",
  },
  proofStats: [
    { big: "comparable", label: "AI vs. human grading, faster turnaround (RCTs, ~300 students)", tag: "[gov/peer-reviewed]" },
    { big: "~$4,270/yr", label: "recoverable grading labor per instructor (modeled)", tag: "[modeled]" },
    { big: "faster", label: "feedback to students, esp. large/online sections", tag: "[gov/peer-reviewed]" },
    { big: "0", label: "autonomous grades — instructor is grader of record", tag: "[design]" },
  ],
  deploySteps: [
    "Provision KMS CMK per data class + per-customer VPC / network.",
    "Stand up Cognito SAML→JWT federation with role scoping.",
    "Front with CloudFront + WAF, ALB TLS 1.3.",
    "Deploy the grading agent + Step Functions waitForTaskToken HITL gate.",
    "Connect the LMS gradebook; load rubrics into a Knowledge Base.",
    "Enable the mandatory approval gate before any grade write-back; smoke test.",
  ],
  deployOneLiner: "Quick-deploy + gateway; connect LMS gradebook, load rubrics, enable the mandatory instructor-approval gate before any grade write-back.",
  notes: {
    s1: "[00:20] Title. Agent 04 is higher-governance — the human gate is non-negotiable. Position to the CISO/provost: no autonomous grades, mandatory instructor override, full audit of draft/override/final. Sequence after the control plane is proven.",
    s2: "[00:45] Hook. Lead with the peer-reviewed RCT (comparable to human, faster) over the vendor 80% marking-speed claim. The 9.9 hrs/week is a vendor-commissioned survey — flag it. The $4,270 is modeled; show arithmetic.",
    s3: "[01:10] Issue + cost. Modeled recoverable grading labor plus attrition risk. The ~40%-of-teaching-time figure is an estimate — flag it. Bright line: instructor is grader of record; the gate is mandatory and enforced by Step Functions.",
    s4: "[01:35] Pipeline. Step 4 uses Step Functions waitForTaskToken — a hard stop the workflow cannot pass autonomously. Audit captures the draft, the override, and the final grade — examiner- and appeal-ready.",
    s5: "[02:15] Architecture. Note the Step Functions HITL box in the runtime tier. Customer provides: IdP, LMS gradebook connectivity, and approved rubrics. Gradebook write-back occurs only after approval, through the gateway.",
    s6: "[02:45] Proof + deploy. Lead with the RCT proof. The zero-autonomous-grades stat is the governance headline. Close on platform-as-product and the runbook pointer.",
  },
},
{
  num: "05", name: "Student Success & Proactive Engagement",
  tagline: "surface at-risk signals early and draft the nudge — an advisor approves every intervention",
  runbook: "05-student-success-engagement.md",
  hero: "ACT BEFORE THEY WITHDRAW",
  valueProp: "A governed early-alert agent that surfaces at-risk signals across SIS/LMS and drafts a timely, personalized nudge — an advisor approves every intervention, protecting both the student and recurring tuition revenue.",
  hookStats: [
    { big: "22.4%", label: "of first-year students don't return for year two (NSC 2025)", tag: "[gov/peer-reviewed — NSC]" },
    { big: "~$5.6M/yr", label: "forgone recurring tuition from preventable non-return (modeled)", tag: "[modeled]" },
    { big: "~$560K/yr", label: "recovered by cutting avoidable non-return just 1-in-10", tag: "[modeled]" },
  ],
  issueBullets: [
    "Warning signs accumulate across SIS/LMS before anyone acts — usually after withdrawal.",
    "22.4% of first-year students don't return for year two; community colleges retain far less.",
    "Each lost student forfeits recurring tuition plus sunk recruitment cost ($457–$2,433).",
    "Advisors can't manually watch every signal for every student.",
  ],
  costBig: "~$5.6M / yr",
  costMath: "Modeled: 2,500 first-years × 22.4% non-return = ~560 lost × ~$10k net tuition/yr. Even a 1-in-10 reduction recovers ~$560K/yr, before recruitment sunk cost.",
  costRisks: [
    "Recurring tuition revenue lost to preventable attrition.",
    "Wasted recruitment investment per non-returning student.",
  ],
  costTag: "[modeled — non-return rate × net tuition × headcount]",
  brightLine: "the agent flags risk and drafts the outreach; an advisor approves every intervention — who is contacted, and why, is a human decision and is audited.",
  pipelineTagline: "Event-driven: a risk signal triggers a scoped read and an approved risk model, the agent drafts a nudge — an advisor approves before any outreach.",
  pipeline: [
    { n: 1, title: "Signal → EventBridge", sub: "attendance/grade/engagement event triggers the flow", kind: "auto" },
    { n: 2, title: "Scoped read + analyze", sub: "SIS/LMS read via gateway; score on approved model", kind: "auto" },
    { n: 3, title: "Draft the nudge", sub: "personalized, timely outreach recommendation", kind: "auto" },
    { n: 4, title: "ADVISOR APPROVES", sub: "approves the intervention (waitForTaskToken)", kind: "gate" },
    { n: 5, title: "Outreach + audit", sub: "who was flagged, contacted, and why — logged", kind: "audit" },
  ],
  pipelineCards: stdCards("who to contact"),
  arch: {
    users: "Advisors / success staff",
    sor: "SIS + LMS",
    ext: "Risk model (Bedrock / SageMaker)",
    runtime: [
      { t: "EventBridge + SQS", s: "event-driven triggers", color: C_INTEG },
      { t: "Success agent + risk scoring", color: C_COMPUTE },
      { t: "Step Functions HITL", s: "advisor approval gate", color: C_INTEG },
      { t: "MCP auth gateway", s: "all outbound tool calls", color: C_INTEG },
    ],
    data: [
      { t: "Aurora / DynamoDB", s: "risk + case state", color: C_MODEL },
      { t: "DynamoDB audit", s: "flagged/contacted/why", color: C_INTEG },
      { t: "S3 Object Lock", s: "WORM", color: C_STORAGE },
      { t: "Secrets Manager", s: "scoped tokens", color: C_STORAGE },
    ],
    legend: "1 advisor sign-in   2 SAML federation (MFA at IdP; Cognito issues JWT)   3 authenticated session to success console   4 SIS/LMS signals read over private connectivity   5 EventBridge + SQS drive event-driven scaling   6 risk analysis + draft via Bedrock + Guardrails inside the VPC   7 Step Functions holds at the advisor gate; flagged/contacted/why persisted to append-only audit   8 systems-of-record reachable only through the governed MCP gateway",
  },
  proofStats: [
    { big: "22.4%", label: "first-year non-return rate targeted (NSC 2025)", tag: "[gov/peer-reviewed]" },
    { big: "~$5.6M/yr", label: "forgone tuition modeled at reference institution", tag: "[modeled]" },
    { big: "lower", label: "withdrawal + higher grades with early alerts (CCRC)", tag: "[gov/peer-reviewed]" },
    { big: "~$560K/yr", label: "recovered at a 1-in-10 reduction", tag: "[modeled]" },
  ],
  deploySteps: [
    "Provision KMS CMK per data class + per-customer VPC / network.",
    "Stand up Cognito SAML→JWT federation with role scoping.",
    "Front with CloudFront + WAF, ALB TLS 1.3.",
    "Deploy the success agent + Step Functions advisor-approval gate.",
    "Connect SIS/LMS; configure the approved risk model; wire EventBridge triggers.",
    "Enable S3 Object Lock + audit of flagged/contacted/why; smoke test.",
  ],
  deployOneLiner: "Quick-deploy + gateway; connect SIS/LMS, configure the approved risk model and advisor-approval gate, wire EventBridge triggers.",
  notes: {
    s1: "[00:20] Title. Agent 05 is the clearest CFO story in the suite — retained tuition. It is also higher-governance (who gets contacted, and why, is consequential). Position to the CFO via the ~$5.6M model; to the CISO via the advisor gate and audit of every flag.",
    s2: "[00:45] Hook. Lead with NSC's 22.4% non-return (gov/peer-reviewed). The $5.6M and $560K are modeled — show arithmetic and stress they substitute the customer's own headcount and net tuition.",
    s3: "[01:10] Issue + cost. This is the revenue-protection agent. The cost-of-nothing is forgone recurring tuition. Bright line: the agent flags and drafts; an advisor decides who is contacted and why — and it's all audited (important for equity/fairness review).",
    s4: "[01:35] Pipeline. This is the event-driven agent — note EventBridge step 1 and SQS scaling. The advisor approval gate is enforced by Step Functions waitForTaskToken. Audit records who was flagged, contacted, and why.",
    s5: "[02:15] Architecture. Highlight EventBridge + SQS in the runtime tier — this is the one event-driven design. Customer provides: IdP, SIS/LMS connectivity, and an approved risk model. No autonomous outreach.",
    s6: "[02:45] Proof + deploy. CCRC early-alert evidence supports the intervention model. Close on revenue protection plus governance: every flag and contact is auditable for fairness review.",
  },
},
{
  num: "06", name: "Pathway Navigator",
  tagline: "plain-language degree audits and transfer-credit mapping — an advisor verifies every plan",
  runbook: "06-pathway-navigator.md",
  hero: "STOP LOSING 43% OF CREDITS",
  valueProp: "A governed navigator that produces plain-language degree audits and transfer-credit mapping against catalog and articulation rules — keeping students on a guided pathway while an advisor verifies every consequential plan.",
  hookStats: [
    { big: "~43%", label: "of credits lost on average when students transfer (~a semester)", tag: "[gov/peer-reviewed — GAO/CHEPP]" },
    { big: "$13K–$26K", label: "added cost per transfer student from lost credits (4-yr)", tag: "[foundation/research — CHEPP]" },
    { big: "4–6 wks → 1 day", label: "credential evaluation at Illinois Tech on AWS", tag: "[vendor]" },
  ],
  issueBullets: [
    "Degree and transfer rules are complex; advisors are overloaded (~441 students/advisor at 2-yr).",
    "Transferring students lose ~43% of credits on average; 1 in 7 lose all of them.",
    "Lost credits lengthen time-to-degree and inflate cost-of-attendance.",
    "Manual credential evaluation is slow — weeks per student.",
  ],
  costBig: "~$13,081–$26,396 / student",
  costMath: "Direct (CHEPP 2024): added cost-of-attendance from lost credits — $13,081 public 4-yr / $26,396 private 4-yr — plus ~$15,400 in lost wages per 3-month graduation delay.",
  costRisks: [
    "Depressed transfer enrollment and completion for the institution.",
    "Added student debt ($2,742–$5,543) and longer time-to-degree.",
  ],
  costTag: "[foundation/research — CHEPP 2024, direct]",
  brightLine: "the agent audits and recommends next-best courses; an advisor verifies before any plan is finalized — consequential planning stays a human decision.",
  pipelineTagline: "Retrieve degree requirements + the student's transcript, analyze against articulation rules, recommend next-best courses — an advisor verifies before the plan is finalized.",
  pipeline: [
    { n: 1, title: "Retrieve transcript + rules", sub: "degree requirements + student record via gateway", kind: "auto" },
    { n: 2, title: "Analyze vs. catalog rules", sub: "map against articulation / catalog rules", kind: "auto" },
    { n: 3, title: "Recommend + flag gaps", sub: "next-best courses; flag credit gaps", kind: "auto" },
    { n: 4, title: "ADVISOR VERIFIES", sub: "verifies before the plan is finalized (waitForTaskToken)", kind: "gate" },
    { n: 5, title: "Audit the audit", sub: "every degree audit + plan logged", kind: "audit" },
  ],
  pipelineCards: stdCards("the degree plan"),
  arch: {
    users: "Students & advisors",
    sor: "SIS / degree-audit + articulation",
    ext: "Catalog / articulation rules → KB",
    runtime: [
      { t: "UI task (pathway console)", color: C_COMPUTE },
      { t: "Navigator agent", color: C_COMPUTE },
      { t: "Step Functions HITL", s: "advisor verify gate", color: C_INTEG },
      { t: "MCP auth gateway", s: "all outbound tool calls", color: C_INTEG },
    ],
    data: [
      { t: "Bedrock Knowledge Base", s: "catalog + articulation", color: C_MODEL },
      { t: "DynamoDB audit", s: "audits + plans", color: C_INTEG },
      { t: "S3 Object Lock", s: "WORM", color: C_STORAGE },
      { t: "Secrets Manager", s: "scoped tokens", color: C_STORAGE },
    ],
    legend: "1 student/advisor sign-in   2 SAML federation (MFA at IdP; Cognito issues JWT)   3 authenticated session to pathway console   4 transcript + degree-audit rules read over private connectivity   5 planning workers scale with demand   6 audit + recommendation via Bedrock + Guardrails inside the VPC   7 Step Functions holds at the advisor verify gate; every audit/plan persisted to append-only store   8 SIS/degree-audit reachable only through the governed MCP gateway",
  },
  proofStats: [
    { big: "~43%", label: "credit-loss problem directly targeted (GAO/CHEPP)", tag: "[gov/peer-reviewed]" },
    { big: "$13K–$26K", label: "per-student added cost reduced when credits transfer", tag: "[foundation/research]" },
    { big: "4–6wk→1d", label: "credential evaluation (Illinois Tech on AWS)", tag: "[vendor]" },
    { big: "2.5×", label: "more likely to graduate with >90% of credits accepted", tag: "[foundation/research]" },
  ],
  deploySteps: [
    "Provision KMS CMK per data class + per-customer VPC / network.",
    "Stand up Cognito SAML→JWT federation with role scoping.",
    "Front with CloudFront + WAF, ALB TLS 1.3.",
    "Deploy the navigator agent + Step Functions advisor-verify gate.",
    "Connect SIS/degree-audit; index catalog + articulation rules.",
    "Enable advisor verification gate + audit; smoke test.",
  ],
  deployOneLiner: "Quick-deploy + gateway; connect SIS/degree-audit, index catalog and articulation rules, enable advisor verification gate.",
  notes: {
    s1: "[00:20] Title. Agent 06 is higher-governance — degree planning is consequential. Position to the CFO via transfer-credit cost and completion; to the provost via advisor-verified plans and full audit. Sequence after the control plane is proven.",
    s2: "[00:45] Hook. Lead with the ~43% credit-loss figure (GAO, restated in CHEPP) — flag the GAO year. The $13K–$26K is foundation/research (CHEPP, direct). Illinois Tech 4-6wk→1day is vendor-attributed.",
    s3: "[01:10] Issue + cost. Uses a DIRECT per-student cost (CHEPP) — a strength. Bright line: advisor verifies before any plan is finalized; consequential planning is a human decision.",
    s4: "[01:35] Pipeline. Advisor verify gate via Step Functions. 'Audit the audit' means the degree audit itself is logged and reproducible — important for appeals and accreditation.",
    s5: "[02:15] Architecture. Customer provides: IdP, SIS/degree-audit connectivity, and catalog/articulation rules to index. Plans finalize only after advisor verification, through the gateway.",
    s6: "[02:45] Proof + deploy. The 2.5x graduation likelihood and Illinois Tech speed-up are the proof points. Close on platform-as-product and the runbook pointer.",
  },
},
{
  num: "07", name: "Document & Accessibility Services",
  tagline: "Textract intake, WCAG 2.1 AA remediation and multilingual output — staff sign off on accessibility",
  runbook: "07-document-accessibility-services.md",
  hero: "BEAT THE 2027 ADA DEADLINE",
  valueProp: "A governed document pipeline that extracts, classifies, and remediates content to WCAG 2.1 AA at scale — with multilingual output and a staff accessibility sign-off — directly addressing the ADA Title II deadline and PDF-dominated complaint risk.",
  hookStats: [
    { big: "Apr 26 2027", label: "ADA Title II WCAG 2.1 AA deadline (≥50k pop.) / 2028 smaller", tag: "[gov/peer-reviewed]" },
    { big: "~95%", label: "of accessibility complaints involve PDFs", tag: "[sector-press]" },
    { big: "4–6 wks → 1 day", label: "transcript/credential evaluation (Illinois Tech on AWS)", tag: "[vendor]" },
  ],
  issueBullets: [
    "Enrollment is document-heavy (transcripts, aid docs) with error and turnaround pressure.",
    "ADA Title II (WCAG 2.1 AA) hits April 26 2027 (≥50k) / 2028 (smaller) — now legally enforced.",
    "~95% of accessibility complaints involve inaccessible PDFs — the artifact offices generate at volume.",
    "Multilingual document handling is manual and slow.",
  ],
  costBig: "$30K–$815K exposure",
  costMath: "Hard non-compliance exposure: settlements avg ~$30k · judgments ~$85k · class actions ~$400k; one institution-scale remediation program ran $665k–$815k. Plus federal-funding conditions.",
  costRisks: [
    "A single campaign drove 2,400+ OCR complaints / 1,000+ resolution agreements.",
    "Federal-funding conditions tied to Title II compliance.",
  ],
  costTag: "[sector-press settlement ranges, flag on slide; gov deadlines]",
  brightLine: "the agent extracts, remediates, and translates; staff sign off on consequential records and accessibility — the human owns the compliance attestation, and every document is audited.",
  pipelineTagline: "Ingest and Textract-extract, detect accessibility gaps, draft remediated and translated output — staff sign off on accessibility before any record is released.",
  pipeline: [
    { n: 1, title: "Ingest + Textract extract", sub: "document in → S3 → Textract OCR/extract", kind: "auto" },
    { n: 2, title: "Classify + detect gaps", sub: "classify; detect WCAG 2.1 AA accessibility gaps", kind: "auto" },
    { n: 3, title: "Remediate + translate", sub: "draft structured output (+ Amazon Translate)", kind: "auto" },
    { n: 4, title: "STAFF SIGN-OFF", sub: "staff reviews consequential records + accessibility", kind: "gate" },
    { n: 5, title: "Audit every document", sub: "every document touched is logged", kind: "audit" },
  ],
  pipelineCards: stdCards("the compliance attestation"),
  arch: {
    users: "Enrollment / accessibility staff",
    sor: "SIS / CRM",
    ext: "Documents (transcripts, aid docs)",
    runtime: [
      { t: "Amazon Textract", s: "extract", color: C_INTEG },
      { t: "IDP agent + Amazon Translate", color: C_COMPUTE },
      { t: "MCP auth gateway", s: "all outbound tool calls", color: C_INTEG },
    ],
    data: [
      { t: "S3 (intake)", s: "documents in", color: C_STORAGE },
      { t: "DynamoDB audit", s: "every doc touched", color: C_INTEG },
      { t: "S3 Object Lock", s: "remediated (WORM)", color: C_STORAGE },
      { t: "Secrets Manager", s: "scoped tokens", color: C_STORAGE },
    ],
    legend: "1 staff sign-in   2 SAML federation (MFA at IdP; Cognito issues JWT)   3 authenticated session to document console   4 documents land in S3; SIS/CRM read over private connectivity   5 IDP workers scale with intake volume   6 Textract extract + Bedrock/Guardrails classify & remediate (+ Translate) inside the VPC   7 every document touched persisted to append-only audit   8 SIS/CRM reachable only through the governed MCP gateway (write on sign-off)",
  },
  proofStats: [
    { big: "4–6wk→1d", label: "transcript/credential eval (Illinois Tech)", tag: "[vendor]" },
    { big: "open-sourced", label: "automated PDF remediation (Ohio State)", tag: "[vendor]" },
    { big: "2027/2028", label: "WCAG 2.1 AA deadlines directly addressed", tag: "[gov/peer-reviewed]" },
    { big: "~95%", label: "PDF-dominated complaint risk mitigated", tag: "[sector-press]" },
  ],
  deploySteps: [
    "Provision KMS CMK per data class + per-customer VPC / network.",
    "Stand up Cognito SAML→JWT federation with role scoping.",
    "Front with CloudFront + WAF, ALB TLS 1.3.",
    "Deploy the IDP agent + wire the Textract/IDP pipeline + gateway grants.",
    "Connect SIS/CRM; enable Amazon Translate.",
    "Enable the staff accessibility-approval gate + S3 WORM audit; smoke test.",
  ],
  deployOneLiner: "Quick-deploy + gateway; wire the Textract/IDP pipeline, connect SIS/CRM, enable Translate and the staff accessibility-approval gate.",
  notes: {
    s1: "[00:20] Title. Agent 07 is land-first — visible, low decision-risk, and tied to a hard regulatory deadline. Position to the CIO/general counsel via ADA Title II; to the CFO via litigation/remediation exposure avoided.",
    s2: "[00:45] Hook. Lead with the gov deadline (Apr 26 2027) and the ~95%-PDF complaint figure (sector-press — flag). Illinois Tech speed-up is vendor-attributed. This is the compliance-clock agent.",
    s3: "[01:10] Issue + cost. The cost-of-nothing is hard litigation/remediation exposure — flag the settlement ranges as industry-tracker estimates. Bright line: staff own the accessibility attestation; the human signs off, the agent does the heavy lifting.",
    s4: "[01:35] Pipeline. Note Textract at step 1 and Translate at step 3 — agent-specific AWS blocks. Staff sign-off is the gate; every document touched is audited.",
    s5: "[02:15] Architecture. Highlight Amazon Textract and Amazon Translate as the agent-specific services. Customer provides: IdP, SIS/CRM connectivity, and the document streams. Remediated output is WORM-stored; records write only on staff sign-off.",
    s6: "[02:45] Proof + deploy. Ohio State (open-sourced) and Illinois Tech are the vendor proofs. The deadline itself is the urgency. Close on platform-as-product and the runbook pointer.",
  },
},
{
  num: "08", name: "Operations / IT Service Desk",
  tagline: "deflect repetitive tickets, ground answers in approved runbooks — humans gate privileged actions",
  runbook: "08-operations-service-desk.md",
  hero: "DEFLECT THE TICKET FLOOD",
  valueProp: "A governed service-desk agent that resolves high-volume, self-serviceable tickets from approved runbooks — auto-resolving low-risk requests and escalating any privileged or account-changing action to a human, all audited.",
  hookStats: [
    { big: "20–50%", label: "of help-desk calls are password issues (~$70/reset loaded)", tag: "[sector-press — flag on slide]" },
    { big: "~$300K/yr", label: "deflectable-ticket cost at a 50k-ticket institution (modeled)", tag: "[modeled]" },
    { big: "45%+", label: "of queries AI can deflect (vendor-cited)", tag: "[sector-press/estimate]" },
  ],
  issueBullets: [
    "Small IT/admin teams drown in repetitive tickets (password/access, how-to, status).",
    "Education cost per ticket is ~$6–$12; password resets alone cost ~$70 each in labor.",
    "Real incidents wait while staff handle self-resolvable volume.",
    "Knowledge is scattered; answers are inconsistent across agents.",
  ],
  costBig: "~$300K / yr",
  costMath: "Modeled: 50,000 tickets × ~30% deflectable × ~$20 agent → self-service delta. Self-service resolves at $1–$4 vs. $17–$25 phone; password resets add ~$70 each where not automated.",
  costRisks: [
    "Slow response to genuine incidents while volume backs up.",
    "Staff burnout on repetitive, low-value tickets.",
  ],
  costTag: "[modeled — ticket volume × deflectable share × cost delta]",
  brightLine: "the agent resolves and drafts from approved runbooks; low-risk resets auto-resolve, but any privileged or account-changing action stops at a human gate — and every action is audited.",
  pipelineTagline: "Retrieve approved runbooks, resolve self-service or draft the action — low-risk resets auto-resolve; privileged actions stop at a human gate.",
  pipeline: [
    { n: 1, title: "Retrieve runbooks/KB", sub: "approved IT KB + runbooks via Knowledge Base", kind: "auto" },
    { n: 2, title: "Analyze ticket intent", sub: "classify the request and its risk level", kind: "auto" },
    { n: 3, title: "Resolve / draft action", sub: "self-service answer or automated action draft", kind: "auto" },
    { n: 4, title: "HUMAN GATE", sub: "privileged actions escalate; low-risk resets auto", kind: "gate" },
    { n: 5, title: "Audit every action", sub: "every resolution and action logged", kind: "audit" },
  ],
  pipelineCards: stdCards("privileged actions"),
  arch: {
    users: "Students / staff / faculty",
    sor: "ITSM (ticketing) + IdP",
    ext: "Runbooks / IT KB",
    runtime: [
      { t: "UI task (service-desk chat)", color: C_COMPUTE },
      { t: "Service-desk agent", color: C_COMPUTE },
      { t: "MCP auth gateway", s: "all outbound tool calls", color: C_INTEG },
    ],
    data: [
      { t: "Bedrock Knowledge Base", s: "runbooks / IT KB", color: C_MODEL },
      { t: "DynamoDB audit", s: "append-only", color: C_INTEG },
      { t: "S3 Object Lock", s: "WORM", color: C_STORAGE },
      { t: "Secrets Manager", s: "scoped tokens", color: C_STORAGE },
    ],
    legend: "1 user sign-in   2 SAML federation (MFA at IdP; Cognito issues JWT)   3 authenticated session to service-desk chat   4 runbooks retrieved from the Knowledge Base; ITSM/IdP read over private connectivity   5 workers scale with ticket volume   6 resolution/draft via Bedrock + Guardrails inside the VPC   7 every resolution & action persisted to append-only audit   8 ITSM + identity-provider reachable only through the governed MCP gateway (privileged actions gated)",
  },
  proofStats: [
    { big: "$1–$4", label: "self-service vs. $17–$25 phone resolution", tag: "[sector-press/estimate]" },
    { big: "45%+", label: "of queries AI can deflect (vendor-cited)", tag: "[sector-press/estimate]" },
    { big: "~$70/reset", label: "password-reset labor cost targeted", tag: "[sector-press/estimate]" },
    { big: "~$300K/yr", label: "deflectable-ticket cost modeled at 50k tickets", tag: "[modeled]" },
  ],
  deploySteps: [
    "Provision KMS CMK per data class + per-customer VPC / network.",
    "Stand up Cognito SAML→JWT federation with role scoping.",
    "Front with CloudFront + WAF, ALB TLS 1.3.",
    "Deploy the service-desk agent + grant tools via the MCP gateway.",
    "Connect the ITSM tool + identity provider; index runbooks.",
    "Set which actions auto-resolve vs. require approval; audit + smoke test.",
  ],
  deployOneLiner: "Quick-deploy + gateway; connect the ITSM tool and identity provider, index runbooks, set which actions auto-resolve vs. require approval.",
  notes: {
    s1: "[00:20] Title. Agent 08 is land-first — visible, measurable deflection, and the small-IT-team pain is acute (especially K-12). Position to the CIO as relief for a stretched team; to the CFO as a clean cost-per-ticket deflection ROI.",
    s2: "[00:45] Hook. The 20–50% password-call share and $70/reset are sector-press/vendor-cited — flag them. The $300K is modeled; show arithmetic. The 45%+ deflection is vendor-cited supporting color, not the lead.",
    s3: "[01:10] Issue + cost. Modeled deflectable-ticket cost plus password-reset labor. Bright line: low-risk resets auto-resolve, but any privileged/account-changing action stops at a human gate — the CISO's key concern.",
    s4: "[01:35] Pipeline. The gate is risk-tiered: define which actions auto-resolve vs. escalate at deploy time. Every action — auto or human — is audited.",
    s5: "[02:15] Architecture. Customer provides: IdP, ITSM connectivity, identity-provider connectivity for resets, and approved runbooks. Privileged actions are gated through the gateway; everything audited.",
    s6: "[02:45] Proof + deploy. The deflection economics are the headline. The auto-vs-approve split is configured at deploy. Close on platform-as-product and the runbook pointer.",
  },
},
];

// ============================================================ SUITE OVERVIEW DECK
function buildOverview(P) {
  // 1 TITLE
  {
    const s = P.addSlide(); s.background = { color: SQUID }; edgeBar(P, s);
    s.addText("EDU AI Agent Suite", { x: 0.85, y: 1.7, w: 11.6, h: 1.3, fontFace: F_BOLD, fontSize: 50, bold: true, color: WHITE, align: "left", valign: "middle", margin: 0 });
    s.addText("Governed Agentic AI for Education — Built on AWS", { x: 0.87, y: 3.15, w: 11.4, h: 0.6, fontFace: F_BOLD, fontSize: 22, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
    s.addText("Eight reference agents on one FERPA/ADA-defensible platform — the agent isn't the product, the governance is.", { x: 0.88, y: 3.9, w: 11.4, h: 0.6, fontFace: F_TAG, fontSize: 16, italic: true, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
    s.addText("Executive Overview  ·  Built on AWS  ·  June 2026", { x: 0.88, y: 6.0, w: 11.4, h: 0.3, fontFace: F_REG, fontSize: 12, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
    s.addNotes("[00:30] Open with the thesis: everyone in education is moving on AI, almost no one is governed. This suite is eight reference agents sharing ONE governed AWS control plane. For a CIO/CFO, the platform is the asset — the agents are interchangeable workloads on top of it. Set the agenda: thesis, shared architecture, portfolio, governance spine, maturity, deployment, land-and-expand, cost of inaction, takeaway.");
  }
  // 2 THESIS
  {
    const s = P.addSlide(); s.background = { color: SQUID }; edgeBar(P, s);
    s.addText("EVERYONE'S MOVING. FEW ARE GOVERNED.", { x: 0.85, y: 0.85, w: 11.8, h: 1.0, fontFace: F_BOLD, fontSize: 36, bold: true, color: WHITE, align: "left", valign: "middle", charSpacing: 0.5, margin: 0 });
    s.addText("Adoption is near-universal; governance is the gap this platform closes.", { x: 0.88, y: 1.95, w: 11.3, h: 0.5, fontFace: F_TAG, fontSize: 16, italic: true, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
    const stats = [
      { big: "57%", label: "of higher-ed institutions now treat AI as a strategic priority", tag: "[foundation/research — EDUCAUSE 2025]" },
      { big: "<40%", label: "have a formal AI governance framework / acceptable-use policy", tag: "[foundation/research — EDUCAUSE/Tyton]" },
      { big: "23%→48%", label: "of districts now train teachers on AI (more than doubled)", tag: "[gov/peer-reviewed — RAND]" },
    ];
    const cw = 3.62, gap = 0.32, x0 = 0.85, cy = 3.0, ch = 2.1;
    stats.forEach((st, i) => {
      const x = x0 + i * (cw + gap);
      s.addShape(P.shapes.RECTANGLE, { x, y: cy, w: cw, h: ch, fill: { color: SQUID2 }, line: { color: "3A485A", width: 1 } });
      s.addText(st.big, { x: x + 0.28, y: cy + 0.22, w: cw - 0.5, h: 0.85, fontFace: F_BOLD, fontSize: 40, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
      s.addText(st.label, { x: x + 0.3, y: cy + 1.12, w: cw - 0.55, h: 0.65, fontFace: F_REG, fontSize: 12, color: "C9D2DC", align: "left", valign: "top", margin: 0 });
      tag(P, s, x + 0.3, cy + ch - 0.3, st.tag, true);
    });
    s.addText("The takeaway: this platform is the governance layer that lets an institution adopt AI as fast as everyone else — and defend it to an examiner.", { x: 0.85, y: 5.5, w: 11.8, h: 0.7, fontFace: F_REG, fontSize: 14, italic: true, color: "C9D2DC", align: "left", valign: "middle", margin: 0 });
    footer(P, s, "EDU AI Agent Suite  ·  Built on AWS  ·  June 2026", true);
    s.addNotes("[00:55] The frame the whole suite answers. EDUCAUSE: 57% strategic priority but <40% have governance. RAND: district AI training doubled. The gap between adoption and governance IS the opportunity. To the CIO: you can move now without owning ungoverned shadow AI. To the CFO: one platform amortized across eight workloads.");
  }
  // 3 SHARED ARCHITECTURE
  slideArch(P, {
    archTitle: "Shared AWS Architecture & Traffic Flow",
    arch: {
      users: "Students · families · educators · staff",
      sor: "SIS · LMS · ERP · ITSM",
      ext: "Approved KB · external data",
      runtime: [
        { t: "UI task (per-agent console)", color: C_COMPUTE },
        { t: "Agent worker + SQS/EventBridge", s: "event-driven agents", color: C_COMPUTE },
        { t: "MCP auth gateway", s: "all outbound tool calls", color: C_INTEG },
      ],
      data: [
        { t: "Aurora / DynamoDB", s: "state", color: C_MODEL },
        { t: "DynamoDB audit", s: "append-only", color: C_INTEG },
        { t: "S3 Object Lock", s: "WORM", color: C_STORAGE },
        { t: "Secrets Manager", s: "scoped tokens", color: C_STORAGE },
      ],
      legend: "1 sign-in   2 SAML federation (MFA at IdP; Cognito issues JWT — no credentials in AWS)   3 authenticated session   4 systems-of-record read over private connectivity   5 queue/scale for event-driven agents   6 model calls stay in-VPC via Bedrock + Guardrails endpoint   7 every action persisted to append-only audit   8 tools reachable only through the governed MCP gateway",
    },
    notes: { s5: "[02:00] The shared platform — every agent inherits this. One control plane: CloudFront/WAF edge, Cognito federation, MCP authorization gateway (deny-by-default, short-lived scoped tokens), Bedrock + Guardrails in-VPC, HITL gate, S3 Object Lock + DynamoDB append-only audit, per-customer VPC + dedicated account. Agent-specific blocks (Textract, Translate, Connect, EventBridge, Step Functions HITL) bolt onto this spine. To the CISO: PII never egresses after masking; least-privilege IAM throughout." },
  });
  // 4 & 5 PORTFOLIO
  function portfolioSlide(idxs, partLabel) {
    const s = P.addSlide(); s.background = { color: GRAYBG }; edgeBar(P, s);
    s.addText("The 8-Agent Portfolio" + (partLabel ? `  —  ${partLabel}` : ""), { x: 0.78, y: 0.35, w: 12, h: 0.6, fontFace: F_BOLD, fontSize: 28, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
    const cols = 2, cw = 5.78, ch = 2.55, gx = 0.78, gy = 1.25, gapx = 0.45, gapy = 0.4;
    idxs.forEach((ai, k) => {
      const a = AGENTS[ai];
      const col = k % cols, row = Math.floor(k / cols);
      const x = gx + col * (cw + gapx), y = gy + row * (ch + gapy);
      s.addShape(P.shapes.RECTANGLE, { x, y, w: cw, h: ch, fill: { color: CARD }, line: { type: "none" }, shadow: sh() });
      s.addShape(P.shapes.RECTANGLE, { x, y, w: 0.07, h: ch, fill: { color: ORANGE }, line: { type: "none" } });
      s.addText(`${a.num}`, { x: x + 0.28, y: y + 0.2, w: 1.0, h: 0.5, fontFace: F_BOLD, fontSize: 22, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
      s.addText(a.name, { x: x + 0.95, y: y + 0.18, w: cw - 1.2, h: 0.6, fontFace: F_BOLD, fontSize: 14, bold: true, color: INK, align: "left", valign: "middle", lineSpacingMultiple: 0.95, margin: 0 });
      s.addText(a.tagline, { x: x + 0.3, y: y + 0.85, w: cw - 0.6, h: 0.62, fontFace: F_REG, fontSize: 10.5, italic: true, color: MUTED, align: "left", valign: "top", lineSpacingMultiple: 1.0, margin: 0 });
      s.addText([
        { text: "Headline:  ", options: { bold: true, color: INK } },
        { text: a.hookStats[0].big + " — " + a.hookStats[0].label, options: { color: INK } },
      ], { x: x + 0.3, y: y + 1.5, w: cw - 0.6, h: 0.55, fontFace: F_REG, fontSize: 10.5, align: "left", valign: "top", lineSpacingMultiple: 0.98, margin: 0 });
      s.addText([
        { text: "Cost of doing nothing:  ", options: { bold: true, color: ORANGED } },
        { text: a.costBig, options: { bold: true, color: ORANGED } },
      ], { x: x + 0.3, y: y + ch - 0.5, w: cw - 0.6, h: 0.4, fontFace: F_REG, fontSize: 11, align: "left", valign: "middle", margin: 0 });
    });
    footer(P, s, null, false);
    return s;
  }
  portfolioSlide([0, 2, 6, 7], "Land-first (low decision-risk)").addNotes("[02:30] The portfolio, part 1 — the land-first agents: Concierge (01), Educator Copilot (03), Document/Accessibility (07), Service Desk (08). Each tile shows value, the strongest headline metric, and the cost of doing nothing. These four are visible, measurable, and low decision-risk — they prove the control plane. Walk the cost-of-nothing column for the CFO.");
  portfolioSlide([1, 3, 4, 5], "Higher-governance (sequence after)").addNotes("[03:00] The portfolio, part 2 — the higher-governance agents: Tutor (02), Assessment (04), Student Success (05), Pathway (06). These touch grades, interventions, and degree plans, so they carry mandatory human gates. Sequence them after the platform is proven by the land-first four. The cost-of-nothing here is larger — retained tuition (05) and transfer cost (06) are the biggest CFO numbers in the suite.");
  // 6 GOVERNANCE SPINE
  {
    const s = P.addSlide(); s.background = { color: GRAYBG }; edgeBar(P, s);
    s.addText("The Governance & Compliance Spine", { x: 0.78, y: 0.35, w: 12, h: 0.6, fontFace: F_BOLD, fontSize: 28, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
    s.addText("Every agent inherits the same controls — mapped to the regulations education buyers are examined against.", { x: 0.8, y: 1.0, w: 12, h: 0.45, fontFace: F_TAG, fontSize: 13, italic: true, color: MUTED, align: "left", valign: "top", margin: 0 });
    const body = [
      ["FERPA (student records)", "Per-customer VPC + KMS CMK; gateway-scoped reads; PII masked before model calls; append-only access audit"],
      ["COPPA (under-13)", "Role-scoped federation; data-minimizing retention boundaries; consent-gated connectors"],
      ["IDEA / ADA Title II (accessibility)", "WCAG 2.1 AA remediation pipeline (Textract); staff accessibility sign-off; 2027/2028-deadline ready"],
      ["GLBA (financial-aid data)", "Encryption in transit/at rest; least-privilege IAM; Secrets Manager; CloudTrail + Security Hub"],
      ["Title VI (non-discrimination)", "Human gate on consequential actions; auditable flag/contact rationale (esp. Student Success)"],
      ["NIST AI RMF", "Govern/Map/Measure/Manage: Guardrails, explainable outputs, HITL, continuous CloudWatch + audit"],
    ];
    const ty = 1.6, rowH = 0.72, tw = 11.78, c0 = 3.7, x0 = 0.78;
    // header band
    s.addShape(P.shapes.RECTANGLE, { x: x0, y: ty, w: tw, h: 0.45, fill: { color: SQUID }, line: { type: "none" } });
    s.addText("Regulation / framework", { x: x0 + 0.15, y: ty, w: c0 - 0.3, h: 0.45, fontFace: F_BOLD, fontSize: 12, bold: true, color: WHITE, valign: "middle", margin: 0 });
    s.addText("Mapped control on the platform", { x: x0 + c0 + 0.15, y: ty, w: tw - c0 - 0.3, h: 0.45, fontFace: F_BOLD, fontSize: 12, bold: true, color: WHITE, valign: "middle", margin: 0 });
    body.forEach((r, i) => {
      const y = ty + 0.45 + i * rowH;
      s.addShape(P.shapes.RECTANGLE, { x: x0, y, w: tw, h: rowH, fill: { color: i % 2 ? "E9ECEF" : CARD }, line: { color: LINE, width: 0.5 } });
      s.addShape(P.shapes.RECTANGLE, { x: x0 + c0, y, w: 0.012, h: rowH, fill: { color: LINE }, line: { type: "none" } });
      s.addText(r[0], { x: x0 + 0.15, y, w: c0 - 0.3, h: rowH, fontFace: F_BOLD, fontSize: 11.5, bold: true, color: SQUID, valign: "middle", align: "left", margin: 0 });
      s.addText(r[1], { x: x0 + c0 + 0.18, y, w: tw - c0 - 0.36, h: rowH, fontFace: F_REG, fontSize: 11, color: INK, valign: "middle", align: "left", lineSpacingMultiple: 0.98, margin: 0 });
    });
    footer(P, s, null, false);
    s.addNotes("[03:30] The compliance spine is the reason a CISO or general counsel signs off. Each regulation education buyers are examined against maps to a concrete control already in the platform — not a policy promise. FERPA, COPPA, IDEA/ADA Title II, GLBA, Title VI, and NIST AI RMF. This is the slide that turns 'interesting AI demo' into 'defensible institutional system.'");
  }
  // 7 MATURITY LADDER
  {
    const s = P.addSlide(); s.background = { color: GRAYBG }; edgeBar(P, s);
    s.addText("The Maturity Ladder", { x: 0.78, y: 0.35, w: 12, h: 0.6, fontFace: F_BOLD, fontSize: 28, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
    s.addText("Climb at the institution's own pace — each rung reuses the same governed control plane.", { x: 0.8, y: 1.0, w: 12, h: 0.45, fontFace: F_TAG, fontSize: 13, italic: true, color: MUTED, align: "left", valign: "top", margin: 0 });
    const rungs = [
      { t: "1 · Assist", b: "Read-only answers & drafts (Concierge, Service Desk). Humans act. Fastest proof, lowest risk." },
      { t: "2 · Draft", b: "AI drafts consequential artifacts (lessons, grades, plans); humans approve every one." },
      { t: "3 · Proactive", b: "Event-driven detection & recommended interventions (Student Success); advisor approves." },
      { t: "4 · Orchestrated", b: "Multiple agents on one control plane; shared audit, identity, and governance." },
    ];
    const bw = 2.82, gap = 0.18, x0 = 0.78, y = 1.7, bh = 3.6;
    rungs.forEach((r, i) => {
      const x = x0 + i * (bw + gap);
      const fill = [TEAL, C_COMPUTE, C_INTEG, SQUID][i];
      s.addShape(P.shapes.RECTANGLE, { x, y, w: bw, h: bh, fill: { color: fill }, line: { type: "none" }, shadow: shsm() });
      s.addText(r.t, { x: x + 0.22, y: y + 0.25, w: bw - 0.4, h: 0.7, fontFace: F_BOLD, fontSize: 17, bold: true, color: WHITE, align: "left", valign: "top", lineSpacingMultiple: 0.98, margin: 0 });
      s.addText(r.b, { x: x + 0.24, y: y + 1.1, w: bw - 0.45, h: bh - 1.3, fontFace: F_REG, fontSize: 12, color: "F2F6F8", align: "left", valign: "top", lineSpacingMultiple: 1.05, margin: 0 });
    });
    s.addText("The control plane never changes — only how much autonomy you grant on top of it.", { x: 0.78, y: 5.6, w: 11.8, h: 0.5, fontFace: F_REG, fontSize: 14, italic: true, color: INK, align: "left", valign: "middle", margin: 0 });
    footer(P, s, null, false);
    s.addNotes("[04:00] The maturity ladder lets an institution self-pace. Rung 1 (assist) is read-only and the safest start; rung 4 is multiple orchestrated agents on one platform. The key governance message: the control plane is identical at every rung — you only dial up how much autonomy you grant. A board can approve rung 1 today and rung 3 next year without re-architecting.");
  }
  // 8 DEPLOYMENT
  {
    const s = P.addSlide(); s.background = { color: GRAYBG }; edgeBar(P, s);
    s.addText("Deployment — One Platform, Per-Customer Isolation", { x: 0.78, y: 0.35, w: 12, h: 0.6, fontFace: F_BOLD, fontSize: 26, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
    const steps = [
      ["Foundation", "Per-customer VPC + dedicated AWS account; KMS CMK per data class; network to systems-of-record (PrivateLink / Direct Connect)."],
      ["Identity", "Cognito SAML→JWT federation with role scoping (student / guardian / educator / counselor / admin). No credentials stored in AWS."],
      ["Edge", "CloudFront + WAF; ALB TLS 1.3; Cognito auth at the edge."],
      ["Agent + tools", "Deploy the AgentCore/Fargate agent; grant tools via the deny-by-default MCP gateway with short-lived scoped tokens."],
      ["Connectors + data", "Wire SIS / LMS / ERP / ITSM connectors and Secrets Manager; index approved KB; add agent-specific blocks (Textract, Translate, EventBridge, Step Functions HITL)."],
      ["Governance + go-live", "Bedrock Guardrails (mandatory); S3 Object Lock + DynamoDB append-only audit; CloudTrail / Security Hub / Config; smoke + HITL test."],
    ];
    const cw = 5.78, ch = 1.35, gx = 0.78, gy = 1.2, gapx = 0.45, gapy = 0.25;
    steps.forEach((st, k) => {
      const col = k % 2, row = Math.floor(k / 2);
      const x = gx + col * (cw + gapx), y = gy + row * (ch + gapy);
      s.addShape(P.shapes.RECTANGLE, { x, y, w: cw, h: ch, fill: { color: CARD }, line: { type: "none" }, shadow: shsm() });
      s.addText(`${k + 1}`, { x: x + 0.22, y: y + 0.18, w: 0.55, h: 0.5, fontFace: F_BOLD, fontSize: 20, bold: true, color: ORANGE, align: "left", valign: "top", margin: 0 });
      s.addText(st[0], { x: x + 0.78, y: y + 0.16, w: cw - 1.0, h: 0.4, fontFace: F_BOLD, fontSize: 13.5, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
      s.addText(st[1], { x: x + 0.78, y: y + 0.52, w: cw - 1.0, h: ch - 0.6, fontFace: F_REG, fontSize: 10, color: MUTED, align: "left", valign: "top", lineSpacingMultiple: 1.0, margin: 0 });
    });
    s.addText("Reference: runbooks/agent-deploy/<NN>-*.md  ·  docs/AWS-DEPLOYMENT-REFERENCE.md", { x: 0.78, y: 6.0, w: 11.8, h: 0.35, fontFace: F_REG, fontSize: 10.5, italic: true, color: MUTED, align: "left", valign: "middle", margin: 0 });
    footer(P, s, null, false);
    s.addNotes("[04:30] Deployment is a repeatable six-stage path: foundation, identity, edge, agent+tools, connectors+data, governance+go-live. The customer provides identity, network reachability, connectors, and approved content; the reference templates provide everything else. Per-customer isolation (dedicated account + VPC) is what regulated buyers require. Point them at the runbooks and the AWS deployment reference.");
  }
  // 9 LAND-AND-EXPAND
  {
    const s = P.addSlide(); s.background = { color: GRAYBG }; edgeBar(P, s);
    s.addText("Land-and-Expand", { x: 0.78, y: 0.35, w: 12, h: 0.6, fontFace: F_BOLD, fontSize: 28, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
    s.addText("Prove the governed control plane with low-risk agents, then expand to higher-governance workloads on the same foundation.", { x: 0.8, y: 1.0, w: 12, h: 0.45, fontFace: F_TAG, fontSize: 13, italic: true, color: MUTED, align: "left", valign: "top", margin: 0 });
    const phases = [
      { t: "LAND", c: TEAL, agents: "01 Concierge · 03 Educator Copilot · 07 Document/Accessibility · 08 Service Desk", why: "Visible, measurable, low decision-risk. Proves identity, gateway, audit, and Guardrails in production." },
      { t: "EXPAND", c: C_COMPUTE, agents: "04 Assessment · 02 Tutor", why: "Add mandatory human gates (grades, integrity) on the now-proven control plane." },
      { t: "SCALE", c: SQUID, agents: "05 Student Success · 06 Pathway", why: "Highest-governance, highest-CFO-value (retained tuition, transfer cost). Event-driven + advisor gates." },
    ];
    const y0 = 1.7, bh = 1.25, gap = 0.3;
    phases.forEach((p, i) => {
      const y = y0 + i * (bh + gap);
      s.addShape(P.shapes.RECTANGLE, { x: 0.78, y, w: 11.78, h: bh, fill: { color: CARD }, line: { type: "none" }, shadow: shsm() });
      s.addShape(P.shapes.RECTANGLE, { x: 0.78, y, w: 2.1, h: bh, fill: { color: p.c }, line: { type: "none" } });
      s.addText(p.t, { x: 0.78, y, w: 2.1, h: bh, fontFace: F_BOLD, fontSize: 22, bold: true, color: WHITE, align: "center", valign: "middle", margin: 0 });
      s.addText(p.agents, { x: 3.1, y: y + 0.18, w: 9.2, h: 0.5, fontFace: F_BOLD, fontSize: 14, bold: true, color: INK, align: "left", valign: "middle", margin: 0 });
      s.addText(p.why, { x: 3.1, y: y + 0.66, w: 9.2, h: 0.5, fontFace: F_REG, fontSize: 12, color: MUTED, align: "left", valign: "top", lineSpacingMultiple: 1.0, margin: 0 });
    });
    footer(P, s, null, false);
    s.addNotes("[05:00] Land-and-expand de-risks the buy. Land with the four low-decision-risk agents (01/03/07/08) — they prove identity, the gateway, audit, and Guardrails in production. Expand to grade- and integrity-touching agents (04/02). Scale to the highest-governance, highest-value agents (05/06) where the CFO numbers are biggest. Every phase reuses the same control plane — no re-architecting.");
  }
  // 10 COST OF INACTION SUMMARY
  {
    const s = P.addSlide(); s.background = { color: SQUID }; edgeBar(P, s);
    s.addText("The Suite-Level Cost of Inaction", { x: 0.85, y: 0.45, w: 11.8, h: 0.7, fontFace: F_BOLD, fontSize: 30, bold: true, color: WHITE, align: "left", valign: "middle", margin: 0 });
    s.addText("Per-agent cost of doing nothing, at a reference institution — substitute your own volumes.", { x: 0.88, y: 1.15, w: 11.4, h: 0.4, fontFace: F_TAG, fontSize: 14, italic: true, color: MUTEDLT, align: "left", valign: "top", margin: 0 });
    const shortNames = {
      "01": "Concierge", "02": "Tutor", "03": "Educator Copilot", "04": "Assessment / Grading",
      "05": "Student Success", "06": "Pathway Navigator", "07": "Document / Accessibility", "08": "IT Service Desk",
    };
    const cw = 3.62, ch = 1.18, gx = 0.85, gy = 1.7, gapx = 0.32, gapy = 0.28;
    AGENTS.forEach((a, k) => {
      const col = k % 3, row = Math.floor(k / 3);
      const x = gx + col * (cw + gapx), y = gy + row * (ch + gapy);
      s.addShape(P.shapes.RECTANGLE, { x, y, w: cw, h: ch, fill: { color: SQUID2 }, line: { color: "3A485A", width: 1 } });
      s.addText(`${a.num}  ${shortNames[a.num]}`, { x: x + 0.2, y: y + 0.14, w: cw - 0.4, h: 0.4, fontFace: F_BOLD, fontSize: 12, bold: true, color: "C9D2DC", align: "left", valign: "top", margin: 0 });
      s.addText(a.costBig, { x: x + 0.2, y: y + 0.55, w: cw - 0.4, h: 0.5, fontFace: F_BOLD, fontSize: 18, bold: true, color: ORANGE, align: "left", valign: "middle", margin: 0 });
    });
    s.addText("Most are modeled at a reference baseline; 03/06/07 use direct published figures. None are guaranteed — they substitute the customer's actuals.", { x: 0.85, y: 6.35, w: 11.8, h: 0.5, fontFace: F_REG, fontSize: 10.5, italic: true, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
    s.addNotes("[05:30] The CFO summary slide. Eight cost-of-doing-nothing figures on one view. Be disciplined: most are modeled at a reference baseline (show that label), while 03 (teacher turnover), 06 (transfer credit), and 07 (litigation exposure) use direct published figures. None are guaranteed — they substitute the customer's own volumes. The point: inaction has a recurring, quantifiable price across the institution.");
  }
  // 11 TAKEAWAY
  {
    const s = P.addSlide(); s.background = { color: SQUID }; edgeBar(P, s);
    s.addText("The Takeaway", { x: 0.85, y: 1.5, w: 11.6, h: 0.8, fontFace: F_BOLD, fontSize: 40, bold: true, color: WHITE, align: "left", valign: "middle", margin: 0 });
    s.addText([
      { text: "The agent isn't the product.  ", options: { bold: true, color: ORANGE } },
      { text: "The governed platform that makes it FERPA/ADA-defensible and deployable on AWS is.", options: { color: WHITE } },
    ], { x: 0.87, y: 2.6, w: 11.4, h: 1.4, fontFace: F_BOLD, fontSize: 26, align: "left", valign: "top", lineSpacingMultiple: 1.1, margin: 0 });
    s.addText("Eight reference agents · one control plane · land-first with 01 / 03 / 07 / 08 · expand at your own pace.", { x: 0.88, y: 4.4, w: 11.4, h: 0.6, fontFace: F_TAG, fontSize: 16, italic: true, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
    s.addText("runbooks/agent-deploy/  ·  docs/AWS-DEPLOYMENT-REFERENCE.md  ·  June 2026", { x: 0.88, y: 6.0, w: 11.4, h: 0.3, fontFace: F_REG, fontSize: 12, color: MUTEDLT, align: "left", valign: "middle", margin: 0 });
    s.addNotes("[06:00] Close on the thesis restated: the agent isn't the product — the governed platform is. That's what an institution actually buys, and what its examiner actually evaluates. Recommend landing with 01/03/07/08 to prove the control plane, then expanding at their own pace. Hand off to the runbooks and AWS deployment reference. Invite the architecture deep-dive next.");
  }
}

// ============================================================ BUILD
const OUT = process.env.DECK_OUT || "/sessions/practical-sweet-planck/mnt/edu-ai-agents/decks";
const fileNames = {
  "01": "EDU-01-Student-Family-Concierge.pptx",
  "02": "EDU-02-Tutor-Study-Companion.pptx",
  "03": "EDU-03-Educator-Copilot.pptx",
  "04": "EDU-04-Assessment-Grading-Feedback.pptx",
  "05": "EDU-05-Student-Success-Engagement.pptx",
  "06": "EDU-06-Pathway-Navigator.pptx",
  "07": "EDU-07-Document-Accessibility-Services.pptx",
  "08": "EDU-08-Operations-Service-Desk.pptx",
};

async function main() {
  for (const d of AGENTS) {
    const P = new pptxgen();
    P.layout = "LAYOUT_WIDE"; P.author = "EDU AI Agent Suite"; P.title = `EDU Agent ${d.num} — ${d.name}`;
    buildAgentDeck(P, d);
    await P.writeFile({ fileName: `${OUT}/${fileNames[d.num]}` });
    console.log("wrote", fileNames[d.num]);
  }
  const PO = new pptxgen();
  PO.layout = "LAYOUT_WIDE"; PO.author = "EDU AI Agent Suite"; PO.title = "EDU AI Agent Suite — Executive Overview";
  buildOverview(PO);
  await PO.writeFile({ fileName: `${OUT}/EDU-Agentic-AI-Suite-Executive-Overview.pptx` });
  console.log("wrote EDU-Agentic-AI-Suite-Executive-Overview.pptx");
}

main().catch((e) => { console.error(e); process.exit(1); });
