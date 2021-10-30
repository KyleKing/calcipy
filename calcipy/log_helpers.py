"""Loguru Helpers."""

# PLANNED: consider a STDOUT format like https://pypi.org/project/readable-log-formatter
#   Colorful Debug Level / Parent/FileName / Line NUmber
#       Indented and wrapped summary string
#       Indented, optional variables (would otherwise not be shown) (i.e. **{name}**: {value})
#   Note: need to ensure that exception tracebacks are properly handled with a custom format
#       See: https://github.com/Delgan/loguru/issues/156
#           And: https://loguru.readthedocs.io/en/stable/api/logger.html#message
#       Or: https://github.com/Delgan/loguru/issues/133

from __future__ import annotations

import json
import logging
import sys
import time
from inspect import signature
from pathlib import Path
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional

from beartype import beartype
from decorator import contextmanager, decorator
from loguru import logger

from .file_helpers import delete_old_files


@beartype
def serializable_compact(record: Dict[str, Any]) -> str:
    """Loguru formatter to return a compact JSON string for JSONLines output.

    `record` documentation: https://loguru.readthedocs.io/en/stable/api/logger.html#record

    Based on the `_serialize_record` method:
    https://github.com/Delgan/loguru/blob/44f6771/loguru/_handler.py#L222

    ```python3
    from calcipy.log_helpers import serializable_compact

    logger.add(LOG_DIR / 'pkg-compact-{time}.jsonl', mode='w', level=logging.INFO,
               format=serializable_compact)
    ```

    Args:
        record: dictionary passed by loguru for formatting

    Returns:
        str: dumped JSON without newlines

    """
    exception = record['exception']
    if exception:
        exception = {
            'type': None if exception.type is None else exception.type.__name__,
            'value': exception.value,
            'traceback': bool(record['exception'].traceback),
        }
    simplified = {
        'record': {
            'exception': exception,
            'extra': record['extra'],
            'file': {'path': record['file'].path},
            'function': record['function'].strip('<>'),
            'level': {'name': record['level'].name},
            'line': record['line'],
            'message': record['message'],
            'module': record['module'],
            'name': record['name'],
            'time': {'timestamp': record['time'].timestamp()},
        },
    }
    str_json: str = json.dumps(simplified, default=str).replace('{', '{{').replace('}', '}}')
    return str_json + '\n'


# Note: loguru.Logger is PEP563 Postponed and can't be use with beartype runtime

def _log_action(
    message: str, level: str = 'INFO',
    _logger: loguru.Logger = logger,  # pylint: disable=no-member
    **kwargs: Any,
) -> Generator[loguru.Logger, None, None]:  # pylint: disable=no-member
    """Log the beggining and end of an action.

    Args:
        message: string message to describe the context
        level: log level. Default is `INFO`
        _logger: Optional logger instance
        kwargs: function keyword arguments passed to the start log statement

    Yields:
        yields the logger instance

    """
    start_time = time.time_ns()
    _logger.log(level, f'(start) {message}', start_time=start_time, **kwargs)
    yield _logger
    runtime = time.time_ns() - start_time
    _logger.log(level, f'(end) {message}', start_time=start_time, runtime=runtime)


# When using `contextmanager` as a decorator, Deepsource won't see the __enter__/__exit__ methods (PYL-E1129)
#   Rather than skipping each use of log_action, use `contextmanager` as a function
log_action = contextmanager(_log_action)


@decorator
def log_fun(fun: Callable[[Any], Any], *args: Iterable[Any], **kwargs: Any) -> Any:
    """Decorate a function to log the function name and completed time.

    Args:
        fun: the decorated function
        args: functional arguments
        kwargs: function keyword arguments

    Returns:
        Any: result of the function

    """
    fun_name = fun.__name__
    with log_action(f'Running {fun_name}{signature(fun)}', args=args, kwargs=kwargs):
        return fun(*args, **kwargs)  # type: ignore[call-arg]


_LOG_SUB_DIR = '.logs'
"""Subdirectory to store log files relative to the project directory."""


@beartype
def _format_jsonl_handler(log_dir: Path, production: bool = True) -> Dict[str, Any]:
    """Return the JSONL Handler dictionary for loguru.

    Args:
        log_dir: Path to the log directory
        production: if True, will tweak logging configuration for production code. Default is True

    Returns:
        Dict[str, Any]: the logger configuration as a dictionary

    """
    log_level = logging.INFO if production else logging.DEBUG

    jsonl_handler = {
        'sink': log_dir / 'debug-{time}.jsonl', 'mode': 'w', 'level': log_level,
        'rotation': '1h', 'backtrace': True, 'diagnose': not production,
    }
    if production:
        jsonl_handler['format'] = serializable_compact
    else:
        jsonl_handler['serialize'] = True

    return {
        'handlers': [
            {
                'sink': sys.stdout, 'level': logging.WARNING if production else logging.INFO,
                'backtrace': True, 'diagnose': not production,
            },
            jsonl_handler,
            {
                'sink': log_dir / 'debug-{time}.log', 'mode': 'w', 'level': log_level,
                'rotation': '1h', 'backtrace': True, 'diagnose': not production,
            },
        ],
    }


@beartype
def build_logger_config(
    path_parent: Optional[Path] = None,
    *, format_handler: Callable[[Path, bool], Dict[str, Any]] = _format_jsonl_handler,
    production: bool = True,
) -> Dict[str, Any]:
    """Build the loguru configuration. Use with `loguru.configure(**configuration)`.

    > See example use in `activate_debug_logging`

    Args:
        path_parent: Path to the directory where the '.logs/' folder should be created. Default is this package
        format_handler: function that will generate the loguru handler dictionary. Default is `_format_jsonl_handler`
        production: if True, will tweak logging configuration for production code. Default is `True`

    Returns:
        Dict[str, Any]: the logger configuration as a dictionary

    """
    if path_parent is None:
        path_parent = Path(__file__).resolve().parent

    log_dir = path_parent / _LOG_SUB_DIR
    log_dir.mkdir(exist_ok=True, parents=True)
    logger.info(f'Started logging to {log_dir} (production={production})')

    return format_handler(log_dir=log_dir, production=production)


@beartype
def activate_debug_logging(
    *, pkg_names: List[str], path_project: Optional[Path] = None,
    clear_log: bool = False,
) -> None:
    """Wrap `build_logger_config` to configure verbose logging for debug use.

    Args:
        pkg_names: list of string package names to activate. If empty, likely no log output.
        path_project: path to the project directory. Defaults to `CWD` if not specified
        clear_log: if True, delete all log files that haven't been updated for at least an hour. Default is False

    """
    if not path_project:
        path_project = Path.cwd()

    # See an example of toggling loguru at: https://github.com/KyleKing/calcipy/tree/examples/loguru-toggle
    for pkg_name in pkg_names:
        logger.enable(pkg_name)

    if clear_log:
        hour = 3600
        delete_old_files(path_project / _LOG_SUB_DIR, ttl_seconds=hour)

    log_config = build_logger_config(path_project, production=False)
    logger.configure(**log_config)
    logger.debug(
        'Started logging to {path_project}/.logs with {log_config}', path_project=path_project,
        log_config=log_config,
    )
