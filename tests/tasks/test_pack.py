from unittest.mock import call

import pytest

from calcipy import can_skip
from calcipy.tasks.executable_utils import python_dir
from calcipy.tasks.pack import check_licenses, install_extras, lock, publish


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (install_extras, {}, [call(
            'poetry install --sync --extras=ddict --extras=doc --extras=experimental --extras=lint'
            ' --extras=nox --extras=tags --extras=test --extras=types',
        )]),
        (lock, {}, [call('poetry lock --no-update')]),
        (publish, {}, [
            f'{python_dir()}/nox --error-on-missing-interpreters --session build_dist build_check',
            'poetry publish',
        ]),
        (check_licenses, {}, ['licensecheck']),
    ],
)
def test_pack(ctx, task, kwargs, commands, monkeypatch):
    monkeypatch.setattr(can_skip, 'can_skip', can_skip.dont_skip)
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
