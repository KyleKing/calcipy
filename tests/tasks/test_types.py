from unittest.mock import call

import pytest

from calcipy.tasks.executable_utils import python_dir
from calcipy.tasks.types import basedpyright, mypy, pyright


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (pyright, {}, [
            call('which pyright', warn=True, hide=True),
            'pyright calcipy',
        ]),
        (mypy, {}, [f'{python_dir()}/mypy calcipy']),
        (basedpyright, {}, [f'{python_dir()}/basedpyright calcipy']),
    ],
)
def test_types(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
