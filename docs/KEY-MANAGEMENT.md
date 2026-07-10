# Key Management Runbook — EDU (K-12 & Higher Education)

*Production-grade AWS KMS key management for a deployment of this accelerator: **rotation, break-glass,
deletion, and separation of duties**. This is a runbook the customer operates; the accelerator ships
the reference key policies and the pattern. Reference accelerator — see [`../NOT-CLAIMS.md`](../NOT-CLAIMS.md);
this is operational guidance, not legal or compliance advice.*

## 1. Keys and scope

- **One customer-managed CMK per data class** (e.g. audit, evidence/WORM, secrets, PHI/PII/CJI store),
  not one shared key. Data class here: **student PII (FERPA)**.
- Encryption is enforced at rest (DynamoDB, S3 Object-Lock evidence, logs) and the CMK is required to
  read — so revoking key access revokes data access.

## 2. Separation of duties (the core control)

- **Key administrators** (rotate, set policy, schedule deletion) and **key users** (encrypt/decrypt at
  runtime) are **different principals**. The workload role can *use* the key but cannot *administer* it.
- No single human holds both admin and use on a production CMK. Admin actions require a second approver
  (change ticket) — the same separation-of-duties principle the gateway enforces for consequential tools.
- KMS key-policy + IAM enforce this; verify with IAM Access Analyzer (see `RUNTIME-EVIDENCE-RUNBOOK.md`).

## 3. Rotation

- **Automatic annual rotation enabled** on every CMK (`aws kms enable-key-rotation`). AWS retains prior
  key material so existing ciphertext stays readable; no data re-encryption needed.
- For a suspected compromise, perform an **out-of-cycle rotation**: create a new CMK, re-point the
  resource's key alias, re-encrypt or re-key as required, then schedule the old key for deletion (§5).
- Record each rotation in the change log; alarms on `DisableKeyRotation` / policy changes.

## 4. Break-glass (emergency access)

- Maintain a **break-glass role** with elevated KMS/data access that is **normally denied** and enabled
  only during a declared incident, with: MFA, a second-approver, a hard time-box, and full CloudTrail
  logging. Every break-glass use raises an alarm and is reviewed post-incident.
- Break-glass credentials are stored offline / in a separate account and rotated after any use.
- Pairs with the incident-response runbook (`INCIDENT-RESPONSE*.md`).

## 5. Deletion (the highest-risk action)

- **Never delete immediately.** Schedule deletion with the **maximum waiting period (30 days)**
  (`aws kms schedule-key-deletion --pending-window-in-days 30`) so it can be cancelled.
- Deleting a CMK **permanently destroys the data it protects** — treat it as data destruction. Require a
  second-approver, a change ticket, and confirmation that no live resource references the key/alias.
- **WORM/Object-Lock evidence:** the evidence CMK must **not** be deletable while retention holds; deletion
  of that key is a governance-bypass and is denied/alarmed. Prefer key **disable** over deletion for audit keys.

## 6. Monitoring (wire these alarms)

- CloudTrail + CloudWatch alarms on: `ScheduleKeyDeletion`, `DisableKey`, `DisableKeyRotation`,
  `PutKeyPolicy`, and any break-glass role assumption. Route to the security on-call
  (see [`OPERATING-MODEL.md`](../OPERATING-MODEL.md)).

## 7. Checklist (before go-live)

- [ ] One CMK per data class; aliases stable; automatic rotation enabled.
- [ ] Key admin vs. key user separated; no principal holds both on a prod key.
- [ ] Break-glass role defined, normally-denied, MFA + second-approver + time-boxed + alarmed.
- [ ] Deletion requires 30-day window + second approver; audit/WORM key protected from deletion.
- [ ] Alarms on all key-lifecycle events; owner named in the operating model.
