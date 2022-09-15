"""Test file_search.py."""

from calcipy.doit_tasks.doit_globals import get_dg
from calcipy.file_search import find_project_files_by_suffix


def test_find_project_files_by_suffix():
    """Test find_project_files_by_suffix."""
    expected_suffixes = ['', 'ini', 'js', 'json', 'lock', 'md', 'py', 'toml', 'yaml', 'yml']

    result = find_project_files_by_suffix(get_dg().meta.path_project, get_dg().meta.ignore_patterns)

    assert len(result) != 0, f'Error: see {get_dg().meta.path_project}/README.md for configuring the directory'
    assert sorted(result.keys()) == expected_suffixes
    assert result[''][0].name == '.flake8'
    assert result['md'][-1].relative_to(get_dg().meta.path_project).as_posix() == 'tests/data/README.md'
