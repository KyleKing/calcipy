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


@beartype
def _lint_python(
    lint_paths: List[Path], path_flake8: Path,
    ignore_errors: Iterable[str] = ('T100', 'T101'),
    xenon_args: str = '--max-absolute B --max-modules A --max-average A',
    diff_fail_under: int = 80, diff_branch: str = 'origin/main',
) -> List[DoitAction]:
    """Lint specified files creating summary log file of errors.

    Args:
        lint_paths: list of file and directory paths to lint
        path_flake8: path to flake8 configuration file
        ignore_errors: list of error codes to ignore (beyond the flake8 config settings). Default is to ignore Code Tags
        xenon_args: string arguments passed to xenon. Default is for most strict options available
        diff_fail_under: integer minimum test coverage. Default is 80
        diff_branch: string branch to compare against. Default is `origin/main`

    Returns:
        List[DoitAction]: doit task

    """
    # Flake8 appends to the log file. Ensure that an existing file is deleted so that Flake8 creates a fresh file
    run_m = 'poetry run python -m'
    flake8_log_path = DG.meta.path_project / 'flake8.log'
    flake8_flags = f'--config={path_flake8}  --output-file={flake8_log_path} --exit-zero'
    diff_params = f'--compare-branch={diff_branch} --fail-under={diff_fail_under}'
    diff_report = f'--html-report {DG.test.path_diff_lint_report}'
    return [
        (if_found_unlink, (flake8_log_path,)),
        Interactive(f'{run_m} flake8 {flake8_flags} ' + ' '.join(f'"{pth}"' for pth in lint_paths)),
        (_check_linting_errors, (flake8_log_path, ignore_errors)),
        Interactive(f'poetry run diff-quality --violations=flake8 {diff_params} {diff_report}'),
        Interactive(f'{run_m} xenon {DG.meta.pkg_name} {xenon_args}'),
    ]


@beartype
def _lint_non_python(strict: bool = False) -> List[DoitAction]:
    """Lint non-Python files such as JSON and YML/YAML.

    Args:
        strict: if True, will use the strictest configuration for the linter

    Returns:
        List[DoitAction]: doit task

    """
    strict_flag = '--strict' if strict else ''

    actions = []

    paths_yaml = DG.meta.paths_by_suffix.get('yml', []) + DG.meta.paths_by_suffix.get('yaml', [])
    if paths_yaml:
        paths = ' '.join(f'"{pth}"' for pth in paths_yaml)
        actions.append(Interactive(f'poetry run yamllint {strict_flag} {paths}'))

    paths_json = DG.meta.paths_by_suffix.get('json', [])
    if paths_json:
        actions.extend(Interactive(f'poetry run jsonlint {strict_flag} "{pth}"') for pth in paths_json)

    return actions


@beartype
def task_lint_python() -> DoitTask:
    """Lint all Python files and create summary of errors.

    Returns:
        DoitTask: doit task

    """
    actions = _lint_python(DG.lint.paths_py, path_flake8=DG.lint.path_flake8)
    return debug_task(actions)


@beartype
def task_lint_project() -> DoitTask:
    """Lint all project files that can be checked.

    Returns:
        DoitTask: doit task

    """
    actions = _lint_python(DG.lint.paths_py, path_flake8=DG.lint.path_flake8)
    actions.extend(_lint_non_python(strict=True))
    return debug_task(actions)


@beartype
def task_lint_critical_only() -> DoitTask:
    """Suppress non-critical linting errors. Great for gating PRs/commits.

    Returns:
        DoitTask: doit task

    """
    actions = _lint_python(
        DG.lint.paths_py, path_flake8=DG.lint.path_flake8, ignore_errors=DG.lint.ignore_errors,
        xenon_args='--max-absolute C --max-modules A --max-average A',
    )
    actions.extend(_lint_non_python())
    return debug_task(actions)


@beartype
def task_radon_lint() -> DoitTask:
    """Lint project with Radon.

    See documentation: https://radon.readthedocs.io/en/latest/intro.html

    PLANNED: Simplify and choose one way of using Radon

    > Try Radon/Xenon, see [metrics](http://www.mccabe.com/iq_research_metrics.htm)

    Returns:
        DoitTask: doit task

    """
    actions: List[DoitAction] = []
    paths = ' '.join(map(Path.as_posix, DG.lint.paths_py))
    for args in ['mi --show --min B', 'cc --total-average --min B', 'hal', 'raw --summary']:
        actions.extend([
            (echo, (f'# Radon with args: {args}',)),
            # Could also create a file "--json --output-file .radon-{arg}.json" ("arg = args.split(' ')[0]")
            Interactive(f'poetry run radon {args} {paths}'),
        ])
    return debug_task(actions)


@beartype
def task_static_checks() -> DoitTask:
    """General static checkers (Inspection Tiger, etc.).

    FYI: `IT` could be useful to handle deprecation. For now, only run the default checkers: https://pypi.org/project/it

    Returns:
        DoitTask: doit task

    """
    paths = ' '.join(map(Path.as_posix, DG.lint.paths_py))
    return debug_task([
        Interactive(f'poetry run it {DG.meta.pkg_name} --show-plugins'),
        Interactive(f'poetry run vulture {paths} --min-confidence 70 --sort-by-size'),
    ])


@beartype
def task_security_checks() -> DoitTask:
    """Use linting tools to identify possible security vulnerabilities. Use `# nosec` to selectively override checks.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        'poetry run pip-audit -f json',  # FIXME: Check for errors in output
        Interactive(f'poetry run bandit --recursive {DG.meta.pkg_name}'),
        Interactive('poetry run nox --session check_safety'),
    ])


# ----------------------------------------------------------------------------------------------------------------------
# Formatting


# TODO: create task that accepts a single file from pre-commit
@beartype
def task_auto_format() -> DoitTask:
    """Format code with isort, autopep8, and others.

    Other Useful Format Snippets:

    ```sh
    poetry run isort --recursive --check --diff calcipy/ tests/
    ```

    Returns:
        DoitTask: doit task

    """
    run = 'poetry run python -m'
    autoflake_args = (
        '--in-place --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports'
        ' --remove-duplicate-keys'
    )
    paths = ' '.join(f'"{pth}"' for pth in DG.lint.paths_py)
    return debug_task([
        f'{run} autoflake {paths} {autoflake_args}',
        f'{run} autopep8 {paths} --in-place --aggressive',
        f'{run} isort {paths} --settings-path "{DG.lint.path_isort}"',
    ])


# ----------------------------------------------------------------------------------------------------------------------
# General Static Analysis


@beartype
def task_pre_commit_hooks() -> DoitTask:
    """Run the pre-commit hooks  on all files.

    > Note: use `git commit` or `git push` with `--no-verify` if needed

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive('poetry run pre-commit install'),
        Interactive('poetry run pre-commit autoupdate'),
        Interactive('poetry run pre-commit run --all-files'),
    ])
