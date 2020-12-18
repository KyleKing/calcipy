"""Test that the logger can be toggled by package."""

import sys
from pathlib import Path
from typing import Iterable, List

import jsonlines
import pack_1
import pack_2
import pack_3
import pytest
from loguru import logger

PATH_LOG = Path(__file__).resolve().parent / 'loguru.jsonl'

logger.configure(**{
    'handlers': [
        {'sink': sys.stdout},
        {'sink': PATH_LOG, 'mode': 'a', 'serialize': True},
    ],
})


def _configure_for_testing(label: str) -> Path:
    """Configure a unique filename for the test."""
    path_log = PATH_LOG.parent / f'{PATH_LOG.stem}-{label}{PATH_LOG.suffix}'
    logger.configure(**{
        'handlers': [
            {'sink': path_log, 'mode': 'w', 'serialize': True},
        ],
    })
    return path_log


def _verify_log_file(path_log: Path, expected_messages: List[str]) -> None:
    """Compare the contents of the log file against the expected messages."""
    print(path_log.read_text())
    with jsonlines.open(path_log) as reader:
        objects = [*reader]

    for idx, obj in enumerate(objects):
        assert obj['record']['message'] == expected_messages[idx]
        # PLANNED: Also check other parameters - expected_messages may need to be a list of dictionaries
        # path_source = Path(obj['record']['file']['path'])
        # assert path_source.name == '__init__.py'
        # assert path_source.parent.name == f'pack_{idx}'
        # assert obj['record']['level']['name'] == 'DEBUG' <or> 'INFO'
    assert len(expected_messages) == len(objects)


def _toggle_loggers(*, enable: bool, pkg_numbers: Iterable[int] = (1, 2, 3)) -> None:
    """Ensure that all package loggers are disabled."""
    for pkg_name in [f'pack_{idx}' for idx in pkg_numbers]:
        if enable:
            logger.enable(pkg_name)
        else:
            logger.disable(pkg_name)


def _make_expected_messages(label: str, pkg_numbers: Iterable[int]) -> None:
    """Populate the text log messages expected from `_make_logs(label)`."""
    expected_messages = ['Beep - Testing Start']
    for pkg_num in pkg_numbers:
        expected_messages.extend([f'I am package pack_{pkg_num}', label])
    expected_messages.append('Beep - Testing Complete')
    return expected_messages


def _make_logs(label: str) -> None:
    """Create some sample log output."""
    logger.info('Beep - Testing Start')
    pack_1.main(label)
    pack_2.main(label)
    pack_3.main(label)
    logger.info('Beep - Testing Complete')


@pytest.mark.parametrize('pkg_numbers', [
    [],
    [1],
    [1, 2],
    [1, 2, 3],
    [2, 3],
])
def test_toggle(pkg_numbers):
    """Test loguru.enable/disable."""
    label = ''.join(map(str, pkg_numbers))
    path_log = _configure_for_testing(label)
    expected_messages = _make_expected_messages(label, pkg_numbers)
    # Reset the log file and toggles
    _toggle_loggers(enable=False)
    _toggle_loggers(enable=True, pkg_numbers=pkg_numbers)

    _make_logs(label)  # act

    _verify_log_file(path_log, expected_messages)


if __name__ == '__main__':
    # Manual test of the logger toggles
    _toggle_loggers(enable=True, pkg_numbers=[2])
    _make_logs('label')

    # Example record from the log file
    """
    {
        'text': '2020-12-18 08:38:42.518 | DEBUG    | pack_2:main:11 - label\n',
        'record': {
            'elapsed': {'repr': '0:00:00.125625', 'seconds': 0.125625},
            'exception': None, 'extra': {},
            'file': {'name': '__init__.py', 'path': '/Users/kyleking/Developer/Werk/__LocalProjects/calcipy-orphan/calcipy/pack_2/pack_2/__init__.py'},
            'function': 'main', 'level': {'icon': '', 'name': 'DEBUG', 'no': 10}, 'line': 11,
            'message': 'label', 'module': '__init__', 'name': 'pack_2',
            'process': {'id': 73739, 'name': 'MainProcess'},
            'thread': {'id': 4731157952, 'name': 'MainThread'},
            'time': {'repr': '2020-12-18 08:38:42.518970-05:00', 'timestamp': 1608298722.51897},
        },
    }
    """
