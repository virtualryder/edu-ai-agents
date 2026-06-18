# Incident Response Runbook
### EDU AI Agent Suite

> This runbook covers detection through post-incident review for the governed agent platform, plus two detailed playbooks for the incident types most specific to a student-data agent platform: a **student-data privacy / FERPA incident** and a **prompt-injection / PII-exfiltration incident**.
>
> **This is a reference, not your incident-response policy.** Every severity threshold, notification timeline, and contact must be replaced with values from your institution's IR plan, FERPA program, and state-law obligations. Where a timeline depends on law, the answer is "it depends on your state" — and this runbook says so rather than inventing a number.

Keep the bright line in view throughout: the agents never autonomously decide **grades, admissions, discipline, financial aid, special-education eligibility, or student placement.** That boundary shapes the blast radius of almost every incident here — controls hold *outside* the model, so even a fully successful attack on the model cannot exceed the permissions of the human in the loop or bypass the human gate.

---

## 1. Severity classification

Declare severity at triage; re-classify as facts change. When in doubt, classify **up** — a privacy incident under-classified is harder to defend than one over-classified.

| Severity | Definition | Examples |
|---|---|---|
| **SEV1** | Confirmed or strongly suspected unauthorized disclosure of student PII; platform-wide outage; bright-line breach (an agent caused a consequential decision without the human gate) | An agent surfaced one student's record to a different authenticated identity; a write occurred without a bound reviewer identity; the audit trail is unavailable or shows tampering signals; KMS CMK unavailable across the environment |
| **SEV2** | Contained privacy risk or significant degradation; single-agent outage with student impact | A single tool returned an over-broad field set but exposure appears contained; sustained grounding-failure or Guardrail-block spike on a student-facing agent; HITL queue stalled past SLA causing real delay |
| **SEV3** | Limited-impact issue; no confirmed PII exposure; workaround available | Elevated deny rate from a misconfigured role mapping (failing *safe*); intermittent connector errors; a single stale task token blocking one approval |
| **SEV4** | Minor / cosmetic; no student or compliance impact | Dashboard widget error; non-blocking log-noise; a known-benign alarm flap |

> **Customer must configure:** the precise quantitative thresholds (error rate %, queue depth, latency) that separate SEV2 from SEV3, and the paging behavior per severity. The qualitative anchors above are the starting point.

---

## 2. General response flow

```
DETECT → TRIAGE → CONTAIN → ERADICATE → RECOVER → POST-INCIDENT
```

1. **Detect.** A CloudWatch alarm fires, a reviewer or user reports something, or routine audit-trail review surfaces an anomaly. Capture the first signal and timestamp it.
2. **Triage.** Assign severity (§1). For SEV1/SEV2, declare an incident and page the Incident Commander. The IC pulls in the privacy officer and/or CISO per the playbooks below.
3. **Contain.** Stop the harm from spreading without destroying evidence. The institution can **disable any tool or agent immediately at the gateway** and **revoke scoped tokens** — these are the primary containment levers. Containment never includes editing or deleting audit records (you cannot, by design — `deny:UpdateItem`/`deny:DeleteItem`).
4. **Eradicate.** Remove the root cause — revoke an over-broad grant, fix a role mapping, tighten a connector field scope, tune a Guardrail, revert a prompt to a known-good hash.
5. **Recover.** Re-enable the tool/agent only after the fix is verified. For quality incidents, the eval harness + fairness checks are the gate to resume (see `MODEL-DEGRADATION-RESPONSE.md`). Confirm the audit trail is continuous across the incident window.
6. **Post-incident.** Run the review in §6 and feed findings into governance (evals, red-team, prompt registry).

---

## 3. Roles during an incident

| Role | Owns |
|---|---|
| **Incident Commander (IC)** | The incident end to end: declaration, severity, the timeline, who is doing what, and the decision to close. Single point of coordination. |
| **On-call operator / SRE** | Hands on keyboard: containment actions at the gateway, evidence preservation, restore steps. |
| **Privacy officer / FERPA program owner** | The unauthorized-disclosure determination and all breach-notification decisions and timelines. Final word on anything FERPA/state-law. |
| **CISO / security lead** | Scope-of-compromise call, forensics, and security containment (token revocation, key posture). |
| **Communications lead** | Internal and external messaging, working only from the privacy officer's and IC's determinations. |

> **Customer must configure:** the named people, the paging order, and the authority each role carries. The suite ships the role definitions, not the roster.

---

## 4. Playbook A — Student-data privacy / FERPA incident

**Trigger scenarios.** An agent surfaced one student's record to a different identity; an authorization-scope failure returned data the requesting role had no right to; a connector returned an over-broad field set that reached a prompt, a UI, or an audit record; a guardian saw a record whose FERPA rights had transferred to the (now adult) student.

