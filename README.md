# employee.md

**The open standard for AI agent employment contracts.**

A single human-readable, machine-parseable YAML file that defines how an AI agent operates — identity, role, mission, scope, permissions, guardrails, economy, and compliance. One contract, validated by a real JSON Schema, enforceable at runtime.

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg?style=flat-square)](pyproject.toml)
[![Tests](https://img.shields.io/badge/tests-303%20passing-brightgreen.svg?style=flat-square)](tests/)
[![Schema](https://img.shields.io/badge/schema-JSON-orange.svg?style=flat-square)](tooling/schema.json)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)

> If `AGENTS.md` tells an agent about the codebase, **`employee.md` tells the agent about itself**.

---

## Table of contents

- [Why](#why)
- [Quick start](#quick-start)
- [The spec at a glance](#the-spec-at-a-glance)
- [Examples](#examples)
- [CLI](#cli)
- [Python API](#python-api)
- [Editor integration](#editor-integration)
- [Protocols (x402, A2A, MCP, SKILL.md)](#protocols)
- [Website & hosting](#website--hosting)
- [Contributing](#contributing)
- [License](#license)

---

## Why

AI agents are becoming production workforce members. They need standardized, auditable contracts that define exactly what they are, what they can do, and what they must not do.

| Section | What it pins down |
|---|---|
| `identity` | Agent ID, version, wallet, tags |
| `role` | Job title, level, capabilities |
| `mission` | Purpose, objectives, non-goals |
| `scope` | In-scope / out-of-scope / dependencies |
| `permissions` | Data, system, network, and tool access |
| `guardrails` | Prohibited actions, approval gates, confidence threshold |
| `economy` | Rate, currency, budget cap, payment method (x402, fiat, crypto) |
| `compliance` | Frameworks (SOC2, GDPR), data class, audit retention |
| `ai_settings` | Model preference, temperature, fallbacks, reasoning effort |
| `integration` | MCP servers, APIs, webhooks |
| `protocols` | A2A, x402, human review, delegation |

Use cases: dev teams scoping coding assistants, enterprises deploying compliant agents, marketplaces standardizing capabilities, multi-agent systems coordinating via A2A.

---

## Quick start

### 1. Install the validator

```bash
pip install -e .
```

### 2. Create your `employee.md`

```yaml
---
spec:
  name: employee.md
  version: "1.0.0"
  kind: agent-employment

identity:
  agent_id: "my-agent-001"
  display_name: "My AI Agent"

role:
  title: "Software Engineer"
  level: senior

mission:
  purpose: "Write clean, secure, and maintainable code."

lifecycle:
  status: active
```

### 3. Validate

```bash
employee-validate employee.md
employee-validate employee.md --format json     # JSON output
employee-validate examples/*.md --parallel      # batch
```

That's it. The `examples/` directory has 10 ready-to-copy specs spanning AI assistant, senior dev, security auditor, data analyst, freelancer, product manager, DevOps, trading bot, and more.

---

## The spec at a glance

Every employee.md is a YAML document with these top-level sections. Only `spec`, `role`, and `lifecycle` are required; everything else is optional.

```yaml
spec:           # name + version + kind (REQUIRED)
identity:       # agent_id, display_name, version, wallet, tags
role:           # title + level (REQUIRED), capabilities, skills
mission:        # purpose, objectives, success_criteria, non_goals
lifecycle:      # status (REQUIRED): onboarding | active | suspended | terminated
context:        # project, repo, environment, team, organization
scope:          # in_scope, out_of_scope, dependencies, constraints
permissions:    # data_access, system_access, network_access, tool_access
guardrails:     # prohibited_actions, required_approval, confidence_threshold
economy:        # rate, currency, budget_limit, payment_method
verification:   # required_checks, evidence, review_policy, min_approvals
ai_settings:    # model_preference, temperature, fallback_models
integration:    # mcp_servers, apis, webhooks
protocols:      # a2a, x402, human_review, delegation
compliance:     # frameworks, data_classification, audit_retention_days
performance:    # efficiency_score, metrics, kpis, slas
communication:  # channels, timezone, availability, response_time_sla
custom_fields:  # extensions
```

The full machine-readable definition lives in [`tooling/schema.json`](tooling/schema.json). The repo's own [`employee.md`](employee.md) is the canonical reference implementation.

---

## Examples

| File | Persona | Level |
|---|---|---|
| [`examples/minimal.md`](examples/minimal.md) | Smallest valid spec | — |
| [`examples/ai-assistant.md`](examples/ai-assistant.md) | General-purpose assistant | senior |
| [`examples/senior-dev.md`](examples/senior-dev.md) | Software engineer | senior |
| [`examples/security-auditor.md`](examples/security-auditor.md) | Compliance / audit | senior |
| [`examples/data-analyst.md`](examples/data-analyst.md) | Analytics specialist | senior |
| [`examples/devops-engineer.md`](examples/devops-engineer.md) | Infrastructure | senior |
| [`examples/product-manager.md`](examples/product-manager.md) | Product strategy | senior |
| [`examples/freelancer.md`](examples/freelancer.md) | Independent contractor | — |
| [`examples/trading-bot.md`](examples/trading-bot.md) | Autonomous trading | — |
| [`examples/zhc-worker.md`](examples/zhc-worker.md) | JouleWork / always-on agent | — |
| [`examples/molt-bot-integration.md`](examples/molt-bot-integration.md) | Integration guide | — |

CI exercises every file under `examples/` against the JSON Schema on every push.

---

## CLI

```bash
employee-validate employee.md                      # plain text
employee-validate employee.md --format json        # JSON
employee-validate employee.md --format compact     # one-line, CI-friendly
employee-validate examples/*.md --parallel         # batch + parallel
employee-validate employee.md --metrics prometheus # emit Prometheus metrics
employee-validate employee.md --production         # sanitize errors for prod
```

Exit codes: `0` valid, `1` invalid, `2` parse error. Suitable for CI pipelines.

---

## Python API

```python
from tooling import validate_file

result = validate_file("employee.md")
if result.is_valid:
    print("OK")
else:
    for err in result.errors:
        print(f"{err.field}: {err.message}")
```

A higher-level runtime SDK lives in `runtime/` and lets you load an `employee.md` as a typed `Employee` object, enforce guardrails at call time, and export to other formats:

```python
from runtime import Employee

emp = Employee.from_file("employee.md")
emp.guardrails.check("delete_production_data")   # raises if prohibited
emp.economy.charge(0.05)                         # raises if over budget
```

---

## Editor integration

VS Code (and any editor with the YAML extension) can validate live against the published schema:

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/NosytLabs/employee-md/main/tooling/schema.json": "employee.md"
  }
}
```

You get inline autocomplete, type hints, and error squiggles as you type.

---

## Protocols

employee.md is designed to interoperate with the agentic ecosystem rather than replace it.

### x402 — HTTP-native agent payments

```yaml
economy:
  payment_method: x402
  rate: 0.001
  currency: USDC
  budget_limit: 500
  wallet:
    chain: base
    address: "0x..."
```

### A2A — Google's Agent-to-Agent protocol

```yaml
protocols:
  a2a:
    enabled: true
    discovery: true
    authentication: oauth2
    coordination:
      mode: collaborative
      max_agents: 5
```

### MCP — Model Context Protocol

```yaml
integration:
  mcp_servers:
    - name: code-search
      endpoint: http://localhost:8080
      capabilities: [semantic_search, code_navigation]
```

### Anthropic SKILL.md export

```python
from runtime import Employee
from runtime.skill_export import to_skill_md

emp = Employee.from_file("employee.md")
(skill_dir / "SKILL.md").write_text(to_skill_md(emp))
```

See [`INTEGRATION.md`](INTEGRATION.md) for full CrewAI / LangGraph / AutoGen / MCP recipes.

---

## Website & hosting

The repo ships with a Flask docs site (`web/`) — spec reference, examples gallery, integration guide, and runtime SDK docs. The site is fully static: `scripts/build_static_site.py` snapshots every route into `dist/`, which `.github/workflows/static.yml` deploys to **GitHub Pages** (`nosytlabs.github.io/employee-md/`) on every push to `main`. Validation is CLI-only — there is no live web validator.

### Enabling GitHub Pages (one-time)

After cloning this repo, go to:

**Settings → Pages → Build and deployment → Source → `GitHub Actions`**

The next push to `main` builds and deploys. (If Source is left as "Deploy from a branch", GitHub will fall back to Jekyll and just render this README — not what you want.)

### Run locally

```bash
pip install -e ".[dev,web]"
python -m web.app                       # dev server on http://localhost:5000
python scripts/build_static_site.py     # produce dist/ for GH Pages
make tailwind                           # rebuild CSS if you edit a template
```

288 tests; run with `pytest tests/ -v`.

---

## Contributing

Issues and PRs welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the workflow and [`AGENTS.md`](AGENTS.md) for agent-specific guidelines.

```bash
git clone https://github.com/NosytLabs/employee-md.git
cd employee-md
pip install -e ".[dev,web]"
pytest tests/ -v
ruff check tooling/ runtime/ web/
employee-validate examples/*.md
```

---

## License

MIT © [Nosyt Labs](https://nosytlabs.com). See [`LICENSE`](LICENSE).
