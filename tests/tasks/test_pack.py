from pathlib import Path
from unittest.mock import call, patch

import pytest

from calcipy.tasks.pack import bump_tag, lock, sync_pyproject_versions


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (lock, {}, [call('uv lock')]),
    ],
)
def test_pack(ctx, task, kwargs, commands, monkeypatch, assert_run_commands):
    mock_can_skip = patch('calcipy.tasks.pack.can_skip.can_skip', return_value=False)
    mock_get_lock = patch('calcipy.tasks.pack.get_lock', return_value=Path('uv.lock'))

    with mock_can_skip, mock_get_lock:
        task(ctx, **kwargs)

    assert_run_commands(ctx, commands)


def test_bump_tag(ctx, monkeypatch):
    """Test bump_tag function."""
    mock_pyproject = {'project': {'name': 'test-package'}}
    mock_bump = patch('calcipy.experiments.bump_programmatically.bump_tag', return_value='1.2.3')
    mock_read_pyproject = patch('calcipy.tasks.pack.file_helpers.read_pyproject', return_value=mock_pyproject)

    with mock_read_pyproject, mock_bump as bump_mock:
        bump_tag(ctx, tag='v1.2.2', tag_prefix='v')

    bump_mock.assert_called_once_with(pkg_name='test-package', tag='v1.2.2', tag_prefix='v')


def test_lock_skips_when_can_skip(ctx):
    mock_can_skip = patch('calcipy.tasks.pack.can_skip.can_skip', return_value=True)
    mock_get_lock = patch('calcipy.tasks.pack.get_lock', return_value=Path('uv.lock'))

    with mock_can_skip, mock_get_lock:
        lock(ctx)

    ctx.run.assert_not_called()


def test_bump_tag_empty_tag(ctx):
    with pytest.raises(ValueError, match='tag must not be empty'):
        bump_tag(ctx, tag='')


def test_sync_pyproject_versions(ctx):
    """Test sync_pyproject_versions function."""
    mock_replace = patch('corallium.sync_dependencies.replace_versions')
    mock_get_lock = patch('calcipy.tasks.pack.get_lock', return_value=Path('uv.lock'))

    with mock_replace as replace_mock, mock_get_lock as get_lock_mock:
        sync_pyproject_versions(ctx)

    get_lock_mock.assert_called_once()
    replace_mock.assert_called_once_with(path_lock=Path('uv.lock'))
