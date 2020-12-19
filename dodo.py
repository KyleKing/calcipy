"""DoIt Script.

```sh
# Ensure that packages are installed
poetry install
# List Tasks
poetry run doit list
# (Or use a poetry shell)
# > poetry shell
# > doit list

# Run tasks individually (examples below)
poetry doit run coverage open_test_docs
poetry doit run set_lint_config create_tag_file document
# Or all of the tasks in DOIT_CONFIG
poetry run doit
```

"""

from pathlib import Path

from loguru import logger

from calcipy import LOGGER_CONFIG
from calcipy.doit_tasks import *  # skipcq: PYL-W0614 # noqa: F401,F403,H303 (Run 'doit list' to see tasks)
from calcipy.doit_tasks.base import debug_task
from calcipy.doit_tasks.doit_globals import DIG, DoItTask

logger.configure(**LOGGER_CONFIG)
logger.info('Starting DoIt tasks in dodo.py')

# Configure source code root path
DIG.set_paths(path_source=Path(__file__).resolve().parent)

# Create list of all tasks run with `poetry run doit`. Comment on/off as needed
DOIT_CONFIG = {
    'action_string_formatting': 'old',  # Required for keyword-based tasks
    'default_tasks': [
        'export_req',  # 'update_cl',
        'coverage',
        # 'open_test_docs',
        'set_lint_config',
        'create_tag_file',
        'auto_format',
        'document',
        # 'open_docs',
        'lint_pre_commit',
        # 'type_checking',
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
        f'poetry run mypy {DIG.meta.pkg_name}',  # --ignore-missing-imports (see config file...)
        # (note: mypy needs `lxml` for the HTML report output)
    ])
