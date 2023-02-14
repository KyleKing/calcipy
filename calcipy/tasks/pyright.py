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

@beartype
def _inner_task(ctx: Context, *, cli_args: List[str]) -> None:
    """Shared task logic."""
    gto = ctx.config.gto
    configure_logger(log_level={3: logging.NOTSET, 2: logging.DEBUG, 1: logging.INFO, 0: logging.WARNING}.get(gto.verbose) or logging.ERROR)

    ctx.run(
        f'poetry run TBD {" ".join(cli_args)}',
        # FYI: see ../tasks/nox.py for open questions
        echo=True, pty=True,
    )


@task(
    default=True,
    help={},
)
def default(ctx: Context) -> None:
    """TBD."""
    _inner_task(ctx, cli_args=[])
