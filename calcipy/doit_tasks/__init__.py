"""doit Helpers.

Register all defaults doit tasks in a dodo.py file with the below snippet:

`from calcipy.doit_tasks import *  # noqa: F401,F403,H303 (Run 'doit list' to see tasks)`

"""

__all__ = [  # noqa: F405
    'DOIT_CONFIG_RECOMMENDED',
    'TASKS_FULL',
    # from .base
    'task_zip_release',
    # from .code_tags
    'task_collect_code_tags',
    # from .doc
    'task_cl_bump_pre',
    'task_cl_bump',
    'task_cl_write',
    'task_deploy_docs',
    'task_document',
    'task_open_docs',
    # from .lint
    'task_auto_format',
    'task_format_py',
    'task_format_toml',
    'task_lint_critical_only',
    'task_lint_project',
    'task_lint_python',
    'task_pre_commit_hooks',
    'task_radon_lint',
    'task_security_checks',
    'task_static_checks',
    # from .packaging
    'task_check_for_stale_packages',
    'task_check_license',
    'task_lock',
    'task_publish',
    # from .test
    'task_check_types',
    'task_coverage',
    'task_nox_test',
    'task_nox_coverage',
    'task_nox',
    'task_open_test_docs',
    'task_ptw_current',
    'task_ptw_ff',
    'task_ptw_marker',
    'task_ptw_not_interactive',
    'task_test_all',
    'task_test_keyword',
    'task_test_marker',
    'task_test',
]

from .base import task_zip_release  # noqa: F401
from .code_tags import task_collect_code_tags  # noqa: F401
from .doc import *  # noqa: F401,F403,H303
from .lint import *  # noqa: F401,F403,H303
from .packaging import *  # noqa: F401,F403,H303
from .summary_reporter import SummaryReporter
from .test import *  # noqa: F401,F403,H303

TASKS_FULL = [
    'collect_code_tags',
    'cl_write',
    'lock',
    'nox_coverage',
    'auto_format',
    'document',
    'check_for_stale_packages',
    'pre_commit_hooks',
    'lint_project',
    'static_checks',
    'security_checks',
    'check_types',
]
"""Full suite of tasks for local development."""

DOIT_CONFIG_RECOMMENDED = {
    'action_string_formatting': 'old',  # Required for keyword-based tasks
    'backend': 'sqlite3',  # Best support for concurrency
    'default_tasks': TASKS_FULL,
    'dep_file': '.doit-db.sqlite',
    'reporter': SummaryReporter,
}
"""doit Configuration Settings. Run with `poetry run doit`."""
