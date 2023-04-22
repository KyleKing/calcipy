from unittest.mock import call

import pytest

from calcipy.tasks.doc import build, deploy, get_out_dir


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (build, {}, [f'poetry run mkdocs build --site-dir {get_out_dir()}']),
        (deploy, {}, ['poetry run mkdocs gh-deploy --force']),
    ],
)
def test_doc(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
