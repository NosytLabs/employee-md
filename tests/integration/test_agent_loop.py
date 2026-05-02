"""End-to-end proof that an agent loop will actually obey an employee.md contract.

This is the test the README and /why page point at when claiming "the contract
is enforceable, not advisory." It builds a *minimal* simulated agent loop —
no LLM, no network — that:

  1. Loads an employee.md contract via the runtime SDK.
  2. Receives a stream of candidate actions (some allowed, some prohibited,
     some over-budget, some out-of-scope).
  3. Decides each one strictly against the contract:
       * `Employee.is_action_allowed()`     — guardrails.prohibited_actions
       * `Employee.is_in_scope()`           — scope.in_scope / out_of_scope
       * `Employee.budget.try_spend()`      — economy.budget_limit
  4. Records every decision with the violated field for audit.

The test asserts both shapes of compliance:

    * **Affirmative compliance** — actions inside the contract execute.
    * **Negative compliance** — actions outside the contract are refused
      with a structured reason that names the violated field.

If any future refactor breaks contract enforcement, this test fails.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import pytest

from runtime import BudgetExceeded, Employee


EXAMPLES = Path(__file__).resolve().parent.parent.parent / "examples"


# -----------------------------------------------------------------------
# Minimal simulated agent loop — no LLM, no network. The point is to
# prove the contract enforcement path is exercised end-to-end.
# -----------------------------------------------------------------------


@dataclass
class Decision:
    action: str
    cost: float
    allowed: bool
    reason: Optional[str]   # None when allowed
    field: Optional[str]    # Which contract field caused the refusal, if any


class SimulatedAgent:
    """A tiny, deterministic stand-in for an LLM-driven agent loop."""

    def __init__(self, employee: Employee) -> None:
        self.employee = employee
        self.audit_log: List[Decision] = []

    def consider(self, action: str, cost: float = 0.0) -> Decision:
        # 1. Guardrails — prohibited actions are rejected outright.
        if not self.employee.is_action_allowed(action):
            d = Decision(action, cost, False, "matches a prohibited action", "guardrails.prohibited_actions")
            self.audit_log.append(d)
            return d

        # 2. Scope — must fall inside in_scope / not match out_of_scope.
        scope = self.employee.is_in_scope(action)
        if not scope.in_scope:
            d = Decision(action, cost, False, scope.reason, "scope")
            self.audit_log.append(d)
            return d

        # 3. Per-task spend cap (declared in guardrails, separate from budget pool).
        cap = (self.employee.data.get("guardrails") or {}).get("max_spend_per_task")
        if isinstance(cap, (int, float)) and cost > cap:
            d = Decision(action, cost, False,
                         f"cost {cost} exceeds max_spend_per_task {cap}",
                         "guardrails.max_spend_per_task")
            self.audit_log.append(d)
            return d

        # 4. Budget pool — economy.budget_limit, enforced atomically.
        try:
            self.employee.budget.try_spend(cost)
        except BudgetExceeded as e:
            d = Decision(action, cost, False, str(e), "economy.budget_limit")
            self.audit_log.append(d)
            return d

        d = Decision(action, cost, True, None, None)
        self.audit_log.append(d)
        return d


# -----------------------------------------------------------------------
# Test cases — the actual proof.
# -----------------------------------------------------------------------


def _build_agent_with_strict_contract() -> SimulatedAgent:
    """Build an Employee with a tight, well-known contract so we can assert
    exact behaviour without depending on an example file."""
    emp = Employee({
        "role": {"title": "Senior Engineer", "level": "senior"},
        "mission": {"purpose": "Ship reliable backend code."},
        "scope": {
            "in_scope": ["write code", "run tests", "open pull request"],
            "out_of_scope": ["deploy to production", "modify billing"],
        },
        "guardrails": {
            "prohibited_actions": ["delete production database", "leak credentials"],
            "max_spend_per_task": 5.0,
        },
        "economy": {"budget_limit": 20.0, "currency": "USD"},
        "lifecycle": {"status": "active"},
    })
    return SimulatedAgent(emp)


def test_allowed_action_executes_and_is_audited():
    agent = _build_agent_with_strict_contract()
    d = agent.consider("write code", cost=2.0)
    assert d.allowed is True
    assert d.field is None
    assert agent.employee.budget.spent == pytest.approx(2.0)


def test_prohibited_action_is_refused_with_field():
    agent = _build_agent_with_strict_contract()
    d = agent.consider("delete production database", cost=0)
    assert d.allowed is False
    assert d.field == "guardrails.prohibited_actions"


def test_prohibited_substring_match_still_caught():
    """A wrapped/rephrased action that still contains the prohibited
    substring must be refused by the guardrail check, not slip through
    on a literal-string mismatch."""
    agent = _build_agent_with_strict_contract()
    d = agent.consider("urgent: delete production database immediately", cost=0)
    assert d.allowed is False
    assert d.field == "guardrails.prohibited_actions"


def test_out_of_scope_action_is_refused():
    agent = _build_agent_with_strict_contract()
    d = agent.consider("deploy to production", cost=1.0)
    assert d.allowed is False
    assert d.field == "scope"


def test_per_task_spend_cap_is_enforced():
    agent = _build_agent_with_strict_contract()
    d = agent.consider("write code", cost=10.0)  # cap = 5.0
    assert d.allowed is False
    assert d.field == "guardrails.max_spend_per_task"
    # The refused action must not have charged the budget pool.
    assert agent.employee.budget.spent == 0.0


def test_budget_pool_enforced_across_actions():
    agent = _build_agent_with_strict_contract()
    # Pool is 20, per-task cap is 5 → four allowed runs, then fifth must fail.
    for _ in range(4):
        assert agent.consider("write code", cost=5.0).allowed is True
    final = agent.consider("write code", cost=5.0)
    assert final.allowed is False
    assert final.field == "economy.budget_limit"
    assert agent.employee.budget.spent == pytest.approx(20.0)


def test_full_simulated_loop_audit_log_shape():
    """Run a realistic mixed sequence and assert the audit log is honest."""
    agent = _build_agent_with_strict_contract()
    sequence = [
        ("write code", 1.0),                          # ✓
        ("delete production database", 0.0),          # ✗ prohibited
        ("run tests", 0.5),                           # ✓
        ("deploy to production", 0.0),                # ✗ scope
        ("open pull request", 1.0),                   # ✓
        ("write code", 99.0),                         # ✗ per-task cap
    ]
    for action, cost in sequence:
        agent.consider(action, cost)

    assert len(agent.audit_log) == 6
    allowed = [d for d in agent.audit_log if d.allowed]
    refused = [d for d in agent.audit_log if not d.allowed]
    assert len(allowed) == 3
    assert len(refused) == 3
    # Every refusal carries a structured field — proves enforcement is auditable.
    assert all(d.field for d in refused)
    refused_fields = {d.field for d in refused}
    assert refused_fields == {
        "guardrails.prohibited_actions",
        "scope",
        "guardrails.max_spend_per_task",
    }


def test_real_trading_bot_example_refuses_unauthorized_withdraw():
    """The trading-bot example (added in v1.0.0) must refuse withdrawals."""
    emp = Employee.from_file(EXAMPLES / "trading-bot.md", validate=False)
    agent = SimulatedAgent(emp)
    d = agent.consider("withdraw_funds", cost=0)
    assert d.allowed is False
    assert d.field == "guardrails.prohibited_actions"


def test_real_trading_bot_example_per_task_cap_enforced():
    """A trade larger than max_spend_per_task must be refused even if the
    action itself is permitted and in scope.

    We pass an action description that contains the literal in_scope phrase
    as a substring, which the scope check matches verbatim before falling
    through to the per-task cap.
    """
    emp = Employee.from_file(EXAMPLES / "trading-bot.md", validate=False)
    cap = emp.data["guardrails"]["max_spend_per_task"]
    in_scope_phrase = emp.data["scope"]["in_scope"][0]
    agent = SimulatedAgent(emp)
    d = agent.consider(in_scope_phrase, cost=cap + 1)
    assert d.allowed is False
    assert d.field == "guardrails.max_spend_per_task"


def test_real_trading_bot_example_allowed_action_within_cap():
    """An in-scope, non-prohibited action below the per-task cap goes through."""
    emp = Employee.from_file(EXAMPLES / "trading-bot.md", validate=False)
    cap = emp.data["guardrails"]["max_spend_per_task"]
    in_scope_phrase = emp.data["scope"]["in_scope"][0]
    agent = SimulatedAgent(emp)
    d = agent.consider(in_scope_phrase, cost=cap / 10)
    assert d.allowed is True, f"expected allowed, refused with reason: {d.reason}"
