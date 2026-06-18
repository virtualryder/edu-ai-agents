# Operations Service Desk — Integration Guide
### Connectors, identity/role mapping, document-level permissions, and the gateway flow

> This guide describes how Agent 08 connects to systems of record and how identity, role, and group membership govern what it may retrieve and do. It assumes the shared MCP authorization gateway (`../../platform_core/edu_agent_platform/mcp_gateway/`) and connector framework are in place. Read it alongside `aws-deployment-guide.md` and the suite architecture (`../../docs/SUITE-ARCHITECTURE.md`).

---

## 1. The integration principle

No agent calls a vendor system directly. Every tool call — read or write — passes through the gateway, which verifies identity, applies deny-by-default authorization with least-privilege intersection, enforces purpose-of-use, runs the student-PII masker on results, mints a short-lived scoped token, and writes an append-only audit record. The connector framework (`../../platform_core/edu_agent_platform/connectors/`) presents an identical `invoke(method, args)` interface in demo (fixtures) and production (live APIs); the gateway does not know which backend is live. This is the foundation the whole agent rests on — see `../../docs/WHY-THE-MCP-LAYER.md` for why it is funded first.

---

## 2. Connectors and the systems they front

| Connector | System of record (examples) | Primary operations |
|---|---|---|
| **itsm** | ServiceNow, Jira Service Management | `search_knowledge`, `get_ticket_status` (READ); `create_ticket`, `route_incident` (WRITE) |
| **endpoint** | AWS Systems Manager (authorized managed devices), endpoint telemetry | `get_device_telemetry`, `run_safe_diagnostic` (READ/DIAGNOSTIC); `restart_managed_service` (PRIVILEGED) |
| **identity** | IdP via IAM Identity Center / Cognito (Okta, Entra, Google Workspace, AD) | claims/role/group resolution; `reset_password` (PRIVILEGED) |
| **hr** | Workday, Banner, PeopleSoft | `lookup_procedure` (READ); `initiate_onboarding_task` (WRITE) |
| **procurement** | Institution procurement platform | `lookup_threshold` (READ); `initiate_requisition` (WRITE — segregation of duties) |
| **finance** | ERP finance module, grants management | `lookup_procedure` (READ); `initiate_workflow` (WRITE — segregation of duties) |
| **facilities** | Facilities / work-order system | `submit_request` (WRITE); status read |
| **kb** | Amazon Bedrock Knowledge Bases; Amazon Q Business | `search_staff_policy`, `search_it_knowledge` (READ, permission-respecting) |
| **records** | Records-management / retention system | records-request handling, retention-schedule integration |

For staff-facing administrative transactions, the gateway fronts the HR/finance/procurement/facilities tools via **AgentCore Gateway / API Gateway** targets. Broad enterprise staff search is served by **Amazon Q Business**; custom, transactional workflows are served by a Bedrock/AgentCore agent calling the domain connectors above.

---

## 3. Identity and role mapping

The experience layer captures the user's verified identity from the institution's own SSO (Okta, Entra, Google Workspace, AD via **IAM Identity Center / Cognito**) and forwards the IdP claims to the gateway. The suite's roles — **student, family (guardian), teacher, staff, administrator** — are mapped from IdP groups, and authorization is the intersection of what the agent is granted and what the user's role entitles. An agent can never do more than the human on whose behalf it acts.

| Role | Service-desk surface | Admin-workflow surface |
|---|---|---|
| **Student** | Own tickets, own password reset (gated), own device help; COPPA-heightened handling for under-13 | None |
| **Family (guardian)** | Tickets and device help scoped by the FERPA rights that transfer to the student at 18 / postsecondary enrollment | None |
| **Teacher** | Own and classroom-tech tickets, LMS access, classroom-device diagnostics | Travel/expense, facilities requests, policy lookup |
| **Staff** | Own tickets, software-install requests | Domain-scoped HR/finance/procurement/facilities per group membership |
| **Administrator** | Routing, broader ticket visibility within domain | Approval authority (the named human in the HITL gate); never the initiator and approver of the same item |

Role state — including the under-13 flag and guardian age-of-majority status — is carried in the identity claims, exactly as the compliance spine requires (`../../governance/README.md`).

---

## 4. Group-membership propagation into retrieval

