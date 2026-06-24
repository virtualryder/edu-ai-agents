# EDU AI Agent Suite — Deck Sources

> **Verified June 2026.** Every figure on a suite sales deck must trace to an entry below. These are *documented results applied to a reference institution*, not guarantees — outcomes depend on the customer's baseline volumes, staffing, data quality, and process design. **Vendor-reported figures are explicitly labeled `[vendor]`** and should never be the lead stat on a slide. Prefer gov/peer-reviewed and foundation/research figures for headline claims. Where a figure is older than 2024 and no newer authoritative replacement exists, it is flagged `[older — flag on slide]`.
>
> **Source-class tags:** `[gov/peer-reviewed]` · `[foundation/research]` · `[sector-press]` · `[vendor]`

---

## Suite-wide proof points (adoption + named deployments)

**Adoption / market context**
- **57% of higher-ed institutions** now view AI as a strategic priority (up from 49% the prior year); **teaching & learning is the top AI focus area (59%)**, followed by administration (52%). 80% are actively experimenting with AI but fewer than half have a formal governance framework. — *2025 EDUCAUSE AI Landscape Study (fielded Nov 2024, pub. Feb 2025)* `[foundation/research]` — https://library.educause.edu/resources/2025/2/2025-educause-ai-landscape-study and https://www.educause.edu/content/2025/2025-educause-ai-landscape-study/strategy-and-leadership
- **Fewer than 40% of institutions** have an AI acceptable-use policy; AI policy adoption jumped from **3% to 24%** in one year. — *2025 EDUCAUSE AI Landscape Study* `[foundation/research]` (above) and *Tyton Partners, Time for Class 2024* `[foundation/research]` — https://www.luminafoundation.org/wp-content/uploads/2024/06/Time-for-Class-2024.pdf
- **59% of students** use generative AI for schoolwork at least monthly (up from 43% in spring 2023); **36% of instructors have never used it**, and more instructors say GenAI *increased* their workload (34%) than decreased it (8%). — *Tyton Partners, Time for Class 2024 (~1,600 students, 1,800 instructors, 300 admins)* `[foundation/research]` — https://tytonpartners.com/time-for-class-2024/
- **K-12:** District teacher-AI training **more than doubled from 23% to 48%** (2023→2024); **25% of teachers used AI** for instructional planning/teaching in 2023-24. Equity gap: low-poverty districts trained teachers at 67% vs. 39% in high-poverty districts. — *RAND, "Uneven Adoption of AI Tools…2023-24" / "More Districts Are Training Teachers on AI" (2024)* `[gov/peer-reviewed — RAND]` — https://www.rand.org/pubs/research_reports/RRA134-25.html and https://www.rand.org/pubs/research_reports/RRA956-31.html

**Named education deployments on AWS** (all from AWS Public Sector Blog, "Doing more with less in higher education," May 12 2025, which links each underlying customer story) `[vendor — AWS, customer-attributed]` — https://aws.amazon.com/blogs/publicsector/doing-more-with-less-in-higher-education-how-institutions-drive-efficiency-with-ai-and-automation-on-aws/
- **UT Austin** — Amazon Connect contact center cut student wait times **from >15 min to <30 sec** at similar staffing. — https://aws.amazon.com/blogs/publicsector/ut-austin-connects-students-answers-faster-using-amazon-connect/
- **Highline College** — financial-aid status self-service tracker drove a **75% reduction** in status emails/calls/in-person visits. — https://aws.amazon.com/blogs/publicsector/making-financial-aid-simple-students-staff-highline-college-collaborated-with-aws-financial-aid-tracking-tool/
- **Dallas College** — multilingual GenAI chatbot trained on institutional data, 24/7, handles common inquiries without staff intervention. — https://aws.amazon.com/blogs/publicsector/transforming-student-communications-how-dallas-college-modernized-its-call-center-with-aws/
- **Georgia State University** — serverless self-service serving **50,000+ students** (schedules, bills, financial aid); first-month compute bill ~$375. — https://www.slalom.com/us/en/customer-stories/georgia-state-university--serverless-aws
- **Illinois Institute of Technology** — transcript/credential evaluation cut **from 4-6 weeks to a single day** via AWS GenAI/ML (w/ Quantiphi). — https://quantiphi.com/case-studies/modernizing-transcript-processing-with-qdox-for-higher-education/
- **Ohio State University** — AI/ML automated PDF accessibility remediation ("Remediate My PDF," open-sourced) for the ADA Title II deadline. — https://www.remediate-pdf.com/home
- **Vanderbilt University** — "Amplify" GenAI platform with agents for routine tasks (template formatting, lesson plans) across campus. — https://www.amplifygenai.org/

