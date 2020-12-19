"""Test doit_tasks/doc.py."""

import os
from pathlib import Path

from calcipy.doit_tasks.doc import task_tag_create, task_tag_remove, task_update_cl
from calcipy.doit_tasks.doit_globals import DIG

from ..configuration import DIG_CWD


def test_task_update_cl():
    """Test task_update_cl."""
    result = task_update_cl()

    assert len(result['actions']) == 1
    assert Path(os.environ['GITCHANGELOG_CONFIG_FILENAME']) == DIG.doc.path_changelog
    assert result['actions'][0] == 'gitchangelog > CHANGELOG-raw.md'


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
