# HITL Queue Operations Runbook
### EDU AI Agent Suite

> How to operate the human-approval queue: what it is, which actions require approval, who reviews what, the SLAs, what a reviewer sees, how an approval binds a human identity into the audit record, and how to handle stale or expired task tokens.

---

## The bright line (this runbook exists to enforce it)

The agents never autonomously decide **grades, admissions, discipline, financial aid, special-education eligibility, or student placement.** The HITL queue is the mechanism that makes that true in running software. Every consequential action **blocks** until a named, authorized human approves it, and the approval **binds that human's identity into the record** before any write happens. If the queue is down, consequential actions do not proceed — they wait. That is the design working, not the design failing.

---

## 1. What the HITL queue is

The HITL queue is the **DynamoDB HITL table** (provisioned by `data.yaml`) holding pending human-approval requests. It is the durable state behind the human gate:

- In the **LangGraph** runtime, the gate is `interrupt_before` on the `finalize` node — the graph suspends and writes a pending request to the queue.
- In the **Strands + Step Functions** native runtime, the gate is `waitForTaskToken` — the state machine pauses and holds a task token until a decision is posted.

In both, the **gateway enforces that a valid reviewer identity is present in the approval record before it mints the short-lived scoped write token** for the downstream system of record. There is no path from intake to a consequential write that skips this — it is tested in `governance/tests/test_hitl_gates.py`.

---

## 2. Actions that require approval (the bright-line list)

Any agent output that would cause one of these requires HITL approval before it can take effect:

| # | Consequential action | What the agent may do | What requires a human |
|---|---|---|---|
| 1 | **Grades** (final / high-stakes) | Draft rubric-grounded feedback and evaluation | The educator owns and issues the grade |
| 2 | **Admissions** | Validate and prepare documents | A human decides admission |
| 3 | **Discipline** | Nothing — never inferred or decided by the agent | All of it |
| 4 | **Financial aid** | Check status, explain | Eligibility / award is a human decision |
| 5 | **Special-education eligibility** | Draft proposed accommodations / retrieve an approved plan | The IEP/504 team decides eligibility and placement |
| 6 | **Student placement** | Present options and recommendations | Placement is human |

Beyond the bright line, any **write / irreversible / consequential tool** (e.g., publishing to the LMS, sending a family message, opening a case in a system of record) is HITL-gated as a class. Reads are not gated; the read/write separation is enforced at Layer 3.

---

## 3. Reviewer roles mapped to action types

Reviewers are authenticated via the institution's IdP and carry the `custom:edu_role` attribute (student / guardian / educator / counselor / administrator). The reviewer's role must be appropriate to the action — an educator cannot approve an enrollment-records change that belongs to the registrar.

| Action type | Originating agent(s) | Appropriate reviewer role |
|---|---|---|
| Grade-related drafts / feedback | 04 Assessment, Grading & Feedback | **Educator** |
| LMS content publish, rubric/quiz publish | 03 Educator Copilot | **Educator** |
| Student-success intervention / outreach | 05 Student Success & Engagement | **Counselor** (or administrator per policy) |
| Advising / pathway recommendation acceptance, placement options | 06 Pathway Navigator | **Counselor** |
| Enrollment / records changes, document acceptance | 07 Document & Accessibility, 01 Concierge | **Registrar / administrator** |
| Financial-aid status actions | 01 Concierge | **Administrator** (aid office) |
| IEP/504 accommodation drafts | (drafted/retrieved only) | **IEP/504 team member** — eligibility never agent-decided |
| Operational / administrative workflow writes | 08 Operations Service Desk | **Administrator** (per segregation-of-duties policy) |

> **Customer must configure:** the exact role-to-action mapping for their institution, in the IdP role mapping and the gateway role-entitlement table. The mapping above is a sensible reference, not a binding default.

---

## 4. SLAs

> **Customer sets the actual SLAs.** The values below are reference starting points. Set them against the real-world cost of delay — a grade draft can wait; a time-sensitive student-success outreach may not.

