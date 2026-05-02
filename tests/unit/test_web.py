"""Flask test-client coverage for the website endpoints.

These lock down the contracts the architect flagged as good-to-have:
  - /api/validate ALWAYS returns JSON (never an HTML 500), even on
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
        "/", "/spec", "/examples", "/validate", "/runtime", "/docs",
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
    import json
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
    for label in ["Home", "Spec", "Examples", "Validate", "Runtime",
                  "Integration guide", "Docs"]:
        assert label in body, f"Missing nav label: {label}"


# ---- /api/validate happy path -------------------------------------------

MINIMAL_YAML = """\
spec:
  name: "employee.md"
  version: "1.0.0"
  kind: "agent-employment"
role:
  title: "Worker"
  level: "senior"
mission:
  purpose: "Do the work."
guardrails:
  prohibited_actions:
    - "delete production database"
economy:
  budget_limit: 1.50
  currency: "USD"
lifecycle:
  status: "active"
"""


def _post_validate(client, yaml_body):
    return client.post(
        "/api/validate",
        data=json.dumps({"yaml": yaml_body}),
        content_type="application/json",
    )


def test_api_validate_happy_returns_system_prompt(client):
    resp = _post_validate(client, MINIMAL_YAML)
    assert resp.status_code == 200
    assert resp.is_json
    body = resp.get_json()
    assert body["valid"] is True
    assert body["error_count"] == 0
    assert isinstance(body.get("system_prompt"), str)
    assert "MISSION" in body["system_prompt"]
    assert "BUDGET" in body["system_prompt"]


def test_api_validate_invalid_returns_json_with_errors(client):
    resp = _post_validate(client, "spec:\n  name: 'employee.md'\n")
    assert resp.status_code == 200
    assert resp.is_json
    body = resp.get_json()
    assert body["valid"] is False
    assert body["error_count"] >= 1
    # No system prompt for invalid contracts.
    assert body.get("system_prompt") is None


# ---- /api/validate must NEVER 500 on bad input --------------------------

@pytest.mark.parametrize(
    "yaml_body",
    [
        "",                                    # empty
        "   \n\n",                             # whitespace
        "not: valid: yaml: at all: 5: 6: 7",  # malformed
        "[1, 2, 3]",                           # top-level list
        "just-a-string",                       # top-level scalar
        "role: 5\nlifecycle: { status: 'active' }",        # wrong section shape
        "lifecycle: 'not-a-mapping'",          # required section wrong type
    ],
)
def test_api_validate_never_500s(client, yaml_body):
    resp = _post_validate(client, yaml_body)
    # Either 200 (validated, with errors) or 413 (oversized) — never 500.
    assert resp.status_code in (200, 413), (
        f"got {resp.status_code} for input: {yaml_body!r}"
    )
    assert resp.is_json, f"non-JSON response for input: {yaml_body!r}"


def test_api_validate_bad_shape_role_5_returns_200_invalid(client):
    """A wrong-typed `role: 5` payload must come back as HTTP 200 with
    `valid: false` — never a 500, never a 413, never a silent pass."""
    resp = _post_validate(
        client, "role: 5\nlifecycle:\n  status: 'active'\n"
    )
    assert resp.status_code == 200
    assert resp.is_json
    body = resp.get_json()
    assert body["valid"] is False
    assert body["error_count"] >= 1


def test_api_validate_oversized_returns_413_json(client):
    big = "spec:\n  name: 'x'\n" + ("# pad\n" * 200_000)
    resp = _post_validate(client, big)
    assert resp.status_code == 413
    assert resp.is_json


def test_api_validate_non_string_input(client):
    resp = client.post(
        "/api/validate",
        data=json.dumps({"yaml": 42}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert resp.is_json
    body = resp.get_json()
    assert body["valid"] is False


# ---- XSS / injection in error messages and system prompt ----------------

def test_api_validate_xss_in_error_messages_not_pre_escaped(client):
    """Server returns raw text in errors; client-side escapeHtml() is the
    second line of defense. This test pins down that the server does NOT
    pre-escape (otherwise the validator output gets double-escaped when
    rendered into the DOM via .textContent / escapeHtml())."""
    payload = (
        "role:\n"
        "  title: \"x\"\n"
        "  level: \"<script>alert(1)</script>\"\n"
        "lifecycle:\n"
        "  status: \"active\"\n"
    )
    resp = _post_validate(client, payload)
    assert resp.is_json
    body = resp.get_json()
    assert body["valid"] is False
    serialized = json.dumps(body)
    # The bad enum value should be echoed verbatim in the error message
    # — not pre-escaped to &lt;script&gt;.
    assert "<script>" in serialized
    assert "&lt;script&gt;" not in serialized


def test_api_validate_xss_in_system_prompt_carried_through(client):
    """The runtime SDK passes role.title through verbatim into the
    system prompt. The browser-side escapeHtml() in validate.html is what
    keeps the prompt from rendering as HTML — verify the JSON carries
    the literal characters."""
    yaml_with_html = """\
spec: { name: "employee.md", version: "1.0.0", kind: "agent-employment" }
role:
  title: "<img src=x onerror=alert(1)>"
  level: "senior"
mission:
  purpose: "ok"
lifecycle:
  status: "active"
"""
    resp = _post_validate(client, yaml_with_html)
    assert resp.is_json
    body = resp.get_json()
    if body["valid"]:
        sp = body.get("system_prompt") or ""
        # Literal characters present (not pre-escaped server-side).
        assert "<img" in sp or "onerror" in sp
