## 2026-02-06 - CLI Visual Hierarchy
**Learning:** CLI tools often lack visual hierarchy, making it hard to scan for errors vs success messages.
**Action:** Always check if a CLI tool has colored output for success/failure states and implement it using standard ANSI codes (with TTY detection) if missing.
