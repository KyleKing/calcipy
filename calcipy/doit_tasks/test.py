"""doit Test Utilities."""

from beartype import beartype
from doit.tools import Interactive

from .base import debug_task, open_in_browser
from .doit_globals import DoitTask, get_dg

# ----------------------------------------------------------------------------------------------------------------------
# Manage Testing with Nox


@beartype
def _run_nox(args: str) -> DoitTask:
    """Run a nox command and fail if the interpreter is not found.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive(f'poetry run nox --error-on-missing-interpreters {args}'),
    ])


@beartype
def task_nox() -> DoitTask:
    """Run the full nox test suite.

    > Note: some nox tasks are run in more-specific doit tasks, but this will run everything

    Returns:
        DoitTask: doit task

    """
    return _run_nox('')


@beartype
def task_nox_test() -> DoitTask:
    """Run the nox tests sessions.

    Returns:
        DoitTask: doit task

    """
    return _run_nox('--session tests')


@beartype
def task_nox_coverage() -> DoitTask:
    """Run the coverage session in nox.

    Returns:
        DoitTask: doit task

    """
    return _run_nox('--session coverage')


# ----------------------------------------------------------------------------------------------------------------------
# Manage Testing with pytest (Should be run from Nox)


@beartype
def task_test() -> DoitTask:
    """Run tests with Pytest and stop on the first failure.

    > Test are randomly ordered by default with pytest-randomly because that can help catch common errors
    > Tests can be re-run in the last order with `poetry run pytest --randomly-seed=last`

    > Tip: `--record-mode=rewrite` can be useful if working with `pytest-recording`

    Returns:
        DoitTask: doit task

    """
    dg = get_dg()
    return debug_task([
        Interactive(f'poetry run python -m pytest "{dg.test.path_tests}" {dg.test.args_pytest}'),
    ])


@beartype
def task_test_all() -> DoitTask:
    """Run all possible tests with Pytest even if one or more failures.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive(f'poetry run python -m pytest "{get_dg().test.path_tests}" --ff -vv'),
    ])


@beartype
def task_test_marker() -> DoitTask:
    """Specify a marker to run a subset of tests.

    Example: `doit run test_marker -m "not MARKER"` or `doit run test_marker -m "MARKER"`

    Returns:
        DoitTask: doit task

    """
    dg = get_dg()
    task = debug_task(
        [
            Interactive(
                f'poetry run python -m pytest "{dg.test.path_tests}" {dg.test.args_pytest} -m "%(marker)s"',
            ),
        ],
    )
    task['params'] = [{
        'name': 'marker', 'short': 'm', 'long': 'marker', 'default': '',
        'help': (
            'Runs test with specified marker logic\nSee: '
            'https://docs.pytest.org/en/latest/example/markers.html?highlight=-m'
        ),
    }]
    return task


@beartype
def task_test_keyword() -> DoitTask:
    """Specify a keyword to run a subset of tests.

    Example: `doit run test_keyword -k "KEYWORD"`

    Returns:
        DoitTask: doit task

    """
    dg = get_dg()
    return {
        'actions': [
            Interactive(
                f'poetry run python -m pytest "{dg.test.path_tests}" {dg.test.args_pytest} -k "%(keyword)s"',
            ),
        ],
        'params': [{
            'name': 'keyword', 'short': 'k', 'long': 'keyword', 'default': '',
            'help': (
                'Runs only tests that match the string pattern\nSee: '
                'https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests'
            ),
        }],
        'verbosity': 2,
    }


@beartype
def task_coverage() -> DoitTask:
    """Run pytest and create coverage and test reports.

    Returns:
        DoitTask: doit task

    """
    dg = get_dg()
    path_tests = dg.test.path_tests
    cov_dir = dg.test.path_coverage_index.parent
    test_html = f'--html="{dg.test.path_test_report}" --self-contained-html'
    min_cov = f'--cov-fail-under={dg.test.min_cov}' if dg.test.min_cov else ''
    return debug_task([
        Interactive(
            f'poetry run coverage run --source={dg.meta.pkg_name} --module'
            + f' pytest "{path_tests}" {dg.test.args_pytest} {min_cov} {test_html}',
        ),
        'poetry run python -m coverage report --show-missing',
        f'poetry run python -m coverage html --directory={cov_dir}',
        'poetry run python -m coverage json',  # Create coverage.json file for "_write_coverage_to_md"
    ])


# ----------------------------------------------------------------------------------------------------------------------
# Other Test Tools (MyPy, etc.)


@beartype
def task_check_types() -> DoitTask:
    """Run type annotation checks.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive(f'poetry run mypy {get_dg().meta.pkg_name}'),
    ])


# ----------------------------------------------------------------------------------------------------------------------
# Test Output Interaction


@beartype
def task_open_test_docs() -> DoitTask:
    """Open the test and coverage files in default browser.

    Returns:
        DoitTask: doit task

    """
    dg = get_dg()
    paths = [
        dg.test.path_test_report,
        dg.test.path_coverage_index,
        dg.test.path_mypy_index,
    ]
    return debug_task([(open_in_browser, (pth,)) for pth in paths if pth.is_file()])


# ----------------------------------------------------------------------------------------------------------------------
# Implement long running ptw tasks


@beartype
def ptw_task(cli_args: str) -> DoitTask:
    """Return doit Interactive `ptw` task.

    Args:
        cli_args: string CLI args to pass to `ptw`

    Returns:
        DoitTask: doit task

    """
    return {
        'actions': [Interactive(f'poetry run ptw "{get_dg().meta.path_project}" {cli_args}')],
        'verbosity': 2,
    }


@beartype
def task_ptw_not_interactive() -> DoitTask:
    """Run pytest watch for failed first and skip the INTERACTIVE marker.

    >  `-m 'not INTERACTIVE' -vvv`

    Returns:
        DoitTask: doit task

    """
    return ptw_task('-m "not INTERACTIVE" -vvv')


@beartype
def task_ptw_ff() -> DoitTask:
    """Run pytest watch for failed first and skip the INTERACTIVE marker.

    >  `--last-failed --new-first -m 'not INTERACTIVE' -vv`

    Returns:
        DoitTask: doit task

    """
    return ptw_task('--last-failed --new-first -m "not INTERACTIVE" -vv')


@beartype
def task_ptw_current() -> DoitTask:
    """Run pytest watch for only tests with the CURRENT marker.

    >  `-m 'CURRENT' -vv`

    Returns:
        DoitTask: doit task

    """
    return ptw_task('-m "CURRENT" -vv')


@beartype
def task_ptw_marker() -> DoitTask:
    """Specify a marker to run a subset of tests in Interactive `ptw` task.

    Example: `doit run ptw_marker -m "not MARKER"` or `doit run ptw_marker -m "MARKER"`

    Returns:
        DoitTask: doit task

    """
    task = ptw_task('-vvv -m "%(marker)s"')
    task['params'] = [{
        'name': 'marker', 'short': 'm', 'long': 'marker', 'default': '',
        'help': (
            'Runs test with specified marker logic\nSee: '
            'https://docs.pytest.org/en/latest/example/markers.html?highlight=-m'
        ),
    }]
    return task
