# employee.md

```text
  _____                 _                                _
 | ____|_ __ ___  _ __ | | ___  _   _  ___  ___   _ __ ___   __| |
 |  _| | '_ ` _ \| '_ \| |/ _ \| | | |/ _ \/ _ \ | '_ ` _ \ / _` |
 | |___| | | | | | |_) | | (_) | |_| |  __/  __/ | | | | | | (_| |
 |_____|_| |_| |_| .__/|_|\___/ \__, |\___|\___| |_| |_| |_|\__,_|
                 |_|            |___/
```

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg?style=flat-square)](CHANGELOG.md)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
[![Build Status](https://github.com/NosytLabs/employee-md/actions/workflows/validate.yml/badge.svg?style=flat-square)](https://github.com/NosytLabs/employee-md/actions)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg?style=flat-square)](pyproject.toml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)
[![Schema](https://img.shields.io/badge/schema-JSON-orange.svg?style=flat-square)](tooling/schema.json)
[![Website](https://img.shields.io/badge/website-employee.md-FFB800.svg?style=flat-square)](https://employee-md-site.manus.space)
[![AI Generator](https://img.shields.io/badge/AI_Generator-Try_Now-brightgreen.svg?style=flat-square)](https://employee-md-site.manus.space/generator)

**The Open Standard for AI Agent Employment Contracts**

`employee.md` is a human-readable, machine-parseable YAML specification that defines how AI agents operate—their identity, permissions, responsibilities, constraints, and economics. It serves as the "employment contract" between AI agents and the systems they work within.

> 💡 **Philosophy**: If `AGENTS.md` tells an agent about the codebase, `employee.md` tells the agent about itself.

> 🌐 **Website & AI Generator**: Visit [employee-md-site.manus.space](https://employee-md-site.manus.space) to explore the specification, or use the [AI Generator](https://employee-md-site.manus.space/generator) to create custom employee.md files with dropdowns, toggles, and AI-powered generation.

---

## 📑 Table of Contents

- [Why employee.md?](#why-employeemd)
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Specification](#specification)
- [Examples](#examples)
- [Tooling](#tooling)
- [Integrations](#integrations)
- [Protocol Integrations (x402, A2A, OpenClaw)](#protocol-integrations)
- [Ecosystem](#ecosystem)
- [Contributing](#contributing)
- [License](#license)

---

## 🚀 Why employee.md?

As AI agents become production workforce members, they need standardized contracts that define:

| Feature | Benefit |
|---------|---------|
| **Identity** | Clear agent identification, versioning, and metadata |
| **Mission** | Defined purpose, objectives, and success criteria |
| **Scope** | Explicit boundaries (in_scope/out_of_scope) |
| **Permissions** | Granular access control for data, systems, and tools |
| **Guardrails** | Safety constraints and prohibited actions |
| **Economy** | Budget limits, rates, and payment configuration |
| **Compliance** | Audit trails, frameworks (SOC2, GDPR), and retention |
| **AI Settings** | Model preferences, token limits, and generation params |
| **Integrations** | MCP servers, APIs, webhooks, and protocols |

### Use Cases

- **Development Teams**: Define AI coding assistants with clear scope and guardrails
- **Enterprise Deployments**: Ensure compliance and auditability for AI agents
- **Agent Marketplaces**: Standardize agent capabilities and pricing
- **Multi-Agent Systems**: Enable A2A (Agent-to-Agent) communication with clear contracts

---

## ⚡ Quick Start

### 1. Create your employee.md

```bash
touch employee.md
```

### 2. Add the basic structure

```yaml
---
spec:
  name: employee.md
  version: "2.1.0"
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
# Install the validator
pip install -e .

# Validate your file
employee-validate employee.md

# Or validate with JSON output
employee-validate employee.md --format json
```

---

## 📖 Core Concepts

### Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  employee   │────▶│   Agent      │────▶│   Task      │
│  .md        │     │  Runtime     │     │  Execution  │
└─────────────┘     └──────────────┘     └─────────────┘
      │                    │                    │
      ▼                    ▼                    ▼
 Identity &           Apply            Check against
 Permissions          Guardrails         Scope & Budget
```

### Key Terms

| Term | Description |
|------|-------------|
| **Agent** | An AI system performing work under this contract |
| **Mission** | The high-level purpose guiding agent decisions |
| **Scope** | What the agent should and shouldn't do |
| **Guardrails** | Hard constraints preventing dangerous actions |
| **Economy** | Budget, payment, and cost tracking settings |
| **MCP** | Model Context Protocol for tool integration |
| **A2A** | Agent-to-Agent communication protocol |

### Lifecycle

1. **Load**: The runtime reads and parses `employee.md`
2. **Validate**: Schema validation ensures correctness
3. **Configure**: Identity, permissions, and guardrails are applied
4. **Execute**: Tasks are validated against scope and constraints
5. **Monitor**: Performance and compliance are tracked

---

## 📋 Specification

### Required Fields

| Section | Required Fields | Description |
|---------|-----------------|-------------|
| `spec` | `name`, `version`, `kind` | Specification metadata |
| `role` | `title`, `level` | Job role and seniority |
| `lifecycle` | `status` | Current agent status |

### Complete Structure

```yaml
spec:              # Specification metadata
  name: employee.md
  version: "2.1.0"
  kind: agent-employment
  status: stable
  schema: "https://..."

identity:          # Agent identification
  agent_id: string
  display_name: string
  version: string
  wallet: string
  tags: []

role:              # Job definition (REQUIRED)
  title: string
  level: junior | mid | senior | lead
  department: string
  capabilities: []
  skills: []
  certifications: []

mission:           # Purpose and objectives
  purpose: string
  constitution: url
  objectives: []
  success_criteria: []
  non_goals: []

context:           # Operational environment
  project: string
  repo: url
  environment: dev | staging | prod
  team: string
  organization: string

scope:             # Boundaries
  in_scope: []
  out_of_scope: []
  dependencies: []
  constraints: []

permissions:       # Access control
  data_access: []
  system_access: []
  network_access: []
  tool_access: []
  admin_permissions: boolean

guardrails:        # Safety constraints
  prohibited_actions: []
  required_approval: []
  confidence_threshold: 0.0-1.0
  max_spend_per_task: number
  max_execution_time: seconds

economy:           # Budget and payment
  rate: number
  currency: USD | EUR | BTC | ETH | ENERGY
  budget_limit: number
  payment_method: x402 | crypto | fiat | none | joulework
  billing_schedule: weekly | monthly | milestone | real_time

verification:      # Quality gates
  required_checks: []
  evidence: []
  review_policy: string
  auto_merge: boolean
  min_approvals: number

ai_settings:       # Model configuration
  model_preference: string
  fallback_models: []
  temperature: 0.0-1.0
  tools_enabled: []
  memory_settings: {}
  reasoning_effort: low | medium | high

integration:       # External connections
  mcp_servers: []
  apis: []
  webhooks: []
  services: []

protocols:         # Communication protocols
  a2a: {}
  x402: {}
  human_review: {}
  delegation: {}

compliance:        # Regulatory compliance
  frameworks: []
  data_classification: public | confidential | restricted
  audit_required: boolean
  audit_retention_days: number

performance:       # Metrics and targets
  efficiency_score: 0.0-1.0
  metrics: []
  kpis: []
  slas: []

communication:     # Contact and availability
  channels: []
  timezone: string
  availability: string
  response_time_sla: string

custom_fields: {}  # Extensions
```

See the [full example](employee.md) for a complete reference implementation.

---

## 📚 Examples

| Example | Description | File |
|---------|-------------|------|
| **Minimal** | Smallest valid spec | [examples/minimal.md](examples/minimal.md) |
| **Senior Dev** | Full developer config | [examples/senior-dev.md](examples/senior-dev.md) |
| **AI Assistant** | General-purpose assistant | [examples/ai-assistant.md](examples/ai-assistant.md) |
| **Security** | Compliance-focused auditor | [examples/security-auditor.md](examples/security-auditor.md) |
| **Data Analyst** | Analytics specialist | [examples/data-analyst.md](examples/data-analyst.md) |
| **Freelancer** | Contract worker | [examples/freelancer.md](examples/freelancer.md) |

---

## 🛠️ Tooling

### Installation

```bash
# From source
git clone https://github.com/NosytLabs/employee-md.git
cd employee-md
pip install -e .

# With dev dependencies
pip install -e ".[dev]"
```

### CLI Usage

```bash
# Validate a file
employee-validate employee.md

# Validate multiple files
employee-validate examples/*.md

# JSON output
employee-validate employee.md --format json

# Compact output for CI/CD
employee-validate employee.md --format compact

# With metrics
employee-validate employee.md --metrics prometheus

# Parallel validation
employee-validate examples/*.md --parallel

# Production mode (sanitized errors)
employee-validate employee.md --production
```

### Python API

```python
from tooling import validate_file

result = validate_file("employee.md")

if result.is_valid:
    print("✅ Valid!")
else:
    for error in result.errors:
        print(f"❌ {error.field}: {error.message}")
```

### JSON Schema

The schema is available at [tooling/schema.json](tooling/schema.json). For VS Code integration:

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/NosytLabs/employee-md/main/tooling/schema.json": "employee.md"
  }
}
```

---

## 🔗 Integrations

### Related Standards

| Standard | Purpose | Integration |
|----------|---------|-------------|
| [AGENTS.md](https://agents.md) | Codebase instructions | Use together for context |
| [MCP](https://modelcontextprotocol.io/) | Tool integration | Define in `integration.mcp_servers` |
| [SOUL.md](https://github.com/NosytLabs/soul-md) | Ethics & values | Link in `mission.constitution` |
| [x402](https://x402.org) | HTTP-native agent payments | Define in `economy.payment_method` |
| [A2A](https://google.github.io/A2A/) | Agent-to-agent protocol | Define in `protocols.a2a` |
| [OpenClaw](https://openclaw.ai) | Always-on personal agents | Define in `integration.openclaw` |

### MCP Server Example

```yaml
integration:
  mcp_servers:
    - name: "code-search"
      endpoint: "http://localhost:8080"
      capabilities:
        - "semantic_search"
        - "code_navigation"

    - name: "documentation"
      endpoint: "http://localhost:8081"
      capabilities:
        - "doc_retrieval"
        - "faq_lookup"
