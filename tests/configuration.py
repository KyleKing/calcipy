"""Global variables for testing."""

from pathlib import Path
from typing import Generator

from decorator import contextmanager

from calcipy import __pkg_name__
from calcipy.doit_tasks.doit_globals import DG
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
