"""Extend Invoke for Calcipy."""

import logging
import os
from pathlib import Path

from beartype import beartype
from beartype.typing import Any, List
from corallium.log import configure_logger, logger
from invoke.context import Context
from pydantic import BaseModel, Field, PositiveInt


class GlobalTaskOptions(BaseModel):
    """Global Task Options."""

    working_dir: Path = Field(default_factory=Path.cwd)
    """Working directory for the program to use globally."""

    file_args: List[Path] = Field(default_factory=list)
    """List of Paths to modify."""

    verbose: PositiveInt = Field(default=0, le=3)
    """Verbosity level."""

    keep_going: bool = False
    """Continue task execution regardless of failure."""


@beartype
def _configure_logger(ctx: Context) -> None:
    """Configure the logger based on task context."""
    verbose = ctx.config.gto.verbose
    log_lookup = {3: logging.NOTSET, 2: logging.DEBUG, 1: logging.INFO, 0: logging.WARNING}
    raw_log_level = log_lookup.get(verbose)
    log_level = logging.ERROR if raw_log_level is None else raw_log_level
    configure_logger(log_level=log_level)


@beartype
def _run_task(func: Any, ctx: Context, *args: Any, show_task_info: bool, **kwargs: Any) -> Any:
    """Run the task function with optional logging."""
    if show_task_info:
        summary = func.__doc__.split('\n')[0]
        logger.text(f'Running {func.__name__}', is_header=True, summary=summary)
        logger.text_debug('With task arguments', args=args, kwargs=kwargs)

    result = func(ctx, *args, **kwargs)

    if show_task_info:
        logger.text('')
        logger.text_debug(f'Completed {func.__name__}', result=result)

    return result


@beartype
def _inner_runner(*, func: Any, ctx: Context, show_task_info: bool, args: Any, kwargs: Any) -> Any:
    try:
        ctx.config.gto  # noqa: B018
    except AttributeError:
        ctx.config.gto = GlobalTaskOptions()

    # Begin utilizing Global Task Options
    os.chdir(ctx.config.gto.working_dir)
    _configure_logger(ctx)

    try:
        return _run_task(func, ctx, *args, show_task_info=show_task_info, **kwargs)
    except Exception:
        if not ctx.config.gto.keep_going:
            raise
        logger.exception('Task Failed', func=str(func), args=args, kwargs=kwargs)
    return None
