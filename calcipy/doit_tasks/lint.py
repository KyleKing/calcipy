"""doit Linting Utilities."""

from pathlib import Path
from typing import Iterable, List

from beartype import beartype
from doit.tools import Interactive

from .base import debug_task, echo, if_found_unlink
from .doit_globals import DG, DoitAction, DoitTask

# ----------------------------------------------------------------------------------------------------------------------
# Linting


def _check_linting_errors(flake8_log_path: Path, ignore_errors: Iterable[str] = ()) -> None:  # noqa: CCR001
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
            if all(f': {error_code}' in line for error_code in ignore_errors):
                lines.append(line)
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
    ignore_errors: Iterable[str] = (),
) -> DoitTask:
    """Lint specified files creating summary log file of errors.

    Args:
        lint_paths: list of file and directory paths to lint
        path_flake8: path to flake8 configuration file
        ignore_errors: list of error codes to ignore (beyond the flake8 config settings). Default is None

    Returns:
        DoitTask: doit task

    """
    # Flake8 appends to the log file. Ensure that an existing file is deleted so that Flake8 creates a fresh file
    flake8_log_path = DG.meta.path_project / 'flake8.log'
    actions: List[DoitAction] = [(if_found_unlink, (flake8_log_path,))]
    run = 'poetry run python -m'
    flags = f'--config={path_flake8}  --output-file={flake8_log_path} --exit-zero'
    actions.extend([f'{run} flake8 "{lint_path}" {flags}' for lint_path in lint_paths])
    actions.append((_check_linting_errors, (flake8_log_path, ignore_errors)))
    return actions


def task_lint_project() -> DoitTask:
    """Lint files from DG creating summary log file of errors.

    Returns:
        DoitTask: doit task

    """
    return debug_task(
        _lint_project(
            DG.lint.paths, path_flake8=DG.lint.path_flake8,
            ignore_errors=[],
        ),
    )


def task_lint_critical_only() -> DoitTask:
    """Lint files from DG creating summary log file of errors, but ignore non-critical errors.

    Returns:
        DoitTask: doit task

    """
    return debug_task(
        _lint_project(
            DG.lint.paths, path_flake8=DG.lint.path_flake8,
            ignore_errors=DG.lint.ignore_errors,
        ),
    )


def task_radon_lint() -> DoitTask:
    """Lint project with Radon.

    See documentation: https://radon.readthedocs.io/en/latest/intro.html

    Returns:
        DoitTask: doit task

    """
    actions: List[DoitAction] = []
    for args in ['mi', 'cc --total-average -nb', 'hal']:
        actions.append((echo, (f'# Radon with args: {args}',)))
        actions.extend([f'poetry run radon {args} "{lint_path}"' for lint_path in DG.lint.paths])
    return debug_task(actions)


# ----------------------------------------------------------------------------------------------------------------------
# Formatting


def task_auto_format() -> DoitTask:
    """Format code with isort and autopep8.

    Returns:
        DoitTask: doit task

    """
    run = 'poetry run python -m'
    actions = []
    for lint_path in DG.lint.paths:
        actions.append(f'{run} isort "{lint_path}" --settings-path "{DG.lint.path_isort}"')
        actions.append(f'{run} autopep8 "{lint_path}" --in-place --aggressive')
    # FIXME: autopep8 can take a list of space-separated files
    return debug_task(actions)


def task_pre_commit_hooks() -> DoitTask:
    """Run the pre-commit hooks on all files.

    Note: use `git commit` or `git push` with `--no-verify` if needed

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive('poetry run pre-commit autoupdate'),
        Interactive('poetry run pre-commit install --install-hooks --hook-type commit-msg --hook-type pre-push'),
        Interactive('poetry run pre-commit run --all-files'),
    ])
