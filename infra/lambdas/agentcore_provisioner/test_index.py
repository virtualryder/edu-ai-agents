"""Unit tests for the AgentCore provisioner custom-resource Lambda.

No AWS, no network. A fake boto3 client records the control-plane calls; the
real `index.send` (cfnresponse) is monkeypatched to capture what would be sent
to CloudFormation. We assert:

  * Create/CreateGateway calls the gateway + target create ops and sends SUCCESS
    with the live endpoint in the response Data.
  * Create/RegisterRuntime calls the runtime create op and sends SUCCESS.
  * Delete calls the matching delete op and sends SUCCESS (idempotent teardown).
  * Any exception in the Create path sends FAILED (fail-closed), never SUCCESS.

Run:  python -m pytest infra/lambdas/agentcore_provisioner -q
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
index = importlib.import_module("index")


# ---------------------------------------------------------------------------
# Fakes
# ---------------------------------------------------------------------------
class FakeControlClient:
    """Records the control-plane calls the provisioner makes."""

    def __init__(self, fail_on: str | None = None):
        self.calls: list[str] = []
        self.fail_on = fail_on

    def _maybe_fail(self, name: str):
        if self.fail_on == name:
            raise RuntimeError(f"boom in {name}")

    def create_gateway(self, **kw):
        self.calls.append("create_gateway")
        self._maybe_fail("create_gateway")
        return {"gatewayId": "gw-123", "gatewayUrl": "https://gw.example/mcp", "gatewayArn": "arn:gw"}

    def create_gateway_target(self, **kw):
        self.calls.append("create_gateway_target")
        self._maybe_fail("create_gateway_target")
        return {"targetId": "tgt-1"}

    def delete_gateway(self, **kw):
        self.calls.append("delete_gateway")
        self._maybe_fail("delete_gateway")
        return {}

    def create_agent_runtime(self, **kw):
        self.calls.append("create_agent_runtime")
        self._maybe_fail("create_agent_runtime")
        return {"agentRuntimeId": "rt-1", "agentRuntimeArn": "arn:rt", "agentRuntimeEndpoint": "https://rt/inv"}

    def delete_agent_runtime(self, **kw):
        self.calls.append("delete_agent_runtime")
        self._maybe_fail("delete_agent_runtime")
        return {}


class FakeContext:
    log_stream_name = "test-stream"


@pytest.fixture
def captured(monkeypatch):
    """Capture index.send() calls; stub SSM resolution and the control client."""
    sent: list[dict] = []

    def fake_send(event, context, status, data=None, physical_resource_id=None, reason=None):
        sent.append(
            {"status": status, "data": data or {}, "pid": physical_resource_id, "reason": reason}
        )

    monkeypatch.setattr(index, "send", fake_send)

    # Stub SSM resolution so no AWS is touched: return one target spec + authorizer.
    def fake_resolve(names, region):
        if not names:
            return []
        if any("authorizer" in str(n) for n in names):
            return [{"clientId": "client-abc", "discoveryUrl": "https://idp/.well-known"}]
        return [{"system": "sis", "read": "sis.get", "write": "sis.put", "consequential": ""}]

    monkeypatch.setattr(index, "_resolve_ssm", fake_resolve)
    return sent


def _install_client(monkeypatch, client):
    monkeypatch.setattr(index, "_control_client", lambda props: client)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_create_gateway_calls_ops_and_sends_success_with_endpoint(captured, monkeypatch):
    client = FakeControlClient()
    _install_client(monkeypatch, client)
    event = {
        "RequestType": "Create",
        "StackId": "stk",
        "RequestId": "req",
        "LogicalResourceId": "AgentCoreGateway",
        "ResourceProperties": {
            "Action": "CreateGateway",
            "Environment": "pilot",
            "AuthorizerParam": "/edu-agents/pilot/gateway/authorizer",
            "TargetParams": ["/edu-agents/pilot/gateway/targets/sis"],
            "InvokerRoleArn": "arn:role",
            "KmsKeyArn": "arn:kms",
        },
    }
    index.lambda_handler(event, FakeContext())

    assert "create_gateway" in client.calls
    assert "create_gateway_target" in client.calls
    assert len(captured) == 1
    assert captured[0]["status"] == index.SUCCESS
    assert captured[0]["data"]["GatewayUrl"] == "https://gw.example/mcp"
    assert "sis" in captured[0]["data"]["Targets"]


def test_register_runtime_calls_op_and_sends_success(captured, monkeypatch):
    client = FakeControlClient()
    _install_client(monkeypatch, client)
    event = {
        "RequestType": "Create",
        "ResourceProperties": {
            "Action": "RegisterRuntime",
            "Environment": "pilot",
            "AgentId": "01-concierge",
            "ContainerImageUri": "123.dkr.ecr/x:latest",
            "ExecutionRoleArn": "arn:role",
            "GuardrailId": "gr-1",
        },
    }
    index.lambda_handler(event, FakeContext())

    assert client.calls == ["create_agent_runtime"]
    assert captured[0]["status"] == index.SUCCESS
    assert captured[0]["data"]["RuntimeEndpoint"] == "https://rt/inv"


def test_delete_gateway_calls_delete_op_and_sends_success(captured, monkeypatch):
    client = FakeControlClient()
    _install_client(monkeypatch, client)
    event = {
        "RequestType": "Delete",
        "ResourceProperties": {"Action": "CreateGateway", "Environment": "pilot"},
    }
    index.lambda_handler(event, FakeContext())

    assert client.calls == ["delete_gateway"]
    assert captured[0]["status"] == index.SUCCESS


def test_delete_runtime_calls_delete_op_and_sends_success(captured, monkeypatch):
    client = FakeControlClient()
    _install_client(monkeypatch, client)
    event = {
        "RequestType": "Delete",
        "ResourceProperties": {
            "Action": "RegisterRuntime",
            "Environment": "pilot",
            "AgentId": "01-concierge",
        },
    }
    index.lambda_handler(event, FakeContext())

    assert client.calls == ["delete_agent_runtime"]
    assert captured[0]["status"] == index.SUCCESS


def test_create_exception_fails_closed(captured, monkeypatch):
    """If a control-plane call raises during Create, we send FAILED, not SUCCESS."""
    client = FakeControlClient(fail_on="create_gateway")
    _install_client(monkeypatch, client)
    event = {
        "RequestType": "Create",
        "ResourceProperties": {
            "Action": "CreateGateway",
            "Environment": "pilot",
            "AuthorizerParam": "/edu-agents/pilot/gateway/authorizer",
            "TargetParams": ["/edu-agents/pilot/gateway/targets/sis"],
        },
    }
    result = index.lambda_handler(event, FakeContext())

    assert result["status"] == index.FAILED
    assert len(captured) == 1
    assert captured[0]["status"] == index.FAILED
    assert "boom" in (captured[0]["reason"] or "")


def test_unknown_action_fails_closed(captured, monkeypatch):
    client = FakeControlClient()
    _install_client(monkeypatch, client)
    event = {
        "RequestType": "Create",
        "ResourceProperties": {"Action": "Nonsense", "Environment": "pilot"},
    }
    index.lambda_handler(event, FakeContext())

    assert captured[0]["status"] == index.FAILED
    # No control-plane op should have been attempted for an unknown action.
    assert client.calls == []


def test_delete_idempotent_when_resource_absent(captured, monkeypatch):
    """Delete of an already-absent resource still returns SUCCESS (idempotent)."""
    client = FakeControlClient(fail_on="delete_gateway")
    _install_client(monkeypatch, client)
    event = {
        "RequestType": "Delete",
        "ResourceProperties": {"Action": "CreateGateway", "Environment": "pilot"},
    }
    index.lambda_handler(event, FakeContext())

    assert captured[0]["status"] == index.SUCCESS