```

### LangChain Integration

```python
from langchain_openai import ChatOpenAI
import yaml

# Load employee config
with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

# Configure LLM based on agent settings
llm = ChatOpenAI(
    model=config['ai_settings']['model_preference'],
    temperature=config['ai_settings']['generation_params']['temperature']
)
```

See [INTEGRATION.md](INTEGRATION.md) for detailed integration guides.

---

## 🔌 Protocol Integrations

### x402 — HTTP-Native Agent Payments

The [x402 protocol](https://x402.org) enables AI agents to pay for resources using stablecoins (USDC) directly via HTTP. When an agent requests a paid resource, the server responds with HTTP 402 Payment Required. The agent automatically pays and receives the data.

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

### A2A — Agent-to-Agent Protocol

[Google's A2A protocol](https://google.github.io/A2A/) enables agents to discover, authenticate, and coordinate with each other. employee.md defines the A2A configuration for your agents.

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

### OpenClaw — Always-On Personal Agents

[OpenClaw](https://openclaw.ai) agents are always-on autonomous systems managing email, calendar, browsing, and more. employee.md provides the governance layer.

```yaml
integration:
  openclaw:
    enabled: true
    channels:
      - whatsapp
      - telegram
      - slack
    capabilities:
      - email_management
      - calendar_scheduling
      - web_browsing
    heartbeat:
      interval: 60
      timeout: 300
