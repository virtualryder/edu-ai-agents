"""Accessibility pre-flight: WCAG 2.1 AA failures in AI-generated content are caught."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from governance.accessibility import check_html, check_plain_language


def test_img_without_alt_flagged():
    assert not check_html('<img src="x.png">').passes


def test_img_with_alt_passes():
    assert check_html('<img src="x.png" alt="Campus map">').passes


def test_heading_skip_flagged():
    assert not check_html("<h1>Welcome</h1><h3>Aid</h3>").passes


def test_vague_link_flagged():
    assert not check_html('<a href="/x">click here</a>').passes


def test_descriptive_link_passes():
    assert check_html('<a href="/aid">View your financial-aid checklist</a>').passes


def test_plain_language_grade_passes_for_simple_text():
    assert check_plain_language("Bring your ID to the front office by 9 AM.").passes
