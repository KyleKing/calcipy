from unittest.mock import call

import pytest

from calcipy.tasks.lint import autopep8, check, fix, flake8, pre_commit, pylint, security, watch


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (check, {}, ['poetry run python -m ruff check ./calcipy ./tests']),
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
def test_lint(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
