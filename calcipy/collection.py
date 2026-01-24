"""Extend Invoke for Calcipy."""

from __future__ import annotations

import logging
import os
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass, field
from functools import wraps
from io import StringIO
from pathlib import Path
from types import ModuleType

from beartype.typing import Any, Callable, Dict, List, Optional, Tuple, Union
from corallium.log import LOGGER, configure_logger
from invoke.collection import Collection as InvokeCollection  # noqa: TID251
from invoke.context import Context
from invoke.tasks import Task

TASK_ARGS_ATTR = 'dev_args'
TASK_KWARGS_ATTR = 'dev_kwargs'

DeferredTask = Union[Callable, Task]  # type: ignore[type-arg]

LOG_LOOKUP = {3: logging.NOTSET, 2: logging.DEBUG, 1: logging.INFO, 0: logging.WARNING}


@dataclass
class GlobalTaskOptions:
    """Global Task Options."""

    working_dir: Path = field(default_factory=Path.cwd)
    """Working directory for the program to use globally."""

    file_args: List[Path] = field(default_factory=list)
    """List of Paths to modify."""

    verbose: int = field(default=0)
    """Verbosity level."""

    keep_going: bool = False
    """Continue task execution regardless of failure."""

    capture_output: bool = False
    """Capture stdout and stderr output from tasks."""

    def __post_init__(self) -> None:
        """Validate dataclass."""
        options_verbose = [*LOG_LOOKUP.keys()]
        if self.verbose not in options_verbose:
            error = f'verbose must be one of: {options_verbose}'
            raise ValueError(error)


def _configure_task_logger(ctx: Context) -> None:  # pragma: no cover
    """Configure the logger based on task context."""
    verbose = ctx.config.gto.verbose
    raw_log_level = LOG_LOOKUP.get(verbose)
    log_level = logging.ERROR if raw_log_level is None else raw_log_level
    configure_logger(log_level=log_level)


def _run_task(func: Any, ctx: Context, *args: Any, show_task_info: bool, **kwargs: Any) -> Any:  # pragma: no cover
    """Run the task function with optional logging."""
    if show_task_info:
        summary = func.__doc__.split('\n')[0]
        LOGGER.text(f'Running {func.__name__}', is_header=True, summary=summary)
        LOGGER.text_debug('With task arguments', args=args, kwargs=kwargs)

    if ctx.config.gto.capture_output:
        stdout_capture = StringIO()
        stderr_capture = StringIO()
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            result = func(ctx, *args, **kwargs)
        captured_stdout = stdout_capture.getvalue()
        captured_stderr = stderr_capture.getvalue()
        if show_task_info:
            if captured_stdout:
                LOGGER.text_debug('Captured stdout', output=captured_stdout)
            if captured_stderr:
                LOGGER.text_debug('Captured stderr', output=captured_stderr)
    else:
        result = func(ctx, *args, **kwargs)

    if show_task_info:
        LOGGER.text('')
        LOGGER.text_debug(f'Completed {func.__name__}', result=result)

    return result


def _wrapped_task(ctx: Context, *args: Any, func: Any, show_task_info: bool, **kwargs: Any) -> Any:  # pragma: no cover
    """Wrap task with extended logic."""
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
        LOGGER.exception('Task Failed', func=str(func), args=args, kwargs=kwargs)
    return None


def _build_task(task: DeferredTask) -> Task:  # type: ignore[type-arg]  # pragma: no cover
    """Defer creation of the Task."""
    if hasattr(task, TASK_ARGS_ATTR) or hasattr(task, TASK_KWARGS_ATTR):

        @wraps(task)
        def inner(*args: Any, **kwargs: Any) -> Any:
            return _wrapped_task(*args, func=task, show_task_info=show_task_info, **kwargs)

        kwargs = getattr(task, TASK_KWARGS_ATTR)
        show_task_info = kwargs.pop('show_task_info', None) or False
        pre = [_build_task(pre) for pre in kwargs.pop('pre', None) or []]
        post = [_build_task(post) for post in kwargs.pop('post', None) or []]
        return Task(inner, *getattr(task, TASK_ARGS_ATTR), pre=pre, post=post, **kwargs)  # type: ignore[misc,arg-type]
    return task  # type: ignore[return-value]


class Collection(InvokeCollection):
    """Calcipy Task Collection."""

    @classmethod
    def from_module(
        cls,
        module: ModuleType,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        loaded_from: Optional[str] = None,
        auto_dash_names: Optional[bool] = None,
    ) -> InvokeCollection:
        """Extend search for a namespace, Task, or deferred task.

        Returns:
            Collection populated with tasks from the module.

        """
        collection = super().from_module(
            module=module,
            name=name,
            config=config,
            loaded_from=loaded_from,
            auto_dash_names=auto_dash_names,
        )

        # If tasks were not loaded from a namespace or otherwise found
        if not collection.task_names:
            # Look for any decorated, but deferred "Tasks"
            for task in (fxn for fxn in vars(module).values() if hasattr(fxn, TASK_ARGS_ATTR)):
                collection.add_task(task)

        return collection

    def add_task(
        self,
        task: DeferredTask,
        name: Optional[str] = None,
        aliases: Optional[Tuple[str, ...]] = None,
        default: Optional[bool] = None,
    ) -> None:
        """Extend for deferred tasks."""
        super().add_task(task=_build_task(task), name=name, aliases=aliases, default=default)
