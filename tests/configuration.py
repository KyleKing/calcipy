"""Global variables for testing."""

from pathlib import Path
from typing import Generator

from decorator import contextmanager

from calcipy import __pkg_name__
from calcipy.doit_tasks.doit_globals import DG
from calcipy.file_helpers import delete_dir, ensure_dir
from calcipy.log_helpers import activate_debug_logging

activate_debug_logging(pkg_names=[__pkg_name__], clear_log=True)

TEST_DIR = Path(__file__).resolve().parent
"""Path to the `test` directory that contains this file and all other tests."""

TEST_DATA_DIR = TEST_DIR / 'data'
"""Path to subdirectory with test data within the Test Directory."""

TEST_TMP_CACHE = TEST_DIR / '_tmp_cache'
"""Path to the temporary cache folder in the Test directory."""

# PLANNED: Replace magic numbers in tests with meta-data about the test project
#   _COUNT_PY_FILES = 8
#   _COUNT_MD_FILES = ?
#   etc...
PATH_TEST_PROJECT = TEST_DIR.parent / '.test_calcipy_project'
"""Local directory used for testing the doit globals.

Note: outside of `tests/` to prevent pytest from finding test files.

"""


def clear_test_cache() -> None:
    """Remove the test cache directory if present."""
    delete_dir(TEST_TMP_CACHE)
    ensure_dir(TEST_TMP_CACHE)


# Ensure that the temporary cache directory exists
clear_test_cache()

# Set the DoitGlobals instance to use the Test Project for all tests
DG.set_paths(path_project=PATH_TEST_PROJECT)


@contextmanager
def _temp_dg(path_project: Path = PATH_TEST_PROJECT) -> Generator[None, None, None]:
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
