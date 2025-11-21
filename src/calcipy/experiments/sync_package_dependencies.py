"""Experiment with setting pyproject versions to latest lock file versions.

Supports both poetry.lock and uv.lock formats.

"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from corallium.log import LOGGER
from corallium.tomllib import tomllib


def _extract_base_version(version_spec: str) -> str:
    """Extract the base version from a version specification."""
    # Find version numbers in the spec
    version_match = re.search(r'(\d+(?:\.\d+)*(?:\.\d+)*)', version_spec)
    return version_match.group(1) if version_match else version_spec


def _parse_pep621_dependency(dep_spec: str) -> tuple[str, str] | None:
    """Parse a PEP 621 dependency string into (package_name, version).

    Handles formats like:
    - "package>=1.0.0"
    - "package[extra]>=1.0.0"
    - "package[extra1,extra2]>=1.0.0"
    - "zope.interface>=5.0.0" (dot-separated package names)

    Args:
        dep_spec: Dependency specification string

    Returns:
        Tuple of (package_name, version) or None if no version specified

    """
    # Match package name (with optional extras) and version spec
    # Package name can contain letters, numbers, hyphens, underscores, dots
    # Extras are in square brackets
    # Version spec starts with comparison operators
    match = re.match(r'^([a-zA-Z0-9_.-]+(?:\[[^\]]+\])?)([><=!~].+)?$', dep_spec.strip())
    if not match:
        return None

    package_name = match.group(1)
    version_spec = match.group(2)

    # Remove extras from package name for version tracking
    base_package_name = re.sub(r'\[.+\]', '', package_name)

    if version_spec:
        return (base_package_name, _extract_base_version(version_spec))

    return None


def _collect_uv_dependencies(pyproject: dict[str, Any]) -> dict[str, str]:
    """Collect dependencies from UV format sections.

    Args:
        pyproject: Parsed pyproject.toml data

    Returns:
        Dictionary mapping package names to versions

    """
    versions: dict[str, str] = {}
    deps_sources: list[Any] = []

    # Collect from [project.dependencies]
    if 'project' in pyproject:
        if 'dependencies' in pyproject['project']:
            deps_sources.append(pyproject['project']['dependencies'])

        # Collect from [project.optional-dependencies]
        if 'optional-dependencies' in pyproject['project']:
            deps_sources.extend(pyproject['project']['optional-dependencies'].values())

    # Collect from [dependency-groups]
    if 'dependency-groups' in pyproject:
        deps_sources.extend(pyproject['dependency-groups'].values())

    # Parse list format dependencies
    for deps in deps_sources:
        if isinstance(deps, list):
            for dep_spec in deps:
                if not isinstance(dep_spec, str):
                    continue
                result = _parse_pep621_dependency(dep_spec)
                if result:
                    name, version = result
                    versions[name] = version

    return versions


def _collect_poetry_dependencies(pyproject: dict[str, Any]) -> dict[str, str]:
    """Collect dependencies from Poetry format sections.

    Args:
        pyproject: Parsed pyproject.toml data

    Returns:
        Dictionary mapping package names to versions

    """
    versions: dict[str, str] = {}

    if 'tool' not in pyproject or 'poetry' not in pyproject['tool']:
        return versions

    poetry_config = pyproject['tool']['poetry']

    # Collect from [tool.poetry.dependencies]
    deps_sources: list[dict[str, Any]] = [poetry_config.get('dependencies', {})]

    # Collect from [tool.poetry.group.*.dependencies]
    poetry_groups = poetry_config.get('group', {})
    deps_sources.extend([group.get('dependencies', {}) for group in poetry_groups.values()])

    # Parse dict format dependencies
    for deps in deps_sources:
        if isinstance(deps, dict):
            for name, value in deps.items():
                if name == 'python':
                    continue
                version = value if isinstance(value, str) else value.get('version') if isinstance(value, dict) else None
                if version:
                    versions[name] = _extract_base_version(version)

    return versions


def _collect_pyproject_versions(pyproject_text: str) -> dict[str, str]:
    """Return pyproject versions without version specification for possible replacement.

    Supports both poetry and uv dependency formats:
    - Poetry: https://python-poetry.org/docs/dependency-specification
    - UV: Uses [project.dependencies] and [dependency-groups]

    """
    pyproject = tomllib.loads(pyproject_text)

    # Collect from both UV and Poetry formats
    uv_versions = _collect_uv_dependencies(pyproject)
    poetry_versions = _collect_poetry_dependencies(pyproject)

    # Merge, preferring UV versions if both exist
    return {**poetry_versions, **uv_versions}


def _replace_poetry_versions(
    line: str,
    name: str,
    lock_version: str,
    pyproject_version: str,
) -> str | None:
    """Replace version in Poetry dict format line.

    Args:
        line: Line from pyproject.toml
        name: Package name
        lock_version: New version from lock file
        pyproject_version: Current version in pyproject

    Returns:
        Updated line or None if no replacement made

    """
    if pyproject_version != lock_version and pyproject_version in line:
        LOGGER.text(
            'Upgrade minimum package version',
            name=name,
            new_version=lock_version,
            old_version=pyproject_version,
        )
        return line.replace(pyproject_version, lock_version, 1)
    return None


def _replace_pep621_versions(
    line: str,
    lock_versions: dict[str, str],
    pyproject_versions: dict[str, str],
) -> str | None:
    """Replace version in PEP 621 list format line.

    Args:
        line: Line from pyproject.toml (e.g., '  "package>=1.0.0",')
        lock_versions: Versions from lock file
        pyproject_versions: Current versions in pyproject

    Returns:
        Updated line or None if no replacement made

    """
    # Extract package spec from line (handle quotes and commas)
    stripped = line.strip().strip('"\'').rstrip(',')
    result = _parse_pep621_dependency(stripped)

    if not result:
        return None

    name, _ = result

    lock_version = lock_versions.get(name)
    pyproject_version = pyproject_versions.get(name)

    if not (lock_version and pyproject_version):
        return None

    if pyproject_version != lock_version and pyproject_version in line:
        LOGGER.text(
            'Upgrade minimum package version',
            name=name,
            new_version=lock_version,
            old_version=pyproject_version,
        )
        return line.replace(pyproject_version, lock_version, 1)

    return None


def _is_dependency_section(section: str) -> bool:
    """Check if section is dependency-related.

    Matches sections that can contain dependencies, but not unrelated
    sections like [project.urls], [project.scripts], etc.

    """
    section_lower = section.lower()

    # Match sections that can contain dependencies
    valid_sections = {
        '[project]',
        '[project.optional-dependencies]',
        '[dependency-groups]',
        '[tool.poetry.dependencies]',
    }

    if section_lower in valid_sections:
        return True

    # Poetry groups like [tool.poetry.group.dev.dependencies]
    if '.group.' in section_lower and 'dependencies' in section_lower:
        return True

    # Exclude non-dependency project sections
    if section_lower.startswith('[project.') and section_lower not in valid_sections:
        return False

    return False


def _try_replace_poetry_line(
    line: str,
    lock_versions: dict[str, str],
    pyproject_versions: dict[str, str],
) -> str | None:
    """Try to replace version in Poetry dict format line."""
    name = line.split('=')[0].strip()
    lock_version = lock_versions.get(name)
    pyproject_version = pyproject_versions.get(name)

    if lock_version and pyproject_version:
        return _replace_poetry_versions(line, name, lock_version, pyproject_version)
    if lock_version and not pyproject_version:
        LOGGER.text('WARNING: consider manually updating the version', new_version=lock_version)
    return None


def _handle_single_line_list(
    line: str,
    lock_versions: dict[str, str],
    pyproject_versions: dict[str, str],
) -> str | None:
    """Handle single-line list format like: dependencies = ["pkg>=1.0"].

    Returns the replaced line or None if no replacement was made.

    """
    stripped = line.split('#')[0].strip()
    list_content = stripped[stripped.index('[') + 1:stripped.index(']')].strip()

    if list_content and ('"' in list_content or "'" in list_content) and (
        replaced := _replace_pep621_versions(list_content, lock_versions, pyproject_versions)
    ):
        # Reconstruct the line with replaced version
        before_bracket = line[:line.index('[') + 1]
        after_bracket = line[line.index(']'):]
        return f'{before_bracket}{replaced}{after_bracket}'

    return None


def _replace_pyproject_versions(
    lock_versions: dict[str, str],
    pyproject_versions: dict[str, str],
    pyproject_text: str,
) -> str:
    """Return pyproject text with replaced versions.

    Handles both Poetry dict format and PEP 621 list format.

    """
    new_lines: list[str] = []
    active_section = ''
    in_dependency_list = False

    for line in pyproject_text.split('\n'):
        # Track current section
        if line.startswith('['):
            active_section = line
            in_dependency_list = False

        is_dep_section = _is_dependency_section(active_section)

        # Handle lines with '=' in dependency sections
        if '=' in line and is_dep_section and not line.strip().startswith('#'):
            stripped = line.split('#')[0].strip()  # Remove trailing comments

            # Check if line starts a list
            if '[' in stripped:
                in_dependency_list = True
                if ']' not in stripped:
                    # Multi-line list, will handle items on subsequent lines
                    new_lines.append(line)
                    continue

                # Single-line list - handle inline
                if replaced := _handle_single_line_list(line, lock_versions, pyproject_versions):
                    new_lines.append(replaced)
                    continue

            # Poetry dict format (name = "version")
            elif not in_dependency_list and ']' not in line and (
                replaced := _try_replace_poetry_line(line, lock_versions, pyproject_versions)
            ):
                new_lines.append(replaced)
                continue

        # Try PEP 621 list format for multi-line lists
        has_quotes = '"' in line or "'" in line
        if (
            in_dependency_list
            and has_quotes
            and (replaced := _replace_pep621_versions(line, lock_versions, pyproject_versions))
        ):
            new_lines.append(replaced)
            continue

        # Check if we're leaving a list
        if in_dependency_list and line.strip() == ']':
            in_dependency_list = False

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
