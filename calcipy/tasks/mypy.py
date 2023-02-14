"""TBD CLI."""

from pathlib import Path
from beartype.typing import Dict, List, Tuple, Optional, Callable
from functools import partial
from invoke import task, Context
from beartype import beartype
import logging
from shoal import get_logger
from shoal._log import configure_logger

logger = get_logger()


@task(
    default=True,
    help={},
)
def default(ctx: Context) -> None:
    """TBD."""
    gto = ctx.config.gto
    configure_logger(log_level={3: logging.NOTSET, 2: logging.DEBUG, 1: logging.INFO, 0: logging.WARNING}.get(gto.verbose) or logging.ERROR)

    ctx.run(
        f'poetry run mypy {target_package_name}',  # FIXME: Need the path to the source code directory...
        # FYI: see ../tasks/nox.py for open questions
        echo=True, pty=True,
    )
