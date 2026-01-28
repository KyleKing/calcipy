from unittest.mock import call

import pytest

from calcipy.tasks.all_tasks import main, other


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (main, {}, []),
        (other, {}, []),
    ],
)
def test_all_tasks(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([call(cmd) if isinstance(cmd, str) else cmd for cmd in commands])
