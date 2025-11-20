"""Experiment with setting pyproject versions to latest lock file versions.

Supports both poetry.lock and uv.lock formats.

"""

import re
from pathlib import Path

from corallium.log import LOGGER
from corallium.tomllib import tomllib


def _extract_base_version(version_spec: str) -> str:
    """Extract the base version from a version specification."""
    # Find version numbers in the spec
    version_match = re.search(r'(\d+(?:\.\d+)*(?:\.\d+)*)', version_spec)
    return version_match.group(1) if version_match else version_spec


def _collect_pyproject_versions(pyproject_text: str) -> dict[str, str]:
    """Return pyproject versions without version specification for possible replacement.

    Supports both poetry and uv dependency formats:
    - Poetry: https://python-poetry.org/docs/dependency-specification
    - UV: Uses [project.dependencies] and [dependency-groups]

    """
    pyproject = tomllib.loads(pyproject_text)

    pyproject_versions: dict[str, str] = {}

    # Collect dependencies from different formats
    deps_sources = []

    # UV format: [project.dependencies] and [dependency-groups]
    if 'project' in pyproject:
        if 'dependencies' in pyproject['project']:
            deps_sources.append(pyproject['project']['dependencies'])

        # Optional dependencies
        if 'optional-dependencies' in pyproject['project']:
            deps_sources.extend(pyproject['project']['optional-dependencies'].values())

    # UV dependency-groups
    if 'dependency-groups' in pyproject:
        deps_sources.extend(pyproject['dependency-groups'].values())

    # Poetry format: [tool.poetry.dependencies] and groups
    if 'tool' in pyproject and 'poetry' in pyproject['tool']:
        deps_sources.append(pyproject['tool']['poetry']['dependencies'])

        pyproject_groups = pyproject['tool']['poetry'].get('group', {})
        deps_sources.extend([group.get('dependencies', {}) for group in pyproject_groups.values()])

    # Process all dependency sources
    for deps in deps_sources:
        if isinstance(deps, list):
            # UV format: list of strings like "package>=1.0.0"
            for dep_spec in deps:
                if not isinstance(dep_spec, str):
                    continue
                # Parse "package>=1.0.0" format
                match = re.match(r'^([a-zA-Z0-9_-]+)([><=!]+.+)?$', dep_spec)
                if match:
                    name = match.group(1)
                    version_spec = match.group(2) or ''
                    if version_spec:
                        pyproject_versions[name] = _extract_base_version(version_spec)
        elif isinstance(deps, dict):
            # Poetry format: dict of {package: version}
            for name, value in deps.items():
                if name == 'python':
                    continue
                version = value if isinstance(value, str) else value.get('version') if isinstance(value, dict) else None
                if version:
                    pyproject_versions[name] = _extract_base_version(version)

    return pyproject_versions


def _replace_pyproject_versions(
    lock_versions: dict[str, str],
    pyproject_versions: dict[str, str],
    pyproject_text: str,
) -> str:
    """Return pyproject text with replaced versions."""
    new_lines: list[str] = []
    active_section = ''
    for line in pyproject_text.split('\n'):
        if line.startswith('['):
            active_section = line
        elif '=' in line and 'dependencies' in active_section:
            name = line.split('=')[0].strip()
            if (lock_version := lock_versions.get(name)) and (pyproject_version := pyproject_versions.get(name)):
                versions = {'name': name, 'new_version': lock_version, 'old_version': pyproject_version}
                if pyproject_version != lock_version:
                    if pyproject_version in line:
                        new_lines.append(line.replace(pyproject_version, lock_version, 1))
                        LOGGER.text('Upgrade minimum package version', **versions)  # type: ignore[arg-type]
                        continue
                    LOGGER.warning(
                        'Could not set new version. Please do so manually and submit a bug report',
                        line=line,
                        **versions,
                    )
            elif lock_version and not pyproject_versions.get(name):
                LOGGER.text('WARNING: consider manually updating the version', new_version=lock_version)

        new_lines.append(line)
    return '\n'.join(new_lines)


def _parse_lock_file(path_lock: Path) -> dict[str, str]:
    """Parse lock file and return package versions.

    Supports both poetry.lock and uv.lock formats.

    Args:
        path_lock: Path to the lock file (poetry.lock or uv.lock)

    Returns:
        Dictionary mapping package names to versions

    Raises:
        NotImplementedError: if the lock file format is not recognized

    """
    lock_content = path_lock.read_text(encoding='utf-8', errors='ignore')
    lock = tomllib.loads(lock_content)

    if path_lock.name == 'poetry.lock':
        # Poetry format: list of packages under 'package' key
        return {dependency['name']: dependency['version'] for dependency in lock.get('package', [])}
    if path_lock.name == 'uv.lock':
        # UV format: list of [[package]] sections
        return {pkg['name']: pkg['version'] for pkg in lock.get('package', [])}

    msg = f'Unsupported lock file format: "{path_lock.name}". Expected "poetry.lock" or "uv.lock"'
    raise NotImplementedError(msg)


def replace_versions(path_lock: Path) -> None:
    """Read packages from lock file and update the versions in pyproject.toml.

    Supports both poetry.lock and uv.lock formats.

    Args:
        path_lock: Path to the lock file (poetry.lock or uv.lock)

    Raises:
        NotImplementedError: if the lock file format is not recognized

    """
    if path_lock.name not in {'poetry.lock', 'uv.lock'}:
        msg = f'Expected a path to a "poetry.lock" or "uv.lock" file. Instead, received: "{path_lock.name}"'
        raise NotImplementedError(msg)

    lock_versions = _parse_lock_file(path_lock)

    path_pyproject = path_lock.parent / 'pyproject.toml'
    pyproject_text = path_pyproject.read_text(encoding='utf-8')
    pyproject_versions = _collect_pyproject_versions(pyproject_text)

    path_pyproject.write_text(_replace_pyproject_versions(lock_versions, pyproject_versions, pyproject_text))
