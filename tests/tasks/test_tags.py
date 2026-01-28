# mypy: disable_error_code=type-arg


import os

import pytest
import os
from pathlib import Path

import pytest
from beartype.typing import Callable, Dict
from corallium.shell import capture_shell

from calcipy.tasks.tags import collect_code_tags
from tests.configuration import APP_DIR, TEST_DATA_DIR


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


def test_collect_code_tags_from_subdirectory_uses_repo_root(ctx, tmp_path):
    """Test that collect_code_tags outputs to repo root when run from subdirectory."""
    # Create a git repo with a subdirectory containing a TODO
    repo_dir = tmp_path / 'repo'
    repo_dir.mkdir()
    sub_dir = repo_dir / 'subdir'
    sub_dir.mkdir()

    # Initialize git repo in parent
    capture_shell('git init', cwd=repo_dir)
    capture_shell('git config user.email "test@test.com"', cwd=repo_dir)
    capture_shell('git config user.name "Test"', cwd=repo_dir)

    # Create a .copier-answers.yml for get_doc_subdir
    (repo_dir / '.copier-answers.yml').write_text('doc_dir: docs')

    # Create files with TODO tags in both root and subdirectory
    (repo_dir / 'root.py').write_text('# TODO: root task')
    (sub_dir / 'sub.py').write_text('# TODO: subdirectory task')
    capture_shell('git add .', cwd=repo_dir)
    capture_shell('git commit -m "initial"', cwd=repo_dir)

    # Create docs/docs at repo root
    docs_dir = repo_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    # Change to subdirectory and run collect_code_tags
    original_cwd = Path.cwd()
    try:
        os.chdir(sub_dir)
        # This should log a warning and create file at repo root
        collect_code_tags(ctx)

        # CODE_TAG_SUMMARY.md should be created at repo root, not in subdirectory
        code_tag_file = docs_dir / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file(), f'File should be created at repo root {code_tag_file}'

        # Should NOT be created in subdirectory
        sub_docs_dir = sub_dir / 'docs' / 'docs'
        if sub_docs_dir.exists():
            assert not (sub_docs_dir / 'CODE_TAG_SUMMARY.md').is_file()

        # Clean up
        code_tag_file.unlink()
    finally:
        os.chdir(original_cwd)


def test_collect_code_tags_ignore_repo_root_flag(ctx, tmp_path):
    """Test that ignore_repo_root flag allows using CWD as base."""
    # Create a git repo with a subdirectory
    repo_dir = tmp_path / 'repo'
    repo_dir.mkdir()
    sub_dir = repo_dir / 'subdir'
    sub_dir.mkdir()

    # Initialize git repo
    capture_shell('git init', cwd=repo_dir)
    capture_shell('git config user.email "test@test.com"', cwd=repo_dir)
    capture_shell('git config user.name "Test"', cwd=repo_dir)

    # Create a file with TODO in subdirectory
    (sub_dir / 'sub.py').write_text('# TODO: subdirectory task')
    (sub_dir / '.copier-answers.yml').write_text('doc_dir: docs')
    capture_shell('git add .', cwd=repo_dir)
    capture_shell('git commit -m "initial"', cwd=repo_dir)

    # Create docs/docs in subdirectory
    docs_dir = sub_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    # Change to subdirectory and run with ignore_repo_root flag
    original_cwd = Path.cwd()
    try:
        os.chdir(sub_dir)
        collect_code_tags(ctx, ignore_repo_root=True)

        # File should be created in subdirectory
        code_tag_file = docs_dir / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file(), f'File should be created in subdirectory {code_tag_file}'
        code_tag_file.unlink()
    finally:
        os.chdir(original_cwd)


