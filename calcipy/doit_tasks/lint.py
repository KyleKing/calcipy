"""doit Linting Utilities."""

from pathlib import Path
from typing import List, Optional, Sequence

from loguru import logger

from ..log_helpers import log_fun
from .base import debug_task, echo, if_found_unlink
from .doit_globals import DIG, DoItTask

# ----------------------------------------------------------------------------------------------------------------------
# General


# TODO: Possibly remove - may be unused
@log_fun
def _collect_py_files(add_paths: Sequence[Path] = (), sub_directories: Optional[List[Path]] = None) -> List[str]:
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
    sub_directories.extend([DIG.meta.path_project / DIG.meta.pkg_name, DIG.test.path_tests] + DIG.lint.paths)
    package_files = [*add_paths] + [*DIG.meta.path_project.glob('*.py')]
    for subdir in sub_directories:  # Capture files in package and in tests directory
        package_files.extend([*subdir.rglob('*.py')])
    return [str(file_path) for file_path in package_files if file_path.name not in DIG.lint.paths_excluded]


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


def _check_linting_errors(flake8_log_path: Path, ignore_errors: Optional[str] = None) -> None:    # noqa: CCR001
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
        lines = [
            line
            for line in log_contents.split('\n')
            if all(
                f': {error_code}' not in line for error_code in ignore_errors
            )
        ]

        log_contents = '\n'.join(lines)
        flake8_log_path.write_text(log_contents)
        review_info = (
            f' even when ignoring {ignore_errors}.\nReview: {flake8_log_path}'
            f'\nNote: the full list linting errors are reported in {flake8_full_path}'
        )
    else:
        if_found_unlink(flake8_full_path)

    # Raise an exception if any errors were found. Remove the files if not
    if len(log_contents) > 0:
        raise RuntimeError(f'Found Linting Errors{review_info}')
    if_found_unlink(flake8_log_path)


def _lint_project(
    lint_paths: List[Path], path_flake8: Path,
    ignore_errors: Optional[List[str]] = None,
) -> DoItTask:
    """Lint specified files creating summary log file of errors.

    Args:
        lint_paths: list of file and directory paths to lint
        path_flake8: path to flake8 configuration file
        ignore_errors: list of error codes to ignore (beyond the flake8 config settings). Default is None

    Returns:
        DoItTask: doit task

    """
    # Flake8 appends to the log file. Ensure that an existing file is deleted so that Flake8 creates a fresh file
    flake8_log_path = DIG.meta.path_project / 'flake8.log'
    actions = [(if_found_unlink, (flake8_log_path,))]
    run = 'poetry run python -m'
    flags = f'--config={path_flake8}  --output-file={flake8_log_path} --exit-zero'
    for lint_path in _list_lint_file_paths(lint_paths):
        actions.append(f'{run} flake8 "{lint_path}" {flags}')
    actions.append((_check_linting_errors, (flake8_log_path, ignore_errors)))
    return actions


def task_lint_project() -> DoItTask:
    """Lint files from DIG creating summary log file of errors.

    Returns:
        DoItTask: doit task

    """
    return debug_task(_lint_project(DIG.lint.paths, path_flake8=DIG.lint.path_flake8, ignore_errors=None))


def task_lint_critical_only() -> DoItTask:
    """Lint files from DIG creating summary log file of errors, but ignore non-critical errors.

    Returns:
        DoItTask: doit task

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
        DoItTask: doit task

    """
    actions = []
    for args in ['mi', 'cc --total-average -nb', 'hal']:
        actions.extend(
            [(echo, (f'# Radon with args: {args}',))]
            + [f'poetry run radon {args} "{lint_path}"' for lint_path in _list_lint_file_paths(DIG.lint.paths)],
        )
    return debug_task(actions)


# ----------------------------------------------------------------------------------------------------------------------
# Formatting


def task_auto_format() -> DoItTask:
    """Format code with isort and autopep8.

    Returns:
        DoItTask: doit task

    """
    run = 'poetry run python -m'
    actions = []
    for lint_path in DIG.lint.paths:
        actions.append(f'{run} isort "{lint_path}" --settings-path "{DIG.lint.path_isort}"')
        for fn in _list_lint_file_paths([lint_path]):
            actions.append(f'{run} autopep8 "{fn}" --in-place --aggressive')
    return debug_task(actions)


def task_pre_commit_hooks() -> DoItTask:
    """Run the pre-commit hooks on all files.

    Note: use `git commit` or `git push` with `--no-verify` if needed

    Returns:
        DoItTask: doit task

    """
    return debug_task([
        'poetry run pre-commit autoupdate',

        'poetry run pre-commit install --install-hooks --hook-type commit-msg --hook-type pre-push',

        'poetry run pre-commit run --hook-stage commit',  # --all-files
        'poetry run pre-commit run --hook-stage push',  # --all-files
    ])
