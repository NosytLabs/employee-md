# employee.md

## Overview

`employee.md` is an open standard and Python validation tooling for AI agent
employment contracts. It defines a human-readable, machine-parseable YAML
specification that describes how AI agents operate — their identity,
permissions, responsibilities, constraints, and economics.

The repo ships:

- The reference spec (`employee.md`) and a JSON Schema (`tooling/schema.json`)
  pinned at **v1.0.0** — the first stable, public release. Earlier in-tree
  drafts numbered 2.x were never tagged or published; CHANGELOG.md tells the
  honest version-history story.
- A permissive Python validator + CLI (`tooling/`) with caching, monitoring,
  and parallel validation.
- A reference **runtime SDK** (`runtime/`) that turns a validated contract
  into an LLM-ready system prompt + guardrail checker + budget tracker, plus
  a **SKILL.md exporter** (`runtime/skill_export.py`) that converts a contract
  to Anthropic Claude Skills format.
- Ten official example specs under `examples/` (including the
  `trading-bot.md` worked example with Hummingbot/Freqtrade-style risk caps)
  plus one markdown integration guide (`molt-bot-integration.md`).
- A research-grounded marketing site under `web/` with a `/why` page that
  cites the verified primary sources behind every claim
  (`docs/RESEARCH_NOTES.md`), and an `/integrations` page that lists only
  recipes we built and tested.

## Project Structure

```
.
├── employee.md                 # Reference v1.0.0 spec
├── PROMPT.md                   # Prompt for generating valid employee.md files
├── examples/                   # Official example specs (all schema-strict)
│   ├── minimal.md
│   ├── senior-dev.md
│   ├── ai-assistant.md
│   ├── security-auditor.md
│   ├── data-analyst.md
│   ├── freelancer.md
│   ├── devops-engineer.md
│   ├── product-manager.md
│   ├── zhc-worker.md           # Experimental JouleWork / always-on agent example
│   ├── trading-bot.md          # NEW: spot-only mean-reversion bot with kill-switch
│   └── molt-bot-integration.md # Markdown guide (excluded from schema-check)
├── runtime/                    # Reference SDK (Employee class)
│   ├── __init__.py             # Public API: Employee, BudgetTracker, errors
│   ├── employee.py             # ~280 LOC: load+validate, system_prompt(),
│   │                           # is_action_allowed(), is_in_scope(), budget
│   ├── skill_export.py         # NEW: to_skill_md() — Anthropic SKILL.md exporter
│   └── cli.py                  # employee-runtime CLI
├── tooling/                    # Python validation library
│   ├── cli.py                  # CLI entry point (text/json/compact output)
│   ├── employee_validator.py   # EmployeeValidationOrchestrator (public API)
│   ├── validators/             # Field validators (type, enum, format, ...)
│   ├── parser.py               # SecureYAMLParser with depth + size limits
│   ├── schema.json             # JSON Schema for the spec
│   ├── cache.py                # TTL-based validation result caching
│   ├── config.py               # Configuration management
│   ├── constants.py            # Version and constants
│   ├── logging_config.py       # Logging setup
│   ├── monitoring.py           # Prometheus / StatsD metrics export
│   └── utils.py                # Utility functions (Color, etc.)
├── tests/                      # pytest suite (unit + integration + perf)
├── docs/
│   ├── COMPARISON.md           # employee.md vs AGENTS.md / worker.md / SOUL.md / SKILL.md
│   └── RESEARCH_NOTES.md       # NEW: verified primary sources backing /why and /integrations
├── INTEGRATION.md              # LangChain / AutoGen / CrewAI / MCP / experimental integrations
├── CONTRIBUTING.md
├── CHANGELOG.md
├── AGENTS.md                   # Instructions for AI agents working on this repo
├── Makefile                    # Local mirror of the CI quality gate
├── pyproject.toml              # Package config and dependencies
└── requirements.txt            # Core deps: pyyaml, jsonschema
```

## Setup

```bash
pip install -e ".[dev]"
```

## Usage

```bash
# Validate a single file
python -m tooling.cli employee.md

# Validate the full official set
python -m tooling.cli employee.md examples/*.md

# JSON output for CI
python -m tooling.cli employee.md --format json

# After installation, use the entry point
employee-validate employee.md
```

