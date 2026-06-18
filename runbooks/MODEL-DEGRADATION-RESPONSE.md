# Model & Agent Degradation Response Runbook
### EDU AI Agent Suite

> How to detect and respond when model or agent quality degrades: the signals monitored, the thresholds to tune, and a response/rollback procedure anchored on the prompt registry — with the eval harness and fairness checks as the gate to resume.

---

## The framing that matters (and the bright line)

Because every consequential action is **human-gated**, degradation in this platform is a **quality and trust issue, not an autonomous-harm issue.** A degraded model does not silently issue a wrong grade or make a placement decision — the agents never decide **grades, admissions, discipline, financial aid, special-education eligibility, or student placement** on their own. Instead, degradation surfaces as **reviewers rejecting or revising more drafts** before anything reaches a student, and as **eval and fairness checks failing** in CI. The harm is caught by humans and by tests, upstream of the student. That changes the response: the goal is to detect the drop in quality early and roll back cleanly, not to scramble to undo something that already harmed a learner.

The bright line stays visible throughout this runbook for that reason — it is *why* degradation is survivable.

---

## 1. Signals monitored

For each signal: how it is detected, threshold guidance (the customer tunes the actual numbers), and the first response.

### 1.1 Eval-harness regression
- **How detected:** structural golden-artifact regression in `governance/evals/` — advising plans, intervention drafts, rubric-graded feedback, accessible-content output. Runs in CI with no API key.
- **Threshold guidance:** any regression against a reviewed golden artifact is a failure; CI should be red. There is no "acceptable" silent regression on a reviewed artifact.
- **Response:** treat a CI failure as a blocker to deploy/resume. Identify what changed (prompt? model? KB? connector?) per §3.

### 1.2 Prompt-hash drift
- **How detected:** the prompt registry (`prompt_registry.py`, `prompt_manifest.json`) hash-pins prompts; **CI fails on un-bumped drift.** A changed prompt with an unchanged hash is the signal.
- **Threshold guidance:** zero tolerance — any un-bumped drift fails. A bumped (intentional) change must pass evals before it ships.
- **Response:** if drift is unexpected, you may have an unauthorized or accidental prompt change — investigate as a change-control and possibly a security issue (see `INCIDENT-RESPONSE.md` Playbook B). If intentional, run the eval gate before resuming.

### 1.3 Grounding-failure spikes
- **How detected:** `grounding.py` — every fact, deadline, policy statement, and figure in a student/family-facing artifact must trace to approved institutional content; **ungrounded claims fail fast.** A spike in grounding failures is monitored in CloudWatch.
- **Threshold guidance:** set a baseline grounding-failure rate per agent; alarm on a sustained deviation above it.
- **Response:** a spike can mean a model change, prompt drift, a changed knowledge base, or an injection attempt. Freeze the affected agent (§2) and root-cause (§3).

### 1.4 Fairness-metric drift
- **How detected:** `governance/fairness/` — equity/representativeness checks plus false-positive/false-negative monitoring, specifically on **student-success targeting and intervention recommendations** (Agent 05).
- **Threshold guidance:** customer sets equity tolerances and FP/FN bounds appropriate to its population and policy; alarm on drift beyond them.
- **Response:** fairness drift is high-priority even at low volume — it bears on anti-discrimination obligations. Freeze the affected targeting/recommendation path and root-cause before resuming.

### 1.5 Guardrail block-rate changes
- **How detected:** Bedrock Guardrails block-rate metric in CloudWatch.
- **Threshold guidance:** baseline the normal block rate per agent; alarm on a significant rise or fall. A *fall* can mean Guardrails weakened; a *rise* can mean a model/prompt change is producing more blockable output (or an attack — see Incident Response).
- **Response:** confirm Guardrail config is unchanged; correlate with prompt/model changes (§3).

### 1.6 HITL rejection-rate increase
- **How detected:** rejection/revision rate from the HITL queue (CloudWatch; see `HITL-QUEUE-OPERATIONS.md`).
- **Threshold guidance:** baseline the normal rejection and one-bounded-revision rate per reviewer role; alarm on a sustained rise.
- **Response:** this is often the **earliest human-visible signal** — reviewers are catching degraded drafts before students see them. Treat a sustained rise as a degradation event and root-cause it; the humans have already contained the harm.

