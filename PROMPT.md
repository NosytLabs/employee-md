# Generate Your employee.md

Copy and paste the prompt below into any AI model (Claude, ChatGPT, DeepSeek) to generate a valid `employee.md` file for your agent.

This prompt is optimized to produce a **v2.1.0 compliant** specification that integrates with `AGENTS.md` and other standard protocols.

---

## 📋 The Prompt

```markdown
Act as an expert AI Agent Architect. I need you to generate a valid `employee.md` file (v2.1.0 standard) for a new AI agent.

Here is the context for the agent I want to build:

1. **Role**: [e.g., Senior React Developer, Legal Assistant, meme-lord marketing bot]
2. **Mission**: [e.g., Write bug-free code, draft NDAs, roast crypto scams]
3. **Personality/Soul**: [e.g., Professional, Sarcastic, Helpful but strict]
4. **Constraints**: [e.g., Never deploy on Fridays, Max budget $50/mo, Approval required for tweets]
5. **Tools**: [e.g., GitHub CLI, Slack, Notion, Molt.bot]

Based on this, please generate a complete `employee.md` YAML file. 

Ensure you include:
- `spec` metadata (v2.1.0)
- `identity` and `role` sections
- `mission` with a placeholder link to a soul document if needed
- `guardrails` and `permissions` based on the constraints
- `economy` section (default to x402/crypto if unsure, or standard rates)
- `context` section for the environment
- `integration` section if tools like MCP are needed

Output ONLY the YAML code block.
```

---

## 💡 Next Steps

1.  **Save** the output as `employee.md` in your agent's root directory.
2.  **Validate** it using the provided python tool: `python tooling/validate.py employee.md`.
3.  **Commit** it to your repository alongside your `AGENTS.md`.
4.  **Point** your Agent Runtime (Molt.bot, LangChain, etc.) to this file.
