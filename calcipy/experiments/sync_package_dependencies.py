"""Expriment with setting pyproject versions to latest lock file versions."""

from pathlib import Path

from corallium.log import LOGGER
from corallium.tomllib import tomllib


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
    pyproject = tomllib.loads(pyproject_text)

    pyproject_versions: dict[str, str] = {}
    # for section in
    groups = [group['dependencies'] for group in pyproject['tool']['poetry']['group'].values()]
    for deps in [pyproject['tool']['poetry']['dependencies'], *groups]:
        for name, value in deps.items():
            if name == 'python':
                continue
            pyproject_versions[name] = value if isinstance(value, str) else value['version']

    new_lines: list[str] = []
    active_section = ''
    for line in pyproject_text.split('\n'):
        if line.startswith('['):
            active_section = line
        elif '=' in line and 'dependencies' in active_section:
            name = line.split('=')[0].strip()
            if lock_version := lock_versions.get(name):
                if (pyproject_version := pyproject_versions[name].lstrip('^>=')) in line:
                    new_lines.append(line.replace(pyproject_version, lock_version, 1))
                    continue
                LOGGER.warning(
                    'Could not set new version. Please do so manually and submit a bug report',
                    line=line,
                    new_version=lock_version,
                    old_version=pyproject_version,
                )
        new_lines.append(line)
    path_pyproject.write_text('\n'.join(new_lines))
