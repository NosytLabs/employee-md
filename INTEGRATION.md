# Integration Guide

Integrate **employee.md** with your AI agent systems, including LangChain, AutoGen, and custom Python/TypeScript runtimes.

`employee.md` is part of the open Agentic Web ecosystem, designed to work alongside:
*   **[AGENTS.md](https://agents.md)**: For repository-level context.
*   **[MCP](https://modelcontextprotocol.io/)**: For connecting tools and data.
*   **[SOUL.md](https://github.com/NosytLabs/soul-md)**: For defining agent personality.

---

## Python Integration

### Using PyYAML

The simplest way to parse `employee.md`.

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

### Using Pydantic (Recommended)

Type-safe validation for robust agents.

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
import yaml

class Level(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"

class Employee(BaseModel):
    spec: Optional[Dict[str, Any]] = None
    identity: Optional[Dict[str, Any]] = None
    role: Dict[str, Any]
    lifecycle: Dict[str, Any]
    # ... add other fields as needed

# Load and validate
with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)
    employee = Employee(**config)

print(f"Validated Agent: {employee.role['title']}")
```

---

## TypeScript Integration

### Using js-yaml

```typescript
import yaml from 'js-yaml';
import * as fs from 'fs';

interface Employee {
  role: {
    title: string;
    level: 'junior' | 'mid' | 'senior' | 'lead';
  };
  // ... other interfaces
}

const file = fs.readFileSync('employee.md', 'utf8');
const config = yaml.load(file) as Employee;

console.log(`Agent Role: ${config.role.title}`);
```

### Using Zod

Runtime validation for TypeScript agents.

```typescript
import { z } from 'zod';
import yaml from 'js-yaml';
import * as fs from 'fs';

const EmployeeSchema = z.object({
  role: z.object({
    title: z.string(),
    level: z.enum(['junior', 'mid', 'senior', 'lead']),
  }),
  // ... complete schema
});

const file = fs.readFileSync('employee.md', 'utf8');
const config = yaml.load(file);
const employee = EmployeeSchema.parse(config);

console.log(employee.role.title);
```

---

## AI Framework Integration

### LangChain

Inject `employee.md` context into your system prompt.

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
import yaml

# Load employee config
with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

# Create system prompt with context injection
system_prompt = f"""
You are a {config['role']['title']} at level {config['role']['level']}.
Your Mission: {config['mission']['purpose']}

Capabilities:
{', '.join(config['role'].get('capabilities', []))}

GUARDRAILS (STRICTLY ENFORCED):
- Do not: {', '.join(config['guardrails'].get('prohibited_actions', []))}
- Require approval for: {', '.join(config['guardrails'].get('required_approval', []))}
"""

# Create agent
llm = ChatOpenAI(
    model=config['ai_settings'].get('model_preference', 'gpt-4'),
    temperature=config['ai_settings'].get('generation_params', {}).get('temperature', 0.7)
)
```

### AutoGen

Configure an AutoGen assistant using `employee.md`.

```python
import autogen
import yaml

with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

assistant = autogen.AssistantAgent(
    name=config['identity']['agent_id'],
    system_message=f"""
    You are a {config['role']['title']} ({config['role']['level']}).
    Capabilities: {', '.join(config['role'].get('capabilities', []))}
    """,
    llm_config={
        "config_list": [
            {
                "model": config['ai_settings'].get('model_preference', 'gpt-4'),
                "api_key": "your-api-key"
            }
        ],
        "temperature": config['ai_settings'].get('generation_params', {}).get('temperature', 0.7)
    }
)
```

---

## Protocol Integration

### A2A (Agent-to-Agent) Protocol

Enable agents to discover and communicate with each other.

```python
if config['protocols']['a2a']['enabled']:
    message = {
        "from": config['identity']['agent_id'],
        "to": "target-agent-id",
        "timestamp": datetime.utcnow().isoformat(),
        "payload": { "task": "process_data" }
    }
    # Send via your transport layer (HTTP, WebSocket, P2P)
```

### x402 Payment Protocol

Handle crypto payments for agent services.

```python
if config['protocols']['x402']['enabled']:
    # Example using Web3.py
    transaction = {
        'to': config['identity']['wallet'],
        'value': w3.to_wei(config['economy']['rate'], 'ether'),
        # ... standard transaction fields
    }
```

### MCP (Model Context Protocol)

Connect to external data and tools dynamically.

```python
# Pseudo-code for MCP connection
for server in config['integration'].get('mcp_servers', []):
    mcp_client.connect(server['endpoint'])
    print(f"Connected to MCP Server: {server['name']}")
```

---

## Validation Tools

Always validate your `employee.md` before deploying.

```bash
# Install validator
pip install pyyaml jsonschema

# Run validation
python tooling/validate.py employee.md
```
