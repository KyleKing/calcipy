"""Global variables for testing."""

from pathlib import Path

from calcipy import __pkg_name__
from calcipy.log_helpers import activate_debug_logging

activate_debug_logging(pkg_names=[__pkg_name__])

TEST_DIR: Path = Path(__file__).resolve().parent
"""Path to the `test` directory that contains this file and all other tests."""

TEST_DATA_DIR: Path = TEST_DIR / 'data'
"""Path to subdirectory with test data within the Test Directory."""

PATH_TEST_PROJECT: Path = TEST_DIR.parent / '.test_calcipy_project'
"""Local directory used for testing the doit globals.

Note: outside of `tests/` to prevent pytest from finding test files.

"""
