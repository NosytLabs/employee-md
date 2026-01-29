# Integration Guide

Integrate employee.md with your AI agent systems.

---

## Python Integration

### Using PyYAML

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

### Using Pydantic

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class Level(str, Enum):
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"

class Status(str, Enum):
    ONBOARDING = "onboarding"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"

class Employee(BaseModel):
    spec: Optional[Dict[str, Any]] = None
    identity: Optional[Dict[str, Any]] = None
    role: Dict[str, Any]
    lifecycle: Dict[str, Any]

# Load and validate
with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)
    employee = Employee(**config)

print(employee.role['title'])
```

---

## TypeScript Integration

### Using js-yaml

```typescript
import yaml from 'js-yaml';
import * as fs from 'fs';

interface Employee {
  spec?: {
    name?: string;
    version?: string;
    kind?: string;
    status?: 'draft' | 'stable' | 'deprecated';
    schema?: string;
    license?: string;
    homepage?: string;
  };
  identity?: {
    agent_id?: string;
    version?: string;
    wallet?: string;
    created_at?: string;
  };
  role: {
    title: string;
    level: 'junior' | 'mid' | 'senior' | 'lead';
    department?: string;
  };
  lifecycle: {
    status: 'onboarding' | 'active' | 'suspended' | 'terminated';
  };
}

const file = fs.readFileSync('employee.md', 'utf8');
const config = yaml.load(file) as Employee;

console.log(`Agent ${config.identity?.agent_id} is ${config.role.title}`);
```

### Using Zod

```typescript
import { z } from 'zod';
import yaml from 'js-yaml';
import * as fs from 'fs';

const EmployeeSchema = z.object({
  spec: z.object({
    name: z.string(),
    version: z.string(),
    kind: z.string(),
    status: z.enum(['draft', 'stable', 'deprecated']).optional(),
    schema: z.string().url().optional(),
    license: z.string().optional(),
    homepage: z.string().url().optional(),
  }).optional(),
  identity: z.object({
    agent_id: z.string(),
    version: z.string(),
    wallet: z.string().regex(/^0x[a-fA-F0-9]{40}$/),
  }).optional(),
  role: z.object({
    title: z.string(),
    level: z.enum(['junior', 'mid', 'senior', 'lead']),
    department: z.string().optional(),
  }),
  lifecycle: z.object({
    status: z.enum(['onboarding', 'active', 'suspended', 'terminated']),
  }),
});

const file = fs.readFileSync('employee.md', 'utf8');
const config = yaml.load(file);
const employee = EmployeeSchema.parse(config);

console.log(employee.role.title);
```

---

## Validation

### Using Python Validator

```bash
# Install dependencies
pip install pyyaml

# Run validation
python tooling/validate.py employee.md

# Validate examples
python tooling/validate.py examples/ai-assistant.md
python tooling/validate.py examples/data-analyst.md
python tooling/validate.py examples/security-auditor.md
```

### Using JSON Schema

```python
import json
from jsonschema import validate, ValidationError
import yaml

with open('tooling/schema.json', 'r') as f:
    schema = json.load(f)

with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

try:
    validate(instance=config, schema=schema)
    print("✓ Valid!")
except ValidationError as e:
    print(f"✗ Invalid: {e.message}")
```

---

## Custom Fields

### Extending with Custom Data

```yaml
---
custom_fields:
  department_code: "ENG-001"
  manager_id: "manager-001"
  team_size: 12
  on_call_rotation: true
  preferred_tools:
    - "VS Code"
    - "Docker"
    - "Kubernetes"
---
```

### Accessing Custom Fields in Python

```python
import yaml

with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

custom = config.get('custom_fields', {})
department_code = custom.get('department_code')
on_call = custom.get('on_call_rotation', False)

print(f"Department: {department_code}, On Call: {on_call}")
```

---

## AI Agent Integration

### LangChain Integration

```python
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
import yaml

# Load employee config
with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

