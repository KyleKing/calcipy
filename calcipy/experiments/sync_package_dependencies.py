"""Expriment with setting pyproject versions to latest lock file versions."""

from pathlib import Path

from corallium.log import LOGGER
from corallium.tomllib import tomllib


def _collect_pyproject_versions(pyproject_text: str) -> dict[str, str]:
    """Return pyproject versions without version specification for possible replacement.

    Documentation: https://python-poetry.org/docs/dependency-specification

    """
    pyproject = tomllib.loads(pyproject_text)

    pyproject_versions: dict[str, str] = {}
    # for section in
    pyproject_groups = pyproject['tool']['poetry'].get('group', {})
    groups = [group.get('dependencies', []) for group in pyproject_groups.values()]
    for deps in [pyproject['tool']['poetry']['dependencies'], *groups]:
        for name, value in deps.items():
            if name == 'python':
                continue
            version = value if isinstance(value, str) else value.get('version')
            if not version or any(_c in version for _c in ',*!@/'):
                LOGGER.text('WARNING: requires manually review', name=name, version=version)
            else:
                pyproject_versions[name] = version.lstrip('~^<>=')
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
                # TODO: Handle ">=3.0.0,<4"
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


def replace_versions(path_lock: Path) -> None:
    """Read packages from poetry.lock and update the versions in pyproject.toml.

    Args:
        path_lock: Path to the poetry.lock file

    Raises:
        NotImplementedError: if a lock file other that the poetry lock file is used

    """
    if path_lock.name != 'poetry.lock':
        msg = f'Expected a path to a "poetry.lock" file. Instead, received: "{path_lock.name}"'
        raise NotImplementedError(msg)

    lock = tomllib.loads(path_lock.read_text(encoding='utf-8', errors='ignore'))
    lock_versions = {dependency['name']: dependency['version'] for dependency in lock['package']}

    path_pyproject = path_lock.parent / 'pyproject.toml'
    pyproject_text = path_pyproject.read_text(encoding='utf-8')
    pyproject_versions = _collect_pyproject_versions(pyproject_text)

    path_pyproject.write_text(_replace_pyproject_versions(lock_versions, pyproject_versions, pyproject_text))
