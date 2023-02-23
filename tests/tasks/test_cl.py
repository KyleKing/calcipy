from unittest.mock import call

import pytest

from calcipy.tasks.cl import bump


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (bump, {}, [
            'poetry run cz bump --annotated-tag --no-verify --gpg-sign',
            'git push origin --tags --no-verify',
            'which gh >> /dev/null && gh release create --generate-notes $(git tag --list --sort=-creatordate | head -n 1)',  # noqa: E501
        ]),
    ],
)
def test_cl(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
