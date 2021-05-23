"""Test file_helpers."""

from calcipy.file_helpers import sanitize_filename


def test_sanitize_filename():
    """Test sanitize_filename."""
    result = sanitize_filename('_dash-09-ϑ//.// SUPER.py')

    assert result == '_dash-09-___.___SUPER.py'