## Quality Gate

There are **two** validation surfaces and both must stay green:

| Surface | Command | What it enforces |
|---|---|---|
| Permissive runtime | `make validate` (`python -m tooling.cli`) | The validator the runtime ships with — friendly errors, lax on unknown fields. |
| Strict JSON Schema | `make validate-strict` | `jsonschema.Draft7Validator` against `tooling/schema.json` — catches **unknown enum values** and **mistyped values**. Mirrors the `schema-check` job in CI. Note: the schema does **not** set `additionalProperties: false`, so unknown / stray fields are *not* rejected by either surface today. |

The full CI gate is reproducible locally with:

```bash
make ci   # lint + format-check + typecheck + test + validate + validate-strict
```

Component commands:

```bash
make lint           # ruff check tooling/        (CI scope is tooling/ only)
make format         # ruff format tooling/
make format-check   # ruff format --check tooling/
make typecheck      # mypy tooling/ --ignore-missing-imports
make test           # pytest tests/ -v
```

> Note: `tests/` has pre-existing `F401` unused-import findings. CI does not
> lint `tests/` and neither do these targets — keep it that way until a
> dedicated cleanup PR lands.

## Dependencies

- `pyyaml>=6.0` — YAML parsing
- `jsonschema>=4.0.0` — Schema validation

Dev: `pytest`, `pytest-cov`, `ruff`, `mypy`, `pre-commit`.

## Architecture

- **CLI** (`tooling/cli.py`): argument parsing, output formatting
  (text/json/compact), metrics export.
- **Validator** (`tooling/employee_validator.py`): orchestrates validation
  across batch and parallel modes. Public API:
  `EmployeeValidationOrchestrator`, `ValidationResult`, `validate_file`.
- **Schema** (`tooling/schema.json`): JSON Schema for spec v1.0.0.
- **Parser** (`tooling/parser.py`): `SecureYAMLParser` with depth limits and
  path-traversal defenses.
- **Cache** (`tooling/cache.py`): TTL-based validation result caching.
- **Monitoring** (`tooling/monitoring.py`): Prometheus / StatsD export.

## Runtime SDK (`runtime/`)

`runtime/` is the missing 90% of the value prop: it lets an agent actually
*use* the contract instead of just having it as documentation.

```python
from runtime import Employee

emp = Employee.from_file("employee.md")     # loads + validates
prompt = emp.system_prompt()                # LLM-ready system prompt
emp.is_action_allowed("delete prod db")     # False (substring + token match)
emp.is_in_scope("write some tests")         # ScopeDecision(in_scope=True, ...)
emp.budget.try_spend(0.05)                  # raises BudgetExceeded over cap
```

Design constraints honoured:

- Zero new runtime dependencies — only `pyyaml` + the existing `tooling/`.
- No mutation of the schema or the `tooling/` validator. The runtime
  *imports* `EmployeeValidationOrchestrator` for its `from_file` /
  `from_yaml` validation step.
- Honest scope: `is_action_allowed` is a substring + token check, not a
  policy engine. `BudgetTracker` is in-process and resets on restart.
  Production-grade enforcement is a job for the consumer, not the SDK.

13 unit tests in `tests/unit/test_runtime.py`. The SDK is also exposed as a
CLI entry point installed alongside `employee-validate`:

```bash
employee-runtime examples/senior-dev.md                          # print system prompt
employee-runtime examples/senior-dev.md --summary                # one-line status
employee-runtime examples/senior-dev.md --check-action "delete prod db"   # exits 2 on deny
employee-runtime examples/senior-dev.md --check-scope "ship feature"      # exits 2 on out-of-scope
employee-runtime examples/senior-dev.md --json                   # machine-readable
```

## Website (`web/`)

The repo also ships a small marketing + docs + interactive validator site
served by the same Python process. It does **not** modify or fork the
spec, the examples, or the `tooling/` validator — it imports them.

Stack:

- Flask 3.x (server-rendered Jinja2 templates), single Python process.
- Prebuilt Tailwind CSS at `web/static/tailwind.css` (generated from
  `web/templates/**/*.html` + `tailwind.config.js` via the standalone
  Tailwind CLI binary at `.local/bin/tailwindcss`) + tiny custom CSS in
  `web/static/style.css`. **No CDN, no Node, no runtime JS build step.**
  Regenerate with `make tailwind` whenever a template adds or changes
  Tailwind utility classes (otherwise new classes will be missing from
  the compiled stylesheet). The input file is `web/static/tailwind.src.css`.
