"""PyTest configuration."""

from typing import Generator

import pytest

from calcipy.conftest import pytest_configure  # noqa: F401
from calcipy.conftest import pytest_html_results_table_header  # noqa: F401
from calcipy.conftest import pytest_html_results_table_row  # noqa: F401
from calcipy.conftest import pytest_runtest_makereport  # noqa: F401

from .configuration import _temp_dg


@pytest.fixture()
def _fix_dg() -> Generator[None, None, None]:
    """Fixture for DG.

    Use with: `@pytest.mark.usefixtures('_fix_dg')`

    Yields:
        None: continues execution with DG set to the specified `path_project`

    """
    with _temp_dg():
        yield
