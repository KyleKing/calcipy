"""DoIt Linting Utilities."""

from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

import toml
from doit.tools import LongRunning
from loguru import logger

from ..log_helpers import log_fun
from .base import debug_task, echo, if_found_unlink, write_text
from .doit_globals import DIG, DoItTask

# ----------------------------------------------------------------------------------------------------------------------
# General


# TODO: Possibly remove - may be unused
@log_fun
def _collect_py_files(add_paths: Sequence[Path] = (), sub_directories: Optional[Sequence[Path]] = None) -> List[str]:
    """Collect the tracked files for linting and formatting. Return as list of string paths.

    Args:
        add_paths: List of absolute paths to additional Python files to process. Default is an empty list
        sub_directories: folder Paths to recursively check for Python files

    Returns:
        list: of string path names

    Raises:
        TypeError: if the add_paths argument is not a list or tuple

    """
    if not isinstance(add_paths, (list, tuple)):
        raise TypeError(f'Expected add_paths to be a list of Paths, but received: {add_paths}')
    if sub_directories is None:
        sub_directories = []
    sub_directories.extend([DIG.meta.path_source / DIG.meta.pkg_name, DIG.test.path_tests] + DIG.lint.paths)
    package_files = [*add_paths] + [*DIG.meta.path_source.glob('*.py')]
    for subdir in sub_directories:  # Capture files in package and in tests directory
        package_files.extend([*subdir.rglob('*.py')])
    return [str(file_path) for file_path in package_files if file_path.name not in DIG.lint.paths_excluded]


# ----------------------------------------------------------------------------------------------------------------------
# Configuration Settings

_FLAKE8: str = """[flake8]
annoy = true
assertive-snakecase = true
cohesion-below = 50.0
docstring-convention = all
# Explanation and Notes on Flake8 Ignore Rules. Also see: https://www.flake8rules.com/
# ANN01,ANN101 / flake8-annotations: https://github.com/sco1/flake8-annotations
# D203,D213,D214,D406,D407 / (conflicts with Google docstrings) http://www.pydocstyle.org/en/latest/error_codes.html
# G004 / https://github.com/globality-corp/flake8-logging-format#violations-detected
# H101,H238,H301,H304,H306 / https://docs.openstack.org/hacking/latest/user/hacking.html
# PD005,PD011 / (false positives) https://github.com/deppen8/pandas-vet/issues/74
# S322 / https://github.com/tylerwince/flake8-bandit
# W503 - Must select one of W503 or W504. See: https://lintlyci.github.io/Flake8Rules/rules/W504.html
#   Python 3 standard is a line break BEFORE binary operator, so ignore W503. Enforce W504
ignore = ANN01,ANN101,D203,D213,D214,D406,D407,G004,H101,H238,H301,H304,H306,PD005,PD011,S322,W503
# Default is 7. See: https://github.com/Melevir/flake8-cognitive-complexity
max-cognitive-complexity = 7
max-complexity = 10
# Default is 7. See: https://github.com/best-doctor/flake8-expression-complexity
max-expression-complexity = 7
max-function-length = 55
max-line-length = 120
max-parameters-amount = 6
per-file-ignores=test_*.py:ANN001,ANN201,DAR101,DAR201,E800,S101
select = A,B,C,D,E,F,G,H,I,J,K,L,M,N,O,P,Q,R,S,T,U,V,W,X,Y,Z

# Do not modify, auto-generated by calcipy
"""
"""Flake8 configuration file settings."""

_ISORT: Dict[str, Union[int, str]] = {
    'balanced_wrapping': True,
    'default_section': 'THIRDPARTY',
    'force_grid_wrap': 0,
    'length_sort': False,
    'line_length': 120,
}
"""ISort configuration file settings."""


def task_set_lint_config() -> DoItTask:
    """Lint specified files creating summary log file of errors.

    Returns:
        DoItTask: DoIt task

    """
    user_toml = toml.load(DIG.meta.path_toml)
    user_toml['tool']['isort'] = _ISORT
    return debug_task([
        (write_text, (DIG.lint.path_flake8, _FLAKE8)),
        (write_text, (DIG.meta.path_toml, toml.dumps(user_toml))),
    ])


# ----------------------------------------------------------------------------------------------------------------------
# Linting


def _list_lint_file_paths(path_list: List[Path]) -> List[Path]:
    """Create a list of all Python files specified in the path_list.

    Args:
        path_list: list of paths to directories or files

    Returns:
        list: list of file Paths

    """
    file_paths = []
    for path_item in path_list:
        file_paths.extend([*path_item.rglob('*.py')] if path_item.is_dir() else [path_item])
    logger.debug(f'Found {len(file_paths)} files', file_paths=file_paths)
    return [pth for pth in file_paths if pth.name not in DIG.lint.paths_excluded]


