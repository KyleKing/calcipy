from pathlib import Path
from unittest.mock import call

import pytest
from beartype import beartype
from beartype.typing import Callable, Dict, List

from calcipy.tasks.tags import collect_code_tags
from tests.configuration import APP_DIR, TEST_DATA_DIR


@beartype
def _merge_path_kwargs(kwargs: Dict) -> Path:
    return Path(f"{kwargs['doc_sub_dir']}/{kwargs['filename']}")


@beartype
def _check_no_write(kwargs: Dict) -> None:
    assert not _merge_path_kwargs(kwargs).is_file()


@beartype
def _check_output(kwargs: Dict) -> None:
    path_tag_summary = _merge_path_kwargs(kwargs)
    assert path_tag_summary.is_file()
    content = path_tag_summary.read_text()
    path_tag_summary.unlink()
    assert '# Collected Code Tags' in content


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands', 'validator'),
    [
        (collect_code_tags, {
            'base_dir': APP_DIR.as_posix(),
            'doc_sub_dir': TEST_DATA_DIR.as_posix(),
            'filename': 'test_tags.md.rej',
            'tag_order': 'FIXME,TODO',
            'regex': '',
            'ignore_patterns': '*.py,*.yaml,docs/docs/*.md',
        }, [], _check_no_write),
        (collect_code_tags, {
            'base_dir': APP_DIR.as_posix(),
            'doc_sub_dir': TEST_DATA_DIR.as_posix(),
            'filename': 'test_tags.md.rej',
        }, [], _check_output),
    ],
    ids=[
        'Check that no code tags were matched and no file was created',
        'Check that no code tags were matched and no file was created',
    ],
)
@beartype
def test_tags(ctx, task, kwargs: Dict, commands: List[str], validator: Callable[[Dict], None]):
    task(ctx, **kwargs)

    ctx.run.assert_has_calls([
        call(cmd) if isinstance(cmd, str) else cmd
        for cmd in commands
    ])

    validator(kwargs)
