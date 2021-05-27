"""Test doit_tasks/base.py."""

from doit.task import Task

from calcipy.doit_tasks.base import _show_cmd, debug_task


def test_show_cmd():
    """Test _show_cmd."""
    name = 'this_action'
    actions = ['123', 'abc']

    result = _show_cmd(Task(name=name, actions=actions))

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
