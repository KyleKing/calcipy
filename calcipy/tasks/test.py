"""Test CLI."""

from contextlib import suppress
from pathlib import Path
from beartype.typing import Dict, List, Tuple, Optional, Callable
from functools import partial
from invoke import task, Context
from beartype import beartype
import logging
from shoal import get_logger
from shoal._log import configure_logger

logger = get_logger()

_STEPWISE_ARGS = ' --failed-first --new-first --exitfirst -vv --no-cov'


@beartype
def _inner_task(ctx: Context, *, cli_args: str, target: str = 'python -m pytest') -> None:
    """Shared task logic."""
    verbose = 2
    with suppress(AttributeError):
        verbose = ctx.config.gto.verbose
    configure_logger(log_level={3: logging.NOTSET, 2: logging.DEBUG, 1: logging.INFO, 0: logging.WARNING}.get(verbose) or logging.ERROR)

    ctx.run(
        f'poetry run {target} ./tests{cli_args}',
        # FYI: see ../tasks/nox.py for open questions
        echo=True, pty=True,
    )


@task(
    default=True,
    help={
        # See: https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests
        'keyword': 'Only run tests that match the string pattern',
        'marker': 'Only run tests matching given mark expression',
    },
)
def default(ctx: Context, keyword: str = '', marker: str = '') -> None:
    """Run pytest with default arguments."""
    cli_args = ''
    if keyword:
        cli_args += f' -k "{keyword}"'
    if marker:
        cli_args += f' -m "{marker}"'
    _inner_task(ctx, cli_args=cli_args)


@task(help=default.help)
def step(ctx: Context, keyword: str = '', marker: str = '') -> None:
    """Run pytest with default arguments."""
    cli_args = _STEPWISE_ARGS
    if keyword:
        cli_args += f' -k "{keyword}"'
    if marker:
        cli_args += f' -m "{marker}"'
    _inner_task(ctx, cli_args=cli_args)


@task(help=default.help)
def watch(ctx: Context, keyword: str = '', marker: str = '') -> None:
    """Run pytest with default arguments."""
    cli_args = _STEPWISE_ARGS
    if keyword:
        cli_args += f' -k "{keyword}"'
    if marker:
        cli_args += f' -m "{marker}"'
    _inner_task(ctx, cli_args=cli_args, target='ptw . --now')


# TODO: Coverage (sequence of commands)
