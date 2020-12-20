"""Loguru Helpers."""

import logging
import sys
import time
from inspect import signature
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from decorator import contextmanager, decorator
from loguru import logger
from loguru._logger import Logger

try:
    from preconvert.output import simplejson as json
except ImportError:
    import json


def serializable_compact(record: Dict[str, Any]) -> str:
    """Loguru formatter to return a compact JSON string for JSONLines output.

    `record` documentation: https://loguru.readthedocs.io/en/stable/api/logger.html#record

    Based on the `_serialize_record` method:
    https://github.com/Delgan/loguru/blob/44f6771/loguru/_handler.py#L222

    ```py
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
    return json.dumps(simplified, default=str).replace('{', '{{').replace('}', '}}') + '\n'


def _log_action(message: str, level: str = 'INFO', _logger: Logger = logger, **kwargs: Any) -> None:
    """Log the beggining and end of an action.

    Args:
        message: string message to describe the context
        level: log level. Default is `INFO`
        _logger: Optional logger instance
        **kwargs: function keyword arguments passed to the start log statement

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
def log_fun(fun: Callable, *args: Any, **kwargs: Any) -> Any:
    """Decorate a function to log the function name and completed time.

    Args:
        fun: the decorated function
        *args: functional arguments
        **kwargs: function keyword arguments

    Returns:
        Any: result of the function

    """
    fun_name = fun.__name__
    with log_action(f'Running {fun_name}{signature(fun)}', args=args, kwargs=kwargs):
        return fun(*args, **kwargs)


def build_logger_config(path_parent: Optional[Path] = None, *, production: bool = True) -> Dict[str, Any]:
    """Build the loguru configuration. Use with `loguru.configure(**configuration)`.

    ```py
    # Typical example enabling loguru for a package

    from pathlib import Path

    from loguru import logger

    from calcipy import __pkg_name__
    from calcipy.log_helpers import build_logger_config

    logger.enable(__pkg_name__)  # This will enable output from calcipy, which is off by default
    # See an example of toggling loguru at: https://github.com/KyleKing/calcipy/tree/examples/loguru-toggle

    path_parent = Path(__file__).resolve().parent
    log_config = build_logger_config(path_parent, production=False)
    logger.configure(**log_config)
    logger.info('Started logging to {path_parent}/.logs with {log_config}', path_parent=path_parent,
                log_config=log_config)
    ```

    Args:
        path_parent: Path to the directory where the '.logs/' folder should be created. Default is this package
        production: if True, will tweak logging configuration for production code. Default is True

    Returns:
        Dict[str, Any]: the logger configuration as a dictionary

    """
    if path_parent is None:
        path_parent = Path(__file__).resolve().parent

    log_dir = path_parent / '.logs'
    log_dir.mkdir(exist_ok=True, parents=True)
    logger.info(f'Started logging to {log_dir} (production={production})')
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
