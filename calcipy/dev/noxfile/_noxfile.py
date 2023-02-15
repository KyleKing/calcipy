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

import re
import shlex
from contextlib import suppress
from pathlib import Path
from functools import lru_cache
from urllib.parse import urlparse
from urllib.request import url2pathname

from beartype import beartype
from beartype.typing import Callable, Dict, Iterable, List

# from ..._fixme_.doit_tasks.doit_globals import DoitTask, get_dg
# from ..._fixme_.doit_tasks.test import task_coverage, task_test
from ...file_helpers import if_found_unlink  # FIXME: Move to grouper (name tbd)

from nox_poetry import session as nox_session
from nox_poetry.poetry import DistributionFormat
from nox_poetry.sessions import Session

from shoal import get_logger

logger = get_logger()

_DEV_KEY = '_dev'
"""Key for list of development dependencies."""

_PINS: Dict[str, List[str]] = {_DEV_KEY: []}
"""Hackish global to track dev-dependencies that are user-specified."""


@lru_cache(maxsize=1)
@beartype
def get_pythons() -> List[str]:
    # FIXME: Replace with read_tool_versions...
    return ['3.10.5']

@beartype
def pin_dev_dependencies(pins: List[str]) -> None:
    """Manually specify dependencies for development.

    TODO: Make this auto-resolve based on pyproject.toml

    Args:
        pins: list of dependencies (i.e. `['Cerberus=>1.3.4', 'freezegun']`)

    """
    _PINS[_DEV_KEY] = pins



# @beartype
# def _run_str_cmd(session: Session, cmd_str: str) -> None:
#     """Run a command string. Ensure that poetry is left-stripped.

#     Args:
#         session: nox_poetry Session
#         cmd_str: string command to run

#     """
#     cmd_str = re.sub(r'^poetry run ', '', cmd_str)
#     session.run(*shlex.split(cmd_str), stdout=True)

# @beartype
# def _install_calcipy_extras(session: Session, extras: List[str]) -> None:
#     """Ensure calcipy extras are installed.

#     Args:
#         session: nox_poetry Session
#         extras: list of extras to install

#     """
#     if get_dg().meta.pkg_name == 'calcipy':
#         session.poetry.installroot(extras=extras)
#     else:  # pragma: no cover
#         session.install('.', f'calcipy[{",".join(extras)}]')

# @beartype
# def _install_pinned(session: Session, key: str) -> None:
#     """Ensure user-pinned dependencies are installed.

#     See [Issue #230](https://github.com/cjolowicz/nox-poetry/issues/230)

#     Args:
#         session: nox_poetry Session

#     """
#     for pin in _PINS.get(key, []):
#         session.install(pin)

# @beartype
# def _run_func_cmd(action: Iterable) -> None:  # type: ignore[type-arg]
#     """Run a python action.

#     Args:
#         action: doit python action

#     Raises:
#         RuntimeError: if a function action fails

#     """
#     # https://pydoit.org/tasks.html#python-action
#     func, args, kwargs = [*list(action), {}][:3]
#     result = func(args, **kwargs)
#     if result not in [True, None] or not isinstance(result, (str, dict)):
#         raise RuntimeError(f'Returned {result}. Failed to run task: {action}')

# @beartype
# def _run_doit_task(session: Session, task_fun: Callable[[], DoitTask]) -> None:
#     """Run a DoitTask actions without using doit.

#     Args:
#         session: nox_poetry Session
#         task_fun: function that returns a DoitTask

#     Raises:
#         NotImplementedError: if the action is of an unknown type

#     """
#     task = task_fun()
#     for action in task['actions']:
#         if isinstance(action, str):
#             _run_str_cmd(session, action)
#         elif getattr(action, 'action', None):
#             _run_str_cmd(session, action.action)  # type: ignore[union-attr]
#         elif isinstance(action, (list, tuple)):
#             _run_func_cmd(action)
#         else:
#             raise NotImplementedError(f'Unable to run {action} ({type(action)})')

# @nox_session(python=get_pythons(), reuse_venv=True)
# def tests(session: Session) -> None:
#     """Run doit test task for specified python versions.

#     Args:
#         session: nox_poetry Session

#     """
#     _install_calcipy_extras(session, ['dev', 'test'])
#     _install_pinned(session, key=_DEV_KEY)
#     _run_doit_task(session, task_test)

# @nox_session(python=get_pythons()[-1:], reuse_venv=True)
# def coverage(session: Session) -> None:
#     """Run doit test task for specified python versions.

#     Args:
#         session: nox_poetry Session

#     """
#     _install_calcipy_extras(session, ['dev', 'test'])
#     _install_pinned(session, key=_DEV_KEY)
#     _run_doit_task(session, task_coverage)

# @nox_session(python=get_pythons()[-1:], reuse_venv=False)
# def build_dist(session: Session) -> None:
#     """Build the project files within a controlled environment for repeatability.

#     Args:
#         session: nox_poetry Session

#     """
#     if_found_unlink(get_dg().meta.path_project / 'dist')
#     path_wheel = session.poetry.build_package()
#     logger.info(f'Created wheel: {path_wheel}')
#     # Install the wheel and check that imports without any of the optional dependencies
#     session.install(path_wheel)
#     session.run(*shlex.split('python scripts/check_imports.py'), stdout=True)

@nox_session(python=get_pythons()[-1:], reuse_venv=True)
def build_check(session: Session) -> None:
    """Check that the built output meets all checks.

    Args:
        session: nox_poetry Session

    """
    # Build sdist and fix return URI, which will have file://...#egg=calcipy
    sdist_uri = session.poetry.build_package(distribution_format=DistributionFormat.SDIST)
    path_sdist = Path(url2pathname(urlparse(sdist_uri).path))
    logger.debug(f'Fixed sdist URI ({sdist_uri}): {path_sdist}')
    # Check with pyroma
    session.install('pyroma>=4.0', '--upgrade')
    # required for "poetry.core.masonry.api" build backend
    session.run('python', '-m', 'pip', 'install', 'poetry>=1.3', stdout=True)
    session.run('pyroma', '--file', path_sdist.as_posix(), '--min=9', stdout=True)