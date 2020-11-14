"""Test doit_helpers/test.py."""

from dash_dev.doit_helpers.base import DIG
from dash_dev.doit_helpers.test import task_test_marker

from ..configuration import DIG_CWD


def test_task_test_marker():
    """Test task_test_marker."""
    DIG.set_paths(source_path=DIG_CWD)

    result = task_test_marker()

    assert len(result['actions']) == 1
    assert result['actions'][0].startswith('poetry run pytest')
    assert len(result['params']) == 1
    assert result['params'][0]['name'] == 'marker'
    assert result['params'][0]['short'] == 'm'