---

## 01 — Student & Family Services Concierge

- **During the 2024-25 FAFSA rollout, ~4 million of 5.4 million calls (about three-quarters) to Education's call center went UNANSWERED**, with the call center understaffed for 5 months. — *U.S. GAO, GAO-24-107407, "FAFSA: Education Needs to Improve Communications and Support" (Sept 24 2024)* `[gov/peer-reviewed]` — https://www.gao.gov/products/gao-24-107407
- **Highline College: 75% reduction** in financial-aid status emails/calls/in-person visits after self-service status tracking. — *AWS Public Sector Blog* `[vendor]` — https://aws.amazon.com/blogs/publicsector/making-financial-aid-simple-students-staff-highline-college-collaborated-with-aws-financial-aid-tracking-tool/
- **UT Austin: wait times cut from >15 min to <30 sec** at similar staffing. — *AWS Public Sector Blog* `[vendor]` — https://aws.amazon.com/blogs/publicsector/ut-austin-connects-students-answers-faster-using-amazon-connect/
- **Cost-per-contact benchmark (cross-industry, education ~$6-$12/ticket):** self-service portals resolve at **$1-$4** vs. phone **$17-$25**, chat **$10-$16**, email **$8-$15**. — *InvGate / industry service-desk benchmarks (2024-25)* `[sector-press — industry estimate, flag on slide]` — https://blog.invgate.com/cost-per-ticket
- **Multilingual demand:** the federal FSAIC offers service in English and Spanish only; institutional offices face the same multilingual gap. — *Federal Student Aid Help Center* `[gov]` — https://fsapartners.ed.gov/help-center/fsa-customer-service-center/service-centers-for-students/federal-student-aid-information-center-fsaic

## 02 — Personalized Tutor & Study Companion

- **Harvard physics RCT (194 students, fall 2023): students using a purpose-built AI tutor learned MORE THAN TWICE as much, in less time, than peers in an active-learning class**, and reported higher engagement/motivation. — *Kestin et al., "AI Tutoring Outperforms Active Learning" (2024); Harvard Gazette / Hechinger* `[gov/peer-reviewed — preprint + reputable coverage]` — https://news.harvard.edu/gazette/story/2024/09/professor-tailored-ai-tutor-to-physics-course-engagement-doubled/ and https://hechingerreport.org/proof-points-ai-tutor-harvard-physics/
- **Human tutoring works but is expensive/access-limited:** meta-analytic pooled effect **~0.37 SD** (≈50th→66th percentile); high-impact programs cost roughly **$1,200-$2,500+ per student per year**. — *Nickow, Oreopoulos & Quan, AERJ 2024 (meta-analysis of experimental evidence); EdResearch for Action (June 2024)* `[gov/peer-reviewed + foundation/research]` — https://journals.sagepub.com/doi/10.3102/00028312231208687 and https://edresearchforaction.org/research-briefs/design-principles-for-accelerating-student-learning-with-high-impact-tutoring/
- **Tech can lower the cost barrier:** substituting some tutor time with educational technology can cut costs by about **one-third** and halve the number of tutors needed without compromising effectiveness. — *Univ. of Chicago Education Lab (May 2024)* `[gov/peer-reviewed]` — https://educationlab.uchicago.edu/2024/05/study-finds-in-school-high-dosage-tutoring-combining-technology-and-tutor-time-can-successfully-accelerate-student-learning-reduce-costs-to-districts/

## 03 — Educator Copilot (lesson / rubric / quiz drafting, differentiation)

- **U.S. teachers work an average of ~53 hours/week (2024), vs. 44 for comparable working adults** — a 9-hour gap, much of it lesson planning, grading, and administrative work; public schools provide only ~266 min (~4.4 hrs) of planning time/week. — *RAND, 2024 State of the American Teacher Survey; NCTQ/EdSurge on planning time (2024)* `[gov/peer-reviewed — RAND]` — https://www.rand.org/pubs/research_reports/RRA1108-12.html and https://www.edsurge.com/news/2024-03-14-we-know-how-much-planning-time-teachers-get-on-average-is-it-enough
- **Teacher turnover is costly: ~$11,860 (small districts) to ~$24,930 (large districts) to replace ONE teacher**; national cost ~$2.2B/yr. — *Learning Policy Institute, "2024 Update: What's the Cost of Teacher Turnover?" (Sept 2024)* `[foundation/research]` — https://learningpolicyinstitute.org/product/2024-whats-cost-teacher-turnover-factsheet
- **Adoption signal:** 25% of K-12 teachers already used AI for planning/teaching in 2023-24; districts say GenAI helps with prep. — *RAND (2024)* `[gov/peer-reviewed — RAND]` — https://www.rand.org/pubs/research_reports/RRA134-25.html
- **Vanderbilt "Amplify"** includes agents that draft lesson plans and format documents to university templates. — *AWS Public Sector Blog* `[vendor]` — https://www.amplifygenai.org/

