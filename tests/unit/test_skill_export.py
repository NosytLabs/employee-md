"""Tests for runtime.skill_export — the employee.md → SKILL.md converter.

These tests verify that the rendered SKILL.md:
  * Has YAML frontmatter with the Anthropic-required `name` and `description`.
  * Slugifies the name into kebab-case (≤64 chars).
  * Caps `description` at 1024 characters (Anthropic's progressive-disclosure budget).
  * Includes the load-bearing constraints (prohibited_actions, scope, budget) in the body.
  * Round-trips through PyYAML so the frontmatter is real, parseable YAML.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from runtime import Employee
from runtime.skill_export import to_skill_md, _slugify, _short, _MAX_DESCRIPTION_CHARS


EXAMPLES = Path(__file__).resolve().parent.parent.parent / "examples"


def _split_frontmatter(text: str):
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter fence"
    _, rest = text.split("---\n", 1)
    fm_text, body = rest.split("\n---\n", 1)
    return yaml.safe_load(fm_text), body


def test_slugify_basic():
    assert _slugify("Senior Backend Engineer") == "senior-backend-engineer"
    assert _slugify("trading_bot_001") == "trading-bot-001"
    assert _slugify("  Multiple   Spaces  ") == "multiple-spaces"
    assert _slugify("") == "unnamed-skill"
    assert _slugify("!!!") == "unnamed-skill"


def test_slugify_caps_at_64_chars():
    long = "Some Very Long Agent Name That Easily Exceeds Sixty Four Characters In One Line"
    out = _slugify(long)
    assert len(out) <= 64
    assert not out.endswith("-")


def test_slugify_rejects_reserved_anthropic_prefix():
    """A name slugifying to ``anthropic`` or ``anthropic-foo`` must NOT be
    emitted as-is — it would silently collide with the platform namespace."""
    assert _slugify("Anthropic") == "user-anthropic"
    assert _slugify("Anthropic Helper") == "user-anthropic-helper"
    # Bare exact match
    assert _slugify("anthropic") == "user-anthropic"


def test_slugify_rejects_reserved_claude_prefix():
    assert _slugify("Claude") == "user-claude"
    assert _slugify("Claude Assistant") == "user-claude-assistant"
    # Substring that is NOT a prefix should be left alone
    assert _slugify("not-claude-but-similar") == "not-claude-but-similar"


def test_short_respects_budget():
    text = "word " * 500
    out = _short(text, 50)
    assert len(out) <= 50
    # Must end with the ellipsis marker only when actually truncated
    assert out.endswith("…")


def test_short_passthrough_when_under_limit():
    assert _short("hello world", 100) == "hello world"


def test_export_minimal_example_has_frontmatter_and_body():
    emp = Employee.from_file(EXAMPLES / "minimal.md", validate=False)
    out = to_skill_md(emp)
    fm, body = _split_frontmatter(out)
    assert isinstance(fm, dict)
    assert "name" in fm
    assert "description" in fm
    # Anthropic limits
    assert len(fm["name"]) <= 64
    assert fm["name"] == fm["name"].lower()
    assert all(c.isalnum() or c in "-" for c in fm["name"]) and "_" not in fm["name"]
    assert len(fm["description"]) <= _MAX_DESCRIPTION_CHARS
    # Body should mention the role title
    assert emp.title in body or emp.title.lower() in body.lower()


def test_export_includes_prohibited_actions_in_body():
    emp = Employee.from_file(EXAMPLES / "senior-dev.md", validate=False)
    out = to_skill_md(emp)
    _, body = _split_frontmatter(out)
    assert "Never do" in body or "Guardrails" in body
    for forbidden in emp.prohibited_actions():
        # Each prohibited action should appear in the rendered body.
        assert forbidden in body, f"prohibited action '{forbidden}' missing from SKILL.md body"


def test_export_includes_tools_in_frontmatter():
    emp = Employee.from_file(EXAMPLES / "trading-bot.md", validate=False)
    out = to_skill_md(emp)
    fm, _ = _split_frontmatter(out)
    tools = (emp.data.get("permissions") or {}).get("tool_access") or []
    if tools:
        assert "allowed-tools" in fm
        assert set(fm["allowed-tools"]) == {str(t) for t in tools}


def test_export_explicit_name_override():
    emp = Employee.from_file(EXAMPLES / "minimal.md", validate=False)
    out = to_skill_md(emp, name="My Custom Skill")
    fm, _ = _split_frontmatter(out)
    assert fm["name"] == "my-custom-skill"


def test_export_handles_long_purpose_without_blowing_budget():
    long_purpose = "x" * 5000
    emp = Employee({
        "role": {"title": "Test", "level": "senior"},
        "lifecycle": {"status": "active"},
        "mission": {"purpose": long_purpose},
    })
    out = to_skill_md(emp)
    fm, _ = _split_frontmatter(out)
    assert len(fm["description"]) <= _MAX_DESCRIPTION_CHARS


def test_export_renders_budget_when_present():
    emp = Employee({
        "role": {"title": "Funded Agent", "level": "senior"},
        "lifecycle": {"status": "active"},
        "economy": {"budget_limit": 5000, "currency": "USD"},
    })
    out = to_skill_md(emp)
    _, body = _split_frontmatter(out)
    assert "5000" in body
    assert "USD" in body


def test_export_round_trip_through_pyyaml():
    """The frontmatter must be valid YAML — parseable round-trip."""
    emp = Employee.from_file(EXAMPLES / "ai-assistant.md", validate=False)
    out = to_skill_md(emp)
    fm, body = _split_frontmatter(out)
    re_dumped = yaml.safe_dump(fm, sort_keys=False)
    re_loaded = yaml.safe_load(re_dumped)
    assert re_loaded == fm
    assert body.strip(), "body must be non-empty"
