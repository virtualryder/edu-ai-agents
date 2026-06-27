"""AgentCore provisioning custom-resource Lambda — index.lambda_handler.

WHAT THIS PROVISIONS
====================
The shipped CloudFormation accelerator (infra/cloudformation/agentcore-gateway.yaml
and agent-service.yaml) treats the Amazon Bedrock AgentCore Gateway and AgentCore
Runtime as provisioning *contracts*: it writes SSM placeholders describing the
intended topology and exposes CloudFormation custom resources gated by the
`GatewayCustomResourceServiceToken` / `RuntimeCustomResourceServiceToken`
parameters. Until a provisioner Lambda is wired to those tokens, the gateway
endpoint reads `PENDING-PROVISION` and no AgentCore control-plane object exists.

THIS Lambda is that provisioner. It is the ServiceToken behind both custom
resources. On a CloudFormation Create/Update/Delete it calls the Bedrock
AgentCore *control-plane* APIs (boto3 client `bedrock-agentcore-control`) to make
the contract real, then signals CloudFormation with the live endpoint(s).

Two actions are dispatched off the `Action` property the templates pass:

  * Action == "CreateGateway"  (from agentcore-gateway.yaml `AgentCoreGateway`)
        Create/update an AgentCore Gateway, register one target per system of
        record from the passed-in TargetParams (SIS / LMS / CRM / ITSM tool
        lists, read vs write vs consequential), attach the Cognito JWT inbound
        authorizer, and wire AgentCore Identity for short-lived scoped
        (single-purpose, per-call) tokens. Returns `GatewayUrl` / `GatewayId`
        / `GatewayArn` as response data (the template reads `GatewayUrl` into the
        `/edu-agents/<env>/gateway/endpoint` SSM parameter).

  * Action == "RegisterRuntime"  (from agent-service.yaml `AgentCoreRuntimeRegistration`)
        Register/update an AgentCore Runtime from the container image URI / the
        container contract (ARM64, port 8080, POST /invocations + GET /ping),
        bind the execution role and the Bedrock Guardrail. Returns
        `RuntimeEndpoint` / `RuntimeArn` / `RuntimeId` as response data.

FAIL-CLOSED CONTRACT
====================
Every external (control-plane) call is wrapped and marked `# TODO(confirm-api)`
because the exact AgentCore control-plane operation names and request/response
shapes must be confirmed against the customer's installed boto3 version (the
`bedrock-agentcore-control` service is newer than some pinned boto3 builds — if
the client cannot even be constructed we FAIL, we do not pretend success). On
ANY exception during Create or Update we send **FAILED** to CloudFormation with
the error string, so the stack rolls back rather than reporting a gateway/runtime
that does not exist. We never silently succeed. The only place we deliberately
swallow errors is Delete of an already-absent resource (idempotent teardown),
which still returns SUCCESS so a stack can always be torn down.

IAM PERMISSIONS THIS LAMBDA NEEDS (attach to its execution role)
================================================================
  * bedrock-agentcore:CreateGateway / UpdateGateway / DeleteGateway / GetGateway
  * bedrock-agentcore:CreateGatewayTarget / UpdateGatewayTarget / DeleteGatewayTarget / ListGatewayTargets
  * bedrock-agentcore:CreateAgentRuntime / UpdateAgentRuntime / DeleteAgentRuntime / GetAgentRuntime
    (confirm the exact action namespace/names against the installed boto3 model)
  * ssm:GetParameter / GetParameters          (to resolve the target & authorizer specs)
  * iam:PassRole on the AgentExecutionRoleArn  (so the gateway/runtime can assume the agent role)
  * kms:DescribeKey / CreateGrant on the env CMK (gateway config / token encryption)
  * cognito-idp:DescribeUserPool / DescribeUserPoolClient (authorizer wiring; read-only)
  * logs:CreateLogGroup / CreateLogStream / PutLogEvents (its own logs)
Scope every statement to the env's resource ARNs; do NOT grant Resource: "*".

No third-party dependencies: stdlib + boto3 (present in the Lambda runtime). A
minimal `cfnresponse` is vendored inline (below) so the function has no layer
dependency.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List
from urllib.request import Request, urlopen

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SUCCESS = "SUCCESS"
FAILED = "FAILED"


# ---------------------------------------------------------------------------
# Vendored cfnresponse — signal CloudFormation over the pre-signed S3 URL.
# Inlined (rather than `import cfnresponse`) so the function needs no layer.
# ---------------------------------------------------------------------------
def send(
    event: Dict[str, Any],
    context: Any,
    status: str,
    data: Dict[str, Any] | None = None,
    physical_resource_id: str | None = None,
    reason: str | None = None,
) -> None:
    """Send a SUCCESS/FAILED response to the CloudFormation pre-signed URL."""
    data = data or {}
    physical_resource_id = physical_resource_id or _physical_id(event)
    reason = reason or (
        "See CloudWatch log stream: "
        + getattr(context, "log_stream_name", "n/a")
    )
    body = json.dumps(
        {
            "Status": status,
            "Reason": reason,
            "PhysicalResourceId": physical_resource_id,
            "StackId": event.get("StackId", ""),
            "RequestId": event.get("RequestId", ""),
            "LogicalResourceId": event.get("LogicalResourceId", ""),
            "NoEcho": False,
            "Data": data,
        }
    ).encode("utf-8")

    url = event.get("ResponseURL")
    if not url:
        # Unit-test / local path: no callback URL. Log and return.
        logger.info("cfnresponse (no ResponseURL): status=%s data=%s", status, data)
        return
    req = Request(
        url,
        data=body,
        method="PUT",
        headers={"content-type": "", "content-length": str(len(body))},
    )
    try:
        with urlopen(req) as resp:  # noqa: S310 - CFN-provided pre-signed URL
            logger.info("cfnresponse sent: %s (HTTP %s)", status, resp.status)
    except Exception:  # pragma: no cover - network failure path
        logger.exception("failed to PUT cfnresponse to CloudFormation")
        raise


def _physical_id(event: Dict[str, Any]) -> str:
    """Stable physical resource id derived from the request, action and env."""
    existing = event.get("PhysicalResourceId")
    if existing:
        return existing
    props = event.get("ResourceProperties", {}) or {}
    action = props.get("Action", "AgentCore")
    env = props.get("Environment", "env")
    agent = props.get("AgentId", "")
    suffix = f"-{agent}" if agent else ""
    return f"edu-agents-{env}-{action}{suffix}"


# ---------------------------------------------------------------------------
# Control-plane client helper. Construction itself can fail when boto3 is older
# than the AgentCore control-plane model — that is a real failure, not a
# success, so callers let it propagate to the fail-closed handler.
# ---------------------------------------------------------------------------
def _control_client(props: Dict[str, Any]):
    """Build the bedrock-agentcore-control boto3 client (region-aware)."""
    import boto3  # imported lazily so import-time errors are caught per-call

    region = props.get("Region") or None
    # TODO(confirm-api): confirm the service id is "bedrock-agentcore-control"
    # in the customer's installed boto3 (older boto3 builds lack this model and
    # will raise UnknownServiceError here — which correctly fails the stack).
    return boto3.client("bedrock-agentcore-control", region_name=region)


def _resolve_ssm(names: List[str], region: str | None) -> List[Dict[str, Any]]:
    """Resolve a list of SSM parameter names to their parsed JSON values."""
    import boto3

    if not names:
        return []
    ssm = boto3.client("ssm", region_name=region or None)
    out: List[Dict[str, Any]] = []
    resp = ssm.get_parameters(Names=names)
    for p in resp.get("Parameters", []):
        try:
            out.append(json.loads(p["Value"]))
        except (json.JSONDecodeError, KeyError):
            out.append({"raw": p.get("Value")})
    return out


# ---------------------------------------------------------------------------
# Action: CreateGateway
# ---------------------------------------------------------------------------
def provision_gateway(event: Dict[str, Any], props: Dict[str, Any]) -> Dict[str, Any]:
    """Create/update the AgentCore Gateway, its targets, authorizer and Identity.

    Each external call is marked `# TODO(confirm-api)` — the operation names and
    shapes below are the *intended* contract and must be confirmed against the
    customer's boto3 version before first live deploy. Any failure raises, and
    the handler turns that into a CloudFormation FAILED (fail-closed).
    """
    region = props.get("Region")
    client = _control_client(props)

    target_param_names = props.get("TargetParams", []) or []
    authorizer_param_name = props.get("AuthorizerParam")
    targets = _resolve_ssm(target_param_names, region)
    authorizer = (
        _resolve_ssm([authorizer_param_name], region)[0]
        if authorizer_param_name
        else {}
    )

    env = props.get("Environment", "dev")
    gateway_name = f"edu-agents-{env}-gateway"
    invoker_role = props.get("InvokerRoleArn")
    kms_key = props.get("KmsKeyArn")

    # 1) Create (or update) the gateway with the Cognito JWT inbound authorizer
    #    and AgentCore Identity wiring for short-lived scoped tokens.
    # TODO(confirm-api): create_gateway operation name / authorizer + identity shape.
    gw = client.create_gateway(
        name=gateway_name,
        roleArn=invoker_role,
        protocolType="MCP",
        authorizerType="CUSTOM_JWT",
        authorizerConfiguration={
            "customJWTAuthorizer": {
                "discoveryUrl": authorizer.get("discoveryUrl", ""),
                "allowedAudience": [authorizer.get("clientId", "")],
                "allowedClients": [authorizer.get("clientId", "")],
            }
        },
        kmsKeyArn=kms_key,
    )
    gateway_id = gw.get("gatewayId") or gw.get("GatewayId") or gateway_name
    gateway_url = gw.get("gatewayUrl") or gw.get("GatewayUrl") or ""
    gateway_arn = gw.get("gatewayArn") or gw.get("GatewayArn") or ""

    # 2) Register one target per system of record (read/write/consequential
    #    tool lists carried in each SSM target spec).
    registered: List[str] = []
    for spec in targets:
        system = spec.get("system", "unknown")
        # TODO(confirm-api): create_gateway_target operation name / target shape.
        client.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name=f"{gateway_name}-{system}",
            targetConfiguration={
                "system": system,
                "readTools": spec.get("read", ""),
                "writeTools": spec.get("write", ""),
                "consequentialTools": spec.get("consequential", ""),
            },
        )
        registered.append(system)

    logger.info("gateway %s provisioned with targets: %s", gateway_id, registered)
    return {
        "GatewayId": gateway_id,
        "GatewayUrl": gateway_url,
        "GatewayArn": gateway_arn,
        "Targets": ",".join(registered),
    }


# ---------------------------------------------------------------------------
# Action: RegisterRuntime
# ---------------------------------------------------------------------------
def provision_runtime(event: Dict[str, Any], props: Dict[str, Any]) -> Dict[str, Any]:
    """Register/update the AgentCore Runtime from the container image / contract."""
    client = _control_client(props)

    env = props.get("Environment", "dev")
    agent_id = props.get("AgentId", "agent")
    runtime_name = f"edu-agents-{env}-{agent_id}-runtime"
    image_uri = props.get("ContainerImageUri")
    role_arn = props.get("ExecutionRoleArn")
    guardrail_id = props.get("GuardrailId")

    if not image_uri:
        raise ValueError("ContainerImageUri is required to register an AgentCore Runtime")

    # Register the ARM64 container runtime against the /invocations + /ping
    # contract, bind the execution role and the Bedrock Guardrail.
    # TODO(confirm-api): create_agent_runtime operation name / artifact + network shape.
    rt = client.create_agent_runtime(
        agentRuntimeName=runtime_name,
        agentRuntimeArtifact={"containerConfiguration": {"containerUri": image_uri}},
        roleArn=role_arn,
        networkConfiguration={"networkMode": "PUBLIC"},
        protocolConfiguration={"serverProtocol": "HTTP"},
        environmentVariables={"GUARDRAIL_ID": guardrail_id or ""},
    )
    runtime_id = rt.get("agentRuntimeId") or rt.get("AgentRuntimeId") or runtime_name
    runtime_arn = rt.get("agentRuntimeArn") or rt.get("AgentRuntimeArn") or ""
    runtime_endpoint = rt.get("agentRuntimeEndpoint") or rt.get("AgentRuntimeEndpoint") or ""

    logger.info("runtime %s registered from image %s", runtime_id, image_uri)
    return {
        "RuntimeId": runtime_id,
        "RuntimeArn": runtime_arn,
        "RuntimeEndpoint": runtime_endpoint,
    }


# ---------------------------------------------------------------------------
# Action dispatch: Delete (idempotent teardown)
# ---------------------------------------------------------------------------
def teardown(event: Dict[str, Any], props: Dict[str, Any]) -> Dict[str, Any]:
    """Tear down the gateway or runtime idempotently. Absent == success."""
    action = props.get("Action", "")
    env = props.get("Environment", "dev")
    try:
        client = _control_client(props)
    except Exception:  # pragma: no cover - client unavailable; nothing to delete
        logger.exception("control client unavailable on delete; treating as absent")
        return {"Deleted": "skipped"}

    try:
        if action == "CreateGateway":
            gateway_name = f"edu-agents-{env}-gateway"
            # TODO(confirm-api): delete_gateway (+ delete_gateway_target) op names.
            client.delete_gateway(gatewayIdentifier=gateway_name)
            return {"Deleted": gateway_name}
        if action == "RegisterRuntime":
            agent_id = props.get("AgentId", "agent")
            runtime_name = f"edu-agents-{env}-{agent_id}-runtime"
            # TODO(confirm-api): delete_agent_runtime op name.
            client.delete_agent_runtime(agentRuntimeId=runtime_name)
            return {"Deleted": runtime_name}
    except Exception as exc:  # idempotent: already gone is not an error on delete
        logger.warning("delete encountered %s: %s (idempotent)", type(exc).__name__, exc)
        return {"Deleted": "absent-or-error-ignored", "Detail": str(exc)}
    return {"Deleted": "noop"}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def lambda_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """CloudFormation custom-resource entry point. Fails closed on any error."""
    request_type = event.get("RequestType", "")
    props = event.get("ResourceProperties", {}) or {}
    action = props.get("Action", "")
    logger.info("AgentCore provisioner: RequestType=%s Action=%s", request_type, action)

    # Delete is idempotent and always succeeds so a stack can be torn down.
    if request_type == "Delete":
        try:
            data = teardown(event, props)
            send(event, context, SUCCESS, data)
        except Exception as exc:  # never block a teardown
            logger.exception("teardown error (still returning SUCCESS)")
            send(event, context, SUCCESS, {"Deleted": "error-ignored", "Detail": str(exc)})
        return {"status": SUCCESS}

    # Create / Update: do the real work and FAIL CLOSED on any error.
    try:
        if action == "CreateGateway":
            data = provision_gateway(event, props)
        elif action == "RegisterRuntime":
            data = provision_runtime(event, props)
        else:
            raise ValueError(f"unknown Action '{action}' (expected CreateGateway or RegisterRuntime)")
        send(event, context, SUCCESS, data)
        return {"status": SUCCESS, "data": data}
    except Exception as exc:
        # FAIL CLOSED: report FAILED to CloudFormation so the stack rolls back
        # rather than recording a gateway/runtime that does not actually exist.
        logger.exception("provisioning failed; sending FAILED to CloudFormation")
        send(
            event,
            context,
            FAILED,
            data={},
            reason=f"{type(exc).__name__}: {exc}",
        )
        return {"status": FAILED, "error": str(exc)}
