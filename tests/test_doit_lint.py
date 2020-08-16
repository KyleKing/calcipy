"""Test doit_lint.py."""

from dash_dev import doit_lint

from .configuration import DIG_CWD


def test_glob_path_list():
    """Test glob_path_list."""
    result = doit_lint.glob_path_list()

    assert len(result) == 2
    assert DIG_CWD / 'test_file.py' in result
    assert DIG_CWD / 'tests/test_file_2.py' in result
