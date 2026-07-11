# Security Policy

## What this project is

The EDU AI Agent Suite is an **independent, open-source reference accelerator** for building governed AI agents on AWS. It is **not** an AWS service, an official AWS solution, or a turnkey production system, and it is provided **without warranty** of any kind (see `LICENSE`). It is intended for discovery, architecture design, demonstrations, and scoped pilots. Production deployments require customer-specific identity integration, connectors, security hardening, accessibility conformance testing, operations, and legal/privacy review.

This policy covers vulnerabilities in the **code and configuration in this repository**. It does **not** cover the security of Amazon Bedrock, AWS, or any other third-party service — report those through the respective vendor's disclosure channel.

## Runtime identity contract

The native entrypoints derive the acting user's identity **server-side** and never trust it
from the request body. `aws-native-reference/_shared/agentcore_server.py` (`POST /invocations`)
verifies an `Authorization: Bearer` RS256/JWKS token via `edu_agent_platform.auth.verify_jwt`
before invoking the graph; `aws-native-reference/_shared/lambda_handler.py` takes claims from the
**verified** API Gateway JWT authorizer context (`requestContext.authorizer.jwt.claims`). Any
`acting_user_claims` supplied in the body is overridden by the verified identity. Both fail closed
(HTTP 401 / `unauthorized`) outside demo mode; a caller-supplied claims dict is accepted **only**
in demo mode (`EXTRACT_MODE=demo` / `CONNECTOR_MODE=fixture` / `AUTH_ALLOW_UNVERIFIED_CLAIMS=1`).

## Scope

In scope:

- The reference platform code under `platform_core/`.
- The governance and evaluation code under `governance/`.
- The per-agent reference implementations (`01-*` through `08-*`).
- Infrastructure-as-code under `infra/` (CloudFormation and Terraform reference templates).
- Build, packaging, and deployment scripts under `scripts/`.

Out of scope:

- Vulnerabilities in AWS services, Amazon Bedrock, or other third-party platforms and dependencies (report upstream).
- Findings that require a misconfigured or unhardened deployment that this repository explicitly documents as the customer's responsibility (for example, demo-mode defaults, placeholder secrets, or the single-NAT reference simplification).
- Theoretical findings without a demonstrated, reproducible impact on the reference code.

## Reporting a vulnerability

Please report suspected vulnerabilities **privately**. Do not open a public issue, pull request, or discussion for a security report.

Report vulnerabilities privately via GitHub Security Advisories: use the *Security* tab -> *Report a vulnerability* on this repository. Please do not open public issues for security reports.

Please include:

- A description of the issue and the affected component(s) and path(s).
- Reproduction steps or a proof of concept.
- The potential impact as you assess it.
- Any suggested remediation.

## Coordinated disclosure

We follow a coordinated-disclosure model. We ask that you give us a reasonable opportunity to investigate and remediate before any public disclosure, and that you avoid accessing, modifying, or exfiltrating data that is not yours while researching. We will credit reporters who request it once a fix is available.

## Response targets

These are good-faith targets for an open-source reference project, not contractual commitments:

| Stage | Target |
|---|---|
| Acknowledge receipt | Within 5 business days |
| Initial assessment / triage | Within 10 business days |
| Status updates | At least every 2 weeks until resolution |
| Fix or documented mitigation | Prioritized by severity |

## Supported versions

This is a reference accelerator, not a released product with long-term support branches. Security fixes are applied to the **default branch (`main`) only**. Consumers who fork or vendor this code are responsible for tracking changes and applying fixes to their own copies. There is no back-porting to prior commits or tags.
