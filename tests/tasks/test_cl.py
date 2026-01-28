from unittest.mock import call

import pytest

from calcipy.tasks.cl import bump
from calcipy.tasks.executable_utils import python_m


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (
            bump,
            {},
            [
                f'{python_m()} commitizen bump --annotated-tag --no-verify --gpg-sign',
            ],
        ),
    ],
)
def test_cl(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([call(cmd) if isinstance(cmd, str) else cmd for cmd in commands])
