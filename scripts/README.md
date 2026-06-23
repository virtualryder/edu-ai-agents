# Build & Deploy Scripts

Turnkey tooling for the artifacts `docs/DEPLOYMENT-HANDBOOK.md` references. There are
two runtime paths (identical enforcement semantics); pick one per agent.

| Script | What it does | Path |
|---|---|---|
| `local_smoke.sh <agent>` | Run the AgentCore container contract locally (no docker/AWS) and exercise `/ping` + `/invocations`. Prove the artifact first. | both |
| `build_and_push_image.sh --agent <folder> --region <r>` | Build the **ARM64** container (`Dockerfile.agentcore`), create the ECR repo, push, and print `ContainerImageUri`. | **container** |
| `package_lambdas.sh --agent <folder> [--bucket <b>]` | Build the four native-path Lambda zips (`core/policy_gate/hitl_enqueue/finalize`) and optionally upload to `LambdaCodeBucket`. | **native** |
| `deploy.sh --env <e> --agent-id <id> --mode <container\|native> ...` | Stage the nested templates and deploy the master CloudFormation stack. | both |

## Recommended flow (container path — cleanest, matches `demo-in-a-box.yaml`)

```bash
# 0. prove the artifact locally (no cloud)
scripts/local_smoke.sh 01-student-family-concierge

# 1. build + push the ARM64 image
IMAGE=$(scripts/build_and_push_image.sh \
          --agent 01-student-family-concierge --region us-east-1 \
        | sed -n 's/^ContainerImageUri=//p')

# 2. deploy the governed stack for this agent
scripts/deploy.sh --env prod --agent-id 01-concierge --mode container \
  --template-bucket my-cfn-bucket \
  --idp-metadata https://idp.example.edu/app/x/sso/saml/metadata \
  --image "$IMAGE" --region us-east-1
```

## Native path (Step Functions + Lambda + `waitForTaskToken` HITL gate)

```bash
scripts/package_lambdas.sh --agent 01-student-family-concierge \
  --bucket my-lambda-bucket --agent-id 01-concierge --region us-east-1

scripts/deploy.sh --env prod --agent-id 01-concierge --mode native \
  --template-bucket my-cfn-bucket --lambda-bucket my-lambda-bucket \
  --idp-metadata https://idp.example.edu/app/x/sso/saml/metadata --region us-east-1
```

## Notes / honesty

- **Prerequisites** (Bedrock model access, Guardrail, region/quota confirmation, IAM) are in
  `docs/DEPLOYMENT-HANDBOOK.md` and `docs/AWS-FUNDING-AND-PREREQUISITES.md`. Run those first.
- **AgentCore Runtime** resource types are not yet fully expressible in plain CloudFormation; the
  container path captures the contract in SSM and registers via a customer-supplied custom resource
  (`RuntimeCustomResourceServiceToken`). The fully-turnkey running endpoint today is **ECS Fargate via
  `infra/cloudformation/demo-in-a-box.yaml`** (also consumes the image from `build_and_push_image.sh`).
- **Lambda size:** LangGraph + LangChain are sizeable; prefer a container-image Lambda or the AgentCore
  Runtime container if an unzipped native zip approaches the Lambda limit.
- To **author a new agent** (not just deploy one), see `docs/CREATE-A-NEW-AGENT.md`.
