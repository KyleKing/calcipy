"""nox-poetry configuration file.

[Useful snippets from docs](https://nox.thea.codes/en/stable/usage.html)

```sh
poetry run nox -l
poetry run nox --list-sessions

poetry run nox -s build_check-3.9 build_dist-3.9 coverage-3.9
poetry run nox --session coverage-3.9

poetry run nox --python 3.8

poetry run nox -k "not tests and not coverage"
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
from beartype.typing import Dict, List, Union
from nox_poetry import session as nox_session
from nox_poetry.poetry import DistributionFormat
from nox_poetry.sessions import Session
from shoal import get_logger

from ..file_helpers import get_tool_versions, if_found_unlink, read_package_name, read_pyproject

logger = get_logger()


@lru_cache(maxsize=1)
@beartype
def _get_pythons() -> List[str]:
    """Read the `.tool-versions` file."""
    return get_tool_versions()['python']


@lru_cache(maxsize=1)
@beartype
def _get_dev_deps() -> List[str]:
    """list of dependencies from pyproject.

    Returns:
        List[str]: `['Cerberus=>1.3.4', 'freezegun']`

    """
    @beartype
    def to_package(key: str, value: Union[Dict, str]) -> str:
        extras = [] if isinstance(value, str) else value.get('extras', [])
        if extras:
            key += f'[{",".join(extras)}]'
        return key

    @beartype
    def to_constraint(value: Union[Dict, str]) -> str:
        version = value if isinstance(value, str) else value['version']
        return version.replace('^', '==')

    poetry_config = read_pyproject()['tool']['poetry']
    dependencies = {
        **poetry_config.get('dev', {}).get('dependencies', {}),
        **poetry_config.get('group', {}).get('dev', {}).get('dependencies', {}),
    }
    return [f'{to_package(key, value)}{to_constraint(value)}' for key, value in dependencies.items()]


@beartype
def _install_local(session: Session, extras: List[str]) -> None:
    """Ensure local dev-dependencies and calcipy extras are installed.

    See: https://github.com/cjolowicz/nox-poetry/issues/230#issuecomment-855445920

    """
    if read_package_name() == 'calcipy':
        session.poetry.installroot(extras=extras)
    else:  # pragma: no cover
        session.install('.', f'calcipy[{",".join(extras)}]')

    session.install(*_get_dev_deps())


@nox_session(python=_get_pythons(), reuse_venv=True)
def tests(session: Session) -> None:
    """Run doit test task for specified python versions.

    Args:
        session: nox_poetry Session

    """
    _install_local(session, ['dev', 'test'])
    session.run(*shlex.split('pytest ./tests'), stdout=True)


@nox_session(python=_get_pythons()[-1:], reuse_venv=True)
def coverage(session: Session) -> None:
    """Run doit test task for specified python versions.

    Args:
        session: nox_poetry Session

    """
    _install_local(session, ['dev', 'test'])
    pkg_name = read_package_name()
    session.run(
        *shlex.split(f'pytest ./tests --cov={pkg_name} --cov-report=term-missing'),
        stdout=True,
    )


@nox_session(python=_get_pythons()[-1:], reuse_venv=False)
def build_dist(session: Session) -> None:
    """Build the project files within a controlled environment for repeatability.

    Args:
        session: nox_poetry Session

    """
    if_found_unlink(Path('dist'))
    path_wheel = session.poetry.build_package()
    logger.info('Created wheel', path_wheel=path_wheel)
    # Install the wheel and check that imports without any of the optional dependencies
    session.install(path_wheel)
    session.run(*shlex.split('python scripts/check_imports.py'), stdout=True)


@nox_session(python=_get_pythons()[-1:], reuse_venv=True)
def build_check(session: Session) -> None:
    """Check that the built output meets all checks.

    Args:
        session: nox_poetry Session

    """
    # Build sdist and fix return URI, which will have file://...#egg=calcipy
    sdist_uri = session.poetry.build_package(distribution_format=DistributionFormat.SDIST)
    path_sdist = Path(url2pathname(urlparse(sdist_uri).path))
    logger.debug('Fixed sdist URI', sdist_uri=sdist_uri, path_sdist=path_sdist)
    # Check with pyroma
    session.install('pyroma>=4.0', '--upgrade')
    # required for "poetry.core.masonry.api" build backend
    session.run('python', '-m', 'pip', 'install', 'poetry>=1.3', stdout=True)
    session.run('pyroma', '--file', path_sdist.as_posix(), '--min=9', stdout=True)
