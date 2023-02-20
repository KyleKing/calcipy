from unittest.mock import call

import pytest
from shoal import can_skip

from calcipy.invoke_helpers import use_pty
from calcipy.tasks.pack import check_licenses, lock, publish


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (lock, {}, [call('poetry lock --no-update')]),
        (publish, {}, [
            'poetry run nox --error-on-missing-interpreters --session build_dist build_check',
            'poetry publish',
        ]),
        (check_licenses, {}, ['licensecheck']),
    ],
)
def test_pack(ctx, task, kwargs, commands, monkeypatch):
    monkeypatch.setattr(can_skip, 'can_skip', can_skip.dont_skip)
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd, echo=True, pty=use_pty()) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
