from __future__ import annotations

from contextlib import suppress
from functools import lru_cache
from pathlib import Path

from corallium.file_helpers import read_pyproject


@lru_cache(maxsize=5)
def read_package_name(cwd: Path | None = None) -> str:
    """Return the package name."""
    pyproject = read_pyproject(cwd=cwd)
    with suppress(KeyError):
        return str(pyproject['project']['name'])  # For uv
    return str(pyproject['tool']['poetry']['name'])