- Pygments for server-side YAML syntax highlighting on `/examples/<slug>`.

Routes:

| Route | What it does |
|---|---|
| `/` | Landing page, value props, peer-standards comparison strip. |
| `/why` | Research-grounded explanation of why employee.md exists vs AGENTS.md / worker.md / SKILL.md, with verified failure-mode evidence, peer-reviewed citations (arXiv:2509.22735, arXiv:2601.11369), FAQ JSON-LD. |
| `/spec` | Reference page generated from `tooling/schema.json` at request time. |
| `/examples` | Gallery of every `examples/*.md`, plus the markdown integration guide. |
| `/examples/<slug>` | Single example with syntax-highlighted YAML + Copy YAML button. |
| `/runtime` | Showcases the `runtime/` SDK with live system-prompt demo from `examples/senior-dev.md`. |
| `/integrations` | **NEW**: verified recipes for SKILL.md export, CrewAI, LangGraph, AutoGen, MCP, plain Python. Explicit honesty note about removed unverified projects. |
| `/integration` | **NEW**: full `INTEGRATION.md` (~790 lines) rendered in-app with Pygments syntax highlighting (`codehilite`), sidebar TOC (`toc` extension), heading permalinks, and mobile-safe overflow handling. Replaces the old GitHub bounce-out from `/docs` and the nav. |
| `/docs` | Quickstart with copyable code blocks (install + CLI + Python + runtime + CI). Now links internally to `/integration` (no GitHub redirect). |
| `/healthz` | `{"status": "ok", "version": "..."}` for uptime probes. |
| `/robots.txt` | **NEW**: SEO surface, points crawlers at `/sitemap.xml`. |
| `/sitemap.xml` | **NEW**: auto-generated from the route list + every non-guide example. |

Run the site locally:

```bash
python -m web.app             # dev server on 0.0.0.0:5000
```

Production is **GitHub Pages** — `make build-static` writes `dist/`
which `.github/workflows/static.yml` deploys on every push to `main`.
No WSGI server, no app host. Dependencies added on top of the core
spec for the dev server / static build: `flask`, `pygments`, `markdown`.

Web tests live in `tests/unit/test_web.py` (Flask test-client coverage
for every page, the experimental-section badges on `/spec`, and the
nav/sitemap/robots invariants).

Configurable URLs (handy until the GitHub repo and PyPI package are
published — both currently 404):

| Env var | Default | Purpose |
|---|---|---|
| `EMPLOYEE_MD_GITHUB_URL` | `https://github.com/NosytLabs/employee-md` | Used in `/docs`, `/runtime`, footer, and to derive `schema_url`. |
| `EMPLOYEE_MD_SCHEMA_URL` | derived from `EMPLOYEE_MD_GITHUB_URL` | Direct URL to `tooling/schema.json` shown on `/spec`. |

## Workflow

The Replit workflow `Start application` runs the website
(`python -m web.app`) on `0.0.0.0:5000`. The CLI smoke test is reachable
via `make validate` / `make validate-strict`, and the full official set is
exercised by the `schema-check` job in `.github/workflows/validate.yml` —
those three lists are the source of truth and must be kept in sync when
adding a new official example.

## Deployment

The site ships as a fully static snapshot to **GitHub Pages**:
`.github/workflows/static.yml` runs on every push to `main`, calls
`scripts/build_static_site.py` to snapshot the Flask site to `dist/`,
then deploys to the `gh-pages` environment at
`nosytlabs.github.io/employee-md/`. Validation is CLI-only
(`employee-validate examples/minimal.md`); there is no server-side
endpoint to host.

To enable GitHub Pages once after the workflow lands:
**Settings → Pages → Build and deployment → Source: GitHub Actions**.
The workflow rewrites root-relative URLs to the `/employee-md/`
subdirectory; if you point a custom domain at the repo, set the workflow
env var `BASE_PATH=` (empty string) and `CANONICAL_ORIGIN=https://your.domain`.

