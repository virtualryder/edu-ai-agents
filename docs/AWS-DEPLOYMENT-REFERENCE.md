# AWS Deployment Reference
### EDU AI Agent Suite — The Master, Step-by-Step Shared Runbook for the Secure Request Path

> **Audience.** An SI engineer or a customer cloud team standing up the suite in their own AWS account. This document is the **shared backbone** every one of the eight agents reuses: the secure request path from the public edge down to the append-only audit trail. Per-agent specifics (which tools, which connectors, which consequential actions) live in the per-agent runbooks under [`runbooks/agent-deploy/`](../runbooks/agent-deploy/). Deploy the shared path **once per environment**; then deploy agents on top of it.
>
> **This is a deployable accelerator, not a certified product.** Following this end-to-end gives you one governed, human-gated agent in a customer-isolated AWS environment — deny-by-default authorization, student-PII masking, a framework-enforced human-in-the-loop (HITL) gate, and an append-only audit trail. It does **not** give you a FERPA-certified, accessibility-conformance-tested, penetration-tested production system. The customer must harden, security-review, and accept accountability before it touches a live student record.

This document is the AWS-services-and-flow companion to:
- [`docs/DEPLOYMENT-HANDBOOK.md`](DEPLOYMENT-HANDBOOK.md) — the narrative empty-account-to-running walkthrough (CLI/console steps).
- [`docs/SUITE-ARCHITECTURE.md`](SUITE-ARCHITECTURE.md) — the six-layer architecture and AWS service mapping.
- [`docs/AWS-FUNDING-AND-PREREQUISITES.md`](AWS-FUNDING-AND-PREREQUISITES.md) — funding (PoA/MAP) and the pre-flight account checklist.
- [`docs/SHARED-RESPONSIBILITY-MATRIX.md`](SHARED-RESPONSIBILITY-MATRIX.md) — who owns what.

Where this document and the Handbook overlap, the Handbook is the canonical CLI source; this reference adds the **deploy-order, service-by-service, control-by-control** view and is explicit about **which layers the shipped IaC does and does not yet provision.**

---

## How to read this document

Each numbered step below is a layer of the shared request path, in **deploy order**. For each layer you get:

- **What it does** — the function in plain terms.
- **AWS services** — the concrete services involved.
- **Why / the security control** — the governance property it enforces.
- **Traffic flow** — how a request passes through it.
- **IaC mapping** — the CloudFormation template (in `infra/cloudformation/`) that provisions it, or a **Gaps / what you must add** callout where no template ships yet.

The bright line is constant across every layer: **agents never autonomously decide grades, admissions, discipline, financial aid, special-education eligibility, or student placement.** Every consequential action is HITL-gated to a named, authorized human whose identity is bound into the audit record before any write token is minted.

---

## Architecture at a glance — the shared request path

```
                                 INTERNET
                                    │
                        ┌───────────▼────────────┐
                        │  EDGE (Gap — see §5)    │   CloudFront + WAF + ACM/TLS
                        │  DDoS · WAF · TLS · CDN  │   Route 53 custom domain
                        └───────────┬─────────────┘
                                    │ HTTPS (static assets cached; API pass-through)
                        ┌───────────▼─────────────┐
                        │  IDENTITY (§4)          │   Cognito user pool ⇽ institution IdP
                        │  JWT issuance · claims  │   SAML/OIDC federation → custom:edu_role
                        └───────────┬─────────────┘
                                    │ Cognito JWT (sub + custom:edu_role + COPPA claims)
                        ┌───────────▼─────────────┐
                        │  JWT EXCHANGE / AUTHZ   │   Edge / Lambda authorizer validates JWT
                        │  (§6)                   │   → scoped session
                        └───────────┬─────────────┘
                                    │ verified claims forwarded (authz happens at Layer 3)
   ┌────────────────────────────────▼──────────────────────────────────────────┐
   │  VPC  (private subnets · no public app subnet · VPC endpoints)  (§3)       │
   │                                                                            │
   │   ┌─────────────────────────┐         ┌──────────────────────────────┐    │
   │   │ APPLICATION TIER (§7)   │         │ MCP GATEWAY (Layer 3) (§6/§8) │    │
   │   │ AgentCore Runtime       │ tool    │ AgentCore Gateway + Identity  │    │
   │   │ container (ARM64)       │ call    │ deny-by-default               │    │
   │   │  /invocations + /ping   ├────────▶│ agent-grant ∩ user-entitlement│    │
   │   │   OR                    │         │ HITL gate on consequential    │    │
   │   │ Step Functions + Lambda │◀────────┤ scoped per-call tokens        │    │
   │   │ (waitForTaskToken HITL) │ result  │ → connectors / targets        │    │
   │   └───────────┬─────────────┘         └───────────────┬──────────────┘    │
   │               │ Bedrock InvokeModel                   │ connector invoke   │
   │   ┌───────────▼─────────────┐         ┌───────────────▼──────────────┐    │
   │   │ MODELS (§7, Layer 5)    │         │ TOOLS / CONNECTORS (§8)       │    │
   │   │ Bedrock (Claude) via    │         │ Secrets Manager (CMK)         │    │
   │   │ VPC endpoint            │         │ SIS · LMS · CRM · ITSM · ERP  │    │
   │   │ + Bedrock Guardrails    │         │ Textract/Translate (07) etc.  │    │
   │   └─────────────────────────┘         └───────────────────────────────┘    │
   │                                                                            │
   │   ┌────────────────────────────────────────────────────────────────────┐  │
   │   │ DATA PLANE (§9)   DynamoDB append-only audit · HITL queue ·          │  │
   │   │                   S3 Object Lock (COMPLIANCE WORM) · all CMK-encrypted│  │
   │   └────────────────────────────────────────────────────────────────────┘  │
   │   ┌────────────────────────────────────────────────────────────────────┐  │
   │   │ HITL (§11)  Step Functions waitForTaskToken → reviewer UI handoff    │  │
   │   └────────────────────────────────────────────────────────────────────┘  │
   └────────────────────────────────────────────────────────────────────────────┘
        KMS CMK (§2) encrypts everything · CloudWatch + CloudTrail + OTel (§10) observe everything
```

