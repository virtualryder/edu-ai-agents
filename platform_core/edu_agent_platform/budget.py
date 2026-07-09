"""budget — per-agent token budget meter with a hard/soft cap (AGP v1.0 FinOps clause).

Real-time preflight that DENIES (hard) or WARNS (soft) an over-budget call *before* spend —
fail-closed on budget — plus one-time threshold alerts. Offline analog of the gateway meter;
in production AWS Budgets is a second account-level guardrail. Ported from the Aegis platform
so every AGP-conformant pack enforces the same cost-control contract. No dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BudgetDecision:
    allowed: bool
    reason: str
    used_before: int
    requested: int
    cap: int
    cap_behavior: str
    throttled: bool = False
    fired_alerts: list = field(default_factory=list)

    @property
    def remaining(self) -> int:
        return max(self.cap - self.used_before, 0)


class BudgetMeter:
    """A running token meter for one agent/department budget line."""

    def __init__(self, agent_id: str, dept: str, monthly_token_cap: int,
                 cap_behavior: str = "hard", alert_thresholds=None, inference_profile: str = ""):
        if monthly_token_cap < 1:
            raise ValueError("monthly_token_cap must be >= 1")
        if cap_behavior not in ("hard", "soft"):
            raise ValueError("cap_behavior must be 'hard' or 'soft'")
        self.agent_id = agent_id
        self.dept = dept
        self.cap = int(monthly_token_cap)
        self.cap_behavior = cap_behavior
        self.alert_thresholds = sorted(alert_thresholds or [0.6, 0.85, 1.0])
        self.inference_profile = inference_profile
        self.used = 0
        self._alerts_fired: set = set()

    def preflight(self, estimated_tokens: int) -> BudgetDecision:
        if estimated_tokens < 0:
            raise ValueError("estimated_tokens must be >= 0")
        projected = self.used + estimated_tokens
        would_breach = projected > self.cap
        fired = self._peek_alerts(projected)
        if would_breach and self.cap_behavior == "hard":
            return BudgetDecision(
                allowed=False,
                reason=(f"budget_exceeded: hard cap {self.cap:,} tokens for agent "
                        f"'{self.agent_id}' (dept '{self.dept}') would be breached: "
                        f"{self.used:,} used + {estimated_tokens:,} requested = {projected:,}"),
                used_before=self.used, requested=estimated_tokens, cap=self.cap,
                cap_behavior=self.cap_behavior, throttled=False, fired_alerts=fired)
        if would_breach and self.cap_behavior == "soft":
            return BudgetDecision(
                allowed=True,
                reason=f"budget_soft_over_cap: soft cap {self.cap:,} exceeded (projected {projected:,})",
                used_before=self.used, requested=estimated_tokens, cap=self.cap,
                cap_behavior=self.cap_behavior, throttled=True, fired_alerts=fired)
        return BudgetDecision(allowed=True, reason="budget_ok", used_before=self.used,
                              requested=estimated_tokens, cap=self.cap,
                              cap_behavior=self.cap_behavior, throttled=False, fired_alerts=fired)

    def commit(self, actual_tokens: int) -> list:
        if actual_tokens < 0:
            raise ValueError("actual_tokens must be >= 0")
        self.used += actual_tokens
        crossed = self._peek_alerts(self.used)
        newly = [t for t in crossed if t not in self._alerts_fired]
        self._alerts_fired.update(newly)
        return newly

    def _peek_alerts(self, level: int) -> list:
        frac = level / self.cap if self.cap else 0.0
        return [t for t in self.alert_thresholds if frac >= t]

    @property
    def utilization(self) -> float:
        return self.used / self.cap if self.cap else 0.0
