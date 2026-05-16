# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | ✅ Yes    |
| < 1.0   | ❌ No     |

## Reporting a Vulnerability

We take the security of this open standard and its tooling seriously.

**Please do NOT open a public GitHub issue for security vulnerabilities.**

### How to report

1. Email **hi@nosytlabs.com** with subject line `[employee.md] Security Vulnerability`
2. Or create a [draft security advisory](https://github.com/NosytLabs/employee-md/security/advisories/new) in this repository

Include:
- A description of the vulnerability
- Steps to reproduce
- Affected versions
- Suggested fix (optional)

We will acknowledge your report within **48 hours** and aim to release a fix within **14 days** for confirmed issues.

## Scope

This policy covers:
- The JSON Schema validator (`tooling/`)
- The Python runtime SDK (`runtime/`)
- The Flask web app (`web/`)
- The YAML spec itself

## Validation Security

When integrating `employee.md` into your agent runtimes:

- **Sanitize inputs** — always validate YAML content before processing. The reference validator uses `SecureYAMLParser` which blocks `!!python/object` and `!!python/exec` tags.
- **Limit file size** — enforce a maximum file size before parsing to prevent resource exhaustion. The validator enforces a 512 KB default limit.
- **Guard against YAML bombs** — the parser rejects deeply nested structures and alias loops (billion-laughs attack).
- **Sandbox execution** — if your agent runtime executes code referenced in the spec, run it in an isolated environment (Docker, Firecracker, sandbox VMs).
- **Don't eval guardrails client-side** — `guardrails.prohibited_actions` must be enforced server-side or in a trusted runtime layer, never in untrusted client code.

## License

MIT — see [LICENSE](LICENSE).
