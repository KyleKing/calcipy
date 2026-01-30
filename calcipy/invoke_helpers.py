"""Invoke Helpers."""

import platform
from contextlib import suppress
from functools import lru_cache
from os import environ
from pathlib import Path

from beartype.typing import Any, Optional
from corallium.file_helpers import COPIER_ANSWERS, read_yaml_file
from corallium.log import LOGGER
from corallium.vcs import find_repo_root
from invoke.context import Context
from invoke.runners import Result

# ----------------------------------------------------------------------------------------------------------------------
# General Invoke


@lru_cache(maxsize=1)
def use_pty() -> bool:
    """Return False on Windows and some CI environments."""
    if platform.system() == 'Windows':  # pragma: no cover
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

    Searches for `.copier-answers.yml` at path_project first, then at repo root if not found.
    The doc_dir config is read from wherever the file is found, but the returned path is
    always relative to path_project.

    Args:
        path_project: Path to the project directory with contains `.copier-answers.yml`

    Returns:
        Path: to the source documentation directory

    """
    base_path = path_project or get_project_path()
    path_copier = base_path / COPIER_ANSWERS

    # If not found at base_path, try repo root
    if not path_copier.is_file():
        repo_root = find_repo_root(base_path)
        if repo_root:
            path_copier_at_root = repo_root / COPIER_ANSWERS
            if path_copier_at_root.is_file():
                LOGGER.debug('Found .copier-answers.yml at repo root', repo_root=repo_root)
                path_copier = path_copier_at_root
            else:
                LOGGER.debug('.copier-answers.yml not found at repo root', repo_root=repo_root)

    doc_dir = read_yaml_file(path_copier).get('doc_dir', 'docs')
    # Always return path relative to base_path, not where copier answers was found
    return base_path / doc_dir / 'docs'
