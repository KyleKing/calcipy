"""Pytest configuration."""

from pathlib import Path

import pytest
from invoke.context import MockContext

from .configuration import TEST_TMP_CACHE, clear_test_cache


@pytest.fixture
def fix_test_cache() -> Path:
    """Fixture to clear and return the test cache directory for use.

    Returns:
        Path: Path to the test cache directory

    """
    clear_test_cache()
    return TEST_TMP_CACHE


@pytest.fixture
def ctx() -> MockContext:
    """Return Mock Invoke Context.

    Adapted from:
    https://github.com/pyinvoke/invocations/blob/4e3578e9c49dbbff2ec00ef3c8d37810fba511fa/tests/conftest.py#L13-L19

    Documentation: https://docs.pyinvoke.org/en/stable/concepts/testing.html

    """
    MockContext.run_command = property(lambda self: self.run.call_args[0][0])  # type: ignore[attr-defined]
    return MockContext(run=True)
