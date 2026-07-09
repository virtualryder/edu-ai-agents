"""Budget meter (AGP FinOps clause): hard cap denies before spend; soft cap warns."""
import pytest

from edu_agent_platform.budget import BudgetMeter


def test_hard_cap_denies_over_budget_before_spend():
    m = BudgetMeter("01-student-family-concierge", "StudentServices", monthly_token_cap=1000, cap_behavior="hard")
    m.commit(900)
    d = m.preflight(500)
    assert d.allowed is False and "budget_exceeded" in d.reason
    assert m.used == 900


def test_under_budget_allowed():
    assert BudgetMeter("a", "d", monthly_token_cap=1000).preflight(100).allowed is True


def test_soft_cap_allows_with_throttle():
    m = BudgetMeter("a", "d", monthly_token_cap=100, cap_behavior="soft")
    m.commit(90)
    assert m.preflight(50).throttled is True


def test_invalid_cap_rejected():
    with pytest.raises(ValueError):
        BudgetMeter("a", "d", monthly_token_cap=0)
