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

### Linting & Formatting

Use `ruff` and `black` (if configured) for linting:

```bash
ruff check tooling/ tests/
```

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
