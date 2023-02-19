
import pytest

from calcipy.invoke_helpers import use_pty
from calcipy.tasks.types import mypy, pyright


@pytest.mark.parametrize(
    ('task', 'kwargs', 'command'),
    [
        (pyright, {}, 'poetry run pyright calcipy'),
        (mypy, {}, 'poetry run python -m mypy calcipy'),
    ],
    ids=[
        'Default pyright task',
        'mypy task',
    ],
)
def test_types(ctx, task, kwargs, command):
    task(ctx, **kwargs)
    ctx.run.assert_called_once_with(command, echo=True, pty=use_pty())
