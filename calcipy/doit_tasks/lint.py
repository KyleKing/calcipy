"""doit Linting Utilities."""

from pathlib import Path

from beartype import beartype
from beartype.typing import Iterable, List
from doit.tools import Interactive
from loguru import logger

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
        # Exclude the errors specified to be ignored by the user
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
        # FIXME" Need to check if the branch is available first! Will fail on GHA
        Interactive(f'echo "poetry run diff-quality --violations=flake8 {diff_params} {diff_report}"'),
        Interactive(f'{run_m} xenon {DG.meta.pkg_name} {xenon_args}'),
    ]


@beartype
def _lint_non_python() -> List[DoitAction]:
    """Lint non-Python files such as JSON and YML/YAML.

    Returns:
        List[DoitAction]: doit task

    """
    actions = []
    pbs = DG.meta.paths_by_suffix
    paths_yaml = pbs.get('yml', []) + pbs.get('yaml', [])
    if paths_yaml:
        yamllint_args = '-d "{rules: {line-length: {max: 120}}}"'
        paths = ' '.join(f'"{pth}"' for pth in paths_yaml)
        actions.append(Interactive(f'poetry run yamllint {yamllint_args} {paths}'))

    # FYI: Use pre-commit instead
    # From: https://github.com/pre-commit/pre-commit-hooks/blob/0d261aaf84419c0c8fe70ff4a23f6a99655868de/
    #   lint: ./pre_commit_hooks/check_json.py
    #   format: ./pre_commit_hooks/pretty_format_json.py
    # > if paths_json := DG.meta.paths_by_suffix.get('json', []):
    # >     actions.extend(Interactive(f'poetry run jsonlint "{pth}"') for pth in paths_json)

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
    actions.extend(_lint_non_python())
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
    """General static checkers (vulture, etc.).

    Returns:
        DoitTask: doit task

    """
    paths = ' '.join(map(Path.as_posix, DG.lint.paths_py))
    return debug_task([
        Interactive(f'poetry run vulture {paths} --min-confidence 70 --sort-by-size'),
    ])


@beartype
def task_security_checks() -> DoitTask:
    """Use linting tools to identify possible security vulnerabilities. Use `# nosec` to selectively override checks.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive(f'poetry run bandit --recursive {DG.meta.pkg_name}'),
        Interactive('poetry run nox --session check_safety'),
    ])


# ----------------------------------------------------------------------------------------------------------------------
# Formatting


@beartype
def _gen_format_actions(paths: str) -> List[str]:
    """Generate the list of format actions for Python files (isort, autopep8, etc.).

    # PLANNED: Considering splitting paths on commas if above some maximum character length?

    Args:
        paths: string list of one or more paths to pass to the cli tools

    Returns:
        DoitTask: doit task

    """
    run = 'poetry run'
    run_mod = f'{run} python -m'
    autoflake_args = (
        '--in-place --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports'
        ' --remove-duplicate-keys'
    )
    return [
        f'{run} pyupgrade {paths} --py38-plus --keep-runtime-typing',
        f'{run_mod} autoflake {paths} {autoflake_args}',
        f'{run_mod} autopep8 {paths} --in-place --aggressive',
        f'{run} pycln --quiet {paths}',
        f'{run} absolufy-imports {paths} --never',
        f'{run_mod} isort {paths} --settings-path "{DG.lint.path_isort}"',
        f'{run} add-trailing-comma {paths} --py36-plus --exit-zero-even-if-changed',
    ]


@beartype
def task_format_py() -> DoitTask:
    """Format a space-separate list of Python file(s). Particularly useful for pre-commit.

    ```sh
    poetry run format_py -p dodo.py tests/conftest.py
    ```

    Returns:
        DoitTask: doit task

    """
    return {
        'actions': _gen_format_actions('%(py_paths)s'),
        'pos_arg': 'py_paths',
        'verbosity': 2,
    }


# FIXME: Add bulk toml formatting to the auto_format task!
@beartype
def task_format_toml() -> DoitTask:
    """Format a space-separate list of TOML file(s) with `taplo`. Particularly useful for pre-commit.

    ```sh
    poetry run format_toml -p pyproject.toml .deepsource.toml
    ```

    Returns:
        DoitTask: doit task

    """
    return {
        # PLANNED: Could provide more hooks for configuring taplo options. See:
        #   https://taplo.tamasfe.dev/configuration/#formatting-options
        'actions': [
            # FIXME: capturing to /dev/null doesn't seem to work reliably
            Interactive(
                '(which taplo >> /dev/null && taplo format --options="indent_string=\'    \'" %(toml_paths)s) || true',
            ),
        ],
        'pos_arg': 'toml_paths',
        'verbosity': 2,
    }


@beartype
def task_auto_format() -> DoitTask:
    """Format code with isort, autopep8, and others.

    Additional snippets that may be useful, but aren't used by doit:

    ```sh
    poetry run isort --recursive --check --diff calcipy/ tests/
    ```

    Returns:
        DoitTask: doit task

    """
    @beartype
    def get_short_path(_pth: Path) -> Path:
        try:
            return _pth.relative_to(DG.meta.path_project)
        except Exception as exc:
            logger.warning(
                '{pth} is not relative to {rel_path}. Error: {exc}',
                pth=_pth, rel_path=DG.meta.path_project, exc=exc,
            )
            return _pth

    paths = ' '.join(f'"{get_short_path(pth)}"' for pth in DG.lint.paths_py)
    return debug_task(_gen_format_actions(paths))


# ----------------------------------------------------------------------------------------------------------------------
# General Static Analysis


@beartype
def task_pre_commit_hooks() -> DoitTask:
    """Run the pre-commit hooks  on all files.

    > Note: use `git commit` or `git push` with `--no-verify` if needed

    Returns:
        DoitTask: doit task

    """
    # Hooks should be installed for all types
    # https://github.com/pre-commit/pre-commit/blob/7858ad066f2dfd11453c2f7e25c8f055ba4de931/pre_commit/commands/install_uninstall.py#L103-L130
    return debug_task([
        Interactive('poetry run pre-commit install'),
        Interactive('poetry run pre-commit autoupdate'),
        Interactive('poetry run pre-commit run --all-files --hook-stage commit --hook-stage push'),
    ])
