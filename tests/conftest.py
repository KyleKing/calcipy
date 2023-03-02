"""PyTest configuration."""

from pathlib import Path

import pytest
from beartype import beartype
from beartype.typing import Dict
from invoke import MockContext

from .configuration import TEST_TMP_CACHE, clear_test_cache


@pytest.fixture(scope='module')
def vcr_config() -> Dict:
    """Global configuration (https://github.com/kiwicom/pytest-recording) for `pytest-recording` (vcr).

    Returns:
        Dict: `pytest-recording` options

    """
    return {
        'filter_headers': ['authorization'],
        'ignore_localhost': True,
        'record_mode': 'once',
    }


@pytest.fixture()
@beartype
def fix_test_cache() -> Path:
    """Fixture to clear and return the test cache directory for use.

    Returns:
        Path: Path to the test cache directory

    """
    clear_test_cache()
    return TEST_TMP_CACHE


@pytest.fixture()
def ctx() -> MockContext:
    """Mock Invoke Context.

    Adapted from:

    https://github.com/pyinvoke/invocations/blob/8a277c304dd7aaad03888ee42d811c468e7fb37d/tests/conftest.py#L5-L11

    Documentation: https://docs.pyinvoke.org/en/stable/concepts/testing.html

    """
    MockContext.run_command = property(lambda self: self.run.call_args[0][0])
    return MockContext(run=True)
