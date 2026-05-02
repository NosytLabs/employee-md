"""Render tooling/schema.json into structured data for the /spec page.

The spec page must never drift from the schema, so we read schema.json at
request time and project it into a list of section dictionaries the
template can iterate over without further logic.

Maintains a hand-curated set of `EXPERIMENTAL_FIELDS` (paths whose
status is documented in INTEGRATION.md as "experimental / planned" rather
than stable). The schema itself does not flag these — keep this list in
sync with the warnings in INTEGRATION.md.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


# Hand-curated. Sourced from INTEGRATION.md (the "Experimental / Planned
# Integrations" section). Kept here so the /spec page can visually
# distinguish stable schema surface from aspirational hooks.
EXPERIMENTAL_FIELDS: Set[str] = {
    # Whole sections that are experimental "namespaces":
    "protocols",
    # Specific fields with documented experimental status:
    "protocols.x402",
    "protocols.a2a",
    "economy.energy_accounting",
    "economy.profit_loss_tracking",
    "economy.insolvency_policy",
    "economy.wallets",
    "economy.internal_token",
    "economy.deductions",
    # `payment_method: "joulework"` is the experimental enum value, but the
    # field itself is stable. We don't flag it at the field level.
}


def load_schema(path: Path) -> Dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _resolve_ref(schema: Dict[str, Any], ref: str) -> Dict[str, Any]:
    if not ref.startswith("#/"):
        return {}
    parts = ref.lstrip("#/").split("/")
    node: Any = schema
    for part in parts:
        if not isinstance(node, dict) or part not in node:
            return {}
        node = node[part]
    return node if isinstance(node, dict) else {}


def _format_type(node: Dict[str, Any], schema: Dict[str, Any]) -> str:
    if "$ref" in node:
        target = _resolve_ref(schema, node["$ref"])
        ref_name = node["$ref"].split("/")[-1]
        if target:
            inner = _format_type(target, schema)
            return f"{ref_name} ({inner})" if inner else ref_name
        return ref_name
    t = node.get("type")
    if isinstance(t, list):
        return " | ".join(t)
    if t == "array":
        items = node.get("items", {})
        if isinstance(items, dict):
            inner = _format_type(items, schema)
            return f"array<{inner}>" if inner else "array"
        return "array"
    if t == "object":
        return "object"
    if t:
        return str(t)
    if "enum" in node:
        return "enum"
    return ""


def _format_constraints(node: Dict[str, Any]) -> List[str]:
    pieces: List[str] = []
    if "enum" in node:
        pieces.append("enum: " + ", ".join(str(v) for v in node["enum"]))
    if "format" in node:
        pieces.append(f"format: {node['format']}")
    if "pattern" in node:
        pieces.append(f"pattern: {node['pattern']}")
    if "minimum" in node or "maximum" in node:
        lo = node.get("minimum")
        hi = node.get("maximum")
        if lo is not None and hi is not None:
            pieces.append(f"range: {lo}..{hi}")
        elif lo is not None:
            pieces.append(f"min: {lo}")
        elif hi is not None:
            pieces.append(f"max: {hi}")
    return pieces


def _flatten_object(
    node: Dict[str, Any],
    schema: Dict[str, Any],
    prefix: str = "",
    required: Optional[List[str]] = None,
    depth: int = 0,
    max_depth: int = 8,
) -> List[Dict[str, Any]]:
    """Flatten an object schema into a list of {path, type, required, ...} rows."""
    if depth > max_depth:
        return []
    rows: List[Dict[str, Any]] = []
    required = required or []
    properties = node.get("properties", {})
    if not isinstance(properties, dict):
        return rows
    for name, child in properties.items():
        if not isinstance(child, dict):
            continue
        path = f"{prefix}.{name}" if prefix else name
        resolved = child
        if "$ref" in child:
            resolved = {**_resolve_ref(schema, child["$ref"]), **{
                k: v for k, v in child.items() if k != "$ref"
            }}
        type_str = _format_type(child, schema)
        constraints = _format_constraints(resolved)
        row = {
            "path": path,
            "name": name,
            "type": type_str,
            "required": name in required,
            "description": resolved.get("description", ""),
            "constraints": constraints,
            "depth": depth,
            "experimental": path in EXPERIMENTAL_FIELDS,
        }
        rows.append(row)
        # One level deep into nested objects so users see the shape without
        # the page becoming a wall of text.
        if depth < max_depth:
            if resolved.get("type") == "object" and "properties" in resolved:
                rows.extend(
                    _flatten_object(
                        resolved,
                        schema,
                        prefix=path,
                        required=resolved.get("required", []),
                        depth=depth + 1,
                        max_depth=max_depth,
                    )
                )
            elif resolved.get("type") == "array":
                items = resolved.get("items", {})
                if (
                    isinstance(items, dict)
                    and items.get("type") == "object"
                    and "properties" in items
                ):
                    rows.extend(
                        _flatten_object(
                            items,
                            schema,
                            prefix=f"{path}[]",
                            required=items.get("required", []),
                            depth=depth + 1,
                            max_depth=max_depth,
                        )
                    )
    return rows


def build_spec_sections(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build the section list rendered by spec.html."""
    sections: List[Dict[str, Any]] = []
    top_required = schema.get("required", []) or []
    properties = schema.get("properties", {})
    if not isinstance(properties, dict):
        return sections
    for section_name, section_node in properties.items():
        if not isinstance(section_node, dict):
            continue
        is_required = section_name in top_required
        description = section_node.get("description", "")
        section_type = section_node.get("type", "object")
        if section_type == "object":
            fields = _flatten_object(
                section_node,
                schema,
                required=section_node.get("required", []),
            )
        elif section_type == "array":
            items = section_node.get("items", {})
            if (
                isinstance(items, dict)
                and items.get("type") == "object"
                and "properties" in items
            ):
                fields = _flatten_object(
                    items,
                    schema,
                    prefix="[]",
                    required=items.get("required", []),
                )
            else:
                fields = []
        else:
            fields = []
        sections.append(
            {
                "name": section_name,
                "anchor": section_name,
                "required": is_required,
                "type": section_type,
                "description": description,
                "fields": fields,
                "experimental": section_name in EXPERIMENTAL_FIELDS,
            }
        )
    return sections
