"""
Secret resolution — AWS Secrets Manager with environment fallback.

All credentials (Anthropic API key, SIS/LMS/CRM/ITSM connector secrets, IdP
client secrets) resolve through one function so that:

  * dev/demo reads from environment variables / .env (no AWS required), and
  * production reads from Secrets Manager, namespaced per institution/tenant, with
    rotation and no plaintext secrets in code, images, or task definitions.

Resolution order: explicit env var -> Secrets Manager (if boto3 + name) -> default.
Values are cached process-wide; call clear_cache() in tests.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_CACHE: Dict[str, str] = {}
_SECRET_PREFIX = os.getenv("SECRETS_PREFIX", "edu/")


def clear_cache() -> None:
    _CACHE.clear()


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Resolve a secret by logical name.

    1. Environment variable matching `name` (upper-cased, non-alnum -> _).
    2. AWS Secrets Manager at `${SECRETS_PREFIX}{name}` (string or JSON {name:value}).
    3. `default`.
    """
    env_key = "".join(c if c.isalnum() else "_" for c in name).upper()
    if env_key in os.environ:
        return os.environ[env_key]

    if name in _CACHE:
        return _CACHE[name]

    secret = _from_secrets_manager(name)
    if secret is not None:
        _CACHE[name] = secret
        return secret

    return default


def _from_secrets_manager(name: str) -> Optional[str]:
    if os.getenv("DISABLE_SECRETS_MANAGER", "").strip().lower() in ("1", "true", "yes"):
        return None
    try:  # pragma: no cover - requires AWS
        import boto3  # lazy

        client = boto3.client("secretsmanager", region_name=os.getenv("AWS_REGION", "us-east-1"))
        resp = client.get_secret_value(SecretId=f"{_SECRET_PREFIX}{name}")
        raw = resp.get("SecretString", "")
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                return data.get(name) or next(iter(data.values()), None)
        except json.JSONDecodeError:
            return raw
        return raw
    except Exception as exc:  # pragma: no cover
        logger.debug("Secrets Manager lookup failed for %s: %s", name, exc)
        return None
