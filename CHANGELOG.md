# Changelog

All notable changes to the **employee.md** specification and tooling are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-05-02 — First stable release

This is the **first stable, public release** of the `employee.md` specification and reference tooling. Earlier in-tree drafts numbered 2.x were development snapshots that were never published to PyPI, never tagged in git, and never advertised — they should be treated as internal pre-1.0 work. To avoid implying a track record we don't have, the spec is being re-baselined at **v1.0.0** here.

### What v1.0.0 actually ships

#### The specification
- A single, schema-validated YAML contract format (`employee.md`) for declaring an AI agent's identity, role, scope, permissions, guardrails, economy, lifecycle, and compliance posture.
- 19 first-class sections, every field individually validated.
- Strict, draft-07 JSON Schema in `tooling/schema.json` — usable by any JSON Schema validator in any language.
- 9 worked example specs in `examples/` covering senior dev, devops, security auditor, data analyst, freelancer, product manager, AI assistant, ZHC worker, plus a minimal starter.
- A new **trading-bot** example (added in this release) showing real-world risk constraints (max position, drawdown, kill switch, allowed symbols).

#### The Python tooling
- `validate-employee` CLI with text and JSON output, exit codes suitable for CI.
- `EmployeeValidationOrchestrator` library API for embedding validation in other Python systems.
- `runtime.Employee` SDK that loads a contract and produces an LLM-ready system prompt, plus `decide()` / `check_action()` helpers for runtime enforcement.
- `employee-runtime` CLI for one-shot decisions (`employee-runtime decide --contract employee.md --action deploy`).
- New: `runtime.skill_export` — converts an `employee.md` contract into Anthropic SKILL.md format (frontmatter + body), so the same contract can be consumed by Claude Skills.
- 271+ pytest tests across unit, integration, and runtime suites; CI runs on Python 3.8 → 3.12.

#### The website
- Server-rendered Flask site (`web/`) with a live validator backed by the same `EmployeeValidationOrchestrator` the CLI uses.
- `/spec` is generated from `tooling/schema.json` so the rendered reference can never drift from the schema.
- `/examples` gallery loads from `examples/` directly — no duplicated source of truth.
- `/why`, `/integrations`, `/runtime`, `/docs` pages with research-grounded content (see `docs/RESEARCH_NOTES.md`).
- New SEO/GEO surfaces: OpenGraph + Twitter cards, JSON-LD `SoftwareSourceCode` schema, `robots.txt`, `sitemap.xml`.

#### Honest scope
- The reference repo is **MIT-licensed** and lives at `github.com/NosytLabs/employee-md`. There is no PyPI package yet — install from source (`pip install -e .`).
- Where the spec carries explicit **`status: experimental`** badges (e.g. some `economy` / `protocols` fields like `wallets`, `internal_token`, `a2a`, `x402`), those fields are reserved for future iteration and not load-bearing in v1.0.0.
- Adoption claims have been removed from marketing copy. v1.0.0 is the day-one release; we'll publish adoption numbers when there's real data to publish.

### Backward compatibility
- This is the first published version. Compatibility is declared as `compatibility: ["1.x"]`.
- Future minor releases (1.1, 1.2, …) will add fields without breaking existing valid contracts.
- Breaking changes will require a 2.0.

### Migration from in-tree drafts
If you used a pre-1.0 draft of this repo:
1. Update `spec.version` to `"1.0.0"` in your contracts.
2. Update `spec.compatibility` to `["1.x"]`.
3. Re-run `validate-employee path/to/your.md` — the schema is unchanged from the latest draft.

### Acknowledgements
- Spec design draws on conventions from [`AGENTS.md`](https://agents.md/) (repo-local agent context), [`worker.md`](https://worker.md/) (bounded execution units), and Anthropic's [SKILL.md](https://docs.anthropic.com/) (skill packaging). See `/why` and `docs/RESEARCH_NOTES.md` for honest comparisons.

---

## Pre-1.0 development history (in-tree only, never published)

Earlier in-repo drafts (mis-numbered 1.0.0 / 2.0.0 / 2.1.0) were never tagged or released. The features they introduced — granular permissions, expanded economy, AI settings, performance metrics, protocols block, parallel validation, schema definitions cleanup — are all part of the v1.0.0 ship list above. The mis-numbered tags have been removed from documentation; treat all prior history as `0.x` development.
