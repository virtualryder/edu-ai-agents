# AgentCore Provisioner — CloudFormation custom resource

This Lambda makes the AgentCore **provisioning contracts** real. The shipped
templates (`infra/cloudformation/agentcore-gateway.yaml`, `agent-service.yaml`)
write SSM placeholders describing the intended AgentCore Gateway / Runtime
topology and expose CloudFormation custom resources gated by two parameters:

| Template | Custom resource | Gated by parameter | This Lambda's `Action` |
|---|---|---|---|
| `agentcore-gateway.yaml` | `AgentCoreGateway` | `GatewayCustomResourceServiceToken` | `CreateGateway` |
| `agent-service.yaml` (container) | `AgentCoreRuntimeRegistration` | `RuntimeCustomResourceServiceToken` | `RegisterRuntime` |

Until a `ServiceToken` is supplied, the gateway endpoint SSM parameter reads
`PENDING-PROVISION` and no AgentCore control-plane object exists. Wire **this**
Lambda's ARN into those two parameters and the contracts get provisioned for
real on `cloudformation deploy`.

## What it does

- **CreateGateway** — creates/updates an AgentCore Gateway, registers one target
  per system of record (SIS / LMS / CRM / ITSM, read vs write vs consequential
  tool lists read from the SSM target specs), attaches the Cognito **JWT inbound
  authorizer**, and wires **AgentCore Identity** for short-lived scoped tokens.
  Returns `GatewayUrl` (read into `/edu-agents/<env>/gateway/endpoint`).
- **RegisterRuntime** — registers/updates an AgentCore Runtime from the container
  image URI against the ARM64 `/invocations` + `/ping` contract, binding the
  execution role and the Bedrock Guardrail. Returns `RuntimeEndpoint`.
- **Delete** — idempotent teardown of either resource.

## Fail-closed

Every control-plane call is marked `# TODO(confirm-api)` (operation names/shapes
must be confirmed against the customer's installed boto3) and wrapped so that on
**any** error during Create/Update the handler sends **FAILED** to CloudFormation
with the error string — the stack rolls back rather than recording a gateway or
runtime that does not exist. It never silently succeeds. Delete is the only path
that swallows "already absent" errors, and it still returns SUCCESS so a stack
can always be torn down.

> The `bedrock-agentcore-control` service model is newer than some bundled boto3
> builds. If the client cannot be constructed, that raises during Create and
> correctly produces a FAILED signal (not a false success). See `requirements.txt`.

## IAM the execution role needs

`bedrock-agentcore:*Gateway*`, `bedrock-agentcore:*GatewayTarget*`,
`bedrock-agentcore:*AgentRuntime*`, `ssm:GetParameter(s)`, `iam:PassRole` on the
agent execution role, `kms:DescribeKey`/`CreateGrant` on the env CMK,
`cognito-idp:DescribeUserPool*` (read-only), and CloudWatch Logs. Scope every
statement to the env's resource ARNs — never `Resource: "*"`. Full list is in the
module docstring in `index.py`.

## Test

```bash
python -m pytest infra/lambdas/agentcore_provisioner -q
```

No AWS or network — a fake boto3 client and a monkeypatched `cfnresponse` assert
the create/delete ops fire and that the exception path fails closed.

## Package & wire

`make golden-path-01` (or `scripts/package_lambdas.sh`) builds the agent Lambdas;
package this provisioner the same way (zip `index.py`, handler
`index.lambda_handler`, runtime python3.12) and pass its ARN as both
`GatewayCustomResourceServiceToken` and `RuntimeCustomResourceServiceToken`.
See `runbooks/agent-deploy/01-GOLDEN-PATH.md` step 7.