```

---

## 🌐 Ecosystem

### Tools & Implementations

| Project | Description | Link |
|---------|-------------|------|
| **employee-md-validator** | Official Python validator | This repo |
| **employee-md-site** | Interactive website & AI Generator | [employee-md-site.manus.space](https://employee-md-site.manus.space) |
| **VS Code Extension** | Schema validation and autocomplete | Coming soon |
| **OpenClaw Gateway** | MCP server gateway | [openclaw.ai](https://openclaw.ai) |
| **x402 Protocol** | HTTP-native agent payments | [x402.org](https://x402.org) |
| **A2A Protocol** | Agent-to-agent coordination | [Google A2A](https://google.github.io/A2A/) |

### Community

- 💬 [Discussions](https://github.com/NosytLabs/employee-md/discussions)
- 🐛 [Issues](https://github.com/NosytLabs/employee-md/issues)
- 📖 [Wiki](https://github.com/NosytLabs/employee-md/wiki)

---

## ✅ Best Practices

### Security First

```yaml
guardrails:
  prohibited_actions:
    - "delete_production_data"
    - "modify_security_settings"
    - "access_unauthorized_data"
    - "disable_audit_logging"
  confidence_threshold: 0.9
  max_spend_per_task: 100

compliance:
  audit_required: true
  frameworks:
    - "SOC2"
    - "GDPR"
  encryption_required: true
```

### Production Checklist

- [ ] Set `lifecycle.status` to `active`
- [ ] Define clear `scope.in_scope` and `scope.out_of_scope`
- [ ] Configure `guardrails.confidence_threshold` ≥ 0.8
- [ ] Set `economy.budget_limit` appropriate for workload
- [ ] Enable `compliance.audit_required`
- [ ] Link a `mission.constitution` for ethical alignment
- [ ] Define `verification.required_checks`
- [ ] Set up `communication.channels` for notifications
- [ ] Configure `integration.mcp_servers` for tools

### CI/CD Integration

```yaml
# .github/workflows/employee-md.yml
name: Validate employee.md
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install employee-md
      - run: employee-validate employee.md --format compact
```

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
See [AGENTS.md](AGENTS.md) for AI agent-specific instructions.

```bash
# Development setup
git clone https://github.com/NosytLabs/employee-md.git
cd employee-md
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Validate examples
employee-validate examples/*.md

# Run linting
ruff check tooling/
ruff format tooling/

# Type checking
mypy tooling/ --ignore-missing-imports
```

---

## 📄 License

MIT © [Nosyt Labs](https://nosytlabs.com)

---

**Made with ❤️ for the Agentic Workforce**

[![Star History](https://api.star-history.com/svg?repos=NosytLabs/employee-md&type=Date)](https://star-history.com/#NosytLabs/employee-md&Date)
