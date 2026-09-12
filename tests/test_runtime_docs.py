"""Published runtime guidance must match the implemented helper boundaries."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'web/templates/runtime.html').read_text(encoding='utf-8')
TEXT = re.sub(r'<[^>]+>', ' ', SOURCE)
TEXT = re.sub(r'\s+', ' ', TEXT)


def test_budget_guide_documents_invalid_values_and_unlimited_marker():
    assert 'finite, nonnegative' in TEXT
    assert 'ValueError' in TEXT
    assert 'None' in TEXT


def test_guardrail_guide_does_not_claim_token_matching_or_implicit_denial():
    assert 'substring + token check' not in TEXT
    assert 'Nonmatching actions are allowed' in TEXT
    assert 'lifecycle' in TEXT


def test_runtime_examples_are_keyboard_scroll_targets():
    blocks = re.findall(r'<pre\b[^>]*>', SOURCE)
    assert blocks
    assert all('tabindex="0"' in tag for tag in blocks)


def test_runtime_uses_existing_header_footer_gutters():
    assert 'max-w-5xl mx-auto px-5 sm:px-8' in SOURCE
