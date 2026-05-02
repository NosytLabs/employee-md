#!/usr/bin/env python3
"""Snapshot the Flask site to a static `dist/` tree for GitHub Pages.

Walks every public route via Flask's test client, copies static assets,
and rewrites root-relative URLs so the site works under a subdirectory
(default `/employee-md/`, override with the `BASE_PATH` env var, set to
empty string when serving from a custom-domain root).

The dynamic /api/validate endpoint cannot run on GitHub Pages, so the
snapshot replaces the /validate page with install-the-CLI instructions.
The interactive validator stays available on the Replit/Vercel deploy.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from web.app import app, EXAMPLES  # noqa: E402

DIST = ROOT / "dist"
BASE_PATH = os.environ.get("BASE_PATH", "/employee-md").rstrip("/")
LIVE_VALIDATOR_URL = os.environ.get("LIVE_VALIDATOR_URL", "")
CANONICAL_ORIGIN = os.environ.get(
    "CANONICAL_ORIGIN", "https://nosytlabs.github.io"
).rstrip("/")


def routes() -> list[str]:
    paths = [
        "/", "/why", "/spec", "/examples", "/validate", "/runtime",
        "/integration", "/integrations", "/docs", "/healthz",
        "/robots.txt", "/sitemap.xml", "/pygments.css", "/favicon.ico",
    ]
    paths += [f"/examples/{ex['slug']}" for ex in EXAMPLES]
    return paths


def output_path(route: str) -> Path:
    if route == "/":
        return DIST / "index.html"
    if "." in route.rsplit("/", 1)[-1]:
        return DIST / route.lstrip("/")
    return DIST / route.strip("/") / "index.html"


_URL_ATTR_RE = re.compile(r'(?P<attr>\b(?:href|src|action))="(?P<url>/[^"]*)"')


def rewrite_urls(html: str) -> str:
    # Always strip the test-client's localhost origin so canonical/og URLs
    # don't leak into the snapshot.
    html = html.replace("http://localhost", f"{CANONICAL_ORIGIN}{BASE_PATH}")
    if not BASE_PATH:
        return html
    def sub(m: re.Match[str]) -> str:
        url = m.group("url")
        # Skip protocol-relative ("//cdn...") and absolute-ish leftovers.
        if url.startswith("//"):
            return m.group(0)
        # Don't double-prefix.
        if url.startswith(BASE_PATH + "/") or url == BASE_PATH:
            return m.group(0)
        return f'{m.group("attr")}="{BASE_PATH}{url}"'
    return _URL_ATTR_RE.sub(sub, html)


VALIDATOR_SHIM_LIVE_BLOCK = """\
    <li>
      <div class="text-white font-semibold">1. Use the hosted validator</div>
      <p class="text-ink-300 mt-1">Same code, running on a Python server:</p>
      <a href="__LIVE__"
         class="inline-block mt-2 bg-brand hover:bg-brand-dark text-white font-semibold px-4 py-2 rounded-lg">
        Open the live validator &rarr;
      </a>
    </li>
    <li>
      <div class="text-white font-semibold">2. Run it locally from the CLI</div>
"""

VALIDATOR_SHIM_CLI_ONLY_BLOCK = """\
    <li>
      <div class="text-white font-semibold">Install and run the CLI</div>
"""

VALIDATOR_SHIM_HEAD = """\
{% extends "base.html" %}
{% block title %}Validate · employee.md{% endblock %}
{% block content %}
<div class="max-w-3xl mx-auto px-4 sm:px-6 pt-12 pb-20">
  <div class="text-xs font-mono text-ink-500 mb-2">VALIDATOR</div>
  <h1 class="text-3xl sm:text-4xl font-bold text-white">Run the validator locally</h1>
  <p class="mt-4 text-ink-300">
    The interactive validator needs a Python backend, so it doesn't run on
    this static GitHub Pages snapshot. Install the CLI to validate any
    <code>employee.md</code> in seconds:
  </p>
  <ol class="mt-6 space-y-6 text-ink-200">
__BODY__
<pre class="mt-2 bg-ink-900 border border-ink-700 rounded-lg p-4 text-sm font-mono text-ink-100 overflow-x-auto"><code>pip install -e git+https://github.com/NosytLabs/employee-md.git#egg=employee-md
employee-validate path/to/employee.md
employee-validate path/to/employee.md --format json</code></pre>
    </li>
  </ol>
  <p class="mt-8 text-sm text-ink-500">
    Everything else on this site &mdash; spec reference, examples, integration
    guide, runtime SDK docs &mdash; works fully on GitHub Pages.
  </p>
</div>
{% endblock %}
"""


def render_static_validator() -> str:
    """Render the validator shim through Jinja so it inherits the base layout."""
    from flask import render_template_string
    if LIVE_VALIDATOR_URL:
        body_block = VALIDATOR_SHIM_LIVE_BLOCK.replace("__LIVE__", LIVE_VALIDATOR_URL)
    else:
        body_block = VALIDATOR_SHIM_CLI_ONLY_BLOCK
    with app.app_context(), app.test_request_context("/validate"):
        body = VALIDATOR_SHIM_HEAD.replace("__BODY__", body_block)
        return render_template_string(body)


def main() -> int:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    static_src = ROOT / "web" / "static"
    if static_src.is_dir():
        shutil.copytree(static_src, DIST / "static")

    client = app.test_client()
    snapped = 0
    failed: list[tuple[str, int]] = []

    for route in routes():
        if route == "/validate":
            html = rewrite_urls(render_static_validator())
            out = output_path(route)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(html, encoding="utf-8")
            snapped += 1
            print(f"  STATIC  {route}  -> {out.relative_to(ROOT)}")
            continue

        resp = client.get(route)
        if resp.status_code != 200:
            failed.append((route, resp.status_code))
            print(f"  FAIL    {route}  ({resp.status_code})")
            continue

        body = resp.get_data()
        ctype = resp.headers.get("Content-Type", "")
        if any(t in ctype for t in ("text/html", "xml", "text/plain", "css")):
            try:
                body = rewrite_urls(body.decode("utf-8")).encode("utf-8")
            except UnicodeDecodeError:
                pass

        out = output_path(route)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(body)
        snapped += 1
        print(f"  OK      {route}  -> {out.relative_to(ROOT)}")

    nojekyll = DIST / ".nojekyll"
    nojekyll.write_text("", encoding="utf-8")

    print(f"\nSnapshot complete: {snapped} pages, {len(failed)} failed")
    print(f"  base path: {BASE_PATH or '/ (root)'}")
    print(f"  output:    {DIST.relative_to(ROOT)}/")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
