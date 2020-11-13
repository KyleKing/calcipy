"""Loguru Helpers."""

# PLANNED: Files like this should be in the production dependencies, but dash-dev is designed to be a dev-only

import json
from typing import Any, Dict

from decorator import contextmanager
from loguru import logger


def serializable_compact(record: Dict[str, Any]) -> str:
    """Loguru formatter to return a compact dumpped JSON string for jsonlines output.

    Loguru Record Documentation: https://loguru.readthedocs.io/en/stable/api/logger.html#record

    Based on the `_serialize_record` method:
    https://github.com/Delgan/loguru/blob/44f6771/loguru/_handler.py#L222

    ```py
    from dash_dev.log_helpers import serializable_compact

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
            'elapsed': {
                'seconds': record['elapsed'].total_seconds(),
            },
            'exception': exception,
            'extra': record['extra'],
            'file': {'name': record['file'].name, 'path': record['file'].path},
            'function': record['function'].strip('<>'),
            'level': {
                'name': record['level'].name,
            },
            'line': record['line'],
            'message': record['message'],
            'module': record['module'],
            'name': record['name'],
            'time': {'repr': record['time'], 'timestamp': record['time'].timestamp()},
        },
    }
    return json.dumps(simplified, default=str).replace('{', '{{').replace('}', '}}') + '\n'


@contextmanager
def logger_context(message: str, level: str = 'INFO', _logger: Any = logger) -> None:

    # TODO: Bind some sort of indicator to make these two related events easier to find?
    _logger.log(level, f'Started: {message}', context=True)
    yield
    _logger.log(level, f'Completed: {message}', context=False)