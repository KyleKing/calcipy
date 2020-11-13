"""DoIt Test Utilities."""

from typing import Any, Dict

from doit.tools import LongRunning

from .doit_base import DIG, debug_action, open_in_browser

# ----------------------------------------------------------------------------------------------------------------------
# Manage Testing


def task_test() -> Dict[str, Any]:
    """Run tests with Pytest.

    Returns:
        Dict[str, Any]: DoIt task

    """
    return debug_action([
        f'poetry run pytest "{DIG.test_path}" -x -l --ff -vv',
    ], verbosity=2)


def task_test_all() -> Dict[str, Any]:
    """Run tests with Pytest.

    Returns:
        Dict[str, Any]: DoIt task

    """
    return debug_action([
        f'poetry run pytest "{DIG.test_path}" --ff -vv',
    ], verbosity=2)


def task_test_marker() -> Dict[str, Any]:
    r"""Specify a marker to run a subset of tests.

    Example: `doit run test_marker -m \"not MARKER\"` or `doit run test_marker -m \"MARKER\"`

    Returns:
        Dict[str, Any]: DoIt task

    """
    return {
        'actions': [f'poetry run pytest "{DIG.test_path}" -x -l --ff -v -m "%(marker)s"'],
        'params': [{
            'name': 'marker', 'short': 'm', 'long': 'marker', 'default': '',
            'help': ('Runs test with specified marker logic\nSee: '
                     'https://docs.pytest.org/en/latest/example/markers.html?highlight=-m'),
        }],
        'verbosity': 2,
    }


def task_test_keyword() -> Dict[str, Any]:
    r"""Specify a keyword to run a subset of tests.

    Example: `doit run test_keyword -k \"KEYWORD\"`

    Returns:
        Dict[str, Any]: DoIt task

    """
    return {
        'actions': [f'poetry run pytest "{DIG.test_path}" -x -l --ff -v -k "%(keyword)s"'],
        'params': [{
            'name': 'keyword', 'short': 'k', 'long': 'keyword', 'default': '',
            'help': ('Runs only tests that match the string pattern\nSee: '
                     'https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests'),
        }],
        'verbosity': 2,
    }


def task_coverage() -> Dict[str, Any]:
    """Run pytest and create coverage and test reports.

    Returns:
        Dict[str, Any]: DoIt task

    """
    kwargs = f'--cov-report=html:"{DIG.coverage_path.parent}"  --html="{DIG.test_report_path}"  --self-contained-html'
    return debug_action([
        (f'poetry run pytest "{DIG.test_path}" -x -l --ff -v --cov={DIG.pkg_name} {kwargs}'),
    ], verbosity=2)


def task_open_test_docs() -> Dict[str, Any]:
    """Open the test and coverage files in default browser.

    Returns:
        Dict[str, Any]: DoIt task

    """
    return debug_action([
        (open_in_browser, (DIG.coverage_path, )),
        (open_in_browser, (DIG.test_report_path, )),
    ])


# ----------------------------------------------------------------------------------------------------------------------
# Implement long running ptw tasks


def ptw_task(cli_args: str) -> Dict[str, Any]:
    """Return DoIt LongRunning `ptw` task.

    Args:
        cli_args: string CLI args to pass to `ptw`

    Returns:
        Dict[str, Any]: DoIt task

    """
    return {
        'actions': [LongRunning(f'poetry run ptw -- "{DIG.test_path}" {cli_args}')],
        'verbosity': 2,
    }


def task_ptw_not_chrome() -> Dict[str, Any]:
    """Return DoIt LongRunning `ptw` task to run failed first and skip the CHROME marker.

    kwargs: `-m 'not CHROME' -vvv`

    Returns:
        Dict[str, Any]: DoIt task

    """
    return ptw_task('-m "not CHROME" -vvv')


def task_ptw_ff() -> Dict[str, Any]:
    """Return DoIt LongRunning `ptw` task to run failed first and skip the CHROME marker.

    kwargs: `--last-failed --new-first -m 'not CHROME' -vv`

    Returns:
        Dict[str, Any]: DoIt task

    """
    return ptw_task('--last-failed --new-first -m "not CHROME" -vv')


def task_ptw_current() -> Dict[str, Any]:
    """Return DoIt LongRunning `ptw` task to run only tests tagged with the CURRENT marker.

    kwargs: `-m 'CURRENT' -vv`

    Returns:
        Dict[str, Any]: DoIt task

    """
    return ptw_task('-m "CURRENT" -vv')


def task_ptw_marker() -> Dict[str, Any]:
    r"""Specify a marker to run a subset of tests in LongRunning `ptw` task.

    Example: `doit run ptw_marker -m \"not MARKER\"` or `doit run ptw_marker -m \"MARKER\"`

    Returns:
        Dict[str, Any]: DoIt task

    """
    task = ptw_task('-vvv -m "%(marker)s"')
    task['params'] = [{
        'name': 'marker', 'short': 'm', 'long': 'marker', 'default': '',
        'help': ('Runs test with specified marker logic\nSee: '
                 'https://docs.pytest.org/en/latest/example/markers.html?highlight=-m'),
    }]
    return task