Mermaid view of the full six-layer suite is in [`docs/SUITE-ARCHITECTURE.md`](SUITE-ARCHITECTURE.md#mermaid-diagram--full-suite-reference-architecture).

---

## Layer → CloudFormation template map

| # | Layer | Provisioned by | Status |
|---|---|---|---|
| 1 | Prerequisites & account setup | (manual / pre-flight) | See Handbook + AWS-FUNDING doc |
| 2 | KMS customer-managed keys | `security.yaml` (`EnvKmsKey`) | **Shipped** (one CMK per env; see gap on per-domain split) |
| 3 | Network — VPC, subnets, VPC endpoints | `network.yaml` | **Shipped** |
| 4 | Identity — Cognito + IdP federation | `security.yaml` (`UserPool`, `UserPoolIdentityProvider`, `IdentityPool`) | **Shipped** |
| 5 | Edge — CloudFront + WAF + ACM + Route 53 | `edge.yaml` (standalone; deploy in **us-east-1**) | **Shipped** (not in quickstart — needs us-east-1 + ACM; see §5) |
| 6 | JWT exchange / authorization | `agentcore-gateway.yaml` (`AuthorizerParam`) + gateway logic | **Partial** (authorizer config in SSM; edge authorizer is a gap) |
| 7 | Application tier (runtime) | `agent-service.yaml` (native + container paths) | **Shipped** (container path uses custom resource — see §7) |
| 8 | Tools / connectors / secrets | `agentcore-gateway.yaml` (targets) + Secrets Manager (manual) | **Partial** (targets as SSM/custom resource; secrets manual) |
| 9 | Data plane — audit / HITL / WORM | `data.yaml` | **Shipped** |
| 10 | Observability — CloudWatch / CloudTrail / OTel | `observability.yaml` (alarms + dashboard + SNS; standalone) | **Shipped** (alarms/dashboard; CloudTrail + OTel still manual; see §10) |
| 11 | Human-in-the-loop gate | `agent-service.yaml` (`waitForTaskToken`) + `data.yaml` (HITL table) | **Shipped** (reviewer UI is a gap — see §11) |
| 12 | Validation & smoke tests | `scripts/local_smoke.sh`, Handbook steps 7–9 | **Shipped** |
| 13 | Teardown | (manual) | See §13 |

`quickstart.yaml` is the **master template** that nests `network → security → data → agentcore-gateway → agent-service` in dependency order. Terraform parity lives in `infra/terraform/`.

---

# 1 — Prerequisites & account setup

**What it does.** Establishes the AWS landing zone, enables the foundation-model access the whole suite depends on, and confirms the tooling that builds and deploys artifacts.

**AWS services.** AWS Organizations / accounts, IAM (bootstrap/admin role), Amazon Bedrock (model access), Service Quotas, AWS Budgets / Cost Explorer, AWS CloudTrail.

**Why / the security control.** Environment isolation is a control: **one KMS CMK per environment** (Step 2) means dev/test/stage/prod must be separate accounts or at least cleanly isolated. Bedrock model access is **opt-in** — nothing infers until you enable it.

**Steps.**

1. **Account / Org.** A dedicated account (or a dedicated OU/account per environment). Recommended: separate account from production institutional systems, in the same AWS Organization. Confirm no SCP blocks Bedrock, DynamoDB, S3 (incl. Object Lock), Lambda, KMS, Secrets Manager, Step Functions, ECS/Fargate.
2. **Region.** Choose a region that satisfies the institution's data-residency / state data-localization obligations **and** has Bedrock Claude + AgentCore availability. `us-east-1` and `us-west-2` have the broadest Bedrock availability. **Customer must confirm AgentCore GA in-region** (it is GA as of 2026; verify the specific region). If AgentCore is unavailable in the required region, fall back to gateway Option B (API Gateway + Lambda + Step Functions) or Option C (FastMCP) — identical enforcement semantics; see [`docs/WHY-THE-MCP-LAYER.md`](WHY-THE-MCP-LAYER.md).
3. **Bedrock model access (BLOCKER).** Bedrock console → Model access → request **Anthropic Claude** models the agent uses (e.g., Claude 3.5 Sonnet `anthropic.claude-3-5-sonnet-20241022-v2:0` and Claude 3 Haiku `anthropic.claude-3-haiku-20240307-v1:0`), plus Titan Embeddings if using Bedrock Knowledge Bases. Verify:
   ```bash
   aws bedrock list-foundation-models --region <region> \
     --query "modelSummaries[?providerName=='Anthropic'].modelId"
   ```
4. **Service quotas.** Request Bedrock RPM/TPM increases (2× pilot, 5–10× production), Lambda concurrency (Option B), Step Functions throughput before the pilot — not during enrollment peak.
5. **IAM bootstrap role.** A deploying principal able to create named IAM roles, KMS keys, Cognito, DynamoDB, S3 (Object Lock), Step Functions, Lambda, VPC, and Bedrock AgentCore resources. CloudFormation deploys **named** IAM roles, so you pass `CAPABILITY_NAMED_IAM`. Prefer `PowerUserAccess` + scoped KMS, not `AdministratorAccess`.
6. **Cost / funding.** PoA credits (POC) or MAP (modernization framing) cover infrastructure — see [`docs/AWS-FUNDING-AND-PREREQUISITES.md`](AWS-FUNDING-AND-PREREQUISITES.md). Configure AWS Budgets at 80% and Cost Anomaly Detection on Bedrock.
7. **Tooling.**
   - **AWS CLI v2** configured (`aws sts get-caller-identity`).
   - **Docker with buildx for ARM64** — the AgentCore Runtime container is ARM64 (`Dockerfile.agentcore` targets `linux/arm64`). On an x86 build host, `docker buildx` + QEMU emulation is required.
   - **CloudFormation** (raw) is the primary path; `scripts/deploy.sh` wraps it. SAM/CDK are optional conveniences — the shipped IaC is plain CloudFormation.
8. **Staging buckets.** An S3 bucket for nested CloudFormation templates (`TemplateBaseUrl`) and one for packaged Lambda artifacts (`LambdaCodeBucket`). Versioned, encrypted, access-restricted.
9. **CloudTrail (BLOCKER).** Enable account CloudTrail to S3 before deploy — the audit trail is incomplete without it.

**IaC mapping.** Manual / pre-flight. The full checklist (with [BLOCKER] markers) is in [`docs/AWS-FUNDING-AND-PREREQUISITES.md`](AWS-FUNDING-AND-PREREQUISITES.md#part-b--aws-account-prerequisites-checklist).

---

# 2 — KMS customer-managed keys (CMK)

**What it does.** Establishes the encryption-at-rest root of trust. Every data store in the suite is encrypted with a **customer-managed** KMS key — never an AWS-managed default key.

**AWS services.** AWS KMS.

**Why / the security control.** The institution controls the key, and therefore controls the data. The key policy is the last line of access control: the audit table, HITL queue, WORM bucket, Secrets Manager secrets, and the Bedrock Guardrail config are all encrypted under it. The agent execution role is granted only `Encrypt`/`Decrypt`/`GenerateDataKey`/`DescribeKey`. **Losing the CMK loses the data it protects** — treated as a hard DR dependency (`runbooks/DR-RUNBOOK.md`). Key rotation is enabled (`EnableKeyRotation: true`); the key is `DeletionPolicy: Retain` / `UpdateReplacePolicy: Retain` so a stack delete never silently destroys the key.

**Traffic flow.** Not in the request path — it is in every *storage* path. Each write to DynamoDB/S3/Secrets Manager calls KMS to wrap the data key; each read unwraps it. The agent role's KMS grant is what lets the runtime decrypt its scoped secrets at call time.

**What ships.** `security.yaml` provisions **one CMK per environment** (`EnvKmsKey`, alias `alias/edu-agents-<env>`) with rotation on and a key policy granting the account root and the agent execution role. `data.yaml` consumes its ARN (`KmsKeyArn`) for the audit table, HITL table, and WORM bucket SSE-KMS. Secrets Manager secrets (Step 8) are created against the same CMK.

> **Gaps / what you must add.** The task brief envisions **one CMK per data domain** (audit, documents, secrets). The shipped IaC provisions **one CMK per environment** — a coarser grain. For stronger blast-radius isolation and separable key custody (e.g., the privacy office holds the audit-domain key), split `EnvKmsKey` into three keys (`audit`, `documents`, `secrets`) and point each consuming resource at the right key ARN. The key policies, rotation, and grant pattern in `security.yaml` are the template to replicate. **Grants vs. key policy:** the shipped template uses key-policy statements; for fine-grained, time-bounded delegation to the connector/runtime, prefer KMS **grants** issued at provision time.

---

# 3 — Network (VPC)

**What it does.** Provides the isolated network the application tier runs in. **No public inbound path to the agent runtime exists by design.** AWS-service traffic stays off the public internet via VPC endpoints.

**AWS services.** Amazon VPC, subnets, NAT Gateway, security groups, VPC interface + gateway endpoints.

**Why / the security control.** The agent runtime lives in **private subnets only** (`MapPublicIpOnLaunch: false`). Inbound to the runtime is impossible from the internet; ingress arrives only via the edge/identity layers above. Bedrock inference goes through a **VPC interface endpoint** so student data (post-masking) never traverses a public Bedrock endpoint. S3 and DynamoDB use **gateway endpoints** (no NAT cost, no internet path) for the WORM store and audit/HITL tables.

**Traffic flow.** Edge/identity (public) → application tier (private subnet) → Bedrock interface VPC endpoint (PrivateLink, not the public internet) and gateway endpoints (audit/WORM/connectors). Outbound to live SoR connectors that are internet-facing goes via NAT (HTTPS 443 only, per the runtime security group egress rule).

**What ships.** `network.yaml` provisions:
- A VPC (`10.40.0.0/16` default) with **2 public + 2 private subnets** across 2 AZs.
- A **single NAT gateway** (reference) — the template explicitly notes the customer should run **one NAT per AZ in production**.
- **`AgentRuntimeSecurityGroup`** — no public inbound; egress restricted to HTTPS 443.
- **`VpcEndpointSecurityGroup`** — accepts HTTPS only from the runtime SG.
- VPC endpoints: **`bedrock-runtime`** (interface), **`bedrock`** control-plane (interface), **S3** (gateway), **DynamoDB** (gateway).

> **Gaps / what you must add.** The brief's full endpoint set also names **Secrets Manager**, **CloudWatch Logs**, and **KMS** interface endpoints. `network.yaml` does **not** ship these — today Secrets Manager / KMS / Logs traffic from the private subnet egresses via **NAT**. For a no-internet-egress posture, add `com.amazonaws.<region>.secretsmanager`, `com.amazonaws.<region>.logs`, and `com.amazonaws.<region>.kms` interface endpoints (mirror the existing `BedrockRuntimeEndpoint` block and attach `VpcEndpointSecurityGroup`). The single NAT is a reference-only simplification — harden to one-per-AZ for production availability.

---

# 4 — Identity (Cognito + IdP federation)

**What it does.** Federates the institution's own identity provider into the suite and stamps every user with the role attribute the gateway authorizes against. The platform does **not** own user accounts.

**AWS services.** Amazon Cognito (user pool, app client, identity pool), the institution IdP (Okta / Microsoft Entra / Google Workspace / AD FS) via SAML or OIDC. IAM Identity Center is an alternative substrate.

**Why / the security control.** Authorization is always against a **verified human identity**. The IdP asserts who the user is; Cognito maps the IdP assertion into a `custom:edu_role` claim carrying one of **STUDENT, GUARDIAN, EDUCATOR, COUNSELOR, REGISTRAR, FINANCIAL_AID, ENROLLMENT_STAFF, ADMINISTRATOR, IT_STAFF, IT_ADMIN, STAFF, STAFF_APPROVER** (the `ROLE_ENTITLEMENTS` roles in `platform_core/edu_agent_platform/mcp_gateway/policy.py`). Two COPPA/FERPA claims ride alongside: `custom:under_13` (drives heightened Guardrails / data minimization) and `custom:rights_transferred` (FERPA rights transfer at 18 / postsecondary, which scopes the GUARDIAN role down).

**Traffic flow.** User authenticates at the institution IdP → SAML/OIDC assertion → Cognito → Cognito issues a **JWT** (OAuth2 `code` flow, scopes `openid email profile`) carrying `sub`, `custom:edu_role`, and the COPPA claims → forwarded inward. Token lifetimes (access/ID/refresh) are Cognito app-client settings the customer sets to their session policy.

**What ships.** `security.yaml` provisions:
- **`UserPool`** with MFA optional, a 14-char password policy, admin-create-only, and the custom schema attributes `edu_role`, `under_13`, `rights_transferred`.
- **`UserPoolIdentityProvider`** (conditional on `IdpMetadataUrl`) — SAML or OIDC, with `AttributeMapping` from IdP assertions to the custom claims.
- **`UserPoolClient`** — OAuth2 `code` flow; `SupportedIdentityProviders` switches to `InstitutionIdP` when federation is wired, else `COGNITO` for an early demo.
- **`IdentityPool`** — authenticated identities only (`AllowUnauthenticatedIdentities: false`).

The gateway reads `custom:edu_role` as the `roleClaim` (see `agentcore-gateway.yaml` `AuthorizerParam`).

> **Customer must configure.** IdP integration and the **IdP group → `edu_role` mapping** are customer-owned. Guardian-relationship modeling and the age-of-majority / FERPA rights-transfer logic must be implemented and validated by the institution — the gateway can only enforce what the claims correctly assert. The shipped `CallbackURLs` is `https://localhost/callback` (placeholder) — replace with the real edge domain (Step 5).

---

# 5 — Edge (CloudFront + WAF + TLS + custom domain)

**What it does.** The public front door. Terminates TLS, absorbs DDoS, applies WAF managed rule groups and rate limiting, optionally restricts by geo/IP, caches **static assets only**, and forwards API/auth traffic to the identity and application tiers.

**AWS services.** Amazon CloudFront, AWS WAF (web ACL with managed rule groups + rate-based rules), AWS Certificate Manager (ACM) for TLS, Amazon Route 53 for the custom domain.

**Why / the security control.** The edge is the only public surface. It sits in front so that: (a) TLS is terminated and enforced at a managed, hardened layer; (b) WAF managed rules (e.g., AWS Core rule set, known-bad-inputs, IP reputation) and rate limiting blunt volumetric and common web attacks before they reach identity/app; (c) only **static** assets are cached — never authenticated agent responses, which carry student data; (d) the app tier stays in private subnets (Step 3) with **no public inbound**. WAF logs feed the same observability spine (Step 10).

**Traffic flow.** Internet → Route 53 (custom domain) → CloudFront (ACM TLS) → WAF web ACL evaluation → CloudFront origin (the identity/authorizer/app entry). Static assets served from cache; dynamic/auth requests pass through to Cognito (Step 4) and the authorizer (Step 6).

> **What ships — `edge.yaml` (standalone, deploy in us-east-1).** `infra/cloudformation/edge.yaml` provisions the production edge:
> - **AWS WAFv2 WebACL** (`Scope: CLOUDFRONT`) with the three AWS managed rule groups (`AWSManagedRulesCommonRuleSet`, `AWSManagedRulesKnownBadInputsRuleSet`, `AWSManagedRulesAmazonIpReputationList`) plus a **rate-based rule** (`WafRateLimit`, default 2000 / 5-min / IP). Metrics + sampled requests on.
> - **CloudFront distribution** with `OriginDomainName` (the ALB / AgentCore / authorizer entry) as a `https-only` origin, viewer cert via `AcmCertificateArn` (**must be in us-east-1**), `MinimumProtocolVersion: TLSv1.2_2021`, the WebACL associated, a **response-headers policy** (HSTS, X-Content-Type-Options nosniff, `X-Frame-Options: DENY`, `strict-origin-when-cross-origin`), access logging to `LoggingBucketName`, the default behavior **caching-disabled** with the full method set incl. **POST** (for `/invocations`), `/static/*` cached, `/invocations*` explicitly pass-through.
> - **Route 53** alias record (Condition-gated on `HostedZoneId` + `DomainName`).
> - Outputs `DistributionDomainName` + `WebAclArn`. Origin lockdown (Origin-Verify header / CloudFront prefix list on the ALB SG) is documented in-template as customer hardening.
>
> **Deploy (must be us-east-1 — CLOUDFRONT-scope WAF and the CloudFront viewer ACM cert both live there):**
> ```bash
> aws cloudformation deploy \
>   --region us-east-1 \
>   --template-file infra/cloudformation/edge.yaml \
>   --stack-name edu-agents-<env>-edge \
>   --parameter-overrides Environment=<env> \
>     OriginDomainName=<alb-or-agentcore-dns> AcmCertificateArn=<us-east-1-acm-arn> \
>     DomainName=agents.example.edu HostedZoneId=<zone-id> LoggingBucketName=<log-bucket>
> ```
> **Why it is not in `quickstart.yaml`:** the edge requires a **us-east-1** deployment and a pre-issued **ACM certificate in us-east-1**, which a one-shot regional quickstart cannot satisfy. Deploy it as a standalone stack and then update the Cognito app-client `CallbackURLs` (Step 4) to the edge domain. The shipped `network.yaml` public subnets exist for NAT and a load-balanced ingress; `demo-in-a-box.yaml`'s ALB remains a POC-only demo, not the production edge.

---

# 6 — JWT exchange / authorization

**What it does.** Validates the Cognito JWT at the boundary and turns it into a **scoped session** the MCP gateway enforces. This is where deny-by-default begins.

**AWS services.** Amazon Bedrock AgentCore Identity + AgentCore Gateway authorizer (Option A, default); or API Gateway + a **Lambda authorizer** + STS (Option B); or auth middleware on a FastMCP server (Option C).

**Why / the security control.** The gateway enforces the policy in `policy.py`:
```
permitted(tool) ⇔ tool ∈ AGENT_TOOL_GRANTS[agent] ∩ ⋃ ROLE_ENTITLEMENTS[user_roles]
```
A tool call is allowed only if **both** the agent is granted it **and** the acting user's role entitles it — the agent can never exceed the human on whose behalf it acts. The boundary **denies on a missing subject** (no anonymous calls). The JWT is never trusted as authorization on its own; it is validated, and its `custom:edu_role` claim is the input to the intersection decision. Consequential tools additionally require the human gate (Step 11).

**Traffic flow.** Forwarded Cognito JWT → authorizer validates signature/issuer/audience against the Cognito user pool → extracts `sub` + `custom:edu_role` (+ COPPA claims) → the gateway computes the agent-grant ∩ user-entitlement intersection per tool call → ALLOW (proceed), DENY (audited and refused), or PENDING_APPROVAL (consequential — to the HITL gate). The application tier (Step 7) forwards the verified claims with every tool call so that **authorization happens at Layer 3, not in the container.**

**What ships.** `agentcore-gateway.yaml` writes the authorizer wiring as an SSM parameter (`AuthorizerParam`): `{"type":"cognito","userPoolId":...,"clientId":...,"roleClaim":"custom:edu_role","denyByDefault":true}`. The decision logic is the readable reference in `platform_core/edu_agent_platform/mcp_gateway/` (deny-by-default + intersection). On the native path, the runtime forwards `acting_user_claims` and the gateway "fails closed without a subject" (see `aws-native-reference/_shared/lambda_handler.py`).

> **Gaps / what you must add.** The **AgentCore Gateway resource itself** is provisioned by a **customer-supplied custom-resource Lambda** (`GatewayCustomResourceServiceToken`); when that token is blank the template writes only the SSM topology placeholders and the gateway endpoint reads `PENDING-PROVISION`. If you take **Option B**, you must build the **Lambda authorizer** that performs the JWT validation + intersection decision and the **STS** scoped-token minting — neither ships as a finished resource. The edge-side JWT validation (Step 5) is also a gap since the edge is a gap.

---

# 7 — Application tier (the agent runtime)

**What it does.** Runs the agent. Two first-class shapes, identical governance, selected by the `DeployMode` parameter.

**AWS services.**
- **Container path:** Amazon Bedrock **AgentCore Runtime** (ARM64 container, `POST /invocations` + `GET /ping`, port 8080), Amazon ECR.
- **Native path:** AWS **Step Functions** + AWS **Lambda** (four functions per agent), with a `waitForTaskToken` HITL gate.
- **Both:** Amazon Bedrock (Claude) inference, wrapped by **Bedrock Guardrails**; the MCP gateway as the single egress to tools.

**Why / the security control.** The container is **stateless** — each `/invocations` call carries the forwarded IdP claims + role + task context; no session state, no connector credentials, no direct SoR path live in the container. Authorization is at Layer 3. Every Bedrock call runs through the Guardrail (Step 2 in the Handbook: PII denial, age-appropriate content for minors/COPPA, prohibited-topic filters). PII masking runs before any prompt or audit record. On the native path, **no route from intake to finalize bypasses the `waitForTaskToken` HITL gate** for a consequential action.

**Traffic flow.**
- **Container:** AgentCore Runtime receives the invocation → runs the agent graph (stateless) → tool calls go through the gateway (Step 6/8) → Bedrock inference via the VPC endpoint (Step 3) under the Guardrail → returns the proposed action / answer.
- **Native:** Step Functions `Intake → IntakeRetrieveDraft (Bedrock + gateway reads) → PolicyComplianceGate → Routing (Choice) → HitlApprovalGate (waitForTaskToken) → Finalize` — Finalize is reached only after a verified approval resumes the gate.

**What ships.** `agent-service.yaml` provisions both paths, gated by `DeployMode`:
- **`native`** — the four Lambdas (`core` / `policy_gate` / `hitl_enqueue` / `finalize`, all ARM64, Python 3.12, in private subnets with the runtime SG), the `StateMachineRole`, and the **`AgentStateMachine`** whose definition includes the `waitForTaskToken` `HitlApprovalGate` (72h timeout, fail-closed on timeout/rejection). The Lambda handler shim is `aws-native-reference/_shared/lambda_handler.py`; build artifacts with `scripts/package_lambdas.sh`.
- **`container`** — records the container contract in SSM (`ContainerContractParam`: ARM64, port 8080, `/invocations`, `/ping`, role, guardrail) and, when `RuntimeCustomResourceServiceToken` is supplied, registers the runtime via a **custom resource**. The container is `aws-native-reference/_shared/Dockerfile.agentcore` + `agentcore_server.py`; build/push with `scripts/build_and_push_image.sh`.

> **Gaps / what you must add.** **AgentCore Runtime resource types are not yet fully expressible in plain CloudFormation.** The container path captures the contract in SSM and depends on a **customer-supplied registration Lambda**; the fully-turnkey *running endpoint* that ships today is **ECS Fargate via `demo-in-a-box.yaml`** (POC only, fixture mode). For production container hosting, supply the AgentCore registration custom resource or host on ECS/Fargate behind the gateway. Bedrock model-access scoping (restrict `bedrock:InvokeModel` to specific Claude ARNs) is customer-owned — the shipped agent role grants `bedrock:InvokeModel*` on `Resource: "*"`.

---

# 8 — Tools / connectors

**What it does.** Registers each system of record as a gateway target and brokers every read/write through one validated connection per system. Credentials never live in the agent.

**AWS services.** AgentCore Gateway targets, AWS Secrets Manager (CMK-encrypted), the connector framework (`platform_core/edu_agent_platform/connectors/`), and per-agent ingestion services where relevant (Amazon Textract / Translate / Polly for Agent 07).

**Why / the security control.** **Read and write are separate tools with separate grants.** Tools are named `connector_kind.operation` and map 1:1 to AgentCore Gateway targets. The agent resolves a connector secret at call time; a **short-lived, single-purpose scoped token** (AgentCore Identity / STS) — not a stored master credential — authorizes the downstream action. Connectors are **field-scoped** (return only the fields the tool needs) to prevent redisclosure. The connector factory runs **fixtures in demo, live only after validation**.

**Traffic flow.** Gateway ALLOW → resolve scoped secret from Secrets Manager (CMK-decrypt via the agent's KMS grant) → mint per-call token → connector `invoke(method, args)` against the SoR → field-scoped result → PII-masked audit append.

**What ships.** `agentcore-gateway.yaml` defines one **SSM target spec per SoR** (`sis`, `lms`, `crm`, `itsm`) via the `SystemsOfRecord` mapping, splitting `ReadTools` / `WriteTools` / `ConsequentialTools`. These are **topology-as-IaC**: the source of truth the pipeline (or the custom-resource Lambda) reconciles into real AgentCore Gateway targets. The agent execution role (`security.yaml`) can read `secretsmanager:GetSecretValue` only under `edu-agents/<env>/*`.

> **Gaps / what you must add.** **Secrets are not created by IaC** — create each connector secret manually against the env CMK (Handbook Step 6):
> ```bash
> aws secretsmanager create-secret --name edu-agents/<env>/sis \
>   --kms-key-id <env-cmk-arn> --secret-string file://sis-credentials.json --region <region>
> ```
> The four shipped target specs (`sis/lms/crm/itsm`) **do not cover every connector kind** the agents use — `kb`, `comms`, `assessment`, `analytics`, `rules`, `labor`, `docpipe`, `erp` appear in `policy.py` but have no target spec in `agentcore-gateway.yaml`. Add target specs for the kinds your agent needs (see each per-agent runbook). Live connector validation against SIS/LMS/CRM/ITSM is customer-owned — do not point a target at a live SoR until validated.

---

# 9 — Data plane

**What it does.** Holds the tamper-evident audit trail, the HITL approval queue, and the WORM store for finalized artifacts and audit snapshots. Everything CMK-encrypted.

**AWS services.** Amazon DynamoDB (audit + HITL tables, PITR), Amazon S3 with **Object Lock (COMPLIANCE mode)**, AWS KMS (Step 2).

**Why / the security control.**
- **Append-only audit** — the audit table is enforced append-only **at the principal**: the agent role is granted `dynamodb:PutItem` only (no `UpdateItem`/`DeleteItem`), because DynamoDB has no table-level resource policy to deny mutation. Every gateway attempt (ALLOW / DENY / PENDING_APPROVAL / ERROR) is written PII-masked with lineage to the SoR — the trail aligned to FERPA disclosure recordkeeping. PITR + `DeletionProtectionEnabled`.
- **S3 Object Lock COMPLIANCE** — finalized documents and audit snapshots are write-once, immutable for the retention window (`WormRetentionDays` default 2555 ≈ 7 years), unshortenable by **any** principal including root. Versioning is mandatory for Object Lock; `DenyInsecureTransport` enforces TLS; full public-access block.
- **HITL queue** — the `waitForTaskToken` gate writes a PENDING item carrying the task token; a verified reviewer identity must bind before the write token is minted. TTL fails expired tokens closed.

**Traffic flow.** Every gateway decision → audit `PutItem` (append-only). Consequential action → HITL `PutItem` (PENDING) → reviewer approval → audit transitions to ALLOW with bound reviewer identity. Finalized artifacts / periodic audit snapshots → S3 Object Lock (WORM).

**What ships.** `data.yaml` provisions all three: `AuditTable` (with `outcome-index` GSI, PITR, SSE-KMS, deletion protection), `HitlQueueTable` (with `status-index` GSI, TTL, PITR, SSE-KMS), and `WormBucket` (Object Lock COMPLIANCE, versioning, SSE-KMS, TLS-only bucket policy, optional read-only compliance principal). All `DeletionPolicy: Retain`.

> **Customer must validate.** Retention windows, the append-only IAM invariant (confirm no other principal has mutate access to the audit partition), and COMPLIANCE-mode retention against the records-retention schedule. COMPLIANCE retention cannot be shortened once set — choose deliberately.

---

# 10 — Observability

**What it does.** Makes the running platform observable and the audit queryable: logs, metrics, traces, alarms, and the API-level audit.

**AWS services.** Amazon CloudWatch (logs, metrics, alarms), AWS CloudTrail, OpenTelemetry tracing (`tracing.py` in the platform), the append-only audit table for compliance queries.

**Why / the security control.** Operations and compliance both depend on this layer. CloudWatch alarms on **HITL queue depth, approval latency, error rate, Guardrail block rate, grounding-failure rate, deny rate** are the signals the runbooks (`runbooks/INCIDENT-RESPONSE.md`, `MODEL-DEGRADATION-RESPONSE.md`, `HITL-QUEUE-OPERATIONS.md`) triage on. CloudTrail records all AWS API calls and feeds the **same unified compliance record** as gateway events. OTel traces tie a request across edge → identity → gateway → connector → audit. Log retention ≥ 365 days for FERPA recordkeeping.

**Traffic flow.** Every layer emits: WAF logs (edge), Cognito sign-in events (identity), gateway decision logs + audit `PutItem` (Layer 3), Lambda/Step Functions/AgentCore logs (app tier), Bedrock + Guardrail metrics (models). Alarms fire to the customer's pager; audit queries serve the privacy office.

> **What ships — `observability.yaml` (standalone alarms + dashboard + SNS).** `infra/cloudformation/observability.yaml` provisions:
> - A **KMS-encrypted SNS `AlarmTopic`** (env CMK via `KmsKeyArn`, else `alias/aws/sns`) with a Condition-gated email subscription (`AlarmEmail`) and a topic policy allowing CloudWatch to publish. Subscribe pager/Slack/PagerDuty here.
> - **CloudWatch alarms** on both custom and AWS metrics, each → `AlarmTopic`: tool-authorization **denial spike**, **PII-masking failures > 0**, **HITL backlog age** + **approval timeout**, **grounding-verification failures**, **Bedrock throttling** + **p99 latency**, **Lambda Errors** on all four agent functions (`core`/`policy-gate`/`hitl-enqueue`/`finalize`) + **core Throttles**, **DynamoDB audit SystemErrors** (PutItem) + **WriteThrottleEvents**, and a Condition-gated **AWS/Billing EstimatedCharges** cost guard (`EnableCostAlarm`, us-east-1 only).
> - A **CloudWatch dashboard** summarizing all of the above.
> - **Custom metric contract (the app must `put_metric_data`)** under namespace `CustomMetricNamespace` (default `EduAgentSuite`), Dimension `Environment=<env>`: `ToolAuthorizationDenied`, `PiiMaskingFailure`, `ApprovalBacklogAge`, `HitlApprovalTimeout`, `GroundingFailure`, `AuditWriteFailure`. The exact names + semantics are documented at the top of the template.
>
> **Deploy (standalone, same region as the agent stacks; set `EnableCostAlarm=true` only when in us-east-1 with billing alerts on):**
> ```bash
> aws cloudformation deploy \
>   --region <region> \
>   --template-file infra/cloudformation/observability.yaml \
>   --stack-name edu-agents-<env>-observability \
>   --parameter-overrides Environment=<env> KmsKeyArn=<env-cmk-arn> AlarmEmail=ops@example.edu \
>     CoreFunctionName=edu-agents-<env>-01-concierge-core \
>     PolicyGateFunctionName=edu-agents-<env>-01-concierge-policy-gate \
>     HitlEnqueueFunctionName=edu-agents-<env>-01-concierge-hitl-enqueue \
>     FinalizeFunctionName=edu-agents-<env>-01-concierge-finalize \
>     AuditTableName=edu-agents-<env>-audit
> ```
> **Why it is not in `quickstart.yaml`:** the alarms reference the per-agent Lambda function names (which vary by `AgentId`) and the cost alarm is us-east-1-only, so it deploys cleanly as a standalone stack layered on top of the per-agent runtime. Still customer-owned: **CloudTrail** (manual BLOCKER, AWS-FUNDING doc), log-group ≥365-day retention, S3 access logging, AWS Config for drift, OTel→CloudWatch/X-Ray export, and tuning every threshold + pager routing (`runbooks/README.md`).

---

# 11 — Human-in-the-loop (HITL) gate

**What it does.** Suspends every consequential action until a named, authorized human approves, binding the reviewer's identity into the record before any write token is minted. This is the bright line, framework-enforced.

**AWS services.** AWS Step Functions `waitForTaskToken` (native path) or the AgentCore Gateway approval gate (container path); the DynamoDB HITL queue table (Step 9); a reviewer UI (customer/SI surface).

**Why / the security control.** Consequential tools (the `CONSEQUENTIAL_TOOLS` set in `policy.py`: `sis.update_enrollment_record`, `comms.send_message`, `lms.update_assignment_due_date`, `lms.publish_content`, `assessment.release_grade`, `itsm.reset_password`, `itsm.restart_service`, `erp.initiate_approval`) **block** with `PENDING_APPROVAL` — they never execute on the agent's say-so. The reviewer must be in the correct role (educator / counselor / registrar / administrator) per the entitlement model. On timeout (default 72h) or rejection, the flow **fails closed** and escalates; the scoped write token is never minted without a valid reviewer identity. Tested in `governance/tests/test_hitl_gates.py`.

**Traffic flow.** Routing decides "clean" → `HitlApprovalGate` (waitForTaskToken) → `HitlEnqueueLambda` writes PENDING to the HITL table with the task token and the draft/compliance report → reviewer reviews in the UI → approval calls `SendTaskSuccess` (binds reviewer identity) → `Finalize` mints the scoped token, performs the gateway-brokered write, writes the closing ALLOW audit row. Rejection/timeout → `SendTaskFailure` → `Escalate`.

**What ships.** `agent-service.yaml` provisions the `waitForTaskToken` gate inside `AgentStateMachine` and the `HitlEnqueueLambda` / `FinalizeLambda`; `data.yaml` provisions the `HitlQueueTable`. Operations are documented in `runbooks/HITL-QUEUE-OPERATIONS.md`.

> **Gaps / what you must add.** The **reviewer UI / handoff surface is not in the IaC** — the gate and queue ship, but the screen a reviewer uses to see the draft + compliance report and click approve/reject is a customer/SI build. It must authenticate the reviewer (Cognito, correct `edu_role`), read the HITL queue, and call `SendTaskSuccess`/`SendTaskFailure` with the bound identity. For the container path, the AgentCore approval-gate equivalent must be wired to the same queue semantics.

---

# 12 — Validation & smoke tests

**What it does.** Confirms the path works end-to-end: a healthy runtime, an authenticated read that audits ALLOW, a denied over-reach, and a consequential action blocked pending approval.

**AWS services.** Step Functions, DynamoDB (audit/HITL query), the local container contract harness.

**Steps.**
1. **Prove the artifact locally first (no cloud):**
   ```bash
   scripts/local_smoke.sh 01-student-family-concierge
   ```
   Starts `agentcore_server.py` in `CONNECTOR_MODE=fixture`, checks `GET /ping` returns `{"status":"healthy"}`, and `POST /invocations` runs a benign authenticated read (STUDENT claims) and asserts an audit trail was produced.
2. **Authenticated read (deployed, native path)** — start a Step Functions execution with a benign read + valid student claims; confirm it reaches a successful terminal state and an **ALLOW** audit row appears (Handbook Step 7):
   ```bash
   aws stepfunctions start-execution --state-machine-arn <arn> \
     --input '{"agent":"01-concierge","tool":"sis.get_schedule","claims":{"sub":"demo-student","custom:edu_role":"STUDENT"},"mode":"fixture"}' --region <region>
   ```
3. **Denied over-reach** — invoke a tool the role is **not** entitled to (e.g., a STUDENT attempting `sis.update_enrollment_record`); confirm the gateway returns **DENY** and the deny is audited. This proves deny-by-default + the intersection.
4. **Consequential blocked pending approval** — trigger a consequential tool (e.g., `comms.send_message` finalize); confirm the `waitForTaskToken` gate fires, the item lands in the HITL queue as PENDING, and the action does **not** complete until a correctly-roled reviewer approves (Handbook Step 8).
5. Work the full **Validation checklist** in `docs/DEPLOYMENT-HANDBOOK.md` Step 9 before any pilot — each unchecked item is a go-live blocker.

**IaC mapping.** `scripts/local_smoke.sh`; Handbook Steps 7–9.

---

# 13 — Teardown

**What it does.** Removes the environment, respecting the data-protection invariants that intentionally survive a stack delete.

**Steps.**
1. **Delete the agent-service stack(s) first** (per agent), then the gateway, then data, security, network — i.e., reverse dependency order. With the nested master, delete the `quickstart.yaml` stack.
2. **Retained-by-design resources survive deletion.** `EnvKmsKey`, `AuditTable`, `HitlQueueTable`, and `WormBucket` are `DeletionPolicy: Retain`. This is deliberate — the audit trail and WORM records are compliance evidence. Delete them only via an explicit, authorized decommissioning process.
3. **S3 Object Lock COMPLIANCE** objects **cannot be deleted** until their retention expires — by any principal, including root. Plan decommissioning around the retention window.
4. **Drain the HITL queue** before teardown — do not orphan pending consequential approvals.
5. **De-provision AgentCore Gateway / Runtime** via the custom-resource Lambdas (or manually) since they are outside plain CFN.
6. **Revoke Bedrock model access** and **delete connector secrets** (Secrets Manager) and the CMK only after confirming no retained data still needs decryption — **destroying the CMK destroys the retained data** it protects.

---

## Deployment order checklist

```
[ ]  1. Account/Org, region, Bedrock model access, quotas, IAM bootstrap, CloudTrail (BLOCKERS)
[ ]  1. Tooling: AWS CLI v2, Docker buildx (ARM64), staging + Lambda buckets
[ ]  2. KMS CMK(s) — security.yaml (split per-domain if required)
[ ]  3. Network — network.yaml (add Secrets Manager/Logs/KMS endpoints; NAT-per-AZ for prod)
[ ]  4. Identity — Cognito + IdP federation (map IdP groups → custom:edu_role; wire COPPA claims)
[ ]  5. Edge — edge.yaml (CloudFront + WAFv2 + ACM + Route 53)   *** deploy STANDALONE in us-east-1 (not in quickstart) ***
[ ]  6. JWT exchange / authorizer — gateway authorizer config (+ custom-resource Lambda or Option B authorizer)
[ ]  7. Application tier — agent-service.yaml (native ready; container needs registration custom resource)
[ ]  8. Tools/connectors — register targets; create CMK-encrypted Secrets Manager secrets (manual)
[ ]  9. Data plane — data.yaml (audit / HITL / WORM)
[ ] 10. Observability — observability.yaml (alarms + dashboard + SNS)   *** deploy STANDALONE (not in quickstart) ***; CloudTrail on (manual)
[ ] 11. HITL gate — ships; build the reviewer UI handoff
[ ] 12. Validate — local_smoke.sh; ALLOW read; DENY over-reach; consequential blocked; Handbook Step 9 checklist
[ ] 13. (later) Teardown — reverse order; respect Retain + Object Lock
```

Recommended first deployment: **Agent 01 — Student & Family Services Concierge** (most visible, lowest decision-risk, easiest to measure). The shared path you built here is inherited by Agents 02–08; expand by deploying additional per-agent stacks on the same platform. See the per-agent runbooks in [`runbooks/agent-deploy/`](../runbooks/agent-deploy/).

---

## Request-flow walkthrough (a single authenticated request, end to end)

A request enters **CloudFront** (TLS terminated by ACM, custom domain via Route 53) → **WAF** evaluates managed rules + rate limiting and either blocks or forwards → the request hits the **identity** path where the user is authenticated against the institution **IdP via Cognito**, which issues a **JWT** carrying `sub`, `custom:edu_role`, and the COPPA claims → the **authorizer** (AgentCore Identity / Cognito, or a Lambda authorizer) validates the JWT and forwards the verified claims inward → the **application tier** (AgentCore Runtime container, or Step Functions + Lambda) runs the stateless agent, calling **Bedrock (Claude) via the VPC endpoint under the Guardrail** for generative steps with **PII masked first** → for any tool, the runtime calls the **MCP gateway (Layer 3)**, which computes **agent-grant ∩ user-entitlement**: a read the role is entitled to returns **ALLOW**, an over-reach returns **DENY**, a **consequential** tool returns **PENDING_APPROVAL** → on ALLOW the gateway mints a **short-lived scoped token**, resolves the **CMK-encrypted Secrets Manager** credential, and invokes the **connector** against the system of record, returning a **field-scoped** result → on PENDING_APPROVAL the **`waitForTaskToken` HITL gate** suspends, the item lands in the **HITL queue**, and a **named, correctly-roled reviewer** approves (binding their identity) before **Finalize** mints the write token and performs the action → **every** attempt (ALLOW / DENY / PENDING_APPROVAL / ERROR) is written **PII-masked, append-only** to the **DynamoDB audit table**, with finalized artifacts and audit snapshots landing in the **S3 Object Lock (WORM)** store → throughout, **KMS** encrypts every store and **CloudWatch / CloudTrail / OTel** observe every hop.

---

## Cross-links

- Narrative deploy (CLI/console, empty account → running): [`docs/DEPLOYMENT-HANDBOOK.md`](DEPLOYMENT-HANDBOOK.md)
- Six-layer architecture + AWS service mapping: [`docs/SUITE-ARCHITECTURE.md`](SUITE-ARCHITECTURE.md)
- Why the gateway comes first + the three implementation options: [`docs/WHY-THE-MCP-LAYER.md`](WHY-THE-MCP-LAYER.md)
- Gateway reference logic (Layer 3 enforcement, the six-step pipeline): [`platform_core/edu_agent_platform/mcp_gateway/README.md`](../platform_core/edu_agent_platform/mcp_gateway/README.md)
- Native rebuild + container contract: [`aws-native-reference/README.md`](../aws-native-reference/README.md)
- Funding + pre-flight checklist: [`docs/AWS-FUNDING-AND-PREREQUISITES.md`](AWS-FUNDING-AND-PREREQUISITES.md)
- Shared-responsibility split: [`docs/SHARED-RESPONSIBILITY-MATRIX.md`](SHARED-RESPONSIBILITY-MATRIX.md)
- Per-agent deploy runbooks: [`runbooks/agent-deploy/`](../runbooks/agent-deploy/)
- Build & deploy scripts: [`scripts/README.md`](../scripts/README.md)
- Operations runbooks (HITL queue, incident, DR, degradation): [`runbooks/README.md`](../runbooks/README.md)
- IaC: `infra/cloudformation/` — quickstart-nested: `quickstart.yaml`, `network.yaml`, `security.yaml`, `data.yaml`, `agentcore-gateway.yaml`, `agent-service.yaml`; standalone layers: `edge.yaml` (deploy in us-east-1), `observability.yaml`; Terraform parity in `infra/terraform/`
