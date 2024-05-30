from unittest.mock import call

import pytest

from calcipy.tasks.executable_utils import python_dir, python_m
from calcipy.tasks.lint import autopep8, check, fix, pre_commit, pylint, security, watch


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (check, {}, [f'{python_m()} ruff check ./calcipy ./tests']),
        (autopep8, {}, [
            f'{python_m()} autopep8 ./calcipy ./tests --aggressive --recursive --in-place --max-line-length=120',
        ]),
        (fix, {}, [f'{python_m()} ruff check ./calcipy ./tests --fix']),
        (watch, {}, [f'{python_m()} ruff check ./calcipy ./tests --watch --show-source']),
        (pylint, {}, [f'{python_m()} pylint ./calcipy ./tests']),
        (security, {}, [
            f'{python_dir()}/bandit --recursive calcipy -s B101',
        ]),
        (pre_commit, {}, [
            call('which pre-commit', warn=True, hide=True),
            'pre-commit install',
            'pre-commit autoupdate',
            'pre-commit run --all-files ' + ' '.join(f'--hook-stage {stg}' for stg in (
                'commit', 'merge-commit', 'push', 'prepare-commit-msg', 'commit-msg', 'post-checkout',
                'post-commit', 'post-merge', 'post-rewrite', 'manual',
            )),
        ]),
    ],
)
def test_lint(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
