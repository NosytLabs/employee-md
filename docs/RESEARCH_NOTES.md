# Research Notes — v1.0.0

These are the verified primary sources behind the v1.0.0 documentation. Every claim made on
[`/why`](https://nosytlabs.github.io/employee-md/why/) and [`/integrations`](https://nosytlabs.github.io/employee-md/integrations/)
traces back to one of these. Search snippets and search engine "answers" were **not** treated as primary
sources — only canonical docs, peer-reviewed papers, and organisation-published material.

## Verified — used in production copy

### AGENTS.md ecosystem
- [agents.md](https://agents.md/) — canonical spec site. Spec is "Markdown with no required fields"; conventional sections only.
- [developers.openai.com/codex/guides/agents-md](https://developers.openai.com/codex/guides/agents-md) — Codex AGENTS.md guide. Documents the discovery walk (Git root → CWD), `AGENTS.override.md` precedence, and the **`project_doc_max_bytes = 32 KiB`** truncation. Quote: *"compliance is advisory, not mechanically enforced."*
- [github.blog — How to write a great AGENTS.md (lessons from 2,500+ repos)](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/) — empirical analysis of real AGENTS.md files. Recommends keeping files small (~300 lines).
- [infoq.com — Are AGENTS.md files a help or a hindrance? (Aug 2025)](https://www.infoq.com/news/2025/08/agents-md/) — coverage of the ETH Zurich SWE-bench Lite study showing AGENTS.md *reduced* task resolution from 33.5% baseline → 29.6% (developer-written) → 32% (LLM-generated), and increased token cost by >20%.
- Real example AGENTS.md files: [openai/codex](https://raw.githubusercontent.com/openai/codex/main/AGENTS.md), [apache/airflow](https://raw.githubusercontent.com/apache/airflow/main/AGENTS.md).
- Linux Foundation governance handover: Dec 9, 2025; founded the Agentic AI Foundation (AAIF). Anthropic + OpenAI co-donors.

### worker.md ecosystem
- [worker.md/](https://worker.md/) — landing page. Explicitly **"a design pattern and a shared vocabulary"**, not a framework.
- [worker.md/what-is-ai-worker/](https://worker.md/what-is-ai-worker/) — *"Workers are not goal-seeking. They do not decide what to do next."*
- [worker.md/ai-worker-vs-agent/](https://worker.md/ai-worker-vs-agent/) — *"A worker is a bounded executor … An agent is an autonomous loop."*
- [worker.md/worker-protocol/](https://worker.md/worker-protocol/) — verbatim request/response shapes and the 5-state status taxonomy (`ok`, `retryable_error`, `invalid_request`, `invalid_output`, `needs_human`).
- [worker.md/ai-worker-architecture/](https://worker.md/ai-worker-architecture/), [worker.md/ai-worker-design-patterns/](https://worker.md/ai-worker-design-patterns/) — patterns: Validator, Aggregator, Router, Idempotent, Human-in-the-Loop, Supervisor.
- [worker.md/examples/](https://worker.md/examples/) — 8 worker example specs (Email Summarization, Code Review, Data Validation, Web Scrape, Lambda, Queue, Validator, Aggregator).
- [worker.md/registry/](https://worker.md/registry/) — explicitly self-described as a "Prototype" marketplace; no conformance suite.

### Anthropic SKILL.md / Claude Skills
- [platform.claude.com/docs/en/agents-and-tools/agent-skills/overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — canonical Skills docs.
- [platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — name/description validation rules, progressive-disclosure design.
- [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) — `allowed-tools`, `disable-model-invocation` (Claude Code extras).
- [github.com/anthropics/skills](https://github.com/anthropics/skills) — official example skills repo.
- Verified format used in `runtime/skill_export.py`:
  - `name` ≤ 64 chars, lowercase + digits + hyphens, no XML, no reserved words ("anthropic", "claude")
  - `description` ≤ 1024 chars, must say WHAT it does and WHEN to use it
  - Folder layout: `SKILL.md` + `scripts/` + `references/` + `assets/`
  - Progressive disclosure: metadata at session start → body when matched → bundled resources on demand

### CrewAI (used in /integrations recipe)
- [docs.crewai.com/concepts/agents](https://docs.crewai.com/concepts/agents) — `src/<project>/config/agents.yaml` shape with `role`, `goal`, `backstory` required fields and `{topic}` interpolation.

### Trading-bot constraints (used in examples/trading-bot.md)
- [hummingbot.org — kill switch docs](https://hummingbot.org/client/global-configs/kill-switch/) — `kill_switch_mode`, `kill_switch_rate: -5.0`, `total_amount_quote`, `triple_barrier_config{stop_loss, take_profit, time_limit, trailing_stop}`.
- [freqtrade.io — configuration](https://www.freqtrade.io/en/stable/configuration/) — `max_open_trades`, `stake_amount`, `stoploss: -0.10`, `trailing_stop`, `dry_run: true` default; refuses configs where both `max_open_trades` and `stake_amount` are unlimited (raises `OperationalException`).

### Failure-mode evidence (used in /why incident cards)
- AI Incidents Database — **233 AI incidents recorded in 2024 (+56% YoY).**
- Replit / SaaStr postmortem (July 2025) — autonomous coding agent ignored a code freeze, ran `DROP DATABASE` on production, fabricated 4,000 fake user records and false logs.
- Austin fintech expense agent (Sept 2024) — hallucinated $47K of fake vendors when it could not parse faded receipts; reward signal optimised "complete the task," not "be correct."
- $47K multi-agent recursive loop (2024) — Helicone dashboards, Slack alerts at 50/80/95%, and an OpenAI account spend cap **all failed to halt the spend**: alerts ≠ enforcement.
- IBM-cited refund agent — granted out-of-policy refunds; positive review created a reward-hacking gradient.
- Gartner: >40% of agentic-AI projects projected to be cancelled by 2027.

### Peer-reviewed papers (used in /why)
- Boddy, S. & Joseph, J. — **"Regulating the Agency of LLM-based Agents"**, [arXiv:2509.22735](https://arxiv.org/abs/2509.22735) (Sep 2025). Treats agency as a measurable, regulable system property along *preference rigidity*, *independent operation*, and *goal persistence*. Argues for domain-specific agency limits.
- **"Governing LLM Collusion in Multi-Agent Cournot Markets"**, [arXiv:2601.11369](https://arxiv.org/abs/2601.11369) (2025). Empirically shows that *prompt-only "constitutional" prohibitions provide no statistically reliable improvement* under optimization pressure; an external governance layer cuts severe-collusion incidence from 50% → 5.6% (Cohen's d=1.28).
- **"Position: Towards Responsible LLM-empowered Multi-Agent Systems"**, [arXiv:2502.01714](https://arxiv.org/abs/2502.01714) (Feb 2025) — supporting reference on cascading uncertainty.

## Unverified — explicitly NOT cited as if real

### OpenClaw
Search results returned a confident description of `github.com/openclaw/openclaw` with **367k stars**, **75.6k forks**, future-dated commits ("May 2, 2026"), and a "SOUL.md" contract format. None of those numbers or claims are independently verifiable from primary sources.

**Action taken in v1.0.0:** removed all marketing claims that depended on OpenClaw being real. The forward-looking placeholder shape is preserved in [`INTEGRATION.md` → Experimental / Planned](../INTEGRATION.md#experimental--planned-integrations) with an explicit caveat. The `/integrations` page does **not** list OpenClaw.

### HermesAgent
Search results claimed `github.com/NousResearch/hermes-agent` with **129k stars**, "released February 2026," and the same future-dated-commit pattern. Nous Research is a real organisation (Hermes *model* series exists), but a "Hermes Agent" framework with these stats is unverifiable.

**Action taken in v1.0.0:** removed unverified claims. The `/integrations` page does **not** list HermesAgent.

## Methodology

Research was carried out via four independent web-research subagent runs in May 2026, each instructed to:
1. Run multiple parallel searches.
2. Open and quote canonical primary sources (spec sites, GitHub READMEs, peer-reviewed papers).
3. Flag results as **unverified** when search-layer answers contained future-dated commits, implausible star counts, or otherwise self-inconsistent metadata.

The resulting summaries are stored under `.local/research/` for diff-able review. This document is the publishable distillation.
