"""Lint CLI."""

import logging
from contextlib import suppress

from beartype import beartype
from beartype.typing import Optional
from invoke import Context, task
from shoal import get_logger
from shoal._log import configure_logger

from .cached_utilities import read_package_name

logger = get_logger()


@beartype
def _inner_task(ctx: Context, *, cli_args: str, command: str = 'python -m ruff check', target: Optional[str] = None) -> None:
    """Shared task logic."""
    verbose = 2
    with suppress(AttributeError):
        verbose = ctx.config.gto.verbose
    log_lookup = {3: logging.NOTSET, 2: logging.DEBUG, 1: logging.INFO, 0: logging.WARNING}
    configure_logger(log_level=log_lookup.get(verbose) or logging.ERROR)

    target = f' ./{read_package_name()} ./tests' if target is None else f' {target}'
    ctx.run(
        f'poetry run {command}{target}{cli_args}',
        # FYI: see ../tasks/nox.py for open questions
        echo=True, pty=True,
    )


@task(
    default=True,
    help={
        # TODO: use file_args! 'ctx.config.gto.file_args'
        'target': 'Optional path to directory or file to watch',
    },
)
def fix(ctx: Context, *, target: Optional[str] = None) -> None:
    """Run ruff and apply fixes."""
    _inner_task(ctx, cli_args=' --fix', target=target)


@task(help=fix.help)
def check(ctx: Context, *, target: Optional[str] = None) -> None:
    """Run ruff as check-only."""
    _inner_task(ctx, cli_args='', target=target)


@task(help=fix.help)
def watch(ctx: Context, *, target: Optional[str] = None) -> None:
    """Run ruff as check-only."""
    _inner_task(ctx, cli_args=' --watch --show-source', target=target)
