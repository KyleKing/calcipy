"""nox-poetry configuration file."""

import shlex

import nox
from loguru import logger
from nox_poetry import session
from nox_poetry.sessions import Session

from calcipy.doit_tasks.doit_globals import DG


def configure_nox() -> None:
    """Toggle nox settings. Default is to set `error_on_missing_interpreters` to True."""
    nox.options.reuse_existing_virtualenvs = True
    nox.options.error_on_missing_interpreters = True


@session(python=[DG.test.pythons], reuse_venv=True)
def tests(session: Session) -> None:
    """Run doit test task for specified python versions.

    Args:
        session: nox_poetry Session

    """
    session.install('.[dev]', '.[test]')
    session.run(*shlex.split('poetry run doit run test'))


@session(python=[DG.test.pythons[-1]], reuse_venv=False)
def build(session: Session) -> None:
    """Build the project files within a controlled environment for repeatability.

    Args:
        session: nox_poetry Session

    """
    path_wheel = session.poetry.build_package()
    logger.info(path_wheel)


# PLANNED: Make an environment to check the built wheel file for imports once most are optional:
#   https://stackoverflow.com/questions/34855071/importing-all-functions-from-a-package-from-import
# PLANNED: Add environment for safety, see https://github.com/KyleKing/calcipy/issues/32 for snippet
