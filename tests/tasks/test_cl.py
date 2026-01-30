from unittest.mock import patch

import pytest

from calcipy.tasks.cl import bump, write
from calcipy.tasks.executable_utils import python_m


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (
            bump,
            {},
            [
                f'{python_m()} commitizen bump --annotated-tag --no-verify --gpg-sign',
            ],
        ),
    ],
)
def test_cl(ctx, task, kwargs, commands, assert_run_commands):
    task(ctx, **kwargs)

    assert_run_commands(ctx, commands)


def test_write_moves_changelog(ctx, tmp_path):
    doc_dir = tmp_path / 'docs' / 'docs'
    doc_dir.mkdir(parents=True)
    changelog = tmp_path / 'CHANGELOG.md'
    changelog.write_text('# Changelog')

    with (
        patch('calcipy.tasks.cl.get_project_path', return_value=tmp_path),
        patch('calcipy.tasks.cl.get_doc_subdir', return_value=doc_dir),
    ):
        write(ctx)

    assert (doc_dir / 'CHANGELOG.md').is_file()
    assert not changelog.is_file()


def test_write_raises_when_changelog_missing(ctx, tmp_path):
    with (
        patch('calcipy.tasks.cl.get_project_path', return_value=tmp_path),
        pytest.raises(FileNotFoundError, match='Could not locate the changelog'),
    ):
        write(ctx)
