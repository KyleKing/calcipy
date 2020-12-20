"""DoIt Test Utilities."""

from doit.tools import LongRunning

from .base import debug_task, open_in_browser
from .doit_globals import DIG, DoItTask

# ----------------------------------------------------------------------------------------------------------------------
# Manage Testing


def task_test() -> DoItTask:
    """Run tests with Pytest.

    Returns:
        DoItTask: DoIt task

    """
    return debug_task([
        LongRunning(f'poetry run pytest "{DIG.test.path_tests}" -x -l --ff -vv'),
    ])


def task_test_all() -> DoItTask:
    """Run tests with Pytest.

    Returns:
        DoItTask: DoIt task

    """
    return debug_task([
        LongRunning(f'poetry run pytest "{DIG.test.path_tests}" --ff -vv'),
    ])


def task_test_marker() -> DoItTask:
    r"""Specify a marker to run a subset of tests.

    Example: `doit run test_marker -m \"not MARKER\"` or `doit run test_marker -m \"MARKER\"`

    Returns:
        DoItTask: DoIt task

    """
    task = debug_task([LongRunning(f'poetry run pytest "{DIG.test.path_tests}" -x -l --ff -v -m "%(marker)s"')])
    task['params'] = [{
        'name': 'marker', 'short': 'm', 'long': 'marker', 'default': '',
        'help': (
            'Runs test with specified marker logic\nSee: '
            'https://docs.pytest.org/en/latest/example/markers.html?highlight=-m'
        ),
    }]
    return task


def task_test_keyword() -> DoItTask:
    r"""Specify a keyword to run a subset of tests.

    Example: `doit run test_keyword -k \"KEYWORD\"`

    Returns:
        DoItTask: DoIt task

    """
    return {
        'actions': [
            LongRunning(f'poetry run pytest "{DIG.test.path_tests}" -x -l --ff -v -k "%(keyword)s"'),
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


def task_coverage() -> DoItTask:
    """Run pytest and create coverage and test reports.

    Returns:
        DoItTask: DoIt task

    """
    kwargs = (
        f'--cov-report=html:"{DIG.test.path_coverage_index.parent}"  --html="{DIG.test.path_report_index}"'
        '  --self-contained-html'
    )
    # Note: removed LongRunning so that doit would catch test failures, but the output will not have colors
    return debug_task([
        f'poetry run pytest "{DIG.test.path_tests}" -x -l --ff -v --cov={DIG.meta.pkg_name} {kwargs}',
    ])


def task_open_test_docs() -> DoItTask:
    """Open the test and coverage files in default browser.

    Returns:
        DoItTask: DoIt task

    """
    return debug_task([
        (open_in_browser, (DIG.test.path_coverage_index,)),
        (open_in_browser, (DIG.test.path_report_index,)),
    ])


# ----------------------------------------------------------------------------------------------------------------------
# Implement long running ptw tasks


def ptw_task(cli_args: str) -> DoItTask:
    """Return DoIt LongRunning `ptw` task.

    Args:
        cli_args: string CLI args to pass to `ptw`

    Returns:
        DoItTask: DoIt task

    """
    return {
        'actions': [LongRunning(f'poetry run ptw -- "{DIG.test.path_tests}" {cli_args}')],
        'verbosity': 2,
    }


def task_ptw_not_chrome() -> DoItTask:
    """Return DoIt LongRunning `ptw` task to run failed first and skip the CHROME marker.

    kwargs: `-m 'not CHROME' -vvv`

    Returns:
        DoItTask: DoIt task

    """
    return ptw_task('-m "not CHROME" -vvv')


def task_ptw_ff() -> DoItTask:
    """Return DoIt LongRunning `ptw` task to run failed first and skip the CHROME marker.

    kwargs: `--last-failed --new-first -m 'not CHROME' -vv`

    Returns:
        DoItTask: DoIt task

    """
    return ptw_task('--last-failed --new-first -m "not CHROME" -vv')


def task_ptw_current() -> DoItTask:
    """Return DoIt LongRunning `ptw` task to run only tests tagged with the CURRENT marker.

    kwargs: `-m 'CURRENT' -vv`

    Returns:
        DoItTask: DoIt task

    """
    return ptw_task('-m "CURRENT" -vv')


def task_ptw_marker() -> DoItTask:
    r"""Specify a marker to run a subset of tests in LongRunning `ptw` task.

    Example: `doit run ptw_marker -m \"not MARKER\"` or `doit run ptw_marker -m \"MARKER\"`

    Returns:
        DoItTask: DoIt task

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
