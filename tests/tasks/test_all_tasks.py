from unittest.mock import call

import pytest

from calcipy.invoke_helpers import use_pty
from calcipy.tasks.all_tasks import main, other, release


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (main, {}, []),
        (other, {}, []),
        (release, {}, [
            'poetry run cz bump --annotated-tag --no-verify --gpg-sign',
            'poetry lock --check',
            'git push origin --tags --no-verify',
            'which gh >> /dev/null && gh release create --generate-notes $(git tag --list --sort=-creatordate | head -n 1)',  # noqa: E501
        ]),
    ],
)
def test_all_tasks(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd, echo=True, pty=use_pty()) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
