"""Export an employee.md contract to Anthropic SKILL.md format.

Anthropic's Claude Skills are packaged as a directory with a SKILL.md at
the root. The SKILL.md has YAML frontmatter (``name``, ``description``,
optional ``allowed-tools``) followed by Markdown body content describing
what the skill does and when to use it. This module converts a loaded
:class:`runtime.Employee` contract into that format so the same source of
truth can power a Claude Skill, an MCP server prompt, or a system prompt.

The mapping is intentionally lossy in one direction (SKILL.md is a
narrower format than employee.md) but lossless in spirit: every important
constraint from the contract appears in the rendered body, and the
frontmatter ``description`` field is short enough to fit Anthropic's
progressive-disclosure budget.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional

import yaml

from .employee import Employee


_SLUG_RE = re.compile(r"[^a-z0-9-]+")
_MAX_DESCRIPTION_CHARS = 1024  # Anthropic's documented progressive-disclosure budget
# Reserved slugs Anthropic forbids in the SKILL.md `name` field. We refuse to
# emit these (and any prefixed variant like "anthropic-foo") so that an
# innocent agent name like "Anthropic Helper" can never collide with the
# platform namespace.
_RESERVED_NAME_PREFIXES = ("anthropic", "claude")


def _slugify(value: str) -> str:
    """Lowercase kebab-case slug suitable for the SKILL.md ``name`` field.

    Anthropic enforces ≤64 chars, lowercase + digits + hyphens only, no
    consecutive separators, and no leading/trailing hyphen. We also refuse
    reserved prefixes (``anthropic``/``claude``) — an exporter that quietly
    emitted ``anthropic-helper`` would silently collide with the platform
    namespace, so we prefix them with ``user-`` instead.
    """
    if not value:
        return "unnamed-skill"
    s = value.strip().lower().replace("_", "-")
    s = _SLUG_RE.sub("-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    s = (s or "unnamed-skill")[:64].rstrip("-") or "unnamed-skill"
    for reserved in _RESERVED_NAME_PREFIXES:
        if s == reserved or s.startswith(reserved + "-"):
            s = ("user-" + s)[:64].rstrip("-")
            break
    return s


def _short(text: str, limit: int) -> str:
    """Trim ``text`` to ``limit`` chars on a word boundary, no ellipsis-cruft."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0]
    return cut + "…"


def _join_list(items: Optional[List[Any]], *, bullet: str = "- ") -> str:
    if not items:
        return ""
    return "\n".join(f"{bullet}{str(x).strip()}" for x in items)


def _build_description(employee: Employee) -> str:
    """The frontmatter `description` is what Claude reads to decide whether
    to load the full skill. Keep it tight and action-oriented."""
    role = employee.data.get("role", {}) or {}
    mission = employee.data.get("mission", {}) or {}
    title = role.get("title", "AI agent")
    level = role.get("level", "")
    purpose = mission.get("purpose", "")
    if purpose:
        text = f"{title}{(' (' + level + ')') if level else ''} — {purpose}"
    else:
        text = f"{title}{(' (' + level + ')') if level else ''}"
    return _short(text, _MAX_DESCRIPTION_CHARS)


def _build_frontmatter(employee: Employee, *, name: Optional[str] = None) -> Dict[str, Any]:
    role = employee.data.get("role", {}) or {}
    identity = employee.data.get("identity", {}) or {}
    permissions = employee.data.get("permissions", {}) or {}
    fm: Dict[str, Any] = {
        "name": _slugify(
            name
            or identity.get("agent_id")
            or role.get("title")
            or employee.data.get("spec", {}).get("name")
            or "employee-skill"
        ),
        "description": _build_description(employee),
    }
    tools = permissions.get("tool_access") or []
    if isinstance(tools, list) and tools:
        fm["allowed-tools"] = [str(t) for t in tools]
    return fm


