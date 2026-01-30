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
def test_types(ctx, task, kwargs, commands, assert_run_commands):
    task(ctx, **kwargs)

    assert_run_commands(ctx, commands)
