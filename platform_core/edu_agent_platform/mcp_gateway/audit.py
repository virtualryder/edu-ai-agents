"""
Gateway audit log — tamper-evident, PII-masked record of every tool attempt.

Every decision (ALLOW / DENY / PENDING_APPROVAL / ERROR) is recorded with the
acting user, agent, tool, lineage to the system of record reached, and the
approver where a human gate applied. Free-text args are student-PII-masked before
they are written.

In production the sink is an append-only store (DynamoDB with a deny on
UpdateItem/DeleteItem, or S3 Object Lock) so the trail is tamper-evident by
design — supporting FERPA's recordkeeping of disclosures. Here it is an in-memory
list plus optional JSONL file so the model is testable.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import uuid
from typing import Any, Dict, List, Optional

from edu_agent_platform.pii_masker import mask


def _mask_args(args: Any) -> Any:
    if isinstance(args, dict):
        return {k: _mask_args(v) for k, v in args.items()}
    if isinstance(args, list):
        return [_mask_args(v) for v in args]
    if isinstance(args, str):
        return mask(args)
    return args


class GatewayAuditLog:
    def __init__(self, jsonl_path: Optional[str] = None) -> None:
        self.records: List[Dict[str, Any]] = []
        self._path = jsonl_path or os.getenv("GATEWAY_AUDIT_JSONL")

    def record(self, entry: Dict[str, Any]) -> str:
        audit_id = str(uuid.uuid4())
        full = {
            "audit_id": audit_id,
            "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            **entry,
        }
        if "args" in full:
            full["args"] = _mask_args(full["args"])
        if "detail" in full and isinstance(full["detail"], str):
            full["detail"] = mask(full["detail"])
        self.records.append(full)
        if self._path:  # pragma: no cover - file IO
            with open(self._path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(full) + "\n")
        return audit_id
