# Terraform & GovCloud status — EDU AI Agent Suite

**Honest status.** CloudFormation is the **canonical** IaC. The Terraform under `infra/terraform/` is
**substantial and close to parity** for the core architecture (a monolithic root, ~28 AWS resource
types of ~46 in the CloudFormation set). Note the suite-wide caveat: **no CloudFormation stack has
completed a clean-account stand-up** either (the 2026 validation exercised direct-API provisioning —
see [`../evidence/CLEAN-ACCOUNT-ACCEPTANCE.md`](../evidence/CLEAN-ACCOUNT-ACCEPTANCE.md) and the
README maturity matrix). So both IaC paths lint but neither is deploy-validated; "parity" refers to
resource coverage, not validated status.

## Coverage: Terraform vs CloudFormation

| Area | CloudFormation | Terraform |
|---|---|---|
| VPC / subnets / NAT / IGW / route tables | ✅ | ✅ |
| VPC interface endpoints (PrivateLink) | ✅ | ✅ |
| KMS CMK + alias | ✅ | ✅ |
| DynamoDB audit | ✅ | ✅ |
| S3 WORM (Object Lock + encryption + versioning + policy + PAB) | ✅ | ✅ |
| Bedrock Guardrail (+ version) | ✅ | ✅ |
| Cognito user pool + client + **identity pool + IdP federation** | ✅ | ✅ |
| Step Functions | ✅ | ✅ |
| SSM parameters | ✅ | ✅ |
| Security groups, IAM least-privilege roles | ✅ | ✅ |
| Full per-agent gateway wiring (authorizer/routes) | ✅ | ⚠️ monolithic root; verify per-agent route coverage |
| Lambda functions | ✅ | ⚠️ confirm coverage in the root |

**Bottom line:** the Terraform is a strong monolithic reference (notably it already includes Cognito
**identity-pool + IdP federation**, which some sibling suites do not). Remaining gaps are gateway
route/Lambda completeness, best confirmed with `terraform plan`.

## GovCloud posture

No GovCloud Terraform overlay ships in this repo. Education deployments in GovCloud are uncommon;
if pursued, the portable gateway path applies (as elsewhere) and it is engagement work.

## What "done" would require (engagement-owned)

Confirm gateway/Lambda completeness via `terraform plan`; complete at least one clean-account
stand-up on **either** path to move the "Deployed on AWS" column off the honest-empty state noted in
the README maturity matrix. Until then both IaC paths are lint-clean references, CloudFormation
canonical.
