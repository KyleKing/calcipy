"""nox-poetry configuration file.

[Useful snippets from docs](https://nox.thea.codes/en/stable/usage.html)

```sh
poetry run nox -l
poetry run nox --list-sessions

poetry run nox -s build_check-3.9 build_dist-3.9 check_safety-3.9
poetry run nox --session check_safety-3.9

poetry run nox --python 3.8

poetry run nox -k "not tests and not check_safety"
```

Useful nox snippets

```py
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
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import url2pathname

from loguru import logger

from ..doit_tasks.doit_globals import DG
from ..file_helpers import if_found_unlink

has_test_imports = False
try:
    from nox_poetry import session
    from nox_poetry.poetry import DistributionFormat
    from nox_poetry.sessions import Session
    has_test_imports = True
except ImportError:  # pragma: no cover
    pass

if has_test_imports:
    @session(python=[DG.test.pythons], reuse_venv=True)
    def tests(session: Session) -> None:
        """Run doit test task for specified python versions.

        Args:
            session: nox_poetry Session

        """
        session.install('.[dev]', '.[test]')
        session.run(*shlex.split('doit run test'), stdout=True)

    @session(python=[DG.test.pythons[-1]], reuse_venv=True)
    def coverage(session: Session) -> None:
        """Run doit test task for specified python versions.

        Args:
            session: nox_poetry Session

        """
        session.install('.[dev]', '.[test]')
        session.run(*shlex.split('doit run coverage'), stdout=True)

    @session(python=[DG.test.pythons[-1]], reuse_venv=False)
    def build_dist(session: Session) -> None:
        """Build the project files within a controlled environment for repeatability.

        Args:
            session: nox_poetry Session

        """
        if_found_unlink(DG.meta.path_project / 'dist')
        path_wheel = session.poetry.build_package()
        logger.info(f'Created wheel: {path_wheel}')
        # Install the wheel and check that imports without any of the optional dependencies
        session.install(path_wheel)
        session.run(*shlex.split('python scripts/check_imports.py'), stdout=True)

    @session(python=[DG.test.pythons[-1]], reuse_venv=True)
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
        session.install('pyroma', '--upgrade')
        # PLANNED: Troubleshoot why pyroma score is so low (6/10)
        session.run('pyroma', '--file', path_sdist.as_posix(), '--min=6', stdout=True)

    @session(python=[DG.test.pythons[-1]], reuse_venv=True)
    def check_safety(session: Session) -> None:
        """Check for known vulnerabilities with safety.

        Based on: https://github.com/pyupio/safety/issues/201#issuecomment-632627366

        Args:
            session: nox_poetry Session

        Raises:
            RuntimeError: if safety exited with errors, but not caught by session

        """
        # Note: safety requires a requirements.txt file and doesn't support pyproject.toml yet
        session.poetry.export_requirements()
        # Install and run
        session.install('safety', '--upgrade')
        path_report = Path('insecure_report.json').resolve()
        logger.info(f'Creating safety report: {path_report}')
        session.run(*shlex.split(f'safety check --full-report --cache --output {path_report} --json'), stdout=True)
        if path_report.read_text().strip() != '[]':
            raise RuntimeError(f'Found safety warnings in {path_report}')
        path_report.unlink()
