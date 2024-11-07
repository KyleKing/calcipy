from unittest.mock import call

import pytest

from calcipy import can_skip
from calcipy.tasks.pack import install_extras, lock, publish


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (install_extras, {}, [call('uv sync --all-extras')]),
        (lock, {}, [call('uv lock')]),
        (publish, {}, ['uv build', 'uv publish']),
    ],
)
def test_pack(ctx, task, kwargs, commands, monkeypatch):
    monkeypatch.setattr(can_skip, 'can_skip', can_skip.dont_skip)
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([call(cmd) if isinstance(cmd, str) else cmd for cmd in commands])
