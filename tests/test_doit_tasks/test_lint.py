"""Test doit_tasks/lint.py."""


import pytest

from calcipy.doit_tasks.doit_globals import get_dg
from calcipy.doit_tasks.lint import (
    _check_linting_errors, _lint_python, task_auto_format, task_lint_critical_only,
    task_lint_project, task_lint_python, task_pre_commit_hooks, task_radon_lint,
)

from ..configuration import PATH_TEST_PROJECT


def test_lint_python(assert_against_cache):
    """Test _lint_python."""
    result = _lint_python(
        lint_paths=[PATH_TEST_PROJECT / 'test_file.py', PATH_TEST_PROJECT / 'tests/test_file_2.py'],
        path_flake8=get_dg().lint.path_flake8,
        ignore_errors=['F401', 'E800', 'I001', 'I003'],
    )

    assert_against_cache(result)


FLAKE8_LOG = """doit_project/test_file.py:3:1: F401 'doit' imported but unused
doit_project/test_file.py:3:1: I001 isort found an import in the wrong position
doit_project/test_file.py:4:1: F401 'pathlib.Path' imported but unused
doit_project/test_file.py:6:1: I003 isort expected 1 blank line in imports, found 0
doit_project/test_file.py:6:2: E800: Found commented out code
"""


def test_check_linting_errors(fix_test_cache):
    """Test check_linting_errors."""
    flake8_log_path = fix_test_cache / 'flake8.log'
    flake8_log_path.write_text(FLAKE8_LOG)

    _check_linting_errors(flake8_log_path, ignore_errors=['F401', 'I001', 'I003', 'E800'])  # act

    assert not flake8_log_path.is_file()


def test_check_linting_errors_runtime_error(fix_test_cache):
    """Test check_linting_errors."""
    flake8_log_path = fix_test_cache / 'flake8.log'
    flake8_log_path.write_text(FLAKE8_LOG)

    with pytest.raises(RuntimeError):
        _check_linting_errors(flake8_log_path, ignore_errors=[])

    assert flake8_log_path.read_text() == FLAKE8_LOG


def test_task_lint_python(assert_against_cache):
    """Test task_lint_python."""
    result = task_lint_python()

    assert_against_cache(result)


def test_task_lint_project(assert_against_cache):
    """Test task_lint_project."""
    result = task_lint_project()

    assert_against_cache(result)


def test_task_lint_critical_only(assert_against_cache):
    """Test task_lint_critical_only."""
    result = task_lint_critical_only()

    assert_against_cache(result)


def test_task_radon_lint(assert_against_cache):
    """Test task_radon_lint."""
    result = task_radon_lint()

    assert_against_cache(result)


def test_task_auto_format(assert_against_cache):
    """Test task_auto_format."""
    result = task_auto_format()

    assert_against_cache(result)


def test_task_pre_commit_hooks(assert_against_cache):
    """Test task_pre_commit_hooks."""
    result = task_pre_commit_hooks()

    assert_against_cache(result)
