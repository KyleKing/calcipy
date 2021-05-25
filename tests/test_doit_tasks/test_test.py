"""Test doit_tasks/test.py."""

from calcipy.doit_tasks.doit_globals import DG
from calcipy.doit_tasks.test import task_test_marker

from ..configuration import PATH_TEST_PROJECT


def test_task_test_marker():
    """Test task_test_marker."""
    DG.set_paths(path_project=PATH_TEST_PROJECT)

    result = task_test_marker()

    actions = result['actions']
    assert len(actions) == 1
    assert ' -x -l --ff -v -m "%(marker)s"' in str(actions[0])
    params = result['params']
    assert len(params) == 1
    assert params[0]['name'] == 'marker'
    assert params[0]['short'] == 'm'
