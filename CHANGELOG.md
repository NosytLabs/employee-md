# Changelog

All notable changes to the **employee.md** specification and tooling are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-02-01

### ✨ Added

#### Identity & Role
- **Enhanced Identity Section**: Added `display_name`, `description`, `avatar_url`, and `tags` fields for richer agent metadata
- **Expanded Role Section**: Added `function`, `reports_to`, `certifications`, and `work_schedule` fields for comprehensive job definitions
- **Context Resources**: Added `resources` subsection with `documentation`, `dashboard`, and `api_endpoint` URLs

#### Security & Compliance
- **Permission Controls**: Added `admin_permissions`, `can_invite_users`, and `can_modify_permissions` flags for granular access control
- **Verification Policy**: Added `auto_merge`, `min_approvals`, and `require_tests` options for quality gates
- **Compliance Enhancements**: Added `audit_retention_days`, `data_retention_policy`, `pii_handling`, and `encryption_required` fields

#### AI & Performance
- **Delegation Preferences**: Added `preferred_task_types` and `excluded_task_types` fields for task routing
- **Lifecycle Tracking**: Added `availability_status`, `max_utilization`, and `version_history` for operational visibility
- **Enhanced Guardrails**: Added `max_execution_time`, `max_api_calls_per_minute`, `content_filter`, `allowed_domains`, and `blocked_domains`
- **AI Settings Improvements**: Added `fallback_models`, `chain_of_thought`, and `self_correction` options for advanced model configuration

#### Communication & Integration
- **Communication Details**: Added `email`, `slack_handle`, and `notify_on` fields for better agent interaction
- **Enhanced Protocols**: Expanded A2A, x402, human_review, and delegation protocol configurations

#### Tooling
- **Schema Documentation**: Added comprehensive field descriptions to JSON Schema for better IDE support
- **Performance Monitoring**: Added metrics collection and Prometheus/StatsD export
- **Caching System**: Implemented validation result caching for improved performance
- **Parallel Validation**: Support for concurrent validation of multiple files

### 🔄 Changed

- **Spec Version**: Updated all examples to version 2.1.0
- **Schema Structure**: Reorganized schema with reusable definitions for maintainability
- **Documentation**: Significantly streamlined README.md while maintaining essential information
- **GitHub Templates**: Improved issue and PR templates for better contributor experience
- **CI Workflow**: Enhanced GitHub Actions with schema validation, coverage reporting, and Python 3.8-3.12 matrix testing
- **Development Tools**: Migrated from pylint/black to ruff for unified linting and formatting

### 🗑️ Removed

- **Experimental Concepts Section**: Consolidated JouleWork references into Economy section
- **Redundant Documentation**: Removed duplicate content between README and spec
- **Deprecated Fields**: Removed placeholder type definitions from spec

### 🐛 Fixed

- Fixed duplicate `title` field in employee.md spec
- Corrected CLI argument parsing edge cases
- Improved error message formatting for nested validation errors

### 🔒 Security

- Added validation for wallet address formats (Ethereum, Bitcoin)
- Enhanced password/secret detection in configuration files
- Added content filtering options for agent outputs

---

## [2.0.0] - 2026-01-30

### ✨ Added

- **Workflows Section**: Standard operating procedures for intake, execution, review, and handoff
- **Operating Policy**: Explicit `always`, `avoid`, `ask_first`, and `evidence_required` rules
- **Performance Metrics**: KPIs, SLAs, and benchmark tracking capabilities
- **Knowledge Base**: Documentation URLs, training data sources, and best practices linking

### 🔄 Changed

- Restructured specification for better modularity
- Improved schema validation with stricter type checking
- Updated all examples to reflect new structure

---

## [1.0.0] - 2026-01-29

### ✨ Added

#### Core Specification
- **Spec Metadata**: New `spec` section for versioning, compatibility, and schema linking
- **Mission Section**: Explicit `purpose`, `objectives`, `success_criteria`, and `non_goals` for clear agent direction
- **Scope Section**: Defined boundaries with `in_scope`, `out_of_scope`, `dependencies`, and `constraints`
- **Permissions Section**: Granular access control for `data`, `system`, `network`, and `tools`
- **Verification Section**: Quality gates including `required_checks` and `evidence`

#### Tooling & Infrastructure
- **Validator**: Python-based validation tool (`tooling/validate.py`)
- **JSON Schema**: Machine-readable schema (`tooling/schema.json`)
- **CLI Tool**: Command-line interface for validation
- **CI/CD**: GitHub Actions workflow for automated validation

#### Documentation
- **README.md**: Comprehensive project documentation
- **Integration Guide**: Detailed integration instructions (Python, TypeScript, LangChain, AutoGen)
- **Contributing Guidelines**: Developer setup and contribution process
- **Examples**: 5 example configurations (minimal, senior-dev, ai-assistant, security-auditor, data-analyst, freelancer)

#### Core Sections Established
- `identity`: Agent identification and metadata
- `role`: Job title, level, capabilities, skills
- `economy`: Budget, payment, and cost tracking
- `delegation`: Task delegation and orchestration
- `lifecycle`: Agent status and lifecycle management
- `compliance`: Regulatory frameworks and audit
- `communication`: Channels and availability
- `guardrails`: Safety constraints and limits
- `ai_settings`: Model configuration and behavior
- `knowledge_base`: Information sources and references
- `integration`: External service connections
- `performance`: Metrics and targets
- `protocols`: Communication and payment protocols

### 🚀 Initial Release

Launched `employee.md` as an open standard for AI agent employment contracts. The specification aims to provide:

- **Standardization**: A common format for defining AI agent capabilities and constraints
- **Interoperability**: Works with AGENTS.md, MCP, and other agentic standards
- **Security**: Built-in guardrails and compliance frameworks
- **Flexibility**: Extensible design with custom fields support

---

## Version History Summary

| Version | Date | Key Changes |
|---------|------|-------------|
| 2.1.0 | 2026-02-01 | Major feature expansion: enhanced identity, compliance, AI settings |
| 2.0.0 | 2026-01-30 | Added workflows, operating policy, performance metrics |
| 1.0.0 | 2026-01-29 | Initial release with core specification |

---

## Migration Guides

### Upgrading from 1.x to 2.x

The 2.x release is backward compatible with 1.x configurations. To take advantage of new features:

1. Update `spec.version` to `"2.1.0"`
2. Add new optional sections as needed (workflows, performance, etc.)
3. Update schema reference URL

```yaml
spec:
  name: employee.md
  version: "2.1.0"  # Updated from "1.0.0"
  kind: agent-employment
  schema: "https://raw.githubusercontent.com/NosytLabs/employee-md/main/tooling/schema.json"
```

---

## [Unreleased]

### Planned for Future Releases

- [ ] VS Code extension for schema validation and autocomplete
- [ ] Web-based validator UI
- [ ] Additional compliance frameworks (HIPAA, PCI-DSS)
- [ ] Enhanced A2A protocol implementation guide
- [ ] Multi-agent orchestration examples
- [ ] Cost tracking and analytics dashboard

---

For a complete list of changes, see the [commit history](https://github.com/NosytLabs/employee-md/commits/main).
