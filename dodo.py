"""doit Script.

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

from calcipy import __pkg_name__
from calcipy.doit_tasks import *  # noqa: F401,F403,H303 (Run 'doit list' to see tasks). skipcq: PYL-W0614
from calcipy.doit_tasks import DIG, DOIT_CONFIG_RECOMMENDED, DoItTask, debug_task
from calcipy.log_helpers import build_logger_config

logger.enable(__pkg_name__)  # This will enable output from calcipy, which is off by default
# See an example of toggling loguru at: https://github.com/KyleKing/calcipy/tree/examples/loguru-toggle

path_project = Path(__file__).resolve().parent
log_config = build_logger_config(path_project, production=False)
logger.configure(**log_config)
logger.info(
    'Started logging to {path_project}/.logs with {log_config}', path_project=path_project,
    log_config=log_config,
)

# Create list of all tasks run with `poetry run doit`
DOIT_CONFIG = DOIT_CONFIG_RECOMMENDED
DOIT_CONFIG['default_tasks'].append('check_types')


# TODO: Implement type checking with mypy
def task_check_types() -> DoItTask:
    """Run type annotation checks.

    Returns:
        DoItTask: doit task

    """
    return debug_task([
        f'poetry run mypy {DIG.meta.pkg_name}',
    ])
