"""Render actual Flask templates and check their offline responsive layout.

Uses repository-owned assets only; this is not a deployed-site or external-font
availability test. Evidence includes the exact templates and CSS used to render.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from web.app import app  # noqa: E402

OUTPUT = Path(os.environ.get('DOCS_LAYOUT_OUTPUT', '/tmp/employee-docs-layout'))


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    pages = []
    with app.test_client() as client:
        for route, name in (('/', 'home'), ('/runtime', 'runtime')):
            response = client.get(route)
            assert response.status_code == 200, route
            html = response.get_data(as_text=True)
            css = []
            for tag in re.findall(r'<link\b[^>]*>', html):
                if not re.search(r'rel=[\"\']stylesheet[\"\']', tag):
                    continue
                match = re.search(r'href=[\"\']([^\"\']+)', tag)
                if match and not urlsplit(match[1]).netloc:
                    asset = client.get(match[1])
                    assert asset.status_code == 200, match[1]
                    css.append(asset.get_data(as_text=True))
            assert css, f'No local styles were loaded from Flask for {route}'
            joined_css = '\n'.join(css)
            (OUTPUT / f'{name}-rendered.html').write_text(html, encoding='utf-8')
            (OUTPUT / f'{name}-rendered.css').write_text(joined_css, encoding='utf-8')
            pages.append((route, name, re.sub(r'<link\b[^>]*>', '', html), joined_css))
    sources = []
    for name in ('web/templates/base.html', 'web/templates/index.html', 'web/templates/runtime.html', 'web/static/style.css', 'web/static/tailwind.css'):
        content = (ROOT / name).read_bytes()
        target = OUTPUT / 'sources' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        sources.append(f'{hashlib.sha256(content).hexdigest()}  {name}')
    (OUTPUT / 'sources.sha256').write_text('\n'.join(sources) + '\n', encoding='utf-8')
    results = []
    with sync_playwright() as p:
        executable = os.environ.get('CHROMIUM_EXECUTABLE')
        browser = p.chromium.launch(**({'executable_path': executable} if executable else {}))
        try:
            for route, name, html, css in pages:
                for width in (320, 390, 768, 1440):
                    context = browser.new_context(viewport={'width': width, 'height': 900}, reduced_motion='reduce', service_workers='block')
                    context.route('**/*', lambda route: route.abort())
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.set_content(html)
                    page.add_style_tag(content=css)
                    page.screenshot(path=str(OUTPUT / f'{name}-{width}.png'), full_page=True, animations='disabled')
                    checks = {}
                    checks['one_heading'] = page.locator('h1').count() == 1
                    checks['no_page_overflow'] = page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
                    positions = page.evaluate('''() => [document.querySelector('header nav > a'), document.querySelector('h1'), document.querySelector('footer > div > div > span')].map(el => el.getBoundingClientRect().left)''')
                    checks['aligned'] = max(positions) - min(positions) < 2
                    page.keyboard.press('Tab')
                    checks['skip_first'] = page.locator('a[href="#main"]').evaluate('(el) => el === document.activeElement')
                    page.keyboard.press('Enter')
                    checks['skip_focuses_main'] = page.locator('#main').evaluate('(el) => el === document.activeElement')
                    checks['code_keyboard_targets'] = page.locator('main pre').evaluate_all('(els) => els.length > 0 && els.every(el => el.tabIndex === 0)')
                    checks['navigation_fits'] = page.locator('header a').evaluate_all('(els) => els.every(el => {const r=el.getBoundingClientRect();return r.left>=0 && r.right<=innerWidth+1})')
                    checks['no_browser_errors'] = not errors
                    results.append({'route': route, 'width': width, 'checks': checks, 'alignment_positions': positions, 'errors': errors})
                    context.close()
        finally:
            browser.close()
    (OUTPUT / 'results.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(results, indent=2))
    if not all(all(result['checks'].values()) for result in results):
        raise SystemExit('Public documentation layout checks failed; see results.json and screenshots.')


if __name__ == '__main__':
    main()
