"""doit Helpers.

Register all defaults doit tasks in a dodo.py file with the below snippet:

`from calcipy.doit_tasks import *  # noqa: F401,F403,H303 (Run 'doit list' to see tasks). skipcq: PYL-W0614`

"""

__all__ = [  # noqa: F405
    'DOIT_CONFIG_RECOMMENDED',
    # from .code_tag_collector
    'task_collect_code_tags',
    # from .doc
    'task_cl_bump',
    'task_cl_bump_pre',
    'task_cl_write',
    'task_deploy',
    'task_document',
    'task_open_docs',
    'task_serve_fast',
    # from .lint
    'task_auto_format',
    'task_lint_critical_only',
    'task_lint_project',
    'task_pre_commit_hooks',
    'task_radon_lint',
    # from .test
    'task_check_types',
    'task_coverage',
    'task_open_test_docs',
    'task_ptw_current',
    'task_ptw_ff',
    'task_ptw_marker',
    'task_ptw_not_chrome',
    'task_test_all',
    'task_test_keyword',
    'task_test_marker',
    'task_test',
]

from .code_tag_collector import task_collect_code_tags
from .doc import *  # noqa: F401,F403,H303. lgtm [py/polluting-import]
from .lint import *  # noqa: F401,F403,H303. lgtm [py/polluting-import]
from .test import *  # noqa: F401,F403,H303. lgtm [py/polluting-import]

DOIT_CONFIG_RECOMMENDED = {
    'action_string_formatting': 'old',  # Required for keyword-based tasks
    'default_tasks': [
        'collect_code_tags',
        'coverage',
        'auto_format',
        'document',
        'pre_commit_hooks',
        'lint_critical_only',
        'check_types',
    ],
}
"""doit Configuration Settings. Run with `poetry run doit`."""
