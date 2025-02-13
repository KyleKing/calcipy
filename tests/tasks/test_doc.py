from unittest.mock import call

import pytest

from calcipy.tasks.doc import build, deploy, get_out_dir
from calcipy.tasks.executable_utils import python_dir


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (build, {}, [f'{python_dir() / "mkdocs"} build --site-dir {get_out_dir()}']),
        (deploy, {}, [f'{python_dir() / "mkdocs"} gh-deploy --force']),
    ],
)
def test_doc(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
