"""Test conftest."""

from calcipy.dev.conftest import (  # noqa: F401
    pytest_configure, pytest_html_results_table_header, pytest_html_results_table_row, pytest_runtest_makereport,
)

# WARN: the conftest is only tested for imports - essentially tested in tests/conftest.py
