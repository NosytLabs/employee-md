# Integration Guide

Integrate **employee.md** with your AI agent systems, including LangChain, AutoGen, CrewAI, and custom Python/TypeScript runtimes.

`employee.md` is part of the open Agentic Web ecosystem, designed to work alongside:

- **[AGENTS.md](https://agents.md)**: For repository-level context and codebase instructions
- **[MCP](https://modelcontextprotocol.io/)**: For connecting tools and data sources
- **[SOUL.md](https://github.com/NosytLabs/soul-md)**: For defining agent personality and values

---

## 📚 Table of Contents

- [Python Integration](#python-integration)
- [TypeScript Integration](#typescript-integration)
- [AI Framework Integration](#ai-framework-integration)
- [MCP Integration](#mcp-integration)
- [Protocol Integration](#protocol-integration)
- [Experimental / Planned Integrations](#experimental--planned-integrations)
- [Validation Tools](#validation-tools)

---

## Python Integration

### Basic PyYAML Parsing

The simplest way to parse `employee.md`:

```python
import yaml

with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

# Access fields
agent_id = config['identity']['agent_id']
role_title = config['role']['title']
status = config['lifecycle']['status']

print(f"Agent {agent_id} is a {role_title} with status {status}")
```

### Pydantic Validation (Recommended)

Type-safe validation for robust agents:

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from enum import Enum
import yaml

class Level(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"

class Role(BaseModel):
    title: str
    level: Level
    department: Optional[str] = None
    capabilities: List[str] = []

class Identity(BaseModel):
    agent_id: str
    display_name: Optional[str] = None
    version: Optional[str] = None

class Lifecycle(BaseModel):
    status: Literal["onboarding", "active", "suspended", "terminated"]

class Employee(BaseModel):
    spec: Dict[str, Any]
    identity: Optional[Identity] = None
    role: Role
    lifecycle: Lifecycle

# Load and validate
with open('employee.md', 'r') as f:
    data = yaml.safe_load(f)
    employee = Employee(**data)

print(f"Validated Agent: {employee.role.title} ({employee.role.level})")
```

### Advanced Python Integration

```python
import yaml
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class AgentConfig:
    """Typed configuration wrapper for employee.md"""
    agent_id: str
    title: str
    level: str
    purpose: str
    model: str
    temperature: float

    @classmethod
    def from_file(cls, path: str) -> "AgentConfig":
        with open(path, 'r') as f:
            data = yaml.safe_load(f)

        return cls(
            agent_id=data['identity']['agent_id'],
            title=data['role']['title'],
            level=data['role']['level'],
            purpose=data['mission']['purpose'],
            model=data['ai_settings']['model_preference'],
            temperature=data['ai_settings']['generation_params']['temperature']
        )

    def can_access(self, resource: str) -> bool:
        """Check if agent has access to a resource"""
        # Implementation based on permissions
        pass

# Usage
config = AgentConfig.from_file('employee.md')
```

---

## TypeScript Integration

### Using js-yaml

```typescript
import yaml from 'js-yaml';
import * as fs from 'fs';

interface EmployeeConfig {
  identity?: {
    agent_id: string;
    display_name?: string;
  };
  role: {
    title: string;
    level: 'junior' | 'mid' | 'senior' | 'lead';
  };
  mission?: {
    purpose: string;
  };
  lifecycle: {
    status: string;
  };
}

const file = fs.readFileSync('employee.md', 'utf8');
const config = yaml.load(file) as EmployeeConfig;

console.log(`Agent Role: ${config.role.title}`);
```

### Using Zod (Runtime Validation)

```typescript
import { z } from 'zod';
import yaml from 'js-yaml';
import * as fs from 'fs';

const EmployeeSchema = z.object({
  spec: z.object({
    name: z.literal('employee.md'),
    version: z.string(),
    kind: z.literal('agent-employment'),
  }),
  identity: z.object({
    agent_id: z.string(),
    display_name: z.string().optional(),
  }).optional(),
  role: z.object({
    title: z.string(),
    level: z.enum(['junior', 'mid', 'senior', 'lead']),
  }),
  lifecycle: z.object({
    status: z.enum(['onboarding', 'active', 'suspended', 'terminated']),
  }),
});

type EmployeeConfig = z.infer<typeof EmployeeSchema>;

const file = fs.readFileSync('employee.md', 'utf8');
const data = yaml.load(file);
const employee = EmployeeSchema.parse(data);

console.log(employee.role.title);
```

---

## AI Framework Integration

### LangChain

Inject `employee.md` context into your system prompt:

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import yaml

# Load employee config
with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

# Create dynamic system prompt
system_prompt = f"""You are {config['identity'].get('display_name', 'an AI agent')}.

ROLE: {config['role']['title']} ({config['role']['level']})
MISSION: {config['mission']['purpose']}

CAPABILITIES:
{chr(10).join(f"- {cap}" for cap in config['role'].get('capabilities', []))}

GUARDRAILS (STRICTLY ENFORCED):
- NEVER: {', '.join(config['guardrails'].get('prohibited_actions', []))}
- REQUIRE APPROVAL FOR: {', '.join(config['guardrails'].get('required_approval', []))}

SCOPE:
- IN SCOPE: {', '.join(config['scope'].get('in_scope', []))}
- OUT OF SCOPE: {', '.join(config['scope'].get('out_of_scope', []))}

Respond according to your role and mission while respecting all guardrails.
"""

# Create agent with configured settings
llm = ChatOpenAI(
    model=config['ai_settings'].get('model_preference', 'gpt-4'),
    temperature=config['ai_settings'].get('generation_params', {}).get('temperature', 0.7)
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
```

### AutoGen

Configure an AutoGen assistant using `employee.md`:

```python
import autogen
import yaml

with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

# Create assistant agent from config
assistant = autogen.AssistantAgent(
    name=config['identity']['agent_id'],
    system_message=f"""You are a {config['role']['title']} ({config['role']['level']}).

Your mission: {config['mission']['purpose']}

Capabilities: {', '.join(config['role'].get('capabilities', []))}

Constraints:
- Never: {', '.join(config['guardrails'].get('prohibited_actions', []))}
- Confidence threshold: {config['guardrails'].get('confidence_threshold', 0.8)}

Reply TERMINATE when the task is complete.
""",
    llm_config={
        "config_list": [
            {
                "model": config['ai_settings'].get('model_preference', 'gpt-4'),
                "api_key": "your-api-key"
            }
        ],
        "temperature": config['ai_settings'].get('generation_params', {}).get('temperature', 0.7),
    }
)

# Create user proxy agent
user_proxy = autogen.UserProxyAgent(
    name="user",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={"work_dir": "coding"},
)

# Start conversation
user_proxy.initiate_chat(assistant, message="Hello!")
```

### CrewAI

```python
from crewai import Agent, Task, Crew
import yaml

# Load config
with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

# Create agent from employee.md
coding_agent = Agent(
    role=config['role']['title'],
    goal=config['mission']['purpose'],
    backstory=f"A {config['role']['level']} level developer with expertise in {', '.join(config['role'].get('capabilities', []))}",
    verbose=True,
    allow_delegation=config['delegation'].get('sub_delegation', False) if 'delegation' in config else False,
    llm=config['ai_settings'].get('model_preference', 'gpt-4') if 'ai_settings' in config else 'gpt-4'
)

# Create task
task = Task(
    description="Write a Python function to calculate fibonacci numbers",
    agent=coding_agent,
    expected_output="A working Python function with docstring"
)

# Create and run crew
crew = Crew(agents=[coding_agent], tasks=[task])
result = crew.kickoff()
```

---

## MCP Integration

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) enables secure connections between AI agents and external tools/data sources.

### Quick Start with MCP

```yaml
integration:
  mcp_servers:
    - name: "filesystem"
      endpoint: "http://localhost:3000"
      capabilities:
        - "read_file"
        - "write_file"
        - "list_directory"

    - name: "web-search"
      endpoint: "http://localhost:3001"
      capabilities:
        - "search"
        - "fetch_url"
```

### Popular MCP Servers

| Server | Purpose | Capabilities |
|--------|---------|--------------|
| **filesystem** | Local file operations | `read_file`, `write_file`, `list_directory` |
| **web-search** | Internet search | `search`, `fetch_url` |
| **github** | GitHub integration | `read_repo`, `create_pr`, `list_issues` |
| **database** | SQL database access | `query`, `execute`, `transaction` |
| **browser** | Web browsing | `navigate`, `screenshot`, `extract` |
| **code-execution** | Sandbox code execution | `execute_python`, `execute_javascript` |

### MCP Server Examples

#### Vector Database (Semantic Search)

```yaml
integration:
  mcp_servers:
    - name: "vector-db"
      endpoint: "http://localhost:6333"
      capabilities:
        - "vector_search"
        - "embedding_queries"
        - "similarity_search"
```

#### API Gateway

```yaml
integration:
  mcp_servers:
    - name: "api-gateway"
      endpoint: "http://localhost:8080"
      capabilities:
        - "http_requests"
        - "rate_limiting"
        - "circuit_breaker"
```

#### Browser Automation

```yaml
integration:
  mcp_servers:
    - name: "browser-mcp"
      endpoint: "http://localhost:9222"
      capabilities:
        - "web_navigation"
        - "page_extraction"
        - "screenshot_capture"
        - "form_interaction"
```

#### Code Execution (Sandboxed)

```yaml
integration:
  mcp_servers:
    - name: "code-exec-mcp"
      endpoint: "http://localhost:5555"
      capabilities:
        - "python_execution"
        - "javascript_execution"
        - "sandbox_isolation"
        - "resource_monitoring"
```

#### Knowledge Base

```yaml
integration:
  mcp_servers:
    - name: "kb-mcp"
      endpoint: "http://localhost:7373"
      capabilities:
        - "faq_lookup"
        - "best_practices"
        - "knowledge_graph"
        - "document_retrieval"
```

### Production Multi-Server Setup

```yaml
integration:
  mcp_servers:
    # Primary gateway for tool routing
    - name: "mcp-gateway"
      endpoint: "http://localhost:18789"
      capabilities:
        - "tool_routing"
        - "session_memory"
        - "rate_limiting"

    # Semantic search and embeddings
    - name: "vector-db"
      endpoint: "http://localhost:6333"
      capabilities:
        - "vector_search"
        - "embedding_queries"

    # External API management
    - name: "api-gateway"
      endpoint: "http://localhost:8080"
      capabilities:
        - "http_requests"
        - "rate_limiting"
        - "api_key_management"

    # Web research capabilities
    - name: "browser-mcp"
      endpoint: "http://localhost:9222"
      capabilities:
        - "web_navigation"
        - "page_extraction"
        - "screenshot_capture"

    # Secure code execution
    - name: "code-exec-mcp"
      endpoint: "http://localhost:5555"
      capabilities:
        - "python_execution"
        - "sandbox_isolation"

    # Internal documentation
    - name: "docs-mcp"
      endpoint: "http://localhost:8888"
      capabilities:
        - "doc_retrieval"
        - "faq_lookup"
```

### MCP Capabilities Reference

Common capabilities you may encounter:

| Capability | Description | Use Case |
|-----------|-------------|----------|
| `tool_routing` | Route tools dynamically | Load tools from multiple sources |
| `session_memory` | Persistent session context | Remember conversation history |
| `semantic_search` | Vector-based similarity search | Find relevant documents |
| `document_retrieval` | Fetch documents by ID | Retrieve specific documents |
| `vector_search` | Query vector embeddings | Semantic search over embeddings |
| `embedding_queries` | Generate embeddings | Convert text to vectors |
| `http_requests` | Make HTTP requests | Call external APIs |
| `rate_limiting` | Enforce rate limits | Prevent API abuse |
| `circuit_breaker` | Fail-fast protection | Handle service failures |
| `web_navigation` | Browse web pages | Research and scraping |
| `page_extraction` | Extract page content | Get text from HTML |
| `python_execution` | Run Python code | Execute code snippets |
| `sandbox_isolation` | Isolated execution | Secure code execution |
| `sql_queries` | Execute SQL queries | Database operations |
| `transaction_management` | Handle DB transactions | Atomic operations |

---

## Protocol Integration

### A2A (Agent-to-Agent) Protocol

Enable agents to discover and communicate with each other:

```python
import yaml
from datetime import datetime

with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

if config.get('protocols', {}).get('a2a', {}).get('enabled'):
    message = {
        "protocol": "a2a/1.0",
        "from": config['identity']['agent_id'],
        "to": "target-agent-id",
        "timestamp": datetime.utcnow().isoformat(),
        "type": "task_request",
        "payload": {
            "task": "process_data",
            "priority": "high",
            "deadline": "2026-02-15T12:00:00Z"
        }
    }
    # Send via your transport layer (HTTP, WebSocket, P2P)
```

### x402 Payment Protocol

Handle crypto payments for agent services:

```python
from web3 import Web3
import yaml

with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

if config.get('protocols', {}).get('x402', {}).get('enabled'):
    w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_KEY'))

    # Create payment transaction
    transaction = {
        'to': config['identity']['wallet'],
        'value': w3.to_wei(config['economy']['rate'], 'ether'),
        'gas': 2000000,
        'gasPrice': w3.to_wei('50', 'gwei'),
    }
```

### Human Review Workflow

```python
import yaml

with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

human_review = config.get('protocols', {}).get('human_review', {})

if human_review.get('enabled'):
    def request_human_approval(action: str, context: dict):
        """Request human approval for sensitive actions"""
        triggers = human_review.get('review_triggers', [])

        # Check if action matches any trigger
        if any(trigger in action for trigger in triggers):
            # Send notification to escalation contacts
            contacts = human_review.get('escalation_contacts', [])
            timeout = human_review.get('approval_timeout', 86400)

            # Implementation: Send email/Slack notification
            print(f"Approval required from {contacts} for: {action}")
            return wait_for_approval(timeout)
```

---

## Experimental / Planned Integrations

> ⚠️ **Status: experimental / planned / unverified.** The integrations below
> are not part of the stable v1.0.0 contract. The schema accepts them today
> via free-form sections (`integration.openclaw`, `custom_fields.*`) and via
> existing fields like `economy.payment_method: "joulework"`, but no
> first-class validator, reference server, or production runtime ships with
> this repo yet.
>
> When researching v1.0.0 we attempted to verify the upstream projects named
> below against canonical sources (project websites, GitHub, peer-reviewed
> material). For **OpenClaw** and **Hermes**, the search results we got
> back were inconsistent with what a real, live project would look like
> (future-dated commits, implausible star counts, links that didn't resolve
> to a canonical repo). Rather than pretend, we are leaving these here only
> as a **forward-looking design sketch**: if the projects ship a real,
> public spec we can independently confirm, we'll promote them. Until then,
> treat these blocks as illustrative shapes, not real integrations.
> See `docs/RESEARCH_NOTES.md` for the verification methodology.

### OpenClaw — always-on personal agent runtime (UNVERIFIED upstream)

OpenClaw is described in earlier drafts of this repo as a runtime for
always-on autonomous agents (email, calendar, browsing, messaging).
`employee.md` would be a natural fit as the **governance layer** for such a
runtime: it answers "what is this agent allowed to do, with what budget,
under whose review?". The shape below is a placeholder; we could not
independently verify the upstream project for v1.0.0.

The integration is currently a **placeholder shape**. There is no published
`openclaw` namespace in `tooling/schema.json`; today you express it via
`integration.mcp_servers` plus a free-form `integration.openclaw` block:

```yaml
integration:
  # Stable, validated today:
  mcp_servers:
    - name: "openclaw-gateway"
      endpoint: "http://127.0.0.1:18789"
      capabilities:
        - "tool_routing"
        - "session_memory"

  # Experimental — shape may change before being promoted into the schema:
  openclaw:
    enabled: true
    channels: ["whatsapp", "telegram", "slack"]
    capabilities:
      - "email_management"
      - "calendar_scheduling"
      - "web_browsing"
    heartbeat:
      interval: 60      # seconds
      timeout: 300      # seconds
```

What is **not** shipped yet:

- A published OpenClaw reference server in this repo.
- A first-class `openclaw` block in `tooling/schema.json` with strict
  validation.
- A conformance test suite for the heartbeat / channel contract.

If you need a stable surface today, define your OpenClaw gateway as a regular
MCP server under `integration.mcp_servers` and keep any OpenClaw-specific
fields under `custom_fields` until the shape stabilises.

### Hermes — agent-to-agent message transport (UNVERIFIED upstream)

Hermes is a proposed transport layer for `protocols.a2a` messages
(discovery, authentication, delivery). Today the spec validates the **policy**
of A2A — whether it is enabled, the discovery method, the message format, the
encryption requirement — but does not bind to any specific transport
implementation:

```yaml
protocols:
  a2a:
    enabled: true
    discovery_method: "registry"   # or "broadcast"
    message_format: "json"
    encryption: true
    # Planned — not yet validated by the schema:
    # transport: "hermes"
    # hermes:
    #   relay: "https://hermes.example.com"
    #   identity: "did:web:agent.example.com"
```

A future minor release may add a first-class `protocols.a2a.transport` enum
and a `protocols.a2a.hermes` sub-block. Until then, anything Hermes-specific
should live under `custom_fields` to avoid coupling your config to an
unstable surface.

### JouleWork — energy-denominated economy (experimental example)

The `economy` block already accepts `payment_method: "joulework"` and
`currency: "ENERGY"`, and the schema validates them today. See
[`examples/zhc-worker.md`](examples/zhc-worker.md) for a worked example of an
energy-accounted, profit-tracked agent. The semantic meaning of these values
(how a "joule" is metered, how P&L is settled, how `insolvency_policy`
suspends an agent) is **not** standardised by this repo and is left to the
runtime that consumes the contract.

### How to propose promotion

If you are running one of these integrations in production and want it
promoted to a stable, validated section of the schema:

1. Open a [discussion](https://github.com/NosytLabs/employee-md/discussions)
   describing the production shape and at least one reference implementation.
2. File an issue with the proposed JSON Schema patch.
3. Submit a PR that adds the new block to `tooling/schema.json`, updates
   `employee.md`, adds at least one new example under `examples/`, and adds
   the example to **both** the strict `schema-check` whitelist in
   `.github/workflows/validate.yml` and the `validate` and `validate-strict`
   targets in the `Makefile`.

---

## Validation Tools

Always validate your `employee.md` before deploying:

### CLI Validation

```bash
# Install validator
pip install employee-md

# Basic validation
employee-validate employee.md

# Validate with JSON output
employee-validate employee.md --format json

# Validate multiple files
employee-validate examples/*.md

# Production mode (sanitized errors)
employee-validate employee.md --production

# With metrics
employee-validate employee.md --metrics prometheus
```

### Python API

```python
from tooling import validate_file

result = validate_file("employee.md")

if result.is_valid:
    print("✅ Valid configuration")
else:
    print("❌ Validation failed:")
    for error in result.errors:
        print(f"  - {error.field}: {error.message}")
```

### CI/CD Integration

```yaml
# .github/workflows/validate-employee-md.yml
name: Validate employee.md
on:
  push:
    paths:
      - 'employee.md'
      - 'examples/*.md'
  pull_request:
    paths:
      - 'employee.md'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install validator
        run: pip install employee-md

      - name: Validate
        run: employee-validate employee.md --format compact
```

---

## Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [AGENTS.md](https://agents.md)
- [employee.md Schema](tooling/schema.json)
- [Example Configurations](examples/)
