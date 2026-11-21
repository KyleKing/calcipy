import pytest

from calcipy.tasks.all_tasks import release
from calcipy.tasks.cl import bump, write
from calcipy.tasks.executable_utils import python_m

_BUMP_FLAGS = '--annotated-tag --no-verify --gpg-sign'


@pytest.mark.parametrize(
    ('task', 'kwargs', 'command'),
    [
        (bump, {}, f'{python_m()} commitizen bump {_BUMP_FLAGS}'),
        (bump, {'suffix': 'rc'}, f'{python_m()} commitizen bump --prerelease=rc {_BUMP_FLAGS}'),
        (release, {}, f'{python_m()} commitizen bump {_BUMP_FLAGS}'),
        (release, {'suffix': 'beta'}, f'{python_m()} commitizen bump --prerelease=beta {_BUMP_FLAGS}'),
    ],
)
def test_bump(ctx, task, kwargs, command):
    task(ctx, **kwargs)

    ctx.run.assert_called_once_with(command)


@pytest.mark.parametrize('has_changelog', [True, False])
def test_write_moves_changelog_into_doc_dir(ctx, tmp_project, has_changelog):
    (tmp_project / '.copier-answers.yml').write_text('doc_dir: documentation')
    doc_dir = tmp_project / 'documentation' / 'docs'
    doc_dir.mkdir(parents=True)
    changelog = tmp_project / 'CHANGELOG.md'
    if has_changelog:
        changelog.write_text('# Changelog')
        write(ctx)
        assert (doc_dir / 'CHANGELOG.md').read_text() == '# Changelog'
    else:
        with pytest.raises(FileNotFoundError, match=f'Could not locate the changelog at: {changelog}'):
            write(ctx)
        assert not (doc_dir / 'CHANGELOG.md').exists()

    assert not changelog.exists()
    ctx.run.assert_called_once_with(f'{python_m()} commitizen changelog')
