# ruff: noqa: ERA001
"""nox-uv configuration file.

[Useful snippets from docs](https://nox.thea.codes/en/stable/usage.html)

```sh
source .venv/bin/activate

nox -l
nox --list-sessions

nox -s build_check-3.8 build_dist-3.8 tests-3.8
nox --session tests-3.11

nox --python 3.8

nox -k "not build_check and not build_dist"
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

from beartype.typing import List, Union
from nox import Session as NoxSession
from nox import session as nox_session

from calcipy._corallium.file_helpers import get_tool_versions, read_package_name, read_pyproject


@lru_cache(maxsize=1)
def _get_pythons() -> List[str]:
    """Return python versions from supported configuration files."""
    return [*{str(ver) for ver in get_tool_versions()['python']}]


def _installable_dev_dependencies(pyproject_data: Union[dict, None] = None) -> List[str]:
    """List of dev dependencies from pyproject.toml dependency-groups.

    Args:
        pyproject_data: Optional pyproject data for testing

    Returns:
        List[str]: `['hypothesis[cli] >=6.112.4', 'pytest-asyncio >=0.24.0']`

    """
    pyproject = read_pyproject() if pyproject_data is None else pyproject_data
    return pyproject.get('dependency-groups', {}).get('dev', [])


def _install_local(session: NoxSession) -> None:  # pragma: no cover
    """Ensure local dev-dependencies and calcipy extras are installed.

    Previously required to support poetry, but not re-tested with uv yet.
    See: https://github.com/cjolowicz/nox-poetry/issues/230#issuecomment-855445920

    """
    if read_package_name() == 'calcipy':
        session.run_install(
            'uv',
            'sync',
            '--all-extras',
            env={'UV_PROJECT_ENVIRONMENT': session.virtualenv.location},
        )
    else:
        extras = ['test']
        session.run_install(
            'uv',
            'sync',
            *(f'--extra={extra}' for extra in extras),
            env={'UV_PROJECT_ENVIRONMENT': session.virtualenv.location},
        )

    if dev_deps := _installable_dev_dependencies():
        session.install(*dev_deps)


@nox_session(venv_backend='uv', python=_get_pythons(), reuse_venv=True)
def tests(session: NoxSession) -> None:  # pragma: no cover
    """Run doit test task for specified python versions."""
    _install_local(session)
    session.run(*shlex.split('pytest ./tests'), stdout=True, env={'RUNTIME_TYPE_CHECKING_MODE': 'WARNING'})
