"""Test doit_helpers/lint.py."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from dash_dev.doit_helpers.doit_globals import DIG
from dash_dev.doit_helpers.lint import _check_linting_errors, _collect_py_files, _lint_project

from ..configuration import DIG_CWD


def test_collect_py_files():
    """Test collect_py_files."""
    DIG.set_paths(source_path=DIG_CWD)

    result = _collect_py_files(add_paths=(), sub_directories=None)

    assert len(result) == 2
    assert str(DIG_CWD / 'test_file.py') in result
    assert str(DIG_CWD / 'tests/test_file_2.py') in result


def test_lint_project():
    """Test lint_project."""
    DIG.set_paths(source_path=DIG_CWD)

    result = _lint_project(
        lint_paths=[DIG_CWD / 'test_file.py', DIG_CWD / 'tests/test_file_2.py'],
        ignore_errors=['F401', 'E800', 'I001', 'I003'],
    )

    assert len(result) == 4  # There are two files that are parsed


FLAKE8_LOG = """doit_project/test_file.py:3:1: F401 'doit' imported but unused
doit_project/test_file.py:3:1: I001 isort found an import in the wrong position
doit_project/test_file.py:4:1: F401 'pathlib.Path' imported but unused
doit_project/test_file.py:6:1: I003 isort expected 1 blank line in imports, found 0
doit_project/test_file.py:6:2: E800: Found commented out code
"""


def test_check_linting_errors():
    """Test check_linting_errors."""
    with TemporaryDirectory() as td:
        flake8_log_path = Path(td) / 'flake8.log'
        flake8_log_path.write_text(FLAKE8_LOG)

        _check_linting_errors(flake8_log_path, ignore_errors=['F401', 'I001', 'I003', 'E800'])  # act

        assert not flake8_log_path.is_file()


def test_check_linting_errors_runtime_error():
    """Test check_linting_errors."""
    with TemporaryDirectory() as td:
        flake8_log_path = Path(td) / 'flake8.log'
        flake8_log_path.write_text(FLAKE8_LOG)

        with pytest.raises(RuntimeError):
            _check_linting_errors(flake8_log_path, ignore_errors=None)
