"""doit Linting Utilities."""

from pathlib import Path

from beartype import beartype
from beartype.typing import Iterable, List
from doit.tools import Interactive
from loguru import logger

from ..file_helpers import if_found_unlink
from .base import debug_task, echo
from .doit_globals import DoitAction, DoitTask, get_dg

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
) -> List[DoitAction]:
    """Lint specified files creating summary log file of errors.

    Args:
        lint_paths: list of file and directory paths to lint
        path_flake8: path to flake8 configuration file
        ignore_errors: list of error codes to ignore (beyond the flake8 config settings). Default is to ignore Code Tags
        xenon_args: string arguments passed to xenon. Default is for most strict options available

    Returns:
        List[DoitAction]: doit task

    """
    # Flake8 appends to the log file. Ensure that an existing file is deleted so that Flake8 creates a fresh file
    dg = get_dg()

    # FIXME: Update assert-cache by making all paths in DG relative
    def to_rel(_pth: Path) -> str:
        """COnvert to relative path and escape % symbols."""
        return _pth.relative_to(dg.meta.path_project).as_posix().replace('%', '%%')

    run_m = 'poetry run python -m'
    flake8_log_path = Path('flake8.log')
    flake8_flags = f'--config={to_rel(path_flake8)} --output-file={flake8_log_path} --exit-zero'
    path_args = ' '.join(f'"./{to_rel(pth)}"' for pth in lint_paths)
    return [
        (if_found_unlink, (flake8_log_path,)),
        Interactive(f'{run_m} flake8 {flake8_flags} {path_args}'),
        (_check_linting_errors, (flake8_log_path, ignore_errors)),
        Interactive(f'{run_m} xenon {get_dg().meta.pkg_name} {xenon_args}'),
    ]


@beartype
def _lint_non_python() -> List[DoitAction]:
    """Lint non-Python files such as JSON and YML/YAML.

    Returns:
        List[DoitAction]: doit task

    """
    actions = []
    pbs = get_dg().meta.paths_by_suffix
    if paths_yaml := pbs.get('yml', []) + pbs.get('yaml', []):
        paths = ' '.join(f'"{pth}"' for pth in paths_yaml)
        actions.append(Interactive(f'poetry run yamllint {paths}'))
    return actions


@beartype
def task_lint_python() -> DoitTask:
    """Lint all Python files and create summary of errors.

    Returns:
        DoitTask: doit task

    """
    dg = get_dg()
    actions = _lint_python(dg.lint.paths_py, path_flake8=dg.lint.path_flake8)
    return debug_task(actions)


@beartype
def task_lint_project() -> DoitTask:
    """Lint all project files that can be checked.

    Returns:
        DoitTask: doit task

    """
    dg = get_dg()
    actions = _lint_python(dg.lint.paths_py, path_flake8=dg.lint.path_flake8)
    actions.extend(_lint_non_python())
    return debug_task(actions)


@beartype
def task_lint_critical_only() -> DoitTask:
    """Suppress non-critical linting errors. Great for gating PRs/commits.

    Returns:
        DoitTask: doit task

    """
    dg = get_dg()
    actions = _lint_python(
        dg.lint.paths_py, path_flake8=dg.lint.path_flake8, ignore_errors=dg.lint.ignore_errors,
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
    paths = ' '.join(map(Path.as_posix, get_dg().lint.paths_py))
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
    paths = ' '.join(map(Path.as_posix, get_dg().lint.paths_py))
    return debug_task([
        # Set to 61% because pydantic.Config and attributes are flagged with 60% confidence
        Interactive(f'poetry run vulture {paths} --min-confidence 61 --sort-by-size'),
    ])


@beartype
def task_security_checks() -> DoitTask:
    """Use linting tools to identify possible security vulnerabilities. Use `# nosec` to selectively override checks.

    Returns:
        DoitTask: doit task

    """
    # TODO: Implement semgrep - what are a good ruleset to start with?
    #   https://github.com/returntocorp/semgrep-rules/tree/develop/python
    #   https://awesomeopensource.com/project/returntocorp/semgrep-rules?categorypage=45
    configs = ' '.join([
        # See more at: https://semgrep.dev/explore
        '--config=p/ci',
        '--config=p/security-audit',
        '--config=r/python.airflow',
        '--config=r/python.attr',
        '--config=r/python.click',
        '--config=r/python.cryptography',
        '--config=r/python.distributed',
        '--config=r/python.docker',
        '--config=r/python.flask',
        '--config=r/python.jinja2',
        '--config=r/python.jwt',
        '--config=r/python.lang',
        '--config=r/python.pycryptodome',
        '--config=r/python.requests',
        '--config=r/python.security',
        '--config=r/python.sh',
        '--config=r/python.sqlalchemy',
        # dlukeomalley:unchecked-subprocess-call
        # dlukeomalley:use-assertEqual-for-equality
        # dlukeomalley:flask-set-cookie
        # clintgibler:no-exec
    ])
    return debug_task([
        Interactive(f'poetry run bandit --recursive {get_dg().meta.pkg_name}'),
        Interactive(f'semgrep ci {configs}'),
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
    # pyupgrade only supports py36 to py311 at this time
    pyup_ver = ''.join(get_dg().meta.min_python[:2])
    pyup_flag = ''
    if pyup_ver in [f'3{ix}' for ix in range(6, 12)]:
        pyup_flag = f'--py{pyup_ver}-plus'
    autoflake_args = (
        '--in-place --remove-all-unused-imports --remove-unused-variables --ignore-init-module-imports'
        ' --remove-duplicate-keys'
    )
    docfmt_args = '--blank --close-quotes-on-newline --in-place --wrap-summaries=120 --wrap-descriptions=120'
    return [
        f'{run} pyupgrade {paths} {pyup_flag} --keep-runtime-typing',
        # Note: autoflake and unimport basically do the same thing. Could select just one
        f'{run_mod} autoflake {paths} {autoflake_args}',
        f'{run_mod} unimport {paths} --include-star-import --remove',
        f'{run_mod} autopep8 {paths} --in-place --aggressive',
        f'{run} absolufy-imports {paths} --never',
        f'{run_mod} isort {paths} --settings-path "{get_dg().lint.path_isort}"',
        f'{run} add-trailing-comma {paths} --py36-plus --exit-zero-even-if-changed',
        f'{run_mod} docformatter {paths} {docfmt_args}',
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
            return _pth.relative_to(get_dg().meta.path_project)
        except Exception as exc:
            logger.warning(
                '{pth} is not relative to {rel_path}. Error: {exc}',
                pth=_pth, rel_path=get_dg().meta.path_project, exc=exc,
            )
            return _pth

    paths = ' '.join(f'"{get_short_path(pth)}"' for pth in get_dg().lint.paths_py)
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
