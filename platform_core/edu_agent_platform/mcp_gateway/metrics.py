"""
Operational telemetry — the custom CloudWatch metrics the observability stack
(`infra/cloudformation/observability.yaml`) alarms on.

The gateway emits these on the control-loop events a SOC/operations team must see:
authorization denials, record-scope denials, approval demand, masking failures,
grounding failures, and audit-write failures. Metric NAMES here are the contract
with the alarms in observability.yaml — keep them in sync.

In demo/test mode `emit()` only captures to an in-process buffer (assertable in
tests). In production it calls CloudWatch `put_metric_data`; telemetry failures are
swallowed so they can never break the request path.
"""
from __future__ import annotations

import os
import threading
from typing import Dict, List, Optional

from .approvals import _demo_mode

NAMESPACE = os.getenv("EDU_METRICS_NAMESPACE", "EduAgentSuite")

# Canonical metric names — MUST match observability.yaml.
TOOL_AUTH_DENIED = "ToolAuthorizationDenied"
RECORD_SCOPE_DENIED = "RecordScopeDenied"
APPROVAL_REQUIRED = "ApprovalRequired"
APPROVAL_BACKLOG_AGE = "ApprovalBacklogAge"
PII_MASKING_FAILURE = "PiiMaskingFailure"
GROUNDING_FAILURE = "GroundingFailure"
AUDIT_WRITE_FAILURE = "AuditWriteFailure"

_buffer: List[dict] = []
_lock = threading.Lock()


def emit(metric: str, value: float = 1.0, unit: str = "Count",
         dims: Optional[Dict[str, str]] = None) -> None:
    rec = {"metric": metric, "value": value, "unit": unit, "dims": dims or {}}
    with _lock:
        _buffer.append(rec)
    if _demo_mode():
        return
    try:  # pragma: no cover - requires AWS
        import boto3
        boto3.client("cloudwatch").put_metric_data(
            Namespace=NAMESPACE,
            MetricData=[{
                "MetricName": metric, "Value": value, "Unit": unit,
                "Dimensions": [{"Name": k, "Value": v} for k, v in (dims or {}).items()],
            }],
        )
    except Exception:
        pass  # telemetry must never break the request path


def recorded() -> List[dict]:
    with _lock:
        return list(_buffer)


def reset() -> None:
    with _lock:
        _buffer.clear()
