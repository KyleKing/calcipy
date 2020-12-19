"""Test doit_helpers/base.py."""

from typing import Any, List

import attr

from calcipy.doit_helpers.base import _show_cmd, debug_task, if_found_unlink, task_export_req
from calcipy.doit_helpers.doit_globals import DIG, DoItGlobals

from ..configuration import DIG_CWD, TEST_DATA_DIR


def _get_public_props(obj: Any) -> List[str]:
    return [prop for prop in dir(obj) if not prop.startswith('_')]


def test_dig_props():
    """Test the DIG global variable from DoItGlobals."""
    public_props = ['calcipy_dir', 'set_paths']
    settable_props = public_props + ['meta', 'lint', 'test', 'doc']

    dig = DoItGlobals()  # act

    assert _get_public_props(dig) == sorted(public_props)
    dig.set_paths(path_source=DIG_CWD)
    assert _get_public_props(dig) == sorted(settable_props)


def test_dig_paths():
    """Test the DIG global variable from DoItGlobals."""
    dig = DoItGlobals()
    pkg_name = DIG_CWD.name

    dig.set_paths(path_source=DIG_CWD)  # act

    # Test the properties set by default
    assert dig.calcipy_dir.name == 'calcipy'
    assert dig.lint.path_flake8 == DIG_CWD / '.flake8'
    assert dig.doc.path_changelog == dig.calcipy_dir / '.gitchangelog.rc'
    # Test the properties set by set_paths
    assert dig.meta.path_source == DIG_CWD
    assert dig.meta.path_toml == DIG_CWD / 'pyproject.toml'
    assert dig.meta.pkg_name == pkg_name
    assert dig.doc.path_out == DIG_CWD / 'docs'


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
    DIG.set_paths(path_source=DIG_CWD)

    result = task_export_req()

    assert result['actions'][0].startswith('poetry export -f requirements.txt')
