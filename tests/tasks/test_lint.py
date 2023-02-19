from unittest.mock import call

import pytest

from calcipy.invoke_helpers import use_pty
from calcipy.tasks.lint import absolufy_imports, autopep8, check, fix, flake8, pre_commit, pylint, security, watch


# check(ctx: Context, *, target: Optional[str] = None) -> None:
# absolufy_imports(ctx: Context) -> None:
# autopep8(ctx: Context) -> None:
# fix(ctx: Context, *, target: Optional[str] = None) -> None:
# watch(ctx: Context, *, target: Optional[str] = None) -> None:
# flake8(ctx: Context, *, target: Optional[str] = None) -> None:
# pylint(ctx: Context, *, report: bool = False, target: Optional[str] = None) -> None:
# security(ctx: Context) -> None:
# pre_commit(ctx: Context, *, no_update: bool = False) -> None:


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (check, {}, ['poetry run python -m ruff check ./calcipy ./tests']),
        (absolufy_imports, {'target': './calcipy/__init__.md'},
         ['poetry run absolufy-imports ./calcipy/__init__.md --never']),
        (autopep8, {}, [
            'poetry run python -m autopep8 ./calcipy ./tests --aggressive --recursive --in-place --max-line-length=120',
        ]),
        (fix, {}, ['poetry run python -m ruff check ./calcipy ./tests --fix']),
        (watch, {}, ['poetry run python -m ruff check ./calcipy ./tests --watch --show-source']),
        (flake8, {}, ['poetry run python -m flake8 ./calcipy ./tests']),
        (pylint, {}, ['poetry run python -m pylint ./calcipy ./tests']),
        (security, {}, [
            'poetry run bandit --recursive calcipy',
            'poetry run semgrep ci --autofix --config=p/ci --config=p/security-audit --config=r/python.airflow --config=r/python.attr --config=r/python.click --config=r/python.cryptography --config=r/python.distributed --config=r/python.docker --config=r/python.flask --config=r/python.jinja2 --config=r/python.jwt --config=r/python.lang --config=r/python.pycryptodome --config=r/python.requests --config=r/python.security --config=r/python.sh --config=r/python.sqlalchemy ',  # noqa: E501
        ]),
        (pre_commit, {}, [
            'pre-commit install',
            'pre-commit autoupdate',
            'pre-commit run --all-files --hook-stage commit --hook-stage push',
        ]),
    ],
)
def test_types(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd, echo=True, pty=use_pty()) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
