import pytest
from corallium.file_helpers import get_relative

from calcipy.file_search import (
    _get_all_files,
    _get_default_ignore_patterns,
    _walk_files,
    find_project_files,
    find_project_files_by_suffix,
)

from .configuration import TEST_DATA_DIR

SAMPLE_README_DIR = TEST_DATA_DIR / 'sample_doc_files'


def test_find_project_files_by_suffix():
    expected_suffixes = ['', 'md']

    result = find_project_files_by_suffix(SAMPLE_README_DIR, ignore_patterns=[])

    assert len(result) != 0
    assert sorted(result.keys()) == expected_suffixes
    assert result[''][0].name == '.dotfile'
    rel_pth = get_relative(result['md'][-1], SAMPLE_README_DIR)
    assert rel_pth
    assert rel_pth.as_posix() == 'README.md'


def test_walk_files_basic(tmp_path):
    (tmp_path / 'file1.py').write_text('content')
    (tmp_path / 'subdir').mkdir()
    (tmp_path / 'subdir' / 'file2.py').write_text('content')

    files = _walk_files(cwd=tmp_path)

    assert 'file1.py' in files
    assert 'subdir/file2.py' in files


def test_get_all_files_fallback(tmp_path):
    (tmp_path / 'test.py').write_text('content')

    files, used_git = _get_all_files(cwd=tmp_path)

    assert not used_git
    assert 'test.py' in files


def test_default_ignore_patterns_applied(tmp_path):
    (tmp_path / '__pycache__').mkdir()
    (tmp_path / '__pycache__' / 'cached.pyc').write_text('')
    (tmp_path / 'source.py').write_text('# code')

    files = find_project_files(tmp_path, ignore_patterns=[])

    file_names = [f.name for f in files]
    assert 'source.py' in file_names
    assert 'cached.pyc' not in file_names


@pytest.mark.parametrize(
    'expected_pattern',
    [
        '**/__pycache__/**',
        '**/*.pyc',
        '**/.git/**',
        '**/.jj/**',
        '**/node_modules/**',
        '**/.venv/**',
        '**/venv/**',
        '**/.pytest_cache/**',
        '**/.mypy_cache/**',
        '**/.ruff_cache/**',
        '**/dist/**',
        '**/build/**',
    ],
)
def test_get_default_ignore_patterns(expected_pattern):
    patterns = _get_default_ignore_patterns()
    assert expected_pattern in patterns
