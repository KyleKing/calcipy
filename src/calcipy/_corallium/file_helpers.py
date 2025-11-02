from __future__ import annotations

from contextlib import suppress
from functools import lru_cache
from pathlib import Path

from corallium.file_helpers import find_in_parents, read_pyproject
from corallium.tomllib import tomllib

__all__ = ['get_tool_versions', 'read_package_name', 'read_pyproject']


def _parse_mise_lock(lock_path: Path) -> dict[str, list[str]]:
    """Parse mise.lock file and extract locked tool versions.

    The mise.lock file contains resolved versions for tools, including
    'latest' versions that have been pinned to specific releases.

    """
    content = lock_path.read_bytes()
    data = tomllib.loads(content.decode('utf-8'))

    versions: dict[str, list[str]] = {}

    # Parse [tools] section from lockfile
    if 'tools' in data:
        for tool, tool_data in data['tools'].items():
            if isinstance(tool_data, dict) and 'version' in tool_data:
                version = tool_data['version']
                if version:
                    versions.setdefault(tool, []).append(version)

    return versions


def _parse_mise_toml(mise_path: Path) -> dict[str, list[str]]:
    """Parse mise.toml file and extract tool versions from [tools] section.

    Supports two format variations:
    - Single version string: python = "3.11"
    - Multiple versions array: python = ["3.10", "3.11"]

    """
    content = mise_path.read_bytes()
    data = tomllib.loads(content.decode('utf-8'))

    versions: dict[str, list[str]] = {}

    # Parse [tools] section only
    if 'tools' in data:
        for tool, version in data['tools'].items():
            if isinstance(version, str):
                versions.setdefault(tool, []).append(version)
            elif isinstance(version, list):
                versions.setdefault(tool, []).extend(version)

    return versions


# FIXME: port back to corallium (temporarily extended to support uv and mise)
def get_tool_versions(cwd: Path | None = None) -> dict[str, list[str]]:
    """Return versions from `mise.lock`, `mise.toml`, or `.tool-versions` file.

    Priority order:
    1. mise.lock (contains resolved versions, including 'latest')
    2. mise.toml (contains specified versions)
    3. .tool-versions (legacy asdf format)

    """
    # Try mise.lock first (highest priority - contains resolved versions)
    with suppress(FileNotFoundError):
        lock_path = find_in_parents(name='mise.lock', cwd=cwd)
        return _parse_mise_lock(lock_path)

    # Try mise.toml second
    with suppress(FileNotFoundError):
        mise_path = find_in_parents(name='mise.toml', cwd=cwd)
        return _parse_mise_toml(mise_path)

    # Fall back to .tool-versions (lowest priority)
    tv_path = find_in_parents(name='.tool-versions', cwd=cwd)
    return {line.split(' ')[0]: line.split(' ')[1:] for line in tv_path.read_text().splitlines()}


# FIXME: port back to corallium (temporarily extended to support uv)
@lru_cache(maxsize=5)
def read_package_name(cwd: Path | None = None) -> str:
    """Return the package name."""
    pyproject = read_pyproject(cwd=cwd)
    with suppress(KeyError):
        return str(pyproject['project']['name'])  # For uv
    return str(pyproject['tool']['poetry']['name'])
