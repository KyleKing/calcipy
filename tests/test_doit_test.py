"""Test doit_test.py."""

from dash_dev import doit_test
from dash_dev.doit_base import DIG

from .configuration import DIG_CWD


def test_task_test_marker():
    """Test task_test_marker."""
    DIG.set_paths(source_path=DIG_CWD)

    result = doit_test.task_test_marker()

    assert len(result['actions']) == 1
    assert result['actions'][0].startswith('poetry run pytest')
    assert len(result['params']) == 1
    assert result['params'][0]['name'] == 'marker'
    assert result['params'][0]['short'] == 'm'
