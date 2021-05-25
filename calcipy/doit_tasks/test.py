"""doit Test Utilities."""

from doit.tools import LongRunning

from .base import debug_task, open_in_browser
from .doit_globals import DG, DoitTask

# ----------------------------------------------------------------------------------------------------------------------
# Manage Testing


def task_test() -> DoitTask:
    """Run tests with Pytest and stop on the first failure.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        LongRunning(f'poetry run pytest "{DG.test.path_tests}" -x -l --ff -vv'),
    ])


def task_test_all() -> DoitTask:
    """Run all possible tests with Pytest even if one or more failures.

    Returns:
        DoitTask: doit task

    """
    return debug_task([
        LongRunning(f'poetry run pytest "{DG.test.path_tests}" --ff -vv'),
    ])


def task_test_marker() -> DoitTask:
    r"""Specify a marker to run a subset of tests.

    Example: `doit run test_marker -m \"not MARKER\"` or `doit run test_marker -m \"MARKER\"`

    Returns:
        DoitTask: doit task

    """
    task = debug_task([LongRunning(f'poetry run pytest "{DG.test.path_tests}" -x -l --ff -v -m "%(marker)s"')])
    task['params'] = [{
        'name': 'marker', 'short': 'm', 'long': 'marker', 'default': '',
        'help': (
            'Runs test with specified marker logic\nSee: '
            'https://docs.pytest.org/en/latest/example/markers.html?highlight=-m'
        ),
    }]
    return task


def task_test_keyword() -> DoitTask:
    r"""Specify a keyword to run a subset of tests.

    Example: `doit run test_keyword -k \"KEYWORD\"`

    Returns:
        DoitTask: doit task

    """
    return {
        'actions': [
            LongRunning(f'poetry run pytest "{DG.test.path_tests}" -x -l --ff -v -k "%(keyword)s"'),
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


def task_coverage() -> DoitTask:
    """Run pytest and create coverage and test reports.

    Returns:
        DoitTask: doit task

    """
    kwargs = (
        f'--cov-report=html:"{DG.test.path_coverage_index.parent}"  --html="{DG.test.path_report_index}"'
        '  --self-contained-html'
    )
    # Note: removed LongRunning so that doit would catch test failures, but the output will not have colors
    return debug_task([
        LongRunning(f'poetry run pytest "{DG.test.path_tests}" -x -l --ff -v --cov={DG.meta.pkg_name} {kwargs}'),
    ])


def task_check_types() -> DoitTask:
    """Run type annotation checks.

    Returns:
        DoitTask: doit task

    """
    actions = []
    try:
        import pytype  # noqa: F401
        actions.append(LongRunning(f'poetry run pytype {DG.meta.pkg_name}'))
    except ImportError:
        pass

    actions.append(LongRunning(f'poetry run mypy {DG.meta.pkg_name}'))
    return debug_task(actions)


def task_open_test_docs() -> DoitTask:
    """Open the test and coverage files in default browser.

    Returns:
        DoitTask: doit task

    """
    actions = [
        (open_in_browser, (DG.test.path_coverage_index,)),
        (open_in_browser, (DG.test.path_report_index,)),
    ]
    if DG.test.path_mypy_index.is_file():
        actions.append((open_in_browser, (DG.test.path_mypy_index,)))
    return debug_task(actions)


# ----------------------------------------------------------------------------------------------------------------------
# Implement long running ptw tasks


def ptw_task(cli_args: str) -> DoitTask:
    """Return doit LongRunning `ptw` task.

    Args:
        cli_args: string CLI args to pass to `ptw`

    Returns:
        DoitTask: doit task

    """
    return {
        'actions': [LongRunning(f'poetry run ptw -- "{DG.test.path_tests}" {cli_args}')],
        'verbosity': 2,
    }


def task_ptw_not_chrome() -> DoitTask:
    """Return doit LongRunning `ptw` task to run failed first and skip the CHROME marker.

    kwargs: `-m 'not CHROME' -vvv`

    Returns:
        DoitTask: doit task

    """
    return ptw_task('-m "not CHROME" -vvv')


def task_ptw_ff() -> DoitTask:
    """Return doit LongRunning `ptw` task to run failed first and skip the CHROME marker.

    kwargs: `--last-failed --new-first -m 'not CHROME' -vv`

    Returns:
        DoitTask: doit task

    """
    return ptw_task('--last-failed --new-first -m "not CHROME" -vv')


def task_ptw_current() -> DoitTask:
    """Return doit LongRunning `ptw` task to run only tests tagged with the CURRENT marker.

    kwargs: `-m 'CURRENT' -vv`

    Returns:
        DoitTask: doit task

    """
    return ptw_task('-m "CURRENT" -vv')


def task_ptw_marker() -> DoitTask:
    r"""Specify a marker to run a subset of tests in LongRunning `ptw` task.

    Example: `doit run ptw_marker -m \"not MARKER\"` or `doit run ptw_marker -m \"MARKER\"`

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
