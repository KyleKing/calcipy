"""PyTest configuration."""

from pathlib import Path
from typing import Generator

import pytest
from decorator import contextmanager

from calcipy.conftest import pytest_configure  # noqa: F401
from calcipy.conftest import pytest_html_results_table_header  # noqa: F401
from calcipy.conftest import pytest_html_results_table_row  # noqa: F401
from calcipy.conftest import pytest_runtest_makereport  # noqa: F401
from calcipy.doit_tasks.doit_globals import DG

from .configuration import PATH_TEST_PROJECT


@contextmanager
def temp_dg(path_project: Path = PATH_TEST_PROJECT) -> Generator[None, None, None]:
    """Temporarily change the DG project directory.

    Args:
        path_project: path to the project directory to pass to `DG`

    Yields:
        None: continues execution with DG set to the specified `path_project`

    """
    path_original = DG.meta.path_project
    if path_original != path_project:
        DG.set_paths(path_project=path_project)
        yield
        DG.set_paths(path_project=path_original)


@pytest.fixture()
def _fix_dg() -> Generator[None, None, None]:
    """Fixture for DG.

    Yields:
        None: continues execution with DG set to the specified `path_project`

    """
    with temp_dg():
        yield
