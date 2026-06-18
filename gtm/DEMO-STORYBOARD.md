# Demo Storyboard — EDU AI Agent Suite
### The Governed Concierge: What to Show, How to Show It, What to Say

> This storyboard scripts the POC demo of **Agent 01 — Student & Family Services Concierge** running in `EXTRACT_MODE=demo` (no API keys, no live systems, deterministic fixtures). It is written for the person in the room running the demo — the SA or delivery lead. Every governance moment is a talking point that answers the security and privacy objection in real time, with running software, not slides.
>
> Adapt the customer scenarios to the institution's vocabulary (their SIS, their department names, their seasonal pain) during Week 1 of the POC. Everything else runs as-is.

---

## Demo Philosophy

**Show the governance — not the chat.** The demo's job is not to show that the agent answers questions. Anyone with a browser can demo that. The demo's job is to show that the agent answers questions *under governed control* — deny-by-default authorization, PII masking, a human gate that cannot be bypassed, and a tamper-evident audit trail. Show those four things and the security/privacy objection collapses in the room.

**What to show:**
- A grounded public answer (no authentication required)
- A deny at the gateway (the most powerful 10 seconds in the demo)
- PII masking before the model sees anything
- A consequential action blocked behind the human gate, then released with reviewer approval
- The complete audit log for the session

**What NOT to show:**
- Open-ended "ask it anything" — untailored free-form demos invite hallucination and distract from governance
- Live SIS data — always run on fixtures in the POC; never connect to a live system without the pilot contract signed
- Comparisons to public ChatGPT or Copilot in the demo — mention them only to answer a direct question
- The agent saying "I can't do that" — show the gateway *blocking* it, not the model refusing

---

## Pre-Demo Setup Checklist

```bash
# Install (run once)
cd 01-student-family-concierge
pip install -r requirements.txt
pip install -e ../platform_core

# Verify demo runs end-to-end (no credentials needed)
EXTRACT_MODE=demo python -m pytest tests/ -q

# Start the demo
EXTRACT_MODE=demo python demo/demo_live.py
```

**Environment:**
- [ ] `EXTRACT_MODE=demo` confirmed set — no live system will be touched
- [ ] Terminal visible on screen share alongside a browser window for the audit log output
- [ ] `platform_core/edu_agent_platform/mcp_gateway/` directory open in an editor in a second window (you will point to the code when a skeptic asks "how does it actually work?")
- [ ] `OBJECTION-HANDLING.md` open in a tab for reference
- [ ] Customer scenarios scripted (2–3 from the pre-demo discovery call)
- [ ] Stakeholder map confirmed — who is in the room, what they care about (see table below)

---

## Who Is in the Room

| Stakeholder | What they need to see | Their likely objection |
|---|---|---|
| Executive sponsor (president / superintendent) | The outcome story — families served, staff freed, prudent governance | "Reputation risk / what if it goes wrong?" |
| CISO / security delegate | No standing credentials, deny-by-default, blast radius contained, provable audit | "Attack surface, credential harvesting, breach" |
| Privacy / FERPA officer | Identity-scoped retrieval, PII masked before the prompt, disclosure recorded | "FERPA, parent access, who controls data" |
| Academic or service owner | The workflow is recognizable; the agent does the right things | "Will this actually match our process?" |
| IT lead | It runs on AWS, it's auditable, I can turn it off | "Integration burden, operational overhead" |

**Brief the room before you start:** "What you're about to see is not a finished product and not a live system. It's a governed proof of concept — the same workflows and the same controls that would run in production, on synthetic data that mirrors your institution. My goal is for you to see the controls work, not just be told they work."

---

## Act 1 — The Public Concierge (No Authentication Required)

**Setup:** CIO, VP Student Success, and FERPA officer in the room. You're opening the demo.

**What you type/click:** A public-mode query — e.g., "What are the financial aid deadlines and how do I check my application status?" — run against the fixture knowledge base.

**What the audience sees:** A plain-language answer with a grounding citation pointing to the source document.

**Talking point:**
> "Before authentication — the most common question your call center, email inbox, and front-desk staff field — a family member asking about financial aid deadlines at 11 PM on a Sunday when your office is closed. Notice two things. First, the answer traces to a specific piece of your approved content — not something the model made up. That's grounding verification: if the answer isn't in your approved material, the agent says so rather than inventing a deadline. Second, no authentication was required, and no student record was touched."

