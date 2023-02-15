"""Lint CLI."""

import logging
from contextlib import suppress

from beartype import beartype
from invoke import Context, task
from shoal import get_logger
from shoal._log import configure_logger

from .cached_utilities import read_package_name

logger = get_logger()


@beartype
def _inner_task(ctx: Context, *, cli_args: str, target: str) -> None:
    """Shared task logic."""
    verbose = 2
    with suppress(AttributeError):
        verbose = ctx.config.gto.verbose
    configure_logger(log_level={3: logging.NOTSET, 2: logging.DEBUG, 1: logging.INFO, 0: logging.WARNING}.get(verbose) or logging.ERROR)

    pkg_name = read_package_name()
    ctx.run(
        f'poetry run {target} {pkg_name}{cli_args}',
        # FYI: see ../tasks/nox.py for open questions
        echo=True, pty=True,
    )


@task(
    default=True,
    help={
    },
)
def fix(ctx: Context) -> None:
    """Run ruff and apply fixes."""
    _inner_task(ctx, cli_args=' --fix', target='python -m ruff check')


@task(help={})
def check(ctx: Context) -> None:
    """Run ruff as check-only."""
    _inner_task(ctx, cli_args='', target='python -m ruff check')
