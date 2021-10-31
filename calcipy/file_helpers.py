"""File Helpers."""

import os
import shutil
import string
import time
from pathlib import Path
from typing import Any, List, Optional

import yaml
from beartype import beartype
from loguru import logger

# ----------------------------------------------------------------------------------------------------------------------
# General

ALLOWED_CHARS = string.ascii_lowercase + string.ascii_uppercase + string.digits + '-_.'
"""Default string of acceptable characters in a filename."""


@beartype
def sanitize_filename(filename: str, repl_char: str = '_', allowed_chars: str = ALLOWED_CHARS) -> str:
    """Replace all characters not in the `allow_chars` with `repl_char`.

    Args:
        filename: string filename (stem and suffix only)
        repl_char: replacement character. Default is `_`
        allowed_chars: all allowed characters. Default is `ALLOWED_CHARS`

    Returns:
        str: sanitized filename

    """
    return ''.join((char if char in allowed_chars else repl_char) for char in filename)


_COPIER_ANSWERS_NAME = '.copier-answers.yml'
"""Copier Answer file name."""

_MKDOCS_CONFIG_NAME = 'mkdocs.yml'
"""Copier Answer file name."""


@beartype
def _read_yaml_file(path_yaml: Path) -> Any:
    """Attempt to read the specified yaml file. Returns an empty dictionary if not found or a parser error occurs.

    > Note: suppresses all tags in the YAML file

    Args:
        path_yaml: path to the yaml file

    Returns:
        dictionary representation of the source file

    """
    # TODO: modify so that mkdocs.yml can be read, but Python won't be executed...

    # Based on: https://github.com/yaml/pyyaml/issues/86#issuecomment-380252434
    yaml.add_multi_constructor('', lambda _loader, _suffix, _node: None)
    yaml.add_multi_constructor('!', lambda _loader, _suffix, _node: None)
    yaml.add_multi_constructor('!!', lambda _loader, _suffix, _node: None)
    try:
        return yaml.unsafe_load(path_yaml.read_text())
    except (FileNotFoundError, KeyError) as err:  # pragma: no cover
        logger.warning(f'Unexpected error reading the {path_yaml.name} file ({path_yaml}): {err}')
        return {}
    except yaml.constructor.ConstructorError:
        logger.exception('Warning: burying poorly handled yaml error')
        return {}


@beartype
def get_doc_dir(path_project: Path) -> Path:
    """Retrieve the documentation directory from teh copier answer file.

    > Default directory is "docs" if not found. This is the main parent directory (not doc_sub_dir)

    Args:
        path_project: Path to the project directory with contains `.copier-answers.yml`

    Returns:
        Path: to the source documentation directory

    """
    path_copier = path_project / _COPIER_ANSWERS_NAME
    return path_project / _read_yaml_file(path_copier).get('doc_dir', 'docs')


@beartype
def trim_trailing_whitespace(pth: Path) -> None:
    """Trim trailing whitespace from the specified file.

    PLANNED: handle carriage returns

    """
    line_break = '\n'
    stripped = [line.rstrip(' ') for line in pth.read_text().split(line_break)]
    pth.write_text(line_break.join(stripped))


# ----------------------------------------------------------------------------------------------------------------------
# Read Files


@beartype
def read_lines(path_file: Path) -> List[str]:
    """Read a file and split on newlines for later parsing.

    Args:
        path_file: path to the file

    Returns:
        List[str]: lines of text as list

    """
    if path_file.is_file():
        return path_file.read_text().split('\n')
    return []


@beartype
def tail_lines(path_file: Path, *, count: int) -> List[str]:
    """Tail a file for up to the last count (or full file) lines.

    Based on: https://stackoverflow.com/a/54278929

    > Tip: `file_size = fh.tell()` -or- `os.fstat(fh.fileno()).st_size` -or- return from `fh.seek(0, os.SEEK_END)`

    Args:
        path_file: path to the file
        count: maximum number of lines to return

    Returns:
        List[str]: lines of text as list

    """
    with open(path_file, 'rb') as f_h:
        rem_bytes = f_h.seek(0, os.SEEK_END)
        step_size = 1  # Initially set to 1 so that the last byte is read
        found_lines = 0
        while found_lines < count and rem_bytes >= step_size:
            rem_bytes = f_h.seek(-1 * step_size, os.SEEK_CUR)
            if f_h.read(1) == b'\n':
                found_lines += 1
            step_size = 2  # Increase so that repeats(read 1 / back 2)

        if rem_bytes < step_size:
            f_h.seek(0, os.SEEK_SET)
        return [line.rstrip('\r') for line in f_h.read().decode().split('\n')]


# ----------------------------------------------------------------------------------------------------------------------
# Manage Files and Directories


@beartype
def if_found_unlink(path_file: Path) -> None:
    """Remove file if it exists. Function is intended to a doit action.

    Args:
        path_file: Path to file to remove

    """
    if path_file.is_file():
        logger.info(f'Deleting `{path_file}`', path_file=path_file)
        path_file.unlink()


@beartype
def delete_old_files(dir_path: Path, *, ttl_seconds: int) -> None:
    """Delete old files within the specified directory.

    Args:
        dir_path: Path to directory to delete
        ttl_seconds: if last modified within this number of seconds, will not be deleted

    """
    for pth in dir_path.rglob('*'):
        if pth.is_file() and (time.time() - pth.stat().st_mtime) > ttl_seconds:
            pth.unlink()


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
    logger.info(f'Creating `{dir_path}`', dir_path=dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)


@beartype
def get_relative(full_path: Path, other_path: Path) -> Optional[Path]:
    """Try to return the relative path between the two paths. None if no match.

    Args:
        full_path: the full path to use
        other_path: the path that the full_path may be relative to

    Returns:
        relative path

    """
    try:
        return full_path.relative_to(other_path)
    except ValueError:
        return
