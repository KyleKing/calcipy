"""Test doit_base.py."""

import shutil
from collections import namedtuple

from dash_dev import doit_base
from dash_dev.doit_base import DIG, DoItGlobals

from .configuration import DIG_CWD, TEST_DATA_DIR


def test_dig_props():
    """Test the DIG global variable from DoItGlobals."""
    public_props = ['coverage_path', 'dash_dev_dir', 'doc_dir', 'excluded_files', 'external_doc_dirs', 'flake8_path',
                    'lint_paths', 'path_gitchangelog', 'pkg_name', 'set_paths', 'source_path', 'src_examples_dir',
                    'test_path', 'test_report_path', 'tmp_examples_dir', 'toml_path']
    dig = DoItGlobals()

    result = [prop for prop in dir(dig) if not prop.startswith('_')]

    assert result == public_props
    assert dir(dig) == dir(DIG)


def test_dig_paths():
    """Test the DIG global variable from DoItGlobals."""
    dig = DoItGlobals()
    pkg_name = DIG_CWD.name
    src_examples_dir = DIG_CWD / 'tests/examples'
    if src_examples_dir.is_dir():
        shutil.rmtree(src_examples_dir)

    dig.set_paths(source_path=DIG_CWD)  # act

    # Test the properties set by default
    assert dig.dash_dev_dir.name == 'dash_dev'
    assert dig.flake8_path == DIG_CWD / '.flake8'
    assert dig.path_gitchangelog == dig.dash_dev_dir / '.gitchangelog.rc'
    # Test the properties set by set_paths
    assert dig.source_path == DIG_CWD
    assert dig.toml_path == DIG_CWD / 'pyproject.toml'
    assert dig.pkg_name == pkg_name
    assert dig.doc_dir == DIG_CWD / 'docs'
    assert dig.src_examples_dir is None
    assert dig.tmp_examples_dir == DIG_CWD / f'{pkg_name}/0EX'
    # Create src_examples_dir and ensure that the property is updated
    src_examples_dir.mkdir(parents=True)
    dig.set_paths(source_path=DIG_CWD)
    assert dig.src_examples_dir == src_examples_dir
    shutil.rmtree(src_examples_dir)


def test_show_cmd():
    """Test show_cmd."""
    task_tuple = namedtuple('task_tuple', ('name', 'actions'))
    name = 'this_action'
    actions = [123, 'abc']
    task = task_tuple(name, actions)

    result = doit_base.show_cmd(task)

    assert f'{name} > ' in result
    assert all(str(act) in result for act in actions)


def test_debug_action():
    """Test debug_action."""
    actions = ['123']
    verbosity = 1

    result = doit_base.debug_action(actions, verbosity)

    assert all(key in result for key in ['actions', 'title', 'verbosity'])
    assert result['actions'] == actions
    assert result['verbosity'] == verbosity


def test_if_found_unlink():
    """Test if_found_unlink."""
    file_path = TEST_DATA_DIR / 'if_found_unlink-test_file.txt'

    file_path.write_text('')  # act

    assert file_path.is_file()
    doit_base.if_found_unlink(file_path)
    assert not file_path.is_file()


def test_task_export_req():
    """Test task_export_req."""
    DIG.set_paths(source_path=DIG_CWD)

    result = doit_base.task_export_req()

    assert result['actions'][0].startswith('poetry export -f requirements.txt')


def test_task_check_req():
    """Test task_check_req."""
    DIG.set_paths(source_path=DIG_CWD)

    result = doit_base.task_check_req()

    assert result['actions'][0].startswith('poetry run pur')
    assert len(result['actions']) == 3
