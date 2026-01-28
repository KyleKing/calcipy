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


def test_collect_code_tags_from_subdirectory_uses_git_root(ctx, tmp_path):
    """Test that collect_code_tags outputs to git root when run from subdirectory."""
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

    # Create docs/docs at git root
    docs_dir = repo_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    # Change to subdirectory and run collect_code_tags
    original_cwd = Path.cwd()
    try:
        os.chdir(sub_dir)
        # This should log a warning and create file at git root
        collect_code_tags(ctx)

        # CODE_TAG_SUMMARY.md should be created at git root, not in subdirectory
        code_tag_file = docs_dir / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file(), f'File should be created at git root {code_tag_file}'

        # Should NOT be created in subdirectory
        sub_docs_dir = sub_dir / 'docs' / 'docs'
        if sub_docs_dir.exists():
            assert not (sub_docs_dir / 'CODE_TAG_SUMMARY.md').is_file()

        # Clean up
        code_tag_file.unlink()
    finally:
        os.chdir(original_cwd)


def test_collect_code_tags_ignore_git_root_flag(ctx, tmp_path):
    """Test that ignore_git_root flag allows using CWD as base."""
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

    # Change to subdirectory and run with ignore_git_root flag
    original_cwd = Path.cwd()
    try:
        os.chdir(sub_dir)
        collect_code_tags(ctx, ignore_git_root=True)

        # File should be created in subdirectory
        code_tag_file = docs_dir / 'CODE_TAG_SUMMARY.md'
        assert code_tag_file.is_file(), f'File should be created in subdirectory {code_tag_file}'
        code_tag_file.unlink()
    finally:
        os.chdir(original_cwd)


def test_collect_code_tags_not_in_git_repo(ctx, tmp_path):
    """Test that collect_code_tags raises error when not in a git repository."""
    # Create a non-git directory
    non_git_dir = tmp_path / 'not_git'
    non_git_dir.mkdir()
    docs_dir = non_git_dir / 'docs' / 'docs'
    docs_dir.mkdir(parents=True)

    original_cwd = Path.cwd()
    try:
        os.chdir(non_git_dir)
        with pytest.raises(RuntimeError, match='Not in a git repository'):
            collect_code_tags(ctx)
    finally:
        os.chdir(original_cwd)
