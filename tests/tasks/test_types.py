from unittest.mock import call

import pytest

from calcipy.tasks.executable_utils import python_m
from calcipy.tasks.types import mypy, pyright, ty


@pytest.mark.parametrize(
    ('task', 'commands'),
    [
        (pyright, [call('which pyright', warn=True, hide=True), 'pyright']),
        (mypy, [f'{python_m()} mypy']),
        (ty, ['ty check mypkg tests']),
    ],
)
def test_types(ctx, tmp_project, task, commands, assert_run_commands):
    task(ctx)

    assert_run_commands(ctx, commands)
