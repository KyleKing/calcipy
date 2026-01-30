import pytest

from calcipy.tasks.all_tasks import main, other


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (main, {}, []),
        (other, {}, []),
    ],
)
def test_all_tasks(ctx, task, kwargs, commands, assert_run_commands):
    task(ctx, **kwargs)

    assert_run_commands(ctx, commands)
