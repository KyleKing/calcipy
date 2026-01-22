from unittest.mock import call

import pytest

from calcipy.tasks.executable_utils import python_m
from calcipy.tasks.lint import ALL_PRE_COMMIT_HOOK_STAGES, check, fix, pre_commit, watch


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (check, {}, [f'{python_m()} ruff check "./src/calcipy" ./tests']),
        (fix, {}, [f'{python_m()} ruff check "./src/calcipy" ./tests --fix']),
        (watch, {}, [f'{python_m()} ruff check "./src/calcipy" ./tests --watch']),
        (
            pre_commit,
            {},
            [
                call('which prek', warn=True, hide=True),
                'prek install',
                'prek autoupdate',
                'prek run --all-files ' + ' '.join(f'--hook-stage {stg}' for stg in ALL_PRE_COMMIT_HOOK_STAGES),
            ],
        ),
    ],
)
def test_lint(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([call(cmd) if isinstance(cmd, str) else cmd for cmd in commands])
