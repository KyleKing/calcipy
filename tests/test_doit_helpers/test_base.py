"""Test doit_helpers/base.py."""

import shutil

import attr

from dash_dev.doit_helpers.base import DIG, DoItGlobals, _show_cmd, debug_task, if_found_unlink, task_export_req

from ..configuration import DIG_CWD, TEST_DATA_DIR


def test_dig_props():
    """Test the DIG global variable from DoItGlobals."""
    public_props = ['coverage_path', 'dash_dev_dir', 'doc_dir', 'excluded_files', 'external_doc_dirs', 'flake8_path',
                    'lint_paths', 'path_gitchangelog', 'pkg_name', 'set_paths', 'source_path', 'src_examples_dir',
                    'test_path', 'test_report_path', 'tmp_examples_dir', 'toml_path', 'template_dir', 'pkg_version']
    dig = DoItGlobals()

    result = [prop for prop in dir(dig) if not prop.startswith('_')]

    assert result == sorted(public_props)
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
    DIG.set_paths(source_path=DIG_CWD)

    result = task_export_req()

    assert result['actions'][0].startswith('poetry export -f requirements.txt')
