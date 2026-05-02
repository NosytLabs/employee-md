"""Flask app: landing page, spec reference, examples gallery, validator, docs."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import markdown as md
import yaml
from flask import Flask, abort, jsonify, render_template, request
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import YamlLexer

from tooling.constants import VERSION

from runtime import Employee

# Allow operators to override the GitHub URL when the canonical repo
# moves or while it is still unpublished. Default kept for back-compat.
GITHUB_URL = os.environ.get(
    "EMPLOYEE_MD_GITHUB_URL",
    "https://github.com/NosytLabs/employee-md",
).rstrip("/")

# Derive the raw-content URL from GITHUB_URL when possible so the schema
# link and the GitHub link don't drift apart.
def _derive_raw_url(github_url: str) -> str:
    if github_url.startswith("https://github.com/"):
        slug = github_url[len("https://github.com/"):]
        return f"https://raw.githubusercontent.com/{slug}/main/tooling/schema.json"
    return f"{github_url}/raw/main/tooling/schema.json"


SCHEMA_URL = os.environ.get(
    "EMPLOYEE_MD_SCHEMA_URL",
    _derive_raw_url(GITHUB_URL),
)

from .spec_doc import build_spec_sections, load_schema

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT / "examples"
SCHEMA_PATH = ROOT / "tooling" / "schema.json"
COMPARISON_PATH = ROOT / "docs" / "COMPARISON.md"
INTEGRATION_PATH = ROOT / "INTEGRATION.md"

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["JSON_SORT_KEYS"] = False

_yaml_lexer = YamlLexer()
_html_formatter = HtmlFormatter(cssclass="codehilite", linenos=False, nowrap=False)


def _highlight_yaml(text: str) -> str:
    return highlight(text, _yaml_lexer, _html_formatter)


def _load_examples() -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    if not EXAMPLES_DIR.is_dir():
        return items
    for fp in sorted(EXAMPLES_DIR.glob("*.md")):
        if fp.name == "README.md":
            continue
        text = fp.read_text(encoding="utf-8")
        if fp.name == "molt-bot-integration.md":
            items.append(
                {
                    "slug": fp.stem,
                    "name": fp.name,
                    "title": "MOLT bot integration walk-through",
                    "level": None,
                    "summary": (
                        "Markdown integration guide showing how a MOLT bot "
                        "consumes an employee.md contract."
                    ),
                    "is_guide": True,
                    "raw": text,
                }
            )
            continue
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError:
            continue
        if not isinstance(data, dict):
            continue
        role = data.get("role") if isinstance(data.get("role"), dict) else {}
        identity = (
            data.get("identity") if isinstance(data.get("identity"), dict) else {}
        )
        mission = (
            data.get("mission") if isinstance(data.get("mission"), dict) else {}
        )
        title = (
            role.get("title")
            or identity.get("display_name")
            or fp.stem.replace("-", " ").title()
        )
        summary = (mission.get("purpose") or identity.get("description") or "").strip()
        items.append(
            {
                "slug": fp.stem,
                "name": fp.name,
                "title": title,
                "level": role.get("level"),
                "department": role.get("department"),
                "summary": summary,
                "is_guide": False,
                "raw": text,
            }
        )
    return items


EXAMPLES: List[Dict[str, Any]] = _load_examples()
EXAMPLES_BY_SLUG: Dict[str, Dict[str, Any]] = {e["slug"]: e for e in EXAMPLES}


_COMPARISON_ROW_RE = re.compile(
    r"^\|\s*\*\*\[(?P<name>[^\]]+)\]\((?P<url>[^)]+)\)\*\*\s*\|"
    r"[^|]*\|"
    r"[^|]*\|"
    r"\s*(?P<answers>[^|]+?)\s*\|\s*$"
)
_COMPARISON_NOLINK_ROW_RE = re.compile(
    r"^\|\s*\*\*(?P<name>[A-Za-z0-9_.\-]+)\*\*\s*\|"
    r"[^|]*\|"
    r"[^|]*\|"
    r"\s*(?P<answers>[^|]+?)\s*\|\s*$"
)


def _parse_comparison() -> List[Dict[str, Any]]:
    """Parse the first comparison table out of docs/COMPARISON.md so this
    strip never drifts from the canonical comparison doc.

    The parser is permissive — it stops at the first blank line after the
    header, falls back to a plain-name regex when a row has no markdown
    link, and tolerates the trailing `<https://...>` bare-link cell that
    we don't need to render.
    """
    if not COMPARISON_PATH.is_file():
        return []
    rows: List[Dict[str, Any]] = []
    in_table = False
    for raw in COMPARISON_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not in_table:
            if line.startswith("| Standard"):
                in_table = True
            continue
        if not line or not line.startswith("|"):
            break
        if set(line.replace("|", "").replace(":", "").strip()) <= {"-", " "}:
            continue  # separator row
        m = _COMPARISON_ROW_RE.match(raw) or _COMPARISON_NOLINK_ROW_RE.match(raw)
        if not m:
            continue
        name = m.group("name").strip()
        url = (m.groupdict().get("url") or "").strip()
        answers_md = m.group("answers").strip()
        # Strip markdown bold and trailing prose after the em-dash; the strip
        # is intentionally aggressive so the card stays one short sentence.
        answers = answers_md.replace("**", "").strip()
        if answers.startswith('"') and '"' in answers[1:]:
            short = answers[1 : answers.index('"', 1)]
        else:
            short = answers.split("—", 1)[0].strip().rstrip(".")
        if "—" in answers:
            scope = answers.split("—", 1)[1].strip().rstrip(".")
        else:
            scope = ""
        is_self = name.lower() == "employee.md"
        rows.append(
            {
                "name": name,
                "url": url_for_self if is_self else url,
                "answers": short,
                "scope": scope,
                "self": is_self,
            }
        )
    return rows


# Sentinel used inside _parse_comparison; we want the "employee.md" row to
# point at our own /spec page rather than the GitHub markdown source.
url_for_self = "/spec"


_COMPARISON_ROWS: List[Dict[str, Any]] = _parse_comparison()


@app.context_processor
def _inject_globals() -> Dict[str, Any]:
    return {
        "version": VERSION,
        "github_url": GITHUB_URL,
        "schema_url": SCHEMA_URL,
    }


@app.after_request
def _disable_cache(resp):  # type: ignore[no-untyped-def]
    """Hard-disable caching in dev so the Replit preview iframe always sees
    the latest changes. This is intentionally permissive — production behind
    Replit Deploy will be served by the same Flask app and is fine without
    aggressive cache control."""
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.route("/")
def index() -> str:
    return render_template(
        "index.html",
        comparison=_COMPARISON_ROWS,
        example_count=len([e for e in EXAMPLES if not e["is_guide"]]),
    )


@app.route("/spec")
def spec() -> str:
    schema = load_schema(SCHEMA_PATH)
    sections = build_spec_sections(schema)
    return render_template(
        "spec.html",
        sections=sections,
        spec_title=schema.get("title", "Employee.md Configuration"),
        spec_version=schema.get("version", VERSION),
    )


def _yaml_preview(text: str, max_lines: int = 12) -> str:
    """Pygments-highlighted preview of the first N non-empty YAML lines.

    Used on the /examples gallery so each card shows the actual shape of
    the spec, not just a card title."""
    lines: List[str] = []
    for raw in text.splitlines():
        if raw.strip() in ("", "---"):
            continue
        lines.append(raw)
        if len(lines) >= max_lines:
            break
    snippet = "\n".join(lines)
    return highlight(snippet, _yaml_lexer, _html_formatter)


@app.route("/examples")
def examples() -> str:
    specs = [
        {**e, "preview": _yaml_preview(e["raw"])}
        for e in EXAMPLES
        if not e["is_guide"]
    ]
    guides = [e for e in EXAMPLES if e["is_guide"]]
    return render_template("examples.html", specs=specs, guides=guides)


@app.route("/examples/<slug>")
def example_detail(slug: str) -> str:
    item = EXAMPLES_BY_SLUG.get(slug)
    if not item:
        abort(404)
    highlighted = _highlight_yaml(item["raw"])
    return render_template(
        "example_detail.html",
        item=item,
        highlighted=highlighted,
    )


@app.route("/why")
def why() -> str:
    return render_template("why.html")


@app.route("/integrations")
def integrations() -> str:
    return render_template("integrations.html")


_SOURCE_H1_RE = re.compile(r"^#\s+Integration Guide\s*\n+", flags=re.MULTILINE)
_SOURCE_TOC_RE = re.compile(
    r"##\s+📚 Table of Contents\b.*?\n---\s*\n", flags=re.DOTALL
)


def _strip_source_chrome(text: str) -> str:
    """Strip the source H1 and inline TOC; the template provides both."""
    text = _SOURCE_H1_RE.sub("", text, count=1)
    text = _SOURCE_TOC_RE.sub("", text, count=1)
    return text


def _rewrite_repo_links(text: str) -> str:
    """Rewrite the in-repo relative links so they resolve against the site
    root rather than `/integration/...`."""
    text = text.replace("](examples/zhc-worker.md)", "](/examples/zhc-worker)")
    text = text.replace("](examples/)", "](/examples)")
    text = text.replace("](tooling/schema.json)", f"]({SCHEMA_URL})")
    return text


def _render_integration_markdown() -> Dict[str, str]:
    """Render INTEGRATION.md to HTML + a sidebar TOC. The codehilite class
    matches the Pygments theme served by /pygments.css."""
    if not INTEGRATION_PATH.is_file():
        return {"html": "<p>INTEGRATION.md not found.</p>", "toc": ""}
    raw = _rewrite_repo_links(
        _strip_source_chrome(INTEGRATION_PATH.read_text(encoding="utf-8"))
    )
    converter = md.Markdown(
        extensions=["fenced_code", "tables", "sane_lists", "toc",
                    "codehilite", "attr_list"],
        extension_configs={
            "codehilite": {
                "css_class": "codehilite",
                "guess_lang": False,
                "linenums": False,
            },
            "toc": {
                "permalink": "¶",
                "permalink_class": "headerlink",
                "permalink_title": "Permalink to this section",
                "toc_depth": "2-4",
            },
        },
        output_format="html5",
    )
    html = converter.convert(raw)
    return {"html": html, "toc": getattr(converter, "toc", "")}


# Cached at import time; INTEGRATION.md is a static repo asset.
_INTEGRATION_RENDERED: Dict[str, str] = _render_integration_markdown()


@app.route("/integration")
def integration() -> str:
    return render_template(
        "integration.html",
        html=_INTEGRATION_RENDERED["html"],
        toc=_INTEGRATION_RENDERED["toc"],
    )


@app.route("/robots.txt")
def robots_txt():  # type: ignore[no-untyped-def]
    base = request.url_root.rstrip("/")
    body = (
        "User-agent: *\n"
        "Allow: /\n"
        f"Sitemap: {base}/sitemap.xml\n"
    )
    return body, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/sitemap.xml")
def sitemap_xml():  # type: ignore[no-untyped-def]
    base = request.url_root.rstrip("/")
    # Static page set + one entry per non-guide example
    pages = [
        ("/", "1.0"),
        ("/why", "0.9"),
        ("/spec", "0.9"),
        ("/examples", "0.8"),
        ("/integrations", "0.8"),
        ("/integration", "0.8"),
        ("/runtime", "0.7"),
        ("/docs", "0.7"),
    ]
    for ex in EXAMPLES:
        if ex.get("is_guide"):
            continue
        pages.append((f"/examples/{ex['slug']}", "0.6"))

    parts = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, prio in pages:
        parts.append(
            f"<url><loc>{base}{path}</loc><priority>{prio}</priority></url>"
        )
    parts.append("</urlset>")
    body = "\n".join(parts) + "\n"
    return body, 200, {"Content-Type": "application/xml; charset=utf-8"}


@app.route("/runtime")
def runtime_page() -> str:
    """Showcase the runtime/ reference SDK with a live system-prompt demo."""
    sample_path = EXAMPLES_DIR / "senior-dev.md"
    sample_yaml = sample_path.read_text(encoding="utf-8") if sample_path.exists() else ""
    sample_prompt = ""
    if sample_yaml:
        try:
            sample_prompt = Employee.from_yaml(sample_yaml).system_prompt()
        except Exception:  # noqa: BLE001 - defensive; demo only
            sample_prompt = ""
    return render_template(
        "runtime.html",
        sample_yaml=sample_yaml,
        sample_prompt=sample_prompt,
    )


@app.route("/docs")
def docs() -> str:
    return render_template("docs.html")


@app.route("/healthz")
def healthz():  # type: ignore[no-untyped-def]
    return jsonify({"status": "ok", "version": VERSION})


@app.route("/pygments.css")
def pygments_css():  # type: ignore[no-untyped-def]
    css = _html_formatter.get_style_defs(".codehilite")
    return css, 200, {"Content-Type": "text/css; charset=utf-8"}


_FAVICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="14" fill="#0f172a"/>'
    '<text x="50%" y="58%" text-anchor="middle" font-family="ui-monospace,'
    'Menlo,monospace" font-size="34" font-weight="700" fill="#a5b4fc">e</text>'
    '<circle cx="48" cy="48" r="6" fill="#6366f1"/></svg>'
)


@app.route("/favicon.ico")
def favicon():  # type: ignore[no-untyped-def]
    return _FAVICON, 200, {"Content-Type": "image/svg+xml"}


def create_app() -> Flask:
    """Factory hook for WSGI servers (gunicorn etc.)."""
    return app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
