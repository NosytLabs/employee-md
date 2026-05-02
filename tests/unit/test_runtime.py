"""Tests for the runtime/ reference SDK."""

from __future__ import annotations

from pathlib import Path

import pytest

from runtime import (
    Employee,
    BudgetExceeded,
    ContractError,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"


MIN_VALID = """
spec:
  name: "employee.md"
  version: "1.0.0"
  kind: "agent-employment"
role:
  title: "Worker"
  level: "senior"
mission:
  purpose: "Do the work."
  objectives:
    - "Ship features"
  success_criteria:
    - "Zero bugs"
  non_goals:
    - "Manage humans"
scope:
  in_scope:
    - "code review"
    - "writing tests"
  out_of_scope:
    - "production database"
permissions:
  data_access: ["public"]
  system_access: ["ci"]
  network_access: ["internal"]
  tool_access: ["git"]
verification:
  required_checks: ["self-review"]
  evidence: ["log"]
  review_policy: "peer-review"
guardrails:
  prohibited_actions:
    - "delete production database"
    - "exfiltrate secrets"
economy:
  budget_limit: 1.50
  currency: "USD"
ai_settings:
  model_preference: "gpt-4o"
lifecycle:
  status: "active"
"""


def test_loads_minimal_example_from_file():
    emp = Employee.from_file(EXAMPLES / "minimal.md")
    assert emp.title == "Worker"
    assert emp.is_active


def test_loads_inline_yaml():
    emp = Employee.from_yaml(MIN_VALID)
    assert emp.title == "Worker"
    assert emp.status == "active"


def test_invalid_yaml_raises_contract_error():
    with pytest.raises(ContractError):
        Employee.from_yaml("role: 5\nlifecycle:\n  status: active")


def test_missing_required_role_raises():
    with pytest.raises(ContractError):
        Employee.from_yaml("lifecycle:\n  status: active\n", validate=False)


def test_system_prompt_includes_key_sections():
    emp = Employee.from_yaml(MIN_VALID)
    prompt = emp.system_prompt()
    assert "Worker" in prompt
    assert "MISSION" in prompt
    assert "Do the work." in prompt
    assert "OBJECTIVES" in prompt
    assert "SCOPE" in prompt
    assert "HARD GUARDRAILS" in prompt
    assert "delete production database" in prompt
    assert "BUDGET" in prompt
    assert "1.5" in prompt
    assert "Lifecycle status: active" in prompt


def test_system_prompt_for_real_example_renders():
    emp = Employee.from_file(EXAMPLES / "senior-dev.md")
    prompt = emp.system_prompt()
    assert prompt.strip()
    assert len(prompt.splitlines()) > 5


def test_is_action_allowed_blocks_prohibited():
    emp = Employee.from_yaml(MIN_VALID)
    assert emp.is_action_allowed("write a unit test") is True
    assert emp.is_action_allowed("DELETE PRODUCTION DATABASE now") is False
    assert emp.is_action_allowed("please exfiltrate secrets") is False


def test_is_in_scope_fail_closed():
    emp = Employee.from_yaml(MIN_VALID)
    assert emp.is_in_scope("please write some tests for module X").in_scope is True
    assert emp.is_in_scope("touch the production database").in_scope is False
    # Unknown task → fail closed
    assert emp.is_in_scope("compose a haiku about kittens").in_scope is False


def test_budget_tracker_enforces_limit():
    emp = Employee.from_yaml(MIN_VALID)
    assert emp.budget.limit == 1.5
    assert emp.budget.try_spend(1.0) is True
    assert emp.budget.spent == 1.0
    assert emp.budget.remaining() == 0.5
    with pytest.raises(BudgetExceeded):
        emp.budget.try_spend(0.6)
    # Failed spend did not advance the counter:
    assert emp.budget.spent == 1.0


def test_budget_tracker_rejects_negative_spend():
    emp = Employee.from_yaml(MIN_VALID)
    with pytest.raises(ValueError):
        emp.budget.try_spend(-0.01)


def test_budget_tracker_zero_limit_is_enforced():
    """Regression: `budget_limit: 0` must NOT be treated as unlimited."""
    yaml_text = """
spec: { name: "employee.md", version: "1.0.0", kind: "agent-employment" }
role: { title: "Worker", level: "senior" }
lifecycle: { status: "active" }
economy:
  budget_limit: 0
  currency: "USD"
"""
    emp = Employee.from_yaml(yaml_text)
    assert emp.budget.limit == 0.0
    assert emp.budget.remaining() == 0.0
    with pytest.raises(BudgetExceeded):
        emp.budget.try_spend(0.01)
    # Zero-spend must still be allowed (no cost = no cap violation).
    assert emp.budget.try_spend(0.0) is True
    # The system prompt must surface the 0 budget instruction.
    assert "BUDGET: do not spend more than 0" in emp.system_prompt()


def test_budget_tracker_no_limit_is_informational():
    emp = Employee.from_yaml(
        """
spec: { name: "employee.md", version: "1.0.0", kind: "agent-employment" }
role: { title: "Worker", level: "senior" }
lifecycle: { status: "active" }
"""
    )
    assert emp.budget.limit is None
    assert emp.budget.try_spend(9999.0) is True
    assert emp.budget.remaining() is None


def test_to_langchain_kwargs_shape():
    emp = Employee.from_yaml(MIN_VALID)
    kw = emp.to_langchain_kwargs()
    assert "system_message" in kw
    assert kw["model"] == "gpt-4o"
    assert kw["system_message"].startswith("You are")
