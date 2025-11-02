from unittest.mock import call, patch

import pytest

from calcipy import can_skip
from calcipy.tasks.pack import bump_tag, lock, publish, sync_pyproject_versions

PUBLISH_ENV = {'UV_PUBLISH_USERNAME': 'pypi_user', 'UV_PUBLISH_PASSWORD': 'pypi_password'}
"""Set in `tests/__init__.py`."""


@pytest.mark.parametrize(
    ('task', 'kwargs', 'commands'),
    [
        (lock, {}, [call('uv lock')]),
        (publish, {}, ['uv build --no-sources', call('uv publish', env=PUBLISH_ENV)]),
    ],
)
def test_pack(ctx, task, kwargs, commands, monkeypatch):
    monkeypatch.setattr(can_skip, 'can_skip', can_skip.dont_skip)
    with patch('calcipy.tasks.pack.keyring'):
        task(ctx, **kwargs)

    ctx.run.assert_has_calls([call(cmd) if isinstance(cmd, str) else cmd for cmd in commands])


def test_bump_tag(ctx, monkeypatch):
    """Test bump_tag function."""
    mock_pyproject = {'project': {'name': 'test-package'}}
    mock_bump = patch('calcipy.experiments.bump_programmatically.bump_tag', return_value='1.2.3')
    mock_read_pyproject = patch('calcipy.tasks.pack.file_helpers.read_pyproject', return_value=mock_pyproject)

    with mock_read_pyproject, mock_bump as bump_mock:
        bump_tag(ctx, tag='v1.2.2', tag_prefix='v')

    bump_mock.assert_called_once_with(pkg_name='test-package', tag='v1.2.2', tag_prefix='v')


def test_sync_pyproject_versions(ctx):
    """Test sync_pyproject_versions function."""
    mock_replace = patch('calcipy.experiments.sync_package_dependencies.replace_versions')
    mock_get_lock = patch('calcipy.tasks.pack.get_lock', return_value='path/to/lock')

    with mock_replace as replace_mock, mock_get_lock as get_lock_mock:
        sync_pyproject_versions(ctx)

    get_lock_mock.assert_called_once()
    replace_mock.assert_called_once_with(path_lock='path/to/lock')
