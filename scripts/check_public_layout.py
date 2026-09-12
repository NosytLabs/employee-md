"""Check actual Flask documentation pages without external network access.

Requests to a synthetic HTTPS origin are fulfilled by Flask's test client.
This exercises the real templates, local assets and copy handler, not a
public deployment, external-font service or operating-system clipboard.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from web.app import app  # noqa: E402

OUTPUT = Path(os.environ.get('DOCS_LAYOUT_OUTPUT', '/tmp/employee-docs-layout'))
ORIGIN = 'https://documentation.test'
PAGES = (('/', 'home'), ('/runtime', 'runtime'))


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    sources = []
    for name in ('web/templates/base.html', 'web/templates/index.html',
                 'web/templates/runtime.html', 'web/static/style.css',
                 'web/static/tailwind.css', 'runtime/employee.py'):
        content = (ROOT / name).read_bytes()
        target = OUTPUT / 'sources' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        sources.append(f'{hashlib.sha256(content).hexdigest()}  {name}')
    (OUTPUT / 'sources.sha256').write_text('\n'.join(sources) + '\n', encoding='utf-8')

    results = []
    with app.test_client() as client, sync_playwright() as p:
        def serve_local(route):
            request = route.request
            url = urlsplit(request.url)
            if f'{url.scheme}://{url.netloc}' != ORIGIN or request.method not in ('GET', 'HEAD'):
                route.abort()
                return
            path = url.path + ('?' + url.query if url.query else '')
            response = client.open(path, method=request.method, base_url=ORIGIN)
            route.fulfill(status=response.status_code, body=response.get_data(),
                          content_type=response.content_type)

        for path, name in PAGES:
            response = client.get(path, base_url=ORIGIN)
            assert response.status_code == 200, path
            (OUTPUT / f'rendered-{name}.html').write_text(response.get_data(as_text=True), encoding='utf-8')

        executable = os.environ.get('CHROMIUM_EXECUTABLE')
        browser = p.chromium.launch(**({'executable_path': executable} if executable else {}))
        try:
            for path, name in PAGES:
                for width in (320, 390, 768, 1440):
                    context = browser.new_context(viewport={'width': width, 'height': 900},
                                                  reduced_motion='reduce', service_workers='block')
                    context.grant_permissions(['clipboard-read', 'clipboard-write'], origin=ORIGIN)
                    context.route('**/*', serve_local)
                    page = context.new_page()
                    errors = []
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    checks = {}
                    positions = []
                    try:
                        response = page.goto(ORIGIN + path, wait_until='load')
                        checks['http_200'] = response is not None and response.status == 200
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

                        if name == 'runtime':
                            blocks = page.locator('.codeblock')
                            checks['three_code_examples'] = blocks.count() == 3
                            for index, block in enumerate(blocks.all(), start=1):
                                button = block.locator('button[data-copy]')
                                pre = block.locator('pre')
                                button_box = button.bounding_box()
                                code_box = pre.bounding_box()
                                checks[f'copy_{index}_clear_of_code'] = bool(button_box and code_box and button_box['y'] + button_box['height'] <= code_box['y'] + 1)
                                checks[f'copy_{index}_target_size'] = bool(button_box and button_box['width'] >= 44 and button_box['height'] >= 44)
                                expected = block.locator('pre code').text_content()
                                button.click()
                                expect(button).to_have_text('Copied!')
                                checks[f'copy_{index}_correct_text'] = page.evaluate('navigator.clipboard.readText()') == expected
                                pre.focus()
                                if pre.evaluate('(el) => el.scrollWidth > el.clientWidth + 1'):
                                    pre.press('ArrowRight')
                                    page.wait_for_function('(el) => el.scrollLeft > 0', arg=pre.element_handle())
                                checks[f'code_{index}_keyboard_scroll'] = True
                                pre.evaluate('(el) => {el.scrollLeft = 0}')

                        checks['no_browser_errors'] = not errors
                    except Exception as error:
                        checks['completed'] = False
                        errors.append(str(error))
                    finally:
                        page.evaluate('window.scrollTo(0, 0)')
                        page.screenshot(path=str(OUTPUT / f'{name}-{width}.png'), full_page=True, animations='disabled')
                        results.append({'page': path, 'width': width, 'checks': checks,
                                        'alignment_positions': positions, 'errors': errors})
                        context.close()
        finally:
            browser.close()

    (OUTPUT / 'results.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(results, indent=2))
    if not all(all(result['checks'].values()) for result in results):
        raise SystemExit('Documentation browser checks failed; inspect results.json and screenshots.')


if __name__ == '__main__':
    main()
