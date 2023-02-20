from pathlib import Path
from unittest.mock import call

import pytest

from calcipy.invoke_helpers import use_pty
from calcipy.tasks.tags import collect_code_tags

from ..configuration import TEST_DATA_DIR

BASE_DIR = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (collect_code_tags, {
            'base_dir': BASE_DIR.as_posix(),
            'filename': (TEST_DATA_DIR / 'test_tags.md.rej').as_posix(),
            'tag_order': 'FIXME,TODO',
            'regex': '',
            'ignore_patterns': '*.py,*.yaml,docs/docs/*.md',
        }, []),
    ],
    ids=[
        'Check that no code tags were matched and no file was created',
    ],
)
def test_tags(ctx, task, kwargs, commands):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd, echo=True, pty=use_pty()) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])

    assert not Path(kwargs['filename']).is_file()
