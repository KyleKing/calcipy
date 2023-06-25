"""Utilities for working in calcipy's python environment."""

import sys
from contextlib import suppress
from functools import lru_cache
from pathlib import Path

from beartype import beartype
from invoke.context import Context

from ..invoke_helpers import run


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


PYRIGHT_MESSAGE = """
`pyright` was not found and must be installed separately (such as 'brew install pyright' on Mac).
    See the online documentation for your system: https://microsoft.github.io/pyright/#/installation
"""
PRE_COMMIT_MESSAGE = """
`pre-commit` was not found and must be installed separately (such as 'brew install pre-commit' on Mac).
    See the online documentation for your system: https://pre-commit.com/#install
"""
GH_MESSAGE = """
`gh` was not found and must be installed separately (such as 'brew install gh' on Mac).
    See the online documentation for your system: https://cli.github.com/
"""


@beartype
def check_installed(ctx: Context, executable: str, message: str) -> None:
    """If the required executable isn't present, raise a clear user error."""
    res = run(ctx, f'which {executable}', warn=True, hide=True)
    if not res or res.exited == 1:
        raise RuntimeError(message)
