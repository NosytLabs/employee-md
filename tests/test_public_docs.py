"""Regression checks for public documentation claims, not schema enforcement."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = (ROOT / 'web/templates/index.html').read_text(encoding='utf-8')
BASE = (ROOT / 'web/templates/base.html').read_text(encoding='utf-8')


def test_homepage_distinguishes_validation_from_enforcement():
    assert 'Every field is enforceable' not in HOME
    assert 'Enforceable at runtime.' not in HOME
    assert 'not a sandbox' in HOME.lower()
    assert 'unknown' in HOME.lower()


def test_metadata_does_not_promise_automatic_enforcement():
    assert 'enforceable at runtime' not in BASE.lower()
    assert 'requires' in BASE.lower()


def test_homepage_has_no_static_passing_test_claim():
    assert 'tests passing' not in HOME.lower()
    assert '/actions' in HOME


def test_gallery_link_uses_the_same_example_count_as_the_stats():
    assert 'Browse {{ example_count }}' in HOME
    assert not re.search(r'Browse \d+ full examples', HOME)


def test_homepage_code_samples_and_main_are_keyboard_targets():
    blocks = re.findall(r'<pre\b[^>]*>', HOME)
    assert blocks
    assert all('tabindex="0"' in tag for tag in blocks)
    assert re.search(r'<main\b[^>]*id="main"[^>]*tabindex="-1"', BASE)