## 04 — Assessment, Grading & Feedback

- **An estimated ~40% of teaching time is spent on grading and feedback** (widely cited baseline; treat as estimate). — *Synthesized in AI-grading literature reviews (2024-25)* `[sector-press / literature — flag as estimate]` — https://link.springer.com/article/10.1007/s44163-025-00517-0
- **AI-assisted grading/feedback RCTs (4 undergraduate courses, ~300 students, 2023-24)** found AI-assisted grading comparable to human grading while delivering **faster turnaround**; immediate feedback especially benefits large/online classes. — *AI-assisted grading RCT, political science (peer-reviewed, 2025)* `[gov/peer-reviewed]` — https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12364334/
- **Vendor efficiency claim:** AI grading tools cited as increasing marking speed by ~80%. — *LearnWise (vendor guide)* `[vendor — flag on slide]` — https://www.learnwise.ai/guides/ai-powered-feedback-and-grading-in-higher-education
- **Named deployment:** Benchmark Education reports accelerated grading and stronger student feedback with GenAI on AWS. — *AWS Public Sector Blog* `[vendor]` — https://aws.amazon.com/blogs/publicsector/benchmark-education-accelerates-grading-and-boosts-student-feedback-with-generative-ai-on-aws/

## 05 — Student Success & Proactive Engagement

- **National first-year persistence reached a 10-year high of 76.5%; same-institution retention 68.2%** — but **22.4% of first-year students did NOT return for year two**, and nearly 14% left before their second term. Community-college retention is only ~55%. — *National Student Clearinghouse Research Center, Persistence & Retention 2024 (data for fall 2022 cohort)* `[gov/peer-reviewed — NSC]` — https://www.studentclearinghouse.org/nscblog/first-year-persistence-and-retention-rates-reach-10-year-high/
- **Each dropped student is lost recurring tuition revenue:** average net price per credit hour was **$642 at 4-year and $340 at 2-year institutions (2021-22)**; a single departing full-time student represents a full year (~24-30 credits) of forgone tuition plus the sunk recruitment cost (median **$2,433 private / $457 public** to recruit). — *NCES/IPEDS via BestColleges (2021-22) `[older — flag on slide]` `[gov]`; Ruffalo Noel Levitz recruitment-cost benchmarks* `[foundation/research]` — https://www.bestcolleges.com/research/college-cost-per-credit-hour/ and https://www.ruffalonl.com/
- **Early-alert + proactive advising lifts outcomes:** instructor-initiated academic alerts associated with **lower withdrawal rates and higher grades**; CCRC finds early-warning systems are most effective when paired with proactive advising. — *CCRC; peer-reviewed early-alert studies (2024-25)* `[gov/peer-reviewed + foundation/research]` — https://ccrc.tc.columbia.edu/research/guided-pathways.html and https://www.mdpi.com/2076-3417/15/11/6316

## 06 — Academic / College / Career Pathway Navigator