**Governance moment:** Point to the grounding source citation.
> "Grounding is a control, not a hope. Every fact in a family-facing or student-facing answer must trace to your approved content — policy docs, the catalog, your FA guidance — or the agent fails fast rather than producing a wrong deadline with false confidence."

**Common question here:** "What if our content is out of date?" Answer: grounding-content updates are versioned — the agent never grounds against stale material; updates go through change control.

---

## Act 2 — Authentication and the Deny-By-Default Gateway

**Setup:** CISO has just watched Act 1. Now you demonstrate the access control architecture.

**What you type/click:** Authenticate as a student. Run a status query — e.g., "Can you check my application status?" Show the gateway authorization log alongside the response.

**What the audience sees:** The gateway log showing: ALLOW — student identity verified, tool `check_application_status` authorized, short-lived scoped token issued.

**Talking point:**
> "The gateway just did three things before the agent got any data. One: it verified the student's identity claims from your IdP. Two: it checked that `check_application_status` is in both the agent's tool grants *and* this student's role entitlements — deny-by-default means if either list doesn't include the tool, the call stops here. Three: it issued a short-lived, single-purpose token for this one call. No standing credentials, no broad key sitting in the agent that an attacker can harvest."

**Now demonstrate the deny:** Attempt `get_student_schedule` with a guardian identity for a student who has turned 18.

**What the audience sees:** DENY entry in the audit log — with the deny reason.

**Talking point:**
> "Denied. The guardian's role entitlement no longer includes access to this student's record post-18. That's the age-of-majority transfer the FERPA officer cares about — enforced at the gateway, not by trusting the model to refuse."

**Governance talking point for the CISO:**
> "The authorization logic lives *outside* the model, in this file here." *(Point to `platform_core/edu_agent_platform/mcp_gateway/gateway.py`.)* "A prompt injection hidden in an email attachment cannot grant itself elevated access — because the model doesn't evaluate authorization, the gateway does, before any tool call is made."

**Common question here:** "Can we see the code?" Answer: yes — walk them to the `mcp_gateway/` directory. The enforcement logic is readable Python. A security reviewer can audit it without an AWS account.

---

## Act 3 — PII Masking Before the Prompt

**Setup:** Privacy officer is watching closely after the gateway demo.

**What you type/click:** Show the PII masker operating — raw fixture data (student name, ID, DOB) in, masked output out, going into the prompt.

**What the audience sees:** Side-by-side: the raw fixture record and the masked version that enters the model context. Student name → `[STUDENT-A]`, ID number → `[ID-7823]`, date of birth → `[DOB-MASKED]`.

**Talking point:**
> "The student's name, their ID number, their date of birth, their guardian's contact details — masked to stable pseudonyms before the model sees anything. The model reasons over [STUDENT-A], not Maria Garcia, student ID 7823-44. The audit log records the pseudonym. Real identifiers never enter a prompt or a log."

**Governance talking point for the privacy officer:**
> "This is the EDU analog of HIPAA Safe-Harbor masking, tuned to FERPA-protected identifiers and COPPA's heightened bar for children under 13. If there is ever a prompt-injection attempt that tries to exfiltrate student data, it gets pseudonyms — not real records."

---

## Act 4 — The Human-Gated Write (The Most Important Moment)

**Setup:** Executive sponsor and CISO. This is the centerpiece governance demonstration.

**What you type/click:** Initiate a `draft_family_message` or `comms.send_message` tool call — a consequential action.

**What the audience sees:** PENDING_APPROVAL entry in the audit log. The agent cannot proceed. A reviewer notification is generated.

**Talking point:**
> "The gateway blocked it. The agent cannot send a message to a family without a named human reviewer — a staff member in the right role — approving it first. The action sits in the HITL queue. The agent cannot unblock itself. No prompt it receives, no injection anyone could attempt, can make this action execute without that human approval. The gateway gate runs outside the model."

**What you type/click:** Provide the simulated reviewer approval.

**What the audience sees:** ALLOW entry in the log — with the reviewer identity bound in alongside the action.

**Talking point:**
> "The reviewer approves, the gateway mints the write token, the action executes, and the audit records the reviewer's identity alongside the action. That's the human gate the FERPA officer needs: who approved this consequential action, and when."

