import re
import shutil
from contextlib import suppress
from pathlib import Path
from subprocess import CalledProcessError  # noqa: S404

import pytest
from beartype.typing import Dict, List, Optional, Tuple
from corallium.shell import capture_shell

from calcipy.tasks.tags import collect_code_tags

_FILES = {
    'root.py': '# TODO: root task\n',
    'subdir/sub.py': 'x = 1  # FIXME: sub task\n# TODO: second sub task\n',
}
_ROOT_ROW = ('TODO', 'root task', 'root.py:1')
_SUB_ROWS = [('FIXME', 'sub task', 'subdir/sub.py:1'), ('TODO', 'second sub task', 'subdir/sub.py:2')]
_SUB_ROWS_LOCAL = [(typ, comment, src.removeprefix('subdir/')) for typ, comment, src in _SUB_ROWS]


def _init_vcs(repo_dir: Path, vcs: Optional[str]) -> None:
    if vcs == 'git':
        for cmd in ('git init', 'git config user.email "test@test.com"', 'git config user.name "Test"'):
            capture_shell(cmd, cwd=repo_dir)
        capture_shell('git add .', cwd=repo_dir)
        capture_shell('git commit -m "initial"', cwd=repo_dir)
    elif vcs == 'jj':
        capture_shell('jj git init --no-colocate', cwd=repo_dir)
        with suppress(CalledProcessError):
            capture_shell('jj new', cwd=repo_dir)
    elif vcs == 'jj-marker':
        (repo_dir / '.jj').mkdir()


def _read_summary(path: Path) -> Tuple[List[Tuple[str, ...]], List[str]]:
    lines = path.read_text(encoding='utf-8').splitlines()
    assert lines[:2] == ['# Collected Code Tags', '']
    cells = [tuple(cell.strip() for cell in line.strip('|').split('|')) for line in lines if line.startswith('| ')]
    assert cells[0] == ('Type', 'Comment', 'Last Edit', 'Source File')
    rows = cells[1:]
    return [(typ, comment, src) for typ, comment, _, src in rows], [last_edit for _, _, last_edit, _ in rows]


_DOCS = {'.': 'docs'}
_skip_no_jj = pytest.mark.skipif(not shutil.which('jj'), reason='jj not available')


@pytest.mark.parametrize(
    ('vcs', 'copier', 'cwd', 'kwargs', 'config', 'output', 'rows'),
    [
        pytest.param(
            'git', _DOCS, 'subdir', {}, {}, 'docs/docs/CODE_TAG_SUMMARY.md', [_ROOT_ROW, *_SUB_ROWS], id='git-subdir'
        ),
        pytest.param(
            'jj',
            _DOCS,
            'subdir',
            {},
            {},
            'docs/docs/CODE_TAG_SUMMARY.md',
            [_ROOT_ROW, *_SUB_ROWS],
            id='jj-subdir',
            marks=_skip_no_jj,
        ),
        pytest.param(
            'jj-marker',
            _DOCS,
            'subdir',
            {},
            {},
            'docs/docs/CODE_TAG_SUMMARY.md',
            [_ROOT_ROW, *_SUB_ROWS],
            id='jj-marker-subdir',
        ),
        pytest.param(
            'git',
            {'subdir': 'documentation'},
            'subdir',
            {'ignore_repo_root': True},
            {},
            'subdir/documentation/docs/CODE_TAG_SUMMARY.md',
            _SUB_ROWS_LOCAL,
            id='ignore-repo-root-copier-in-subdir',
        ),
        pytest.param(
            'git',
            {'.': 'documentation'},
            'subdir',
            {'ignore_repo_root': True},
            {},
            'subdir/documentation/docs/CODE_TAG_SUMMARY.md',
            _SUB_ROWS_LOCAL,
            id='ignore-repo-root-copier-at-root',
        ),
        pytest.param(None, {}, '.', {}, {}, 'docs/docs/CODE_TAG_SUMMARY.md', [_ROOT_ROW, *_SUB_ROWS], id='no-repo'),
        pytest.param(
            None,
            _DOCS,
            '.',
            {'ignore_patterns': 'subdir/*'},
            {},
            'docs/docs/CODE_TAG_SUMMARY.md',
            [_ROOT_ROW],
            id='ignore-patterns',
        ),
        pytest.param(
            None,
            _DOCS,
            '.',
            {},
            {'ignore_patterns': 'root.py'},
            'docs/docs/CODE_TAG_SUMMARY.md',
            _SUB_ROWS,
            id='ignore-patterns-from-config',
        ),
        pytest.param(
            'git', _DOCS, '.', {'ignore_patterns': '*.py'}, {}, 'docs/docs/CODE_TAG_SUMMARY.md', [], id='no-matches'
        ),
        pytest.param(
            'git',
            _DOCS,
            '.',
            {'tag_order': 'FIXME'},
            {},
            'docs/docs/CODE_TAG_SUMMARY.md',
            [_SUB_ROWS[0]],
            id='tag-order',
        ),
        pytest.param(
            'git',
            _DOCS,
            '.',
            {'regex': r'# (?P<tag>{tag}): (?P<text>root.+)', 'tag_order': 'TODO'},
            {},
            'docs/docs/CODE_TAG_SUMMARY.md',
            [_ROOT_ROW],
            id='custom-regex',
        ),
        pytest.param(
            'git',
            _DOCS,
            'subdir',
            {'doc_sub_dir': 'out', 'filename': 'TAGS.md'},
            {},
            'out/TAGS.md',
            [_ROOT_ROW, *_SUB_ROWS],
            id='explicit-output',
        ),
        pytest.param(
            'git',
            _DOCS,
            '.',
            {},
            {'filename': 'FROM_CONFIG.md'},
            'docs/docs/FROM_CONFIG.md',
            [_ROOT_ROW, *_SUB_ROWS],
            id='filename-from-config',
        ),
    ],
)
def test_collect_code_tags(
    ctx,
    tmp_path,
    monkeypatch,
    vcs: Optional[str],
    copier: Dict[str, str],
    cwd: str,
    kwargs: Dict,  # type: ignore[type-arg]
    config: Dict,  # type: ignore[type-arg]
    output: str,
    rows: List[Tuple[str, ...]],
):
    repo_dir = tmp_path / 'repo'
    for rel_path, content in _FILES.items():
        (repo_dir / rel_path).parent.mkdir(parents=True, exist_ok=True)
        (repo_dir / rel_path).write_text(content)
    for rel_dir, doc_dir in copier.items():
        (repo_dir / rel_dir / '.copier-answers.yml').write_text(f'doc_dir: {doc_dir}')
    _init_vcs(repo_dir, vcs)
    path_output = repo_dir / output
    path_output.parent.mkdir(parents=True, exist_ok=True)
    if config:
        ctx.config['tags'] = {'filename': 'CODE_TAG_SUMMARY.md', 'ignore_patterns': '', **config}
    monkeypatch.chdir(repo_dir / cwd)

    collect_code_tags(ctx, **kwargs)

    assert list(repo_dir.rglob('*.md')) == ([path_output] if rows else [])
    if rows:
        found_rows, last_edits = _read_summary(path_output)
        assert sorted(found_rows) == sorted(rows)
        if vcs == 'git':
            assert all(re.fullmatch(r'\d{4}-\d{2}-\d{2}', last_edit) for last_edit in last_edits)
        elif vcs is None:
            assert set(last_edits) == {'N/A'}
    ctx.run.assert_not_called()


def test_collect_code_tags_slash_in_filename(ctx):
    with pytest.raises(RuntimeError, match='Unexpected slash in filename'):
        collect_code_tags(ctx, filename='sub/file.md')
