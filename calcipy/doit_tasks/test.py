"""doit Test Utilities."""

from beartype import beartype
from doit.tools import Interactive

from .base import debug_task, open_in_browser
from .doit_globals import DG, DoitTask

# ----------------------------------------------------------------------------------------------------------------------
# Manage Testing with Nox


@beartype
def task_nox() -> DoitTask:
    """Run the full nox test suite.

    > Note: some nox tasks are run in more-specific doit tasks, but this will run everything

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive('poetry run nox'),
    ])


@beartype
def task_nox_test() -> DoitTask:
    """Run the nox tests sessions.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive('poetry run nox --session tests'),
    ])


@beartype
def task_nox_coverage() -> DoitTask:
    """Run the coverage session in nox.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive('poetry run nox --session coverage'),
    ])


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
    return debug_task([
        Interactive(f'poetry run python -m pytest "{DG.test.path_tests}" {DG.test.args_pytest}'),
    ])


@beartype
def task_test_all() -> DoitTask:
    """Run all possible tests with Pytest even if one or more failures.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        Interactive(f'poetry run python -m pytest "{DG.test.path_tests}" --ff -vv'),
    ])


@beartype
def task_test_marker() -> DoitTask:
    """Specify a marker to run a subset of tests.

    Example: `doit run test_marker -m "not MARKER"` or `doit run test_marker -m "MARKER"`

    Returns:
        DoitTask: doit task

    """
    task = debug_task(
        [Interactive(f'poetry run python -m pytest "{DG.test.path_tests}" {DG.test.args_pytest} -m "%(marker)s"')],
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
    return {
        'actions': [
            Interactive(f'poetry run python -m pytest "{DG.test.path_tests}" {DG.test.args_pytest} -k "%(keyword)s"'),
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
    path_tests = DG.test.path_tests
    cov_dir = DG.test.path_coverage_index.parent
    test_html = f'--html="{DG.test.path_test_report}" --self-contained-html'
    diff_html = f'--html-report {DG.test.path_diff_test_report}'
    return debug_task([
        Interactive(
            f'poetry run coverage run --source={DG.meta.pkg_name} --module'
            f' pytest "{path_tests}" {DG.test.args_pytest} {test_html}',
        ),
        'poetry run python -m coverage report --show-missing',
        f'poetry run python -m coverage html --directory={cov_dir}',
        'poetry run python -m coverage json',  # Create coverage.json file for "_write_coverage_to_md"
        'poetry run python -m coverage xml',
        Interactive(f'poetry run diff-cover coverage.xml {DG.test.args_diff} {diff_html}'),
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
        Interactive(f'poetry run mypy {DG.meta.pkg_name} --show-error-codes'),
    ])


# ----------------------------------------------------------------------------------------------------------------------
# Test Output Interaction


@beartype
def task_open_test_docs() -> DoitTask:
    """Open the test and coverage files in default browser.

    Returns:
        DoitTask: doit task

    """
    paths = [
        DG.test.path_test_report,
        DG.test.path_diff_test_report,
        DG.test.path_diff_lint_report,
        DG.test.path_coverage_index,
        DG.test.path_mypy_index,
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
        'actions': [Interactive(f'poetry run ptw "{DG.meta.path_project}" {cli_args}')],
        'verbosity': 2,
    }


@beartype
def task_ptw_not_interactive() -> DoitTask:
    """Run pytest watch for failed first and skip the INTERACTIVE marker.

    kwargs: `-m 'not INTERACTIVE' -vvv`

    Returns:
        DoitTask: doit task

    """
    return ptw_task('-m "not INTERACTIVE" -vvv')


@beartype
def task_ptw_ff() -> DoitTask:
    """Run pytest watch for failed first and skip the INTERACTIVE marker.

    kwargs: `--last-failed --new-first -m 'not INTERACTIVE' -vv`

    Returns:
        DoitTask: doit task

    """
    return ptw_task('--last-failed --new-first -m "not INTERACTIVE" -vv')


@beartype
def task_ptw_current() -> DoitTask:
    """Run pytest watch for only tests with the CURRENT marker.

    kwargs: `-m 'CURRENT' -vv`

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
