# Changelog

All notable changes to the **employee.md** specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-29

### ✨ Added
- **Spec Metadata**: New `spec` section for versioning, compatibility, and schema linking.
- **Mission Section**: Explicit `purpose`, `objectives`, `success_criteria`, and `non_goals`.
- **Scope Section**: Defined boundaries with `in_scope`, `out_of_scope`, `dependencies`, and `constraints`.
- **Permissions Section**: Granular access control for `data`, `system`, `network`, and `tools`.
- **Verification Section**: Quality gates including `required_checks` and `evidence`.
- **Tooling**: Python-based validator (`tooling/validate.py`) and JSON Schema (`tooling/schema.json`).
- **CI/CD**: GitHub Actions workflow for automated validation.
- **Documentation**: Comprehensive README, Integration Guide, and Contributing Guidelines.

### 🦋 Changed
- **Array Types**: Standardized all list items in the spec to explicit types (e.g., `string`) for better validation.
- **Examples**: Updated all example files (`minimal`, `ai-assistant`, etc.) to comply with v1.0 schema.
- **Validation Logic**: Enhanced validator to support new sections and placeholder value skipping.

### 🚀 Initial Release
- Launched `employee.md` as an open standard for AI agent employment.
- Established core sections: `identity`, `role`, `economy`, `delegation`, `lifecycle`, `compliance`, `communication`, `guardrails`, `ai_settings`, `knowledge_base`, `integration`, `performance`, `protocols`.
