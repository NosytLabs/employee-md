# Contributing to employee.md

Thank you for your interest in contributing to the **employee.md** open standard! We welcome contributions from the community to help define the future of AI agent employment contracts.

`employee.md` is part of a broader ecosystem of open standards for the Agentic Web. We aim to ensure interoperability with standards like **[AGENTS.md](https://agents.md)** and **[MCP](https://modelcontextprotocol.io/)**.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Development Setup

1. **Clone the repository:**
```bash
git clone https://github.com/NosytLabs/employee-md.git
cd employee-md
```

2. **Create a virtual environment:**
```bash
# Using venv (built-in)
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
# Install in development mode (includes all dev dependencies)
pip install -e ".[dev]"
```

4. **Verify installation:**
```bash
# Run the validator CLI
employee-validate --version

# Run a quick validation test
employee-validate examples/minimal.md
```

---

## 🛠️ Development Tools

We use modern Python tools to maintain code quality:

| Tool | Purpose | Command |
|------|---------|---------|
| **pytest** | Test framework | `pytest` |
| **pytest-cov** | Coverage reporting | `pytest --cov=tooling --cov-report=html` |
| **ruff** | Linting & formatting | `ruff check tooling/`, `ruff format tooling/` |
| **mypy** | Type checking | `mypy tooling/ --ignore-missing-imports` |
| **pre-commit** | Git hooks | `pre-commit run --all-files` |

### Running Quality Checks

```bash
# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ -v --cov=tooling --cov-report=html --cov-report=term

# Run linting
ruff check tooling/ tests/

# Format code
ruff format tooling/ tests/

# Type checking
mypy tooling/ --ignore-missing-imports --show-error-codes

# Run all pre-commit hooks
pre-commit run --all-files
```

---

## 📋 How to Contribute

### 1. Propose Changes

- **Open an Issue**: For major changes or new sections, please [open an issue](https://github.com/NosytLabs/employee-md/issues) first to discuss the proposal.
- **Join the Discussion**: Engage with other contributors in [GitHub Discussions](https://github.com/NosytLabs/employee-md/discussions).

### 2. Make Changes

- **Fork the Repository**: Create your own fork of the repo.
- **Create a Branch**: Use a descriptive branch name:
  - `feature/add-section-name` for new features
  - `fix/description-of-fix` for bug fixes
  - `docs/description` for documentation updates
- **Edit the Spec**: Update `employee.md` and `tooling/schema.json` as needed.
- **Update Examples**: Ensure all examples in `examples/` reflect your changes.
- **Update Docs**: Don't forget to update `README.md` and `INTEGRATION.md` if relevant.

### 3. Validate Your Changes

Before submitting, run the validation tools:

```bash
# Validate the main spec
employee-validate employee.md

# Validate all examples
employee-validate examples/*.md

# Run full test suite
pytest tests/ -v

# Check code quality
ruff check tooling/ tests/
mypy tooling/ --ignore-missing-imports
```

### 4. Test Your Changes

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v

# Run performance tests
pytest tests/performance/ -v

# Run specific test file
pytest tests/unit/test_parser.py -v

# Run with verbose output
pytest -vv
```

### 5. Submit Pull Request

- **Description**: Clearly explain what you changed and why.
- **Checklist**: Confirm you've updated the schema, examples, and docs.
- **CI**: Ensure the GitHub Actions validation passes.
- **Tests**: Ensure all tests pass before submitting.

See our [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md) for details.

---

## 🎯 Design Principles

When proposing changes, keep these principles in mind:

| Principle | Description |
|-----------|-------------|
| **AI-First** | The spec is primarily read by AI agents. Keep structures logical, explicit, and easy to parse. |
| **Human-Readable** | It must also be easy for humans to write and review. Use clear keys and inline comments. |
| **Flexible** | Avoid over-prescribing implementation details. Focus on *what* (interfaces, constraints) rather than *how*. |
| **Modular** | Allow sections to be optional where possible. Not every agent needs every section. |
| **Backward Compatible** | Prefer additive changes. Avoid breaking existing valid configs. |
| **Extensible** | Use `custom_fields` for organization-specific extensions. |

---

## 📝 Style Guide

### YAML Formatting

- Use standard YAML 1.2 formatting
- Indent with 2 spaces (not tabs)
- Use `snake_case` for all keys
- Group related fields together
- Add inline comments for complex fields

```yaml
# Good
role:
  title: "Software Engineer"    # Job title (required)
  level: senior                 # junior | mid | senior | lead
  department: "Engineering"     # Team/department name

# Bad
role:
  title:Software Engineer
  level:Senior
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Keys | `snake_case` | `agent_id`, `display_name` |
| Enums | `snake_case` | `full_time`, `peer_review` |
| IDs | `kebab-case` or descriptive | `my-agent-001`, `engineering-bot` |
| Dates | ISO 8601 | `2026-01-15` |

### Comments

- Use inline comments (`#`) for field descriptions
- Document enum options where applicable
- Explain complex business logic
- Keep comments concise but informative

```yaml
ai_settings:
  model_preference: gpt-4o      # Primary LLM to use
  temperature: 0.7              # 0.0 = deterministic, 1.0 = creative
```

---

## 🧪 Adding Tests

When adding new features, please include tests:

```python
# tests/unit/test_new_feature.py
import pytest
from tooling.validators import NewValidator

def test_new_validator_success():
    validator = NewValidator()
    result = validator.validate({"field": "value"})
    assert result.is_valid

def test_new_validator_failure():
    validator = NewValidator()
    result = validator.validate({"field": None})
    assert not result.is_valid
    assert len(result.errors) == 1
```

### Test Categories

| Category | Location | Purpose |
|----------|----------|---------|
| Unit Tests | `tests/unit/` | Test individual components in isolation |
| Integration Tests | `tests/integration/` | Test component interactions |
| Performance Tests | `tests/performance/` | Benchmarks and regression tests |

---

## 🏷️ Versioning

We follow [Semantic Versioning](https://semver.org/) for the specification:

- **MAJOR**: Incompatible changes to required fields or structure
- **MINOR**: Additive changes (new optional sections or fields)
- **PATCH**: Bug fixes, documentation improvements, clarifications

When updating the spec:

1. Update `version` in `employee.md` spec section
2. Update `version` in `pyproject.toml`
3. Update `version` in `tooling/schema.json`
4. Update `CHANGELOG.md`
5. Update all examples to reference new version

---

## 🌐 Community

- **Code of Conduct**: Be respectful and constructive. See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
- **Questions**: Open a [discussion](https://github.com/NosytLabs/employee-md/discussions) for help.
- **Security Issues**: See [SECURITY.md](SECURITY.md) for reporting procedures.

---

## 📚 Resources

- [JSON Schema Reference](https://json-schema.org/)
- [YAML 1.2 Spec](https://yaml.org/spec/1.2.2/)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [AGENTS.md](https://agents.md)

---

**Happy Coding!** 🤖✨
