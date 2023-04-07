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
            'poetry run bandit --recursive calcipy -s B101',
            'poetry run semgrep ci --autofix ' + ' '.join([
                '--config=p/ci',
                '--config=p/default',
                '--config=p/security-audit',
                '--config=r/bash',
                '--config=r/contrib',
                '--config=r/fingerprints',
                '--config=r/generic',
                '--config=r/json',
                '--config=r/python',
                '--config=r/terraform',
                '--config=r/yaml',
            ]),
        ]),
        (pre_commit, {}, [
            'pre-commit install',
            'pre-commit autoupdate',
            'pre-commit run --all-files ' + ' '.join(f'--hook-stage {stg}' for stg in [
                'commit', 'merge-commit', 'push', 'prepare-commit-msg', 'commit-msg', 'post-checkout',
                'post-commit', 'post-merge', 'post-rewrite', 'manual',
            ]),
        ]),
    ],
)
def test_lint(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
