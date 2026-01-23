from unittest.mock import call

import pytest

from calcipy.tasks.all_tasks import main, other, release
from calcipy.tasks.executable_utils import python_m


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (main, {}, []),
        (other, {}, []),
        (
            release,
            {},
            [
                f'{python_m()} cz bump --annotated-tag --no-verify --gpg-sign',
                'git push origin --tags --no-verify',
                'gh release create --generate-notes $(git tag --list --sort=-creatordate | head -n 1)',
            ],
        ),
    ],
)
def test_all_tasks(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([call(cmd) if isinstance(cmd, str) else cmd for cmd in commands])
