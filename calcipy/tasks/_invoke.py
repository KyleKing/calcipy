"""Extend Invoke for Calcipy."""

import logging
import os
from contextlib import wraps
from pathlib import Path
from types import ModuleType

from beartype import beartype
from beartype.typing import Any, Dict, List, Optional, Tuple
from corallium.log import configure_logger, logger
from invoke.collection import Collection as InvokeCollection  # noqa: TID251
from invoke.context import Context
from invoke.tasks import Task
from pydantic import BaseModel, Field, PositiveInt

TASK_ARGS_ATTR = 'dev_args'
TASK_KWARGS_ATTR = 'dev_kwargs'


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
def _configure_task_logger(ctx: Context) -> None:
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
def _wrapped_task(ctx: Context, *args: Any, func: Any, show_task_info: bool, **kwargs: Any) -> Any:
    """Extended task logic."""
    try:
        ctx.config.gto  # noqa: B018
    except AttributeError:
        ctx.config.gto = GlobalTaskOptions()

    # Begin utilizing Global Task Options
    os.chdir(ctx.config.gto.working_dir)
    _configure_task_logger(ctx)

    try:
        return _run_task(func, ctx, *args, show_task_info=show_task_info, **kwargs)
    except Exception:
        if not ctx.config.gto.keep_going:
            raise
        logger.exception('Task Failed', func=str(func), args=args, kwargs=kwargs)
    return None


def _build_task(task: Any) -> 'Task':
    """Defer creation of the Task."""

    @wraps(task)
    def inner(*args: Any, **kwargs: Any) -> Any:
        return _wrapped_task(*args, func=task, show_task_info=show_task_info, **kwargs)

    if hasattr(task, TASK_ARGS_ATTR):
        kwargs = getattr(task, TASK_KWARGS_ATTR)
        show_task_info = kwargs.pop('show_task_info', None) or False
        return Task(inner, *getattr(task, TASK_ARGS_ATTR), **kwargs)
    return task


class Collection(InvokeCollection):

    def __repr__(self) -> str:
        """Update the representation to indicate the difference."""
        return super().__repr__().replace('Collection', 'Calcipy:Collection')

    @classmethod
    def from_module(
        cls,
        module: ModuleType,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        loaded_from: Optional[str] = None,
        auto_dash_names: Optional[bool] = None,
    ) -> 'InvokeCollection':
        """Extend search for a namespace, Task, or deferred task."""
        collection = super().from_module(
            module=module,
            name=name,
            config=config,
            loaded_from=loaded_from,
            auto_dash_names=auto_dash_names)

        # If tasks were not loaded from a namespace or otherwise found
        if not collection.task_names:
            # Look for any decorated, but deferred "Tasks"
            for task in (fxn for fxn in vars(module).values() if hasattr(fxn, TASK_ARGS_ATTR)):
                collection.add_task(task)

        return collection

    def add_task(
        self,
        task: 'Task',
        name: Optional[str] = None,
        aliases: Optional[Tuple[str, ...]] = None,
        default: Optional[bool] = None,
    ) -> None:
        """Extend for deferred tasks."""
        super().add_task(task=_build_task(task), name=name, aliases=aliases, default=default)
