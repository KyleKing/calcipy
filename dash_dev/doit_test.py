"""DoIt Test Utilities."""

from doit.tools import LongRunning

from .doit_base import DIG, debug_action, open_in_browser

# ----------------------------------------------------------------------------------------------------------------------
# Manage Testing


def task_test():
    """Run tests with Pytest.

    Returns:
        dict: DoIt task

    """
    return debug_action([
        f'poetry run pytest "{DIG.source_path}" -x -l --ff -v',
    ], verbosity=2)


def task_coverage():
    """Run pytest and create coverage and test reports.

    Returns:
        dict: DoIt task

    """
    coverage_dir = DIG.doc_dir / 'coverage_html'
    test_report_path = DIG.doc_dir / 'test_report.html'
    return debug_action([
        (f'poetry run pytest "{DIG.source_path}" -x -l --ff -v --cov-report=html:"{coverage_dir}" --cov={DIG.pkg_name}'
         f' --html="{test_report_path}" --self-contained-html'),
    ], verbosity=2)


def task_open_test_docs():
    """Open the test and coverage files in default browser.

    Returns:
        dict: DoIt task

    """
    return debug_action([
        (open_in_browser, (DIG.doc_dir / 'coverage_html/index.html',)),
        (open_in_browser, (DIG.doc_dir / 'test_report.html',)),
    ])


def task_test_marker():
    r"""Specify a marker to run a subset of tests.

    Example: `doit run test_marker -m \"not MARKER\"` or `doit run test_marker -m \"MARKER\"`

    Returns:
        dict: DoIt task

    """
    return {
        'actions': [f'poetry run pytest "{DIG.source_path}" -x -l --ff -v -m "%(marker)s"'],
        'params': [{
            'name': 'marker', 'short': 'm', 'long': 'marker', 'default': '',
            'help': ('Runs test with specified marker logic\nSee: '
                     'https://docs.pytest.org/en/latest/example/markers.html?highlight=-m'),
        }],
        'verbosity': 2,
    }


def task_test_keyword():
    r"""Specify a keyword to run a subset of tests.

    Example: `doit run test_keyword -k \"KEYWORD\"`

    Returns:
        dict: DoIt task

    """
    return {
        'actions': [f'poetry run pytest "{DIG.source_path}" -x -l --ff -v -k "%(keyword)s"'],
        'params': [{
            'name': 'keyword', 'short': 'k', 'long': 'keyword', 'default': '',
            'help': ('Runs only tests that match the string pattern\nSee: '
                     'https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests'),
        }],
        'verbosity': 2,
    }

# ----------------------------------------------------------------------------------------------------------------------
# Implement long running ptw tasks


def ptw_task(cli_args):
    """Return DoIt LongRunning `ptw` task.

    Args:
        cli_args: string CLI args to pass to `ptw`

    Returns:
        dict: DoIt task

    """
    return {
        'actions': [LongRunning(f'poetry run ptw -- {cli_args}')],
        'verbosity': 2,
    }


def task_ptw_not_chrome():
    """Return DoIt LongRunning `ptw` task to run failed first and skip the CHROME marker.

    kwargs: `-m 'not CHROME' -vvv`

    Returns:
        dict: DoIt task

    """
    return ptw_task('-m "not CHROME" -vvv')


def task_ptw_ff():
    """Return DoIt LongRunning `ptw` task to run failed first and skip the CHROME marker.

    kwargs: `--last-failed --new-first -m 'not CHROME' -vv`

    Returns:
        dict: DoIt task

    """
    return ptw_task('--last-failed --new-first -m "not CHROME" -vv')


def task_ptw_current():
    """Return DoIt LongRunning `ptw` task to run only tests tagged with the CURRENT marker.

    kwargs: `-m 'CURRENT' -vv`

    Returns:
        dict: DoIt task

    """
    return ptw_task('-m "CURRENT" -vv')
