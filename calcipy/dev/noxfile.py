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
from typing import Callable, Dict, List
from urllib.parse import urlparse
from urllib.request import url2pathname

from beartype import beartype
from loguru import logger

from ..doit_tasks.doit_globals import DG, DoitAction, DoitTask
from ..doit_tasks.test import task_coverage, task_test
from ..file_helpers import if_found_unlink

_HAS_TEST_IMPORTS = False
try:
    from nox_poetry import session as nox_session
    from nox_poetry.poetry import DistributionFormat
    from nox_poetry.sessions import Session
    _HAS_TEST_IMPORTS = True
except ImportError:  # pragma: no cover
    ...

_DEV_KEY = '_dev'
"""Key for list of development dependencies."""

_PINS: Dict[str, List[str]] = {_DEV_KEY: []}
"""Hackish global to track dev-dependencies that are user-specified."""


@beartype
def pin_dev_dependencies(pins: List[str]) -> None:
    """Manually specify dependencies for development.

    TODO: Make this auto-resolve based on pyproject.toml

    Args:
        pins: list of dependencies (i.e. `['Cerberus=>1.3.4', 'freezegun']`)

    """
    _PINS[_DEV_KEY] = pins


if _HAS_TEST_IMPORTS:  # pragma: no cover  # noqa: C901
    def _run_str_cmd(session: Session, cmd_str: str) -> None:
        """Run a command string. Ensure that poetry is left-stripped.

        Args:
            session: nox_poetry Session
            cmd_str: string command to run

        """
        cmd_str = re.sub(r'^poetry run ', '', cmd_str)
        session.run(*shlex.split(cmd_str), stdout=True)

    def _install_calcipy_extras(session: Session, extras: List[str]) -> None:
        """Ensure calcipy extras are installed.

        Args:
            session: nox_poetry Session
            extras: list of extras to install

        """
        if DG.meta.pkg_name == 'calcipy':
            session.poetry.installroot(extras=extras)
        else:  # pragma: no cover
            session.install('.', f'calcipy[{",".join(extras)}]')

    def _install_pinned(session: Session, key: str) -> None:
        """Ensure user-pinned dependencies are installed.

        See [Issue #230](https://github.com/cjolowicz/nox-poetry/issues/230)

        Args:
            session: nox_poetry Session

        """
        for pin in _PINS.get(key, []):
            session.install(pin)

    def _run_func_cmd(action: DoitAction) -> None:
        """Run a python action.

        Args:
            action: doit python action

        Raises:
            RuntimeError: if a function action fails

        """
        # https://pydoit.org/tasks.html#python-action
        func, args, kwargs = [*list(action), {}][:3]
        result = func(args, **kwargs)
        if result not in [True, None] or not isinstance(result, (str, dict)):
            raise RuntimeError(f'Returned {result}. Failed to run task: {action}')

    def _run_doit_task(session: Session, task_fun: Callable[[], DoitTask]) -> None:
        """Run a DoitTask actions without using doit.

        Args:
            session: nox_poetry Session
            task_fun: function that returns a DoitTask

        Raises:
            NotImplementedError: if the action is of an unknown type

        """
        task = task_fun()
        for action in task['actions']:
            if isinstance(action, str):
                _run_str_cmd(session, action)
            elif getattr(action, 'action', None):
                _run_str_cmd(session, action.action)
            elif isinstance(action, (list, tuple)):
                _run_func_cmd(action)
            else:
                raise NotImplementedError(f'Unable to run {action} ({type(action)})')

    @nox_session(python=DG.test.pythons, reuse_venv=True)
    def tests(session: Session) -> None:
        """Run doit test task for specified python versions.

        Args:
            session: nox_poetry Session

        """
        _install_calcipy_extras(session, ['dev', 'test'])
        _install_pinned(session, key=_DEV_KEY)
        _run_doit_task(session, task_test)

    @nox_session(python=DG.test.pythons[-1:], reuse_venv=True)
    def coverage(session: Session) -> None:
        """Run doit test task for specified python versions.

        Args:
            session: nox_poetry Session

        """
        _install_calcipy_extras(session, ['dev', 'test'])
        _install_pinned(session, key=_DEV_KEY)
        _run_doit_task(session, task_coverage)

    @nox_session(python=DG.test.pythons[-1:], reuse_venv=False)
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

    @nox_session(python=DG.test.pythons[-1:], reuse_venv=True)
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

    @nox_session(python=DG.test.pythons[-1:], reuse_venv=True)
    def check_safety(session: Session) -> None:
        """Check for known vulnerabilities with safety.

        Based on: https://github.com/pyupio/safety/issues/201#issuecomment-632627366

        Args:
            session: nox_poetry Session

        Raises:
            RuntimeError: if safety exited with errors, but not caught by session

        """
        session.install('safety', '--upgrade')
        path_report = Path('insecure_report.json').resolve()
        logger.info(f'Creating safety report: {path_report}')
        session.run(*shlex.split(f'safety check --full-report --cache --output {path_report} --json'), stdout=True)
        if path_report.read_text().strip() != '[]':
            raise RuntimeError(f'Found safety warnings in {path_report}')
        path_report.unlink()

    @nox_session(python=DG.test.pythons[-1:], reuse_venv=True)
    def check_security(session: Session) -> None:
        """More general checks for common security issues.

        Args:
            session: nox_poetry Session

        """
        session.install('semgrep', '--upgrade')  # Runs "safety" and other tools
        allow_py_rules = '--dangerously-allow-arbitrary-code-execution-from-rules'
        # TODO: Implement semgrep - what are a good ruleset to start with? Currently only a nox-session (no doit task)
        #   https://github.com/returntocorp/semgrep-rules/tree/develop/python
        #   https://awesomeopensource.com/project/returntocorp/semgrep-rules?categorypage=45
        configs = ' '.join([
            # See more at: https://semgrep.dev/explore
            '--config=p/ci',
            '--config=p/security-audit',
            '--config=r/python.airflow',
            '--config=r/python.attr',
            '--config=r/python.click',
            '--config=r/python.cryptography',
            '--config=r/python.distributed',
            '--config=r/python.docker',
            '--config=r/python.flask',
            '--config=r/python.jinja2',
            '--config=r/python.jwt',
            '--config=r/python.lang',
            '--config=r/python.pycryptodome',
            '--config=r/python.requests',
            '--config=r/python.security',
            '--config=r/python.sh',
            '--config=r/python.sqlalchemy',
            # dlukeomalley:unchecked-subprocess-call
            # dlukeomalley:use-assertEqual-for-equality
            # dlukeomalley:flask-set-cookie
            # clintgibler:no-exec
        ])
        session.run(*shlex.split(f'semgrep {DG.meta.pkg_name} {allow_py_rules} {configs}'), stdout=True)

    # TODO: https://github.com/tonybaloney/wily/blob/e72b7d95228bbe5538a072dc5d1186daa318bb03/src/wily/__main__.py#L261
    @nox_session(python=DG.test.pythons[-1:], reuse_venv=True)
    def check_wily(session: Session) -> None:
        """Run `wily` separately because of dependency constraints.

        Args:
            session: nox_poetry Session

        """
        session.install('wily', '--upgrade')
        logger.warning('FYI: Can only be run when all changes are checked in or stashed')
        # All possible metrics can be listed with: wily list-metrics
        # TODO: How are the additional metrics configured?
        # operators = ','.join([
        #     'raw.loc', 'raw.lloc', 'raw.sloc', 'maintainability.rank', 'maintainability.mi', 'cyclomatic.complexity',
        #     'halstead.h1', 'halstead.vocabulary', 'halstead.length', 'halstead.volume', 'halstead.difficulty', 'halstead.effort',
        # ])
        build_args = '--max-revisions 50'
        report_args = f'--output {DG.meta.path_project}/report.txt --message --number 50'
        with suppress(Exception):
            session.run(*shlex.split(f'wily build {DG.meta.pkg_name} {build_args}'), stdout=True)
            session.run(*shlex.split(f'wily report {DG.meta.pkg_name} {report_args}'), stdout=True)

            # FYI: Opens plotly graph in web browser and not necessary to run "wily" again
            # metric = 'raw.loc'  # 'cyclomatic.complexity' 'maintainability.mi' 'halstead.h1'
            # session.run(*shlex.split(f'wily graph {DG.meta.pkg_name} {metric}'), stdout=True)

        # TODO: Could use file archiver instead of git when the above fails?
