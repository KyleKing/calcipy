"""General doit Utilities and Requirements."""

from __future__ import annotations

import shutil
import webbrowser
from collections.abc import Iterable
from pathlib import Path

from beartype import beartype
from doit.task import Task
from loguru import logger

from ..log_helpers import log_action
from .doit_globals import DoitAction, DoitTask

# ----------------------------------------------------------------------------------------------------------------------
# Really General...


@beartype
def read_lines(file_path: Path) -> list[str]:
    """Read a file and split on newlines for later parsing.

    Args:
        file_path: path to the file

    Returns:
        list[str]: lines of text as list

    """
    if file_path.is_file():
        return file_path.read_text().split('\n')
    return []


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
