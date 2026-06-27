# Accessibility Conformance Plan

### EDU AI Agent Suite · WCAG 2.1 / 2.2 AA · ADA Title II · Section 504 / 508

> **What this is.** A conformance **plan** the deploying institution executes to bring an EDU AI Agent deployment — **both the agent UI and the AI-generated output** — to WCAG 2.1/2.2 Level AA, as required by ADA Title II (28 CFR Part 35) and Section 508. It states honestly what the repository ships today (a deterministic **preflight**), what conformance still requires, and who owns each step.
>
> **The honest line.** The repository ships a **deterministic accessibility preflight** (`governance/accessibility/wcag.py`). **A preflight is not conformance.** It catches the most common WCAG AA failures before content ships; it does **not** replace automated scanning in CI, keyboard/screen-reader testing, PDF/UA review, or testing by people with disabilities. **Full WCAG 2.x conformance testing remains the customer's responsibility** (`docs/PRODUCTION-READINESS-ACTION-PLAN.md`, "Compliance & accessibility posture"; `governance/README.md` §5; README maturity ladder — WCAG 2.2 AA conformance is a *production-readiness gate*).
>
> **Audience.** Institutional accessibility lead / coordinator (ADA/504 coordinator), CISO/security review board, and the procurement/legal team evaluating deployment on AWS.

---

## 1. Why this matters now, and why AI output is in scope

DOJ's April 2024 ADA Title II rule adopts **WCAG 2.1 Level AA** for state/local-government and public-institution web content and mobile apps; Section 508 applies the same bar to federally funded programs. Compliance dates (per DOJ's April 2026 Interim Final Rule, as captured in `governance/accessibility/wcag.py`):

| Entity size | Compliance date |
|---|---|
| Public entities serving **≥ 50,000** population | **April 26, 2027** |
| Smaller entities and special districts (many districts, small colleges) | **April 26, 2028** |

**AI-generated output is in scope.** Every message, announcement, advising plan, remediated document, translated material, and rendered HTML the agent produces is "web content" subject to the same standard as a static page. The large majority of OCR accessibility complaints involve **untagged PDFs and missing text alternatives** — exactly the document- and content-generation surface Agent 07 and the family-facing agents touch (`wcag.py` module docstring; README Agent 07 row). The institution's conformance target for deployed surfaces is **WCAG 2.2 AA** (the newer baseline; `governance/README.md` §"ADA"; Agent 07 `edu-compliance.md` §5).

---

## 2. What the preflight covers **today** vs. what conformance **still requires**

### What ships today — the deterministic preflight (`governance/accessibility/wcag.py`)

`check_html()` and `check_plain_language()` are **deterministic, dependency-free** checks that run on AI-generated HTML/rich text **before content ships**:

| Check | WCAG SC | What it catches |
|---|---|---|
| Every `<img>` has an `alt` attribute | **1.1.1** Non-text Content | Missing text alternatives |
| Heading levels do not skip (no h2→h4 jump) | **1.3.1** Info & Relationships / **2.4.6** | Broken assistive-tech navigation structure |
| No vague link text ("click here", "read more", "here", "link", "this", "more") | **2.4.4** Link Purpose (In Context) | Non-descriptive links |
| Flesch-Kincaid reading grade ≤ target (default 9.0) | **3.1.5** Reading Level (plain-language proxy) | Cognitive-accessibility / plain-language gaps |

This is a **fast pre-flight, not a substitute for full WCAG auditing** (its own docstring says so). It is deterministic, runs without an API key, and is the right gate to enforce on AI output **pre-send**.

### What conformance still requires (customer-owned)

The preflight does **not** cover these — they are required for an actual conformance claim:

| Conformance activity | Why the preflight can't do it |
|---|---|
| **Automated scanning (axe-core) in CI** | The preflight is a narrow regex pass, not a full rules engine; control_mappings names axe-core as the CI target ("CI (axe-core target)") |
| **Keyboard-only operation** | Requires interaction testing of the live UI (focus order, traps, visible focus) |
| **Screen-reader testing (NVDA / JAWS / VoiceOver)** | Requires manual AT testing of rendered, dynamic output |
| **Magnification / reflow** (up to 400%, 320 CSS px) | Requires layout testing at zoom |
| **Color / contrast** (1.4.3, 1.4.11) | Requires computed-style/contrast measurement, not text parsing |
| **Captions / transcripts / audio descriptions** | Required for any media the agent surfaces or Agent 07 produces (Polly audio, video) |
| **Cognitive / plain-language** beyond a grade proxy | Grade level is a proxy; true plain-language review is human |
| **Testing of *dynamically generated agent responses*** | Each generated response is new content; representative sampling + per-response preflight required |
| **PDF/UA** for documents (Agent 07) | Tagged-PDF / PDF-UA conformance is out of scope for an HTML regex pass — and untagged PDFs are the #1 complaint category |
| **Testing by people with disabilities** | No automated tool substitutes for real AT-user testing |

---

## 3. Conformance Test Matrix

Representative WCAG 2.2 AA success criteria mapped to test method, automation level, owner, and status. Status is a **placeholder for the customer to complete** during the conformance engagement. *(Preflight column: ✅ = the shipped `wcag.py` preflight provides partial automated coverage; — = not covered by the preflight.)*

| SC | Title | Level | Test method | Auto / Manual | Preflight | Owner | Status |
|---|---|---|---|---|---|---|---|
| **1.1.1** | Non-text Content | A | axe-core + manual alt-quality review | Both | ✅ (presence) | **[CUSTOMER]** | ☐ |
| **1.3.1** | Info & Relationships | A | axe-core + screen-reader structure check | Both | ✅ (heading order) | **[CUSTOMER]** | ☐ |
| **1.4.3** | Contrast (Minimum) | AA | Contrast analyzer / axe-core | Auto | — | **[CUSTOMER]** | ☐ |
| **1.4.10** | Reflow | AA | 320px / 400% zoom manual test | Manual | — | **[CUSTOMER]** | ☐ |
| **1.4.11** | Non-text Contrast | AA | Contrast analyzer | Auto | — | **[CUSTOMER]** | ☐ |
| **2.1.1** | Keyboard | A | Keyboard-only manual pass | Manual | — | **[CUSTOMER]** | ☐ |
| **2.4.4** | Link Purpose (In Context) | A | axe-core + manual | Both | ✅ (vague-link) | **[CUSTOMER]** | ☐ |
| **2.4.6** | Headings and Labels | AA | Manual + axe-core | Both | ✅ (heading order) | **[CUSTOMER]** | ☐ |
| **2.4.7** | Focus Visible | AA | Keyboard manual pass | Manual | — | **[CUSTOMER]** | ☐ |
| **2.4.11** | Focus Not Obscured (Min) *(2.2 add)* | AA | Manual | Manual | — | **[CUSTOMER]** | ☐ |
| **2.5.8** | Target Size (Min) *(2.2 add)* | AA | Manual / measurement | Both | — | **[CUSTOMER]** | ☐ |
| **3.1.5** | Reading Level | AAA* | Flesch-Kincaid + human plain-language review | Both | ✅ (grade proxy) | **[CUSTOMER]** | ☐ |
| **3.3.7** | Redundant Entry *(2.2 add)* | A | Manual flow test | Manual | — | **[CUSTOMER]** | ☐ |
| **3.3.8** | Accessible Authentication (Min) *(2.2 add)* | AA | Manual auth-flow test | Manual | — | **[CUSTOMER]** | ☐ |
| **4.1.2** | Name, Role, Value | A | axe-core + screen-reader | Both | — | **[CUSTOMER]** | ☐ |
| **PDF/UA** | Tagged-PDF conformance (Agent 07 docs) | — | PAC / Acrobat checker + manual | Both | — | **[CUSTOMER]** | ☐ |

\* 3.1.5 is WCAG AAA; the suite targets it as a **plain-language practice** for family-facing content (the preflight default is grade ≤ 9.0) even though it sits above the AA conformance line.

**[CUSTOMER TO COMPLETE]** — Assign a named owner per row, run each test against the deployed surfaces, record pass/fail/partial, and log defects in the issue tracker (§5).

---

## 4. AI-Output-Specific Guidance

AI output is the part most accessibility programs miss, because it is generated fresh on every request. The plan treats it as first-class scope:

