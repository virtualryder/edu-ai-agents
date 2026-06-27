"""
Single-use enforcement for transaction-bound approvals.

A signed approval (see approvals.py) carries a one-time nonce. To guarantee an
approval cannot be replayed, the gateway must record each nonce as USED in a store
that is shared by every worker that could process the same approval.

  * InMemoryApprovalNonceStore — process-local; fine for local/dev/test and a
    single-process demo. NOT safe across multiple workers.
  * DynamoDBApprovalNonceStore — production: a conditional PutItem with
    `attribute_not_exists(nonce)` makes "first writer wins" atomic across workers,
    with a TTL attribute so consumed nonces self-expire. This is the durable
    single-use store referenced in docs/PRODUCTION-READINESS-ACTION-PLAN.md.

Both expose `consume(nonce, ttl_seconds) -> bool`: True if the nonce was newly
consumed (approval may proceed), False if it was already used (replay -> reject).
"""
from __future__ import annotations

import time
from typing import Optional, Protocol, Set


class ApprovalNonceStore(Protocol):
    def consume(self, nonce: str, ttl_seconds: int = 900) -> bool:
        ...


class InMemoryApprovalNonceStore:
    """Process-local single-use store. Default for dev/test/single-process demo."""

    def __init__(self) -> None:
        self._seen: Set[str] = set()

    def consume(self, nonce: str, ttl_seconds: int = 900) -> bool:
        if not nonce or nonce in self._seen:
            return False
        self._seen.add(nonce)
        return True


class DynamoDBApprovalNonceStore:
    """
    Durable, cross-worker single-use store backed by a DynamoDB table whose hash
    key is the nonce and which has TTL enabled on the `expires_at` attribute.

    The conditional write is the enforcement: two workers racing on the same nonce
    cannot both succeed, so a signed approval executes exactly once cluster-wide.
    """

    def __init__(self, table_name: str, client=None, key_name: str = "nonce",
                 ttl_attr: str = "expires_at") -> None:
        self._table = table_name
        self._key = key_name
        self._ttl_attr = ttl_attr
        if client is None:  # pragma: no cover - requires AWS
            import boto3
            client = boto3.client("dynamodb")
        self._ddb = client

    def consume(self, nonce: str, ttl_seconds: int = 900) -> bool:
        if not nonce:
            return False
        expires_at = int(time.time()) + int(ttl_seconds)
        try:
            self._ddb.put_item(
                TableName=self._table,
                Item={self._key: {"S": nonce}, self._ttl_attr: {"N": str(expires_at)}},
                ConditionExpression=f"attribute_not_exists({self._key})",
            )
            return True
        except Exception as exc:  # ConditionalCheckFailedException -> already used
            name = type(exc).__name__
            if "ConditionalCheckFailed" in name or "ConditionalCheckFailed" in str(exc):
                return False
            raise  # any other error fails closed at the caller


def default_store() -> ApprovalNonceStore:
    """In-memory by default; production wires a DynamoDBApprovalNonceStore."""
    return InMemoryApprovalNonceStore()