- **Transferring students lose, on average, ~43% of their credits** (vertical 2→4-yr ~26%, lateral 2→2-yr ~74%); credit loss directly lengthens time-to-degree and inflates cost, hitting lower-income students hardest. — *U.S. GAO, GAO-17-574, "Students Need More Information to Help Reduce Challenges in Transferring College Credits"* `[gov/peer-reviewed]` `[older — flag on slide; still the authoritative federal figure]` — https://www.gao.gov/products/gao-17-574
- **Excess/lost credits at completion:** transfer students who earn bachelor's degrees do so with substantial excess credits; recent analyses find students lose ~13 credits (≈a semester) on average and ~40% receive no credit for prior coursework. — *CCRC at Columbia; Community College Daily (Jan 2026)* `[foundation/research + sector-press]` — https://ccrc.tc.columbia.edu/publications/using-data-mining-explore-why-community-college-transfer-students-earn-bachelors-degrees-excess-credits.html and https://www.ccdaily.com/2026/01/fixing-the-transfer-process/
- **Guided pathways / degree-audit reforms improve early momentum:** colleges that fully scaled guided pathways saw more students earning 12+ credits in term one and 24+ in year one (5-yr horizon). — *CCRC / AACC guided-pathways evaluations (2024)* `[foundation/research]` — https://ccrc.tc.columbia.edu/easyblog/two-large-studies-measure-progress-guided-pathways.html
- **Advisor load context:** median caseload ~441 students/advisor at 2-year institutions (NACADA's most-cited survey; NACADA notes no single recommended ratio). — *NACADA Clearinghouse* `[foundation/research]` `[older — flag on slide]` — https://nacada.ksu.edu/Resources/Clearinghouse/View-Articles/Advisor-Load.aspx
- **Named deployment:** Illinois Tech cut credential evaluation **from 4-6 weeks to 1 day**. — *AWS Public Sector Blog* `[vendor]` — https://quantiphi.com/case-studies/modernizing-transcript-processing-with-qdox-for-higher-education/

## 07 — Document & Accessibility Services

- **ADA Title II final rule (DOJ, April 2024)** requires state/local government web content and mobile apps — **including public colleges and universities** — to meet **WCAG 2.1 Level AA**. **Compliance deadlines (per April 2026 DOJ extension): April 26 2027** for entities serving populations ≥50,000; **April 26 2028** for smaller entities/special districts. — *Federal Register (DOJ extension, Apr 20 2026); Inside Higher Ed (Apr 21 2026)* `[gov/peer-reviewed + sector-press]` — https://www.federalregister.gov/documents/2026/04/20/2026-07663/extension-of-compliance-dates-for-nondiscrimination-on-the-basis-of-disability-accessibility-of-web and https://www.insidehighered.com/news/government/colleges-localities/2026/04/21/doj-extends-web-accessibility-deadline
- **Inaccessible PDFs are the dominant compliance gap:** in one large coordinated complaint wave, **~95% of complaints involved PDF accessibility**; web-accessibility lawsuits exceeded **4,000 in 2024**, with colleges common targets; one advocacy group filed 2,400+ Title II complaints producing 1,000+ resolution agreements. — *MicroAssist / Accessibility.com 2024 lawsuit report* `[sector-press]` — https://www.microassist.com/digital-accessibility/school-website-accessibility-complaints/
- **Named deployment:** Ohio State + ASU CIC built AI/ML automated PDF remediation (Adobe API on AWS), open-sourced as "Remediate My PDF." — *AWS Public Sector Blog* `[vendor]` — https://www.remediate-pdf.com/home
- **Document-volume seasonality:** transcript/credential evaluation is labor-intensive — Illinois Tech compressed it from 4-6 weeks to 1 day. — *AWS Public Sector Blog* `[vendor]` — https://quantiphi.com/case-studies/modernizing-transcript-processing-with-qdox-for-higher-education/

## 08 — Operations / IT Service Desk

- **Education-sector cost per ticket ~$6-$12; self-service resolves at $1-$4 vs. phone $17-$25.** AI tools cited deflecting **45%+ of incoming queries** and cutting first-response time ~55%. — *InvGate / industry service-desk benchmarks (2024-25)* `[sector-press — industry estimate, flag on slide]` — https://blog.invgate.com/cost-per-ticket
- **Password resets are a large, automatable share:** Forrester's long-cited estimate puts the labor cost of a single help-desk password reset at **~$70** (some 2024 estimates ~$87, ~$795/employee/yr). — *Forrester (via service-desk literature, 2024)* `[sector-press / vendor-cited — flag as estimate]` — https://www.ghdsi.com/blog/evaluate-reduce-it-service-desk-cost-per-ticket
- **K-12 IT teams are small** and benefit disproportionately from deflection/automation. — *Incident IQ (sector vendor)* `[vendor — flag on slide]` — https://www.incidentiq.com/blog/reduce-support-tickets

---

## Labeling discipline (read before building any slide)

1. **Lead with the strongest class.** Headline each slide with a `[gov/peer-reviewed]` or `[foundation/research]` figure (GAO, NCES/IPEDS, NSC, RAND, CCRC, EDUCAUSE, Tyton, Learning Policy Institute, peer-reviewed RCTs). Use vendor and industry-estimate figures only as supporting color.
2. **Flag vendor figures on-slide.** Any `[vendor]` stat (including AWS customer stories and tool-maker efficiency claims) must be visibly attributed to the named institution/vendor on the slide itself — never presented as an independent benchmark.
3. **Flag industry estimates and dated figures.** Cost-per-ticket/contact ranges, the "40% of teaching time on grading" figure, the GAO-17 credit-loss numbers, and NACADA caseloads are either industry estimates or pre-2024; label them as such.
4. **Outcomes are modeled, not promised.** Present ROI as "documented at [institution]" or "modeled for a reference institution at your baseline," not as a guarantee.
5. **Prefer the primary URL.** Where a secondary source (press) summarizes a primary study (GAO/RAND/NSC/peer-review), cite both and link the primary.
