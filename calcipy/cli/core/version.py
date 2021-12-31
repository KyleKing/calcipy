"""Version Utility."""

from typing import Iterable

from beartype import beartype
from cement.utils.version import get_version as cement_get_version

from ... import __version__

_VERSION = __version__.split('.')[:3] + ['beta', '0']  # Expects exactly 5 values


@beartype
def get_version(version: Iterable[str] = _VERSION) -> str:
    """Format the version for printing."""
    return cement_get_version(version)
