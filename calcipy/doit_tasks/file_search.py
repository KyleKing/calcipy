"""Find Files."""

import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Generator, List

from beartype import beartype
from decorator import contextmanager
from loguru import logger
from pre_commit.git import zsplit
from pre_commit.util import cmd_output


@beartype
@contextmanager
def _temp_chdir(path_tmp: Path) -> Generator[None, None, None]:
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


@beartype
def _get_all_files(*, cwd: Path) -> List[str]:
    """Get all files using git. Modified `pre_commit.git.get_all_files` to accept `cwd`.

    https://github.com/pre-commit/pre-commit/blob/488b1999f36cac62b6b0d9bc8eae99418ae5c226/pre_commit/git.py#L153

    Args:
        cwd: current working directory to pass to `subprocess.Popen`

    Returns:
        List[str]: list of all file paths relative to the `cwd`

    """
    return zsplit(cmd_output('git', 'ls-files', '-z', cwd=cwd)[1])  # type: ignore[no-any-return]


@beartype
def find_project_files(path_project: Path) -> List[Path]:
    """Find project files in git version control.

    > Note: uses the relative project directory and verifies that each file exists

    Args:
        path_project: Path to the project directory. Typically `DG.meta.path_project`

    Returns:
        Dict[str, List[Path]]: where keys are the suffix (without leading dot) and values the list of paths

    """
    file_paths = []
    for rel_file in _get_all_files(cwd=path_project):
        path_file = path_project / rel_file
        if path_file.is_file():
            file_paths.append(path_file)
        else:  # pragma: no cover
            logger.warning(f'Could not find {rel_file} in {path_project}')
    return file_paths


@beartype
def find_project_files_by_suffix(path_project: Path) -> Dict[str, List[Path]]:
    """Find project files in git version control.

    > Note: uses the relative project directory and verifies that each file exists

    Args:
        path_project: Path to the project directory. Typically `DG.meta.path_project`

    Returns:
        Dict[str, List[Path]]: where keys are the suffix (without leading dot) and values the list of paths

    """
    file_lookup = defaultdict(list)
    for path_file in find_project_files(path_project):
        file_lookup[path_file.suffix.lstrip('.')].append(path_file)
    return file_lookup
