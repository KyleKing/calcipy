from unittest.mock import call

import pytest

from calcipy.tasks.executable_utils import python_dir
from calcipy.tasks.nox import noxfile


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (noxfile, {}, [f'{python_dir() / "nox"} --error-on-missing-interpreters ']),
    ],
)
def test_nox(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([call(cmd) if isinstance(cmd, str) else cmd for cmd in commands])
