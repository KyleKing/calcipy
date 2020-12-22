"""Test doit_tasks/test.py."""

import pytest

from calcipy.doit_tasks.doit_globals import DIG
from calcipy.doit_tasks.test import task_test_marker

from ..configuration import PATH_TEST_PROJECT


def test_task_test_marker():
    """Test task_test_marker."""
    pytest.skip('Needs to be updated for LongRunning')
    DIG.set_paths(path_source=PATH_TEST_PROJECT)

    result = task_test_marker()

    assert len(result['actions']) == 1
    assert result['actions'][0].startswith('poetry run pytest')
    assert len(result['params']) == 1
    assert result['params'][0]['name'] == 'marker'
    assert result['params'][0]['short'] == 'm'
