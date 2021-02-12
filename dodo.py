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

# TODO: cz_legacy - don't overwrite the init file
# TODO: cz_legacy - no mkdocs.yml file. Fix this with copier?

from pathlib import Path

from loguru import logger

from calcipy import __pkg_name__
from calcipy.doit_tasks import *  # noqa: F401,F403,H303 (Run 'doit list' to see tasks). skipcq: PYL-W0614
from calcipy.doit_tasks import DOIT_CONFIG_RECOMMENDED
from calcipy.doit_tasks.base import debug_task
from calcipy.doit_tasks.doit_globals import DIG, DoItTask
from calcipy.log_helpers import build_logger_config

logger.enable(__pkg_name__)  # This will enable output from calcipy, which is off by default
# See an example of toggling loguru at: https://github.com/KyleKing/calcipy/tree/examples/loguru-toggle

path_parent = Path(__file__).resolve().parent
log_config = build_logger_config(path_parent, production=False)
logger.configure(**log_config)
logger.info(
    'Started logging to {path_parent}/.logs with {log_config}', path_parent=path_parent,
    log_config=log_config,
)

logger.info('Starting doit tasks in dodo.py')

# Configure source code root path
DIG.set_paths(path_project=path_parent)

# Create list of all tasks run with `poetry run doit`
DOIT_CONFIG = DOIT_CONFIG_RECOMMENDED


# TODO: Implement type checking with pytype, mypy, or other
def task_type_checking() -> DoItTask:
    """Run type annotation checks.

    Returns:
        DoItTask: doit task

    """
    return debug_task([
        # 'poetry run pytype --config pytype.cfg',
        f'poetry run mypy {DIG.meta.pkg_name}',  # --ignore-missing-imports (see config file...)
        # (note: mypy needs `lxml` for the HTML report output)
    ])
