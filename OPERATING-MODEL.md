# Operating Model — EDU (K-12 & Higher Education)

*Who runs this in production. A reference accelerator is not an operating service — before a
production deployment, these responsibilities must have named owners on the customer side. This
document answers the six questions a CIO/CISO asks, as a RACI between the **accelerator** (what this
repo provides) and the **customer** (who operates it). It is guidance, not a managed-service offer;
see [`NOT-CLAIMS.md`](NOT-CLAIMS.md).*

**R** = Responsible (does the work) · **A** = Accountable (owns the outcome) · **C** = Consulted · **I** = Informed.

## The six questions

| # | Question | Accelerator provides | Customer owns (recommended owner) | RACI |
|---|---|---|---|---|
| 1 | **Who monitors it?** | CloudWatch dashboards + metrics hooks (`mcp_gateway` emits decision/latency/error signals); operator console reference | Runs monitoring; sets alarms/thresholds; on-call rota (**Platform/SRE team**) | Accel: C · Customer: R/A |
| 2 | **Who approves consequential actions?** | The framework-enforced human-approval gate (bound, single-use, SoD tokens) — the *mechanism* | Names the approver role and staffs it (**Registrar / FERPA officer**); the human makes every consequential decision | Accel: R (mechanism) · Customer: A (decision) |
| 3 | **Who responds to incidents?** | Incident-response + key-management runbook; fail-closed controls; append-only audit for forensics | Staffs incident response; owns sev/escalation; runs the runbook (**Security / IR team**) | Accel: C · Customer: R/A |
| 4 | **Who owns prompt / model changes?** | Prompt hash-pinning (change-control), grounding + scored evals as regression gates in CI | Approves prompt/model changes through change control; re-runs evals before promote (**AI/ML owner + business reviewer**) | Accel: R (guardrails) · Customer: A |
| 5 | **Who handles connector break/fix?** | The connector interface + fixture/live modes; the gateway is connector-agnostic (swap backend, keep governance) | Owns the production connector integration + vendor SLAs; break/fix (**Integration/Platform team + vendor**) | Accel: C · Customer: R/A |
| 6 | **Who answers audit requests?** | Append-only + WORM audit, control matrices (NIST/OWASP), the assurance packet, this operating model | Produces the evidence to the auditor; owns the FERPA / state student-privacy audit response (**Compliance / GRC**) | Accel: C · Customer: R/A |

## Change-control flow (prompts / models / policy)

1. Propose a change (prompt text, model id, or a policy grant/entitlement).
2. CI regression gate: prompt hash-pin update + scored eval + the 10-point negative demo must pass.
3. Business reviewer (Registrar / FERPA officer) and the AI/ML owner approve through the customer's change process.
4. Promote; the change and its approver land on the append-only audit trail.

## Before go-live: named-owner checklist

- [ ] Monitoring owner + on-call rota named; alarms configured.
- [ ] Approver role staffed (Registrar / FERPA officer); SoD enforced (`STRICT_APPROVAL=1` / bound approvals only).
- [ ] Incident-response owner + runbook adopted; key-rotation schedule set.
- [ ] Prompt/model change-control owner named; eval + negative-demo gates wired into the customer CI.
- [ ] Production-connector owner + vendor support contacts; break/fix path defined.
- [ ] GRC owner for FERPA / state student-privacy audit; audit-evidence export tested from the append-only trail.

> This operating model is a **template**. It does not transfer operational responsibility to the
> accelerator or to AWS; the customer owns operations under the shared-responsibility model. See
> [`docs/PRODUCTION-READINESS-AND-SHARED-RESPONSIBILITY.md`] for the full RACI where present.
