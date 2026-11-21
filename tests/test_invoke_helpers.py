from pathlib import Path

import pytest
from invoke.runners import Result

from calcipy.collection import GlobalTaskOptions
from calcipy.invoke_helpers import get_doc_subdir, run, use_pty


@pytest.mark.parametrize(
    ('in_repo', 'copier', 'expected'),
    [
        (True, {}, 'docs/docs'),
        (False, {}, 'docs/docs'),
        (True, {'.': 'documentation'}, 'documentation/docs'),
        (False, {'subdir': 'documentation'}, 'documentation/docs'),
        (True, {'.': 'from_root', 'subdir': 'from_project'}, 'from_project/docs'),
        (True, {'subdir': 'no_doc_dir_key'}, 'docs/docs'),
    ],
)
def test_get_doc_subdir(tmp_path, in_repo, copier, expected):
    repo_dir = tmp_path / 'repo'
    sub_dir = repo_dir / 'subdir'
    sub_dir.mkdir(parents=True)
    if in_repo:
        (repo_dir / '.git').mkdir()
    for rel_dir, doc_dir in copier.items():
        content = 'other: 1' if doc_dir == 'no_doc_dir_key' else f'doc_dir: {doc_dir}'
        (repo_dir / rel_dir / '.copier-answers.yml').write_text(content)

    assert get_doc_subdir(sub_dir) == sub_dir / expected


def test_get_doc_subdir_defaults_to_project_path(tmp_project):
    (tmp_project / '.copier-answers.yml').write_text('doc_dir: site_docs')

    assert get_doc_subdir() == tmp_project / 'site_docs' / 'docs'


@pytest.mark.parametrize('working_dir', [None, Path('/some/dir')])
def test_run_uses_working_dir(ctx, working_dir):
    if working_dir:
        ctx.config.gto = GlobalTaskOptions(working_dir=working_dir)
    seen = []
    expected = Result(command='echo hi')

    def _record(command, **kwargs):
        seen.append((command, kwargs, ctx.cwd))
        return expected

    ctx.run.side_effect = _record

    result = run(ctx, 'echo hi', warn=True)

    assert seen == [('echo hi', {'warn': True}, str(working_dir or '.'))]
    assert result is expected
    assert not ctx.cwd


@pytest.mark.parametrize(('github_action', 'expected'), [('run1', False), (None, True)])
def test_use_pty(monkeypatch, github_action, expected):
    if github_action:
        monkeypatch.setenv('GITHUB_ACTION', github_action)
    else:
        monkeypatch.delenv('GITHUB_ACTION', raising=False)
    use_pty.cache_clear()
    try:
        assert use_pty() is expected
    finally:
        use_pty.cache_clear()
