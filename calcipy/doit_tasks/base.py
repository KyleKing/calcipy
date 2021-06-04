"""General doit Utilities."""

import webbrowser
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from beartype import beartype
from doit.task import Task
from loguru import logger

from .doit_globals import DoitAction, DoitTask


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
    task: DoitTask = defaultdict(list)
    task['actions'] = actions
    task['title'] = _show_cmd
    task['verbosity'] = verbosity
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
def write_text(path_file: Path, text: str) -> None:
    """path_file.write_text wrapper for doit.

    Args:
        path_file: Path to the file
        text: string to write to file

    """
    path_file.write_text(text)  # pragma: no cover


@beartype
def open_in_browser(path_file: Path) -> None:
    """Open the path in the default web browser.

    Args:
        path_file: Path to file

    """
    webbrowser.open(Path(path_file).as_uri())  # pragma: no cover
