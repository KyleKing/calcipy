"""PyTest configuration."""

import os
from pathlib import Path
from typing import Generator

import pytest
from decorator import contextmanager

from calcipy.conftest import pytest_configure  # noqa: F401
from calcipy.conftest import pytest_html_results_table_header  # noqa: F401
from calcipy.conftest import pytest_html_results_table_row  # noqa: F401
from calcipy.conftest import pytest_runtest_makereport  # noqa: F401
from calcipy.doit_tasks.doit_globals import DoitGlobals

from .configuration import TEST_TMP_CACHE, clear_test_cache


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
