# Examples

This directory contains reference implementations of `employee.md` for various AI agent personas. Use these templates to jumpstart your agent development.

## 📂 Available Personas

| File | Persona | Key Features Demonstrated |
|------|---------|---------------------------|
| **[minimal.md](minimal.md)** | **Worker** | Minimum valid spec. The "Hello World" of agent employment. |
| **[ai-assistant.md](ai-assistant.md)** | **AI Assistant** | Standard assistant profile with tools, memory settings, and personality. |
| **[senior-dev.md](senior-dev.md)** | **Senior Developer** | Coding capabilities, high permissions, delegation to junior agents, and higher pay rates. |
| **[data-analyst.md](data-analyst.md)** | **Data Analyst** | Database connections, read-only permissions, and specific reporting metrics. |
| **[security-auditor.md](security-auditor.md)** | **Security Auditor** | Compliance-focused (SOC2), high security clearance, restricted tool access. |
| **[freelancer.md](freelancer.md)** | **Freelancer** | Contract-based work, crypto payments (**x402**), and specific deliverable tracking. |
| **[molt-bot-integration.md](molt-bot-integration.md)** | **Molt Integration** | Example of how to integrate with **Molt.bot** workspaces. |

## 🚀 Usage

You can use these examples as direct templates.

### 1. Copy a template
```bash
# Copy the AI Assistant template
cp examples/ai-assistant.md my-agent.md
```

### 2. Customize
Edit the file to match your specific agent's `identity`, `mission`, and `context`.

### 3. Validate
Ensure your customizations didn't break the schema:

```bash
python tooling/validate.py my-agent.md
```
