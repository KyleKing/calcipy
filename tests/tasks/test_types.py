import pytest
from calcipy.tasks.types import pyright, mypy
from unittest.mock import call

@pytest.mark.parametrize(
    'task,kwargs,command',
    [
        (pyright, {}, f'pyright calcipy'),
        (mypy, {}, f'poetry run python -m mypy calcipy --html-report=releases/tests/mypy_html'),
    ],
    ids=[
        'Default pyright task',
        'mypy task',
    ],
)
def test_types(ctx, task, kwargs, command):
    task(ctx, **kwargs)
    ctx.run.assert_called_once_with(command, echo=True, pty=True)
