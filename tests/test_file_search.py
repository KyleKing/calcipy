"""Test file_search.py."""

from calcipy.doit_tasks.doit_globals import DG
from calcipy.file_search import find_project_files_by_suffix


def test_find_project_files_by_suffix():
    """Test find_project_files_by_suffix."""
    result = find_project_files_by_suffix(DG.meta.path_project, DG.meta.ignore_patterns)

    assert len(result) != 0, f'Error: see {DG.meta.path_project}/README.md for configuring the directory'
    assert sorted(result.keys()) == ['', 'ini', 'js', 'json', 'lock', 'md', 'py', 'toml', 'yaml', 'yml']
    assert result[''][0].name == '.flake8'
    assert result['md'][-1].relative_to(DG.meta.path_project).as_posix() == 'tests/data/README.md'
