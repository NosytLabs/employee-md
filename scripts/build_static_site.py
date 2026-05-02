#!/usr/bin/env python3
"""Snapshot the Flask site to a static `dist/` tree for GitHub Pages.

Walks every public route via Flask's test client, copies static assets,
and rewrites root-relative URLs so the site works under a subdirectory
(default `/employee-md/`, override with the `BASE_PATH` env var, set to
empty string when serving from a custom-domain root).

The site is fully static — no Python backend is required at runtime.
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
CANONICAL_ORIGIN = os.environ.get(
    "CANONICAL_ORIGIN", "https://nosytlabs.github.io"
).rstrip("/")


def routes() -> list[str]:
    paths = [
        "/", "/why", "/spec", "/examples", "/runtime",
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
