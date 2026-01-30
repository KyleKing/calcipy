import pytest

from calcipy.tasks.doc import build, deploy, get_out_dir
from calcipy.tasks.executable_utils import python_m


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (build, {}, [f'{python_m()} mkdocs build --site-dir {get_out_dir()}']),
        (deploy, {}, [f'{python_m()} mkdocs gh-deploy --force']),
    ],
)
def test_doc(ctx, task, kwargs, commands, assert_run_commands):
    task(ctx, **kwargs)

    assert_run_commands(ctx, commands)
