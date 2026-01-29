# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of this open standard and its tooling seriously.

If you discover a security vulnerability within the spec logic, validation tooling, or examples, please report it as follows:

1.  **Do NOT open a public issue.**
2.  Email the maintainers at [INSERT EMAIL] or create a draft security advisory in the repository.
3.  Include details about the vulnerability and steps to reproduce.

We will acknowledge your report within 48 hours and work with you to mitigate the issue.

## Validation Security

When using the `validate.py` tool or integrating `employee.md` into your agents:

*   **Sanitize Inputs**: Always validate YAML content before processing it in your agent runtime.
*   **Limit Resources**: When parsing large spec files, enforce limits on file size and recursion depth to prevent DoS attacks (e.g., "Billion Laughs" attack in YAML).
*   **Sandboxing**: If using `code_execution` capabilities defined in the spec, ensure they run in isolated environments (Docker, Firecracker, etc.).

## License

This project is licensed under the MIT License.
