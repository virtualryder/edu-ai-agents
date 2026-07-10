# Gateway modes — portable (validated default) vs. managed AgentCore

*Which MCP/tool-authorization gateway to deploy, stated precisely so a reviewer isn't misled. The
governed decision/least-privilege/token/audit semantics are identical across modes; what differs is
the AWS service that hosts them. Reference accelerator — see `NOT-CLAIMS.md`.*

## The two modes

| Mode | What it is | Status here |
|---|---|---|
| **Portable — API Gateway + Cognito JWT authorizer** | An API Gateway (HTTP/REST) with a Cognito/JWT (or IAM/SigV4) authorizer in front of the connector Lambdas; the deny-by-default policy, scoped tokens, approvals, and audit run in the Lambda control plane. | **The validated, supported default.** This is the path that was deployed and exercised in a clean account. Use it for pilots. |
| **Managed — Amazon Bedrock AgentCore Gateway + Identity** | AWS-managed gateway that maps each tool to an AgentCore Gateway *target* with AgentCore Identity for inbound/outbound auth. | **Optional / customer-specific, experimental here.** The reference registration ships (`infra/.../agentcore-gateway.yaml`) but the managed path is **not** presented as validated until it has the same clean-account evidence as the portable path. |

**Say it this way:** *"Portable API Gateway + Cognito JWT is the validated default; the managed
AgentCore path is optional and customer-specific unless separately evidenced."*

## Inbound authorization (who is calling)

- **Supported:** a verified **JWT** (Cognito / federated IdP) **or IAM** (SigV4). Identity is taken only
  from the verified authorizer claim, never from the request body.
- **AWS caution — `AUTHENTICATE_ONLY` only authenticates; it does NOT enforce authorization policies.**
  Authenticating a caller is not authorizing an action. This gateway **always authorizes**
  (deny-by-default, least-privilege intersection) *after* authentication — proven by the 12-case
  `test_mcp_authz_matrix.py`.
- **"No Authorization" is development/testing only and must never be used in production.** AWS says
  the same for AgentCore. There is no un-gated path to a system of record here.

## Outbound authorization (what the gateway presents to the system of record)

- **Supported patterns:** IAM, the caller's IAM credentials, **OAuth grants, token exchange /
  on-behalf-of**, token passthrough, and API keys. This gateway mints a **short-lived, per-call,
  tool-scoped credential** (the offline analog of AgentCore Identity / STS); the connector presents it
  to the system of record — no standing service account.
- **"No authorization" outbound is less secure and not recommended** (AWS). This gateway does not offer
  an un-credentialed outbound path — the negative-test matrix proves a call without a valid scoped
  credential is refused (case #11).

## What is actually evidenced

- **Portable path:** deployed + exercised in a clean account (identity → deny-by-default → scoped token
  → connector → bound approval → append-only audit). See `evidence/CLEAN-ACCOUNT-ACCEPTANCE.md`.
- **AgentCore path:** reference registration only; mark experimental until it carries the same evidence.

> Do not present the managed AgentCore path as production-validated unless the runtime evidence
> (`RUNTIME-EVIDENCE-RUNBOOK.md`) has been captured for it specifically.
