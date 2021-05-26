"""Test doit_tasks/doc.py."""

from calcipy.doit_tasks.doc import _move_cl, task_cl_bump, task_cl_bump_pre, task_cl_write


def test_task_cl_write():
    """Test task_cl_write."""
    result = task_cl_write()

    actions = result['actions']
    assert len(actions) == 2
    assert actions[0] == 'poetry run cz changelog'
    assert isinstance(actions[1][0], type(_move_cl))


def test_task_cl_bump():
    """Test task_cl_bump."""
    result = task_cl_bump()

    actions = result['actions']
    assert len(actions) == 3
    assert 'poetry run cz bump --changelog --annotated-tag' in str(actions[0])
    assert isinstance(actions[1][0], type(_move_cl))
    assert actions[2] == 'git push origin --tags --no-verify'


def test_task_cl_bump_pre():
    """Test task_cl_bump_pre."""
    result = task_cl_bump_pre()

    actions = result['actions']
    assert len(actions) == 3
    assert 'poetry run cz bump --changelog --prerelease' in str(actions[0])
    assert isinstance(actions[1][0], type(_move_cl))
    assert actions[2] == 'git push origin --tags --no-verify'
    params = result['params']
    assert len(params) == 1
    assert params[0]['name'] == 'prerelease'
    assert params[0]['short'] == 'p'