def test_collect_code_tags_copier_answers_at_repo_root(ctx, tmp_path):
    """Test that .copier-answers.yml is found at repo root even when running from subdirectory."""
    # Create a git repo with subdirectory
    repo_dir = tmp_path / 'repo'
    repo_dir.mkdir()
    sub_dir = repo_dir / 'subdir'
    sub_dir.mkdir()

    # Initialize git repo
    capture_shell('git init', cwd=repo_dir)
    capture_shell('git config user.email "test@test.com"', cwd=repo_dir)
    capture_shell('git config user.name "Test"', cwd=repo_dir)

    # Create .copier-answers.yml ONLY at repo root (not in subdirectory)
    (repo_dir / '.copier-answers.yml').write_text('doc_dir: docs')

    # Create file with TODO in subdirectory
    (sub_dir / 'sub.py').write_text('# TODO: subdirectory task')
    capture_shell('git add .', cwd=repo_dir)
    capture_shell('git commit -m "initial"', cwd=repo_dir)

    # Create docs/docs at repo root
    docs_dir = repo_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    # Change to subdirectory and run with ignore_repo_root flag
    # This should still find .copier-answers.yml at repo root
    original_cwd = Path.cwd()
    try:
        os.chdir(sub_dir)
        collect_code_tags(ctx, ignore_repo_root=True)

        # File should be created in subdirectory's docs/docs
        # But .copier-answers.yml should have been found at repo root
        code_tag_file = sub_dir / 'docs' / 'docs' / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file(), f'File should be created {code_tag_file}'
        code_tag_file.unlink()
    finally:
        os.chdir(original_cwd)


def test_collect_code_tags_jj_repo(ctx, tmp_path):
    """Test that collect_code_tags works with jj-vcs repositories.

    Note: Still requires git for file listing (find_project_files uses git ls-files).
    This test verifies that repo root detection works with .jj folders.
    """
    # Create a repo with both .jj and .git (jj can coexist with git)
    repo_dir = tmp_path / 'jj_repo'
    repo_dir.mkdir()
    jj_dir = repo_dir / '.jj'
    jj_dir.mkdir()

    # Initialize git for file listing
    capture_shell('git init', cwd=repo_dir)
    capture_shell('git config user.email "test@test.com"', cwd=repo_dir)
    capture_shell('git config user.name "Test"', cwd=repo_dir)

    # Create a .copier-answers.yml
    (repo_dir / '.copier-answers.yml').write_text('doc_dir: docs')

    # Create file with TODO
    (repo_dir / 'code.py').write_text('# TODO: jj task')
    capture_shell('git add .', cwd=repo_dir)
    capture_shell('git commit -m "initial"', cwd=repo_dir)

    # Create docs/docs
    docs_dir = repo_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    # Run from repo directory
    original_cwd = Path.cwd()
    try:
        os.chdir(repo_dir)
        collect_code_tags(ctx)

        # File should be created
        code_tag_file = docs_dir / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file(), f'File should be created {code_tag_file}'
        code_tag_file.unlink()
    finally:
        os.chdir(original_cwd)


def test_find_repo_root_from_nested_subdirectory(tmp_path):
    """Test that find_repo_root works from deeply nested subdirectories."""
    from calcipy.invoke_helpers import find_repo_root

    # Create nested directory structure
    repo_dir = tmp_path / 'project'
    repo_dir.mkdir()
    dist_dir = repo_dir / 'dist'
    dist_dir.mkdir()

    # Create .git directory
    git_dir = repo_dir / '.git'
    git_dir.mkdir()

    # Should find repo root from nested dir
    assert find_repo_root(dist_dir) == repo_dir

    # Test with .jj
    jj_dir = repo_dir / '.jj'
    jj_dir.mkdir()
    git_dir.rmdir()  # Remove .git to test .jj
    assert find_repo_root(dist_dir) == repo_dir


def test_collect_code_tags_not_in_repo(ctx, tmp_path):
    """Test that collect_code_tags raises error when not in a repository."""
    # Create a non-repository directory
    non_repo_dir = tmp_path / 'not_repo'
    non_repo_dir.mkdir()
    docs_dir = non_repo_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    original_cwd = Path.cwd()
    try:
        os.chdir(non_repo_dir)
        with pytest.raises(RuntimeError, match='Not in a repository'):
            collect_code_tags(ctx)
    finally:
        os.chdir(original_cwd)
