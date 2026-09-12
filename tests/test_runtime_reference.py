"""Runtime-page controls are accessible without overstating executor guarantees."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / 'web/templates/runtime.html').read_text(encoding='utf-8')
CSS = (ROOT / 'web/static/style.css').read_text(encoding='utf-8')


def test_code_examples_have_distinct_keyboard_labels():
    blocks = re.findall(r'<pre\b([^>]*)><code>', PAGE)
    assert len(blocks) == 3
    labels = []
    for attrs in blocks:
        assert 'tabindex="0"' in attrs
        label = re.search(r'aria-label="([^"]+)"', attrs)
        assert label
        labels.append(label[1])
    assert len(set(labels)) == len(labels)


def test_copy_controls_have_distinct_accessible_names():
    buttons = re.findall(r'<button\b([^>]*)data-copy([^>]*)>', PAGE)
    assert len(buttons) == 3
    labels = []
    for before, after in buttons:
        label = re.search(r'aria-label="([^"]+)"', before + after)
        assert label
        labels.append(label[1])
    assert len(set(labels)) == 3


def test_reference_layout_changes_are_scoped_to_its_body_class():
    assert '{% block page_class %}page-runtime{% endblock %}' in PAGE
    assert '.page-runtime .codeblock .copy-btn' in CSS
    assert '.page-runtime main pre:focus-visible' in CSS


def test_existing_compatibility_and_enforcement_limits_remain_visible():
    assert 'invalid explicit limits previously could become unlimited' in PAGE
    assert 'in-process floating-point tracker' in PAGE
    assert 'not a sandbox' in PAGE
    assert 'tool ACLs and required approvals' in PAGE