1. **Every generated message, announcement, advising plan, and remediated document must pass the preflight `check_html()` / `check_plain_language()` pre-send.** Wire the preflight as a gate in the response pipeline so non-conformant content cannot ship. This is the shipped control (`governance/accessibility/wcag.py`); enforcing it pre-send is a customer integration step.
2. **Dynamically generated responses must be sampled in manual testing.** Because each response is new content, the conformance engagement must include representative-sample screen-reader and keyboard testing of *generated* output, not only the static UI shell.
3. **Plain-language target for family-facing content.** Public student/family communications target a **6th–9th grade** reading level so they are usable by multilingual families and learners with disabilities (`wcag.py` `check_plain_language`, default `max_grade=9.0`). The institution sets the final target. **[CUSTOMER]**
4. **Agent 07 documents require PDF/UA review and human verification.** Accessibility/multilingual output for **individualized plans, legal notices, and safety information** blocks until a verified human confirms the transformation before release (Agent 07 `edu-compliance.md` §5 — the consequential-material verification gate). Grounding applies: an accessible/translated version that drifts in meaning fails fast.
5. **Translated materials are accessibility artifacts too** (Amazon Translate / Polly outputs) and must meet the same standard.

---

## 5. Roles, Cadence, Remediation, and Issue Tracking

| Item | Detail |
|---|---|
| **Accessibility lead / 504-ADA coordinator** | **[CUSTOMER]** — final acceptance of the VPAT/conformance report (SHARED-RESPONSIBILITY-MATRIX, "Accessibility" row: institution **Owns** the standard, the coordinator, and final acceptance) |
| **SI responsibility** | Conformance testing during pilot; remediation; accessibility maintenance in the managed-service model (SHARED-RESPONSIBILITY-MATRIX) |
| **Preflight enforcement** | Pre-send gate in the response pipeline (shipped check; customer wires it in) |
| **CI scanning** | axe-core run on rendered surfaces (control_mappings names axe-core as the CI target) — **[CUSTOMER]** to stand up |
| **Cadence** | Full conformance pass before production (the production-readiness gate); re-test on any UI change, prompt/model change affecting output structure, or new content type — change control per SHARED-RESPONSIBILITY-MATRIX |
| **Issue tracking** | **[CUSTOMER]** — log each defect with SC, severity, owner, target date; track to closure; retain evidence for the conformance file |

---

## 6. ACR / VPAT-Style Summary Stub *(customer completes)*

An Accessibility Conformance Report (VPAT 2.x, WCAG 2.2 AA edition) the institution completes after testing. **The platform supplies the preflight evidence; the institution produces and signs the conformance claim — the platform does not assert WCAG conformance on the customer's behalf.**

| Criteria set | Conformance level | Remarks & explanations |
|---|---|---|
| WCAG 2.2 Level A | **[CUSTOMER]** — Supports / Partially Supports / Does Not Support | **[CUSTOMER]** |
| WCAG 2.2 Level AA | **[CUSTOMER]** | **[CUSTOMER]** |
| Section 508 (Revised) | **[CUSTOMER]** | **[CUSTOMER]** |
| PDF/UA (Agent 07 documents) | **[CUSTOMER]** | **[CUSTOMER]** |

**Tested product / version:** [CUSTOMER] · **Test environment (AT versions):** [CUSTOMER] · **Tested by (incl. people with disabilities):** [CUSTOMER] · **Date:** [CUSTOMER]

### Sign-off

| Role | Name | Statement | Signature | Date |
|---|---|---|---|---|
| **Accessibility Lead / 504-ADA Coordinator** | **[CUSTOMER]** | Conformance claim accepted; VPAT signed | | |
| **CISO / Review Board** | **[CUSTOMER]** | Plan and residual gaps accepted | | |

> **Residual-risk reminder.** The preflight is a control, not a conformance claim. Until the customer completes the matrix in §3, runs axe-core + AT + PDF/UA testing, and tests with people with disabilities, **no WCAG 2.x conformance claim should be made for the deployment.** Cross-reference [`docs/PRODUCTION-READINESS-ACTION-PLAN.md`](../PRODUCTION-READINESS-ACTION-PLAN.md) (P4: "accessibility conformance — axe-core + manual screen-reader + PDF/UA, not just the preflight").
