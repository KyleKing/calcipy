import pytest

from calcipy.tasks.executable_utils import python_m
from calcipy.tasks.nox import noxfile


@pytest.mark.parametrize(
    ('kwargs', 'command'),
    [
        ({}, f'{python_m()} nox --error-on-missing-interpreters '),
        ({'session': 'tests'}, f'{python_m()} nox --error-on-missing-interpreters --session tests'),
    ],
)
def test_nox(ctx, kwargs, command):
    noxfile(ctx, **kwargs)

    ctx.run.assert_called_once_with(command)
