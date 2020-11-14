"""DoIt Script. Run all tasks with `poetry run doit` or single task with `poetry run doit run update_cl`."""

from pathlib import Path

from dash_dev.doit_base import DIG, DoItTask, debug_task, task_export_req  # noqa: F401
from dash_dev.doit_dev import task_watchcode  # noqa: F401
from dash_dev.doit_doc import (task_create_tag, task_document,  # noqa: F401
                               task_open_docs, task_remove_tag, task_update_cl)
from dash_dev.doit_lint import (task_auto_format, task_lint_pre_commit,  # noqa: F401
                                task_lint_project, task_radon_lint, task_set_lint_config)
from dash_dev.doit_test import (task_coverage, task_open_test_docs, task_ptw_current,  # noqa: F401
                                task_ptw_ff, task_ptw_marker, task_ptw_not_chrome, task_test,
                                task_test_all, task_test_keyword, task_test_marker)
from dash_dev.tag_collector import task_create_tag_file  # noqa: F401

# Configure Dash paths
DIG.set_paths(source_path=Path(__file__).resolve().parent)

# Create list of all tasks run with `poetry run doit`. Comment on/off as needed
DOIT_CONFIG = {
    'action_string_formatting': 'old',  # Required for keyword-based tasks
    'default_tasks': [
        'export_req', 'update_cl',
        'coverage',
        # 'open_test_docs',
        'set_lint_config',
        'create_tag_file',
        'auto_format',
        'lint_pre_commit',
        # 'type_checking',
        'document',
        # 'open_docs',
    ],
}
"""DoIt Configuration Settings. Run with `poetry run doit`."""


# TODO: Implement type checking with pytype, mypy, etc.
def task_type_checking() -> DoItTask:
    """Run type annotation checks.

    Returns:
        DoItTask: DoIt task

    """
    return debug_task([
        # 'poetry run pytype --config pytype.cfg',
        f'poetry run mypy {DIG.pkg_name}',  # --ignore-missing-imports (see config file...)
        # (note: mypy needs `lxml` for the HTML report output)
    ])