**Governance talking point for the executive sponsor:**
> "This same gate is what prevents the agent from autonomously filing a financial-aid determination, setting a grade, making an admissions decision, issuing a disciplinary action, deciding special-education eligibility, or placing a student. The institution is not handing decisions to software. A named human in the correct role decides every consequential action — and is recorded."

**Common question here:** "What if the reviewer queue backs up?" Answer: the managed service monitors queue depth and approval latency; an alarm fires if any consequential item ages past an agreed threshold. A stalled queue is visible and alarmed — a silently blocked student action is not.

---

## Act 5 — The Audit Log Walkthrough

**Setup:** CISO and FERPA officer. You're showing what they can produce to a parent or an auditor.

**What you type/click:** Display the full audit log for the demo session.

**What the audience sees:** Four log entries: ALLOW (student read), DENY (guardian age-of-majority block), PENDING_APPROVAL (family message queued), ALLOW (message after reviewer approval with reviewer identity).

**Talking point:**
> "Let me walk through everything that just happened. ALLOW — the student's authenticated status lookup, with their pseudonymized identity, the tool, the timestamp, and the token reference. DENY — the guardian's attempt on a post-18 record, with the deny reason. PENDING_APPROVAL — the family message queued for human review. ALLOW — the message after reviewer approval, with the reviewer identity bound in. Four entries. No real student identifiers. Every action, every block, every approval, in order, append-only — this log cannot be edited retroactively."

**Governance talking point:**
> "This is what you show a parent who asks what happened, an auditor reviewing a disclosure, or OCR in a compliance inquiry. FERPA expects institutions to record certain disclosures. This log is that record, automatically, for every agent interaction — across all eight agents, because the audit is shared platform."

---

## Act 6 — Customer Scenario Run

**Setup:** Service owner is now the primary audience. Run the 2–3 scenarios agreed in Week 0.

**Scenario 1:** [Customer-specific — e.g., "A parent calls at 8 PM asking why their student's FAFSA is still showing 'processing' when the semester starts in two weeks."]

**Talking point:** Run against fixtures. Narrate the grounding source. Show the identity check if authenticated, and the action or answer produced.

---

**Scenario 2:** [Customer-specific — e.g., "A new student doesn't know what documents they need to submit for enrollment and keeps getting transferred between offices."]

**Talking point:** Run the public read-only path — no authentication needed, grounded in the institution's enrollment checklist.

---

**Scenario 3 (optional):** [Customer-specific — e.g., "An advisor wants to open a case for a student who has missed three appointments and isn't responding to email."]

**Talking point:** Show the authenticated write path and the HITL gate if the case creation is consequential.

---

After the scenarios:
> "Everything you just saw was running against synthetic data shaped like your institution type. If we ran the POC against your specific scenarios, we'd load a slice of your public policy content as the grounding source, use your department names and your vocabulary, and script the two or three workflows your service owner said were most acute. The controls don't change — the scenarios become yours."

---

## Act 7 — What the POC Proves and What Comes Next

**Talking point:**
> "Let me be direct about what you just saw and what you didn't see. What the POC proves: the bounded-agent model is real — the agent retrieves, drafts, and routes, and never autonomously decides a grade, admission, discipline determination, financial-aid award, eligibility, or placement. The MCP gateway enforces deny-by-default authorization, the human gate, PII masking, and the audit — and those controls live outside the model, so they hold regardless of what any prompt says."

> "What the POC did not prove: how the agent performs against *your* live SIS or LMS data (that's the pilot). Whether your IdP can cleanly express guardian relationships and age-of-majority (that's the assessment). Whether your student-facing surfaces meet WCAG 2.2 AA (that's the pilot exit gate). And the measured outcome — the actual deflection rate and cycle-time improvement in your environment — that's what the pilot baselines and measures."

> "If the answer today is go, the next step is a 6–12 week pilot: one live system of record, in your AWS account, with the gateway built first in Phase 1 — because the gateway is what passes your security and privacy review, and it's what every subsequent agent reuses."

**Close:**
> "The question is: which system is the right first pilot target, and what is the baseline we'd measure against? Let's talk about what your data looks like today."

---

## Objection Handling in the Room

