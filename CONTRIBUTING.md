# Contributing to employee.md

Thank you for your interest in contributing to the **employee.md** open standard! We welcome contributions from the community to help define the future of AI agent employment.

## How to Contribute

### 1. Propose Changes
- **Open an Issue**: For major changes or new sections, please open an issue first to discuss the proposal.
- **Join the Discussion**: Engage with other contributors to refine ideas.

### 2. Make Changes
- **Fork the Repository**: Create your own fork of the repo.
- **Create a Branch**: Use a descriptive branch name (e.g., `feature/add-payment-protocol`).
- **Edit the Spec**: Update `employee.md` and `tooling/schema.json` as needed.
- **Update Examples**: Ensure all examples in `examples/` reflect your changes.
- **Update Docs**: Don't forget to update `README.md` and `INTEGRATION.md` if relevant.

### 3. Validate
Before submitting, run the validation tools to ensure everything is correct:

```bash
# Install dependencies
pip install pyyaml jsonschema

# Run validation script
python tooling/validate.py employee.md

# Validate all examples
for f in examples/*.md; do python tooling/validate.py "$f"; done
```

### 4. Submit Pull Request
- **Description**: Clearly explain what you changed and why.
- **Checklist**: Confirm you've updated the schema, examples, and docs.
- **CI**: Ensure the GitHub Actions validation passes.

## Design Principles

When proposing changes, keep these principles in mind:

- **AI-First**: The spec is primarily read by AI agents. Keep structures logical, explicit, and easy to parse.
- **Human-Readable**: It must also be easy for humans to write and review. Use clear keys and inline comments.
- **Flexible**: Avoid over-prescribing implementation details. Focus on *what* (interfaces, constraints) rather than *how*.
- **Modular**: Allow sections to be optional where possible.

## Style Guide

- **YAML**: Use standard YAML formatting.
- **Naming**: Use `snake_case` for keys.
- **Comments**: Use inline comments `#` for field descriptions and enum options.
- **Versioning**: Follow semantic versioning (Major.Minor) for the spec.

## Community

- **Code of Conduct**: Be respectful and constructive.
- **Questions**: Open a discussion or issue for help.

---

**Happy Coding!** 🤖
