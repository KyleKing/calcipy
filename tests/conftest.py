"""Pytest configuration."""

from pathlib import Path

import pytest
from beartype.typing import Iterator
from corallium import file_helpers
from invoke.context import MockContext

from calcipy import invoke_helpers

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
    return MockContext(run=True)


def _clear_cwd_caches() -> None:
    invoke_helpers.get_project_path.cache_clear()
    file_helpers.get_lock.cache_clear()
    file_helpers.read_pyproject.cache_clear()
    file_helpers.read_package_name.cache_clear()


@pytest.fixture
def tmp_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    """Run the test from a minimal project named `mypkg`, with the cwd-keyed caches cleared.

    Yields:
        Path: the project directory, which is also the working directory

    """
    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "mypkg"\n', encoding='utf-8')
    monkeypatch.chdir(tmp_path)
    _clear_cwd_caches()
    yield tmp_path
    _clear_cwd_caches()
