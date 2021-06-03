"""Test doit_tasks/file_search.py."""

from calcipy.doit_tasks.doit_globals import DG
from calcipy.doit_tasks.file_search import find_project_files_by_suffix


def test_find_project_files_by_suffix():
    """Test find_project_files_by_suffix."""
    result = find_project_files_by_suffix(DG.meta.path_project, DG.meta.ignore_patterns)

    assert len(result) != 0, f'Error: see {DG.meta.path_project}/README.md for configuring the directory'
    assert [*result.keys()] == ['yml', 'toml', '', 'md', 'cfg', 'yaml', 'py', 'ini', 'lock', 'json']
    assert result[''][0].name == '.flake8'
    assert result[''][2].name == 'LICENSE'
    assert result['md'][0].relative_to(DG.meta.path_project).as_posix() == '.github/ISSUE_TEMPLATE/bug_report.md'
