"""The Employee reference runtime.

Reads a validated `employee.md`, exposes the parts an agent runtime
actually needs at execution time:

    >>> from runtime import Employee
    >>> emp = Employee.from_file("examples/senior-dev.md")
    >>> print(emp.system_prompt())
    >>> emp.is_action_allowed("delete production database")
    False
    >>> emp.budget.try_spend(0.05)
    True

This is intentionally tiny (~200 LOC). It is not a sandbox and it is not
a replacement for proper guardrails — it is the thin wrapper every team
otherwise has to re-implement on top of the YAML schema.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import yaml

from tooling import EmployeeValidationOrchestrator, ValidationResult


class ContractError(ValueError):
    """Raised when the contract is structurally unusable (parse / required)."""


class BudgetExceeded(RuntimeError):
    """Raised when `BudgetTracker.try_spend` would exceed the configured limit."""

    def __init__(self, requested: float, spent: float, limit: float) -> None:
        self.requested = requested
        self.spent = spent
        self.limit = limit
        super().__init__(
            f"Budget exceeded: requested {requested:.4f}, "
            f"already spent {spent:.4f}, limit {limit:.4f}."
        )


@dataclass(frozen=True)
class ScopeDecision:
    """The result of an `Employee.is_in_scope(text)` check."""

    in_scope: bool
    matched: Optional[str]
    reason: str


class BudgetTracker:
    """Thread-safe spend tracker bound to `economy.budget_limit`.

    The tracker is best-effort: it enforces the limit *if* one is declared in
    the contract. If `economy.budget_limit` is missing or non-numeric, every
    `try_spend` returns True and `remaining` returns `None`.
    """

    def __init__(self, limit: Optional[float], currency: str = "USD") -> None:
        self._limit: Optional[float] = (
            float(limit) if isinstance(limit, (int, float)) and limit >= 0 else None
        )
        self._spent: float = 0.0
        self._lock = Lock()
        self.currency = currency

    @property
    def limit(self) -> Optional[float]:
        return self._limit

    @property
    def spent(self) -> float:
        with self._lock:
            return self._spent

    def remaining(self) -> Optional[float]:
        if self._limit is None:
            return None
        with self._lock:
            return max(0.0, self._limit - self._spent)

    def try_spend(self, amount: float) -> bool:
        """Atomically reserve `amount`. Raises BudgetExceeded if it would
        push past the configured limit.

        Returns True on success. If no limit is configured, always returns
        True (the tracker is informational only).
        """
        if amount < 0:
            raise ValueError("Cannot spend a negative amount.")
        with self._lock:
            if self._limit is not None and self._spent + amount > self._limit:
                raise BudgetExceeded(amount, self._spent, self._limit)
            self._spent += amount
            return True

    def reset(self) -> None:
        with self._lock:
            self._spent = 0.0


def _as_list(value: Any) -> List[str]:
    """Coerce a YAML field that might be missing / scalar / list into a list of strings."""
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if v is not None]
    return [str(value)]


class Employee:
    """A loaded, validated employee.md contract ready to drive an agent."""

    def __init__(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise ContractError("employee.md must be a YAML mapping at the top level.")
        self._data: Dict[str, Any] = data
        # Required by the spec — surface clear errors before runtime use.
        if not isinstance(data.get("role"), dict):
            raise ContractError("Missing required `role` mapping.")
        if not isinstance(data.get("lifecycle"), dict):
            raise ContractError("Missing required `lifecycle` mapping.")

        economy = data.get("economy") or {}
        # Use `in` checks (not falsy `or`) so an explicit `budget_limit: 0`
        # is honoured as a real cap rather than treated as "unlimited".
        if "budget_limit" in economy:
            limit = economy.get("budget_limit")
        elif "max_spend_per_task" in economy:
            limit = economy.get("max_spend_per_task")
        else:
            limit = None
        self.budget = BudgetTracker(
            limit=limit,
            currency=str(economy.get("currency") or "USD"),
        )

    # ---- constructors -------------------------------------------------

    @classmethod
    def from_yaml(cls, text: str, *, validate: bool = True) -> "Employee":
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ContractError(f"YAML parse error: {exc}") from exc
        if validate:
            cls._enforce_validation(text)
        return cls(data)

    @classmethod
    def from_file(cls, path: Union[str, Path], *, validate: bool = True) -> "Employee":
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        if validate:
            result = EmployeeValidationOrchestrator(use_cache=False).validate_file(str(path))
            cls._raise_for_result(result)
        return cls(yaml.safe_load(text))

    @staticmethod
    def _enforce_validation(text: str) -> None:
        orch = EmployeeValidationOrchestrator(use_cache=False)
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            raise ContractError(f"YAML parse error: {exc}") from exc
        try:
            result = orch.validate_data(data)
        except (TypeError, AttributeError, KeyError) as exc:
            # The validator currently crashes when a required section has the
            # wrong shape (e.g. `role: 5`). Surface that as a contract error
            # so callers don't have to special-case the underlying validator.
            raise ContractError(
                f"employee.md is structurally invalid: {exc.__class__.__name__}: {exc}"
            ) from exc
        Employee._raise_for_result(result)

    @staticmethod
    def _raise_for_result(result: ValidationResult) -> None:
        if not result.is_valid:
            top = result.errors[0] if result.errors else None
            msg = f"{top.field}: {top.message}" if top else "validation failed"
            raise ContractError(f"employee.md is invalid — {msg}")

    # ---- accessors ----------------------------------------------------

    @property
    def data(self) -> Dict[str, Any]:
        return self._data

    @property
    def agent_id(self) -> Optional[str]:
        ident = self._data.get("identity") or {}
        return ident.get("agent_id")

    @property
    def display_name(self) -> str:
        ident = self._data.get("identity") or {}
        return str(
            ident.get("display_name")
            or ident.get("agent_id")
            or self._data["role"].get("title")
            or "agent"
        )

    @property
    def title(self) -> str:
        return str(self._data["role"].get("title") or "agent")

    @property
    def status(self) -> str:
        return str(self._data["lifecycle"].get("status") or "unknown")

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    # ---- guardrails ---------------------------------------------------

    def prohibited_actions(self) -> List[str]:
        guardrails = self._data.get("guardrails") or {}
        return _as_list(guardrails.get("prohibited_actions"))

    def is_action_allowed(self, action: str) -> bool:
        """Case-insensitive substring check of `action` against the
        configured `guardrails.prohibited_actions` list.

        Returns False if any prohibited entry is a substring of `action`,
        OR if `action` is a substring of a prohibited entry. This is a
        deliberately permissive check so phrases like "delete the prod
        database" still trip a guardrail of "delete production database".
        """
        haystack = (action or "").strip().lower()
        if not haystack:
            return False
        for forbidden in self.prohibited_actions():
            needle = forbidden.strip().lower()
            if not needle:
                continue
            if needle in haystack or haystack in needle:
                return False
        return True

    # ---- scope --------------------------------------------------------

    def in_scope(self) -> List[str]:
        scope = self._data.get("scope") or {}
        return _as_list(scope.get("in_scope"))

    def out_of_scope(self) -> List[str]:
        scope = self._data.get("scope") or {}
        return _as_list(scope.get("out_of_scope"))

    @staticmethod
    def _tokens(text: str) -> set:
        """Tokenize a phrase into lowercase content words (≥3 chars).
        Strips punctuation and ignores stopwords like 'and'/'the'/'for'."""
        import re

        STOP = {"and", "the", "for", "with", "that", "this", "from", "into", "your"}
        return {
            w
            for w in re.findall(r"[a-zA-Z0-9_]{3,}", (text or "").lower())
            if w not in STOP
        }

    def _phrase_matches(self, phrase: str, haystack_tokens: set, haystack_lower: str) -> bool:
        """A phrase matches if any of these are true:
          1. its lowercase form is a substring of haystack
          2. every one of its content tokens has a prefix-match (≥4 chars)
             against some haystack token (so "writing"/"write"/"writes"
             all match each other without needing a real stemmer)
        """
        if not phrase:
            return False
        if phrase.lower() in haystack_lower:
            return True
        phrase_tokens = self._tokens(phrase)
        if not phrase_tokens:
            return False
        for pt in phrase_tokens:
            stem = pt[:4]
            if not any(ht.startswith(stem) or pt.startswith(ht[:4]) for ht in haystack_tokens):
                return False
        return True

    def is_in_scope(self, text: str) -> ScopeDecision:
        """Decide if `text` (a task description) is in scope.

        Algorithm:
          1. Tokenize `text` into lowercase content words.
          2. For each `out_of_scope` entry: if its substring appears verbatim
             OR all of its tokens are present, it's denied.
          3. Same check for `in_scope` entries — match → allowed.
          4. Otherwise denied (fail-closed) so unknown work always escalates.
        """
        haystack_lower = (text or "").lower()
        haystack_tokens = self._tokens(text)
        for needle in self.out_of_scope():
            if self._phrase_matches(needle, haystack_tokens, haystack_lower):
                return ScopeDecision(False, needle, "matched out_of_scope")
        for needle in self.in_scope():
            if self._phrase_matches(needle, haystack_tokens, haystack_lower):
                return ScopeDecision(True, needle, "matched in_scope")
        return ScopeDecision(
            False, None, "no in_scope entry matched (fail-closed default)"
        )

    # ---- LLM-ready prompt --------------------------------------------

    def system_prompt(self) -> str:
        """Compose an LLM-ready system prompt from the contract.

        The output is plain text, ~30 lines for a typical contract, and is
        designed to drop straight into the `system` slot of OpenAI /
        Anthropic / LangChain calls. It only emits sections that are
        actually present in the contract.
        """
        d = self._data
        identity = d.get("identity") or {}
        role = d.get("role") or {}
        mission = d.get("mission") or {}
        scope = d.get("scope") or {}
        guardrails = d.get("guardrails") or {}
        ai = d.get("ai_settings") or {}
        economy = d.get("economy") or {}

        lines: List[str] = []
        lines.append(f"You are {self.display_name}, a {role.get('title', 'agent')}.")
        if role.get("level"):
            lines.append(f"Level: {role['level']}.")
        if identity.get("agent_id"):
            lines.append(f"Agent ID: {identity['agent_id']}.")
        if mission.get("purpose"):
            lines.append("")
            lines.append("MISSION")
            lines.append(str(mission["purpose"]).strip())

        objectives = _as_list(mission.get("objectives"))
        if objectives:
            lines.append("")
            lines.append("OBJECTIVES")
            for o in objectives:
                lines.append(f"- {o}")

        success = _as_list(mission.get("success_criteria"))
        if success:
            lines.append("")
            lines.append("SUCCESS CRITERIA")
            for s in success:
                lines.append(f"- {s}")

        in_s = _as_list(scope.get("in_scope"))
        out_s = _as_list(scope.get("out_of_scope"))
        if in_s or out_s:
            lines.append("")
            lines.append("SCOPE")
            for s in in_s:
                lines.append(f"+ {s}")
            for s in out_s:
                lines.append(f"- DO NOT: {s}")

        prohibited = self.prohibited_actions()
        if prohibited:
            lines.append("")
            lines.append("HARD GUARDRAILS — never do any of these, no matter what:")
            for p in prohibited:
                lines.append(f"- {p}")

        review = guardrails.get("escalation_required") or guardrails.get(
            "human_review"
        )
        if review:
            lines.append(
                "If a request asks you to take an action you are unsure about, "
                "stop and request human review."
            )

        if economy:
            if "budget_limit" in economy:
                lim = economy.get("budget_limit")
            elif "max_spend_per_task" in economy:
                lim = economy.get("max_spend_per_task")
            else:
                lim = None
            # `is not None` so `budget_limit: 0` still emits the line
            # ("do not spend any money on this task" is a real instruction).
            if lim is not None and isinstance(lim, (int, float)) and lim >= 0:
                cur = economy.get("currency", "USD")
                lines.append("")
                lines.append(
                    f"BUDGET: do not spend more than {lim} {cur} per task."
                )

        if ai.get("model_preference"):
            lines.append("")
            lines.append(
                f"You are running on {ai['model_preference']}; tune verbosity accordingly."
            )

        lines.append("")
        lines.append(
            f"Lifecycle status: {self.status}. "
            "If status is not 'active', refuse all task requests."
        )
        return "\n".join(lines).strip() + "\n"

    # ---- conveniences -------------------------------------------------

    def to_langchain_kwargs(self) -> Dict[str, Any]:
        """Return a kwargs dict that fits langchain ChatPromptTemplate.from_messages."""
        return {
            "system_message": self.system_prompt(),
            "model": (self._data.get("ai_settings") or {}).get("model_preference"),
        }

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Employee {self.display_name!r} status={self.status!r}>"
