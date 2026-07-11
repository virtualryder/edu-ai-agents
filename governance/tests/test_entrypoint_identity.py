"""Regression: native entrypoints derive identity server-side, never from the body."""
import importlib.util
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(_REPO / "platform_core"), str(_REPO)]


def _load_handler():
    p = _REPO / "aws-native-reference" / "_shared" / "lambda_handler.py"
    spec = importlib.util.spec_from_file_location("edu_native_lambda_handler", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_lambda_rejects_forged_body_claims_outside_demo(monkeypatch):
    """A body with self-asserted privileged claims and no verified token is refused in prod."""
    monkeypatch.setenv("EXTRACT_MODE", "live")
    monkeypatch.setenv("CONNECTOR_MODE", "live")
    monkeypatch.delenv("AUTH_ALLOW_UNVERIFIED_CLAIMS", raising=False)
    monkeypatch.delenv("AUTH_JWKS_URL", raising=False)
    mod = _load_handler()
    res = mod.lambda_handler(
        {"input": {"acting_user_claims": {"sub": "attacker", "custom:edu_role": "REGISTRAR"}}}
    )
    assert res.get("error") == "unauthorized"


def test_lambda_prefers_verified_authorizer_context_over_body(monkeypatch):
    """Verified API Gateway JWT authorizer claims win over any body-supplied claims."""
    monkeypatch.setenv("EXTRACT_MODE", "live")
    monkeypatch.setenv("CONNECTOR_MODE", "live")
    mod = _load_handler()
    captured = {}

    class _G:
        def invoke(self, payload):
            captured.update(payload)
            return {"ok": True}

    monkeypatch.setattr(mod, "_graph", lambda: _G())
    event = {
        "requestContext": {"authorizer": {"jwt": {"claims": {"sub": "u1", "custom:edu_role": "COUNSELOR"}}}},
        "input": {"acting_user_claims": {"sub": "attacker", "custom:edu_role": "REGISTRAR"}},
    }
    mod.lambda_handler(event)
    assert captured["acting_user_claims"]["sub"] == "u1"