### 4.1 Detection signals

- **Audit-trail anomaly.** An `ALLOW` whose requesting identity/role does not intersect the data subject, an access without a corresponding purpose-of-use, or a write without a bound reviewer identity. The append-only trail is the primary detector here.
- **Deny-rate change.** A *drop* in deny rate can mean authorization is failing open; a *spike* can mean a role mapping broke (usually failing safe, but still worth triage).
- **A report.** A student, guardian, educator, or staff member says they saw something that wasn't theirs. Treat every such report as SEV2 until disproven.

### 4.2 Immediate containment

1. **Disable the affected tool or agent at the gateway immediately.** No agent has a standing credential or a direct path to a system of record, so disabling the tool target stops further access at the enforcement point.
2. **Revoke the scoped tokens** issued to the affected agent/session via AgentCore Identity / STS. Tokens are short-lived by design; revoke rather than wait for expiry.
3. **Do not modify or delete any audit record.** This is impossible by policy and would also be evidence destruction. Preserve, do not prune.
4. Notify the **privacy officer** — this playbook is theirs from this point. The operator supports.

### 4.3 Investigation using the append-only audit trail

The audit trail answers the three questions a FERPA disclosure assessment turns on. Reconstruct, for the incident window:

- **Who accessed what** — requesting identity and `custom:edu_role`, the tool invoked, the data subject (via stable pseudonym; de-pseudonymization is a controlled step the privacy officer authorizes), and the system-of-record lineage.
- **On what basis** — the purpose-of-use recorded for the tool call and the role-entitlement intersection that produced the `ALLOW`.
- **Who approved** — for any write/consequential action, the bound reviewer identity. An action without one is itself a bright-line finding (escalate to SEV1).

Pull the relevant CloudTrail events as well — the same append-only record unifies gateway events and AWS API calls.

### 4.4 FERPA unauthorized-disclosure assessment

Owned by the privacy officer. The platform does not make this determination; it provides the evidence. Considerations:

- Was personally identifiable information from an **education record** disclosed to a party without a right of access? (The masker means many records carry pseudonyms, not direct identifiers — this is material to the assessment and to whether a disclosure occurred at all.)
- Does an exception apply (e.g., school-official / direct-control)? The gateway's purpose-of-use enforcement is the evidence that data was used only for the authorized purpose.
- **Age-of-majority / rights transfer.** FERPA rights transfer to the student at 18 or on postsecondary enrollment. A guardian seeing a now-adult student's record may be a disclosure even though the same access was lawful a year earlier. Check the role mapping the IdP carried.

### 4.5 Breach-notification considerations

> The platform supports notification; it does not decide it. The privacy officer, with counsel, owns every call below.

- **FERPA recordkeeping.** FERPA itself centers on recordkeeping of disclosures rather than a fixed breach-notification clock. Ensure the disclosure is recorded.
- **State breach-notification laws (~140 statutes).** Most states have their own student-data-privacy and breach-notification requirements; **timelines, definitions of "breach," and notification recipients vary by state.** There is no single number to put here — the customer maps their state obligations during the assessment phase, and the privacy officer applies them per incident.
- **Who is notified.** Guardians and/or the eligible student, depending on age-of-majority / rights-transfer status. Get this right — notifying a guardian about an adult student's record can itself be a disclosure problem.
- **Under-13 (COPPA).** Heightened sensitivity; coordinate notification with the school-authorized-consent posture.

### 4.6 Records to preserve

- A **WORM snapshot** (S3 Object Lock, COMPLIANCE mode) of the relevant audit window, the affected tool configuration, and the role mappings in effect. Object Lock means these cannot be altered or deleted for the retention period — exactly what you want for an incident record.
- The CloudWatch metric history and alarm state for the window.
- The originating report (if any), preserved verbatim.

---

## 5. Playbook B — Prompt-injection / PII-exfiltration incident

**Trigger scenario.** Injection hidden in a **student-submitted document or an inbound email** — the agent ingests attacker-controlled text that tries to make it exfiltrate data, call an unauthorized tool, or bypass the human gate. This is a **named red-team scenario** (`governance/redteam/`); treat a real occurrence as validation that the controls matter, not as a novel surprise.

### 5.1 Detection signals

- **Grounding-failure spike.** Injection often pushes the model toward claims it cannot ground in approved content; `grounding.py` fails those fast, so a spike is a signal.
- **Guardrail blocks.** A cluster of Guardrail blocks (PII denial, prohibited-behavior, topic filters) on a single agent or input source.
- **Anomalous tool-call patterns.** Attempts to call tools the agent isn't granted, or calls outside the normal sequence — all of which the gateway denies, but the *attempt* is the signal.
- **PII-masker alerts.** The masker runs before any content enters a prompt or audit record; unusual recognition activity or attempts to surface record-linkable fields is an early warning.

