# mypy: disable_error_code=type-arg

import os
import shutil
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from pathlib import Path
from subprocess import CalledProcessError  # noqa: S404

import pytest
from beartype.typing import Callable, Dict
from corallium.shell import capture_shell
from corallium.vcs import find_repo_root

from calcipy.tasks.tags import collect_code_tags
from tests.configuration import APP_DIR, TEST_DATA_DIR


@contextmanager
def _in_directory(path: Path):
    """Context manager for temporarily changing working directory."""
    original = Path.cwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(original)


def _init_git_repo(repo_dir: Path) -> None:
    capture_shell('git init', cwd=repo_dir)
    capture_shell('git config user.email "test@test.com"', cwd=repo_dir)
    capture_shell('git config user.name "Test"', cwd=repo_dir)


def _commit_files(repo_dir: Path, message: str = 'initial') -> None:
    capture_shell('git add .', cwd=repo_dir)
    capture_shell(f'git commit -m "{message}"', cwd=repo_dir)


def _init_jj_repo(repo_dir: Path) -> None:
    capture_shell('jj git init --no-colocate', cwd=repo_dir)
    capture_shell('jj config set --repo user.email "test@test.com"', cwd=repo_dir)
    capture_shell('jj config set --repo user.name "Test"', cwd=repo_dir)


def _jj_track_files(repo_dir: Path) -> None:
    with suppress(CalledProcessError):
        capture_shell('jj new', cwd=repo_dir)


@dataclass(frozen=True)
class _VcsSetup:
    init: Callable[..., None]
    snapshot: Callable[..., None]


_GIT = _VcsSetup(init=_init_git_repo, snapshot=_commit_files)
_JJ = _VcsSetup(init=_init_jj_repo, snapshot=_jj_track_files)

_skip_no_jj = pytest.mark.skipif(not shutil.which('jj'), reason='jj not available')
_vcs_params = [pytest.param(_GIT, id='git'), pytest.param(_JJ, id='jj', marks=_skip_no_jj)]


def _merge_path_kwargs(kwargs: Dict) -> Path:
    return Path(f'{kwargs["doc_sub_dir"]}/{kwargs["filename"]}')


def _check_no_write(kwargs: Dict) -> None:
    path_tag_summary = _merge_path_kwargs(kwargs)
    assert not path_tag_summary.is_file()


def _check_output(kwargs: Dict) -> None:
    path_tag_summary = _merge_path_kwargs(kwargs)
    assert path_tag_summary.is_file()
    content = path_tag_summary.read_text()
    path_tag_summary.unlink()
    assert '# Collected Code Tags' in content


@pytest.mark.parametrize(
    ('task', 'kwargs', 'validator'),
    [
        (
            collect_code_tags,
            {
                'base_dir': APP_DIR.as_posix(),
                'doc_sub_dir': TEST_DATA_DIR.as_posix(),
                'filename': 'test_tags.md.rej',
                'tag_order': 'FIXME,TODO',
                'regex': '',
                'ignore_patterns': '*.py,*.yaml,docs/docs/*.md,*.toml',
            },
            _check_no_write,
        ),
        (
            collect_code_tags,
            {
                'base_dir': APP_DIR.as_posix(),
                'doc_sub_dir': TEST_DATA_DIR.as_posix(),
                'filename': 'test_tags.md.rej',
            },
            _check_output,
        ),
    ],
    ids=[
        'Check that no code tags were matched and no file was created',
        'Check that code tags were matched and a file was created',
    ],
)
def test_tags(ctx, task, kwargs: Dict, validator: Callable[[Dict], None]):
    task(ctx, **kwargs)

    validator(kwargs)


@pytest.mark.parametrize('vcs', _vcs_params)
def test_collect_code_tags_from_subdirectory_uses_repo_root(ctx, tmp_path, vcs):
    repo_dir = tmp_path / 'repo'
    repo_dir.mkdir()
    sub_dir = repo_dir / 'subdir'
    sub_dir.mkdir()

    vcs.init(repo_dir)
    (repo_dir / '.copier-answers.yml').write_text('doc_dir: docs')
    (repo_dir / 'root.py').write_text('# TODO: root task')
    (sub_dir / 'sub.py').write_text('# TODO: subdirectory task')
    vcs.snapshot(repo_dir)

    docs_dir = repo_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    with _in_directory(sub_dir):
        collect_code_tags(ctx)

        code_tag_file = docs_dir / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file(), f'File should be created at repo root {code_tag_file}'
        content = code_tag_file.read_text()
        assert 'root task' in content
        assert 'subdirectory task' in content

        sub_docs_dir = sub_dir / 'docs' / 'docs'
        if sub_docs_dir.exists():
            assert not (sub_docs_dir / 'CODE_TAG_SUMMARY.md').is_file()

        code_tag_file.unlink()


