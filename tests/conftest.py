"""PyTest configuration."""

from pathlib import Path

import pytest
from beartype.typing import Dict, Union
from invoke.context import MockContext

from .configuration import TEST_TMP_CACHE, clear_test_cache


@pytest.fixture(scope='module')
def vcr_config() -> Dict[str, Union[str, bool, list[str]]]:
    """Global configuration (https://github.com/kiwicom/pytest-recording) for `pytest-recording` (vcr).

    Returns:
    -------
        Dict: `pytest-recording` options

    """
    return {
        # VCR-py configuration
        #   Docs: https://vcrpy.readthedocs.io/en/latest/advanced.html
        'filter_headers': ['authorization'],
        'ignore_localhost': False,
        # Pytest-Recording CLI Options
        'allowed_hosts': '',
        'block_network': True,
        'record_mode': 'once',
    }


@pytest.fixture()
def fix_test_cache() -> Path:
    """Fixture to clear and return the test cache directory for use.

    Returns:
    -------
        Path: Path to the test cache directory

    """
    clear_test_cache()
    return TEST_TMP_CACHE


@pytest.fixture()
def ctx() -> MockContext:
    """Mock Invoke Context.

    Adapted from:

    https://github.com/pyinvoke/invocations/blob/4e3578e9c49dbbff2ec00ef3c8d37810fba511fa/tests/conftest.py#L13-L19

    Documentation: https://docs.pyinvoke.org/en/stable/concepts/testing.html

    """
    MockContext.run_command = property(lambda self: self.run.call_args[0][0])  # type: ignore[attr-defined]
    return MockContext(run=True)
