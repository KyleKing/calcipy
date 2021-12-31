"""General doit Utilities."""

import shutil
import webbrowser
from collections import defaultdict
from pathlib import Path
from typing import Iterable, List

from beartype import beartype
from doit.task import Task
from loguru import logger
from sty import fg

from ..file_helpers import if_found_unlink
from .doit_globals import DG, DoitAction, DoitTask


@beartype
def _show_cmd(task: Task) -> str:
    """For debugging, log the full command to the console.

    Args:
        task: doit Task

    Returns:
        str: describing the sequence of actions

    """
    def clean_action(action: str) -> str:
        action = action.replace(f'{DG.meta.path_project.as_posix()}/', '')
        if 'password' in action:
            action = action.split('password')[0] + '...password-redacted...'
        return action  # noqa: R504

    indent = '\n\t'
    actions = indent.join(map(clean_action, map(str, task.actions)))
    return f'{task.name} > [{indent}{fg.grey}{actions}{fg.rs}\n]\n'


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
    path_file.parent.mkdir(exist_ok=True, parents=True)
    path_file.write_text(text)  # pragma: no cover


@beartype
def open_in_browser(path_file: Path) -> None:
    """Open the path in the default web browser.

    Args:
        path_file: Path to file

    """
    webbrowser.open(Path(path_file).as_uri())  # pragma: no cover


@beartype
def _make_archive(path_dir: Path, archive_format: str = 'zip') -> None:
    """Make archive.

    Args:
        path_dir: directory to zip
        archive_format: default is `zip`. See `shutil.make_archive` for supported types

    """
    shutil.make_archive(path_dir, archive_format, path_dir)


@beartype
def _zip_release() -> List[DoitAction]:
    """Zip up important information in the releases directory.

    > WARN: zip paths must be in the AppVeyor.yml to be collected

    Returns:
        DoitTask: doit task

    """
    actions = []
    for path_dir in [DG.test.path_out, DG.doc.path_out]:
        if path_dir.is_dir():
            path_zip = path_dir.with_suffix('.zip')
            actions.extend([
                (if_found_unlink, (path_zip,)),
                (_make_archive, (path_dir,)),
                (echo, (f'Created: {path_zip}',)),
            ])
    return actions


@beartype
def task_zip_release() -> DoitTask:
    """Zip up important information in the releases directory.

    Returns:
        DoitTask: doit task

    """
    return debug_task(_zip_release())
