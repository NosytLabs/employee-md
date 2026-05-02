# employee.md vs Other Agentic Standards

A factual, side-by-side comparison of `employee.md` against the other
markdown-based standards that are starting to converge around AI agents.
Everything here links to a real, live source — no vapor.

| Standard | Maintainer | Live source | What it answers |
|----------|------------|-------------|-----------------|
| **[AGENTS.md](https://agents.md/)** | OpenAI + community | <https://agents.md/> · [GitHub](https://github.com/openai/agents.md) | "How do I work in **this codebase**?" — build, test, and contribution instructions for coding agents. |
| **[worker.md](https://worker.md/)** | worker.md project | <https://worker.md/> | "What **task** should this worker run?" — declarative task/worker definitions for autonomous workers. |
| **[SOUL.md](https://soul.md/)** | SOUL.md project | <https://soul.md/> | "**Who** is this agent?" — personality, ethics, voice, and values. |
| **[SKILL.md](https://agentskills.io/)** | Anthropic Claude Skills + community | <https://agentskills.io/> · [Docs](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) | "What **discrete capability** does this agent have?" — a single, packaged skill with metadata + scripts + resources. |
| **employee.md** | [NosytLabs](https://github.com/NosytLabs/employee-md) | This repo | "What is this agent's **job**?" — role, scope, permissions, guardrails, economy, compliance, and lifecycle. |

> Short version: `AGENTS.md` describes a **repo**, `SKILL.md` describes a
> **capability**, `SOUL.md` describes a **personality**, `worker.md` describes
> a **task**, and `employee.md` describes the **employment contract** that
> binds them together.

---

## Feature matrix

| Capability | AGENTS.md | worker.md | SOUL.md | SKILL.md | **employee.md** |
|------------|:---------:|:---------:|:-------:|:--------:|:---------------:|
| Identity & versioning | partial | yes | yes | yes | **yes** |
| Job role & seniority | no | partial | no | no | **yes** |
| Mission, objectives, non-goals | no | no | partial | no | **yes** |
| Explicit `in_scope` / `out_of_scope` | no | partial | no | partial | **yes** |
| Granular permissions (data / system / network / tool) | no | no | no | partial | **yes** |
| Hard guardrails (`prohibited_actions`, `required_approval`) | no | no | partial | no | **yes** |
| Budget & economy (rate, currency, billing) | no | no | no | no | **yes** |
| Verification gates (reviews, evidence, approvals) | no | no | no | no | **yes** |
| Compliance frameworks (SOC2, GDPR, retention, PII) | no | no | no | no | **yes** |
| AI model settings (model, temperature, tools) | no | partial | no | no | **yes** |
| Lifecycle status (`onboarding`, `active`, `terminated`) | no | partial | no | no | **yes** |
| Codebase build/test instructions | **yes** | no | no | no | no |
| Personality / voice / values | no | no | **yes** | no | partial (via `mission.constitution`) |
| Single packaged capability + scripts | no | no | no | **yes** | no |
| Task/worker dispatch payload | no | **yes** | no | no | partial (via `delegation`) |
| Strict JSON Schema | partial | partial | no | partial | **yes** ([`tooling/schema.json`](../tooling/schema.json)) |
| Reference validator | community | partial | no | community | **yes** (this repo) |

"partial" means the standard touches the area but does not define it as a
first-class, validated section.

---

## How they compose

The standards are designed to layer, not compete. A real agent deployment
typically uses several of them at once:

```text
┌─────────────────────────────────────────────────────────┐
│  SOUL.md       — Who am I? (personality, ethics)        │
│  AGENTS.md     — How do I work in THIS repo?            │
│  SKILL.md(s)   — What discrete capabilities do I have?  │
│  worker.md     — What task am I being asked to run?     │
│  employee.md   — What is my JOB? (role, scope,          │
│                  permissions, guardrails, budget,       │
│                  compliance, lifecycle)                 │
└─────────────────────────────────────────────────────────┘
```

`employee.md` is explicit about this. The relevant cross-links are first-class
fields in the spec:

```yaml
mission:
  # Point at a SOUL.md (or any constitution document)
  constitution: "https://github.com/NosytLabs/soul-md/blob/main/PRINCIPLES.md"

context:
  # Point at the repo whose AGENTS.md governs build/test rules
  repo: "https://github.com/NosytLabs/employee-md"

integration:
  # Tools/skills exposed via Model Context Protocol servers
  mcp_servers:
    - name: "filesystem"
      endpoint: "stdio"
      capabilities: ["read_file", "write_file"]
```

---

## When to pick which

| You want to … | Use |
|---|---|
| Tell a coding agent how to build/test/lint your repo | **AGENTS.md** |
| Define a single reusable capability (with code + metadata) | **SKILL.md** |
| Define an agent's voice, ethics, and persona | **SOUL.md** |
| Describe a task to be picked up by a worker pool | **worker.md** |
| Define **what an agent is allowed to do for you, under what budget, with what guardrails, and how its work is verified** | **employee.md** |

If your agent is going to take meaningful actions on real systems — touch
production data, spend money, make API calls, talk to humans — `employee.md`
is the layer where the operational contract lives.

---

## Source links

- AGENTS.md — <https://agents.md/> · [openai/agents.md on GitHub](https://github.com/openai/agents.md)
- worker.md — <https://worker.md/>
- SOUL.md — <https://soul.md/>
- SKILL.md / Agent Skills — <https://agentskills.io/> · [Anthropic docs](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
- employee.md — this repository

If any of these links go stale or a maintainer moves a project, please
[open an issue](https://github.com/NosytLabs/employee-md/issues) so this
comparison stays accurate.
