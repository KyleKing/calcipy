import pytest

from calcipy.tasks.executable_utils import python_m
from calcipy.tasks.nox import noxfile


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (noxfile, {}, [f'{python_m()} nox --error-on-missing-interpreters ']),
    ],
)
def test_nox(ctx, task, kwargs, commands, assert_run_commands):
    task(ctx, **kwargs)

    assert_run_commands(ctx, commands)
