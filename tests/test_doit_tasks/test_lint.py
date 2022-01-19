"""Test doit_tasks/lint.py."""

import pytest

from calcipy.doit_tasks.base import echo
from calcipy.doit_tasks.doit_globals import DG
from calcipy.doit_tasks.lint import (
    _check_linting_errors, _lint_python, task_auto_format, task_lint_critical_only,
    task_lint_project, task_lint_python, task_pre_commit_hooks, task_radon_lint,
)
from calcipy.file_helpers import if_found_unlink

from ..configuration import PATH_TEST_PROJECT


def test_lint_python():
    """Test _lint_python."""
    result = _lint_python(
        lint_paths=[PATH_TEST_PROJECT / 'test_file.py', PATH_TEST_PROJECT / 'tests/test_file_2.py'],
        path_flake8=DG.lint.path_flake8,
        ignore_errors=['F401', 'E800', 'I001', 'I003'],
    )

    assert len(result) == 5
    assert isinstance(result[0][0], type(if_found_unlink))
    assert result[0][1][0].name == 'flake8.log'
    assert str(result[1]).startswith('Cmd: poetry run python -m flake8 --config')
    assert 'test_file.py' in str(result[1])
    assert isinstance(result[2][0], type(_check_linting_errors))


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


def test_task_lint_python():
    """Test task_lint_python."""
    result = task_lint_python()

    actions = result['actions']
    assert len(actions) == 5
    assert isinstance(actions[0][0], type(if_found_unlink))
    assert len(actions[0][1]) == 1
    assert actions[0][1][0].name == 'flake8.log'
    assert str(actions[1]).startswith('Cmd: poetry run python -m flake8 --config')
    assert 'dodo.py" ' in str(actions[1])
    assert '.flake8 ' in str(actions[1])
    assert 'flake8.log ' in str(actions[1])
    assert isinstance(actions[2][0], type(_check_linting_errors))
    assert len(actions[2][1]) == 2
    assert actions[2][1][0].name == 'flake8.log'
    assert actions[2][1][1] == ('T100', 'T101')


def test_task_lint_project():
    """Test task_lint_project."""
    result = task_lint_project()

    actions = result['actions']
    assert len(actions) == 7
    assert 'poetry run yamllint --strict "' in str(actions[5])
    assert 'poetry run jsonlint --strict "' in str(actions[6])


def test_task_lint_critical_only():
    """Test task_lint_critical_only."""
    result = task_lint_critical_only()

    actions = result['actions']
    assert len(actions) == 7
    assert 'T100' not in str(actions[1])
    assert isinstance(actions[2][0], type(_check_linting_errors))
    assert len(actions[2][1]) == 2
    assert actions[2][1][0].name == 'flake8.log'
    assert actions[2][1][1] == ['T100', 'T101', 'T103']  # Read from toml
    assert 'T100' in actions[2][1][1]
    assert '-m xenon ' in str(actions[4])
    assert 'poetry run yamllint  "' in str(actions[5])
    assert 'poetry run jsonlint  "' in str(actions[6])


def test_task_radon_lint():
    """Test task_radon_lint."""
    result = task_radon_lint()

    actions = result['actions']
    assert len(actions) == 8
    for action in actions:
        if isinstance(action, tuple):
            assert isinstance(action[0], type(echo))
        else:
            assert str(action).startswith('Cmd: poetry run radon ')


def test_task_auto_format():
    """Test task_auto_format."""
    result = task_auto_format()

    actions = result['actions']
    assert len(actions) == 4
    assert ' add-trailing-comma ' in actions[0]
    assert '-m autoflake ' in actions[1]
    assert '-m autopep8 ' in actions[2]
    assert '-m isort ' in actions[3]


def test_task_pre_commit_hooks():
    """Test task_pre_commit_hooks."""
    result = task_pre_commit_hooks()

    actions = result['actions']
    assert len(actions) == 3
    assert 'pre-commit install' in str(actions[0])
    assert 'pre-commit autoupdate' in str(actions[1])
    assert 'pre-commit run --all-files' in str(actions[2])
