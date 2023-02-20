from unittest.mock import call

import pytest

from calcipy.invoke_helpers import use_pty
from calcipy.tasks.nox import noxfile


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (noxfile, {}, ['poetry run nox --error-on-missing-interpreters ']),
    ],
)
def test_nox(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd, echo=True, pty=use_pty()) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
