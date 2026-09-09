# employee.md

**An open, machine-readable contract format for AI agents.**

`employee.md` is a human-readable YAML document for describing an agent's identity, role, mission, scope, permissions, guardrails, economy, integrations, and compliance requirements. The repository includes a JSON Schema, CLI validator, Python runtime, reference contracts, and a static documentation site.

[![Validate](https://github.com/NosytLabs/employee-md/actions/workflows/validate.yml/badge.svg)](https://github.com/NosytLabs/employee-md/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg?style=flat-square)](pyproject.toml)
[![Schema](https://img.shields.io/badge/schema-JSON-orange.svg?style=flat-square)](tooling/schema.json)

> `AGENTS.md` describes a codebase to an agent. `employee.md` describes the agent itself.

## Quick start

Install the package and validate a contract:

```bash
pip install -e .
employee-validate employee.md
```

Create a minimal contract:

```yaml
---
spec:
  name: employee.md
  version: "1.0.0"
  kind: agent-employment

role:
  title: "Software Engineer"
  level: senior

mission:
  purpose: "Write clean, secure, maintainable code."

lifecycle:
  status: active
```

Useful CLI modes:

```bash
employee-validate employee.md --format json
employee-validate employee.md --format compact
employee-validate examples/*.md --parallel
employee-validate employee.md --metrics prometheus
employee-validate employee.md --production
```

Exit codes are `0` for valid, `1` for invalid, and `2` for parse errors.

## Contract shape

Only `spec`, `role`, and `lifecycle` are required. Other sections are optional.

```yaml
spec:           # name, version, kind
identity:       # agent_id, display_name, wallet, tags
role:           # title, level, capabilities, skills
mission:        # purpose, objectives, success criteria, non-goals
lifecycle:      # onboarding | active | suspended | terminated
context:        # project, repo, environment, team, organization
scope:          # in-scope, out-of-scope, dependencies, constraints
permissions:    # data, system, network, and tool access
guardrails:     # prohibited actions, approval gates, confidence threshold
economy:        # rate, currency, budget, payment method
verification:   # required checks, evidence, review policy
ai_settings:    # model preference, temperature, fallbacks
integration:    # MCP servers, APIs, webhooks
protocols:      # A2A, x402, human review, delegation
compliance:     # frameworks, data classification, audit retention
performance:    # metrics, KPIs, SLAs
communication:  # channels, timezone, availability
custom_fields:  # extensions
```

The machine-readable definition is [`tooling/schema.json`](tooling/schema.json). The repository's [`employee.md`](employee.md) is the canonical full reference.

## Examples

The repository ships with **11 standalone reference contracts** that are exercised by the validation gate:

| File | Persona |
|---|---|
| [`examples/minimal.md`](examples/minimal.md) | Smallest valid contract |
| [`examples/ai-assistant.md`](examples/ai-assistant.md) | General-purpose assistant |
| [`examples/senior-dev.md`](examples/senior-dev.md) | Software engineer |
| [`examples/security-auditor.md`](examples/security-auditor.md) | Compliance and security auditor |
| [`examples/data-analyst.md`](examples/data-analyst.md) | Data analyst |
| [`examples/devops-engineer.md`](examples/devops-engineer.md) | Infrastructure engineer |
| [`examples/product-manager.md`](examples/product-manager.md) | Product manager |
| [`examples/freelancer.md`](examples/freelancer.md) | Independent contractor |
| [`examples/trading-bot.md`](examples/trading-bot.md) | Autonomous trading agent |
| [`examples/zhc-worker.md`](examples/zhc-worker.md) | JouleWork / always-on worker |
| [`examples/maton-automation-agent.md`](examples/maton-automation-agent.md) | Cross-app Maton automation agent |

[`examples/molt-bot-integration.md`](examples/molt-bot-integration.md) is an **integration guide with embedded YAML**, not a standalone `employee.md` contract, so it is intentionally excluded from strict schema validation.

See [`examples/README.md`](examples/README.md) for the categorized example guide.

## Python runtime

Load a contract and enforce it at runtime:

```python
from runtime import Employee

employee = Employee.from_file("employee.md")
employee.guardrails.check("delete_production_data")
employee.economy.charge(0.05)
```

The lower-level validator is also importable:

```python
from tooling import validate_file

result = validate_file("employee.md")
if not result.is_valid:
    for error in result.errors:
        print(f"{error.field}: {error.message}")
```

## Integrations

`employee.md` can describe MCP endpoints, A2A coordination, x402 payment rules, human-review gates, and other agent infrastructure without replacing those protocols.

Example MCP configuration:

```yaml
integration:
  mcp_servers:
    - name: code-search
      endpoint: http://localhost:8080
      capabilities: [semantic_search, code_navigation]
```

Example x402 configuration:

```yaml
economy:
  payment_method: x402
  rate: 0.001
  currency: USDC
  budget_limit: 500
```

For framework recipes and protocol details, see [`INTEGRATION.md`](INTEGRATION.md).

### SKILL.md export

```python
from runtime import Employee
from runtime.skill_export import to_skill_md

employee = Employee.from_file("employee.md")
(skill_dir / "SKILL.md").write_text(to_skill_md(employee))
```

## Editor integration

Editors with YAML Schema support can validate `employee.md` while you type:

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/NosytLabs/employee-md/main/tooling/schema.json": "employee.md"
  }
}
```

## Development

Install development dependencies and run the same quality gate used by CI:

```bash
pip install -e ".[dev]"
make ci
```

The gate runs Ruff checks/format verification, mypy, pytest, permissive CLI validation of official contracts, and strict JSON Schema validation.

Individual commands:

```bash
make test
make lint
make format-check
make typecheck
make validate
make validate-strict
```

If you change Tailwind utility classes in the docs templates, regenerate the committed CSS with:

```bash
make tailwind
```

## Documentation site

The Flask documentation app lives in `web/`. `scripts/build_static_site.py` snapshots it into `dist/`, and `.github/workflows/static.yml` publishes the static site to GitHub Pages.

Live docs: **https://nosytlabs.github.io/employee-md/**

Run the docs locally:

```bash
pip install -e ".[dev]"
python -m web.app
```

Then open `http://localhost:5000`.

## Repository map

```text
employee.md              canonical full contract
tooling/schema.json      JSON Schema
tooling/                 validator and CLI
runtime/                 runtime enforcement SDK
examples/                reference contracts + integration guide
web/                     documentation application
tests/                   unit and integration tests
scripts/                 static-site and maintenance tooling
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution workflow and [`AGENTS.md`](AGENTS.md) for repository-specific agent guidance. Keep examples and validation whitelists synchronized when adding or removing an official reference contract.

## License

MIT © [Nosyt Labs](https://nosytlabs.com). See [`LICENSE`](LICENSE).
