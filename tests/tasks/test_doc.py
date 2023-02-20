from unittest.mock import call

import pytest

from calcipy.tasks.doc import deploy


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (deploy, {}, ['poetry run mkdocs gh-deploy']),
    ],
)
def test_doc(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])
