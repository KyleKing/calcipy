"""General doit Utilities."""

import os
import shutil
import webbrowser
from collections import defaultdict
from pathlib import Path
from typing import Dict, Generator, Iterable, List

from beartype import beartype
from decorator import contextmanager
from doit.task import Task
from loguru import logger
from pre_commit.git import zsplit
from pre_commit.util import cmd_output

from ..log_helpers import log_action
from .doit_globals import DoitAction, DoitTask

# ----------------------------------------------------------------------------------------------------------------------
# File Manipulation


@beartype
def read_lines(file_path: Path) -> List[str]:
    """Read a file and split on newlines for later parsing.

    Args:
        file_path: path to the file

    Returns:
        List[str]: lines of text as list

    """
    if file_path.is_file():
        return file_path.read_text().split('\n')
    return []


# ----------------------------------------------------------------------------------------------------------------------
# Find Files


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
    return zsplit(cmd_output('git', 'ls-files', '-z', cwd=cwd)[1])


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


# ----------------------------------------------------------------------------------------------------------------------
# Manage Directories


@beartype
def delete_dir(dir_path: Path) -> None:
    """Delete the specified directory from a doit task.

    Args:
        dir_path: Path to directory to delete

    """
    if dir_path.is_dir():
        logger.info(f'Deleting `{dir_path}`', dir_path=dir_path)
        shutil.rmtree(dir_path)


@beartype
def ensure_dir(dir_path: Path) -> None:
    """Make sure that the specified dir_path exists and create any missing folders from a doit task.

    Args:
        dir_path: Path to directory that needs to exists

    """
    with log_action(f'Create `{dir_path}`'):
        dir_path.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------------------------------------------------------
# General doit Utilities


@beartype
def _show_cmd(task: Task) -> str:
    """For debugging, log the full command to the console.

    Args:
        task: doit Task

    Returns:
        str: describing the sequence of actions

    """
    actions = ''.join(f'\n\t{act}' for act in task.actions)
    return f'{task.name} > [{actions}\n]\n'


@beartype
def debug_task(actions: Iterable[DoitAction], verbosity: int = 2) -> DoitTask:
    """Activate verbose logging for the specified actions.

    Args:
        actions: list of doit actions
        verbosity: 2 is maximum, while 0 is deactivated. Default is 2

    Returns:
        DoitTask: doit task

    """
    task = {
        'actions': actions,
        'title': _show_cmd,
        'verbosity': verbosity,
    }
    logger.debug('Created task. See extras', task=f'{task}')
    return task


@beartype
def echo(msg: str) -> None:
    """Wrap the system print command.

    Args:
        msg: string to write to STDOUT

    """
    print(msg)  # noqa: T001  # pragma: no cover


@beartype
def write_text(file_path: Path, text: str) -> None:
    """file_path.write_text wrapper for doit.

    Args:
        file_path: Path to the file
        text: string to write to file

    """
    file_path.write_text(text)  # pragma: no cover


@beartype
def open_in_browser(file_path: Path) -> None:
    """Open the path in the default web browser.

    Args:
        file_path: Path to file

    """
    webbrowser.open(Path(file_path).as_uri())  # pragma: no cover


@beartype
def if_found_unlink(file_path: Path) -> None:
    """Remove file if it exists. Function is intended to a doit action.

    Args:
        file_path: Path to file to remove

    """
    if file_path.is_file():
        logger.info(f'Deleting `{file_path}`', file_path=file_path)
        file_path.unlink()