def _render_body(employee: Employee) -> str:
    """Render the contract as a SKILL.md body. Sections are deliberately
    short and skimmable — Claude loads the body lazily under progressive
    disclosure, so we want the most load-bearing constraints first."""
    d = employee.data
    role = d.get("role", {}) or {}
    mission = d.get("mission", {}) or {}
    scope = d.get("scope", {}) or {}
    guardrails = d.get("guardrails", {}) or {}
    permissions = d.get("permissions", {}) or {}
    operating = d.get("operating_policy", {}) or {}
    economy = d.get("economy", {}) or {}

    parts: List[str] = []

    title_line = role.get("title", "AI Agent")
    if role.get("level"):
        title_line += f" — {role['level']}"
    parts.append(f"# {title_line}\n")

    if mission.get("purpose"):
        parts.append(f"**Purpose.** {mission['purpose']}\n")

    if mission.get("objectives"):
        parts.append("## Objectives\n" + _join_list(mission["objectives"]) + "\n")

    if scope.get("in_scope"):
        parts.append("## In scope\n" + _join_list(scope["in_scope"]) + "\n")

    if scope.get("out_of_scope"):
        parts.append("## Out of scope\n" + _join_list(scope["out_of_scope"]) + "\n")

    if guardrails:
        gp_lines: List[str] = []
        prohibited = guardrails.get("prohibited_actions") or []
        if prohibited:
            gp_lines.append("**Never do:**")
            gp_lines.append(_join_list(prohibited))
        approval = guardrails.get("required_approval") or []
        if approval:
            gp_lines.append("\n**Require human approval before:**")
            gp_lines.append(_join_list(approval))
        if "max_spend_per_task" in guardrails:
            gp_lines.append(
                f"\n**Spend cap per task:** {guardrails['max_spend_per_task']}"
            )
        if "confidence_threshold" in guardrails:
            gp_lines.append(
                f"\n**Minimum confidence to act:** {guardrails['confidence_threshold']}"
            )
        if gp_lines:
            parts.append("## Guardrails\n" + "\n".join(gp_lines).strip() + "\n")

    if operating.get("always") or operating.get("avoid") or operating.get("ask_first"):
        op_lines: List[str] = []
        if operating.get("always"):
            op_lines.append("**Always:**\n" + _join_list(operating["always"]))
        if operating.get("avoid"):
            op_lines.append("\n**Avoid:**\n" + _join_list(operating["avoid"]))
        if operating.get("ask_first"):
            op_lines.append("\n**Ask first:**\n" + _join_list(operating["ask_first"]))
        parts.append("## Operating policy\n" + "\n".join(op_lines).strip() + "\n")

    if permissions.get("tool_access"):
        parts.append(
            "## Tools available\n" + _join_list(permissions["tool_access"]) + "\n"
        )

    if economy.get("budget_limit") is not None:
        currency = economy.get("currency", "USD")
        parts.append(
            f"## Budget\nTotal budget: **{economy['budget_limit']} {currency}**\n"
        )

    parts.append(
        "## Source\nThis SKILL.md was generated from an `employee.md` contract. "
        "The contract is the source of truth — re-export when the contract changes "
        "rather than editing this file by hand."
    )

    return "\n".join(parts).strip() + "\n"


def to_skill_md(employee: Employee, *, name: Optional[str] = None) -> str:
    """Return the full SKILL.md content (frontmatter + body) for ``employee``.

    Parameters
    ----------
    employee:
        A loaded :class:`runtime.Employee` instance.
    name:
        Optional explicit name for the skill. When omitted, the slug is
        derived from ``identity.agent_id`` → ``role.title`` → spec name.

    Returns
    -------
    str
        A complete SKILL.md document, ready to write to disk.
    """
    fm = _build_frontmatter(employee, name=name)
    fm_yaml = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    body = _render_body(employee)
    return f"---\n{fm_yaml}\n---\n\n{body}"


__all__ = ["to_skill_md"]
