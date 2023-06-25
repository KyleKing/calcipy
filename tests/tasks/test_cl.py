from unittest.mock import call

import pytest

from calcipy.tasks.cl import bump
from calcipy.tasks.executable_utils import python_dir


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (bump, {}, [
            f'{python_dir()}/cz bump --annotated-tag --no-verify --gpg-sign',
            'git push origin --tags --no-verify',
            'gh release create --generate-notes $(git tag --list --sort=-creatordate | head -n 1)',
        ]),
    ],
)
def test_cl(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