### 1.7 Latency / error rate
- **How detected:** CloudWatch invocation latency and error-rate metrics.
- **Threshold guidance:** customer-set latency and error-rate alarms per agent.
- **Response:** distinguish infrastructure (handle per `INCIDENT-RESPONSE.md` / `DR-RUNBOOK.md`) from quality. Latency alone is operational; latency plus rising rejection is degradation.

---

## 2. Response and rollback procedure

```
TRIAGE → FREEZE → ROOT-CAUSE → ROLLBACK (prompt registry) → RE-GATE (evals + fairness) → RESUME → FEED BACK
```

### Step 1 — Triage
Correlate the signals (§1). A single signal is a lead; several together (e.g., grounding spike + rising rejection + a recent change) is a degradation event. Assign severity per `INCIDENT-RESPONSE.md`.

### Step 2 — Freeze
**Pause the affected agent or tool at the gateway immediately** — the institution can disable any agent or tool at the enforcement point, and no agent has a standing credential or direct path to a system of record. Freezing stops new degraded drafts from being produced. In-flight items in the HITL queue remain gated; nothing consequential proceeds without a human approval, so freezing is safe.

### Step 3 — Root-cause
Identify what changed:
- **Model version change?** A Bedrock model update under the agent. This is exactly what prompt-hash pinning and model-change control exist to catch.
- **Prompt drift?** Check the prompt registry / `prompt_manifest.json` against the deployed artifact.
- **KB content change?** A knowledge-base re-ingest that altered or removed grounding sources.
- **Connector data change?** A connector now returning different fields or shapes, changing what the agent grounds on.

### Step 4 — Rollback via the prompt registry
- **Revert to the last hash-pinned, known-good prompt version** from the registry. The registry is the rollback target precisely because every prompt is versioned and hash-pinned.
- For a **model change**, apply model-change control: pin/repoint to the known-good model version and treat the new version as a change that must pass the eval gate before adoption.
- For a **KB or connector change**, revert the content/field change or re-scope it, then re-validate grounding.

### Step 5 — Re-gate: evals + fairness as the condition to resume
**Do not resume on a hunch that it's fixed.** The condition to re-enable the agent is:
- `governance/evals/` passes (no golden-artifact regression), **and**
- `governance/fairness/` passes (equity + FP/FN within tolerance) for any agent that touches student-success targeting or recommendations, **and**
- the prompt registry is green (no un-bumped drift), **and**
- the HITL gate test passes (`governance/tests/test_hitl_gates.py`).

Only when the gate is green do you re-enable the agent/tool at the gateway.

### Step 6 — Resume and confirm
Re-enable at the gateway. Watch the same signals (§1) — especially HITL rejection rate and grounding-failure rate — to confirm the degradation cleared.

### Step 7 — Feed back into governance
- Add the degradation as a **new eval case** in `governance/evals/` so this regression is caught structurally next time.
- If the cause was an attack vector (e.g., injection-induced ungrounded output), add a **red-team case** in `governance/redteam/`.
- Record the prompt-registry change (the revert and any subsequent fixed-forward version).

---

## 3. Root-cause reference

| Symptom cluster | Most likely cause | First check |
|---|---|---|
| Grounding spike + rising rejection, no deploy | Model version change underneath the agent | Bedrock model version vs known-good pin |
| Eval + prompt-hash both red | Prompt drift (accidental or unauthorized) | `prompt_manifest.json` vs deployed prompt; change-control log |
| Grounding spike, stable model + prompt | KB content change | Recent KB re-ingest / source corpus change |
| Output shape changed, more revisions | Connector data/field change | Connector field scope vs expected schema |
| Fairness drift on Agent 05 only | Targeting logic / data distribution shift | `governance/fairness/` FP/FN + representativeness output |
| Guardrail block-rate drop | Guardrail config weakened | Guardrail configuration vs baseline |

> **Customer must configure:** every threshold and baseline in §1, the alarm routing, and the equity/FP-FN tolerances in fairness. The detectors and the rollback mechanism ship; the numbers that define "degraded" for your population are yours to set and own.

---

## 4. Why this is safe by design

The agent is frozen at the gateway, the rollback target is a hash-pinned known-good prompt, the resume condition is a passing eval + fairness + HITL-gate suite, and — underneath all of it — **no consequential decision ever happened autonomously.** Degradation was caught by reviewers rejecting drafts and by tests failing in CI, both upstream of any student. That is the bright line doing its job: quality problems surface as extra human review and red CI, not as harm to a learner.
