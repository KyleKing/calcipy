"""Test doit_tasks/base.py."""

import attr

from calcipy.doit_tasks.base import _show_cmd, debug_task, if_found_unlink, task_export_req
from calcipy.doit_tasks.doit_globals import DIG

from ..configuration import PATH_TEST_PROJECT, TEST_DATA_DIR


def test_show_cmd():
    """Test show_cmd."""
    task = attr.make_class('task', ('name', 'actions'))
    name = 'this_action'
    actions = [123, 'abc']

    result = _show_cmd(task(name, actions))

    assert f'{name} > ' in result
    assert all(str(act) in result for act in actions)


def test_debug_task():
    """Test debug_task."""
    actions = ['123']
    verbosity = 1

    result = debug_task(actions, verbosity)

    assert all(key in result for key in ['actions', 'title', 'verbosity'])
    assert result['actions'] == actions
    assert result['verbosity'] == verbosity


def test_if_found_unlink():
    """Test if_found_unlink."""
    file_path = TEST_DATA_DIR / 'if_found_unlink-test_file.txt'

    file_path.write_text('')  # act

    assert file_path.is_file()
    if_found_unlink(file_path)
    assert not file_path.is_file()


def test_task_export_req():
    """Test task_export_req."""
    DIG.set_paths(path_source=PATH_TEST_PROJECT)

    result = task_export_req()

    assert result['actions'][0].startswith('poetry export -f requirements.txt')
