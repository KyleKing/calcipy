"""PyTest configuration."""

import os
from pathlib import Path
from typing import Dict, Generator

import pytest
from decorator import contextmanager

from calcipy.dev.conftest import pytest_configure  # noqa: F401
from calcipy.dev.conftest import pytest_html_results_table_header  # noqa: F401
from calcipy.dev.conftest import pytest_html_results_table_row  # noqa: F401
from calcipy.dev.conftest import pytest_runtest_makereport  # noqa: F401
from calcipy.doit_tasks.doit_globals import DoitGlobals

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


@contextmanager
def __temp_chdir(path_tmp: Path) -> Generator[None, None, None]:
    """Temporarily change the working directory.

    > Not currently used because setting `cwd` for a modified version of `_get_all_files` is more robust

    ```py
    with _temp_chdir(DG.meta.path_project):
        print(f'Current in: {Path.cwd()}')
    ```

    Args:
        path_tmp: path to use as the working directory

    Yields:
        None: continues execution with the specified `path_tmp` working directory

    """
    path_cwd = Path.cwd()
    try:
        os.chdir(path_tmp)
        yield
    finally:
        os.chdir(path_cwd)


@pytest.fixture()
def fix_test_cache() -> Path:
    """Fixture to clear and return the test cache directory for use.

    Returns:
        Path: Path to the test cache directory

    """
    clear_test_cache()
    return TEST_TMP_CACHE


@pytest.fixture()
def fix_dg() -> DoitGlobals:
    """Fixture to create a new DoitGlobals instance for `TEST_TMP_CACHE`.

    > Note use non-yielding fixtures with: `@pytest.mark.usefixtures('_fix_dg')`

    Returns:
        DoitGlobals: continues execution with DG set to the specified `path_project`

    """
    clear_test_cache()
    dg = DoitGlobals()
    dg.set_paths(TEST_TMP_CACHE)
    return dg
