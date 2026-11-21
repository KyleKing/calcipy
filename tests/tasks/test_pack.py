import os
from unittest.mock import Mock

import pytest

from calcipy.tasks.pack import bump_tag, lock, sync_pyproject_versions


@pytest.mark.parametrize(('lock_is_newer', 'commands'), [(False, ['uv lock']), (True, [])])
def test_lock_runs_only_when_pyproject_is_newer(ctx, tmp_project, assert_run_commands, lock_is_newer, commands):
    path_lock = tmp_project / 'uv.lock'
    path_lock.write_text('')
    older, newer = 1_000_000, 2_000_000
    os.utime(path_lock, (newer, newer) if lock_is_newer else (older, older))
    os.utime(tmp_project / 'pyproject.toml', (older, older) if lock_is_newer else (newer, newer))

    lock(ctx)

    assert_run_commands(ctx, commands)


@pytest.mark.parametrize(('pkg_name', 'expected_name'), [('', 'mypkg'), ('other', 'other')])
def test_bump_tag(ctx, tmp_project, monkeypatch, pkg_name, expected_name):
    bump = Mock(return_value='v1.2.3')
    logger = Mock()
    monkeypatch.setattr('calcipy.experiments.bump_programmatically.bump_tag', bump)
    monkeypatch.setattr('calcipy.tasks.pack.LOGGER', logger)

    bump_tag(ctx, tag='v1.2.2', tag_prefix='v', pkg_name=pkg_name)

    bump.assert_called_once_with(pkg_name=expected_name, tag='v1.2.2', tag_prefix='v')
    logger.text.assert_called_once_with('v1.2.3')
    ctx.run.assert_not_called()


def test_bump_tag_empty_tag(ctx):
    with pytest.raises(ValueError, match='tag must not be empty'):
        bump_tag(ctx, tag='')


def test_sync_pyproject_versions(ctx, tmp_project, monkeypatch):
    (tmp_project / 'uv.lock').write_text('')
    replace_versions = Mock()
    monkeypatch.setattr('corallium.sync_dependencies.replace_versions', replace_versions)

    sync_pyproject_versions(ctx)

    replace_versions.assert_called_once_with(path_lock=tmp_project / 'uv.lock')
    ctx.run.assert_not_called()
