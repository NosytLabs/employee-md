"""Runtime documentation matches helper behavior; no providers are called."""
import ast
from html import unescape
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = (ROOT / 'web/templates/runtime.html').read_text(encoding='utf-8')


def test_runtime_reference_discloses_literal_matching_and_separate_checks():
    assert 'literal substring' in PAGE
    assert 'does not check lifecycle, scope or permissions' in PAGE
    assert 'substring + token' not in PAGE
    assert 'fail closed before you call the LLM' not in PAGE
    assert 'not a sandbox' in PAGE


def test_budget_reference_describes_invalid_numbers_and_storage_limits():
    assert 'finite, non-negative' in PAGE
    assert 'ValueError' in PAGE
    assert 'None is the only uncapped setting' in PAGE
    assert 'in-process floating-point' in PAGE


def test_code_examples_have_distinct_keyboard_labels_and_parse():
    blocks = re.findall(r'<pre\b([^>]*)><code>([\s\S]*?)</code></pre>', PAGE)
    assert len(blocks) == 3
    labels = []
    for attrs, code in blocks:
        assert 'tabindex="0"' in attrs
        label = re.search(r'aria-label="([^"]+)"', attrs)
        assert label
        labels.append(label[1])
        if '{{' not in code:
            ast.parse(unescape(code))
    assert len(set(labels)) == len(labels)


def test_execution_example_checks_lifecycle_scope_and_prohibition_explicitly():
    assert 'if not emp.is_active:' in PAGE
    assert 'if not emp.is_in_scope(' in PAGE
    assert 'if not emp.is_action_allowed(action_id):' in PAGE
    assert 'Apply tool permissions/sandbox policy' in PAGE
    assert 'in three lines' not in PAGE