@pytest.mark.parametrize('vcs', _vcs_params)
def test_collect_code_tags_ignore_repo_root_flag(ctx, tmp_path, vcs):
    repo_dir = tmp_path / 'repo'
    repo_dir.mkdir()
    sub_dir = repo_dir / 'subdir'
    sub_dir.mkdir()

    vcs.init(repo_dir)
    (sub_dir / 'sub.py').write_text('# TODO: subdirectory task')
    (sub_dir / '.copier-answers.yml').write_text('doc_dir: docs')
    vcs.snapshot(repo_dir)

    docs_dir = sub_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    with _in_directory(sub_dir):
        collect_code_tags(ctx, ignore_repo_root=True)

        code_tag_file = docs_dir / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file(), f'File should be created in subdirectory {code_tag_file}'
        code_tag_file.unlink()


@pytest.mark.parametrize('vcs', _vcs_params)
def test_collect_code_tags_copier_answers_at_repo_root(ctx, tmp_path, vcs):
    repo_dir = tmp_path / 'repo'
    repo_dir.mkdir()
    sub_dir = repo_dir / 'subdir'
    sub_dir.mkdir()

    vcs.init(repo_dir)
    (repo_dir / '.copier-answers.yml').write_text('doc_dir: docs')
    (sub_dir / 'sub.py').write_text('# TODO: subdirectory task')
    vcs.snapshot(repo_dir)

    docs_dir = repo_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    with _in_directory(sub_dir):
        collect_code_tags(ctx, ignore_repo_root=True)

        code_tag_file = sub_dir / 'docs' / 'docs' / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file(), f'File should be created {code_tag_file}'
        code_tag_file.unlink()


def test_collect_code_tags_jj_repo(ctx, tmp_path):
    repo_dir = tmp_path / 'jj_repo'
    repo_dir.mkdir()
    (repo_dir / '.jj').mkdir()

    _init_git_repo(repo_dir)
    (repo_dir / '.copier-answers.yml').write_text('doc_dir: docs')
    (repo_dir / 'code.py').write_text('# TODO: jj task')
    _commit_files(repo_dir)

    docs_dir = repo_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    with _in_directory(repo_dir):
        collect_code_tags(ctx)

        code_tag_file = docs_dir / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file(), f'File should be created {code_tag_file}'
        code_tag_file.unlink()


@_skip_no_jj
def test_collect_code_tags_pure_jj_repo(ctx, tmp_path):
    repo_dir = tmp_path / 'pure_jj_repo'
    repo_dir.mkdir()

    _init_jj_repo(repo_dir)
    (repo_dir / '.copier-answers.yml').write_text('doc_dir: docs')
    (repo_dir / 'code.py').write_text('# TODO: pure jj task')
    _jj_track_files(repo_dir)

    docs_dir = repo_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    with _in_directory(repo_dir):
        collect_code_tags(ctx)

        code_tag_file = docs_dir / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file(), f'File should be created {code_tag_file}'
        content = code_tag_file.read_text()
        assert 'TODO' in content
        assert 'pure jj task' in content
        code_tag_file.unlink()


@_skip_no_jj
def test_find_repo_root_pure_jj(tmp_path):
    repo_dir = tmp_path / 'jj_only'
    repo_dir.mkdir()
    _init_jj_repo(repo_dir)

    assert (repo_dir / '.jj').is_dir()
    assert not (repo_dir / '.git').exists()
    assert find_repo_root(repo_dir) == repo_dir


def test_find_repo_root_from_nested_subdirectory(tmp_path):
    repo_dir = tmp_path / 'project'
    repo_dir.mkdir()
    dist_dir = repo_dir / 'dist'
    dist_dir.mkdir()

    git_dir = repo_dir / '.git'
    git_dir.mkdir()

    assert find_repo_root(dist_dir) == repo_dir

    jj_dir = repo_dir / '.jj'
    jj_dir.mkdir()
    git_dir.rmdir()
    assert find_repo_root(dist_dir) == repo_dir


def test_collect_code_tags_slash_in_filename(ctx):
    with pytest.raises(RuntimeError, match='Unexpected slash in filename'):
        collect_code_tags(ctx, filename='sub/file.md')


def test_collect_code_tags_not_in_repo(ctx, tmp_path):
    non_repo_dir = tmp_path / 'not_repo'
    non_repo_dir.mkdir()
    docs_dir = non_repo_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)
    (non_repo_dir / 'code.py').write_text('# TODO: test task')

    with _in_directory(non_repo_dir):
        collect_code_tags(ctx)

        code_tag_file = docs_dir / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file()
        content = code_tag_file.read_text()
        assert 'TODO' in content
        assert 'test task' in content
        code_tag_file.unlink()


def test_collect_code_tags_no_git_with_custom_ignore(ctx, tmp_path):
    non_repo_dir = tmp_path / 'not_repo'
    non_repo_dir.mkdir()
    docs_dir = non_repo_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)
    (non_repo_dir / 'include.py').write_text('# TODO: include')
    (non_repo_dir / 'exclude.py').write_text('# TODO: exclude')

    with _in_directory(non_repo_dir):
        collect_code_tags(ctx, ignore_patterns='exclude.py')

        code_tag_file = docs_dir / 'CODE_TAG_SUMMARY.md'
        content = code_tag_file.read_text()
        assert 'include' in content
        assert 'exclude' not in content
        code_tag_file.unlink()