Authorization is not only about which tools the agent may call; it is about what those tools may return. **Group membership propagates from the IdP into retrieval**, so a search reflects the requester's existing entitlements rather than the full corpus.

In practice: when a staff member queries policy, their IdP group membership (e.g., HR, finance, procurement, facilities) is forwarded with the request, and **Amazon Bedrock Knowledge Bases** apply **document-level permissions** keyed to those groups. **Amazon Q Business** enforces the same — its connectors honor source-system ACLs and group membership so broad enterprise search never returns a document the user could not open in the source system. Retrieval respects existing permissions; it never crosses a user's entitlements. This is the mechanism by which "no unrestricted cross-domain search" is enforced at the data layer, complementing the per-domain tool-grant separation at the gateway.

---

## 5. Document-level permissions in Bedrock Knowledge Bases

The knowledge substrate is segmented by institution, domain, and role. Document-level permissions mean a single knowledge base can hold HR, finance, procurement, and facilities policy without a finance clerk's query surfacing HR-restricted material. Configuration steps:

- Index documents with metadata carrying the owning domain and the entitled IdP groups.
- Configure the knowledge base to filter retrieval by the requester's propagated group membership.
- Keep IT-knowledge content (device guides, connectivity runbooks) in its own segment, separate from staff-administrative policy.
- Validate that retrieval honors permissions as part of connector validation (a production-readiness gate, per `../../README.md`).

---

## 6. Tools, grants, and the diagnostic / privileged-remediation separation

Grants are issued per agent per administrative domain. The READ/DIAGNOSTIC set and the WRITE/PRIVILEGED-REMEDIATION set are distinct, and a diagnostic grant never implies a remediation grant. The full tool table is in `../README.md`; the separation enforced here is:

- **READ / DIAGNOSTIC** — `itsm.search_knowledge`, `itsm.get_ticket_status`, `endpoint.get_device_telemetry`, `endpoint.run_safe_diagnostic`, `kb.search_*`, `hr.lookup_procedure`, `procurement.lookup_threshold`, `finance.lookup_procedure`, `doc.draft_artifact`. No approval gate; low-risk; pass through.
- **WRITE / PRIVILEGED REMEDIATION** — `identity.reset_password`, `endpoint.restart_managed_service`, `itsm.route_incident`, `itsm.create_ticket`, `procurement.initiate_requisition`, `finance.initiate_workflow`, `facilities.submit_request`, `hr.initiate_onboarding_task`. Each blocks until a verified, named reviewer identity is bound into the record.

Privileged endpoint remediation reaches devices only through **AWS Systems Manager**, scoped to institution-managed, authorized devices by SSM tag/resource-group policy and the agent IAM role — never personal or unmanaged endpoints.

---

## 7. The gateway flow (one tool call, end to end)

```
1. Experience layer forwards verified IdP claims + role + group membership
2. Gateway: identity verification        → deny on missing subject
3. Gateway: deny-by-default authorization → tool ∈ AGENT_TOOL_GRANTS[agent] ∩ ROLE_ENTITLEMENTS[user_roles]
4. Gateway: purpose-of-use check          → tool permitted for this purpose-of-use only
5. If WRITE / PRIVILEGED REMEDIATION      → HITL gate: Step Functions waitForTaskToken;
                                            named approver (separate human for finance/procurement)
6. Security / identity / safeguarding     → immediate human escalation; never auto-resolved
7. AgentCore Identity mints short-lived, single-purpose token (no standing service account)
8. Connector invoke(method, args) against the system of record
9. Student-PII masker runs on the result before it enters a prompt or audit record
10. Append-only audit record: who · what · when · basis · approver  (DynamoDB / S3 Object Lock)
```

Reads (diagnostics, status, grounded retrieval) pass straight through steps 1–4 and 7–10. Only consequential writes pause at step 5, and any security/identity/safeguarding signal escalates at step 6 rather than being resolved by the agent.

---

## 8. References

- Gateway reference logic and tool registry: `../../platform_core/edu_agent_platform/mcp_gateway/`
- Connector framework: `../../platform_core/edu_agent_platform/connectors/`
- Why the layer comes first + implementation options: `../../docs/WHY-THE-MCP-LAYER.md`
- AWS topology and runtime options: `aws-deployment-guide.md`
- Compliance treatment: `edu-compliance.md` and `../../governance/README.md`

---

Maturity: **Documented.**
