"""Invoke Helpers."""

import platform
from contextlib import suppress
from functools import lru_cache
from os import environ
from pathlib import Path

from beartype.typing import Any, Optional
from corallium.file_helpers import COPIER_ANSWERS, read_yaml_file
from invoke.context import Context
from invoke.runners import Result

# ----------------------------------------------------------------------------------------------------------------------
# General Invoke


@lru_cache(maxsize=1)
def use_pty() -> bool:
    """Return False on Windows and some CI environments."""
    if platform.system() == 'Windows':
        return False
    return not environ.get('GITHUB_ACTION')


def run(ctx: Context, *run_args: Any, **run_kwargs: Any) -> Optional[Result]:
    """Return wrapped `invoke.run` to run within the `working_dir`."""
    working_dir = '.'
    with suppress(AttributeError):
        working_dir = ctx.config.gto.working_dir

    with ctx.cd(working_dir):
        return ctx.run(*run_args, **run_kwargs)


# ----------------------------------------------------------------------------------------------------------------------
# Invoke Task Helpers


@lru_cache(maxsize=1)
def get_project_path() -> Path:
    """Returns the `cwd`."""
    return Path.cwd()


def get_doc_subdir(path_project: Optional[Path] = None) -> Path:
    """Retrieve the documentation directory from the copier answer file.

    Args:
        path_project: Path to the project directory with contains `.copier-answers.yml`

    Returns:
        Path: to the source documentation directory

    """
    path_copier = (path_project or get_project_path()) / COPIER_ANSWERS
    doc_dir = read_yaml_file(path_copier).get('doc_dir', 'docs')
    return path_copier.parent / doc_dir / 'docs'
