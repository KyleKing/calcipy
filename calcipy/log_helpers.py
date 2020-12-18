"""Loguru Helpers."""

import json
import time
from inspect import signature
from typing import Any, Callable, Dict, Type

from decorator import contextmanager, decorator
from loguru import logger


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
        str: dumped JSON

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


@contextmanager
def log_action(message: str, level: str = 'INFO', _logger: Type(logger) = logger, **kwargs: Any) -> None:
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
