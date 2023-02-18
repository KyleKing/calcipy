"""Invoke Helpers."""

import platform
from functools import lru_cache
from os import environ

from beartype import beartype


@lru_cache(maxsize=1)
@beartype
def use_pty() -> bool:
    """Returns False on Windows and some CI environments."""
    if platform.system() == 'Windows':
        return False
    return not environ.get('GITHUB_ACTION')
