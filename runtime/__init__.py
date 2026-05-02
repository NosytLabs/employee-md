"""Reference runtime for employee.md.

This package turns a validated `employee.md` contract from a piece of
documentation into something an agent can actually execute against:

  - `Employee.from_file("employee.md")` loads + validates the contract.
  - `.system_prompt()` returns an LLM-ready system prompt string.
  - `.is_action_allowed(action)` checks the action against `guardrails`.
  - `.is_in_scope(text)` checks a task description against `scope`.
  - `.budget` is a `BudgetTracker` you call `.try_spend(amount)` on; it
    raises `BudgetExceeded` when `economy.budget_limit` is exhausted.

It depends only on `tooling` (the existing validator) and PyYAML, so it
ships with the same install as the validator itself.
"""

from .employee import (
    Employee,
    BudgetTracker,
    BudgetExceeded,
    ContractError,
    ScopeDecision,
)

__all__ = [
    "Employee",
    "BudgetTracker",
    "BudgetExceeded",
    "ContractError",
    "ScopeDecision",
]
