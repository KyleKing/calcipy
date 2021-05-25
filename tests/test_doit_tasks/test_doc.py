"""Test doit_tasks/doc.py."""

from calcipy.doit_tasks.doc import task_cl_bump, task_cl_bump_pre, task_cl_write
from calcipy.doit_tasks.doit_globals import DG

from ..configuration import PATH_TEST_PROJECT


def test_task_cl_write():
    """Test task_cl_write."""
    result = task_cl_write()

    actions = result['actions']
    assert len(actions) == 2
    assert actions[0] == 'poetry run cz changelog'
    assert '_move_cl' in str(actions[1][0])


def test_task_cl_bump():
    """Test task_cl_bump."""
    DG.set_paths(path_project=PATH_TEST_PROJECT)

    result = task_cl_bump()

    actions = result['actions']
    assert len(actions) == 3
    assert 'poetry run cz bump --changelog --annotated-tag' in str(actions[0])
    assert '_move_cl' in str(actions[1][0])
    assert actions[2] == 'git push origin --tags --no-verify'


def test_task_cl_bump_pre():
    """Test task_cl_bump_pre."""
    DG.set_paths(path_project=PATH_TEST_PROJECT)

    result = task_cl_bump_pre()

    actions = result['actions']
    assert len(actions) == 3
    assert 'poetry run cz bump --changelog --prerelease' in str(actions[0])
    assert '_move_cl' in str(actions[1][0])
    assert actions[2] == 'git push origin --tags --no-verify'
    params = result['params']
    assert len(params) == 1
    assert params[0]['name'] == 'prerelease'
    assert params[0]['short'] == 'p'
