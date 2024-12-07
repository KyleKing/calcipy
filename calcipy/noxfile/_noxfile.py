"""nox-uv configuration file.

[Useful snippets from docs](https://nox.thea.codes/en/stable/usage.html)

```sh
uv run nox -l
uv run nox --list-sessions

uv run nox -s build_check-3.8 build_dist-3.8 tests-3.8
uv run nox --session tests-3.11

uv run nox --python 3.8

uv run nox -k "not build_check and not build_dist"
```

Useful nox snippets

```python3
# Example conditionally skipping a session
if not session.interactive:
    session.skip('Cannot run detect-secrets audit in non-interactive shell')

# Install pinned version
session.install('detect-secrets==1.0.3')

# Example capturing STDOUT into a file (could do the same for stderr)
path_stdout = Path('.stdout.txt').resolve()
with open(path_stdout, 'w') as out:
    session.run(*shlex.split('echo Hello World!'), stdout=out)
```

"""

import shlex
from functools import lru_cache

from beartype.typing import Dict, List, Union, cast
from corallium import file_helpers  # Required for mocking read_pyproject
from corallium.file_helpers import get_lock, get_tool_versions, read_package_name
from corallium.tomllib import tomllib
from nox import Session as NoxSession
from nox_uv.sessions import Session as NPSession

if read_package_name() == 'corallium':
    # 'uv export' will fail on circular dependencies, so use nox instead of nox-uv
    from nox import session as nox_session
else:
    from nox_uv import session as nox_session  # type: ignore[no-redef]


@lru_cache(maxsize=1)
def _get_pythons() -> List[str]:
    """Return python versions from the `.tool-versions` file."""
    # TODO: interop for uv/uv/* && asdf/mise
    return [*{str(ver) for ver in get_tool_versions()['python']}]


def _get_uv_dev_dependencies() -> Dict[str, Dict]:  # type: ignore[type-arg]
    """Return a dictionary of all dev-dependencies from the 'pyproject.toml'."""
    result = {}
    extras = file_helpers.read_pyproject()['project'].get('optional-dependencies', {})
    for deps in extras.values():
        for dep in deps:
            name, constraint = dep.split(' ', maxsplit=1)
            if '=' in name:
                raise ValueError('Excepted a space between dependency name and constraint')
            result[name] = {'version': constraint}
    return result


@lru_cache(maxsize=1)
def _installable_dev_dependencies() -> List[str]:
    """List of dependencies from pyproject, excluding calcipy.

    Returns:
        List[str]: `['Cerberus=>1.3.4', 'freezegun']`

    """

    def to_package(key: str, value: Dict) -> str:  # type: ignore[type-arg]
        extras = value.get('extras', [])
        return f'{key}[{",".join(extras)}]' if extras else key

    def to_constraint(value: Dict) -> str:  # type: ignore[type-arg]
        return str(value['version']).replace('^', '==')

    return [
        f'{to_package(key, value)}{to_constraint(value)}'
        for key, value in _get_uv_dev_dependencies().items()
        if key != 'calcipy'
    ]


def _install_local(session: Union[NoxSession, NPSession]) -> None:  # pragma: no cover
    """Ensure local dev-dependencies and calcipy extras are installed.

    See: https://github.com/cjolowicz/nox-uv/issues/230#issuecomment-855445920

    """
    if read_package_name() == 'calcipy':
        session = cast(NPSession, session)
        lock_data = tomllib.loads(get_lock().read_text())
        session.uv.installroot(extras=[*lock_data['extras']])  # First party extras
    else:
        extras = ['test']
        session.install('.', f'calcipy[{",".join(extras)}]')

    if dev_deps := _installable_dev_dependencies():
        session.install(*dev_deps)


@nox_session(python=_get_pythons(), reuse_venv=True)
def tests(session: Union[NoxSession, NPSession]) -> None:  # pragma: no cover
    """Run doit test task for specified python versions."""
    _install_local(session)
    session.run(*shlex.split('pytest ./tests'), stdout=True, env={'RUNTIME_TYPE_CHECKING_MODE': 'WARNING'})
