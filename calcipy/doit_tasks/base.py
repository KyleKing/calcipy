"""General doit Utilities and Requirements."""

import shutil
import webbrowser
from pathlib import Path
from typing import Any, List, Sequence

from loguru import logger

from ..log_helpers import log_action
from .doit_globals import DIG, DoItTask

# TODO: Show dodo.py in the documentation
# TODO: Show README.md in the documentation (may need to update paths?)
# TODO: Replace src_examples_dir and make more generic to specify code to include in documentation
# TODO: Show table of contents in __init__.py file. Use ast:
#   https://www.ecosia.org/search?q=ast+find+all+functions+and+classes+in+python+package

# ----------------------------------------------------------------------------------------------------------------------
# Really General...


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
# Manage Directories


def delete_dir(dir_path: Path) -> None:
    """Delete the specified directory from a doit task.

    Args:
        dir_path: Path to directory to delete

    """
    if dir_path.is_dir():
        logger.info(f'Deleting `{dir_path}`', dir_path=dir_path)
        shutil.rmtree(dir_path)


def ensure_dir(dir_path: Path) -> None:
    """Make sure that the specified dir_path exists and create any missing folders from a doit task.

    Args:
        dir_path: Path to directory that needs to exists

    """
    with log_action(f'Create `{dir_path}`'):
        dir_path.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------------------------------------------------------
# General doit Utilities


def _show_cmd(task: DoItTask) -> str:
    """For debugging, log the full command to the console.

    Args:
        task: doit task

    Returns:
        str: describing the sequence of actions

    """
    actions = ''.join([f'\n\t{act}' for act in task.actions])
    return f'{task.name} > [{actions}\n]\n'


def debug_task(actions: Sequence[Any], verbosity: int = 2) -> DoItTask:
    """Activate verbose logging for the specified actions.

    Args:
        actions: list of doit actions
        verbosity: 2 is maximum, while 0 is deactivated. Default is 2

    Returns:
        DoItTask: doit task

    """
    task = {
        'actions': actions,
        'title': _show_cmd,
        'verbosity': verbosity,
    }
    logger.debug('Created task. See extras', task=f'{task}')
    return task


def debug_action(actions: Sequence[Any], verbosity: int = 2) -> DoItTask:  # noqa
    import warnings
    warnings.warn('debug_action is deprecated. Replace with `debug_task`')
    return debug_task(actions, verbosity)


def echo(msg: str) -> None:
    """Wrap the system print command.

    Args:
        msg: string to write to STDOUT

    """
    print(msg)  # noqa: T001


def write_text(file_path: Path, text: str) -> None:
    """file_path.write_text wrapper for doit.

    Args:
        file_path: Path to the file
        text: string to write to file

    """
    file_path.write_text(text)


def open_in_browser(file_path: Path) -> None:
    """Open the path in the default web browser.

    Args:
        file_path: Path to file

    """
    webbrowser.open(Path(file_path).as_uri())


def if_found_unlink(file_path: Path) -> None:
    """Remove file if it exists. Function is intended to a doit action.

    Args:
        file_path: Path to file to remove

    """
    if file_path.is_file():
        logger.info(f'Deleting `{file_path}`', file_path=file_path)
        file_path.unlink()


# ----------------------------------------------------------------------------------------------------------------------
# Manage Requirements


def task_export_req() -> DoItTask:
    """Create a `requirements.txt` file for non-Poetry users and for Github security tools.

    Returns:
        DoItTask: doit task

    """
    req_path = DIG.meta.path_toml.parent / 'requirements.txt'
    return debug_task([f'poetry export -f {req_path.name} -o "{req_path}" --without-hashes --dev'])
