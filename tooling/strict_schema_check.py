"""Strict JSON Schema validation for every official employee.md spec/example.

This is the local mirror of the ``schema-check`` job in
``.github/workflows/validate.yml``. It uses ``jsonschema.Draft7Validator``
against ``tooling/schema.json`` and rejects **unknown enum values** and
**mistyped values** that the permissive CLI happily ignores.

Honest caveat: ``tooling/schema.json`` does **not** set
``additionalProperties: false``, so this strict gate does **not** currently
reject unknown / stray top-level or sub-fields (e.g. a stray top-level
``title:`` shadowing ``role.title``). Adding strict unknown-field rejection
is a deliberate, separate change tracked in the project backlog.

``examples/molt-bot-integration.md`` is intentionally excluded because it is
a markdown integration guide with embedded YAML, not a standalone spec.

Run via ``make validate-strict`` or directly:

    python tooling/strict_schema_check.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List

import yaml
from jsonschema import Draft7Validator

# Resolve paths relative to this file so the script works from any cwd.
_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCHEMA_PATH = _REPO_ROOT / "tooling" / "schema.json"

# The complete set of official files that MUST pass strict schema validation.
# Keep this list in sync with the ``schema-check`` whitelist in
# ``.github/workflows/validate.yml`` and the ``validate`` target in the
# ``Makefile``.
OFFICIAL_FILES: List[str] = [
    "employee.md",
    "examples/minimal.md",
    "examples/senior-dev.md",
    "examples/ai-assistant.md",
    "examples/security-auditor.md",
    "examples/data-analyst.md",
    "examples/freelancer.md",
    "examples/devops-engineer.md",
    "examples/product-manager.md",
    "examples/zhc-worker.md",
    "examples/trading-bot.md",
]


def main() -> int:
    with _SCHEMA_PATH.open() as fh:
        schema = json.load(fh)
    validator = Draft7Validator(schema)

    failed = 0
    for rel_path in OFFICIAL_FILES:
        fp = _REPO_ROOT / rel_path
        with fp.open() as fh:
            data = yaml.safe_load(fh)
        errors = sorted(
            validator.iter_errors(data),
            key=lambda e: list(e.absolute_path),
        )
        if not errors:
            print(f"OK   {rel_path}")
            continue
        failed += 1
        print(f"FAIL {rel_path} ({len(errors)} errors)")
        for err in errors[:8]:
            path = ".".join(str(p) for p in err.absolute_path) or "<root>"
            print(f"     - {path}: {err.message}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