# Create system prompt
system_prompt = f"""
You are a {config['role']['title']} at level {config['role']['level']}.
Your role is: {config['role']['title']}
Your capabilities are: {', '.join(config['role'].get('capabilities', []))}

Guardrails:
- Do not: {', '.join(config['guardrails'].get('prohibited_actions', []))}
- Require approval for: {', '.join(config['guardrails'].get('required_approval', []))}
"""

# Create agent
llm = ChatOpenAI(
    model=config['ai_settings'].get('model_preference', 'gpt-4'),
    temperature=config['ai_settings'].get('generation_params', {}).get('temperature', 0.7)
)

agent = create_openai_functions_agent(llm, tools, system_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

### AutoGen Integration

```python
import autogen
import yaml

# Load employee config
with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

# Create agent
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

```python
import json
import yaml
from datetime import datetime

# Load employee config
with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

# Check if A2A is enabled
if config['protocols']['a2a']['enabled']:
    # Send message to another agent
    message = {
        "from": config['identity']['agent_id'],
        "to": "target-agent-id",
        "timestamp": datetime.utcnow().isoformat(),
        "payload": {
            "task": "process_data",
            "params": {"data_id": "123"}
        }
    }

    if config['protocols']['a2a']['encryption']:
        # Encrypt message
        encrypted = encrypt_message(message)
    else:
        encrypted = message

    # Send message (implementation depends on your transport)
    send_message(encrypted, config['protocols']['a2a']['message_format'])
```

### x402 Payment Protocol

```python
import yaml
from web3 import Web3

# Load employee config
with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

# Check if x402 is enabled
if config['protocols']['x402']['enabled']:
    # Initialize Web3
    w3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR-KEY'))

    # Create transaction
    transaction = {
        'to': config['identity']['wallet'],
        'from': config['protocols']['x402']['wallet_address'],
        'value': w3.to_wei(config['economy']['rate'], 'ether'),
        'gas': 21000,
        'gasPrice': w3.to_wei('20', 'gwei'),
        'nonce': w3.eth.get_transaction_count(config['protocols']['x402']['wallet_address'])
    }

    # Send transaction
    tx_hash = w3.eth.send_transaction(transaction)
    print(f"Payment sent: {tx_hash.hex()}")
```

---

## MCP Server Integration

```python
import yaml
import json

# Load employee config
with open('employee.md', 'r') as f:
    config = yaml.safe_load(f)

# Connect to MCP servers
for mcp_server in config['integration'].get('mcp_servers', []):
    # Connect to MCP server
    client = connect_to_mcp(mcp_server['endpoint'])

    # Query capabilities
    capabilities = mcp_server.get('capabilities', [])
    for capability in capabilities:
        result = client.query(capability)
        print(f"{mcp_server['name']}.{capability}: {result}")
```

---

## Error Handling

```python
import yaml
import sys

try:
    with open('employee.md', 'r') as f:
        config = yaml.safe_load(f)

    # Validate required fields
    if 'role' not in config:
        raise ValueError("Missing required section: 'role'")
    if 'title' not in config['role']:
        raise ValueError("Missing required field: 'role.title'")

    print("✓ Config loaded successfully")

except FileNotFoundError:
    print("✗ File not found: employee.md")
    sys.exit(1)
except yaml.YAMLError as e:
    print(f"✗ YAML parsing error: {e}")
    sys.exit(1)
except ValueError as e:
    print(f"✗ Validation error: {e}")
    sys.exit(1)
```

---

## Best Practices

### 1. Always Validate
- Use the provided validator before loading
- Check required fields
- Validate data types

### 2. Handle Errors Gracefully
- Catch YAML parsing errors
- Handle missing optional fields
- Provide clear error messages

### 3. Use Type Hints
- TypeScript: Use interfaces
- Python: Use Pydantic or type hints

### 4. Cache Config
- Load config once at startup
- Avoid repeated file I/O
- Reload on config changes

### 5. Use Custom Fields
- Store app-specific data
- Keep standard fields intact
- Document custom field usage
