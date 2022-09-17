"""Don't set a CAP for Python dependencies for packages and avoid for projects when possible.

> https://iscinumpy.dev/post/bound-version-constraints/#tldr
This script is useful for raising the floor, which helps reduce the load on a dependency
resolver by reducing the possible number of combinations to consider

"""

import re
from pathlib import Path

import tomlkit
from loguru import logger

from calcipy.proc_helpers import run_cmd

# Globals
RE_FREEZE = re.compile(r'^(?P<name>[^=]+)==(?P<version>\d+\..+)$')
RE_TOML_VER = re.compile(r'^(?P<prefix>[^\d+]+)\d+.*$')

# TODO: Convert to function arguments - see example from code_tag_collector
cwd = Path(__file__).parent
py_path = 'poetry run python'  # Or path to .venv python, etc.
path_toml = cwd / 'pyproject.toml'
skipped_packages = set(['python'] + [])  # << TODO: Merge with user list

# HACK: For quick testing
# pip_freeze = """
# watchdog==2.1.7
# wheel==0.36.2
# wrapt==1.14.0
# xenon==0.9.0
# yamllint==1.26.3
# yarl==1.7.2
# zipp==3.8.0
# WARNING: You are using pip version 21.3.1; however, version 22.2 is available.
# You should consider upgrading via the '/Users/kyleking/Developer/recipes/.venv/bin/python -m pip install --upgrade pip' command.
#
# """

# Generate freeze file
# Use list instead of freeze. See: https://stackoverflow.com/a/62886215/3219667
pip_freeze = run_cmd(f'{py_path} -m pip list --format=freeze', cwd=str(cwd))

# TODO: Consider using pip-pi instead!
# https://pypi.org/project/pip-api/

# Parse each line from freeze pip_freeze into dictionary: {name: version}
freeze_dict = {}
for line in pip_freeze.split('\n'):
    match = RE_FREEZE.match(line)
    if match:
        group_dict = match.groupdict()
        if group_dict['name'] not in skipped_packages:
            freeze_dict[group_dict['name']] = group_dict['version']

# Update the dependency minimum versions to match what is installed
toml_config = tomlkit.loads(path_toml.read_text())
poetry_config = toml_config['tool']['poetry']
for dep_key in ['dependencies', 'dev-dependencies']:
    dependencies = poetry_config.get(dep_key) or {}
    for name, version in freeze_dict.items():
        try:
            # Dictionary entry `package = {version = "*"}`
            old_ver = dependencies.get(name, {}).get('version')
        except AttributeError:
            # For shorthand `package = "*"`
            old_ver = dependencies.get(name)

        if old_ver:
            match = RE_TOML_VER.match(old_ver)
            if match:
                prefix = match.groupdict()['prefix']
            elif old_ver == '*':
                prefix = '>='
            else:
                raise RuntimeError(f'Could not parse `{old_ver}` with `{RE_TOML_VER}`')

            new_ver = f'{prefix}{version}'
            if old_ver != new_ver:
                logger.info(f"Upgrading '{name}' from '{old_ver}' to '{new_ver}'")
            try:
                dependencies[name]['version'] = new_ver  # Dictionary entry
            except TypeError:
                dependencies[name] = new_ver  # For shorthand
            continue

# Write the update Pyproject.toml file
path_toml.write_text(tomlkit.dumps(toml_config))
