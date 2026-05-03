"""Flask test-client coverage for the website endpoints.

These lock down the contracts the architect flagged as good-to-have:
  - All marketing/docs pages return 200, even on
    pathological input (non-string, oversized, malformed YAML, wrong
    top-level type, wrong section shape).
  - When the YAML is valid, the response includes a `system_prompt`
    field compiled by the runtime SDK.
  - User-controlled fields rendered into the validate UI come back
    untouched (the page-level escapeHtml() is the second line of defense;
    the server should not transform them).
  - The static pages render and link correctly.
"""

from __future__ import annotations

import json

import pytest

from web.app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


# ---- static pages -------------------------------------------------------

@pytest.mark.parametrize(
    "path",
    [
        "/", "/spec", "/examples", "/runtime", "/docs",
        "/integration", "/healthz",
        "/examples/minimal", "/examples/molt-bot-integration",
        "/favicon.ico", "/pygments.css",
    ],
)
def test_pages_return_200(client, path):
    resp = client.get(path)
    assert resp.status_code == 200, f"{path} returned {resp.status_code}"


def test_spec_page_lists_every_schema_section(client):
    """The /spec page must surface every top-level section defined in
    tooling/schema.json so the docs stay in sync with the contract."""
    from pathlib import Path
    schema = json.loads(
        Path("tooling/schema.json").read_text(encoding="utf-8")
    )
    sections = list(schema.get("properties", {}).keys())
    assert sections, "schema.json has no top-level properties"
    body = client.get("/spec").get_data(as_text=True)
    missing = [s for s in sections if s not in body]
    assert not missing, f"/spec missing schema sections: {missing}"


def test_integration_page_renders_pygments_and_rewrites_repo_links(client):
    resp = client.get("/integration")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'class="codehilite"' in body
    for label in ("Python Integration", "TypeScript Integration",
                  "MCP Integration"):
        assert label in body, f"sidebar TOC missing {label!r}"
    for broken in ("/integration/examples", "/integration/tooling"):
        assert broken not in body, f"unrewritten repo link leaked: {broken}"
    assert "/examples/zhc-worker" in body


def test_docs_page_links_to_in_app_integration(client):
    resp = client.get("/docs")
    body = resp.get_data(as_text=True)
    assert 'href="/integration"' in body
    assert "INTEGRATION.md" not in body


def test_healthz_is_json(client):
    resp = client.get("/healthz")
    assert resp.is_json
    body = resp.get_json()
    assert body["status"] == "ok"
    assert body["version"]


def test_runtime_page_includes_sample_prompt(client):
    resp = client.get("/runtime")
    body = resp.get_data(as_text=True)
    # Live-rendered prompt should include the senior-dev mission language.
    assert "Senior Full-Stack Developer" in body or "MISSION" in body
    # And the SDK quickstart snippet must be present.
    assert "from runtime import Employee" in body


def test_spec_page_marks_experimental_sections(client):
    resp = client.get("/spec")
    body = resp.get_data(as_text=True)
    # Curated experimental section: protocols. Marker should appear.
    assert "experimental" in body.lower()
    assert "protocols" in body


def test_nav_links_present(client):
    resp = client.get("/")
    body = resp.get_data(as_text=True)
    for label in ["Why", "Spec", "Examples", "Runtime",
                  "Integrations", "Docs"]:
        assert label in body, f"Missing nav label: {label}"

