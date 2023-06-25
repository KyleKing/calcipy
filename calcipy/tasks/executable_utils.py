"""Utilities for working in calcipy's python environment."""

import sys
from contextlib import suppress
from functools import lru_cache
from pathlib import Path

from beartype import beartype


@lru_cache(maxsize=1)
@beartype
def resolve_python() -> Path:
    """Resolve the user's Python path based on `sys`."""
    python_path = Path(sys.executable)
    with suppress(ValueError):
        return python_path.relative_to(Path.cwd())
    return python_path


@lru_cache(maxsize=1)
@beartype
def python_dir() -> str:
    """Runs an executable from the currently active Python directory."""
    return str(resolve_python().parent)


@lru_cache(maxsize=1)
@beartype
def python_m() -> str:
    """Return the active python path and `-m` flag."""
    return f'{resolve_python()} -m'
