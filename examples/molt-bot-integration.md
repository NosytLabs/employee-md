# Molt.bot Integration Guide

[Molt.bot](https://github.com/moltbot/moltbot) is a powerful, local-first AI assistant. `employee.md` is the perfect companion to define your Molt.bot's "Employment Contract".

---

## 🦞 Why use employee.md with Molt.bot?

Molt.bot already uses `SOUL.md` for personality and `AGENTS.md` for repo instructions. `employee.md` adds the missing layer: **Operational Constraints & Economy**.

*   **SOUL.md**: "Who am I?" (Personality, Ethics)
*   **AGENTS.md**: "How do I build this code?" (Tech stack, commands)
*   **employee.md**: "What is my job?" (Role, Salary, Permissions, Guardrails)

---

## 🚀 Setup Instructions

### 1. Place the file
Put `employee.md` in the root of your Molt.bot workspace (where your `AGENTS.md` lives).

```text
my-agent-workspace/
├── AGENTS.md
├── SOUL.md
├── employee.md   <-- HERE
└── ...
```

### 2. Link it in AGENTS.md
Tell Molt.bot to respect the contract by adding this to your `AGENTS.md`:

```markdown
# Operational Contract
This agent operates under the strict guidelines defined in `employee.md`.
You MUST read `employee.md` before taking any action to understand your:
- Permissions (what you can access)
- Guardrails (what is forbidden)
- Budget (economy limits)
- Role (your job title and level)
```

### 3. (Optional) Create a Molt Skill
You can create a custom skill to allow the agent to "check its contract".

Create `skills/check-contract/SKILL.md`:

```markdown
---
name: check-contract
description: Read the employee.md contract to verify permissions and budget.
---

When the user asks about budget, permissions, or role scope:
1. Read the `employee.md` file.
2. Verify if the requested action is `in_scope`.
3. Check if `budget_limit` allows the action.
4. Report back to the user.
```

---

## 📝 Example Configuration for Molt.bot

Here is a `employee.md` tailored for a Molt.bot instance running as a personal assistant:

```yaml
---
spec:
  name: employee.md
  version: "1.0"
  kind: agent-employment

identity:
  agent_id: "molt-personal-01"
  version: "1.0.0"

role:
  title: "Personal Executive Assistant"
  level: "senior"
  capabilities:
    - "calendar_management"
    - "email_triage"
    - "research"

mission:
  purpose: "Optimize the user's time and attention."
  constitution: "SOUL.md" # Links directly to Molt's Soul file

context:
  environment: "local-mac-mini"
  team: "Personal"

permissions:
  data_access:
    - "calendar"
    - "email"
    - "notes"
  tool_access:
    - "browser"
    - "terminal"

guardrails:
  prohibited_actions:
    - "Delete files without confirmation"
    - "Send emails without draft approval"
    - "Buy items over $50 without auth"
  confidence_threshold: 0.9

economy:
  budget_limit: 100 # $100/month API spend limit
  currency: "USD"

integration:
  mcp_servers:
    - name: "filesystem"
      endpoint: "stdio"
    - name: "brave-search"
      endpoint: "stdio"
---
```
