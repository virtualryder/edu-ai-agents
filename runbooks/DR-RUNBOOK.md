# Disaster Recovery Runbook
### EDU AI Agent Suite

> Disaster recovery for the governed agent platform: what to protect, how it is backed up, how to restore it without breaking the append-only and WORM guarantees the compliance posture depends on, and what region failover means when student data carries residency obligations.
>
> **Reference targets only.** Every RTO/RPO in this runbook is a *starting point a customer must replace* with values from their own business-impact analysis and service agreements. A district's tolerance for a Concierge outage is not a university's tolerance for an audit-trail gap.

The recovery objective is not just "the agents run again." It is "the agents run again **and the audit trail is continuous, the WORM records are intact, and the bright line still holds.**" A restore that resumes service but loses audit continuity has failed.

---

## 1. RTO / RPO targets by data class

RTO = how long until restored. RPO = how much recent data you can afford to lose. Different data classes warrant very different targets — the audit trail and WORM store are near-zero-loss by design; a knowledge base can be rebuilt.

| Data class | Store | Reference RTO | Reference RPO | Notes |
|---|---|---|---|---|
| **Append-only audit trail** | DynamoDB (PITR) | ≤ 1 hour | ≤ 5 min | Highest priority. PITR gives ~second-level recovery. Loss here is a compliance gap, not just an outage. |
| **HITL queue** | DynamoDB (PITR) | ≤ 1 hour | ≤ 5 min | Pending approvals must survive; a lost queue strands consequential actions. Stale tokens handled per `HITL-QUEUE-OPERATIONS.md`. |
| **WORM document store** | S3 + Object Lock (COMPLIANCE) | ≤ 4 hours | ~0 (versioned) | Object Lock + versioning means records are not lost, only temporarily unavailable. Recovered via versioning/replication, never overwrite. |
| **Knowledge bases** | Bedrock KB (OpenSearch Serverless / Aurora pgvector) | ≤ 8 hours | Source-of-truth driven | Reconstructable by re-ingesting approved institutional content; RPO is the freshness of the source corpus, not the index. |
| **Config / IaC** | Source control (CloudFormation / Terraform) | ≤ 2 hours | 0 (in VCS) | The recovery *source* for all infrastructure. If it isn't in source control, it isn't recoverable. |

> **Customer must configure:** the real RTO/RPO per class from a business-impact analysis, and confirm PITR retention and S3 retention periods meet them. The values above are defensible defaults, not commitments.

---

## 2. Backup mechanisms

- **DynamoDB (audit trail, HITL queue):** **Point-in-Time Recovery (PITR)** enabled on every table for continuous backup, plus scheduled **on-demand backups** for long-horizon retention. The append-only policy (`deny:UpdateItem`/`deny:DeleteItem`) means the live table is already tamper-resistant; PITR protects against accidental table-level loss.
- **S3 WORM store:** **versioning** plus **Object Lock in COMPLIANCE mode**. COMPLIANCE-mode retention **cannot be shortened or removed by anyone, including the root account, for the retention period** — this is the WORM guarantee. Data is protected against deletion and overwrite by design.
- **Cross-region replication:** consider **S3 Cross-Region Replication** (replicating Object Lock state) and DynamoDB cross-region strategy (global tables or backup copy) for region-level resilience — **subject to the residency constraints in §6.** Do not replicate student data to a region that violates a data-localization obligation.
- **KMS:** consider **multi-Region keys** so encrypted data is decryptable in a failover region. **The CMK is a hard dependency** — see §4.4.
- **IaC in source control:** CloudFormation (`infra/cloudformation/`) and Terraform (`infra/terraform/`) are the **authoritative recovery source for infrastructure.** Rebuilding the VPC, gateway, IAM roles, Guardrails, and tables is `git checkout` + deploy, not manual console work.

> **Customer must configure:** PITR/on-demand backup schedules and retention, whether cross-region replication is enabled (and whether residency permits it), and the KMS key topology (multi-Region vs per-region).

---

## 3. Multi-AZ posture

The reference architecture is **multi-AZ within a region** by default — the common-case resilience that does not trigger residency questions.

- **VPC across multiple Availability Zones** — subnets span AZs; no single-AZ chokepoint for the network layer.
- **Bedrock (Claude) and Guardrails** are regional, managed, multi-AZ services — no AZ-level action required.
- **Step Functions and Lambda** (native runtime) are regional and multi-AZ inherently.
- **DynamoDB** is multi-AZ inherently — the audit trail and HITL queue survive an AZ loss with no operator action.
- **AgentCore Runtime** containers (ARM64, `/invocations` + `/ping`, port 8080) autoscale across AZs.

An **AZ failure should be transparent** for most components. The procedures in §4 are for region-level or store-level loss, which is rarer and harder.

---

## 4. Restore procedures

> Throughout: **preserve the append-only / WORM guarantees and audit continuity.** A restore that creates a mutable copy of audit data, or that "fixes" WORM records by overwriting, has broken the control it was meant to protect.

