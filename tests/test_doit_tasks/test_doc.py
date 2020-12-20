"""Test doit_tasks/doc.py."""

from calcipy.doit_tasks.doc import task_tag_create, task_tag_remove, task_cl_write
from calcipy.doit_tasks.doit_globals import DIG

from ..configuration import DIG_CWD


def test_task_cl_write():
    """Test task_cl_write."""
    result = task_cl_write()

    assert len(result['actions']) == 1
    assert result['actions'][0] == 'poetry run cz changelog'


def test_task_tag_create():
    """Test task_tag_create."""
    DIG.set_paths(path_source=DIG_CWD)

    result = task_tag_create()

    assert len(result['actions']) == 3
    assert result['actions'][0].startswith('git tag -a')
    assert result['actions'][1] == 'git tag -n10 --list'
    assert result['actions'][2] == 'git push origin --tags'


def test_task_tag_remove():
    """Test task_tag_remove."""
    DIG.set_paths(path_source=DIG_CWD)

    result = task_tag_remove()

    assert len(result['actions']) == 3
    assert result['actions'][0].startswith('git tag -d')
    assert result['actions'][1] == 'git tag -n10 --list'
    assert result['actions'][2].startswith('git push origin :refs/tags/')
