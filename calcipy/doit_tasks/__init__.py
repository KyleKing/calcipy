"""DoIt Helpers.

Register all defaults DoIt tasks in a dodo.py file with the below snippet:

`from calcipy.doit_tasks import *  # noqa: F401,F403,H303 (Run 'doit list' to see tasks). skipcq: PYL-W0614`

"""

__all__ = [  # noqa: F405
    # from .base
    'task_export_req',
    # from .doc
    'task_document',
    'task_open_docs',
    'task_tag_create',
    'task_tag_remove',
    'task_cl_bump',
    'task_cl_write',
    # from .lint
    'task_auto_format',
    'task_lint_project',
    'task_lint_critical_only',
    'task_pre_commit_hooks',
    'task_radon_lint',
    'task_set_lint_config',
    # from ..tag_collector
    'task_create_tag_file',
    # from .test
    'task_coverage',
    'task_open_test_docs',
    'task_ptw_current',
    'task_ptw_ff',
    'task_ptw_marker',
    'task_ptw_not_chrome',
    'task_test',
    'task_test_all',
    'task_test_keyword',
    'task_test_marker',
]

from .base import *  # noqa: F401,F403,H303. lgtm [py/polluting-import]
from .doc import *  # noqa: F401,F403,H303. lgtm [py/polluting-import]
from .lint import *  # noqa: F401,F403,H303. lgtm [py/polluting-import]
from .tag_collector import task_create_tag_file
from .test import *  # noqa: F401,F403,H303. lgtm [py/polluting-import]