### 4.1 DynamoDB — audit trail / HITL queue (PITR restore)

1. Restore from PITR to a **new table** (DynamoDB PITR always restores to a new table; you cannot restore in place).
2. Re-apply the **append-only policy** to the restored table (`deny:UpdateItem`/`deny:DeleteItem` on the audit partition) **before** repointing — never expose a window where the restored table is mutable.
3. Re-enable PITR on the restored table.
4. **Repoint** the gateway / application config to the new table (via IaC, so the change is itself recorded).
5. Verify **audit continuity** across the restore window — there should be no unexplained gap; if there is, record it as a known gap with the PITR timestamp.

### 4.2 S3 WORM store

1. **Object Lock retention cannot be shortened.** WORM records are recovered via **versioning and replication, never by overwrite.** To "restore" a deleted-marker situation, remove the delete marker / promote the prior version — the locked object itself was never gone.
2. If recovering into a new bucket (region failover), the target bucket must have **Object Lock enabled at creation** (it cannot be added later) and the same COMPLIANCE-mode retention.
3. Verify retention metadata replicated correctly — a restored WORM store with weakened retention is not a WORM store.

### 4.3 Knowledge bases

Rebuild by re-ingesting approved institutional content into a fresh Bedrock Knowledge Base (OpenSearch Serverless or Aurora pgvector) via IaC. The index is derived data; the **source corpus** is the thing to protect, and it is segmented by institution/course/section/role on ingest — confirm segmentation is preserved.

### 4.4 KMS — the hard dependency

**Losing the CMK loses the data it protects.** There is no workaround: data encrypted under a destroyed or unavailable customer-managed key is unrecoverable. Therefore:

- Treat CMK availability as a **gating precondition** for every restore above — confirm the key (or its multi-Region replica) is available in the recovery region **before** restoring data.
- Never schedule a CMK for deletion as part of an environment teardown without confirming no retained (especially WORM / audit) data depends on it.
- Keys are **separate per environment** — confirm you are restoring with the right environment's key.

---

## 5. Region failover considerations

Region failover is the heavy procedure. Work through these before failing over:

1. **Data residency / state data-localization.** Several of the ~140 state student-privacy laws impose data-localization or residency obligations. **The failover region must satisfy the same residency obligations as the primary** — you cannot fail student data over to a non-compliant region to restore availability. If no compliant alternate region exists, the DR strategy is in-region (multi-AZ) plus a documented residency-constrained recovery posture, not cross-region failover.
2. **Bedrock model + Guardrail availability per region.** Confirm the required Claude models and the configured Guardrails are available in the failover region. Model and Guardrail availability differs by region; a region with the data but not the model cannot run the agents.
3. **AgentCore Gateway target re-registration.** Tool targets and connector registrations must be re-registered against the failover region's gateway (via IaC). No agent has a direct path to a system of record, so the gateway must be fully stood up before any agent can act.
4. **KMS in the failover region** (§4.4) — confirm key availability first.
5. **Repoint identity / IdP federation** (Cognito / IAM Identity Center) and confirm `custom:edu_role` mapping carries over.

> **Customer must configure:** whether cross-region failover is permitted at all given residency obligations, which region is the sanctioned alternate, and the IaC parameterization that makes a failover-region deploy a config change rather than a rewrite.

---

## 6. DR test cadence and validation checklist

DR procedures that are never tested do not work. Test on a cadence the customer sets (a reasonable reference: PITR restore quarterly, full region failover annually or per major change).

**Validation checklist for any DR test or real recovery:**

- [ ] CMK (or multi-Region replica) confirmed available in the recovery region **before** any data restore.
- [ ] Audit table restored to a new table with the append-only policy **re-applied before repoint**; PITR re-enabled.
- [ ] **Audit continuity verified** across the recovery window; any gap documented with timestamps.
- [ ] HITL queue restored; pending approvals accounted for; stale/expired task tokens handled per `HITL-QUEUE-OPERATIONS.md`.
- [ ] WORM store integrity confirmed — Object Lock COMPLIANCE retention intact, no records overwritten, recovery done via versioning/replication.
- [ ] Knowledge bases re-ingested from the approved source corpus with role/segment scoping preserved.
- [ ] Bedrock models + Guardrails confirmed present in the recovery region.
- [ ] Gateway targets / connectors re-registered; deny-by-default confirmed (a misconfigured gateway must fail *closed*).
- [ ] IdP federation and `custom:edu_role` mapping confirmed.
- [ ] **Bright line confirmed:** the HITL gate is enforced in the recovered environment (assert via `governance/tests/test_hitl_gates.py`); no consequential write path bypasses it.
- [ ] Residency obligations confirmed satisfied by the recovery region.
- [ ] RTO/RPO actuals measured against targets (§1); gaps logged and fed into the next DR-plan revision.
