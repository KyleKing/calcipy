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

from beartype.typing import List
from corallium.file_helpers import get_tool_versions
from nox import Session as NoxSession
from nox import session as nox_session

from calcipy._corallium.file_helpers import read_package_name


@lru_cache(maxsize=1)
def _get_pythons() -> List[str]:
    """Return python versions from supported configuration files."""
    return [*{str(ver) for ver in get_tool_versions()['python']}]


# def _get_poetry_dev_dependencies() -> Dict[str, Dict]:  # type: ignore[type-arg]
#     """Return a dictionary of all dev-dependencies from the 'pyproject.toml'."""
#     poetry_config = file_helpers.read_pyproject()['tool']['poetry']
#
#     def normalize_dep(value: Union[str, Dict]) -> Dict:  # type: ignore[type-arg]
#         return {'version': value} if isinstance(value, str) else value
#
#     return {
#         key: normalize_dep(value)
#         for key, value in {
#             **_retrieve_keys(poetry_config, ['dev', 'dependencies']),
#             **_retrieve_keys(poetry_config, ['group', 'dev', 'dependencies']),
#         }.items()
#     }
#
#
# @lru_cache(maxsize=1)
# def _installable_dev_dependencies() -> List[str]:
#     """List of dependencies from pyproject, excluding calcipy.
#
#     Returns:
#         List[str]: `['Cerberus=>1.3.4', 'freezegun']`
#
#     """
#
#     def to_package(key: str, value: Dict) -> str:  # type: ignore[type-arg]
#         extras = value.get('extras', [])
#         return f'{key}[{",".join(extras)}]' if extras else key
#
#     def to_constraint(value: Dict) -> str:  # type: ignore[type-arg]
#         return str(value['version']).replace('^', '==')
#
#     return [
#         f'{to_package(key, value)}{to_constraint(value)}'
#         for key, value in _get_poetry_dev_dependencies().items()
#         if key != 'calcipy'
#     ]


def _install_local(session: NoxSession) -> None:  # pragma: no cover
    """Ensure local dev-dependencies and calcipy extras are installed.

    Previously required to support poetry, but no re-tested is still required for uv.
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

    # PLANNED: revisit this logic from poetry-implementation
    # if dev_deps := _installable_dev_dependencies():
    #     session.install(*dev_deps)


@nox_session(venv_backend='uv', python=_get_pythons(), reuse_venv=True)
def tests(session: NoxSession) -> None:  # pragma: no cover
    """Run doit test task for specified python versions."""
    _install_local(session)
    session.run(*shlex.split('pytest ./tests'), stdout=True, env={'RUNTIME_TYPE_CHECKING_MODE': 'WARNING'})
