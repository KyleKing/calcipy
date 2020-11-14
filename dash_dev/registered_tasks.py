"""Registered tasks. Import with the below snippet.

`from dash_dev.registered_tasks import *  # noqa: F401,F403,H303 (Run 'doit list' to see tasks)`

"""

from .doit_helpers.base import task_export_req  # noqa: F401 lgtm [py/unused-import]
from .doit_helpers.doc import (task_tag_create, task_document,  # noqa: F401
                               task_open_docs, task_tag_remove, task_update_cl)
from .doit_helpers.lint import (task_auto_format, task_lint_pre_commit,  # noqa: F401 lgtm [py/unused-import]
                                task_lint_project, task_radon_lint, task_set_lint_config)
from .doit_helpers.test import (task_coverage, task_open_test_docs,  # noqa: F401 lgtm [py/unused-import]
                                task_ptw_current, task_ptw_ff, task_ptw_marker, task_ptw_not_chrome,
                                task_test, task_test_all, task_test_keyword, task_test_marker)
from .tag_collector import task_create_tag_file  # noqa: F401 lgtm [py/unused-import]