### 5.2 Containment — and why the blast radius is bounded

The defining property of this platform: **the controls hold outside the model.** A successful injection changes what the *model* says; it cannot change what the *system* permits.

- **Authorization is deny-by-default and identity-scoped.** The injected instruction runs, at most, with the permissions of the human on whose behalf the agent acts — and only on tools the agent is granted, intersected with that human's role entitlements. It cannot self-escalate.
- **The HITL gate is framework-enforced.** A consequential action still blocks until a named reviewer's identity is bound into the record. Injection cannot mint a write token; only a verified approval does.
- **The audit trail is append-only.** The attack and every denied attempt are recorded and cannot be erased.
- **The PII masker limits what was ever exposed.** Because masking runs before content enters the prompt, an exfiltration attempt typically reaches pseudonyms, not raw FERPA-protected identifiers — shrinking the blast radius before containment even begins.

Immediate steps: disable the affected tool/agent at the gateway, revoke scoped tokens, and quarantine the offending input source (the document or inbound email) for analysis.

### 5.3 Eradication

1. **Prompt-hash review via the prompt registry.** Confirm the running prompt matches the hash-pinned, known-good version in `prompt_manifest.json`. CI fails on un-bumped drift, but verify the deployed artifact directly during an incident.
2. **Guardrail tuning.** If the injection class slipped past Guardrails, tune the relevant filter (PII / prohibited-behavior / topic). Guardrail configuration is a customer responsibility.
3. **Connector field-scoping review.** Tighten the fields a connector returns so that even a coerced tool call yields the minimum necessary — reinforcing data minimization and no-redisclosure.
4. **PII-masker review.** Confirm the masker recognized and pseudonymized the relevant identifiers for the attacking input class.

> Because outputs are human-gated and authorization is external to the model, a prompt-injection incident is contained even when the injection "succeeds" at the model layer. The work is closing the gap so the *attempt* is blocked earlier and adding the case to the red-team suite.

---

## 6. Escalation matrix

| Severity | Page immediately | Engage | External notification |
|---|---|---|---|
| **SEV1** | IC + privacy officer + CISO | Comms lead; executive sponsor | Likely required — privacy officer determines per FERPA recordkeeping + applicable state breach-notification law and timelines |
| **SEV2** | IC + (privacy officer **or** CISO, per playbook) | Comms lead on standby | Privacy officer assesses; often not required if contained |
| **SEV3** | On-call operator; IC informed | Privacy officer consulted if any PII question | Generally none |
| **SEV4** | On-call operator handles | — | None |

> **Customer must configure:** paging targets, escalation timers, and the executive/legal notification path. The mapping of severity to *who* is the suite's contribution; the *contact* is yours.

---

## 7. Communication templates

> Keep templates short, factual, and free of speculation. The communications lead drafts from the privacy officer's and IC's determinations only — never ahead of them.

Maintain (customer-owned, reviewed by counsel) at least:

- **Internal incident declaration** — severity, scope known so far, IC, next update time.
- **Reviewer/staff advisory** — when an agent or tool is disabled and a manual fallback applies.
- **Guardian / eligible-student notification** — for confirmed disclosures, respecting age-of-majority / rights-transfer status; wording and timing per applicable state law.
- **Resolution / all-clear** — what happened, what was done, what changed.

The suite intentionally ships **no pre-written external notification text** — that content is legal and state-specific and must be owned by the institution.

---

## 8. Post-incident review checklist

Run within a fixed window after close (customer sets the SLA). The output is not just a writeup — it is **new controls fed back into governance.**

- [ ] Timeline reconstructed from the append-only audit trail and CloudTrail, with a WORM snapshot preserved.
- [ ] Root cause identified (authorization, role mapping, connector scope, Guardrail gap, prompt drift, model change, or genuine novel attack).
- [ ] Severity and any disclosure determination confirmed by the privacy officer; notifications (if any) documented.
- [ ] **New eval case** added to `governance/evals/` capturing the failure as a golden-artifact regression.
- [ ] **New red-team case** added to `governance/redteam/` for any injection / exfiltration / authorization-bypass vector.
- [ ] **Prompt registry** updated if a prompt was the cause or the fix (new hash-pinned version, CI green).
- [ ] HITL gate behavior confirmed correct (or fixed) — assert via `governance/tests/test_hitl_gates.py`.
- [ ] Bright line confirmed intact: no consequential decision occurred without a bound reviewer identity. If one did, that is the headline finding.
- [ ] Action items assigned with owners and dates; thresholds/alarms tuned if detection lagged.
