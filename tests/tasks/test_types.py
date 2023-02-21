from unittest.mock import call

import pytest

from calcipy.tasks.types import mypy, pyright


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (pyright, {}, ['poetry run pyright calcipy']),
        (mypy, {}, ['poetry run python -m mypy calcipy']),
    ],
)
def test_types(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
