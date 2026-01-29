# Examples

This directory contains reference implementations of `employee.md` for various AI agent personas.

| File | Persona | Key Features Demonstrated |
|------|---------|---------------------------|
| [minimal.md](minimal.md) | **Worker** | Minimum required fields only. Good starting point. |
| [ai-assistant.md](ai-assistant.md) | **AI Assistant** | Full AI settings, tools, memory, and personality. |
| [data-analyst.md](data-analyst.md) | **Data Analyst** | Database connections, read-only permissions, reporting metrics. |
| [security-auditor.md](security-auditor.md) | **Security Auditor** | Compliance frameworks, high security clearance, restricted tools. |
| [senior-dev.md](senior-dev.md) | **Senior Developer** | Coding capabilities, delegation to junior agents, higher rates. |
| [freelancer.md](freelancer.md) | **Freelancer** | Contract terms, crypto payments (x402), specific deliverables. |

## Usage

You can use these examples as templates for your own agents.

```bash
# Copy an example to start
cp examples/ai-assistant.md my-agent.md

# Validate your new file
python tooling/validate.py my-agent.md
```
