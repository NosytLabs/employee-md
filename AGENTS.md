# AGENTS.md

This file provides instructions for AI agents working on this repository.

## 🧭 Project Overview

`employee-md` is the repository for the **Agent Employment Contract Specification** and its associated tooling.
The goal is to define a standard for how AI agents are defined, managed, and audited.

### Directory Structure

- `employee.md`: The reference specification file.
- `PROMPT.md`: A prompt for generating valid `employee.md` files.
- `tooling/`: Python source code for the validator and CLI.
- `tests/`: Unit and integration tests.
- `examples/`: Example `employee.md` files for various roles.
- `AGENTS.md`: This file.

## 🛠️ Development Tools

### Installation

Install the package in editable mode with dev dependencies:

```bash
pip install -e ".[dev]"
```

### Running Tests

Use `pytest` or `make` to run tests:

```bash
make test
# OR
pytest tests/ -v
```

### Validation

To validate the `employee.md` file or examples:

```bash
make validate
# OR
employee-validate employee.md
employee-validate examples/*.md
```

### Linting, Formatting & Type Checking

The project uses `ruff` for both linting and formatting (no `black`), and
`mypy` for static type checking. The full CI quality gate is exposed via the
`Makefile`:

```bash
make lint           # ruff check tooling/         (CI scope is tooling/ only)
make format         # ruff format tooling/
make format-check   # ruff format --check tooling/   (CI gate)
make typecheck      # mypy tooling/ --ignore-missing-imports
make ci             # lint + format-check + typecheck + test + validate + validate-strict
```

> Note: CI does not lint or format the `tests/` tree. The existing test files
> have pre-existing unused-import findings that are out of scope for this
> hardening pass — do not expand the lint scope in `Makefile` or
> `.github/workflows/validate.yml` without first cleaning up `tests/` in a
> dedicated PR.

### Strict Schema Validation

Two validation surfaces exist and must both stay green:

1. `make validate` — the permissive runtime CLI (`python -m tooling.cli`).
   Friendly errors, designed to coach humans writing specs by hand.
2. `make validate-strict` — strict `jsonschema.Draft7Validator` against
   `tooling/schema.json`. This catches drift the permissive CLI ignores —
   in particular **unknown enum values** and **mistyped values**. It mirrors
   the `schema-check` job in `.github/workflows/validate.yml`.

> **Honest caveat about "strict":** `tooling/schema.json` does *not* set
> `additionalProperties: false`, so the strict validator does **not**
> reject unknown / stray top-level or sub-fields today. If you want the
> strict gate to also catch typos and shadow fields (e.g. a stray top-level
> `title:` shadowing `role.title`), that is a deliberate, separate change:
> add `additionalProperties: false` at the relevant levels of
> `tooling/schema.json`, audit every example, and ship it as a minor version
> bump.

If you add a new official example, add it to **both** `make validate` and the
strict whitelist in `Makefile` and `.github/workflows/validate.yml`.

## 📝 Coding Standards

- **Python**: Follow PEP 8. Use type hints.
- **YAML**: Ensure valid YAML syntax.
- **Commits**: Use descriptive commit messages.

## 🔒 Security

- The `tooling/parser.py` module includes security checks for path traversal and file sizes.
- Ensure any new file I/O operations are secure.

## 🤖 Context for Agents

If you are an agent reading this:
1.  Always verify your changes with `make test`.
2.  If modifying `employee.md` schema, update `tooling/schema.json` accordingly.
3.  Respect the `AGENTS.md` instructions.