| Moment it arises | Objection | Response |
|---|---|---|
| After Act 2 (auth) | "This is just an API gateway." | "It authorizes per action, per user, per role — not just routes traffic. It gates consequential steps to a named human, issues short-lived scoped keys, and produces the FERPA-aligned audit trail. An authorization-and-accountability layer, not a proxy." |
| After Act 3 (PII mask) | "What if someone tries to inject the real ID through a prompt?" | "The masker runs before the model sees anything. Injection into the prompt gets pseudonyms back. And the authorization check lives outside the model — a prompt cannot grant the call elevated access." |
| After Act 4 (human gate) | "What if the HITL queue backs up and students wait?" | "The managed service monitors queue depth and latency; an alarm fires if any item ages past an agreed threshold. A stalled queue is visible and alarmed. A silently blocked action is not — that's why the gate exists." |
| After Act 5 (audit) | "Can we really show this to OCR?" | "The audit is PII-masked and append-only. It records who accessed what, on what basis, and who approved. That is the FERPA disclosure recordkeeping record. The institution's privacy counsel determines what to produce; the log is what they produce from." |
| Any point | "We're not on AWS." | "The demo runs locally. The pilot needs the customer's AWS account and Bedrock access. If that's not available, the assessment identifies the path — and we can fund the infrastructure through AWS PoA credits." |
| Any point | "What about [state] privacy law?" | "State-law mapping is the assessment workstream. The platform is parameterized — data residency, consent capture, retention, and prohibited use are configuration. The assessment maps your state's obligations to the platform configuration." |
| Any point | "We tried AI and it stalled at security." | "That's the exact gap this solves. The reason it stalled was the governance review couldn't be answered. Now you've watched it happen — deny, PII mask, human gate, audit. Run this with your CISO and privacy officer in the room." |

---

## The Go/No-Go Conversation

Ask these questions to drive to the decision:

1. **"Did the security and privacy stakeholders see — not just hear — that the governance is enforced?"** If yes: "Can you tell me in your own words what you'd say to the CISO about why this is different from a chatbot with API keys?"
2. **"Were the scenarios recognizable? Did the service owner see their workflow?"** If yes: "Which scenario was most urgent — and what's the baseline metric we'd measure it against?"
3. **"Any objections or concerns we didn't address during the demo?"** Log them. Promise a written response in the POC findings memo.
4. **"Based on what you saw, is the case for a pilot made?"** If yes: "Let's agree on the live system of record and the baseline metrics today."

**If go:** Move to the recommended pilot scope and hand off to `offerings/PILOT-OFFERING.md` and `gtm/SOW-TEMPLATE.md`.

**If not yet:** Deliver the POC findings memo with responses to every concern raised. Agree on what question needs to be answered before go/no-go. Schedule the answer.

---

## Leave-Behinds (Send Within 24 Hours)

1. **The recorded demo** — the session recording with all five governance moments visible
2. **The POC findings memo** — what was demonstrated, what wasn't, which objections were raised and answered
3. **`gtm/TEASER-DECK.md`** — the 5-slide executive summary
4. **`offerings/TPRM-DUE-DILIGENCE-PACKET.md`** — for the CISO and procurement team to begin the vendor review
5. **`docs/STAKEHOLDER-SECURITY-BRIEFINGS.md`** — tailored for the CISO and privacy officer to share internally
6. **`gtm/roi-calculator/EDU-AI-Suite-ROI-Calculator.xlsx`** — for the CFO or VP to plug in their own numbers
7. **Proposed pilot scope** — one paragraph: which agent, which system, what baseline, what timeline

---

## Quick Reference: The Five Governance Moments

| # | Moment | What to say | What to show |
|---|---|---|---|
| **1** | Grounded public answer | "Traces to approved content or fails fast — no invented deadlines." | Grounding source citation in the response |
| **2** | Authenticated read / deny-by-default | "The agent can never exceed the human; deny-by-default enforced at the gateway, not by trusting the model." | ALLOW log entry; DENY log entry for the age-of-majority case |
| **3** | PII masking | "Student identifiers replaced before the model sees anything — pseudonyms in the prompt and the log." | Raw fixture data vs. masked input to model |
| **4** | Human-gated write | "Consequential action blocked until a named human is bound into the record — cannot be bypassed by any prompt." | PENDING_APPROVAL → reviewer approval → ALLOW, with reviewer identity in the log |
| **5** | Audit log | "Every attempt, allowed or denied, PII-masked, append-only — FERPA disclosure recordkeeping, automatic." | Full session audit log displayed and walked through |
