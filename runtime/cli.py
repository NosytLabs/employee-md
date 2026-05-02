"""Tiny CLI for the runtime SDK.

Usage:
    employee-runtime <file>                       # print system prompt
    employee-runtime <file> --check-action TEXT   # check a guardrail
    employee-runtime <file> --check-scope TEXT    # check a scope decision
    employee-runtime <file> --json                # machine-readable summary

Exit codes:
    0  success
    1  contract is invalid / file not found
    2  guardrail / scope check denied (when used with --check-action / --check-scope)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Optional

from .employee import ContractError, Employee


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="employee-runtime",
        description=(
            "Compile an employee.md contract into an LLM-ready system "
            "prompt and run guardrail / scope / budget checks against it."
        ),
    )
    p.add_argument(
        "file",
        type=Path,
        help="Path to an employee.md file (or any .md/.yaml file in the spec format).",
    )
    g = p.add_mutually_exclusive_group()
    g.add_argument(
        "--print-prompt",
        action="store_true",
        help="Print the LLM-ready system prompt (this is the default).",
    )
    g.add_argument(
        "--check-action",
        metavar="TEXT",
        help="Check whether TEXT is allowed by guardrails. Exits 2 on deny.",
    )
    g.add_argument(
        "--check-scope",
        metavar="TEXT",
        help="Check whether TEXT is in scope. Exits 2 on out-of-scope.",
    )
    g.add_argument(
        "--summary",
        action="store_true",
        help="Print a one-line summary (display_name / status / budget / counts).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human-readable text.",
    )
    p.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip schema validation (use only when the file is known-good).",
    )
    return p


def _emit(payload: dict, *, as_json: bool, fallback_text: str) -> None:
    if as_json:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(fallback_text)
        if not fallback_text.endswith("\n"):
            sys.stdout.write("\n")


def main(argv: Optional[List[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    try:
        emp = Employee.from_file(args.file, validate=not args.no_validate)
    except FileNotFoundError:
        msg = f"file not found: {args.file}"
        _emit({"ok": False, "error": msg}, as_json=args.json, fallback_text=f"error: {msg}")
        return 1
    except ContractError as exc:
        msg = str(exc)
        _emit({"ok": False, "error": msg}, as_json=args.json, fallback_text=f"error: {msg}")
        return 1

    if args.check_action:
        allowed = emp.is_action_allowed(args.check_action)
        _emit(
            {"ok": True, "action": args.check_action, "allowed": allowed},
            as_json=args.json,
            fallback_text=("allowed" if allowed else f"BLOCKED: {args.check_action}"),
        )
        return 0 if allowed else 2

    if args.check_scope:
        decision = emp.is_in_scope(args.check_scope)
        _emit(
            {
                "ok": True,
                "task": args.check_scope,
                "in_scope": decision.in_scope,
                "matched": decision.matched,
                "reason": decision.reason,
            },
            as_json=args.json,
            fallback_text=(
                f"in_scope ({decision.reason})"
                if decision.in_scope
                else f"OUT_OF_SCOPE ({decision.reason})"
            ),
        )
        return 0 if decision.in_scope else 2

    if args.summary:
        _emit(
            {
                "ok": True,
                "display_name": emp.display_name,
                "title": emp.title,
                "status": emp.status,
                "is_active": emp.is_active,
                "budget_limit": emp.budget.limit,
                "currency": emp.budget.currency,
                "prohibited_actions": len(emp.prohibited_actions()),
                "in_scope_entries": len(emp.in_scope()),
                "out_of_scope_entries": len(emp.out_of_scope()),
            },
            as_json=args.json,
            fallback_text=(
                f"{emp.display_name} — {emp.title} — status={emp.status} "
                f"— budget={emp.budget.limit} {emp.budget.currency} "
                f"— prohibited={len(emp.prohibited_actions())} "
                f"— in_scope={len(emp.in_scope())} "
                f"— out_of_scope={len(emp.out_of_scope())}"
            ),
        )
        return 0

    # Default: print the system prompt.
    prompt = emp.system_prompt()
    if args.json:
        _emit({"ok": True, "system_prompt": prompt}, as_json=True, fallback_text="")
    else:
        sys.stdout.write(prompt)
        if not prompt.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
