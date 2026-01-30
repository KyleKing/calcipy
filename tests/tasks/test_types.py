from unittest.mock import call

import pytest

from calcipy.tasks.executable_utils import python_m
from calcipy.tasks.types import mypy, pyright, ty


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (
            pyright,
            {},
            [
                call('which pyright', warn=True, hide=True),
                'pyright',
            ],
        ),
        (mypy, {}, [f'{python_m()} mypy']),
        (ty, {}, ['ty check calcipy tests']),
    ],
)
def test_types(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([call(cmd) if isinstance(cmd, str) else cmd for cmd in commands])
