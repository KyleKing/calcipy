"""doit Linting Utilities."""

from pathlib import Path
from typing import Iterable, List

from beartype import beartype
from doit.tools import Interactive

from ..file_helpers import if_found_unlink
from .base import debug_task, echo
from .doit_globals import DG, DoitAction, DoitTask

# ----------------------------------------------------------------------------------------------------------------------
# Linting


@beartype
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
        lines = log_contents.split('\n')
        lines = [
            line for line in lines
            if all(f': {error_code}' in line for error_code in ignore_errors)
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


# TODO: see if all return types could be removed from docstrings b/c technically optional and not linted
@beartype
def _lint_project(
    lint_paths: List[Path], path_flake8: Path,
    ignore_errors: Iterable[str] = (),
) -> List[DoitAction]:  # FIXME: Docstrings should report an error here for mismatch in types?
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
    actions.append(f'{run} flake8 {flags} ' + ' '.join(f'"{pth}"' for pth in lint_paths))
    actions.append((_check_linting_errors, (flake8_log_path, ignore_errors)))
    return actions


@beartype
def task_lint_project() -> DoitTask:
    """Lint files from DG creating summary log file of errors.

    Returns:
        DoitTask: doit task

    """
    return debug_task(
        _lint_project(
            DG.lint.paths_py, path_flake8=DG.lint.path_flake8,
            ignore_errors=[],
        ),
    )


@beartype
def task_lint_critical_only() -> DoitTask:
    """Lint files from DG creating summary log file of errors, but ignore non-critical errors.

    Returns:
        DoitTask: doit task

    """
    return debug_task(
        _lint_project(
            DG.lint.paths_py, path_flake8=DG.lint.path_flake8,
            ignore_errors=DG.lint.ignore_errors,
        ),
    )


@beartype
def task_radon_lint() -> DoitTask:
    """Lint project with Radon.

    See documentation: https://radon.readthedocs.io/en/latest/intro.html

    Returns:
        DoitTask: doit task

    """
    actions: List[DoitAction] = []
    for args in ['mi', 'cc --total-average -nb', 'hal']:
        actions.append((echo, (f'# Radon with args: {args}',)))
        actions.extend([f'poetry run radon {args} "{lint_path}"' for lint_path in DG.lint.paths_py])
    return debug_task(actions)


@beartype
def task_security_checks() -> DoitTask:
    """Use linting tools to identify possible security vulnerabilities.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive(f'poetry run bandit -r {DG.meta.pkg_name}'),
    ])


# ----------------------------------------------------------------------------------------------------------------------
# Formatting


@beartype
def task_auto_format() -> DoitTask:
    """Format code with isort and autopep8.

    Other Useful Format Snippets:

    ```sh
    poetry run isort --recursive --check --diff calcipy/ tests/
    ```

    Returns:
        DoitTask: doit task

    """
    run = 'poetry run python -m'
    paths = ' '.join(f'"{pth}"' for pth in DG.lint.paths_py)
    return debug_task([
        f'{run} autopep8 {paths} --in-place --aggressive',
        f'{run} isort {paths} --settings-path "{DG.lint.path_isort}"',
    ])


@beartype
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
