"""DoIt Script. Run all tasks with `poetry run doit` or single task with `poetry run doit run update_cl`."""

from pathlib import Path

from dash_dev.doit_base import DIG, task_check_req, task_export_req  # noqa: F401
from dash_dev.doit_doc import (task_create_tag, task_document, task_open_docs, task_remove_tag,  # noqa: F401
                               task_update_cl)
from dash_dev.doit_lint import collect_py_files, lint_project, radon_lint, task_auto_format  # noqa: F401
from dash_dev.doit_test import (task_coverage, task_open_test_docs, task_ptw_current, task_ptw_ff,  # noqa: F401
                                task_ptw_marker, task_ptw_not_chrome, task_test, task_test_all, task_test_keyword,
                                task_test_marker)

# Configure Dash paths
DIG.set_paths(source_path=Path(__file__).parent.resolve())
PACKAGE_FILES = collect_py_files()  # TODO: replace with folder-based linting

# Create list of all tasks run with `poetry run doit`
DOIT_CONFIG = {
    'action_string_formatting': 'old',  # Required for keyword-based tasks
    'default_tasks': [
        'export_req', 'check_req', 'update_cl',  # Comment on/off as needed
        'auto_format',  # Comment on/off as needed
        'lint_pre_commit',  # Comment on/off as needed
        'coverage',  # Comment on/off as needed
        'open_test_docs',  # Comment on/off as needed
        'document',  # Comment on/off as needed
        'open_docs',  # Comment on/off as needed
    ],
}
"""DoIt Configuration Settings. Run with `poetry run doit`."""


def task_lint():
    """Configure `lint` as a task.

    Returns:
        dict: DoIt task

    """
    return lint_project(PACKAGE_FILES)


def task_lint_pre_commit():
    """Create linting task that is more relaxed and just catches linting errors that I do not want in VCS.

    Returns:
        dict: DoIt task

    """
    return lint_project(PACKAGE_FILES, ignore_errors=[
        'AAA01',  # AAA01 / act block in pytest
        'C901',  # C901 / complexity from "max-complexity = 10"
        'D417',  # D417 / missing arg descriptors
        'DAR101', 'DAR201', 'DAR401',  # https://pypi.org/project/darglint/ (Scroll to error codes)
        'DUO106',  # DUO106 / insecure use of os
        'E800',  # E800 / Commented out code
        'G001',  # G001 / logging format for un-indexed parameters
        'H601',  # H601 / class with low cohesion
        'P101', 'P103',  # P101,P103 / format string
        'PD013',
        'PD901',  # PD901 / 'df' is a bad variable name
        'S101',  # S101 / assert
        'S605', 'S607',  # S605,S607 / os.popen(...)
        'T100', 'T101',  # T100,T101 / fixme and todo comments
    ])


def task_radon_lint():
    """Configure `radon_lint` as a task.

    Returns:
        dict: DoIt task

    """
    return radon_lint(PACKAGE_FILES)