| Metric | Reference target | Escalation if breached |
|---|---|---|
| Approval latency (time in queue to decision) | ≤ 1 business day for grades/content; ≤ 4 hours for time-sensitive outreach | Re-route to a backup reviewer in the same role; notify the reviewer's supervisor |
| Queue depth (pending items per role) | Warn at a per-role threshold | Page the queue owner; consider additional reviewers |
| Stale task token (approaching token timeout) | Act before timeout (see §8) | Re-issue / re-enqueue per §8 |

> **Customer must configure:** the numeric SLA per action type, the queue-depth warning thresholds, and the backup-reviewer routing.

---

## 5. What a reviewer sees

A reviewer is given everything needed to make a defensible decision — and nothing that violates data minimization. The review surface presents:

- **The draft** — the proposed feedback, message, recommendation, or action, clearly labeled as a draft (an **option** or **recommendation**, never an "approved decision").
- **The compliance / grounding report** — whether every fact, deadline, policy statement, and figure traces to approved institutional content (`grounding.py`); ungrounded artifacts fail before they reach a reviewer.
- **The source citations** — the approved content each claim is grounded in.
- **The masked context** — the student/operational context the draft was built from, with student PII replaced by stable pseudonyms (FERPA/COPPA), so the reviewer can judge the draft without unnecessary exposure of record-linkable identifiers.
- **The requesting identity and role** — who/what initiated the request, so the reviewer can confirm the action is within scope and supports segregation of duties (§7).

---

## 6. The approval action

The reviewer chooses one of three outcomes:

1. **Approve.** The decision is recorded with the reviewer's identity bound into it, and **only then** is the short-lived scoped write token minted (via AgentCore Identity / STS) and the action executed against the system of record.
2. **Request one bounded revision.** Routes back to the agent for a single, scoped revision loop (the routing node's "loop back" path), then returns to the queue.
3. **Reject / escalate.** Stops the action; routes to a human per the escalation path. A rejection is itself a recorded outcome and is a signal monitored in `MODEL-DEGRADATION-RESPONSE.md`.

**Approval binds identity, then mints the token — in that order, never the reverse.** A write token is never minted on the strength of an agent's output alone; it is minted on the strength of a verified human approval record.

---

## 7. Audit binding and segregation of duties

- **Every decision is logged** to the append-only audit trail with the outcome (`ALLOW` / `DENY` / `PENDING_APPROVAL` / `ERROR`), the reviewer identity for any approval, the system-of-record lineage, and the purpose-of-use. The trail is append-only (`deny:UpdateItem`/`deny:DeleteItem`, PITR) — a decision, once recorded, cannot be altered.
- **Segregation of duties:** the **requester must not be the approver.** A reviewer cannot approve an action they originated. Enforce this in the role-entitlement configuration; confirm it in review.
- The bound reviewer identity is what makes the bright line auditable: a compliance reviewer can answer "who approved this consequential action, and on what basis" for every such action, from the trail alone.

---

## 8. Handling stale / expired task tokens

A pending request can outlive its token — the reviewer is away, an SLA lapses, or a `waitForTaskToken` timeout approaches.

1. **Detect** via the queue-depth and approval-latency alarms (§9) and any token-timeout metric.
2. **Before timeout:** re-route to a backup reviewer in the same role so the decision is made in time.
3. **On expiry / failed token:** the action **must not auto-approve and must not silently drop.** The safe default is **fail-closed** — the consequential action does not proceed. Re-enqueue the request (a new pending item / new task token) so a human still decides; do not fabricate an approval to clear the queue.
4. **Record** the expiry and the re-enqueue in the audit trail. A token that expired is itself an auditable event.

> **Customer must configure:** the `waitForTaskToken` timeout duration and the re-enqueue / backup-routing behavior. The non-negotiable is fail-closed: no consequential action proceeds without a live, bound human approval.

---

## 9. Queue monitoring

Monitor in CloudWatch (provisioned with the platform):

- **HITL queue depth** — per role; alarm at the customer-set threshold.
- **Approval latency** — time from enqueue to decision; alarm on SLA breach.
- **Rejection / revision rate** — a rising trend is a quality signal; hand off to `MODEL-DEGRADATION-RESPONSE.md`.
- **Token expiry rate** — should be near zero; a nonzero rate means the SLA or staffing is misaligned.

> **Customer must configure:** all alarm thresholds and their routing to the queue owner. The dashboards ship; the thresholds are yours.
