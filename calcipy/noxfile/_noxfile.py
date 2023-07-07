"""nox-poetry configuration file.

[Useful snippets from docs](https://nox.thea.codes/en/stable/usage.html)

```sh
poetry run nox -l
poetry run nox --list-sessions

poetry run nox -s build_check-3.8 build_dist-3.8 tests-3.8
poetry run nox --session tests-3.11

poetry run nox --python 3.8

poetry run nox -k "not build_check and not build_dist"
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
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

from beartype import beartype
from beartype.typing import Dict, List, Union, cast
from corallium import file_helpers  # Required for mocking read_pyproject
from corallium.file_helpers import get_tool_versions, if_found_unlink, read_package_name
from corallium.log import logger
from nox import Session as NoxSession
from nox_poetry import session as nox_poetry_session
from nox_poetry.poetry import DistributionFormat
from nox_poetry.sessions import Session as NPSession

if read_package_name() == 'corallium':
    # 'poetry export' will fail on circular dependencies, so use no instead of nox-poetry
    from nox import session as nox_session
else:
    from nox_poetry import session as nox_session  # type: ignore[no-redef]


@lru_cache(maxsize=1)
@beartype
def _get_pythons() -> List[str]:
    """Get python versions from the `.tool-versions` file."""
    return [*{str(ver) for ver in get_tool_versions()['python']}]


@beartype
def _retrieve_keys(source: Dict, keys: List[str]) -> Dict:  # type: ignore[type-arg]
    """Retrieve nested dictionary keys unless not found."""
    result = source
    for key in keys:
        if not (result := result.get(key)):  # type: ignore[assignment]
            return {}
    return result


@beartype
def _get_poetry_dev_dependencies() -> Dict[str, Dict]:  # type: ignore[type-arg]
    """Return a dictionary of all dev-dependencies from the 'pyproject.toml'."""
    poetry_config = file_helpers.read_pyproject()['tool']['poetry']

    @beartype
    def normalize_dep(value: Union[str, Dict]) -> Dict:  # type: ignore[type-arg]
        return {'version': value} if isinstance(value, str) else value

    return {
        key: normalize_dep(value) for key, value in {
            **_retrieve_keys(poetry_config, ['dev', 'dependencies']),
            **_retrieve_keys(poetry_config, ['group', 'dev', 'dependencies']),
        }.items()
    }


@lru_cache(maxsize=1)
@beartype
def _installable_dev_dependencies() -> List[str]:
    """list of dependencies from pyproject, excluding calcipy.

    Returns:
        List[str]: `['Cerberus=>1.3.4', 'freezegun']`

    """
    @beartype
    def to_package(key: str, value: Dict) -> str:  # type: ignore[type-arg]
        extras = value.get('extras', [])
        return f'{key}[{",".join(extras)}]' if extras else key

    @beartype
    def to_constraint(value: Dict) -> str:  # type: ignore[type-arg]
        return str(value['version']).replace('^', '==')

    return [
        f'{to_package(key, value)}{to_constraint(value)}'
        for key, value in _get_poetry_dev_dependencies().items()
        if key != 'calcipy'
    ]


@beartype
def _install_local(session: Union[NoxSession, NPSession], extras: List[str]) -> None:  # pragma: no cover
    """Ensure local dev-dependencies and calcipy extras are installed.

    See: https://github.com/cjolowicz/nox-poetry/issues/230#issuecomment-855445920

    """
    if read_package_name() == 'calcipy':
        session = cast(NPSession, session)
        session.poetry.installroot(extras=extras)
    else:
        session.install('.', f'calcipy[{",".join(extras)}]')

    if dev_deps := _installable_dev_dependencies():
        session.install(*dev_deps)


@nox_session(python=_get_pythons(), reuse_venv=True)
def tests(session: Union[NoxSession, NPSession]) -> None:  # pragma: no cover
    """Run doit test task for specified python versions."""
    _install_local(session, ['ddict', 'doc', 'lint', 'nox', 'stale', 'tags', 'test'])
    session.run(*shlex.split('pytest ./tests'), stdout=True)


@nox_session(python=_get_pythons()[-1:], reuse_venv=False)
def build_dist(session: Union[NoxSession, NPSession]) -> None:  # pragma: no cover
    """Build and test the project files within a controlled environment for repeatability."""
    dist_path = Path('dist')
    if_found_unlink(dist_path)

    # Support 'corallium' by re-implementing "session.poetry.build_package()", from:
    # https://github.com/cjolowicz/nox-poetry/blob/5772b66ebff8d5a3351a08ed402d3d31e48be5f8/src/nox_poetry/sessions.py#L233-L255
    # https://github.com/cjolowicz/nox-poetry/blob/5772b66ebff8d5a3351a08ed402d3d31e48be5f8/src/nox_poetry/poetry.py#L111-L154
    output = session.run(*shlex.split('poetry build --format=wheel --no-ansi'),
                         external=True, silent=True, stderr=None)
    output = cast(str, output)
    wheel = dist_path / output.split()[-1]
    path_wheel = wheel.resolve().as_uri()

    logger.text('Created wheel', path_wheel=path_wheel)
    # Install the wheel and check that imports without any of the optional dependencies
    session.install(path_wheel)
    session.run(*shlex.split('python scripts/check_imports.py'), stdout=True)


@nox_poetry_session(python=_get_pythons()[-1:], reuse_venv=True)
def build_check(session: NPSession) -> None:  # pragma: no cover
    """Check that the built output meets all checks."""
    # Build sdist and fix return URI, which will have file://...#egg=calcipy
    sdist_uri = session.poetry.build_package(distribution_format=DistributionFormat.SDIST)
    path_sdist = Path(url2pathname(urlparse(sdist_uri).path))
    logger.text_debug('Fixed sdist URI', sdist_uri=sdist_uri, path_sdist=path_sdist)
    # Check with pyroma
    session.install('pyroma>=4.0', '--upgrade')
    # required for "poetry.core.masonry.api" build backend
    session.run('python', '-m', 'pip', 'install', 'poetry>=1.3', stdout=True)
    session.run('pyroma', '--file', path_sdist.as_posix(), '--min=9', stdout=True)
