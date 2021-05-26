"""Test doit_tasks/base.py."""

from pathlib import Path
from typing import Generator

from decorator import contextmanager
from doit.task import Task

from calcipy.doit_tasks.base import (
    _show_cmd, debug_task, delete_dir, ensure_dir, find_project_files, if_found_unlink, read_lines,
)
from calcipy.doit_tasks.doit_globals import DG

from ..configuration import PATH_TEST_PROJECT, TEST_DATA_DIR, TEST_DIR


@contextmanager
def temp_dg(path_project: Path = PATH_TEST_PROJECT) -> Generator[None, None, None]:
    """Temporarily change the DG project directory.

    Args:
        path_project: path to the project directory to pass to `DG`

    Yields:
        None: continues execution with the specified `path_project`

    """
    path_original = DG.meta.path_project
    if path_original != path_project:
        DG.set_paths(path_project=path_project)
        yield
        DG.set_paths(path_project=path_original)


def test_find_project_files():
    """Test find_project_files."""
    with temp_dg():

        result = find_project_files(DG.meta.path_project)

        assert len(result) != 0, f'Error: see {DG.meta.path_project}/README.md for configuring the directory'
        assert [*result.keys()] == ['yml', 'toml', '', 'md', 'cfg', 'yaml', 'py', 'ini']
        assert result[''][0].name == '.flake8'
        assert result[''][2].name == 'LICENSE'
        assert result['md'][0].relative_to(DG.meta.path_project).as_posix() == '.github/ISSUE_TEMPLATE/bug_report.md'


def test_read_lines():
    """Test read_lines."""
    result = read_lines(Path(__file__).resolve())

    assert result[0] == '"""Test doit_tasks/base.py."""'
    assert len(result) > 40


def test_dir_tools():
    """Test delete_dir & ensure_dir."""
    tmp_dir = TEST_DIR / '.tmp-test_delete_dir'
    tmp_dir.mkdir(exist_ok=True)
    (tmp_dir / 'tmp.txt').write_text('Placeholder\n')
    tmp_subdir = tmp_dir / 'subdir'

    ensure_dir(tmp_subdir)  # act

    assert tmp_subdir.is_dir()
    delete_dir(tmp_dir)
    assert not tmp_dir.is_dir()


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


def test_if_found_unlink():
    """Test if_found_unlink."""
    file_path = TEST_DATA_DIR / 'if_found_unlink-test_file.txt'

    file_path.write_text('')  # act

    assert file_path.is_file()
    if_found_unlink(file_path)
    assert not file_path.is_file()
