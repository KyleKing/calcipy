from unittest.mock import call

import pytest

from calcipy import can_skip
from calcipy.tasks.pack import lock, publish

PUBLISH_ENV = {'UV_PUBLISH_USERNAME': 'pypi_user', 'UV_PUBLISH_PASSWORD': 'pypi_password'}
"""Set in `tests/__init__.py`."""


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (lock, {}, [call('uv lock')]),
        (publish, {}, ['uv build --no-sources', call('uv publish', env=PUBLISH_ENV)]),
    ],
)
def test_pack(ctx, task, kwargs, commands, monkeypatch):
    monkeypatch.setattr(can_skip, 'can_skip', can_skip.dont_skip)
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([call(cmd) if isinstance(cmd, str) else cmd for cmd in commands])