def _check_linting_errors(flake8_log_path: Path, ignore_errors: Optional[str] = None) -> None:  # noqa: CCR001
    """Check for errors reported in flake8 log file. Removes log file if no errors detected.

    Args:
        flake8_log_path: path to flake8 log file created with flag: `--output-file=flake8_log_path`
        ignore_errors: list of error codes to ignore (beyond the flake8 config settings). Default is None

    Raises:
        RuntimeError: if flake8 log file contains any text results

    """
    flake8_full_path = flake8_log_path.parent / f'{flake8_log_path.stem}-full{flake8_log_path.suffix}'
    log_contents = flake8_log_path.read_text().strip()
    review_info = f'. Review: {flake8_log_path}'
    if ignore_errors:
        # Backup the full list of errors
        flake8_full_path.write_text(log_contents)
        # Exclude the errors specificed to be ignored by the user
        lines = []
        for line in log_contents.split('\n'):
            if not any(f': {error_code}' in line for error_code in ignore_errors):
                lines.append(line)
        log_contents = '\n'.join(lines)
        flake8_log_path.write_text(log_contents)
        review_info = (f' even when ignoring {ignore_errors}.\nReview: {flake8_log_path}'
                       f'\nNote: the full list linting errors are reported in {flake8_full_path}')
    else:
        if_found_unlink(flake8_full_path)

    # Raise an exception if any errors were found. Remove the files if not
    if len(log_contents) > 0:
        raise RuntimeError(f'Found Linting Errors{review_info}')
    if_found_unlink(flake8_log_path)


def _lint_project(lint_paths: List[Path], path_flake8: Path,
                  ignore_errors: Optional[List[str]] = None) -> DoItTask:
    """Lint specified files creating summary log file of errors.

    Args:
        lint_paths: list of file and directory paths to lint
        path_flake8: path to flake8 configuration file
        ignore_errors: list of error codes to ignore (beyond the flake8 config settings). Default is None

    Returns:
        DoItTask: DoIt task

    """
    # Flake8 appends to the log file. Ensure that an existing file is deleted so that Flake8 creates a fresh file
    flake8_log_path = DIG.meta.path_source / 'flake8.log'
    actions = [(if_found_unlink, (flake8_log_path, ))]
    run = 'poetry run python -m'
    flags = f'--config={path_flake8}  --output-file={flake8_log_path} --exit-zero'
    for lint_path in _list_lint_file_paths(lint_paths):
        actions.append(f'{run} flake8 "{lint_path}" {flags}')
    actions.append((_check_linting_errors, (flake8_log_path, ignore_errors)))
    return actions


def task_lint_project() -> DoItTask:
    """Lint files from DIG creating summary log file of errors.

    Returns:
        DoItTask: DoIt task

    """
    return debug_task(_lint_project(DIG.lint.paths, path_flake8=DIG.lint.path_flake8, ignore_errors=None))


def task_lint_critical_only() -> DoItTask:
    """Lint files from DIG creating summary log file of errors, but ignore non-critical errors.

    Returns:
        DoItTask: DoIt task

    """
    ignore_errors = [
        'AAA01',  # AAA01 / act block in pytest
        'C901',  # C901 / complexity from "max-complexity = 10"
        'D417',  # D417 / missing arg descriptors
        'DAR101', 'DAR201', 'DAR401',  # https://pypi.org/project/darglint/ (Scroll to error codes)
        'DUO106',  # DUO106 / insecure use of os
        'E800',  # E800 / Commented out code
        'G001',  # G001 / logging format for un-indexed parameters
        'H601',  # H601 / class with low cohesion
        'P101', 'P103',  # P101,P103 / format string
        'PD013',
        'S101',  # S101 / assert
        'S605', 'S607',  # S605,S607 / os.popen(...)
        'T100', 'T101', 'T103',  # T100,T101,T103 / fixme and todo comments
    ]
    return debug_task(_lint_project(DIG.lint.paths, path_flake8=DIG.lint.path_flake8, ignore_errors=ignore_errors))


def task_radon_lint() -> DoItTask:
    """See documentation: https://radon.readthedocs.io/en/latest/intro.html. Lint project with Radon.

    Returns:
        DoItTask: DoIt task

    """
    actions = []
    for args in ['mi', 'cc --total-average -nb', 'hal']:
        actions.extend(
            [(echo, (f'# Radon with args: {args}', ))]
            + [f'poetry run radon {args} "{lint_path}"' for lint_path in _list_lint_file_paths(DIG.lint.paths)],
        )
    return debug_task([*map(LongRunning, actions)])


# ----------------------------------------------------------------------------------------------------------------------
# Formatting


def task_auto_format() -> DoItTask:
    """Format code with isort and autopep8.

    Returns:
        DoItTask: DoIt task

    """
    run = 'poetry run python -m'
    actions = []
    for lint_path in DIG.lint.paths:
        actions.append(f'{run} isort "{lint_path}" --settings-path "{DIG.meta.path_toml}"')
        for fn in _list_lint_file_paths([lint_path]):
            actions.append(f'{run} autopep8 "{fn}" --in-place --aggressive')
    return debug_task([*map(LongRunning, actions)])


def task_pre_commit_hooks() -> DoItTask:
    """Run the pre-commit hooks on all files.

    Returns:
        DoItTask: DoIt task

    """
    return debug_task([
        LongRunning('poetry run pre-commit autoupdate'),
        LongRunning('poetry run pre-commit run --all-files'),
    ])
