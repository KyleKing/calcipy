"""Test that the logger can be toggled by package."""

import sys
from pathlib import Path

import pack_1
import pack_2
import pack_3
from loguru import logger

path_log = Path(__file__).resolve().parent / 'loguru.jsonl'

logger.configure(**{
    'handlers': [
        {'sink': sys.stdout},
        {'sink': path_log, 'mode': 'w', 'serialize': True},
    ],
})


def test_toggle(label):
    logger.info('Beep - Testing Start')

    pack_1.main(label)
    pack_2.main(label)
    pack_3.main(label)

    logger.info('Beep - Testing Complete')


if __name__ == '__main__':
    logger.enable(pack_1.__pkg_name__)
    logger.enable(pack_2.__pkg_name__)
    logger.enable(pack_3.__pkg_name__)
    test_toggle('label')
